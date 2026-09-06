"""Dynamic decision orchestration with advisory research and hard execution limits."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, wait
from dataclasses import dataclass
from datetime import datetime, timedelta
from math import sqrt
from typing import Protocol

from .domain import (
    Action, AgentResult, ConfidenceScore, DatasetSnapshot, DecisionBranch, DecisionRecord, EvidenceState,
    ExecutionConstraints, InformationRequest, Observation, ProbabilityEstimate,
    ProbabilityKind, ProbabilisticConsensus, JudgmentSignal, RecommendationRevision,
)


class ReadOnlyProvider(Protocol):
    name: str

    def observe(self, instrument: str, cutoff: datetime) -> list[Observation]: ...


class Adviser(Protocol):
    name: str

    def answer(self, request: InformationRequest) -> AgentResult: ...


@dataclass(frozen=True)
class HistoricalOutcome:
    observed_at: datetime
    resolved_at: datetime
    positive_after_costs: bool
    return_after_costs: float


def empirical_probability(
    event: str, horizon: str, cutoff: datetime, outcomes: list[HistoricalOutcome]
) -> ProbabilityEstimate:
    """Compute a Wilson interval using only outcomes resolved by the cutoff."""
    cohort = [outcome for outcome in outcomes if outcome.observed_at <= cutoff and outcome.resolved_at <= cutoff]
    sample_size = len(cohort)
    if not sample_size:
        return ProbabilityEstimate(event, horizon, ProbabilityKind.UNAVAILABLE, None,
                                   "No resolved historical cohort available at decision cutoff.",
                                   limitations="A probability cannot be defended without resolved in-cutoff outcomes.")
    successes = sum(outcome.positive_after_costs for outcome in cohort)
    probability = successes / sample_size
    z = 1.96
    denominator = 1 + z * z / sample_size
    center = (probability + z * z / (2 * sample_size)) / denominator
    margin = z * sqrt(probability * (1 - probability) / sample_size + z * z / (4 * sample_size * sample_size)) / denominator
    returns = [outcome.return_after_costs for outcome in cohort]
    return ProbabilityEstimate(
        event=event, horizon=horizon, kind=ProbabilityKind.EMPIRICAL, probability=probability,
        method="Historical frequency with 95% Wilson binomial interval.", sample_size=sample_size,
        cohort="Resolved observations with observation and resolution timestamps no later than cutoff.",
        coverage=f"{sample_size}/{len(outcomes)} supplied outcomes eligible at cutoff.",
        interval=(max(0.0, center - margin), min(1.0, center + margin)),
        assumptions="Historical cases are sufficiently comparable and outcomes are independently sampled.",
        calibration="Not computed by this fixture; evaluate on a separate out-of-sample cohort.",
        expected_payoff=sum(returns) / sample_size,
        downside=min(returns), transaction_cost_assumption="Returns are supplied after costs.",
        limitations="Small or nonstationary cohorts widen practical uncertainty.",
    )


HIGH_CONVICTION_THRESHOLD = 0.75
LOW_CONVICTION_THRESHOLD = 0.40


def evaluate_probabilistic_consensus(signals: tuple[JudgmentSignal, ...]) -> float:
    """Return the weighted conviction score for independently supplied judgments."""
    total_weight = sum(signal.weight for signal in signals)
    if total_weight == 0:
        return 0.5
    return sum(signal.confidence.value * signal.weight for signal in signals) / total_weight


def human_in_the_loop_escalation(summary: str) -> str:
    """Create the auditable manual tie-breaking request; this system never executes orders."""
    return f"Manual tie-break required: {summary}"


@dataclass(frozen=True)
class JudgmentEvaluation:
    consensus: ProbabilisticConsensus
    support: tuple[str, ...]
    oppose: tuple[str, ...]
    missing: tuple[str, ...]


class EvidenceWeightedJudge:
    """A transparent fallback for when a configured LLM judgment adapter is unavailable.

    Deployments can replace this object with an LLM adapter implementing ``decide``;
    this fallback is intentionally labelled subjective rather than misrepresenting it
    as a calibrated model.
    """

    model_version = "evidence-weighted-fallback/1"
    prompt_version = "dynamic-judgment/1"

    def request_information(self, instrument: str, horizon: str, snapshot: DatasetSnapshot,
                            now: datetime, deadline: datetime) -> list[InformationRequest]:
        requests = []
        for observation in snapshot.observations:
            if observation.state in (EvidenceState.MISSING, EvidenceState.STALE, EvidenceState.UNAVAILABLE):
                requests.append(InformationRequest(
                    request_id=f"{instrument}-{observation.name}-{len(requests)}", instrument=instrument,
                    horizon=horizon, question=f"Provide {observation.name} or explain why it is unavailable.",
                    cutoff=snapshot.cutoff,
                    expected_effect=f"May change uncertainty or position size; does not require a WAIT decision.",
                    deadline=deadline, source_requirements="Read-only source with event and availability timestamps.",
                ))
        return requests[:3]

    def decide(self, instrument: str, horizon: str, snapshot: DatasetSnapshot,
               probability: ProbabilityEstimate) -> JudgmentEvaluation:
        support: list[str] = []
        oppose: list[str] = []
        missing: list[str] = []
        signals: list[JudgmentSignal] = []
        for observation in snapshot.observations:
            value = observation.value
            if observation.state in (EvidenceState.MISSING, EvidenceState.STALE, EvidenceState.UNAVAILABLE):
                missing.append(f"{observation.name}: {observation.state.value}; {observation.effect}")
                signals.append(JudgmentSignal(observation.name, ConfidenceScore(
                    0.5, f"{observation.state.value} evidence is neutral and requires uncertainty-aware sizing."
                )))
                continue
            if observation.state == EvidenceState.CONFLICTING:
                oppose.append(f"{observation.name} is conflicting: {observation.effect}")
                signals.append(JudgmentSignal(observation.name, ConfidenceScore(
                    0.25, f"Conflicting evidence reduces confidence: {observation.effect}"
                )))
            elif value is True or (isinstance(value, (int, float)) and value > 0):
                support.append(f"{observation.name}: {observation.effect}")
                signals.append(JudgmentSignal(observation.name, ConfidenceScore(
                    0.9, f"Favorable evidence: {observation.effect}"
                )))
            elif value is False or (isinstance(value, (int, float)) and value < 0):
                oppose.append(f"{observation.name}: {observation.effect}")
                signals.append(JudgmentSignal(observation.name, ConfidenceScore(
                    0.1, f"Unfavorable evidence: {observation.effect}"
                )))
        if probability.kind == ProbabilityKind.EMPIRICAL and probability.probability is not None:
            (support if probability.probability >= 0.5 else oppose).append(
                f"Empirical probability is {probability.probability:.1%} for {probability.event}."
            )
            signals.append(JudgmentSignal("empirical_outcomes", ConfidenceScore(
                probability.probability, f"Empirical probability for {probability.event}."
            ), weight=1.5))
        else:
            signals.append(JudgmentSignal("empirical_outcomes", ConfidenceScore(
                0.5, "No empirical probability is available at the decision cutoff."
            ), weight=1.5))
        conviction = evaluate_probabilistic_consensus(tuple(signals))
        if conviction > HIGH_CONVICTION_THRESHOLD:
            branch = DecisionBranch.AUTO_EXECUTE
            escalation = None
        elif conviction < LOW_CONVICTION_THRESHOLD:
            branch = DecisionBranch.REJECT
            escalation = None
        else:
            branch = DecisionBranch.ESCALATE
            escalation = human_in_the_loop_escalation(
                f"conviction {conviction:.1%} is between the {LOW_CONVICTION_THRESHOLD:.0%} and "
                f"{HIGH_CONVICTION_THRESHOLD:.0%} routing thresholds."
            )
        return JudgmentEvaluation(
            ProbabilisticConsensus(tuple(signals), conviction, branch, escalation),
            tuple(support), tuple(oppose), tuple(missing),
        )


class DecisionEngine:
    def __init__(self, providers: list[ReadOnlyProvider], advisers: list[Adviser], judge: EvidenceWeightedJudge | None = None,
                 max_workers: int = 3) -> None:
        self.providers = providers
        self.advisers = advisers
        self.judge = judge or EvidenceWeightedJudge()
        self.max_workers = max_workers

    def _consult(self, requests: list[InformationRequest], timeout_seconds: float) -> tuple[AgentResult, ...]:
        # One bounded pass: advisers receive no engine reference and cannot recurse.
        if not requests or not self.advisers:
            return ()
        jobs = [(adviser, request) for request in requests for adviser in self.advisers]
        results: list[AgentResult] = []
        pool = ThreadPoolExecutor(max_workers=min(self.max_workers, len(jobs)))
        try:
            future_map = {pool.submit(adviser.answer, request): adviser.name for adviser, request in jobs}
            done, pending = wait(future_map, timeout=timeout_seconds)
            for future in done:
                name = future_map[future]
                try:
                    results.append(future.result())
                except Exception as error:  # A failed adviser must not discard other research.
                    results.append(AgentResult(agent=name, response=None, error=str(error)))
            for future in pending:
                future.cancel()
                results.append(AgentResult(agent=future_map[future], response=None, timed_out=True,
                                           error="Consultation deadline expired."))
        finally:
            # Running provider code cannot be forcibly killed, but it must not hold
            # the decision cycle open once its bounded research budget is exhausted.
            pool.shutdown(wait=False, cancel_futures=True)
        return tuple(results)

    def decide(self, instrument: str, horizon: str, cutoff: datetime, constraints: ExecutionConstraints,
               outcomes: list[HistoricalOutcome], research_budget_seconds: float = 1.0) -> DecisionRecord:
        observations = [item for provider in self.providers for item in provider.observe(instrument, cutoff)]
        snapshot = DatasetSnapshot.at_cutoff(cutoff, observations)
        initial_snapshot = snapshot
        probability = empirical_probability(f"positive {horizon} return after costs", horizon, cutoff, outcomes)
        initial_evaluation = self.judge.decide(instrument, horizon, snapshot, probability)
        initial_action, initial_quantity = self._route(initial_evaluation.consensus, constraints)
        research_deadline = datetime.now(cutoff.tzinfo) + timedelta(seconds=research_budget_seconds)
        requests = self.judge.request_information(instrument, horizon, snapshot, cutoff, research_deadline)
        agent_results = self._consult(requests, research_budget_seconds)
        additional = [item for result in agent_results for item in result.observations]
        snapshot = DatasetSnapshot.at_cutoff(cutoff, list(snapshot.observations) + additional)
        evaluation = self.judge.decide(instrument, horizon, snapshot, probability)
        action, quantity = self._route(evaluation.consensus, constraints)
        support, oppose, missing = evaluation.support, evaluation.oppose, evaluation.missing
        feasible, issues = constraints.assess(instrument, action, quantity)
        initial = RecommendationRevision(initial_action, initial_quantity, initial_snapshot.snapshot_id,
                                        "Initial judgment before adviser consultation.", cutoff)
        revisions = ()
        if (action, quantity) != (initial_action, initial_quantity):
            revisions = (RecommendationRevision(action, quantity, snapshot.snapshot_id,
                         "Consulted evidence changed the recommendation or size.", datetime.now(cutoff.tzinfo)),)
        return DecisionRecord.new(
            instrument=instrument, timestamp=cutoff, horizon=horizon, action=action, quantity=quantity,
            rationale=f"Probabilistic judgment routed to {evaluation.consensus.branch.value}; "
                      "research gaps reduce certainty or size rather than acting as gates.",
            supporting_factors=support, opposing_factors=oppose, missing_data_implications=missing,
            probabilities=(probability,), information_requests=tuple(requests), agent_results=agent_results,
            alternatives=("WAIT: rejected when available evidence supports limited risk.", "ENTER: rejected when evidence balance is non-positive."),
            change_conditions=("A current GEX reading could alter uncertainty and size.", "Execution remains subject to authorization, limits, and live pricing."),
            execution_feasible=feasible, execution_issues=issues, snapshot=snapshot,
            model_version=self.judge.model_version, prompt_version=self.judge.prompt_version,
            strategy_version="dynamic-evidence/1", dataset_version="snapshot/1",
            initial_recommendation=initial, revisions=revisions,
            changed_by_evidence=tuple(observation.name for observation in additional),
            expires_at=cutoff + timedelta(minutes=15),
            probabilistic_consensus=evaluation.consensus,
        )

    @staticmethod
    def _route(consensus: ProbabilisticConsensus, constraints: ExecutionConstraints) -> tuple[Action, float]:
        if consensus.branch != DecisionBranch.AUTO_EXECUTE:
            return Action.WAIT, 0.0
        cash_limited = constraints.available_cash / constraints.indicative_price if constraints.indicative_price else 0.0
        max_allocation = max(0.0, min(constraints.max_position - constraints.current_position, cash_limited))
        return Action.ENTER, max_allocation * consensus.final_conviction_score