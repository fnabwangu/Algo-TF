def delta_limited_quantity(
	target_quantity: int, current_delta: float, target_delta: float, price: float
) -> int:
	if target_quantity <= 0 or price <= 0 or target_delta <= 0:
		return 0
	remaining = max(0.0, target_delta - abs(current_delta))
	return min(target_quantity, int(remaining / price))
