from __future__ import annotations

from dataclasses import asdict, replace
from datetime import datetime

from algo_tf.domain.enums import Action, AssetClass, Direction, OrderType
from algo_tf.domain.execution_mandate import ExecutionMandate
from algo_tf.persistence.repositories.decision_repository import DecisionRepository
from algo_tf.persistence.repositories.intent_repository import IntentRepository
from algo_tf.persistence.repositories.mandate_repository import MandateRepository
from algo_tf.services.child_intent_builder import ChildIntentBuilder
from algo_tf.services.decision_engine import DecisionEngine
from algo_tf.services.observation_service import ObservationService
from algo_tf.services.risk_monitor import RiskMonitor


class Scheduler:
    def __init__(
        self,
        mandates: MandateRepository,
        observations: ObservationService,
        decisions: DecisionRepository,
        intents: IntentRepository,
    ) -> None:
        self._mandates = mandates
        self._observations = observations
        self._decisions = decisions
        self._intents = intents
        self._engine = DecisionEngine()
        self._intent_builder = ChildIntentBuilder()
        self._risk_monitor = RiskMonitor()

    def run_once(self, mandate_id: str, now: datetime) -> dict[str, object] | None:
        record = self._mandates.get(mandate_id)
        if record is None or record.get("state") not in {"ARMED", "ACTIVE"}:
            return None
        mandate = self._to_mandate(record)
        observation = self._observations.latest_observation(
            mandate.instrument,
            now,
            int(record.get("target_remaining_quantity", 0)),
            bool(record.get("eligible", True)),
        )
        if observation is None:
            return None
        decision = self._engine.decide(mandate, observation, now)
        if decision.action is not Action.WAIT:
            assessment = self._risk_monitor.assess(
                mandate,
                self._observations.latest_position(mandate.instrument),
                decision.requested_quantity,
            )
            if not assessment.approved:
                decision = replace(
                    decision,
                    action=Action.WAIT,
                    requested_quantity=0,
                    limit_price=None,
                    gate_results={**decision.gate_results, "risk_monitor": False},
                    reason_codes=("RISK_GATE_FAILED", *assessment.reason_codes),
                )
        decision_document = asdict(decision)
        self._decisions.save(decision_document)
        if decision.action is Action.WAIT:
            return decision_document
        intent = self._intent_builder.build(mandate, decision, now)
        if intent is not None:
            self._intents.save(asdict(intent))
        return decision_document

    @staticmethod
    def _to_mandate(record: dict[str, object]) -> ExecutionMandate:
        return ExecutionMandate(
            mandate_id=str(record["mandate_id"]),
            strategy_id=str(record["strategy_id"]),
            strategy_version=int(record["strategy_version"]),
            sleeve_element_id=str(record["sleeve_element_id"]),
            instrument=str(record["instrument"]),
            asset_class=AssetClass(str(record["asset_class"])),
            direction=Direction(str(record["direction"])),
            allowed_actions=tuple(Action(value) for value in record["allowed_actions"]),
            maximum_notional=float(record["maximum_notional"]),
            maximum_loss=float(record["maximum_loss"]),
            maximum_slippage_bps=float(record["maximum_slippage_bps"]),
            permitted_order_types=tuple(
                OrderType(value) for value in record["permitted_order_types"]
            ),
            maximum_child_orders=int(record["maximum_child_orders"]),
            maximum_reentries=int(record["maximum_reentries"]),
            maximum_state_flips=int(record["maximum_state_flips"]),
            effective_at=datetime.fromisoformat(str(record["effective_at"])),
            expires_at=datetime.fromisoformat(str(record["expires_at"])),
            is_revoked=record.get("state") == "REVOKED",
        )
