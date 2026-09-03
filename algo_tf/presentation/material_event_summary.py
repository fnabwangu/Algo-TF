from __future__ import annotations


def summarize_material_event(event_type: str, payload: dict[str, object]) -> str:
	event = event_type.upper()
	mandate_id = payload.get("mandate_id", "unknown")
	reason = payload.get("reason") or payload.get("reason_code")
	return f"{event} for mandate {mandate_id}" + (f": {reason}" if reason else "")
