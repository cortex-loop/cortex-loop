"""Focused unit tests for the first computed reference executive-state builder."""

from __future__ import annotations

from cortex.core.environment import (
    CAPABILITY_VIEW,
    EXECUTION_TRACE,
    ExecutiveEnvironmentView,
)
from cortex.core.errors import ContradictionRecord, DegradationRecord
from cortex.core.support import (
    SupportExecMemoryState,
    SupportHostState,
    SupportSessionState,
    SupportSnapshot,
    SupportTraceState,
)
from cortex.drivers.reference_host import observe_reference_host_event
from cortex.runtime.reference import ReferenceRuntimeSession
from cortex.sre.brake import BrakeState
from cortex.sre.feedback import ReferenceRealizationFeedback
from cortex.sre.feedback import ReferenceRealizationFeedbackWindow
from cortex.sre.families import SoftControlFamily
from cortex.sre.reference_builder import build_reference_executive_state


def test_build_reference_executive_state_for_cheap_event_stays_pass_through_and_low_budget() -> None:
    state = build_reference_executive_state(
        observe_reference_host_event("ContextLoad", {"session_id": "runtime-1"}).observation,
        SupportSnapshot(
            trace=SupportTraceState(),
            session=SupportSessionState(branch_registry=("main",)),
            host=SupportHostState(),
            exec_memory_pub=SupportExecMemoryState(),
        ),
        ExecutiveEnvironmentView(
            available_query_kinds=frozenset({CAPABILITY_VIEW, EXECUTION_TRACE}),
            host_capability_tags=frozenset({"reference-local"}),
        ),
        ReferenceRuntimeSession(
            session_id="runtime-1",
            event_index=1,
            active_track_ref="main",
            budget_history=("shell-low",),
            brake_history=("quiescent",),
            last_selected_family=SoftControlFamily.NEUTRAL,
        ),
    )

    assert state.goal_continuity.main_goal_ref is None
    assert state.goal_continuity.active_track_ref == "main"
    assert state.mode_and_gating.mode_tag == "pass_through"
    assert state.control_allocation.budget_band == "low"
    assert state.control_allocation.top_family_set == frozenset({SoftControlFamily.NEUTRAL})
    assert state.brake.brake_state is BrakeState.QUIESCENT


def test_build_reference_executive_state_admits_seek_context_under_missing_capability_pressure() -> None:
    state = build_reference_executive_state(
        observe_reference_host_event(
            "ContextLoad",
            {"session_id": "runtime-j4b-gap"},
        ).observation,
        SupportSnapshot(
            trace=SupportTraceState(),
            session=SupportSessionState(branch_registry=("main",)),
            host=SupportHostState(constraint_tags=frozenset({"missing-capability"})),
            exec_memory_pub=SupportExecMemoryState(),
        ),
        ExecutiveEnvironmentView(
            available_query_kinds=frozenset({EXECUTION_TRACE}),
            host_capability_tags=frozenset({"reference-local"}),
        ),
        ReferenceRuntimeSession(
            session_id="runtime-j4b-gap",
            event_index=1,
            active_track_ref="main",
            budget_history=("shell-low",),
            brake_history=("quiescent",),
            last_selected_family=SoftControlFamily.NEUTRAL,
        ),
    )

    assert state.control_allocation.host_friction_tags == frozenset(
        {
            "missing-capability",
            "capability-view-missing",
        }
    )
    assert state.mode_and_gating.family_mask == frozenset(
        {
            SoftControlFamily.NEUTRAL,
            SoftControlFamily.CHECK,
            SoftControlFamily.BRAKE,
            SoftControlFamily.SEEK_CONTEXT,
        }
    )
    assert state.control_allocation.top_family_set == frozenset(
        {
            SoftControlFamily.NEUTRAL,
            SoftControlFamily.BRAKE,
            SoftControlFamily.SEEK_CONTEXT,
        }
    )
    assert state.brake.brake_state is BrakeState.GUARDED
    assert SoftControlFamily.SEEK_CONTEXT in state.mode_and_gating.family_mask
    assert SoftControlFamily.SEEK_CONTEXT in state.control_allocation.top_family_set


def test_build_reference_executive_state_keeps_seek_context_closed_under_generic_host_friction() -> None:
    state = build_reference_executive_state(
        observe_reference_host_event(
            "ContextLoad",
            {"session_id": "runtime-generic-host-friction"},
        ).observation,
        SupportSnapshot(
            trace=SupportTraceState(),
            session=SupportSessionState(branch_registry=("main",)),
            host=SupportHostState(constraint_tags=frozenset({"single-process-limit"})),
            exec_memory_pub=SupportExecMemoryState(),
        ),
        ExecutiveEnvironmentView(
            available_query_kinds=frozenset({CAPABILITY_VIEW, EXECUTION_TRACE}),
            host_capability_tags=frozenset({"reference-local"}),
        ),
        ReferenceRuntimeSession(
            session_id="runtime-generic-host-friction",
            event_index=1,
            active_track_ref="main",
            budget_history=("shell-low",),
            brake_history=("quiescent",),
            last_selected_family=SoftControlFamily.NEUTRAL,
        ),
    )

    assert state.control_allocation.host_friction_tags == frozenset({"single-process-limit"})
    assert state.mode_and_gating.family_mask == frozenset(
        {
            SoftControlFamily.NEUTRAL,
            SoftControlFamily.CHECK,
            SoftControlFamily.BRAKE,
        }
    )
    assert state.control_allocation.top_family_set == frozenset(
        {
            SoftControlFamily.NEUTRAL,
            SoftControlFamily.BRAKE,
        }
    )
    assert state.brake.brake_state is BrakeState.GUARDED
    assert SoftControlFamily.SEEK_CONTEXT not in state.mode_and_gating.family_mask
    assert SoftControlFamily.SEEK_CONTEXT not in state.control_allocation.top_family_set


def test_build_reference_executive_state_for_candidate_bearing_event_surfaces_review_mode() -> None:
    state = build_reference_executive_state(
        observe_reference_host_event(
            "ApprovalRequest",
            {"session_id": "runtime-2", "candidate_id": "candidate-1"},
        ).observation,
        SupportSnapshot(
            trace=SupportTraceState(),
            session=SupportSessionState(
                branch_registry=("main",),
                pending_goal_refs=("goal-review",),
            ),
            host=SupportHostState(),
            exec_memory_pub=SupportExecMemoryState(),
        ),
        ExecutiveEnvironmentView(
            available_query_kinds=frozenset({CAPABILITY_VIEW, EXECUTION_TRACE}),
            host_capability_tags=frozenset({"reference-local"}),
        ),
        ReferenceRuntimeSession(
            session_id="runtime-2",
            event_index=2,
            active_track_ref="main",
            budget_history=("shell-low", "shell-medium"),
            brake_history=("quiescent", "quiescent"),
            last_selected_family=SoftControlFamily.NEUTRAL,
        ),
    )

    assert state.goal_continuity.main_goal_ref == "goal-review"
    assert state.mode_and_gating.mode_tag == "review_pending"
    assert state.control_allocation.budget_band == "medium"
    assert state.control_allocation.top_family_set == frozenset(
        {SoftControlFamily.NEUTRAL, SoftControlFamily.CHECK}
    )
    assert state.brake.brake_state is BrakeState.QUIESCENT


def test_build_reference_executive_state_for_full_commitment_event_preserves_high_budget_band() -> None:
    state = build_reference_executive_state(
        observe_reference_host_event(
            "ApprovalResult",
            {
                "session_id": "runtime-3",
                "commitment_id": "commit-1",
                "externally_consequential": True,
                "result_artifact_ref": "artifact-1",
            },
        ).observation,
        SupportSnapshot(
            trace=SupportTraceState(),
            session=SupportSessionState(branch_registry=("main",)),
            host=SupportHostState(),
            exec_memory_pub=SupportExecMemoryState(),
        ),
        ExecutiveEnvironmentView(
            available_query_kinds=frozenset({CAPABILITY_VIEW, EXECUTION_TRACE}),
            host_capability_tags=frozenset({"reference-local"}),
        ),
        ReferenceRuntimeSession(
            session_id="runtime-3",
            event_index=3,
            active_track_ref="main",
            budget_history=("shell-low", "shell-medium", "shell-high"),
            brake_history=("quiescent", "quiescent", "quiescent"),
            last_selected_family=SoftControlFamily.NEUTRAL,
        ),
    )

    assert state.mode_and_gating.mode_tag == "commitment_path"
    assert state.control_allocation.budget_band == "high"
    assert state.control_allocation.top_family_set == frozenset({SoftControlFamily.NEUTRAL})
    assert state.uncertainty_monitoring.classwise_uncertainty[0].class_tag == "evidence"
    assert state.brake.brake_state is BrakeState.QUIESCENT


def test_build_reference_executive_state_surfaces_guarded_brake_when_snapshot_has_degradation() -> None:
    state = build_reference_executive_state(
        observe_reference_host_event("ContextLoad", {"session_id": "runtime-4"}).observation,
        SupportSnapshot(
            trace=SupportTraceState(
                degradation_records=(
                    DegradationRecord(
                        reason_code="host-friction-spike",
                        contradiction_records=(
                            ContradictionRecord(
                                source_tag="environment-drift",
                                summary="host environment drifted",
                            ),
                        ),
                    ),
                ),
            ),
            session=SupportSessionState(
                branch_registry=("main", "review-track"),
                reminders=("resume-anchor-missing",),
            ),
            host=SupportHostState(constraint_tags=frozenset({"single-process-limit"})),
            exec_memory_pub=SupportExecMemoryState(),
        ),
        ExecutiveEnvironmentView(
            available_query_kinds=frozenset({EXECUTION_TRACE}),
            host_capability_tags=frozenset({"reference-local"}),
        ),
        ReferenceRuntimeSession(
            session_id="runtime-4",
            event_index=2,
            branch_registry=("main", "review-track"),
            active_track_ref="review-track",
            budget_history=("shell-low", "shell-medium"),
            brake_history=("quiescent", "guarded"),
            last_selected_family=SoftControlFamily.BRANCH,
        ),
    )

    assert state.goal_continuity.active_track_ref == "review-track"
    assert state.goal_continuity.resume_anchor_available is False
    assert state.brake.brake_state is BrakeState.GUARDED
    assert state.brake.dominant_cause_family is SoftControlFamily.BRAKE
    assert state.mode_and_gating.mode_tag == "guarded_review"
    assert state.mode_and_gating.family_mask == frozenset(
        {
            SoftControlFamily.NEUTRAL,
            SoftControlFamily.CHECK,
            SoftControlFamily.BRANCH,
            SoftControlFamily.BRAKE,
            SoftControlFamily.SEEK_CONTEXT,
        }
    )
    assert "environment-drift" in state.uncertainty_monitoring.contradiction_spike_flags
    assert "resume-anchor-missing" in state.uncertainty_monitoring.contradiction_spike_flags
    assert state.control_allocation.host_friction_tags == frozenset(
        {
            "single-process-limit",
            "capability-view-missing",
        }
    )
    assert state.control_allocation.top_family_set == frozenset(
        {
            SoftControlFamily.NEUTRAL,
            SoftControlFamily.BRANCH,
            SoftControlFamily.BRAKE,
            SoftControlFamily.SEEK_CONTEXT,
        }
    )
    assert not state.control_allocation.feedback_pressure_tags


def test_build_reference_executive_state_raises_goal_progress_floor_after_session_rejection() -> None:
    state = build_reference_executive_state(
        observe_reference_host_event("ContextLoad", {"session_id": "runtime-5"}).observation,
        SupportSnapshot(
            trace=SupportTraceState(),
            session=SupportSessionState(branch_registry=("main",)),
            host=SupportHostState(),
            exec_memory_pub=SupportExecMemoryState(),
        ),
        ExecutiveEnvironmentView(
            available_query_kinds=frozenset({CAPABILITY_VIEW, EXECUTION_TRACE}),
            host_capability_tags=frozenset({"reference-local"}),
        ),
        ReferenceRuntimeSession(
            session_id="runtime-5",
            event_index=2,
            active_track_ref="main",
            budget_history=("shell-low", "shell-low"),
            brake_history=("quiescent", "quiescent"),
            last_selected_family=SoftControlFamily.NEUTRAL,
            last_realization_feedback=ReferenceRealizationFeedback(
                selected_family=SoftControlFamily.NEUTRAL,
                realized_family=SoftControlFamily.NEUTRAL,
                brake_state=BrakeState.QUIESCENT,
                warning_codes=("session-rejected:mismatched-session-id:runtime-5-b",),
            ),
            feedback_window=ReferenceRealizationFeedbackWindow(
                entries=(
                    ReferenceRealizationFeedback(
                        selected_family=SoftControlFamily.NEUTRAL,
                        realized_family=SoftControlFamily.NEUTRAL,
                        brake_state=BrakeState.QUIESCENT,
                        warning_codes=("session-rejected:mismatched-session-id:runtime-5-b",),
                    ),
                )
            ),
        ),
    )

    goal_progress = next(
        estimate
        for estimate in state.uncertainty_monitoring.classwise_uncertainty
        if estimate.class_tag == "goal-progress"
    )
    assert goal_progress.level == 0.55
    assert state.brake.brake_state is BrakeState.GUARDED
    assert "prior-session-mismatch" in state.uncertainty_monitoring.contradiction_spike_flags
    assert state.control_allocation.feedback_pressure_tags == frozenset(
        {
            "feedback:degradation-pressure",
            "feedback:rejection-pressure",
        }
    )


def test_build_reference_executive_state_marks_prior_enforcement_override() -> None:
    state = build_reference_executive_state(
        observe_reference_host_event("ContextLoad", {"session_id": "runtime-6"}).observation,
        SupportSnapshot(
            trace=SupportTraceState(),
            session=SupportSessionState(branch_registry=("main",)),
            host=SupportHostState(),
            exec_memory_pub=SupportExecMemoryState(),
        ),
        ExecutiveEnvironmentView(
            available_query_kinds=frozenset({CAPABILITY_VIEW, EXECUTION_TRACE}),
            host_capability_tags=frozenset({"reference-local"}),
        ),
        ReferenceRuntimeSession(
            session_id="runtime-6",
            event_index=2,
            active_track_ref="main",
            budget_history=("shell-low", "shell-low"),
            brake_history=("latched", "latched"),
            last_selected_family=SoftControlFamily.BRANCH,
            last_realization_feedback=ReferenceRealizationFeedback(
                selected_family=SoftControlFamily.BRANCH,
                realized_family=SoftControlFamily.NEUTRAL,
                brake_state=BrakeState.LATCHED,
            ),
            feedback_window=ReferenceRealizationFeedbackWindow(
                entries=(
                    ReferenceRealizationFeedback(
                        selected_family=SoftControlFamily.BRANCH,
                        realized_family=SoftControlFamily.NEUTRAL,
                        brake_state=BrakeState.LATCHED,
                    ),
                )
            ),
        ),
    )

    goal_progress = next(
        estimate
        for estimate in state.uncertainty_monitoring.classwise_uncertainty
        if estimate.class_tag == "goal-progress"
    )
    assert goal_progress.level == 0.45
    assert state.brake.brake_state is BrakeState.GUARDED
    assert (
        "prior-enforcement-override"
        in state.uncertainty_monitoring.contradiction_spike_flags
    )
    assert state.control_allocation.feedback_pressure_tags == frozenset(
        {
            "feedback:degradation-pressure",
            "feedback:latched-history",
            "feedback:override-pressure",
        }
    )


def test_build_reference_executive_state_uses_repeated_rejection_window_pressure() -> None:
    state = build_reference_executive_state(
        observe_reference_host_event("ContextLoad", {"session_id": "runtime-7"}).observation,
        SupportSnapshot(
            trace=SupportTraceState(),
            session=SupportSessionState(branch_registry=("main",)),
            host=SupportHostState(),
            exec_memory_pub=SupportExecMemoryState(),
        ),
        ExecutiveEnvironmentView(
            available_query_kinds=frozenset({CAPABILITY_VIEW, EXECUTION_TRACE}),
            host_capability_tags=frozenset({"reference-local"}),
        ),
        ReferenceRuntimeSession(
            session_id="runtime-7",
            event_index=3,
            active_track_ref="main",
            budget_history=("shell-low", "shell-low", "shell-low"),
            brake_history=("quiescent", "guarded", "guarded"),
            last_selected_family=SoftControlFamily.NEUTRAL,
            last_realization_feedback=ReferenceRealizationFeedback(
                selected_family=SoftControlFamily.NEUTRAL,
                realized_family=SoftControlFamily.NEUTRAL,
                brake_state=BrakeState.QUIESCENT,
                warning_codes=("session-rejected:mismatched-session-id:runtime-7-b",),
            ),
            feedback_window=ReferenceRealizationFeedbackWindow(
                entries=(
                    ReferenceRealizationFeedback(
                        selected_family=SoftControlFamily.NEUTRAL,
                        realized_family=SoftControlFamily.NEUTRAL,
                        brake_state=BrakeState.QUIESCENT,
                        warning_codes=("continuity-rejected:missing-open-track-ref",),
                    ),
                    ReferenceRealizationFeedback(
                        selected_family=SoftControlFamily.NEUTRAL,
                        realized_family=SoftControlFamily.NEUTRAL,
                        brake_state=BrakeState.QUIESCENT,
                        warning_codes=("session-rejected:mismatched-session-id:runtime-7-b",),
                    ),
                )
            ),
        ),
    )

    goal_progress = next(
        estimate
        for estimate in state.uncertainty_monitoring.classwise_uncertainty
        if estimate.class_tag == "goal-progress"
    )
    assert goal_progress.level == 0.70
    assert state.brake.brake_state is BrakeState.LATCHED
    assert "prior-continuity-rejection" in state.uncertainty_monitoring.contradiction_spike_flags
    assert "prior-session-mismatch" in state.uncertainty_monitoring.contradiction_spike_flags
    assert "sustained-feedback-disruption" in state.uncertainty_monitoring.contradiction_spike_flags
    assert state.control_allocation.feedback_pressure_tags == frozenset(
        {
            "feedback:degradation-pressure",
            "feedback:rejection-pressure",
        }
    )


def test_build_reference_executive_state_uses_repeated_override_window_pressure() -> None:
    state = build_reference_executive_state(
        observe_reference_host_event("ContextLoad", {"session_id": "runtime-8"}).observation,
        SupportSnapshot(
            trace=SupportTraceState(),
            session=SupportSessionState(branch_registry=("main",)),
            host=SupportHostState(),
            exec_memory_pub=SupportExecMemoryState(),
        ),
        ExecutiveEnvironmentView(
            available_query_kinds=frozenset({CAPABILITY_VIEW, EXECUTION_TRACE}),
            host_capability_tags=frozenset({"reference-local"}),
        ),
        ReferenceRuntimeSession(
            session_id="runtime-8",
            event_index=3,
            active_track_ref="main",
            budget_history=("shell-low", "shell-low", "shell-low"),
            brake_history=("latched", "latched", "latched"),
            last_selected_family=SoftControlFamily.BRANCH,
            last_realization_feedback=ReferenceRealizationFeedback(
                selected_family=SoftControlFamily.ESCALATE,
                realized_family=SoftControlFamily.NEUTRAL,
                brake_state=BrakeState.LATCHED,
            ),
            feedback_window=ReferenceRealizationFeedbackWindow(
                entries=(
                    ReferenceRealizationFeedback(
                        selected_family=SoftControlFamily.BRANCH,
                        realized_family=SoftControlFamily.CHECK,
                        brake_state=BrakeState.LATCHED,
                    ),
                    ReferenceRealizationFeedback(
                        selected_family=SoftControlFamily.ESCALATE,
                        realized_family=SoftControlFamily.NEUTRAL,
                        brake_state=BrakeState.LATCHED,
                    ),
                )
            ),
        ),
    )

    goal_progress = next(
        estimate
        for estimate in state.uncertainty_monitoring.classwise_uncertainty
        if estimate.class_tag == "goal-progress"
    )
    assert goal_progress.level == 0.60
    assert state.brake.brake_state is BrakeState.LATCHED
    assert "prior-enforcement-override" in state.uncertainty_monitoring.contradiction_spike_flags
    assert "sustained-latched-brake" in state.uncertainty_monitoring.contradiction_spike_flags
    assert state.control_allocation.feedback_pressure_tags == frozenset(
        {
            "feedback:degradation-pressure",
            "feedback:latched-history",
            "feedback:override-pressure",
        }
    )


def test_build_reference_executive_state_clean_window_does_not_raise_pressure() -> None:
    state = build_reference_executive_state(
        observe_reference_host_event("ContextLoad", {"session_id": "runtime-9"}).observation,
        SupportSnapshot(
            trace=SupportTraceState(),
            session=SupportSessionState(branch_registry=("main",)),
            host=SupportHostState(),
            exec_memory_pub=SupportExecMemoryState(),
        ),
        ExecutiveEnvironmentView(
            available_query_kinds=frozenset({CAPABILITY_VIEW, EXECUTION_TRACE}),
            host_capability_tags=frozenset({"reference-local"}),
        ),
        ReferenceRuntimeSession(
            session_id="runtime-9",
            event_index=4,
            active_track_ref="main",
            budget_history=("shell-low", "shell-low", "shell-low", "shell-low"),
            brake_history=("quiescent", "quiescent", "quiescent", "quiescent"),
            last_selected_family=SoftControlFamily.NEUTRAL,
            last_realization_feedback=ReferenceRealizationFeedback(
                selected_family=SoftControlFamily.NEUTRAL,
                realized_family=SoftControlFamily.NEUTRAL,
                brake_state=BrakeState.QUIESCENT,
            ),
            feedback_window=ReferenceRealizationFeedbackWindow(
                entries=(
                    ReferenceRealizationFeedback(
                        selected_family=SoftControlFamily.NEUTRAL,
                        realized_family=SoftControlFamily.NEUTRAL,
                        brake_state=BrakeState.QUIESCENT,
                    ),
                    ReferenceRealizationFeedback(
                        selected_family=SoftControlFamily.NEUTRAL,
                        realized_family=SoftControlFamily.NEUTRAL,
                        brake_state=BrakeState.QUIESCENT,
                    ),
                    ReferenceRealizationFeedback(
                        selected_family=SoftControlFamily.NEUTRAL,
                        realized_family=SoftControlFamily.NEUTRAL,
                        brake_state=BrakeState.QUIESCENT,
                    ),
                )
            ),
        ),
    )

    goal_progress = next(
        estimate
        for estimate in state.uncertainty_monitoring.classwise_uncertainty
        if estimate.class_tag == "goal-progress"
    )
    assert goal_progress.level == 0.2
    assert state.brake.brake_state is BrakeState.QUIESCENT
    assert not state.uncertainty_monitoring.contradiction_spike_flags
    assert not state.control_allocation.feedback_pressure_tags
