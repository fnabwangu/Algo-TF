from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ExecutionUpdate(BaseModel):
	model_config = ConfigDict(frozen=True, extra="forbid")

	intent_id: str = Field(min_length=1)
	mandate_id: str = Field(min_length=1)
	status: Literal["ACCEPTED", "WORKING", "PARTIALLY_FILLED", "FILLED", "CANCELLED", "REJECTED"]
	updated_at: datetime
	filled_quantity: int = Field(default=0, ge=0)
	average_fill_price: float | None = Field(default=None, gt=0)
	reason: str | None = None
