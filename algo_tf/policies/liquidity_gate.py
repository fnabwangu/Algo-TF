def spread_within_limit(spread_bps: float, maximum_spread_bps: float) -> bool:
	return spread_bps >= 0 and maximum_spread_bps >= 0 and spread_bps <= maximum_spread_bps


def liquidity_quantity(target_quantity: int, liquidity_score: float) -> int:
	if target_quantity <= 0 or liquidity_score <= 0:
		return 0
	return min(target_quantity, max(1, int(target_quantity * min(liquidity_score, 1.0))))
