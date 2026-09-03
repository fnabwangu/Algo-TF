from __future__ import annotations

import uuid
from datetime import datetime

from algo_tf.domain.market_observation import MarketObservation
from algo_tf.persistence.repositories.observation_repository import ObservationRepository


class ObservationService:
    def __init__(self, repository: ObservationRepository) -> None:
        self._repository = repository

    def record(self, kind: str, instrument: str, payload: dict[str, object]) -> dict[str, object]:
        if "observed_at" not in payload:
            raise ValueError("observed_at is required")
        document = {"kind": kind, "instrument": instrument, **payload}
        return self._repository.save(str(uuid.uuid4()), document, f"{kind}:{instrument}")

    def latest_observation(
        self,
        instrument: str,
        now: datetime,
        target_remaining_quantity: int,
        strategy_eligible: bool,
    ) -> MarketObservation | None:
        quote = self._repository.latest_for(f"quote:{instrument}")
        if quote is None:
            return None
        observed_at = datetime.fromisoformat(str(quote["observed_at"]))
        age = max(0.0, (now - observed_at).total_seconds())
        spread_bps = (float(quote["ask"]) - float(quote["bid"])) / float(quote["ask"]) * 10_000
        gex = self._repository.latest_for(f"gex:{instrument}")
        return MarketObservation(
            observed_at=observed_at,
            bid=float(quote["bid"]),
            ask=float(quote["ask"]),
            last=float(quote["last"]),
            spread_bps=spread_bps,
            quote_age_seconds=age,
            market_structure_age_seconds=age,
            liquidity_score=float(quote.get("liquidity_score", 1)),
            signal_coefficient=float(quote.get("signal_coefficient", 1)),
            gex_coefficient=float(gex.get("gex_coefficient", 1)) if gex else 0,
            spread_coefficient=float(quote.get("spread_coefficient", 1)),
            participation_coefficient=float(quote.get("participation_coefficient", 1)),
            time_coefficient=float(quote.get("time_coefficient", 1)),
            risk_budget_available=True,
            confirmation_pass=bool(quote.get("confirmation_pass", True)),
            market_open=bool(quote.get("market_open", True)),
            execution_engine_available=bool(quote.get("execution_engine_available", True)),
            kill_switch_clear=bool(quote.get("kill_switch_clear", True)),
            strategy_eligible=strategy_eligible,
            target_remaining_quantity=target_remaining_quantity,
            gex_fresh=gex is not None,
            quote_fresh=age <= 30,
        )

    def latest_position(self, instrument: str) -> dict[str, object] | None:
        return self._repository.latest_for(f"position:{instrument}")
