from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class MandateApproval(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    approved_by: str = Field(min_length=1)
    effective_at: datetime
    expires_at: datetime
    target_remaining_quantity: int = Field(gt=0)

    @model_validator(mode="after")
    def approval_window_is_valid(self) -> MandateApproval:
        if self.expires_at <= self.effective_at:
            raise ValueError("expires_at must follow effective_at")
        return self