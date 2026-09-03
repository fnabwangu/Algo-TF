from __future__ import annotations

from algo_tf.orchestration.event_bus import Event
from algo_tf.persistence.repositories.mandate_repository import MandateRepository


class MandateHandler:
	def __init__(self, repository: MandateRepository) -> None:
		self._repository = repository

	def __call__(self, event: Event) -> None:
		mandate_id = str(event.payload["mandate_id"])
		mandate = self._repository.get(mandate_id)
		if mandate is not None:
			mandate.update(event.payload)
			self._repository.upsert(mandate)
