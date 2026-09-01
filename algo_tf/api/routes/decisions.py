from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["decisions"])

_decisions: dict[str, dict[str, object]] = {}
_mandate_decisions: dict[str, list[str]] = {}


@router.get("/decisions/{decision_id}")
def get_decision(decision_id: str) -> dict[str, object]:
    return _decisions.get(decision_id, {})


@router.get("/mandates/{mandate_id}/decisions")
def list_mandate_decisions(mandate_id: str) -> list[str]:
    return _mandate_decisions.get(mandate_id, [])


@router.get("/mandates/{mandate_id}/intents")
def list_mandate_intents(mandate_id: str) -> list[dict[str, str]]:
    return [{"mandate_id": mandate_id, "note": "intents are emitted to execution engine adapter"}]
