from __future__ import annotations

from fastapi import APIRouter, HTTPException

from algo_tf.api.runtime import mandates, observations
from algo_tf.contracts.inbound.eligibility_update import EligibilityUpdate
from algo_tf.contracts.inbound.gex_snapshot import GexSnapshot
from algo_tf.contracts.inbound.greeks_snapshot import GreeksSnapshot
from algo_tf.contracts.inbound.position_snapshot import PositionSnapshot
from algo_tf.contracts.inbound.quote_snapshot import QuoteSnapshot

router = APIRouter(tags=["state"])


@router.post("/observations/quote")
def quote_observation(payload: QuoteSnapshot) -> dict[str, object]:
    observations.record("quote", payload.instrument, payload.model_dump(mode="json"))
    return {"accepted": True, "type": "quote"}


@router.post("/observations/gex")
def gex_observation(payload: GexSnapshot) -> dict[str, object]:
    observations.record("gex", payload.instrument, payload.model_dump(mode="json"))
    return {"accepted": True, "type": "gex"}


@router.post("/observations/greeks")
def greeks_observation(payload: GreeksSnapshot) -> dict[str, object]:
    observations.record("greeks", payload.instrument, payload.model_dump(mode="json"))
    return {"accepted": True, "type": "greeks"}


@router.post("/observations/position")
def position_observation(payload: PositionSnapshot) -> dict[str, object]:
    observations.record("position", payload.instrument, payload.model_dump(mode="json"))
    return {"accepted": True, "type": "position"}


@router.post("/eligibility-updates")
def eligibility_updates(payload: EligibilityUpdate) -> dict[str, object]:
    mandate = mandates.get(payload.mandate_id)
    if mandate is None:
        raise HTTPException(status_code=404, detail="not found")
    mandate["eligible"] = payload.eligible
    mandates.upsert(mandate)
    return {"accepted": True, "type": "eligibility"}
