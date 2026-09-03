from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TradeTfClient:
	"""Boundary client for upstream authority; transport is injected by the host."""

	transport: object | None = None

	def validate_mandate(self, mandate_id: str) -> dict[str, object]:
		if not mandate_id:
			raise ValueError("mandate_id is required")
		if self.transport is None:
			return {"mandate_id": mandate_id, "eligible": False, "source": "UNAVAILABLE"}
		validator = getattr(self.transport, "validate_mandate", None)
		if validator is None:
			raise TypeError("transport must provide validate_mandate")
		return dict(validator(mandate_id))
