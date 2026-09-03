from datetime import UTC, datetime, timedelta

from algo_tf.audit.chain import AuditEvent, append_event
from algo_tf.audit.replay import verify_chain
from algo_tf.contracts.inbound.algorithm_design_bundle import AlgorithmDesignBundle
from algo_tf.domain.enums import Action, AssetClass, Direction, OrderType
from algo_tf.domain.execution_mandate import ExecutionMandate
from algo_tf.domain.market_observation import MarketObservation
from algo_tf.services.bundle_compiler import BundleCompiler
from algo_tf.services.decision_engine import DecisionEngine
from algo_tf.settings import settings


def test_decision_does_not_invent_entry_action() -> None:
    now = datetime.now(UTC)
    mandate = ExecutionMandate(
        mandate_id="m1",
        strategy_id="s1",
        strategy_version=1,
        sleeve_element_id="e1",
        instrument="QQQ",
        asset_class=AssetClass.ETF,
        direction=Direction.LONG,
        allowed_actions=(Action.EXIT,),
        maximum_notional=100_000,
        maximum_loss=1_000,
        maximum_slippage_bps=20,
        permitted_order_types=(OrderType.LIMIT,),
        maximum_child_orders=1,
        maximum_reentries=0,
        maximum_state_flips=0,
        effective_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(minutes=1),
    )
    observation = MarketObservation(
        observed_at=now,
        bid=100,
        ask=100.1,
        last=100.05,
        spread_bps=10,
        quote_age_seconds=1,
        market_structure_age_seconds=1,
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

    decision = DecisionEngine().decide(mandate, observation, now)

    assert decision.action is Action.WAIT
    assert decision.reason_codes == ("ACTION_NOT_PERMITTED",)


def test_bundle_compiler_preserves_timing() -> None:
    payload = {
        "schema": "algo-tf.algorithm-design-bundle.v4",
        "bundle_id": "not-a-uuid",
        "created_at": datetime.now(UTC).isoformat(),
        "status": "PROPOSAL_READY",
        "effective_mode": "REPLAY",
        "strategy_specification": {
            "instrument": {
                "symbol": "QQQ",
                "asset_class": "ETF",
                "direction": "LONG",
                "session": "REGULAR",
            }
        },
        "risk_mandate": {"max_dollar_risk": 100, "max_notional": 1_000, "calculate_quantity": True},
        "execution_mandate": {
            "order": {
                "type": "LIMIT",
                "tranches": 1,
                "max_replaces": 0,
                "max_spread_bps": 20,
                "max_slippage_bps": 20,
            },
            "broker_boundary": "ROOT_EXECUTION_ENGINE_ONLY",
            "auto_send": False,
        },
        "testing": {
            "backtest": False,
            "out_of_sample": False,
            "costs": False,
            "sensitivity": False,
            "scenarios": False,
            "paper": False,
            "shadow": False,
        },
    }
    bundle = AlgorithmDesignBundle.model_validate(payload)

    compiled = BundleCompiler().compile(bundle, settings.mode)
    assert compiled["effective_at"] == payload["created_at"]
    assert compiled["expires_at"]


def test_audit_replay_detects_tampering() -> None:
    chain: list[AuditEvent] = []
    append_event(chain, {"type": "one"})
    append_event(chain, {"type": "two"})
    assert verify_chain(chain)
    tampered = list(chain)
    tampered[1] = AuditEvent(previous_hash="tampered", payload_digest=tampered[1].payload_digest)
    assert not verify_chain(tampered)
