from __future__ import annotations

from algo_tf.persistence.database import Database


class DecisionRepository:
    def __init__(self, database: Database) -> None:
        self._database = database

    def save(self, decision: dict[str, object]) -> dict[str, object]:
        return self._database.upsert(
            "decisions", str(decision["decision_id"]), decision, str(decision["mandate_id"])
        )

    def get(self, decision_id: str) -> dict[str, object] | None:
        return self._database.get("decisions", decision_id)

    def list_for_mandate(self, mandate_id: str) -> list[dict[str, object]]:
        return self._database.list("decisions", mandate_id)
