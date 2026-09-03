from __future__ import annotations

from datetime import datetime, timedelta


def maximum_hold_expired(opened_at: datetime, now: datetime, maximum_hold_minutes: int) -> bool:
	return now >= opened_at + timedelta(minutes=maximum_hold_minutes)


def stop_triggered(
	entry_price: float, current_price: float, stop_price: float, direction: str
) -> bool:
	if direction == "LONG":
		return current_price <= stop_price
	if direction == "SHORT":
		return current_price >= stop_price
	return False
