from __future__ import annotations

from algo_tf.persistence.repositories.observation_repository import ObservationRepository


class PositionReader:
    def __init__(self, observations: ObservationRepository) -> None:
        self._observations = observations

    def latest(self, instrument: str) -> dict[str, object] | None:
        return self._observations.latest_for(f"position:{instrument}")
