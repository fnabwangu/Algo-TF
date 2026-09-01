from __future__ import annotations

from dataclasses import dataclass

from algo_tf.domain.child_order_intent import ChildOrderIntent


@dataclass(slots=True)
class ExecutionEngineClient:
    """Only adapter allowed to submit child intents across execution boundary."""

    def submit_intent(self, intent: ChildOrderIntent) -> dict[str, object]:
        return {
            "status": "ACCEPTED",
            "intent_id": intent.intent_id,
            "idempotency_key": intent.idempotency_key,
        }
