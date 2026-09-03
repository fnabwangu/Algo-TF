from __future__ import annotations

from algo_tf.persistence.database import Database


class ObservationRepository:
    def __init__(self, database: Database) -> None:
        self._database = database

    def save(
        self, observation_id: str, observation: dict[str, object], instrument: str
    ) -> dict[str, object]:
        return self._database.upsert("observations", observation_id, observation, instrument)

    def latest_for(self, instrument: str) -> dict[str, object] | None:
        observations = self._database.list("observations", instrument)
        return observations[-1] if observations else None
