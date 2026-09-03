from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/kill-switch", tags=["kill-switch"])
_status = {"active": False}


@router.post("/activate")
def activate() -> dict[str, bool]:
    _status["active"] = True
    return {"active": True}


@router.get("/status")
def status() -> dict[str, bool]:
    return {"active": bool(_status["active"])}
