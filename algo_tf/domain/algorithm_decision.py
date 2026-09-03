from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .enums import Action


@dataclass(frozen=True, slots=True)
class AlgorithmDecision:
    decision_id: str
    mandate_id: str
    strategy_id: str
    strategy_version: int
    action: Action
    requested_quantity: int
    limit_price: float | None
    gate_results: dict[str, bool]
    reason_codes: tuple[str, ...]
    policy_name: str
    policy_version: str
    created_at: datetime
    expires_at: datetime
    observation_digest: str
    deterministic_input_hash: str
