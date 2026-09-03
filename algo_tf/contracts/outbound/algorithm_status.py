from pydantic import BaseModel, ConfigDict, Field


class AlgorithmStatus(BaseModel):
	model_config = ConfigDict(frozen=True, extra="forbid")

	mandate_id: str = Field(min_length=1)
	state: str = Field(min_length=1)
	effective_mode: str = Field(min_length=1)
	healthy: bool
