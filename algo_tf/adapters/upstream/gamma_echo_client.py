from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GammaEchoClient:
	"""Boundary client for GEX evidence; no direct market or broker access."""

	transport: object | None = None

	def snapshot(self, instrument: str) -> dict[str, object] | None:
		if not instrument:
			raise ValueError("instrument is required")
		if self.transport is None:
			return None
		reader = getattr(self.transport, "snapshot", None)
		if reader is None:
			raise TypeError("transport must provide snapshot")
		result = reader(instrument)
		return dict(result) if result is not None else None
