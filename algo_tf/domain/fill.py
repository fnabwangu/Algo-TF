from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Fill:
	fill_id: str
	intent_id: str
	instrument: str
	quantity: int
	price: float
	occurred_at: datetime

	def __post_init__(self) -> None:
		if self.quantity <= 0 or self.price <= 0:
			raise ValueError("fill quantity and price must be positive")
