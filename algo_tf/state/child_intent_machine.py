from __future__ import annotations

from collections.abc import Mapping

TERMINAL = frozenset({"FILLED", "CANCELLED", "REJECTED", "EXPIRED", "HALTED"})
TRANSITIONS: Mapping[str, frozenset[str]] = {
    "CREATED": frozenset({"VALIDATING", "EXPIRED", "HALTED"}),
    "VALIDATING": frozenset({"ACCEPTED", "REJECTED", "EXPIRED", "HALTED"}),
    "ACCEPTED": frozenset({"SUBMITTED", "REJECTED", "EXPIRED", "HALTED"}),
    "SUBMITTED": frozenset(
        {"PARTIALLY_FILLED", "FILLED", "CANCEL_PENDING", "REJECTED", "EXPIRED", "HALTED"}
    ),
    "PARTIALLY_FILLED": frozenset({"FILLED", "CANCEL_PENDING", "EXPIRED", "HALTED"}),
    "CANCEL_PENDING": frozenset({"CANCELLED", "EXPIRED", "HALTED"}),
    "FILLED": frozenset(),
    "CANCELLED": frozenset(),
    "REJECTED": frozenset(),
    "EXPIRED": frozenset(),
    "HALTED": frozenset(),
}


def can_transition(current: str, nxt: str) -> bool:
    return nxt in TRANSITIONS.get(current, frozenset())
