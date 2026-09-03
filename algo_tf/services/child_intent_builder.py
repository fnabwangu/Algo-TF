from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from algo_tf.audit.hashing import digest_payload
from algo_tf.domain.algorithm_decision import AlgorithmDecision
from algo_tf.domain.child_order_intent import ChildOrderIntent
from algo_tf.domain.enums import Action, OrderType, TimeInForce
from algo_tf.domain.execution_mandate import ExecutionMandate


class ChildIntentBuilder:
    def build(
        self,
        mandate: ExecutionMandate,
        decision: AlgorithmDecision,
        now: datetime,
    ) -> ChildOrderIntent | None:
        if decision.action not in {
            Action.ENTER,
            Action.SCALE_IN,
            Action.REDUCE,
            Action.EXIT,
        }:
            return None
        if decision.requested_quantity <= 0 or decision.limit_price is None:
            return None
        payload = {
            "mandate_id": mandate.mandate_id,
            "decision_id": decision.decision_id,
            "instrument": mandate.instrument,
            "quantity": decision.requested_quantity,
            "limit_price": decision.limit_price,
        }
        idem = digest_payload(payload)
        return ChildOrderIntent(
            intent_id=str(uuid4()),
            parent_mandate_id=mandate.mandate_id,
            decision_id=decision.decision_id,
            strategy_id=mandate.strategy_id,
            sleeve_element_id=mandate.sleeve_element_id,
            instrument=mandate.instrument,
            asset_class=mandate.asset_class,
            side=mandate.direction,
            quantity=decision.requested_quantity,
            order_type=OrderType.LIMIT,
            limit_price=decision.limit_price,
            time_in_force=TimeInForce.DAY,
            maximum_slippage_bps=mandate.maximum_slippage_bps,
            idempotency_key=idem,
            created_at=now,
            expires_at=min(decision.expires_at, mandate.expires_at),
            evidence_digest=decision.observation_digest,
            mandate_remaining_capacity=decision.requested_quantity,
        )
