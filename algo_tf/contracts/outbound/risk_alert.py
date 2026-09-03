from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RiskAlert(BaseModel):
	model_config = ConfigDict(frozen=True, extra="forbid")

	mandate_id: str = Field(min_length=1)
	reason_codes: tuple[str, ...] = Field(min_length=1)
	occurred_at: datetime
