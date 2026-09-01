from algo_tf.policies.sizing_policy import calculate_child_quantity


def test_negative_gamma_can_reduce_size_but_not_reverse_direction() -> None:
    qty = calculate_child_quantity(
        remaining_target_quantity=10,
        mandate_remaining_quantity=10,
        risk_limited_quantity=10,
        liquidity_limited_quantity=10,
        delta_limited_quantity=10,
        signal_coefficient=1,
        gex_coefficient=0.4,
        spread_coefficient=1,
        participation_coefficient=1,
        time_coefficient=1,
    )
    assert qty == 4
