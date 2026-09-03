from __future__ import annotations

import uuid
from dataclasses import asdict
from datetime import datetime, timedelta

from algo_tf.audit.hashing import digest_payload
from algo_tf.domain.algorithm_decision import AlgorithmDecision
from algo_tf.domain.enums import Action
from algo_tf.domain.execution_mandate import ExecutionMandate
from algo_tf.domain.market_observation import MarketObservation
from algo_tf.policies.adaptive_limit_v1 import derive_limit_price
from algo_tf.policies.mandate_gate import mandate_valid
from algo_tf.policies.sizing_policy import calculate_child_quantity


class DecisionEngine:
    policy_name = "ADAPTIVE_LIMIT_V1"
    policy_version = "1.0.0"

    def decide(
        self,
        mandate: ExecutionMandate,
        obs: MarketObservation,
        now: datetime,
    ) -> AlgorithmDecision:
        gate_results = {
            "mandate_valid": mandate_valid(mandate, now),
            "strategy_eligible": obs.strategy_eligible,
            "within_entry_window": mandate.effective_at <= now < mandate.expires_at,
            "market_open": obs.market_open,
            "quote_fresh": obs.quote_fresh,
            "market_structure_fresh": obs.market_structure_age_seconds <= 300,
            "gex_fresh_or_policy_allows_missing": obs.gex_fresh,
            "spread_within_limit": obs.spread_bps <= mandate.maximum_slippage_bps,
            "confirmation_pass": obs.confirmation_pass,
            "risk_budget_available": obs.risk_budget_available,
            "target_remaining": obs.target_remaining_quantity > 0,
            "execution_engine_available": obs.execution_engine_available,
            "kill_switch_clear": obs.kill_switch_clear,
        }
        hard_gates_pass = all(gate_results.values())

        input_hash = digest_payload(
            {
                "mandate": asdict(mandate),
                "observation": asdict(obs),
                "now": now.isoformat(),
                "policy_version": self.policy_version,
            }
        )

        if not hard_gates_pass:
            return AlgorithmDecision(
                decision_id=str(uuid.uuid4()),
                mandate_id=mandate.mandate_id,
                strategy_id=mandate.strategy_id,
                strategy_version=mandate.strategy_version,
                action=Action.WAIT,
                requested_quantity=0,
                limit_price=None,
                gate_results=gate_results,
                reason_codes=("HARD_GATE_FAILED",),
                policy_name=self.policy_name,
                policy_version=self.policy_version,
                created_at=now,
                expires_at=now + timedelta(seconds=30),
                observation_digest=digest_payload(asdict(obs)),
                deterministic_input_hash=input_hash,
            )

        qty = calculate_child_quantity(
            remaining_target_quantity=obs.target_remaining_quantity,
            mandate_remaining_quantity=obs.target_remaining_quantity,
            risk_limited_quantity=obs.target_remaining_quantity,
            liquidity_limited_quantity=max(
                1,
                int(obs.liquidity_score * obs.target_remaining_quantity),
            ),
            delta_limited_quantity=obs.target_remaining_quantity,
            signal_coefficient=obs.signal_coefficient,
            gex_coefficient=obs.gex_coefficient,
            spread_coefficient=obs.spread_coefficient,
            participation_coefficient=obs.participation_coefficient,
            time_coefficient=obs.time_coefficient,
        )
        reasons: tuple[str, ...]
        if qty <= 0:
            action = Action.WAIT
            limit_price = None
            reasons = ("SIZE_ZERO",)
        else:
            allowed_entry_actions = {Action.ENTER, Action.SCALE_IN} & set(mandate.allowed_actions)
            if not allowed_entry_actions:
                return AlgorithmDecision(
                    decision_id=str(uuid.uuid4()),
                    mandate_id=mandate.mandate_id,
                    strategy_id=mandate.strategy_id,
                    strategy_version=mandate.strategy_version,
                    action=Action.WAIT,
                    requested_quantity=0,
                    limit_price=None,
                    gate_results={**gate_results, "action_allowed": False},
                    reason_codes=("ACTION_NOT_PERMITTED",),
                    policy_name=self.policy_name,
                    policy_version=self.policy_version,
                    created_at=now,
                    expires_at=now + timedelta(seconds=30),
                    observation_digest=digest_payload(asdict(obs)),
                    deterministic_input_hash=input_hash,
                )
            action = Action.ENTER if Action.ENTER in allowed_entry_actions else Action.SCALE_IN
            limit_price = derive_limit_price(
                bid=obs.bid,
                ask=obs.ask,
                side=mandate.direction.value,
                max_slippage_bps=mandate.maximum_slippage_bps,
            )
            reasons = ("ALL_GATES_PASS", "ADAPTIVE_LIMIT_V1")

        return AlgorithmDecision(
            decision_id=str(uuid.uuid4()),
            mandate_id=mandate.mandate_id,
            strategy_id=mandate.strategy_id,
            strategy_version=mandate.strategy_version,
            action=action,
            requested_quantity=qty,
            limit_price=limit_price,
            gate_results=gate_results,
            reason_codes=reasons,
            policy_name=self.policy_name,
            policy_version=self.policy_version,
            created_at=now,
            expires_at=now + timedelta(seconds=30),
            observation_digest=digest_payload(asdict(obs)),
            deterministic_input_hash=input_hash,
        )
