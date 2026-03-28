"""Build the live reference-host uncertainty baseline episodes for mediation evidence."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from cortex.core.commitments import CommitmentStatus
from cortex.core.dispatch import DispatchLane
from cortex.core.errors import ContradictionRecord, DegradationRecord
from cortex.drivers.reference_host_commitment import evaluate_reference_host_commitment
from cortex.sre.allocation import AllocationScore, AllocationScorecard
from cortex.sre.brake import BrakeState, evaluate_brake_state
from cortex.sre.families import SoftControlFamily
from cortex.sre.policy import neutral_dominance_decision
from cortex.sre.uncertainty import UncertaintyEstimate
from tests.integration._reference_lane import (
    assert_reference_commitment_result_preserves_degradation_pair,
    assert_reference_verdict_status,
    host_surface_degradation_pair,
    provenance_manifest_for,
    reference_environment_handle,
)


EXPECTED_REFERENCE_UNCERTAINTY_STEP_SEQUENCE = ("guard", "retry", "resolve")
DEFAULT_REFERENCE_UNCERTAINTY_PAIR_KEY = "001"
REFERENCE_UNCERTAINTY_PAIR_KEYS = ("001", "002", "003")
REFERENCE_UNCERTAINTY_LEVEL = 0.62


@dataclass(frozen=True, slots=True)
class ReferenceUncertaintyPairSpec:
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
            "docs/mediation_evidence/reference/"
            f"scenario_uncertainty_reference_01__baseline_non_mediated__run_{self.pair_key}.md"
        )

    @property
    def mediated_packet_path(self) -> str:
        return (
            "docs/mediation_evidence/reference/"
            f"scenario_uncertainty_reference_01__experimental_mediated__run_{self.pair_key}.md"
        )

    @property
    def baseline_step_prefix(self) -> str:
        if self.pair_key == DEFAULT_REFERENCE_UNCERTAINTY_PAIR_KEY:
            return "uncertainty-step"
        return f"uncertainty-{self.pair_key}-step"

    @property
    def mediated_step_prefix(self) -> str:
        if self.pair_key == DEFAULT_REFERENCE_UNCERTAINTY_PAIR_KEY:
            return "uncertainty-mediated-step"
        return f"uncertainty-mediated-{self.pair_key}-step"


REFERENCE_UNCERTAINTY_PAIR_SPECS: Mapping[str, ReferenceUncertaintyPairSpec] = {
    "001": ReferenceUncertaintyPairSpec(
        pair_key="001",
        pair_id="pair_reference_uncertainty_001",
        baseline_run_id="reference_uncertainty_baseline_run_001",
        mediated_run_id="reference_uncertainty_mediated_run_001",
        session_id="uncertainty-session-1",
        commitment_id="uncertainty-commit-1",
        provenance_artifact_id="artifact-uncertainty-1",
        contradiction_source_tag="trace-check",
        contradiction_summary="execution trace omits approval evidence",
        degradation_reason_code="trace-evidence-partial",
        uncertainty_spike_tag="trace-gap-ambiguity",
        guard_check_score=1.22,
        guard_branch_score=0.92,
        retry_check_score=1.18,
        retry_branch_score=0.90,
        resolve_check_score=1.10,
        resolve_branch_score=0.88,
    ),
    "002": ReferenceUncertaintyPairSpec(
        pair_key="002",
        pair_id="pair_reference_uncertainty_002",
        baseline_run_id="reference_uncertainty_baseline_run_002",
        mediated_run_id="reference_uncertainty_mediated_run_002",
        session_id="uncertainty-session-2",
        commitment_id="uncertainty-commit-2",
        provenance_artifact_id="artifact-uncertainty-2",
        contradiction_source_tag="receipt-check",
        contradiction_summary="provenance receipt remains incomplete",
        degradation_reason_code="receipt-evidence-partial",
        uncertainty_spike_tag="receipt-lag-ambiguity",
        guard_check_score=1.24,
        guard_branch_score=0.91,
        retry_check_score=1.19,
        retry_branch_score=0.89,
        resolve_check_score=1.11,
        resolve_branch_score=0.87,
    ),
    "003": ReferenceUncertaintyPairSpec(
        pair_key="003",
        pair_id="pair_reference_uncertainty_003",
        baseline_run_id="reference_uncertainty_baseline_run_003",
        mediated_run_id="reference_uncertainty_mediated_run_003",
        session_id="uncertainty-session-3",
        commitment_id="uncertainty-commit-3",
        provenance_artifact_id="artifact-uncertainty-3",
        contradiction_source_tag="artifact-check",
        contradiction_summary="artifact chain remains unconfirmed",
        degradation_reason_code="artifact-chain-partial",
        uncertainty_spike_tag="artifact-chain-ambiguity",
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


def build_reference_uncertainty_episode_snapshot(
    pair_key: str = DEFAULT_REFERENCE_UNCERTAINTY_PAIR_KEY,
) -> dict[str, object]:
    spec = REFERENCE_UNCERTAINTY_PAIR_SPECS[pair_key]
    contradiction, degradation = _pair_evidence(spec)
    steps = (
        _build_guard_step(spec, contradiction, degradation),
        _build_retry_step(spec, contradiction, degradation),
        _build_resolve_step(spec, contradiction, degradation),
    )

    return {
        "scenario_id": "scenario_uncertainty_reference_01",
        "run_id": spec.baseline_run_id,
        "paired_episode_set_id": spec.pair_id,
        "session_id": spec.session_id,
        "commitment_id": spec.commitment_id,
        "provenance_artifact_id": spec.provenance_artifact_id,
        "contradiction_ref": _contradiction_ref(contradiction),
        "degradation_ref": degradation.reason_code,
        "uncertainty_spike_tag": spec.uncertainty_spike_tag,
        "step_sequence": list(EXPECTED_REFERENCE_UNCERTAINTY_STEP_SEQUENCE),
        "uncertified_loop_count": 2,
        "event_trace_refs": ", ".join(
            (
                f"{spec.baseline_step_prefix}-1:ApprovalResult/guard",
                f"{spec.baseline_step_prefix}-2:ApprovalResult/retry",
                f"{spec.baseline_step_prefix}-3:ApprovalResult/resolve",
            )
        ),
        "steps": [
            {
                "step_id": step.step_id,
                "host_event_name": "ApprovalResult",
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


def reference_uncertainty_scenario_inputs(
    spec: ReferenceUncertaintyPairSpec,
) -> dict[str, str]:
    return {
        "starting_request_or_event": (
            f"bounded reference-host approval result flow on `{spec.session_id}` with "
            "guarded uncertainty before certified resolution"
        ),
        "host_surface": (
            "reference-host commitment path with contradiction-bearing degradation "
            "preserved across guarded uncertainty and certified resolution"
        ),
        "declared_scenario_goal": (
            "evaluate whether mediation improves uncertainty handling on a bounded "
            "reference-host episode without smoothing contradictions, removing "
            "degradation evidence, or changing commitment truth"
        ),
        "bounded_environment_or_approval_context": (
            "`CommitmentEnvironmentHandle` with "
            "`available_query_kinds={EXECUTION_TRACE}` and "
            "`capability_tags={trace/read}` on `env_uncertainty_sensitive`"
        ),
    }


def _build_guard_step(
    spec: ReferenceUncertaintyPairSpec,
    contradiction: ContradictionRecord,
    degradation: DegradationRecord,
) -> _EpisodeStep:
    result = _evaluate_uncertainty_commitment(spec, contradiction, degradation)
    _assert_uncertified_result(result, contradiction, degradation)
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
    spec: ReferenceUncertaintyPairSpec,
    contradiction: ContradictionRecord,
    degradation: DegradationRecord,
) -> _EpisodeStep:
    result = _evaluate_uncertainty_commitment(spec, contradiction, degradation)
    _assert_uncertified_result(result, contradiction, degradation)
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
    spec: ReferenceUncertaintyPairSpec,
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
    assert_reference_verdict_status(result, CommitmentStatus.CERTIFIED)
    assert result.verdict is not None
    assert result.verdict.provenance_manifest is not None
    assert_reference_commitment_result_preserves_degradation_pair(
        result,
        contradiction,
        degradation,
    )
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
    spec: ReferenceUncertaintyPairSpec,
    contradiction: ContradictionRecord,
    degradation: DegradationRecord,
    *,
    include_provenance: bool = False,
):
    provenance_manifest = None
    if include_provenance:
        provenance_manifest = provenance_manifest_for(spec.provenance_artifact_id)
    return evaluate_reference_host_commitment(
        "ApprovalResult",
        {
            "commitment_id": spec.commitment_id,
            "session_id": spec.session_id,
            "externally_consequential": True,
        },
        environment_handle=reference_environment_handle(),
        provenance_manifest=provenance_manifest,
        contradiction_refs=(contradiction,),
        degradation_refs=(degradation,),
    )


def _assert_uncertified_result(result, contradiction: ContradictionRecord, degradation: DegradationRecord) -> None:
    assert result.dispatch_decision.lane is DispatchLane.FULL_COMMITMENT
    assert_reference_verdict_status(result, CommitmentStatus.UNCERTIFIED)
    assert result.verdict is not None
    assert result.verdict.provenance_manifest is None
    assert_reference_commitment_result_preserves_degradation_pair(
        result,
        contradiction,
        degradation,
    )


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


def _guarded_brake(spec: ReferenceUncertaintyPairSpec):
    brake = evaluate_brake_state(
        (
            UncertaintyEstimate(
                "evidence",
                REFERENCE_UNCERTAINTY_LEVEL,
                spike_tags=frozenset({spec.uncertainty_spike_tag}),
            ),
        )
    )
    assert brake.state is BrakeState.GUARDED
    return brake


def _pair_evidence(
    spec: ReferenceUncertaintyPairSpec,
) -> tuple[ContradictionRecord, DegradationRecord]:
    return host_surface_degradation_pair(
        source_tag=spec.contradiction_source_tag,
        summary=spec.contradiction_summary,
        evidence_tags=frozenset({"approval-evidence", spec.uncertainty_spike_tag}),
        reason_code=spec.degradation_reason_code,
        capability_tags=frozenset({"trace/read"}),
    )


def _contradiction_ref(contradiction: ContradictionRecord) -> str:
    return f"{contradiction.source_tag}:{contradiction.summary}"
