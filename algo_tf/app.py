from __future__ import annotations

from fastapi import Depends, FastAPI

from algo_tf.api.dependencies import require_api_key
from algo_tf.api.routes import audit, decisions, execution, health, kill_switch, mandates, state

app = FastAPI(title="Algo-TF")

app.include_router(health.router)
app.include_router(mandates.router, dependencies=[Depends(require_api_key)])
app.include_router(state.router, dependencies=[Depends(require_api_key)])
app.include_router(execution.router, dependencies=[Depends(require_api_key)])
app.include_router(decisions.router, dependencies=[Depends(require_api_key)])
app.include_router(audit.router, dependencies=[Depends(require_api_key)])
app.include_router(kill_switch.router, dependencies=[Depends(require_api_key)])
