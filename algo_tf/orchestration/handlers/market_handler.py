from __future__ import annotations

from algo_tf.orchestration.event_bus import Event
from algo_tf.services.observation_service import ObservationService


class MarketHandler:
	def __init__(self, observations: ObservationService) -> None:
		self._observations = observations

	def __call__(self, event: Event) -> None:
		self._observations.record(
			str(event.payload["kind"]), str(event.payload["instrument"]), event.payload
		)
