from __future__ import annotations

from algo_tf.persistence.database import Database


class MandateRepository:
    def __init__(self, database: Database) -> None:
        self._database = database

    def upsert(self, mandate: dict[str, object]) -> dict[str, object]:
        return self._database.upsert("mandates", str(mandate["mandate_id"]), mandate)

    def get(self, mandate_id: str) -> dict[str, object] | None:
        return self._database.get("mandates", mandate_id)

    def list(self) -> list[dict[str, object]]:
        return self._database.list("mandates")
