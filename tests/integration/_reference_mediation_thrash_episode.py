"""Build the live reference-host thrash baseline episode for mediation evidence."""

from __future__ import annotations

from dataclasses import dataclass

from cortex.core.commitments import CommitmentStatus
from cortex.core.dispatch import DispatchLane
from cortex.core.support import SupportCounter, SupportSessionState
from cortex.drivers.reference_host_commitment import (
    ReferenceHostCommitmentResult,
    evaluate_reference_host_commitment,
)
from cortex.sre.allocation import AllocationScore, AllocationScorecard
from cortex.sre.brake import BrakeState, evaluate_brake_state
from cortex.sre.branching import BranchOperation
from cortex.sre.families import SoftControlFamily
from cortex.sre.goals import GoalContinuityView
from cortex.sre.policy import neutral_dominance_decision
from cortex.sre.uncertainty import UncertaintyEstimate
from tests.integration._reference_lane import (
    provenance_manifest_for,
    reference_environment_handle,
)


EXPECTED_REFERENCE_THRASH_BRANCH_SEQUENCE = (
    BranchOperation.OPEN.value,
    BranchOperation.SUSPEND.value,
    BranchOperation.RESUME.value,
    BranchOperation.MERGE.value,
)


@dataclass(frozen=True, slots=True)
class _EpisodeStep:
    step_id: str
    result: ReferenceHostCommitmentResult
    payload_identity: str
    selected_family: SoftControlFamily
    brake_state: BrakeState
    goal_continuity: GoalContinuityView
    support_session: SupportSessionState
    outcome_class: str


def build_reference_thrash_episode_snapshot() -> dict[str, object]:
    environment_handle = reference_environment_handle()
    steps = (
        _build_open_step(environment_handle),
        _build_suspend_step(environment_handle),
        _build_resume_step(environment_handle),
        _build_merge_step(environment_handle),
    )
    branch_sequence = _derive_branch_sequence(steps)

    return {
        "scenario_id": "scenario_thrash_reference_01",
        "run_id": "reference_thrash_baseline_run_001",
        "paired_episode_set_id": "pair_reference_thrash_001",
        "session_id": "thrash-session-1",
        "candidate_id": "candidate-thrash-1",
        "commitment_id": "thrash-commit-1",
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


def _build_open_step(environment_handle) -> _EpisodeStep:
    result = evaluate_reference_host_commitment(
        "ApprovalRequest",
        {
            "candidate_id": "candidate-thrash-1",
            "session_id": "thrash-session-1",
        },
        environment_handle=environment_handle,
    )
    assert result.dispatch_decision.lane is DispatchLane.CANDIDATE_BEARING
    assert result.candidate is not None
    assert result.candidate.candidate_id == "candidate-thrash-1"
    assert result.verdict is None

    decision = neutral_dominance_decision(
        AllocationScorecard(
            scores=(
                AllocationScore(SoftControlFamily.NEUTRAL, 1.0),
                AllocationScore(SoftControlFamily.CHECK, 1.05),
                AllocationScore(SoftControlFamily.BRANCH, 1.25),
            ),
            activation_threshold=0.1,
        )
    )
    assert decision.selected_family is SoftControlFamily.BRANCH

    brake = evaluate_brake_state(())
    assert brake.state is BrakeState.QUIESCENT

    # The opened branch becomes the active track immediately so step 2 can
    # derive a lawful suspend event from state rather than prose.
    goal_continuity = GoalContinuityView(
        main_goal_ref="goal-thrash-main",
        active_track_ref="branch-approval-context",
        pending_goal_refs=(),
        resume_anchor_available=True,
    )
    support_session = SupportSessionState(
        branch_registry=("main", "branch-approval-context"),
        pending_goal_refs=(),
        budget_history=("budget/branch",),
        brake_history=("quiescent",),
        wake_counters=(SupportCounter("candidate-bearing", 1),),
        reminders=(),
    )
    return _EpisodeStep(
        step_id="thrash-step-1",
        result=result,
        payload_identity="candidate_id=candidate-thrash-1, session_id=thrash-session-1",
        selected_family=decision.selected_family,
        brake_state=brake.state,
        goal_continuity=goal_continuity,
        support_session=support_session,
        outcome_class="candidate-bearing",
    )


def _build_suspend_step(environment_handle) -> _EpisodeStep:
    result = evaluate_reference_host_commitment(
        "ApprovalResult",
        {
            "commitment_id": "thrash-commit-1",
            "session_id": "thrash-session-1",
            "externally_consequential": True,
        },
        environment_handle=environment_handle,
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
                0.62,
                spike_tags=frozenset({"goal-progress-ambiguity"}),
            ),
        )
    )
    assert brake.state is BrakeState.GUARDED

    decision = neutral_dominance_decision(
        AllocationScorecard(
            scores=(
                AllocationScore(SoftControlFamily.NEUTRAL, 1.0),
                AllocationScore(SoftControlFamily.CHECK, 1.18),
                AllocationScore(SoftControlFamily.BRANCH, 0.95),
            ),
            activation_threshold=0.1,
        )
    )
    assert decision.selected_family is SoftControlFamily.CHECK

    goal_continuity = GoalContinuityView(
        main_goal_ref="goal-thrash-main",
        active_track_ref="main",
        pending_goal_refs=("branch-approval-context",),
        resume_anchor_available=True,
    )
    support_session = SupportSessionState(
        branch_registry=("main", "branch-approval-context"),
        pending_goal_refs=("branch-approval-context",),
        budget_history=("budget/branch", "budget/check"),
        brake_history=("quiescent", "guarded"),
        wake_counters=(SupportCounter("candidate-bearing", 1),),
        reminders=("resume-branch-approval-context",),
    )
    return _EpisodeStep(
        step_id="thrash-step-2",
        result=result,
        payload_identity=(
            "commitment_id=thrash-commit-1, externally_consequential=True, "
            "session_id=thrash-session-1"
        ),
        selected_family=decision.selected_family,
        brake_state=brake.state,
        goal_continuity=goal_continuity,
        support_session=support_session,
        outcome_class="uncertified-full-commitment",
    )


def _build_resume_step(environment_handle) -> _EpisodeStep:
    result = evaluate_reference_host_commitment(
        "ApprovalRequest",
        {
            "candidate_id": "candidate-thrash-1",
            "session_id": "thrash-session-1",
        },
        environment_handle=environment_handle,
    )
    assert result.dispatch_decision.lane is DispatchLane.CANDIDATE_BEARING
    assert result.candidate is not None
    assert result.candidate.candidate_id == "candidate-thrash-1"
    assert result.verdict is None

    brake = evaluate_brake_state(())
    assert brake.state is BrakeState.QUIESCENT

    decision = neutral_dominance_decision(
        AllocationScorecard(
            scores=(
                AllocationScore(SoftControlFamily.NEUTRAL, 1.0),
                AllocationScore(SoftControlFamily.CHECK, 1.05),
                AllocationScore(SoftControlFamily.BRANCH, 1.22),
            ),
            activation_threshold=0.1,
        )
    )
    assert decision.selected_family is SoftControlFamily.BRANCH

    goal_continuity = GoalContinuityView(
        main_goal_ref="goal-thrash-main",
        active_track_ref="branch-approval-context",
        pending_goal_refs=(),
        resume_anchor_available=True,
    )
    support_session = SupportSessionState(
        branch_registry=("main", "branch-approval-context"),
        pending_goal_refs=(),
        budget_history=("budget/branch", "budget/check", "budget/branch"),
        brake_history=("quiescent", "guarded", "quiescent"),
        wake_counters=(SupportCounter("candidate-bearing", 2),),
        reminders=("collect-provenance-before-final-approval",),
    )
    return _EpisodeStep(
        step_id="thrash-step-3",
        result=result,
        payload_identity="candidate_id=candidate-thrash-1, session_id=thrash-session-1",
        selected_family=decision.selected_family,
        brake_state=brake.state,
        goal_continuity=goal_continuity,
        support_session=support_session,
        outcome_class="candidate-bearing",
    )


def _build_merge_step(environment_handle) -> _EpisodeStep:
    result = evaluate_reference_host_commitment(
        "ApprovalResult",
        {
            "commitment_id": "thrash-commit-1",
            "session_id": "thrash-session-1",
            "externally_consequential": True,
        },
        environment_handle=environment_handle,
        provenance_manifest=provenance_manifest_for("artifact-thrash-1"),
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
                AllocationScore(SoftControlFamily.CHECK, 1.12),
                AllocationScore(SoftControlFamily.BRANCH, 0.9),
            ),
            activation_threshold=0.1,
        )
    )
    assert decision.selected_family is SoftControlFamily.CHECK

    goal_continuity = GoalContinuityView(
        main_goal_ref="goal-thrash-main",
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
        step_id="thrash-step-4",
        result=result,
        payload_identity=(
            "commitment_id=thrash-commit-1, externally_consequential=True, "
            "session_id=thrash-session-1"
        ),
        selected_family=decision.selected_family,
        brake_state=brake.state,
        goal_continuity=goal_continuity,
        support_session=support_session,
        outcome_class="certified-full-commitment",
    )


def _derive_branch_sequence(steps: tuple[_EpisodeStep, ...]) -> tuple[str, ...]:
    previous_goal = GoalContinuityView(
        main_goal_ref="goal-thrash-main",
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

    assert tuple(operations) == EXPECTED_REFERENCE_THRASH_BRANCH_SEQUENCE
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


def _raw_host_event_name(result: ReferenceHostCommitmentResult) -> str:
    for field in result.bound_event.observation.event.payload_metadata:
        if field.key == "raw_host_event_name":
            return str(field.value)
    raise AssertionError("Missing raw_host_event_name metadata field.")
