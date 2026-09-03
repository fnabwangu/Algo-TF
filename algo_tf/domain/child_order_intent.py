from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .enums import AssetClass, Direction, OrderType, TimeInForce


@dataclass(frozen=True, slots=True)
class ChildOrderIntent:
    intent_id: str
    parent_mandate_id: str
    decision_id: str
    strategy_id: str
    sleeve_element_id: str
    instrument: str
    asset_class: AssetClass
    side: Direction
    quantity: int
    order_type: OrderType
    limit_price: float
    time_in_force: TimeInForce
    maximum_slippage_bps: float
    idempotency_key: str
    created_at: datetime
    expires_at: datetime
    evidence_digest: str
    mandate_remaining_capacity: int
