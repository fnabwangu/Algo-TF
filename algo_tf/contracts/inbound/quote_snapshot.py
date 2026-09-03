from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class QuoteSnapshot(BaseModel):
	model_config = ConfigDict(frozen=True, extra="forbid")

	instrument: str = Field(min_length=1)
	observed_at: datetime
	bid: float = Field(gt=0)
	ask: float = Field(gt=0)
	last: float = Field(gt=0)

	@model_validator(mode="after")
	def bid_does_not_exceed_ask(self) -> QuoteSnapshot:
		if self.bid > self.ask:
			raise ValueError("bid must not exceed ask")
		return self
