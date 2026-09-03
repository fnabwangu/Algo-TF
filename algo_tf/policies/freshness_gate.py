from __future__ import annotations

from datetime import datetime


def is_fresh(observed_at: datetime, now: datetime, maximum_age_seconds: float) -> bool:
	age = (now - observed_at).total_seconds()
	return 0 <= age <= maximum_age_seconds
