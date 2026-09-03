from __future__ import annotations

from dataclasses import dataclass

from .hashing import digest_payload


@dataclass(frozen=True, slots=True)
class AuditEvent:
    previous_hash: str
    payload_digest: str

    @property
    def event_hash(self) -> str:
        payload = {
            "previous_hash": self.previous_hash,
            "payload_digest": self.payload_digest,
        }
        return digest_payload(payload)


def append_event(chain: list[AuditEvent], payload: dict[str, object]) -> AuditEvent:
    previous = chain[-1].event_hash if chain else "GENESIS"
    event = AuditEvent(previous_hash=previous, payload_digest=digest_payload(payload))
    chain.append(event)
    return event
