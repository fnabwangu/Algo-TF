from __future__ import annotations

from math import floor


def bounded_coefficient(value: float) -> float:
    if value < 0:
        return 0.0
    if value > 1:
        return 1.0
    return value


def floor_to_lot(quantity: float, lot_size: int = 1) -> int:
    if lot_size <= 0:
        raise ValueError("lot_size must be positive")
    if quantity <= 0:
        return 0
    return int(floor(quantity / lot_size) * lot_size)


def calculate_child_quantity(
    *,
    remaining_target_quantity: int,
    mandate_remaining_quantity: int,
    risk_limited_quantity: int,
    liquidity_limited_quantity: int,
    delta_limited_quantity: int,
    signal_coefficient: float,
    gex_coefficient: float,
    spread_coefficient: float,
    participation_coefficient: float,
    time_coefficient: float,
    lot_size: int = 1,
) -> int:
    raw_quantity = min(
        remaining_target_quantity,
        mandate_remaining_quantity,
        risk_limited_quantity,
        liquidity_limited_quantity,
        delta_limited_quantity,
    )
    scalar = (
        bounded_coefficient(signal_coefficient)
        * bounded_coefficient(gex_coefficient)
        * bounded_coefficient(spread_coefficient)
        * bounded_coefficient(participation_coefficient)
        * bounded_coefficient(time_coefficient)
    )
    return floor_to_lot(raw_quantity * scalar, lot_size=lot_size)
