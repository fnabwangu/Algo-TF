from __future__ import annotations

from algo_tf.persistence.repositories.observation_repository import ObservationRepository


class OptionReader:
    def __init__(self, observations: ObservationRepository) -> None:
        self._observations = observations

    def latest_gex(self, instrument: str) -> dict[str, object] | None:
        return self._observations.latest_for(f"gex:{instrument}")

    def latest_greeks(self, instrument: str) -> dict[str, object] | None:
        return self._observations.latest_for(f"greeks:{instrument}")
