from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class GexSnapshot:
	instrument: str
	observed_at: datetime
	net_gex: float
	gamma_flip: float | None = None

	@property
	def regime(self) -> str:
		if self.net_gex > 0:
			return "POSITIVE"
		if self.net_gex < 0:
			return "NEGATIVE"
		return "NEUTRAL"
