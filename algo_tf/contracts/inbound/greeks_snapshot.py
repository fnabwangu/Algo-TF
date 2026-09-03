from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GreeksSnapshot(BaseModel):
	model_config = ConfigDict(frozen=True, extra="forbid")

	instrument: str = Field(min_length=1)
	observed_at: datetime
	delta: float
	gamma: float
	vega: float
	theta: float
