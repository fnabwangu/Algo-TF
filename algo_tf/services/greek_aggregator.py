from __future__ import annotations

from collections.abc import Iterable

from algo_tf.domain.greeks import Greeks


def aggregate_greeks(snapshots: Iterable[Greeks]) -> Greeks | None:
	values = list(snapshots)
	if not values:
		return None
	first = values[0]
	return Greeks(
		instrument=first.instrument,
		observed_at=max(value.observed_at for value in values),
		delta=sum(value.delta for value in values),
		gamma=sum(value.gamma for value in values),
		vega=sum(value.vega for value in values),
		theta=sum(value.theta for value in values),
	)
