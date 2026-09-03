from __future__ import annotations

from algo_tf.persistence.database import Database


class IntentRepository:
    def __init__(self, database: Database) -> None:
        self._database = database

    def save(self, intent: dict[str, object]) -> dict[str, object]:
        return self._database.upsert(
            "intents", str(intent["intent_id"]), intent, str(intent["parent_mandate_id"])
        )

    def get(self, intent_id: str) -> dict[str, object] | None:
        return self._database.get("intents", intent_id)

    def list_for_mandate(self, mandate_id: str) -> list[dict[str, object]]:
        return self._database.list("intents", mandate_id)
