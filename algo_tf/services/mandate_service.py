from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MandateService:
    active_mandates: dict[str, dict[str, object]]

    def __init__(self) -> None:
        self.active_mandates = {}

    def upsert(self, mandate_id: str, payload: dict[str, object]) -> dict[str, object]:
        self.active_mandates[mandate_id] = payload
        return payload

    def get(self, mandate_id: str) -> dict[str, object] | None:
        return self.active_mandates.get(mandate_id)
