from __future__ import annotations

from collections.abc import Mapping

TRANSITIONS: Mapping[str, frozenset[str]] = {
    "DRAFT": frozenset({"PENDING_APPROVAL"}),
    "PENDING_APPROVAL": frozenset({"APPROVED"}),
    "APPROVED": frozenset({"ARMED"}),
    "ARMED": frozenset({"ACTIVE"}),
    "ACTIVE": frozenset({"PAUSED", "COMPLETED", "EXPIRED", "REVOKED", "HALTED"}),
    "PAUSED": frozenset({"ACTIVE"}),
    "COMPLETED": frozenset(),
    "EXPIRED": frozenset(),
    "REVOKED": frozenset(),
    "HALTED": frozenset(),
}


def can_transition(current: str, nxt: str) -> bool:
    return nxt in TRANSITIONS.get(current, frozenset())
