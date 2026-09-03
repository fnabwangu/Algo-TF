from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GexSnapshot(BaseModel):
	model_config = ConfigDict(frozen=True, extra="forbid")

	instrument: str = Field(min_length=1)
	observed_at: datetime
	net_gex: float
	gex_coefficient: float = Field(ge=0)
