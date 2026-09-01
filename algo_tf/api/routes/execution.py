from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["execution"])


@router.post("/execution-updates")
def execution_updates(payload: dict[str, object]) -> dict[str, object]:
    return {"accepted": True, "payload": payload}
