from algo_tf.policies.sizing_policy import calculate_child_quantity


def test_child_quantity_never_exceeds_raw_minimum_even_with_large_coefficients() -> None:
    qty = calculate_child_quantity(
        remaining_target_quantity=10,
        mandate_remaining_quantity=8,
        risk_limited_quantity=9,
        liquidity_limited_quantity=7,
        delta_limited_quantity=6,
        signal_coefficient=10,
        gex_coefficient=10,
        spread_coefficient=10,
        participation_coefficient=10,
        time_coefficient=10,
    )
    assert qty == 6


def test_negative_coefficient_reduces_to_zero() -> None:
    qty = calculate_child_quantity(
        remaining_target_quantity=10,
        mandate_remaining_quantity=10,
        risk_limited_quantity=10,
        liquidity_limited_quantity=10,
        delta_limited_quantity=10,
        signal_coefficient=-1,
        gex_coefficient=1,
        spread_coefficient=1,
        participation_coefficient=1,
        time_coefficient=1,
    )
    assert qty == 0
