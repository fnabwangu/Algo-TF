from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class MarketObservation:
    observed_at: datetime
    bid: float
    ask: float
    last: float
    spread_bps: float
    quote_age_seconds: float
    market_structure_age_seconds: float
    liquidity_score: float
    signal_coefficient: float
    gex_coefficient: float
    spread_coefficient: float
    participation_coefficient: float
    time_coefficient: float
    risk_budget_available: bool
    confirmation_pass: bool
    market_open: bool
    execution_engine_available: bool
    kill_switch_clear: bool
    strategy_eligible: bool
    target_remaining_quantity: int
    gex_fresh: bool
    quote_fresh: bool
