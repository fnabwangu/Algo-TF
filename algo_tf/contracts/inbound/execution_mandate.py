from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InboundExecutionMandate(BaseModel):
    model_config = ConfigDict(frozen=True)

    mandate_id: str
    strategy_id: str
    strategy_version: int
    sleeve_element_id: str
    instrument: str
    asset_class: str
    direction: str
    maximum_notional: float
    maximum_loss: float
    maximum_slippage_bps: float
    allowed_actions: tuple[str, ...]
    maximum_child_orders: int
    maximum_reentries: int
    maximum_state_flips: int
    permitted_order_types: tuple[str, ...]
    effective_at: datetime
    expires_at: datetime
    contract_version: str = "1.0.0"
