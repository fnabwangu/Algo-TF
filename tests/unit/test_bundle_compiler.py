from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from algo_tf.contracts.inbound.algorithm_design_bundle import AlgorithmDesignBundle
from algo_tf.domain.enums import Mode
from algo_tf.services.bundle_compiler import BundleCompiler


def bundle_payload() -> dict[str, object]:
    return {
        "schema": "algo-tf.algorithm-design-bundle.v4",
        "bundle_id": "builder-proposal-1",
        "created_at": datetime.now(UTC).isoformat(),
        "status": "PROPOSAL_READY",
        "effective_mode": "REPLAY",
        "strategy_specification": {
            "instrument": {
                "symbol": "qqq",
                "asset_class": "ETF",
                "direction": "LONG",
                "session": "REGULAR",
            }
        },
        "risk_mandate": {
            "max_dollar_risk": 1_000,
            "max_notional": 30_000,
            "calculate_quantity": True,
        },
        "execution_mandate": {
            "order": {
                "type": "LIMIT",
                "tranches": 1,
                "max_replaces": 0,
                "max_spread_bps": 20,
                "max_slippage_bps": 25,
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


def test_compiler_creates_pending_approval_runtime_mandate() -> None:
    payload = bundle_payload()
    payload["strategy_specification"] = {
        **payload["strategy_specification"],
        "hypothesis": {"statement": "A documented, testable hypothesis."},
    }
    payload["risk_mandate"] = {**payload["risk_mandate"], "stop": {"no_widening": True}}
    payload["execution_mandate"] = {
        **payload["execution_mandate"],
        "monitoring": {"quotes_seconds": 5},
    }
    bundle = AlgorithmDesignBundle.model_validate(payload)

    compiled = BundleCompiler().compile(bundle, Mode.REPLAY)

    assert compiled["state"] == "PENDING_APPROVAL"
    assert compiled["instrument"] == "QQQ"
    assert compiled["maximum_loss"] == 1_000
    assert compiled["source_bundle_digest"]
    assert compiled["source_bundle"]["strategy_specification"]["hypothesis"] == {
        "statement": "A documented, testable hypothesis."
    }


def test_compiler_rejects_unsupported_or_unearned_authority() -> None:
    unsupported = bundle_payload()
    unsupported["execution_mandate"] = {
        **unsupported["execution_mandate"],
        "order": {**unsupported["execution_mandate"]["order"], "tranches": 2},
    }
    with pytest.raises(ValidationError):
        AlgorithmDesignBundle.model_validate(unsupported)

    inconsistent_mode = bundle_payload()
    inconsistent_mode["effective_mode"] = "PAPER"
    with pytest.raises(ValueError, match="effective_mode"):
        BundleCompiler().compile(
            AlgorithmDesignBundle.model_validate(inconsistent_mode), Mode.PAPER
        )
