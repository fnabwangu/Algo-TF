from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Greeks:
	instrument: str
	observed_at: datetime
	delta: float
	gamma: float
	vega: float
	theta: float
