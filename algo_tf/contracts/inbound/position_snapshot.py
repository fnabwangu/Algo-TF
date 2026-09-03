from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PositionSnapshot(BaseModel):
	model_config = ConfigDict(frozen=True, extra="forbid")

	instrument: str = Field(min_length=1)
	observed_at: datetime
	quantity: int
	average_price: float = Field(ge=0)
	realized_pnl: float = 0
	unrealized_pnl: float = 0
