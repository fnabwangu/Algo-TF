from __future__ import annotations

from fastapi import APIRouter, HTTPException

from algo_tf.api.runtime import execution_monitor
from algo_tf.contracts.inbound.execution_update import ExecutionUpdate

router = APIRouter(tags=["execution"])


@router.post("/execution-updates")
def execution_updates(payload: ExecutionUpdate) -> dict[str, object]:
    try:
        status = execution_monitor.apply(payload)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return {"accepted": True, "intent_id": status.intent_id, "status": status.status}
