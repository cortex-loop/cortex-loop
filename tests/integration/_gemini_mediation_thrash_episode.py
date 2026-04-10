"""Build the live Gemini-host thrash baseline episodes for mediation evidence."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from cortex.core.commitments import CommitmentStatus
from cortex.core.dispatch import DispatchLane
from cortex.core.support import SupportCounter, SupportSessionState
from cortex.drivers.gemini_host_commitment import (
    GeminiHostCommitmentResult,
    evaluate_gemini_host_commitment,
)
from cortex.sre.allocation import AllocationScore, AllocationScorecard
from cortex.sre.brake import BrakeState, evaluate_brake_state
from cortex.sre.branching import BranchOperation
from cortex.sre.families import SoftControlFamily
from cortex.sre.goals import GoalContinuityView
from cortex.sre.policy import neutral_dominance_decision
from cortex.sre.uncertainty import UncertaintyEstimate
from tests.integration._gemini_mediation_uncertainty_episode import (
    gemini_environment_handle,
)
from tests.integration._reference_lane import provenance_manifest_for


EXPECTED_GEMINI_THRASH_BRANCH_SEQUENCE = (
    BranchOperation.OPEN.value,
    BranchOperation.SUSPEND.value,
    BranchOperation.RESUME.value,
    BranchOperation.MERGE.value,
)
DEFAULT_GEMINI_THRASH_PAIR_KEY = "001"
GEMINI_THRASH_PAIR_KEYS = ("001", "002", "003")
GEMINI_THRASH_UNCERTAINTY_LEVEL = 0.62


@dataclass(frozen=True, slots=True)
class GeminiThrashPairSpec:
    pair_key: str
    pair_id: str
    baseline_run_id: str
    mediated_run_id: str
    session_id: str
    candidate_id: str
    commitment_id: str
    provenance_artifact_id: str
    branch_track_ref: str
    uncertainty_spike_tag: str
    open_check_score: float
    open_branch_score: float
    suspend_check_score: float
    suspend_branch_score: float
    resume_check_score: float
    resume_branch_score: float
    merge_check_score: float
    merge_branch_score: float

    @property
    def baseline_packet_path(self) -> str:
        return (
            "docs/lab/mediation_evidence/gemini/"
            f"scenario_thrash_gemini_01__baseline_non_mediated__run_{self.pair_key}.md"
        )

    @property
    def mediated_packet_path(self) -> str:
        return (
            "docs/lab/mediation_evidence/gemini/"
            f"scenario_thrash_gemini_01__experimental_mediated__run_{self.pair_key}.md"
        )

    @property
    def baseline_step_prefix(self) -> str:
        if self.pair_key == DEFAULT_GEMINI_THRASH_PAIR_KEY:
            return "gemini-thrash-step"
        return f"gemini-thrash-{self.pair_key}-step"

    @property
    def mediated_step_prefix(self) -> str:
        if self.pair_key == DEFAULT_GEMINI_THRASH_PAIR_KEY:
            return "gemini-thrash-mediated-step"
        return f"gemini-thrash-mediated-{self.pair_key}-step"


GEMINI_THRASH_PAIR_SPECS: Mapping[str, GeminiThrashPairSpec] = {
    "001": GeminiThrashPairSpec(
        pair_key="001",
        pair_id="pair_gemini_thrash_001",
        baseline_run_id="gemini_thrash_baseline_run_001",
        mediated_run_id="gemini_thrash_mediated_run_001",
        session_id="gemini-thrash-session-1",
        candidate_id="gemini-candidate-thrash-1",
        commitment_id="gemini-thrash-commit-1",
        provenance_artifact_id="gemini-artifact-thrash-1",
        branch_track_ref="gemini-branch-continuation-context",
        uncertainty_spike_tag="gemini-goal-progress-ambiguity",
        open_check_score=1.05,
        open_branch_score=1.25,
        suspend_check_score=1.18,
        suspend_branch_score=0.95,
        resume_check_score=1.05,
        resume_branch_score=1.22,
        merge_check_score=1.12,
        merge_branch_score=0.9,
    ),
    "002": GeminiThrashPairSpec(
        pair_key="002",
        pair_id="pair_gemini_thrash_002",
        baseline_run_id="gemini_thrash_baseline_run_002",
        mediated_run_id="gemini_thrash_mediated_run_002",
        session_id="gemini-thrash-session-2",
        candidate_id="gemini-candidate-thrash-2",
        commitment_id="gemini-thrash-commit-2",
        provenance_artifact_id="gemini-artifact-thrash-2",
        branch_track_ref="gemini-branch-provenance-review",
        uncertainty_spike_tag="gemini-provenance-lag-ambiguity",
        open_check_score=1.07,
        open_branch_score=1.27,
        suspend_check_score=1.20,
        suspend_branch_score=0.94,
        resume_check_score=1.04,
        resume_branch_score=1.19,
        merge_check_score=1.14,
        merge_branch_score=0.91,
    ),
    "003": GeminiThrashPairSpec(
        pair_key="003",
        pair_id="pair_gemini_thrash_003",
        baseline_run_id="gemini_thrash_baseline_run_003",
        mediated_run_id="gemini_thrash_mediated_run_003",
        session_id="gemini-thrash-session-3",
        candidate_id="gemini-candidate-thrash-3",
        commitment_id="gemini-thrash-commit-3",
        provenance_artifact_id="gemini-artifact-thrash-3",
        branch_track_ref="gemini-branch-evidence-confirmation",
        uncertainty_spike_tag="gemini-artifact-consistency-ambiguity",
        open_check_score=1.03,
        open_branch_score=1.24,
        suspend_check_score=1.17,
        suspend_branch_score=0.96,
        resume_check_score=1.06,
        resume_branch_score=1.21,
        merge_check_score=1.13,
        merge_branch_score=0.92,
    ),
}


@dataclass(frozen=True, slots=True)
class _EpisodeStep:
    step_id: str
    result: GeminiHostCommitmentResult
    payload_identity: str
    selected_family: SoftControlFamily
    brake_state: BrakeState
    goal_continuity: GoalContinuityView
    support_session: SupportSessionState
    outcome_class: str


def build_gemini_thrash_episode_snapshot(
    pair_key: str = DEFAULT_GEMINI_THRASH_PAIR_KEY,
) -> dict[str, object]:
    spec = GEMINI_THRASH_PAIR_SPECS[pair_key]
    steps = (
        _build_open_step(spec),
        _build_suspend_step(spec),
        _build_resume_step(spec),
        _build_merge_step(spec),
    )
    branch_sequence = _derive_branch_sequence(steps)

    return {
        "scenario_id": "scenario_thrash_gemini_01",
        "run_id": spec.baseline_run_id,
        "paired_episode_set_id": spec.pair_id,
        "session_id": spec.session_id,
        "candidate_id": spec.candidate_id,
        "commitment_id": spec.commitment_id,
        "provenance_artifact_id": spec.provenance_artifact_id,
        "branch_track_ref": spec.branch_track_ref,
        "uncertainty_spike_tag": spec.uncertainty_spike_tag,
        "branch_sequence": list(branch_sequence),
        "event_trace_refs": ", ".join(
            f"{step.step_id}:{_raw_host_event_name(step.result)}/{operation}"
            for step, operation in zip(steps, branch_sequence, strict=True)
        ),
        "steps": [
            {
                "step_id": step.step_id,
                "host_event_name": _raw_host_event_name(step.result),
                "payload_identity": step.payload_identity,
                "dispatch_lane": step.result.dispatch_decision.lane.value,
                "selected_soft_control_family": step.selected_family.value,
                "brake_state": step.brake_state.value,
                "goal_continuity_view": {
                    "main_goal_ref": step.goal_continuity.main_goal_ref,
                    "active_track_ref": step.goal_continuity.active_track_ref,
                    "pending_goal_refs": list(step.goal_continuity.pending_goal_refs),
                    "resume_anchor_available": step.goal_continuity.resume_anchor_available,
                },
                "support_session_snapshot": {
                    "branch_registry": list(step.support_session.branch_registry),
                    "pending_goal_refs": list(step.support_session.pending_goal_refs),
                    "budget_history": list(step.support_session.budget_history),
                    "brake_history": list(step.support_session.brake_history),
                    "wake_counters": {
                        counter.counter_tag: counter.count
                        for counter in step.support_session.wake_counters
                    },
                    "reminders": list(step.support_session.reminders),
                },
                "derived_branch_operation": operation,
                "outcome_class": step.outcome_class,
            }
            for step, operation in zip(steps, branch_sequence, strict=True)
        ],
    }


def _build_open_step(spec: GeminiThrashPairSpec) -> _EpisodeStep:
    result = evaluate_gemini_host_commitment(
        "content.delta",
        {
            "interaction": {"id": spec.session_id},
            "session_id": spec.session_id,
            "candidate_id": spec.candidate_id,
            "stop_fields": {"claim_id": spec.candidate_id},
        },
        environment_handle=gemini_environment_handle(),
    )
    assert result.dispatch_decision.lane is DispatchLane.CANDIDATE_BEARING
    assert result.candidate is not None
    assert result.candidate.candidate_id == spec.candidate_id
    assert result.verdict is None

    decision = neutral_dominance_decision(
        AllocationScorecard(
            scores=(
                AllocationScore(SoftControlFamily.NEUTRAL, 1.0),
                AllocationScore(SoftControlFamily.CHECK, spec.open_check_score),
                AllocationScore(SoftControlFamily.BRANCH, spec.open_branch_score),
            ),
            activation_threshold=0.1,
        )
    )
    assert decision.selected_family is SoftControlFamily.BRANCH

    brake = evaluate_brake_state(())
    assert brake.state is BrakeState.QUIESCENT

    goal_continuity = GoalContinuityView(
        main_goal_ref="goal-gemini-thrash-main",
        active_track_ref=spec.branch_track_ref,
        pending_goal_refs=(),
        resume_anchor_available=True,
    )
    support_session = SupportSessionState(
        branch_registry=("main", spec.branch_track_ref),
        pending_goal_refs=(),
        budget_history=("budget/branch",),
        brake_history=("quiescent",),
        wake_counters=(SupportCounter("candidate-bearing", 1),),
        reminders=(),
    )
    return _EpisodeStep(
        step_id=f"{spec.baseline_step_prefix}-1",
        result=result,
        payload_identity=(
            f"candidate_id={spec.candidate_id}, session_id={spec.session_id}"
        ),
        selected_family=decision.selected_family,
        brake_state=brake.state,
        goal_continuity=goal_continuity,
        support_session=support_session,
        outcome_class="candidate-bearing",
    )


def _build_suspend_step(spec: GeminiThrashPairSpec) -> _EpisodeStep:
    result = evaluate_gemini_host_commitment(
        "interaction.complete",
        {
            "commitment_id": spec.commitment_id,
            "session_id": spec.session_id,
            "externally_consequential": True,
        },
        environment_handle=gemini_environment_handle(),
    )
    assert result.dispatch_decision.lane is DispatchLane.FULL_COMMITMENT
    assert result.verdict is not None
    assert result.verdict.status is CommitmentStatus.UNCERTIFIED
    assert result.verdict.provenance_manifest is None
    assert result.verdict.contradiction_refs == ()
    assert result.verdict.degradation_refs == ()

    brake = evaluate_brake_state(
        (
            UncertaintyEstimate(
                "evidence",
                GEMINI_THRASH_UNCERTAINTY_LEVEL,
                spike_tags=frozenset({spec.uncertainty_spike_tag}),
            ),
        )
    )
    assert brake.state is BrakeState.GUARDED

    decision = neutral_dominance_decision(
        AllocationScorecard(
            scores=(
                AllocationScore(SoftControlFamily.NEUTRAL, 1.0),
                AllocationScore(SoftControlFamily.CHECK, spec.suspend_check_score),
                AllocationScore(SoftControlFamily.BRANCH, spec.suspend_branch_score),
            ),
            activation_threshold=0.1,
        )
    )
    assert decision.selected_family is SoftControlFamily.CHECK

    goal_continuity = GoalContinuityView(
        main_goal_ref="goal-gemini-thrash-main",
        active_track_ref="main",
        pending_goal_refs=(spec.branch_track_ref,),
        resume_anchor_available=True,
    )
    support_session = SupportSessionState(
        branch_registry=("main", spec.branch_track_ref),
        pending_goal_refs=(spec.branch_track_ref,),
        budget_history=("budget/branch", "budget/check"),
        brake_history=("quiescent", "guarded"),
        wake_counters=(SupportCounter("candidate-bearing", 1),),
        reminders=(f"resume-{spec.branch_track_ref}",),
    )
    return _EpisodeStep(
        step_id=f"{spec.baseline_step_prefix}-2",
        result=result,
        payload_identity=(
            f"commitment_id={spec.commitment_id}, externally_consequential=True, "
            f"session_id={spec.session_id}"
        ),
        selected_family=decision.selected_family,
        brake_state=brake.state,
        goal_continuity=goal_continuity,
        support_session=support_session,
        outcome_class="uncertified-full-commitment",
    )


def _build_resume_step(spec: GeminiThrashPairSpec) -> _EpisodeStep:
    result = evaluate_gemini_host_commitment(
        "content.delta",
        {
            "interaction": {"id": spec.session_id},
            "session_id": spec.session_id,
            "candidate_id": spec.candidate_id,
            "stop_fields": {"claim_id": spec.candidate_id},
        },
        environment_handle=gemini_environment_handle(),
    )
    assert result.dispatch_decision.lane is DispatchLane.CANDIDATE_BEARING
    assert result.candidate is not None
    assert result.candidate.candidate_id == spec.candidate_id
    assert result.verdict is None

    brake = evaluate_brake_state(())
    assert brake.state is BrakeState.QUIESCENT

    decision = neutral_dominance_decision(
        AllocationScorecard(
            scores=(
                AllocationScore(SoftControlFamily.NEUTRAL, 1.0),
                AllocationScore(SoftControlFamily.CHECK, spec.resume_check_score),
                AllocationScore(SoftControlFamily.BRANCH, spec.resume_branch_score),
            ),
            activation_threshold=0.1,
        )
    )
    assert decision.selected_family is SoftControlFamily.BRANCH

    goal_continuity = GoalContinuityView(
        main_goal_ref="goal-gemini-thrash-main",
        active_track_ref=spec.branch_track_ref,
        pending_goal_refs=(),
        resume_anchor_available=True,
    )
    support_session = SupportSessionState(
        branch_registry=("main", spec.branch_track_ref),
        pending_goal_refs=(),
        budget_history=("budget/branch", "budget/check", "budget/branch"),
        brake_history=("quiescent", "guarded", "quiescent"),
        wake_counters=(SupportCounter("candidate-bearing", 2),),
        reminders=("collect-provenance-before-final-merge",),
    )
    return _EpisodeStep(
        step_id=f"{spec.baseline_step_prefix}-3",
        result=result,
        payload_identity=(
            f"candidate_id={spec.candidate_id}, session_id={spec.session_id}"
        ),
        selected_family=decision.selected_family,
        brake_state=brake.state,
        goal_continuity=goal_continuity,
        support_session=support_session,
        outcome_class="candidate-bearing",
    )


def _build_merge_step(spec: GeminiThrashPairSpec) -> _EpisodeStep:
    result = evaluate_gemini_host_commitment(
        "interaction.complete",
        {
            "commitment_id": spec.commitment_id,
            "session_id": spec.session_id,
            "externally_consequential": True,
        },
        environment_handle=gemini_environment_handle(),
        provenance_manifest=provenance_manifest_for(spec.provenance_artifact_id),
    )
    assert result.dispatch_decision.lane is DispatchLane.FULL_COMMITMENT
    assert result.verdict is not None
    assert result.verdict.status is CommitmentStatus.CERTIFIED
    assert result.verdict.contradiction_refs == ()
    assert result.verdict.degradation_refs == ()

    brake = evaluate_brake_state(())
    assert brake.state is BrakeState.QUIESCENT

    decision = neutral_dominance_decision(
        AllocationScorecard(
            scores=(
                AllocationScore(SoftControlFamily.NEUTRAL, 1.0),
                AllocationScore(SoftControlFamily.CHECK, spec.merge_check_score),
                AllocationScore(SoftControlFamily.BRANCH, spec.merge_branch_score),
            ),
            activation_threshold=0.1,
        )
    )
    assert decision.selected_family is SoftControlFamily.CHECK

    goal_continuity = GoalContinuityView(
        main_goal_ref="goal-gemini-thrash-main",
        active_track_ref="main",
        pending_goal_refs=(),
        resume_anchor_available=True,
    )
    support_session = SupportSessionState(
        branch_registry=("main",),
        pending_goal_refs=(),
        budget_history=("budget/branch", "budget/check", "budget/branch", "budget/check"),
        brake_history=("quiescent", "guarded", "quiescent", "quiescent"),
        wake_counters=(SupportCounter("candidate-bearing", 2),),
        reminders=(),
    )
    return _EpisodeStep(
        step_id=f"{spec.baseline_step_prefix}-4",
        result=result,
        payload_identity=(
            f"commitment_id={spec.commitment_id}, externally_consequential=True, "
            f"session_id={spec.session_id}"
        ),
        selected_family=decision.selected_family,
        brake_state=brake.state,
        goal_continuity=goal_continuity,
        support_session=support_session,
        outcome_class="certified-full-commitment",
    )


def _derive_branch_sequence(steps: tuple[_EpisodeStep, ...]) -> tuple[str, ...]:
    previous_goal = GoalContinuityView(
        main_goal_ref="goal-gemini-thrash-main",
        active_track_ref="main",
        pending_goal_refs=(),
        resume_anchor_available=True,
    )
    previous_session = SupportSessionState(
        branch_registry=("main",),
        pending_goal_refs=(),
        budget_history=(),
        brake_history=(),
        wake_counters=(),
        reminders=(),
    )

    operations = []
    for step in steps:
        operation = _derive_branch_operation(previous_goal, previous_session, step)
        operations.append(operation.value)
        previous_goal = step.goal_continuity
        previous_session = step.support_session

    assert tuple(operations) == EXPECTED_GEMINI_THRASH_BRANCH_SEQUENCE
    return tuple(operations)


def _derive_branch_operation(
    previous_goal: GoalContinuityView,
    previous_session: SupportSessionState,
    current: _EpisodeStep,
) -> BranchOperation:
    previous_branches = set(previous_session.branch_registry)
    current_branches = set(current.support_session.branch_registry)

    if (
        any(
            branch != "main" and branch not in previous_branches
            for branch in current.support_session.branch_registry
        )
        and current.selected_family is SoftControlFamily.BRANCH
    ):
        return BranchOperation.OPEN

    previous_active_track = previous_goal.active_track_ref
    current_active_track = current.goal_continuity.active_track_ref
    if (
        previous_active_track is not None
        and previous_active_track != "main"
        and current_active_track == "main"
        and previous_active_track in current_branches
    ):
        return BranchOperation.SUSPEND

    if (
        previous_active_track == "main"
        and current_active_track is not None
        and current_active_track != "main"
        and current_active_track in previous_branches
        and current.goal_continuity.resume_anchor_available
    ):
        return BranchOperation.RESUME

    if (
        any(branch != "main" and branch not in current_branches for branch in previous_branches)
        and current.result.dispatch_decision.lane is DispatchLane.FULL_COMMITMENT
        and current.result.verdict is not None
        and current.result.verdict.status is CommitmentStatus.CERTIFIED
    ):
        return BranchOperation.MERGE

    raise AssertionError(f"Could not derive branch operation for {current.step_id}.")


def _raw_host_event_name(result: GeminiHostCommitmentResult) -> str:
    for field in result.bound_event.observation.event.payload_metadata:
        if field.key == "raw_host_event_name":
            return str(field.value)
    raise AssertionError("Missing raw_host_event_name metadata field.")
