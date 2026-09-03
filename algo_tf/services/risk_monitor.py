from __future__ import annotations

from dataclasses import dataclass

from algo_tf.domain.execution_mandate import ExecutionMandate


@dataclass(frozen=True, slots=True)
class RiskAssessment:
    approved: bool
    reason_codes: tuple[str, ...]


class RiskMonitor:
    def assess(
        self, mandate: ExecutionMandate, position: dict[str, object] | None, proposed_quantity: int
    ) -> RiskAssessment:
        if proposed_quantity <= 0:
            return RiskAssessment(False, ("NON_POSITIVE_QUANTITY",))
        if position is None:
            return RiskAssessment(True, ())
        average_price = float(position.get("average_price", 0))
        quantity = abs(int(position.get("quantity", 0)))
        notional = (quantity + proposed_quantity) * average_price
        losses = max(
            0.0, -float(position.get("realized_pnl", 0)) - float(position.get("unrealized_pnl", 0))
        )
        reasons = tuple(
            reason
            for passed, reason in (
                (notional <= mandate.maximum_notional, "MAXIMUM_NOTIONAL_EXCEEDED"),
                (losses <= mandate.maximum_loss, "MAXIMUM_LOSS_EXCEEDED"),
            )
            if not passed
        )
        return RiskAssessment(not reasons, reasons)
