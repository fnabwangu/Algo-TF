from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EligibilityUpdate(BaseModel):
	model_config = ConfigDict(frozen=True, extra="forbid")

	mandate_id: str = Field(min_length=1)
	observed_at: datetime
	eligible: bool
	reason: str | None = None
