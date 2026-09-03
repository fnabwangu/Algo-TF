from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass
from threading import RLock


@dataclass(frozen=True, slots=True)
class Event:
	topic: str
	payload: dict[str, object]


EventHandler = Callable[[Event], None]


class EventBus:
	def __init__(self) -> None:
		self._handlers: dict[str, list[EventHandler]] = defaultdict(list)
		self._events: deque[Event] = deque()
		self._lock = RLock()

	def subscribe(self, topic: str, handler: EventHandler) -> None:
		with self._lock:
			self._handlers[topic].append(handler)

	def publish(self, event: Event) -> None:
		with self._lock:
			self._events.append(event)

	def drain(self) -> int:
		processed = 0
		while True:
			with self._lock:
				if not self._events:
					return processed
				event = self._events.popleft()
				handlers = tuple(self._handlers.get(event.topic, ()))
			for handler in handlers:
				handler(event)
			processed += 1
