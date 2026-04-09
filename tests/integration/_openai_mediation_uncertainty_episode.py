"""Build the live OpenAI-host uncertainty baseline episodes for mediation evidence."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from cortex.core.commitments import CommitmentStatus
from cortex.core.dispatch import DispatchLane
from cortex.core.environment import CommitmentEnvironmentHandle, EXECUTION_TRACE
from cortex.core.errors import ContradictionRecord, DegradationRecord
from cortex.drivers.openai_host_commitment import evaluate_openai_host_commitment
from experimental.sre.allocation import AllocationScore, AllocationScorecard
from experimental.sre.brake import BrakeState, evaluate_brake_state
from experimental.sre.families import SoftControlFamily
from experimental.sre.policy import neutral_dominance_decision
from experimental.sre.uncertainty import UncertaintyEstimate
from tests.integration._reference_lane import (
    host_surface_degradation_pair,
    provenance_manifest_for,
)


EXPECTED_OPENAI_UNCERTAINTY_STEP_SEQUENCE = ("guard", "retry", "resolve")
DEFAULT_OPENAI_UNCERTAINTY_PAIR_KEY = "001"
OPENAI_UNCERTAINTY_PAIR_KEYS = ("001", "002", "003")
OPENAI_UNCERTAINTY_LEVEL = 0.62


@dataclass(frozen=True, slots=True)
class OpenAIUncertaintyPairSpec:
    pair_key: str
    pair_id: str
    baseline_run_id: str
    mediated_run_id: str
    session_id: str
    commitment_id: str
    provenance_artifact_id: str
    contradiction_source_tag: str
    contradiction_summary: str
    degradation_reason_code: str
    uncertainty_spike_tag: str
    guard_check_score: float
    guard_branch_score: float
    retry_check_score: float
    retry_branch_score: float
    resolve_check_score: float
    resolve_branch_score: float

    @property
    def baseline_packet_path(self) -> str:
        return (
            "docs/lab/mediation_evidence/openai/"
            f"scenario_uncertainty_openai_01__baseline_non_mediated__run_{self.pair_key}.md"
        )

    @property
    def mediated_packet_path(self) -> str:
        return (
            "docs/lab/mediation_evidence/openai/"
            f"scenario_uncertainty_openai_01__experimental_mediated__run_{self.pair_key}.md"
        )

    @property
    def baseline_step_prefix(self) -> str:
        if self.pair_key == DEFAULT_OPENAI_UNCERTAINTY_PAIR_KEY:
            return "openai-uncertainty-step"
        return f"openai-uncertainty-{self.pair_key}-step"

    @property
    def mediated_step_prefix(self) -> str:
        if self.pair_key == DEFAULT_OPENAI_UNCERTAINTY_PAIR_KEY:
            return "openai-uncertainty-mediated-step"
        return f"openai-uncertainty-mediated-{self.pair_key}-step"


OPENAI_UNCERTAINTY_PAIR_SPECS: Mapping[str, OpenAIUncertaintyPairSpec] = {
    "001": OpenAIUncertaintyPairSpec(
        pair_key="001",
        pair_id="pair_openai_uncertainty_001",
        baseline_run_id="openai_uncertainty_baseline_run_001",
        mediated_run_id="openai_uncertainty_mediated_run_001",
        session_id="openai-uncertainty-session-1",
        commitment_id="openai-uncertainty-commit-1",
        provenance_artifact_id="openai-artifact-uncertainty-1",
        contradiction_source_tag="openai-trace-check",
        contradiction_summary="OpenAI approval evidence remains incomplete",
        degradation_reason_code="openai-evidence-partial",
        uncertainty_spike_tag="openai-trace-gap-ambiguity",
        guard_check_score=1.22,
        guard_branch_score=0.92,
        retry_check_score=1.18,
        retry_branch_score=0.90,
        resolve_check_score=1.10,
        resolve_branch_score=0.88,
    ),
    "002": OpenAIUncertaintyPairSpec(
        pair_key="002",
        pair_id="pair_openai_uncertainty_002",
        baseline_run_id="openai_uncertainty_baseline_run_002",
        mediated_run_id="openai_uncertainty_mediated_run_002",
        session_id="openai-uncertainty-session-2",
        commitment_id="openai-uncertainty-commit-2",
        provenance_artifact_id="openai-artifact-uncertainty-2",
        contradiction_source_tag="openai-receipt-check",
        contradiction_summary="OpenAI provenance receipt remains incomplete",
        degradation_reason_code="openai-receipt-partial",
        uncertainty_spike_tag="openai-receipt-lag-ambiguity",
        guard_check_score=1.24,
        guard_branch_score=0.91,
        retry_check_score=1.19,
        retry_branch_score=0.89,
        resolve_check_score=1.11,
        resolve_branch_score=0.87,
    ),
    "003": OpenAIUncertaintyPairSpec(
        pair_key="003",
        pair_id="pair_openai_uncertainty_003",
        baseline_run_id="openai_uncertainty_baseline_run_003",
        mediated_run_id="openai_uncertainty_mediated_run_003",
        session_id="openai-uncertainty-session-3",
        commitment_id="openai-uncertainty-commit-3",
        provenance_artifact_id="openai-artifact-uncertainty-3",
        contradiction_source_tag="openai-artifact-check",
        contradiction_summary="OpenAI artifact chain remains unconfirmed",
        degradation_reason_code="openai-artifact-chain-partial",
        uncertainty_spike_tag="openai-artifact-chain-ambiguity",
        guard_check_score=1.21,
        guard_branch_score=0.93,
        retry_check_score=1.17,
        retry_branch_score=0.91,
        resolve_check_score=1.11,
        resolve_branch_score=0.86,
    ),
}


@dataclass(frozen=True, slots=True)
class _EpisodeStep:
    step_id: str
    selected_family: SoftControlFamily
    brake_state: BrakeState
    outcome_class: str
    contradiction_ref: str
    degradation_ref: str


def build_openai_uncertainty_episode_snapshot(
    pair_key: str = DEFAULT_OPENAI_UNCERTAINTY_PAIR_KEY,
) -> dict[str, object]:
    spec = OPENAI_UNCERTAINTY_PAIR_SPECS[pair_key]
    contradiction, degradation = openai_uncertainty_pair_evidence(spec)
    steps = (
        _build_guard_step(spec, contradiction, degradation),
        _build_retry_step(spec, contradiction, degradation),
        _build_resolve_step(spec, contradiction, degradation),
    )

    return {
        "scenario_id": "scenario_uncertainty_openai_01",
        "run_id": spec.baseline_run_id,
        "paired_episode_set_id": spec.pair_id,
        "session_id": spec.session_id,
        "commitment_id": spec.commitment_id,
        "provenance_artifact_id": spec.provenance_artifact_id,
        "contradiction_ref": _contradiction_ref(contradiction),
        "degradation_ref": degradation.reason_code,
        "uncertainty_spike_tag": spec.uncertainty_spike_tag,
        "step_sequence": list(EXPECTED_OPENAI_UNCERTAINTY_STEP_SEQUENCE),
        "uncertified_loop_count": 2,
        "event_trace_refs": ", ".join(
            (
                f"{spec.baseline_step_prefix}-1:response.completed/guard",
                f"{spec.baseline_step_prefix}-2:response.completed/retry",
                f"{spec.baseline_step_prefix}-3:response.completed/resolve",
            )
        ),
        "steps": [
            {
                "step_id": step.step_id,
                "host_event_name": "response.completed",
                "payload_identity": (
                    f"commitment_id={spec.commitment_id}, externally_consequential=True, "
                    f"session_id={spec.session_id}"
                ),
                "dispatch_lane": DispatchLane.FULL_COMMITMENT.value,
                "selected_soft_control_family": step.selected_family.value,
                "brake_state": step.brake_state.value,
                "contradiction_ref": step.contradiction_ref,
                "degradation_ref": step.degradation_ref,
                "outcome_class": step.outcome_class,
            }
            for step in steps
        ],
    }


def openai_uncertainty_scenario_inputs(
    spec: OpenAIUncertaintyPairSpec,
) -> dict[str, str]:
    return {
        "starting_request_or_event": (
            f"bounded OpenAI-host `response.completed` flow on `{spec.session_id}` "
            "with guarded uncertainty before certified resolution"
        ),
        "host_surface": (
            "OpenAI observe/bind plus commitment-path slice with contradiction-bearing "
            "degradation preserved across guarded uncertainty and certified resolution"
        ),
        "declared_scenario_goal": (
            "evaluate whether mediation improves OpenAI-host uncertainty handling "
            "without smoothing contradiction or degradation evidence or changing "
            "commitment truth"
        ),
        "bounded_environment_or_approval_context": (
            "`CommitmentEnvironmentHandle` with "
            "`available_query_kinds={EXECUTION_TRACE}` and "
            "`capability_tags={trace/read}` on `env_uncertainty_sensitive`"
        ),
    }


def openai_uncertainty_pair_evidence(
    spec: OpenAIUncertaintyPairSpec,
) -> tuple[ContradictionRecord, DegradationRecord]:
    return host_surface_degradation_pair(
        source_tag=spec.contradiction_source_tag,
        summary=spec.contradiction_summary,
        evidence_tags=frozenset({"openai", "approval-evidence", spec.uncertainty_spike_tag}),
        reason_code=spec.degradation_reason_code,
        capability_tags=frozenset({"trace/read"}),
    )


def openai_environment_handle() -> CommitmentEnvironmentHandle:
    return CommitmentEnvironmentHandle(
        available_query_kinds=frozenset({EXECUTION_TRACE}),
        capability_tags=frozenset({"trace/read"}),
    )


def _build_guard_step(
    spec: OpenAIUncertaintyPairSpec,
    contradiction: ContradictionRecord,
    degradation: DegradationRecord,
) -> _EpisodeStep:
    result = _evaluate_uncertainty_commitment(spec, contradiction, degradation)
    _assert_uncertified_result(result, spec, contradiction, degradation)
    _assert_selected_check(spec.guard_check_score, spec.guard_branch_score)
    brake = _guarded_brake(spec)
    return _EpisodeStep(
        step_id=f"{spec.baseline_step_prefix}-1",
        selected_family=SoftControlFamily.CHECK,
        brake_state=brake.state,
        outcome_class="uncertified-full-commitment",
        contradiction_ref=_contradiction_ref(contradiction),
        degradation_ref=degradation.reason_code,
    )


def _build_retry_step(
    spec: OpenAIUncertaintyPairSpec,
    contradiction: ContradictionRecord,
    degradation: DegradationRecord,
) -> _EpisodeStep:
    result = _evaluate_uncertainty_commitment(spec, contradiction, degradation)
    _assert_uncertified_result(result, spec, contradiction, degradation)
    _assert_selected_check(spec.retry_check_score, spec.retry_branch_score)
    brake = _guarded_brake(spec)
    return _EpisodeStep(
        step_id=f"{spec.baseline_step_prefix}-2",
        selected_family=SoftControlFamily.CHECK,
        brake_state=brake.state,
        outcome_class="uncertified-full-commitment",
        contradiction_ref=_contradiction_ref(contradiction),
        degradation_ref=degradation.reason_code,
    )


def _build_resolve_step(
    spec: OpenAIUncertaintyPairSpec,
    contradiction: ContradictionRecord,
    degradation: DegradationRecord,
) -> _EpisodeStep:
    result = _evaluate_uncertainty_commitment(
        spec,
        contradiction,
        degradation,
        include_provenance=True,
    )
    assert result.dispatch_decision.lane is DispatchLane.FULL_COMMITMENT
    assert result.candidate is not None
    assert result.candidate.candidate_id == spec.commitment_id
    assert result.verdict is not None
    assert result.verdict.status is CommitmentStatus.CERTIFIED
    assert result.verdict.provenance_manifest is not None
    assert result.verdict.degradation_refs == (degradation,)
    assert contradiction in result.verdict.contradiction_refs
    _assert_selected_check(spec.resolve_check_score, spec.resolve_branch_score)
    brake = evaluate_brake_state(())
    assert brake.state is BrakeState.QUIESCENT
    return _EpisodeStep(
        step_id=f"{spec.baseline_step_prefix}-3",
        selected_family=SoftControlFamily.CHECK,
        brake_state=brake.state,
        outcome_class="certified-full-commitment",
        contradiction_ref=_contradiction_ref(contradiction),
        degradation_ref=degradation.reason_code,
    )


def _evaluate_uncertainty_commitment(
    spec: OpenAIUncertaintyPairSpec,
    contradiction: ContradictionRecord,
    degradation: DegradationRecord,
    *,
    include_provenance: bool = False,
):
    provenance_manifest = None
    if include_provenance:
        provenance_manifest = provenance_manifest_for(spec.provenance_artifact_id)
    return evaluate_openai_host_commitment(
        "response.completed",
        {
            "commitment_id": spec.commitment_id,
            "session_id": spec.session_id,
            "externally_consequential": True,
        },
        environment_handle=openai_environment_handle(),
        provenance_manifest=provenance_manifest,
        contradiction_refs=(contradiction,),
        degradation_refs=(degradation,),
    )


def _assert_uncertified_result(
    result,
    spec: OpenAIUncertaintyPairSpec,
    contradiction: ContradictionRecord,
    degradation: DegradationRecord,
) -> None:
    assert result.dispatch_decision.lane is DispatchLane.FULL_COMMITMENT
    assert result.candidate is not None
    assert result.candidate.candidate_id == spec.commitment_id
    assert result.verdict is not None
    assert result.verdict.status is CommitmentStatus.UNCERTIFIED
    assert result.verdict.provenance_manifest is None
    assert result.verdict.degradation_refs == (degradation,)
    assert contradiction in result.verdict.contradiction_refs


def _assert_selected_check(check_score: float, branch_score: float) -> None:
    decision = neutral_dominance_decision(
        AllocationScorecard(
            scores=(
                AllocationScore(SoftControlFamily.NEUTRAL, 1.0),
                AllocationScore(SoftControlFamily.CHECK, check_score),
                AllocationScore(SoftControlFamily.BRANCH, branch_score),
            ),
            activation_threshold=0.1,
        )
    )
    assert decision.selected_family is SoftControlFamily.CHECK


def _guarded_brake(spec: OpenAIUncertaintyPairSpec):
    brake = evaluate_brake_state(
        (
            UncertaintyEstimate(
                "evidence",
                OPENAI_UNCERTAINTY_LEVEL,
                spike_tags=frozenset({spec.uncertainty_spike_tag}),
            ),
        )
    )
    assert brake.state is BrakeState.GUARDED
    return brake


def _contradiction_ref(contradiction: ContradictionRecord) -> str:
    return f"{contradiction.source_tag}:{contradiction.summary}"
