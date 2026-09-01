from datetime import UTC, datetime, timedelta

from algo_tf.domain.enums import Action, AssetClass, Direction, OrderType
from algo_tf.domain.execution_mandate import ExecutionMandate
from algo_tf.domain.market_observation import MarketObservation
from algo_tf.services.decision_engine import DecisionEngine


def test_same_input_produces_same_hash() -> None:
    now = datetime.now(UTC)
    mandate = ExecutionMandate(
        mandate_id='m1',
        strategy_id='s1',
        strategy_version=1,
        sleeve_element_id='el1',
        instrument='QQQ',
        asset_class=AssetClass.ETF,
        direction=Direction.LONG,
        allowed_actions=(Action.ENTER,),
        maximum_notional=100000,
        maximum_loss=1000,
        maximum_slippage_bps=20,
        permitted_order_types=(OrderType.LIMIT,),
        maximum_child_orders=5,
        maximum_reentries=1,
        maximum_state_flips=2,
        effective_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(minutes=10),
    )
    obs = MarketObservation(
        observed_at=now,
        bid=100,
        ask=100.2,
        last=100.1,
        spread_bps=15,
        quote_age_seconds=1,
        market_structure_age_seconds=10,
        liquidity_score=1,
        signal_coefficient=1,
        gex_coefficient=1,
        spread_coefficient=1,
        participation_coefficient=1,
        time_coefficient=1,
        risk_budget_available=True,
        confirmation_pass=True,
        market_open=True,
        execution_engine_available=True,
        kill_switch_clear=True,
        strategy_eligible=True,
        target_remaining_quantity=10,
        gex_fresh=True,
        quote_fresh=True,
    )

    engine = DecisionEngine()
    d1 = engine.decide(mandate, obs, now)
    d2 = engine.decide(mandate, obs, now)

    assert d1.deterministic_input_hash == d2.deterministic_input_hash
