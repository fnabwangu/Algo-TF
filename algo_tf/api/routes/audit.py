from __future__ import annotations

from fastapi import APIRouter

from algo_tf.audit.chain import AuditEvent

router = APIRouter(prefix="/audit", tags=["audit"])
_audit: list[AuditEvent] = []


@router.get("/events")
def audit_events() -> list[dict[str, str]]:
    return [{"previous_hash": e.previous_hash, "event_hash": e.event_hash} for e in _audit]
