def gex_regime_allowed(regime: str, permitted_regimes: tuple[str, ...]) -> bool:
	return regime.upper() in {value.upper() for value in permitted_regimes}


def adverse_gamma_flip(net_gex: float, previous_net_gex: float, direction: str) -> bool:
	if direction == "LONG":
		return previous_net_gex >= 0 and net_gex < 0
	if direction == "SHORT":
		return previous_net_gex <= 0 and net_gex > 0
	return False
