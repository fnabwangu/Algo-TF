from __future__ import annotations

from fastapi import APIRouter

from algo_tf.api.runtime import decisions, intents

router = APIRouter(tags=["decisions"])


@router.get("/decisions/{decision_id}")
def get_decision(decision_id: str) -> dict[str, object]:
    return decisions.get(decision_id) or {}


@router.get("/mandates/{mandate_id}/decisions")
def list_mandate_decisions(mandate_id: str) -> list[dict[str, object]]:
    return decisions.list_for_mandate(mandate_id)


@router.get("/mandates/{mandate_id}/intents")
def list_mandate_intents(mandate_id: str) -> list[dict[str, object]]:
    return intents.list_for_mandate(mandate_id)
