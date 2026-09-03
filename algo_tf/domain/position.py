from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Position:
	instrument: str
	quantity: int
	average_price: float
	observed_at: datetime
	realized_pnl: float = 0.0
	unrealized_pnl: float = 0.0

	@property
	def notional(self) -> float:
		return abs(self.quantity) * self.average_price

	@property
	def total_pnl(self) -> float:
		return self.realized_pnl + self.unrealized_pnl
