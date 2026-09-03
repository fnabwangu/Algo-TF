from __future__ import annotations

from algo_tf.domain.position import Position


class PositionReconciler:
	def reconcile(self, expected: Position, actual: Position) -> tuple[bool, str]:
		if expected.instrument != actual.instrument:
			return False, "INSTRUMENT_MISMATCH"
		if expected.quantity != actual.quantity:
			return False, "QUANTITY_MISMATCH"
		return True, "MATCH"
