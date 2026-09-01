from __future__ import annotations

from fastapi import APIRouter, HTTPException

from algo_tf.contracts.inbound.execution_mandate import InboundExecutionMandate

router = APIRouter(prefix="/mandates", tags=["mandates"])
_store: dict[str, dict[str, object]] = {}


@router.post("")
def ingest_mandate(payload: InboundExecutionMandate) -> dict[str, object]:
    doc = payload.model_dump(mode="json")
    doc["state"] = "APPROVED"
    _store[payload.mandate_id] = doc
    return doc


@router.post("/{mandate_id}/arm")
def arm_mandate(mandate_id: str) -> dict[str, str]:
    mandate = _store.get(mandate_id)
    if mandate is None:
        raise HTTPException(status_code=404, detail="not found")
    mandate["state"] = "ARMED"
    return {"mandate_id": mandate_id, "state": "ARMED"}


@router.post("/{mandate_id}/pause")
def pause_mandate(mandate_id: str) -> dict[str, str]:
    mandate = _store.get(mandate_id)
    if mandate is None:
        raise HTTPException(status_code=404, detail="not found")
    mandate["state"] = "PAUSED"
    return {"mandate_id": mandate_id, "state": "PAUSED"}


@router.post("/{mandate_id}/revoke")
def revoke_mandate(mandate_id: str) -> dict[str, str]:
    mandate = _store.get(mandate_id)
    if mandate is None:
        raise HTTPException(status_code=404, detail="not found")
    mandate["state"] = "REVOKED"
    return {"mandate_id": mandate_id, "state": "REVOKED"}


@router.get("/{mandate_id}")
def get_mandate(mandate_id: str) -> dict[str, object]:
    mandate = _store.get(mandate_id)
    if mandate is None:
        raise HTTPException(status_code=404, detail="not found")
    return mandate


@router.get("/{mandate_id}/state")
def get_mandate_state(mandate_id: str) -> dict[str, str]:
    mandate = _store.get(mandate_id)
    if mandate is None:
        raise HTTPException(status_code=404, detail="not found")
    state = mandate.get("state", "UNKNOWN")
    return {"mandate_id": mandate_id, "state": str(state)}
