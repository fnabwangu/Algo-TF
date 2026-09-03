from __future__ import annotations


class NotificationFilter:
	_material_events = frozenset({"FILL", "REJECTION", "INVALIDATION", "RISK_ALERT", "OUTAGE"})

	def should_notify(self, event_type: str, *, material: bool = False) -> bool:
		return material or event_type.upper() in self._material_events
