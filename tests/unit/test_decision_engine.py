from dataclasses import replace
from datetime import UTC, datetime, timedelta

from algo_tf.domain.enums import Action, AssetClass, Direction, OrderType
from algo_tf.domain.execution_mandate import ExecutionMandate
from algo_tf.domain.market_observation import MarketObservation
from algo_tf.services.decision_engine import DecisionEngine


def _mandate(now: datetime) -> ExecutionMandate:
    return ExecutionMandate(
        mandate_id="m1",
        strategy_id="s1",
        strategy_version=1,
        sleeve_element_id="e1",
        instrument="QQQ",
        asset_class=AssetClass.ETF,
        direction=Direction.LONG,
        allowed_actions=(Action.ENTER, Action.SCALE_IN, Action.REDUCE, Action.EXIT),
        maximum_notional=100000,
        maximum_loss=3000,
        maximum_slippage_bps=20,
        permitted_order_types=(OrderType.LIMIT,),
        maximum_child_orders=5,
        maximum_reentries=1,
        maximum_state_flips=2,
        effective_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(minutes=30),
    )


def _observation(now: datetime) -> MarketObservation:
    return MarketObservation(
        observed_at=now,
        bid=100.0,
        ask=100.2,
        last=100.1,
        spread_bps=15,
        quote_age_seconds=1,
        market_structure_age_seconds=30,
        liquidity_score=1.0,
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


def test_hard_gate_cannot_be_overridden_by_coefficients() -> None:
    now = datetime.now(UTC)
    mandate = _mandate(now)
    obs = replace(_observation(now), quote_fresh=False, signal_coefficient=1.0)

    decision = DecisionEngine().decide(mandate, obs, now)

    assert decision.action == Action.WAIT
    assert decision.requested_quantity == 0
    assert decision.gate_results["quote_fresh"] is False


def test_all_gates_pass_produces_enter() -> None:
    now = datetime.now(UTC)
    decision = DecisionEngine().decide(_mandate(now), _observation(now), now)

    assert decision.action == Action.ENTER
    assert decision.requested_quantity > 0
    assert decision.limit_price is not None
