from __future__ import annotations

from algo_tf.orchestration.event_bus import EventBus


class Worker:
	def __init__(self, event_bus: EventBus) -> None:
		self.event_bus = event_bus

	def run_once(self) -> int:
		return self.event_bus.drain()
