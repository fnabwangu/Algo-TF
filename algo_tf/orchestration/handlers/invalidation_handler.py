from __future__ import annotations

from algo_tf.orchestration.event_bus import Event
from algo_tf.persistence.repositories.mandate_repository import MandateRepository


class InvalidationHandler:
	def __init__(self, repository: MandateRepository) -> None:
		self._repository = repository

	def __call__(self, event: Event) -> None:
		mandate = self._repository.get(str(event.payload["mandate_id"]))
		if mandate is not None:
			mandate["eligible"] = False
			mandate["invalidation_reason"] = event.payload.get("reason", "UPSTREAM_INVALIDATION")
			self._repository.upsert(mandate)
