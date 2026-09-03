from __future__ import annotations


def derive_limit_price(*, bid: float, ask: float, side: str, max_slippage_bps: float) -> float:
    if bid <= 0 or ask <= 0 or ask < bid:
        raise ValueError("invalid quote")
    midpoint = (bid + ask) / 2
    half_spread = (ask - bid) / 2
    max_move = midpoint * (max_slippage_bps / 10000)
    bounded_move = min(half_spread, max_move)
    if side == "LONG":
        return round(min(ask, midpoint + bounded_move), 4)
    return round(max(bid, midpoint - bounded_move), 4)
