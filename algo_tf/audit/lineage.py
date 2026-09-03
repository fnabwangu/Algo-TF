from __future__ import annotations

from algo_tf.audit.hashing import digest_payload


def lineage_digest(*digests: str) -> str:
	return digest_payload({"digests": list(digests)})
