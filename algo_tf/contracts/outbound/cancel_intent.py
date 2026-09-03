from pydantic import BaseModel, ConfigDict, Field


class CancelIntent(BaseModel):
	model_config = ConfigDict(frozen=True, extra="forbid")

	intent_id: str = Field(min_length=1)
	mandate_id: str = Field(min_length=1)
	reason: str = Field(min_length=1)
