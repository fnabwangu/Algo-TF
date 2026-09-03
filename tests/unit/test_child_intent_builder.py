from datetime import UTC, datetime, timedelta

from algo_tf.domain.algorithm_decision import AlgorithmDecision
from algo_tf.domain.enums import Action, AssetClass, Direction, OrderType
from algo_tf.domain.execution_mandate import ExecutionMandate
from algo_tf.services.child_intent_builder import ChildIntentBuilder


def test_idempotency_key_stable_for_same_inputs() -> None:
    now = datetime.now(UTC)
    mandate = ExecutionMandate(
        mandate_id="m1",
        strategy_id="s1",
        strategy_version=1,
        sleeve_element_id="el1",
        instrument="QQQ",
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
    decision = AlgorithmDecision(
        decision_id="d1",
        mandate_id="m1",
        strategy_id="s1",
        strategy_version=1,
        action=Action.ENTER,
        requested_quantity=3,
        limit_price=100.1,
        gate_results={"all": True},
        reason_codes=("ok",),
        policy_name="ADAPTIVE_LIMIT_V1",
        policy_version="1.0.0",
        created_at=now,
        expires_at=now + timedelta(seconds=30),
        observation_digest="abc",
        deterministic_input_hash="def",
    )

    builder = ChildIntentBuilder()
    i1 = builder.build(mandate, decision, now)
    i2 = builder.build(mandate, decision, now)

    assert i1 is not None and i2 is not None
    assert i1.idempotency_key == i2.idempotency_key
