from __future__ import annotations

from collections.abc import Iterable

from algo_tf.audit.chain import AuditEvent


def verify_chain(events: Iterable[AuditEvent]) -> bool:
	previous = "GENESIS"
	for event in events:
		if event.previous_hash != previous or event.event_hash == event.previous_hash:
			return False
		previous = event.event_hash
	return True
