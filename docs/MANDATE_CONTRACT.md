# Mandate Contract

Algo-TF accepts two authority inputs: a direct runtime mandate or an Algo-TF v4 design bundle.
Both paths create `PENDING_APPROVAL` records. They cannot be armed until the authenticated
`/mandates/{mandate_id}/approve` action records an approver, effective window, expiry, and
positive target quantity.

Design bundles are evidence-bearing proposals. The compiler preserves the source bundle and its
digest, derives only supported runtime controls, recomputes the earned deployment mode, and
rejects a proposal that exceeds the configured server mode. Unsupported runtime semantics,
including stop-limit orders, multi-tranche entry, and replacement loops, are rejected rather than
silently discarded.

Every proposal, compilation, approval, revocation, and mandate state transition appends a
hash-chained audit event. Scheduler execution is permitted only for armed or active mandates and
adds a position-aware risk check before an intent can be persisted.
