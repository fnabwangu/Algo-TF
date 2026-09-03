def eligible_for_action(eligible: bool, action: str) -> bool:
	return eligible or action in {"REDUCE", "EXIT", "HALT"}
