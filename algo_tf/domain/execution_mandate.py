from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .enums import Action, AssetClass, Direction, OrderType


@dataclass(frozen=True, slots=True)
class ExecutionMandate:
    mandate_id: str
    strategy_id: str
    strategy_version: int
    sleeve_element_id: str
    instrument: str
    asset_class: AssetClass
    direction: Direction
    allowed_actions: tuple[Action, ...]
    maximum_notional: float
    maximum_loss: float
    maximum_slippage_bps: float
    permitted_order_types: tuple[OrderType, ...]
    maximum_child_orders: int
    maximum_reentries: int
    maximum_state_flips: int
    effective_at: datetime
    expires_at: datetime
    is_approved: bool = True
    is_revoked: bool = False
    integrity_ok: bool = True

    def is_valid_at(self, now: datetime) -> bool:
        return (
            self.is_approved
            and (not self.is_revoked)
            and self.integrity_ok
            and self.effective_at <= now < self.expires_at
        )
