"""Audit-friendly types for dynamic trading judgments.

This package deliberately distinguishes strategy evidence from non-negotiable
execution constraints.  It never submits orders.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
import json
from typing import Any
from uuid import uuid4


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class EvidenceState(str, Enum):
    KNOWN = "KNOWN"
    MISSING = "MISSING"
    STALE = "STALE"
    ESTIMATED = "ESTIMATED"
    CONFLICTING = "CONFLICTING"
    UNAVAILABLE = "UNAVAILABLE"


class ProbabilityKind(str, Enum):
    EMPIRICAL = "EMPIRICAL"
    MODEL_ESTIMATE = "MODEL_ESTIMATE"
    SUBJECTIVE = "SUBJECTIVE"
    UNAVAILABLE = "UNAVAILABLE"


class Action(str, Enum):
    ENTER = "ENTER"
    SCALE_IN = "SCALE_IN"
    REDUCE = "REDUCE"
    EXIT = "EXIT"
    WAIT = "WAIT"


class ReviewAction(str, Enum):
    APPROVE = "APPROVE"
    RESIZE = "RESIZE"
    HOLD = "HOLD"
    REJECT = "REJECT"
    REQUEST_EVIDENCE = "REQUEST_EVIDENCE"


@dataclass(frozen=True)
class Observation:
    name: str
    value: Any
    state: EvidenceState
    source: str
    event_time: datetime | None
    available_at: datetime | None
    effect: str
    missing_fields: tuple[str, ...] = ()
    source_url: str | None = None
    label: str = "OBSERVATION"

    def is_available_at(self, cutoff: datetime) -> bool:
        return self.available_at is not None and self.available_at <= cutoff


@dataclass(frozen=True)
class ProbabilityEstimate:
    event: str
    horizon: str
    kind: ProbabilityKind
    probability: float | None
    method: str
    sample_size: int | None = None
    cohort: str | None = None
    coverage: str | None = None
    interval: tuple[float, float] | None = None
    assumptions: str = ""
    calibration: str | None = None
    expected_payoff: float | None = None
    downside: float | None = None
    transaction_cost_assumption: str | None = None
    limitations: str = ""


@dataclass(frozen=True)
class InformationRequest:
    request_id: str
    instrument: str
    horizon: str
    question: str
    cutoff: datetime
    expected_effect: str
    deadline: datetime
    source_requirements: str


@dataclass(frozen=True)
class AgentResult:
    agent: str
    response: str | None
    observations: tuple[Observation, ...] = ()
    error: str | None = None
    timed_out: bool = False


@dataclass(frozen=True)
class ExecutionConstraints:
    authorized: bool
    permitted_instruments: tuple[str, ...]
    permitted_actions: tuple[Action, ...]
    available_cash: float
    current_position: float
    max_position: float
    indicative_price: float | None
    pricing_source: str | None

    def assess(self, instrument: str, action: Action, quantity: float) -> tuple[bool, tuple[str, ...]]:
        issues: list[str] = []
        if not self.authorized:
            issues.append("Account is not authorized for execution.")
        if instrument not in self.permitted_instruments:
            issues.append("Instrument is not permitted.")
        if action not in self.permitted_actions:
            issues.append("Action is not permitted.")
        if quantity < 0:
            issues.append("Quantity cannot be negative.")
        if action in (Action.ENTER, Action.SCALE_IN):
            if self.indicative_price is None:
                issues.append("No truthful executable price is available.")
            elif quantity * self.indicative_price > self.available_cash:
                issues.append("Proposed purchase exceeds available cash.")
            if self.current_position + quantity > self.max_position:
                issues.append("Proposed position exceeds position limit.")
        if action in (Action.REDUCE, Action.EXIT) and quantity > self.current_position:
            issues.append("Proposed closing quantity exceeds current position.")
        return not issues, tuple(issues)


@dataclass(frozen=True)
class DatasetSnapshot:
    cutoff: datetime
    observations: tuple[Observation, ...]
    snapshot_id: str = ""

    @classmethod
    def at_cutoff(cls, cutoff: datetime, observations: list[Observation]) -> "DatasetSnapshot":
        eligible = tuple(item for item in observations if item.is_available_at(cutoff))
        payload = json.dumps(
            [asdict(item) for item in eligible], default=str, sort_keys=True, separators=(",", ":")
        )
        return cls(cutoff=cutoff, observations=eligible, snapshot_id=sha256(payload.encode()).hexdigest()[:16])


@dataclass(frozen=True)
class RecommendationRevision:
    action: Action
    quantity: float
    snapshot_id: str
    reason: str
    timestamp: datetime


@dataclass(frozen=True)
class DecisionRecord:
    decision_id: str
    instrument: str
    timestamp: datetime
    horizon: str
    action: Action
    quantity: float
    rationale: str
    supporting_factors: tuple[str, ...]
    opposing_factors: tuple[str, ...]
    missing_data_implications: tuple[str, ...]
    probabilities: tuple[ProbabilityEstimate, ...]
    information_requests: tuple[InformationRequest, ...]
    agent_results: tuple[AgentResult, ...]
    alternatives: tuple[str, ...]
    change_conditions: tuple[str, ...]
    execution_feasible: bool
    execution_issues: tuple[str, ...]
    snapshot: DatasetSnapshot
    model_version: str
    prompt_version: str
    strategy_version: str
    dataset_version: str
    initial_recommendation: RecommendationRevision | None = None
    revisions: tuple[RecommendationRevision, ...] = ()
    parent_decision_id: str | None = None
    changed_by_evidence: tuple[str, ...] = ()
    expires_at: datetime | None = None

    @classmethod
    def new(cls, **values: Any) -> "DecisionRecord":
        return cls(decision_id=str(uuid4()), **values)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReviewSubmission:
    decision_id: str
    snapshot_id: str
    action: ReviewAction
    reviewer: str
    timestamp: datetime
    quantity: float | None = None
    note: str = ""