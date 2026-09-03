from __future__ import annotations

from algo_tf.persistence.database import Database


class AuditRepository:
    def __init__(self, database: Database) -> None:
        self._database = database

    def append(self, event_id: str, event: dict[str, object]) -> dict[str, object]:
        return self._database.upsert("audit_events", event_id, event)

    def list(self) -> list[dict[str, object]]:
        return self._database.list("audit_events")
