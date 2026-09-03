from __future__ import annotations

from algo_tf.contracts.inbound.execution_update import ExecutionUpdate
from algo_tf.orchestration.event_bus import Event
from algo_tf.services.execution_monitor import ExecutionMonitor


class ExecutionHandler:
	def __init__(self, monitor: ExecutionMonitor) -> None:
		self._monitor = monitor

	def __call__(self, event: Event) -> None:
		self._monitor.apply(ExecutionUpdate.model_validate(event.payload))
