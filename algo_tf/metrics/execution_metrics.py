from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ExecutionMetrics:
	intents_created: int = 0
	intents_accepted: int = 0
	intents_rejected: int = 0
	fills: int = 0

	@property
	def acceptance_rate(self) -> float:
		total = self.intents_accepted + self.intents_rejected
		return self.intents_accepted / total if total else 0.0
