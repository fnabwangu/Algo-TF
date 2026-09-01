from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["state"])


@router.post("/observations/quote")
def quote_observation(payload: dict[str, object]) -> dict[str, object]:
    return {"accepted": True, "type": "quote", "payload": payload}


@router.post("/observations/gex")
def gex_observation(payload: dict[str, object]) -> dict[str, object]:
    return {"accepted": True, "type": "gex", "payload": payload}


@router.post("/observations/greeks")
def greeks_observation(payload: dict[str, object]) -> dict[str, object]:
    return {"accepted": True, "type": "greeks", "payload": payload}


@router.post("/observations/position")
def position_observation(payload: dict[str, object]) -> dict[str, object]:
    return {"accepted": True, "type": "position", "payload": payload}


@router.post("/eligibility-updates")
def eligibility_updates(payload: dict[str, object]) -> dict[str, object]:
    return {"accepted": True, "type": "eligibility", "payload": payload}
