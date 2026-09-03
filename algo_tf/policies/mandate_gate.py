from __future__ import annotations

from datetime import datetime

from algo_tf.domain.execution_mandate import ExecutionMandate


def mandate_valid(mandate: ExecutionMandate, now: datetime) -> bool:
    return mandate.is_valid_at(now)
