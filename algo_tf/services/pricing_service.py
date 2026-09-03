from __future__ import annotations


class PricingService:
	def limit_price(self, bid: float, ask: float, side: str, slippage_bps: float) -> float:
		if bid <= 0 or ask < bid or slippage_bps < 0:
			raise ValueError("invalid quote or slippage")
		spread = ask - bid
		if side == "LONG":
			return min(ask, bid + spread * slippage_bps / 100)
		if side == "SHORT":
			return max(bid, ask - spread * slippage_bps / 100)
		raise ValueError("side must be LONG or SHORT")
