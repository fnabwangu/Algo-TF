from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class HealthMetrics:
	observations_received: int = 0
	stale_observations: int = 0
	execution_updates: int = 0
	errors: int = 0

	@property
	def healthy(self) -> bool:
		return self.errors == 0
