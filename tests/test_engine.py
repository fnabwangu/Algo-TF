from datetime import datetime, timedelta, timezone
import time
import unittest

from algof.domain import Action, AgentResult, EvidenceState, ExecutionConstraints, Observation
from algof.engine import DecisionEngine, HistoricalOutcome, empirical_probability
from algof.server import ReviewStore


NOW = datetime(2026, 1, 5, tzinfo=timezone.utc)


class Provider:
    name = "synthetic-market"

    def __init__(self, observations):
        self.observations = observations

    def observe(self, instrument, cutoff):
        return self.observations


class Adviser:
    name = "synthetic-adviser"

    def answer(self, request):
        return AgentResult(agent=self.name, response="No additional reading.")


class SlowAdviser(Adviser):
    name = "slow-adviser"

    def answer(self, request):
        time.sleep(0.2)
        return super().answer(request)


def constraints():
    return ExecutionConstraints(True, ("SPY",), tuple(Action), 10000, 0, 100, 100, "synthetic quote")


class DynamicDecisionTests(unittest.TestCase):
    def test_missing_gex_does_not_block_positive_judgment(self):
        observations = [
            Observation("GEX", None, EvidenceState.MISSING, "gex", None, NOW, "Reduces proposed size."),
            Observation("technical_confirmation", True, EvidenceState.KNOWN, "bars", NOW, NOW, "Trend supports entry."),
        ]
        outcomes = [HistoricalOutcome(NOW - timedelta(days=5), NOW - timedelta(days=4), True, .01)] * 8
        record = DecisionEngine([Provider(observations)], [Adviser()]).decide("SPY", "next-session", NOW, constraints(), outcomes)
        self.assertEqual(record.action, Action.ENTER)
        self.assertGreater(record.quantity, 0)
        self.assertIn("GEX: MISSING", record.missing_data_implications[0])
        self.assertIsNotNone(record.initial_recommendation)

    def test_agent_disagreement_is_advisory_evidence(self):
        observations = [
            Observation("technical_confirmation", True, EvidenceState.KNOWN, "bars", NOW, NOW, "Trend supports entry."),
            Observation("agent_disagreement", None, EvidenceState.CONFLICTING, "advisers", NOW, NOW, "One adviser disagrees."),
        ]
        outcomes = [HistoricalOutcome(NOW - timedelta(days=5), NOW - timedelta(days=4), True, .01)] * 8
        record = DecisionEngine([Provider(observations)], []).decide("SPY", "next-session", NOW, constraints(), outcomes)
        self.assertEqual(record.action, Action.ENTER)
        self.assertGreater(record.quantity, 0)

    def test_future_observations_and_outcomes_are_excluded(self):
        future = Observation("future_signal", True, EvidenceState.KNOWN, "future", NOW, NOW + timedelta(minutes=1), "Must not appear.")
        record = DecisionEngine([Provider([future])], []).decide("SPY", "next-session", NOW, constraints(), [
            HistoricalOutcome(NOW, NOW + timedelta(days=1), True, .2)
        ])
        self.assertEqual(record.snapshot.observations, ())
        self.assertEqual(record.probabilities[0].kind.value, "UNAVAILABLE")

    def test_empirical_probability_has_provenance_and_interval(self):
        outcomes = [HistoricalOutcome(NOW, NOW, index < 3, .01 if index < 3 else -.01) for index in range(4)]
        estimate = empirical_probability("positive return", "one day", NOW, outcomes)
        self.assertEqual(estimate.kind.value, "EMPIRICAL")
        self.assertEqual(estimate.sample_size, 4)
        self.assertIsNotNone(estimate.interval)

    def test_adviser_timeout_does_not_deadlock_decision(self):
        observations = [Observation("GEX", None, EvidenceState.MISSING, "gex", None, NOW, "Unknown.")]
        start = time.monotonic()
        record = DecisionEngine([Provider(observations)], [SlowAdviser()]).decide(
            "SPY", "next-session", NOW, constraints(), [], research_budget_seconds=.01
        )
        self.assertLess(time.monotonic() - start, .1)
        self.assertTrue(record.agent_results[0].timed_out)

    def test_closing_direction_and_cash_limits_are_execution_only(self):
        allowed, issues = constraints().assess("SPY", Action.EXIT, 1)
        self.assertFalse(allowed)
        self.assertIn("closing quantity", issues[0])

    def test_review_is_bound_to_its_decision_snapshot(self):
        store = ReviewStore()
        status, response = store.submit({"decision_id": store.decision.decision_id, "snapshot_id": "wrong", "action": "APPROVE"})
        self.assertEqual(status, 409)
        self.assertIn("snapshot", response["error"])


if __name__ == "__main__":
    unittest.main()