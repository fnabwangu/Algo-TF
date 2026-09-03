from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from algo_tf.api.runtime import audit, mandates
from algo_tf.audit.chain import AuditEvent
from algo_tf.audit.hashing import digest_payload
from algo_tf.contracts.inbound.algorithm_design_bundle import AlgorithmDesignBundle
from algo_tf.contracts.inbound.execution_mandate import InboundExecutionMandate
from algo_tf.contracts.inbound.mandate_approval import MandateApproval
from algo_tf.services.bundle_compiler import BundleCompiler
from algo_tf.settings import settings
from algo_tf.state.mandate_machine import can_transition

router = APIRouter(prefix="/mandates", tags=["mandates"])


@router.post("")
def ingest_mandate(payload: InboundExecutionMandate) -> dict[str, object]:
    doc = payload.model_dump(mode="json")
    doc["state"] = "PENDING_APPROVAL"
    doc["eligible"] = False
    doc["target_remaining_quantity"] = 0
    stored = mandates.upsert(doc)
    _record_audit("MANDATE_PROPOSED", stored)
    return stored


@router.post("/design-bundles")
def ingest_design_bundle(payload: AlgorithmDesignBundle) -> dict[str, object]:
    try:
        mandate = BundleCompiler().compile(payload, settings.mode)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    stored = mandates.upsert(mandate)
    _record_audit("DESIGN_BUNDLE_COMPILED", stored)
    return stored


@router.post("/{mandate_id}/approve")
def approve_mandate(mandate_id: str, payload: MandateApproval) -> dict[str, object]:
    mandate = mandates.get(mandate_id)
    if mandate is None:
        raise HTTPException(status_code=404, detail="not found")
    if not can_transition(str(mandate["state"]), "APPROVED"):
        raise HTTPException(status_code=409, detail="mandate is not pending approval")
    mandate.update(payload.model_dump(mode="json"))
    mandate["state"] = "APPROVED"
    mandate["eligible"] = True
    stored = mandates.upsert(mandate)
    _record_audit("MANDATE_APPROVED", stored)
    return stored


@router.post("/{mandate_id}/arm")
def arm_mandate(mandate_id: str) -> dict[str, str]:
    return _transition(mandate_id, "ARMED")


@router.post("/{mandate_id}/pause")
def pause_mandate(mandate_id: str) -> dict[str, str]:
    return _transition(mandate_id, "PAUSED")


@router.post("/{mandate_id}/revoke")
def revoke_mandate(mandate_id: str) -> dict[str, str]:
    mandate = mandates.get(mandate_id)
    if mandate is None:
        raise HTTPException(status_code=404, detail="not found")
    mandate["state"] = "REVOKED"
    mandates.upsert(mandate)
    _record_audit("MANDATE_REVOKED", mandate)
    return {"mandate_id": mandate_id, "state": "REVOKED"}


@router.get("/{mandate_id}")
def get_mandate(mandate_id: str) -> dict[str, object]:
    mandate = mandates.get(mandate_id)
    if mandate is None:
        raise HTTPException(status_code=404, detail="not found")
    return mandate


@router.get("/{mandate_id}/state")
def get_mandate_state(mandate_id: str) -> dict[str, str]:
    mandate = mandates.get(mandate_id)
    if mandate is None:
        raise HTTPException(status_code=404, detail="not found")
    state = mandate.get("state", "UNKNOWN")
    return {"mandate_id": mandate_id, "state": str(state)}


def _transition(mandate_id: str, state: str) -> dict[str, str]:
    mandate = mandates.get(mandate_id)
    if mandate is None:
        raise HTTPException(status_code=404, detail="not found")
    current = str(mandate["state"])
    if not can_transition(current, state):
        raise HTTPException(status_code=409, detail=f"invalid transition: {current} -> {state}")
    mandate["state"] = state
    mandates.upsert(mandate)
    _record_audit("MANDATE_STATE_CHANGED", mandate)
    return {"mandate_id": mandate_id, "state": state}


def _record_audit(event_type: str, mandate: dict[str, object]) -> None:
    payload = {
        "event_type": event_type,
        "mandate_id": mandate["mandate_id"],
        "state": mandate["state"],
        "source_bundle_digest": mandate.get("source_bundle_digest"),
    }
    existing = audit.list()
    previous_hash = str(existing[-1]["event_hash"]) if existing else "GENESIS"
    event = AuditEvent(previous_hash=previous_hash, payload_digest=digest_payload(payload))
    audit.append(
        str(uuid4()),
        {
            "event_id": str(uuid4()),
            "occurred_at": datetime.now(UTC).isoformat(),
            "event_type": event_type,
            "mandate_id": mandate["mandate_id"],
            "previous_hash": event.previous_hash,
            "payload_digest": event.payload_digest,
            "event_hash": event.event_hash,
        },
    )
