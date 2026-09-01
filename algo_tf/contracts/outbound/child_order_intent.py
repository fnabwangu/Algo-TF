from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class OutboundChildOrderIntent(BaseModel):
    model_config = ConfigDict(frozen=True)

    intent_id: str
    parent_mandate_id: str
    decision_id: str
    strategy_id: str
    sleeve_element_id: str
    instrument: str
    asset_class: str
    side: str
    quantity: int
    order_type: str
    limit_price: float
    time_in_force: str
    maximum_slippage_bps: float
    idempotency_key: str
    created_at: datetime
    expires_at: datetime
    evidence_digest: str
    contract_version: str = "1.0.0"
