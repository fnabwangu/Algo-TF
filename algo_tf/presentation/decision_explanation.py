from __future__ import annotations

from algo_tf.domain.algorithm_decision import AlgorithmDecision


def explain_decision(decision: AlgorithmDecision) -> dict[str, object]:
	failed = tuple(name for name, passed in decision.gate_results.items() if not passed)
	return {
		"decision_id": decision.decision_id,
		"action": decision.action.value,
		"quantity": decision.requested_quantity,
		"reason_codes": decision.reason_codes,
		"failed_gates": failed,
		"policy": f"{decision.policy_name}:{decision.policy_version}",
	}
