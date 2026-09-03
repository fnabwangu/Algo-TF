from __future__ import annotations

from collections.abc import Mapping

TRANSITIONS: Mapping[str, frozenset[str]] = {
    "ARMED": frozenset({"MONITORING"}),
    "MONITORING": frozenset({"WORKING", "HALTED", "EXPIRED"}),
    "WORKING": frozenset({"PARTIALLY_FILLED", "FILLED", "HALTED", "EXPIRED"}),
    "PARTIALLY_FILLED": frozenset({"WORKING"}),
    "FILLED": frozenset({"MANAGING"}),
    "MANAGING": frozenset({"REDUCING", "EXITING", "HALTED"}),
    "REDUCING": frozenset({"MANAGING", "EXITING", "HALTED"}),
    "EXITING": frozenset({"CLOSED", "HALTED"}),
    "CLOSED": frozenset(),
    "HALTED": frozenset(),
    "EXPIRED": frozenset(),
}


def can_transition(current: str, nxt: str) -> bool:
    return nxt in TRANSITIONS.get(current, frozenset())
