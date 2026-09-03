from __future__ import annotations

from fastapi import APIRouter

from algo_tf.api.runtime import audit

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/events")
def audit_events() -> list[dict[str, object]]:
    return audit.list()
