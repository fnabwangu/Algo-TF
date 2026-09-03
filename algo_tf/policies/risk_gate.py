def within_risk_limits(
	current_notional: float,
	proposed_notional: float,
	maximum_notional: float,
	current_loss: float,
	maximum_loss: float,
) -> bool:
	return (
		current_notional >= 0
		and proposed_notional >= 0
		and current_notional + proposed_notional <= maximum_notional
		and max(0.0, current_loss) <= maximum_loss
	)
