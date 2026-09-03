from datetime import UTC, datetime, timedelta

import pytest

from algo_tf.contracts.inbound.execution_update import ExecutionUpdate
from algo_tf.domain.enums import Action, AssetClass, Direction, OrderType
from algo_tf.domain.execution_mandate import ExecutionMandate
from algo_tf.orchestration.scheduler import Scheduler
from algo_tf.persistence.database import Database
from algo_tf.persistence.repositories.decision_repository import DecisionRepository
from algo_tf.persistence.repositories.intent_repository import IntentRepository
from algo_tf.persistence.repositories.mandate_repository import MandateRepository
from algo_tf.persistence.repositories.observation_repository import ObservationRepository
from algo_tf.services.execution_monitor import ExecutionMonitor
from algo_tf.services.observation_service import ObservationService
from algo_tf.services.risk_monitor import RiskMonitor


def mandate(now: datetime) -> ExecutionMandate:
    return ExecutionMandate(
        mandate_id="m1",
        strategy_id="s1",
        strategy_version=1,
        sleeve_element_id="e1",
        instrument="QQQ",
        asset_class=AssetClass.ETF,
        direction=Direction.LONG,
        allowed_actions=(Action.ENTER,),
        maximum_notional=1_000,
        maximum_loss=100,
        maximum_slippage_bps=20,
        permitted_order_types=(OrderType.LIMIT,),
        maximum_child_orders=2,
        maximum_reentries=0,
        maximum_state_flips=0,
        effective_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(minutes=1),
    )


def test_document_repositories_are_durable_and_parent_scoped() -> None:
    database = Database()
    mandates = MandateRepository(database)
    decisions = DecisionRepository(database)
    intents = IntentRepository(database)
    mandates.upsert({"mandate_id": "m1", "state": "ARMED"})
    decisions.save({"decision_id": "d1", "mandate_id": "m1"})
    intents.save({"intent_id": "i1", "parent_mandate_id": "m1"})

    assert mandates.get("m1") == {"mandate_id": "m1", "state": "ARMED"}
    assert decisions.list_for_mandate("m1") == [{"decision_id": "d1", "mandate_id": "m1"}]
    assert intents.list_for_mandate("m1") == [{"intent_id": "i1", "parent_mandate_id": "m1"}]


def test_risk_monitor_blocks_loss_and_notional_breaches() -> None:
    now = datetime.now(UTC)
    assessment = RiskMonitor().assess(
        mandate(now),
        {"quantity": 10, "average_price": 100, "realized_pnl": -101, "unrealized_pnl": 0},
        1,
    )

    assert assessment.approved is False
    assert set(assessment.reason_codes) == {"MAXIMUM_NOTIONAL_EXCEEDED", "MAXIMUM_LOSS_EXCEEDED"}


def test_execution_monitor_rejects_regressive_or_terminal_updates() -> None:
    monitor = ExecutionMonitor()
    update = ExecutionUpdate(
        intent_id="i1",
        mandate_id="m1",
        status="PARTIALLY_FILLED",
        updated_at=datetime.now(UTC),
        filled_quantity=1,
        average_fill_price=100,
    )
    assert monitor.apply(update).status == "PARTIALLY_FILLED"
    with pytest.raises(ValueError, match="filled quantity cannot decrease"):
        monitor.apply(update.model_copy(update={"filled_quantity": 0}))
    assert (
        monitor.apply(update.model_copy(update={"status": "FILLED", "filled_quantity": 2})).status
        == "FILLED"
    )
    with pytest.raises(ValueError, match="invalid execution transition"):
        monitor.apply(update.model_copy(update={"status": "CANCELLED", "filled_quantity": 2}))


def test_scheduler_persists_decision_and_intent_for_armed_mandate() -> None:
    now = datetime.now(UTC)
    database = Database()
    mandate_repository = MandateRepository(database)
    decision_repository = DecisionRepository(database)
    intent_repository = IntentRepository(database)
    observation_service = ObservationService(ObservationRepository(database))
    record = {
        "mandate_id": "m1",
        "strategy_id": "s1",
        "strategy_version": 1,
        "sleeve_element_id": "e1",
        "instrument": "QQQ",
        "asset_class": "ETF",
        "direction": "LONG",
        "allowed_actions": ["ENTER"],
        "maximum_notional": 100_000,
        "maximum_loss": 1_000,
        "maximum_slippage_bps": 20,
        "permitted_order_types": ["LIMIT"],
        "maximum_child_orders": 2,
        "maximum_reentries": 0,
        "maximum_state_flips": 0,
        "effective_at": (now - timedelta(minutes=1)).isoformat(),
        "expires_at": (now + timedelta(minutes=1)).isoformat(),
        "state": "ARMED",
        "eligible": True,
        "target_remaining_quantity": 10,
    }
    mandate_repository.upsert(record)
    observation_service.record(
        "quote",
        "QQQ",
        {
            "observed_at": now.isoformat(),
            "bid": 100,
            "ask": 100.1,
            "last": 100.05,
        },
    )
    observation_service.record(
        "gex",
        "QQQ",
        {
            "observed_at": now.isoformat(),
            "net_gex": 1,
            "gex_coefficient": 1,
        },
    )
    scheduler = Scheduler(
        mandate_repository, observation_service, decision_repository, intent_repository
    )

    decision = scheduler.run_once("m1", now)

    assert decision is not None and decision["action"] == "ENTER"
    assert len(decision_repository.list_for_mandate("m1")) == 1
    assert len(intent_repository.list_for_mandate("m1")) == 1


def test_scheduler_blocks_intent_when_position_breaches_compiled_risk() -> None:
    now = datetime.now(UTC)
    database = Database()
    mandate_repository = MandateRepository(database)
    decision_repository = DecisionRepository(database)
    intent_repository = IntentRepository(database)
    observation_service = ObservationService(ObservationRepository(database))
    mandate_repository.upsert(
        {
            "mandate_id": "m1",
            "strategy_id": "s1",
            "strategy_version": 1,
            "sleeve_element_id": "e1",
            "instrument": "QQQ",
            "asset_class": "ETF",
            "direction": "LONG",
            "allowed_actions": ["ENTER"],
            "maximum_notional": 1_000,
            "maximum_loss": 100,
            "maximum_slippage_bps": 20,
            "permitted_order_types": ["LIMIT"],
            "maximum_child_orders": 1,
            "maximum_reentries": 0,
            "maximum_state_flips": 0,
            "effective_at": (now - timedelta(minutes=1)).isoformat(),
            "expires_at": (now + timedelta(minutes=1)).isoformat(),
            "state": "ARMED",
            "eligible": True,
            "target_remaining_quantity": 10,
        }
    )
    observation_service.record(
        "quote", "QQQ", {"observed_at": now.isoformat(), "bid": 100, "ask": 100.1, "last": 100.05}
    )
    observation_service.record(
        "gex", "QQQ", {"observed_at": now.isoformat(), "net_gex": 1, "gex_coefficient": 1}
    )
    observation_service.record(
        "position",
        "QQQ",
        {
            "observed_at": now.isoformat(),
            "quantity": 10,
            "average_price": 100,
            "realized_pnl": -101,
        },
    )
    scheduler = Scheduler(
        mandate_repository, observation_service, decision_repository, intent_repository
    )

    decision = scheduler.run_once("m1", now)

    assert decision is not None and decision["action"] == "WAIT"
    assert decision["reason_codes"][0] == "RISK_GATE_FAILED"
    assert intent_repository.list_for_mandate("m1") == []
