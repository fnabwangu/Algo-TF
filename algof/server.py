"""Local human-review server. It has no broker adapter and never places orders."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import urlparse

from .domain import Action, AgentResult, EvidenceState, ExecutionConstraints, Observation, ReviewAction, ReviewSubmission
from .engine import DecisionEngine, HistoricalOutcome


ROOT = Path(__file__).parent.parent


class FixtureProvider:
    name = "synthetic-market-fixture"

    def observe(self, instrument: str, cutoff: datetime) -> list[Observation]:
        return [
            Observation("GEX", None, EvidenceState.MISSING, "configured GEX provider", None, cutoff,
                        "No current GEX reduces entry size; it is not a veto.", ("net_gex",), label="OBSERVATION"),
            Observation("technical_confirmation", True, EvidenceState.KNOWN, "synthetic OHLC fixture", cutoff, cutoff,
                        "Trend and breadth confirm the directional thesis.", source_url="/api/decision/data"),
            Observation("research_eligibility", True, EvidenceState.KNOWN, "synthetic eligibility fixture", cutoff, cutoff,
                        "Research criteria are favorable but remain advisory."),
        ]


class FixtureAdviser:
    name = "synthetic-options-adviser"

    def answer(self, request):
        return AgentResult(self.name, "GEX unavailable from fixture provider; retain reduced size.")


def build_demo_decision():
    cutoff = datetime.now(timezone.utc)
    constraints = ExecutionConstraints(
        authorized=True, permitted_instruments=("SPY",), permitted_actions=tuple(Action),
        available_cash=10_000, current_position=0, max_position=100, indicative_price=500.0,
        pricing_source="synthetic quote fixture; not executable pricing",
    )
    outcomes = [
        HistoricalOutcome(cutoff - timedelta(days=8 + index), cutoff - timedelta(days=7 + index), index < 6,
                          .008 if index < 6 else -.006)
        for index in range(10)
    ]
    return DecisionEngine([FixtureProvider()], [FixtureAdviser()]).decide(
        "SPY", "next-session", cutoff, constraints, outcomes, research_budget_seconds=.2
    )


class ReviewStore:
    def __init__(self) -> None:
        self.decision = build_demo_decision()
        self.reviews: list[ReviewSubmission] = []
        self.mode = "ADVISORY"

    def submit(self, body: dict) -> tuple[int, dict]:
        if body.get("decision_id") != self.decision.decision_id or body.get("snapshot_id") != self.decision.snapshot.snapshot_id:
            return HTTPStatus.CONFLICT, {"error": "Decision or dataset snapshot no longer matches this review."}
        if self.decision.expires_at and datetime.now(timezone.utc) > self.decision.expires_at:
            return HTTPStatus.CONFLICT, {"error": "Decision has expired; review its revision before acting."}
        try:
            action = ReviewAction(body["action"])
        except (KeyError, ValueError):
            return HTTPStatus.BAD_REQUEST, {"error": "Invalid review action."}
        quantity = body.get("quantity")
        if action == ReviewAction.RESIZE and (not isinstance(quantity, (int, float)) or quantity < 0):
            return HTTPStatus.BAD_REQUEST, {"error": "Resize requires a non-negative numeric quantity."}
        self.reviews.append(ReviewSubmission(self.decision.decision_id, self.decision.snapshot.snapshot_id, action,
                                              str(body.get("reviewer", "local reviewer")), datetime.now(timezone.utc),
                                              quantity, str(body.get("note", ""))))
        return HTTPStatus.CREATED, {"status": "recorded", "mode": self.mode, "review": self.reviews[-1]}


STORE = ReviewStore()


class ReviewHandler(SimpleHTTPRequestHandler):
    def _json(self, status: int, payload: object) -> None:
        data = json.dumps(payload, default=str).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):  # noqa: N802
        route = urlparse(self.path).path
        if route == "/api/decision":
            return self._json(HTTPStatus.OK, {"decision": STORE.decision.to_dict(), "mode": STORE.mode, "reviews": STORE.reviews})
        if route == "/api/decision/data":
            return self._json(HTTPStatus.OK, {"snapshot_id": STORE.decision.snapshot.snapshot_id,
                                               "cutoff": STORE.decision.snapshot.cutoff,
                                               "observations": STORE.decision.snapshot.observations,
                                               "synthetic_fixture": True})
        if route == "/download/decision.json":
            return self._json(HTTPStatus.OK, STORE.decision.to_dict())
        if route == "/":
            self.path = "/ui/index.html"
        return super().do_GET()

    def do_POST(self):  # noqa: N802
        if urlparse(self.path).path != "/api/reviews":
            return self._json(HTTPStatus.NOT_FOUND, {"error": "Unknown endpoint."})
        try:
            size = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(size))
        except (ValueError, json.JSONDecodeError):
            return self._json(HTTPStatus.BAD_REQUEST, {"error": "Body must be JSON."})
        status, response = STORE.submit(body)
        self._json(status, response)


def serve(port: int = 8000) -> None:
    with ThreadingHTTPServer(("0.0.0.0", port), ReviewHandler) as server:
        print(f"Algo-TF review server: http://localhost:{port}")
        server.serve_forever()


if __name__ == "__main__":
    serve()