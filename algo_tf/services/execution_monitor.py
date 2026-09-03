from __future__ import annotations

from dataclasses import dataclass

from algo_tf.contracts.inbound.execution_update import ExecutionUpdate
from algo_tf.state.child_intent_machine import TERMINAL, can_transition


@dataclass(frozen=True, slots=True)
class ExecutionStatus:
    intent_id: str
    status: str
    filled_quantity: int
    average_fill_price: float | None
    reason: str | None


class ExecutionMonitor:
    def __init__(self) -> None:
        self._statuses: dict[str, ExecutionStatus] = {}

    def apply(self, update: ExecutionUpdate) -> ExecutionStatus:
        previous = self._statuses.get(update.intent_id)
        current_status = previous.status if previous else "SUBMITTED"
        if previous and update.filled_quantity < previous.filled_quantity:
            raise ValueError("filled quantity cannot decrease")
        if current_status in TERMINAL or (
            update.status != current_status and not can_transition(current_status, update.status)
        ):
            raise ValueError(f"invalid execution transition: {current_status} -> {update.status}")
        status = ExecutionStatus(
            intent_id=update.intent_id,
            status=update.status,
            filled_quantity=update.filled_quantity,
            average_fill_price=update.average_fill_price,
            reason=update.reason,
        )
        self._statuses[update.intent_id] = status
        return status

    def get(self, intent_id: str) -> ExecutionStatus | None:
        return self._statuses.get(intent_id)
