from __future__ import annotations

import hashlib
import json
from datetime import datetime
from enum import Enum
from typing import Any


def _normalize(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {str(k): _normalize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_normalize(v) for v in value]
    return value


def digest_payload(payload: dict[str, Any]) -> str:
    encoded = json.dumps(_normalize(payload), sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
