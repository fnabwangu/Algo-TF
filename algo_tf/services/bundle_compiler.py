from __future__ import annotations

from datetime import timedelta

from algo_tf.audit.hashing import digest_payload
from algo_tf.contracts.inbound.algorithm_design_bundle import AlgorithmDesignBundle
from algo_tf.domain.enums import Mode


class BundleCompiler:
    _mode_rank = {
        Mode.REPLAY: 0,
        Mode.PAPER: 1,
        Mode.SHADOW: 2,
        Mode.LIMITED_LIVE: 3,
        Mode.LIVE: 4,
    }

    def compile(self, bundle: AlgorithmDesignBundle, server_mode: Mode) -> dict[str, object]:
        computed_mode = self._effective_mode(bundle)
        if bundle.effective_mode != computed_mode.value:
            raise ValueError("effective_mode does not match testing evidence")
        if self._mode_rank[computed_mode] > self._mode_rank[server_mode]:
            raise ValueError("proposal mode exceeds the configured server mode")
        instrument = bundle.strategy_specification.instrument
        return {
            "mandate_id": bundle.bundle_id,
            "strategy_id": bundle.bundle_id,
            "strategy_version": 4,
            "sleeve_element_id": bundle.bundle_id,
            "instrument": instrument.symbol.upper(),
            "asset_class": instrument.asset_class,
            "direction": instrument.direction,
            "maximum_notional": bundle.risk_mandate.max_notional,
            "maximum_loss": bundle.risk_mandate.max_dollar_risk,
            "maximum_slippage_bps": bundle.execution_mandate.order.max_slippage_bps,
            "allowed_actions": ["ENTER"],
            "maximum_child_orders": bundle.execution_mandate.order.tranches,
            "maximum_reentries": 0,
            "maximum_state_flips": 0,
            "permitted_order_types": [bundle.execution_mandate.order.type],
            "state": "PENDING_APPROVAL",
            "eligible": False,
            "effective_at": bundle.created_at.isoformat(),
            "expires_at": (bundle.created_at + timedelta(days=1)).isoformat(),
            "approved_at": None,
            "approved_by": None,
            "effective_mode": computed_mode.value,
            "source_bundle": bundle.model_dump(mode="json", by_alias=True),
            "source_bundle_digest": digest_payload(bundle.model_dump(mode="json", by_alias=True)),
        }

    @staticmethod
    def _effective_mode(bundle: AlgorithmDesignBundle) -> Mode:
        evidence = bundle.testing
        if all(
            (
                evidence.backtest,
                evidence.out_of_sample,
                evidence.costs,
                evidence.sensitivity,
                evidence.scenarios,
                evidence.paper,
                evidence.shadow,
            )
        ):
            return Mode.LIMITED_LIVE
        if all((evidence.backtest, evidence.out_of_sample, evidence.costs, evidence.paper)):
            return Mode.SHADOW
        if all((evidence.backtest, evidence.costs)):
            return Mode.PAPER
        return Mode.REPLAY