"""Unit tests for the first reference-host runtime step kernel."""

import pytest

import cortex.runtime.reference as reference_runtime
from cortex.core.dispatch import DispatchLane
from cortex.runtime.reference import (
    ReferenceRuntimeSession,
    run_reference_runtime_step,
)
from cortex.sre.brake import BrakeState
from cortex.sre.feedback import ReferenceRealizationFeedback
from cortex.sre.families import SoftControlFamily
from cortex.sre.state import (
    ReferenceBrakeView,
    ReferenceControlAllocationView,
    ReferenceExecutiveState,
    ReferenceGoalContinuityView,
    ReferenceModeAndGatingView,
    ReferenceUncertaintyMonitoringView,
)
from cortex.sre.uncertainty import UncertaintyEstimate


def test_reference_runtime_session_tracks_minimum_live_state() -> None:
    session = ReferenceRuntimeSession(session_id="session-1")

    assert session.session_id == "session-1"
    assert session.event_index == 0
    assert session.branch_registry == ("main",)
    assert session.active_track_ref == "main"
    assert session.pending_goal_refs == ()
    assert session.budget_history == ()
    assert session.brake_history == ()
    assert session.last_selected_family is None
    assert session.last_commitment_result_summary is None
    assert session.last_realization_feedback is None
    assert session.feedback_window.entries == ()
    assert session.as_summary()["branch_registry"] == ["main"]
    assert session.as_summary()["active_track_ref"] == "main"


def test_reference_runtime_step_result_surfaces_cheap_reference_event_without_commitment_kind() -> None:
    result = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-1"},
    )

    assert result.event_index == 1
    assert result.bound_event.observation.event.native_event_name == "context/load"
    assert result.dispatch_decision.lane is DispatchLane.CHEAP
    assert result.selected_family is SoftControlFamily.NEUTRAL
    assert result.realized_family is SoftControlFamily.NEUTRAL
    assert result.brake_state is BrakeState.QUIESCENT
    assert result.executive_state_summary["mode_tag"] == "pass_through"
    assert result.executive_state_summary["budget_band"] == "low"
    assert result.control_ledger_summary == {
        "event_class": "cheap",
        "admissible_families": ["neutral", "check"],
        "selected_family": "neutral",
        "realized_family": "neutral",
        "dominant_uncertainty_sources": ["environment", "goal-progress"],
        "brake_state": "quiescent",
        "budget_band": "low",
        "primary_reason": None,
    }
    assert result.feedback_window_summary_payload == {
        "window_size": 0,
        "rejection_count": 0,
        "override_count": 0,
        "latched_count": 0,
        "clean_success_streak": 0,
        "goal_progress_floor": 0.0,
        "degradation_pressure_bonus": 0,
        "sustained_spike_flags": [],
    }
    assert result.commitment_result_kind is None
    assert result.session.session_id == "session-1"
    assert result.session.active_track_ref == "main"
    assert result.session.budget_history == ("shell-low",)
    assert result.session.brake_history == ("quiescent",)
    assert result.session.last_selected_family is SoftControlFamily.NEUTRAL
    assert result.session.last_commitment_result_summary is None
    assert isinstance(result.session.last_realization_feedback, ReferenceRealizationFeedback)
    assert result.session.last_realization_feedback.as_summary() == {
        "selected_family": "neutral",
        "realized_family": "neutral",
        "brake_state": "quiescent",
        "commitment_result_kind": None,
        "warning_codes": [],
        "host_friction_tags": [],
    }
    assert result.session.feedback_window.entries == (result.session.last_realization_feedback,)
    assert result.session_summary["feedback_window_size"] == 1


def test_reference_runtime_step_result_keeps_candidate_bearing_event_candidate_only() -> None:
    first = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-2"},
    )
    second = run_reference_runtime_step(
        "ApprovalRequest",
        {
            "session_id": "session-2",
            "candidate_id": "candidate-1",
        },
        first.session,
    )

    assert second.event_index == 2
    assert second.dispatch_decision.lane is DispatchLane.CANDIDATE_BEARING
    assert second.commitment_result_kind is None
    assert second.realized_family is SoftControlFamily.NEUTRAL
    assert second.session.session_id == "session-2"
    assert second.session.active_track_ref == "main"
    assert second.session.budget_history == ("shell-low", "shell-medium")
    assert second.session.brake_history == ("quiescent", "quiescent")
    assert second.executive_state_summary["mode_tag"] == "review_pending"
    assert second.executive_state_summary["budget_band"] == "medium"
    assert second.control_ledger_summary["event_class"] == "candidate-bearing"
    assert second.control_ledger_summary["admissible_families"] == ["neutral", "check"]
    assert second.control_ledger_summary["dominant_uncertainty_sources"] == [
        "evidence",
        "environment",
    ]
    assert second.session.last_commitment_result_summary == "candidate-only"
    assert second.session.last_realization_feedback is not None
    assert second.session.last_realization_feedback.commitment_result_kind is None
    assert second.session.feedback_window.entries[-1] == second.session.last_realization_feedback
    assert second.session_summary["event_index"] == 2


def test_reference_runtime_step_result_certifies_full_commitment_when_runtime_payload_supplies_artifact_ref() -> None:
    result = run_reference_runtime_step(
        "ApprovalResult",
        {
            "session_id": "session-3",
            "commitment_id": "commit-1",
            "externally_consequential": True,
            "result_artifact_ref": "artifact-1",
        },
    )

    assert result.event_index == 1
    assert result.dispatch_decision.lane is DispatchLane.FULL_COMMITMENT
    assert result.commitment_result_kind == "certified"
    assert result.selected_family is SoftControlFamily.NEUTRAL
    assert result.realized_family is SoftControlFamily.NEUTRAL
    assert result.brake_state is BrakeState.QUIESCENT
    assert result.executive_state_summary["mode_tag"] == "commitment_path"
    assert result.executive_state_summary["budget_band"] == "high"
    assert result.control_ledger_summary == {
        "event_class": "full-commitment",
        "admissible_families": ["neutral", "check"],
        "selected_family": "neutral",
        "realized_family": "neutral",
        "dominant_uncertainty_sources": ["evidence", "environment"],
        "brake_state": "quiescent",
        "budget_band": "high",
        "primary_reason": None,
    }
    assert result.session.active_track_ref == "main"
    assert result.session.budget_history == ("shell-high",)
    assert result.session.last_commitment_result_summary == "certified"
    assert result.session.last_realization_feedback is not None
    assert result.session.last_realization_feedback.commitment_result_kind == "certified"
    assert result.session.feedback_window.entries[-1] == result.session.last_realization_feedback


def test_reference_runtime_step_rejects_malformed_open_without_mutating_existing_anchor() -> None:
    opened = run_reference_runtime_step(
        "ContextLoad",
        {
            "session_id": "session-open-1",
            "branch_operation": "open",
            "branch_track_ref": "branch-alpha",
        },
    )
    suspended = run_reference_runtime_step(
        "ApprovalRequest",
        {
            "session_id": "session-open-1",
            "branch_operation": "suspend",
            "branch_track_ref": "branch-alpha",
            "candidate_id": "candidate-1",
        },
        opened.session,
    )
    malformed_open = run_reference_runtime_step(
        "ContextLoad",
        {
            "session_id": "session-open-1",
            "branch_operation": "open",
        },
        suspended.session,
    )

    assert malformed_open.warnings == ("continuity-rejected:missing-open-track-ref",)
    assert malformed_open.session.branch_registry == ("main", "branch-alpha")
    assert malformed_open.session.active_track_ref == "main"
    assert malformed_open.session.pending_goal_refs == ("branch-alpha",)
    assert malformed_open.executive_state_summary["pending_goal_refs"] == ["branch-alpha"]


def test_reference_runtime_step_rejects_mismatched_session_id_without_reassigning_shell() -> None:
    first = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-stable-a"},
    )
    second = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-stable-b"},
        first.session,
    )

    assert second.warnings == ("session-rejected:mismatched-session-id:session-stable-b",)
    assert second.session.session_id == "session-stable-a"
    assert second.session_summary["session_id"] == "session-stable-a"


def test_reference_runtime_step_propagates_session_rejection_feedback_into_next_event_pressure() -> None:
    first = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-feedback-a"},
    )
    rejected = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-feedback-b"},
        first.session,
    )
    follow_up = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-feedback-a"},
        rejected.session,
    )

    assert rejected.session.last_realization_feedback is not None
    assert rejected.session.last_realization_feedback.warning_codes == (
        "session-rejected:mismatched-session-id:session-feedback-b",
    )
    assert _goal_progress_level(follow_up) == 0.55
    assert (
        "prior-session-mismatch"
        in follow_up.executive_state.uncertainty_monitoring.contradiction_spike_flags
    )
    assert follow_up.brake_state is BrakeState.GUARDED


def test_reference_runtime_step_propagates_prior_enforcement_override_into_next_event_pressure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_builder = reference_runtime.build_reference_executive_state
    original_select = reference_runtime.select_reference_soft_control

    monkeypatch.setattr(
        reference_runtime,
        "build_reference_executive_state",
        _latched_state_with_evidence,
    )
    monkeypatch.setattr(
        reference_runtime,
        "select_reference_soft_control",
        lambda executive_state: _selection(SoftControlFamily.BRANCH),
    )
    enforced = run_reference_runtime_step(
        "ApprovalResult",
        {
            "session_id": "session-feedback-latched",
            "commitment_id": "commit-feedback-latched",
            "externally_consequential": True,
            "result_artifact_ref": "artifact-feedback-latched",
        },
    )

    monkeypatch.setattr(
        reference_runtime,
        "build_reference_executive_state",
        original_builder,
    )
    monkeypatch.setattr(
        reference_runtime,
        "select_reference_soft_control",
        original_select,
    )
    follow_up = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-feedback-latched"},
        enforced.session,
    )

    assert enforced.session.last_realization_feedback is not None
    assert enforced.session.last_realization_feedback.selected_family is SoftControlFamily.BRANCH
    assert enforced.session.last_realization_feedback.realized_family is SoftControlFamily.CHECK
    assert _goal_progress_level(follow_up) == 0.45
    assert (
        "prior-enforcement-override"
        in follow_up.executive_state.uncertainty_monitoring.contradiction_spike_flags
    )
    assert follow_up.brake_state is BrakeState.GUARDED


def test_reference_runtime_step_does_not_raise_feedback_pressure_after_clean_success() -> None:
    first = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-feedback-clean"},
    )
    second = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-feedback-clean"},
        first.session,
    )

    assert _goal_progress_level(second) == 0.2
    assert not second.executive_state.uncertainty_monitoring.contradiction_spike_flags
    assert second.brake_state is BrakeState.QUIESCENT


def test_reference_runtime_step_appends_feedback_window_and_truncates_oldest_entry() -> None:
    session = ReferenceRuntimeSession(
        session_id="session-feedback-window",
        event_index=3,
        budget_history=("shell-low", "shell-low", "shell-low"),
        brake_history=("quiescent", "quiescent", "quiescent"),
        last_selected_family=SoftControlFamily.NEUTRAL,
        last_realization_feedback=_feedback("warn-3"),
        feedback_window=reference_runtime.ReferenceRealizationFeedbackWindow(
            entries=(
                _feedback("warn-1"),
                _feedback("warn-2"),
                _feedback("warn-3"),
            )
        ),
    )

    result = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-feedback-window"},
        session,
    )

    assert result.session.feedback_window.entries[0].warning_codes == ("warn-2",)
    assert result.session.feedback_window.entries[1].warning_codes == ("warn-3",)
    assert result.session.feedback_window.entries[2].warning_codes == ()
    assert result.session.feedback_window.entries[-1] == result.session.last_realization_feedback


def test_reference_runtime_step_reports_prior_window_summary_for_single_rejection_sequence() -> None:
    first = run_reference_runtime_step("ContextLoad", {"session_id": "session-a"})
    second = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-b"},
        first.session,
    )
    third = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-a"},
        second.session,
    )

    assert third.feedback_window_summary_payload == {
        "window_size": 2,
        "rejection_count": 1,
        "override_count": 0,
        "latched_count": 0,
        "clean_success_streak": 0,
        "goal_progress_floor": 0.55,
        "degradation_pressure_bonus": 1,
        "sustained_spike_flags": ["prior-session-mismatch"],
    }
    assert third.session_summary["feedback_window_size"] == 3


def test_reference_runtime_step_reports_prior_window_summary_for_repeated_rejection_sequence() -> None:
    first = run_reference_runtime_step("ContextLoad", {"session_id": "session-a"})
    second = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-b"},
        first.session,
    )
    third = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-a"},
        second.session,
    )
    fourth = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-b"},
        third.session,
    )
    fifth = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-a"},
        fourth.session,
    )

    assert fifth.feedback_window_summary_payload == {
        "window_size": 3,
        "rejection_count": 2,
        "override_count": 0,
        "latched_count": 0,
        "clean_success_streak": 0,
        "goal_progress_floor": 0.70,
        "degradation_pressure_bonus": 2,
        "sustained_spike_flags": [
            "prior-session-mismatch",
            "sustained-feedback-disruption",
        ],
    }
    assert fifth.session_summary["feedback_window_size"] == 3


def test_reference_runtime_step_orders_admissible_families_by_soft_control_enum(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        reference_runtime,
        "build_reference_executive_state",
        _state_with_ordered_family_mask,
    )
    monkeypatch.setattr(
        reference_runtime,
        "select_reference_soft_control",
        lambda executive_state: _selection(SoftControlFamily.NEUTRAL),
    )

    result = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-admissible-order"},
    )

    assert result.control_ledger_summary["admissible_families"] == [
        "neutral",
        "redirect",
        "check",
        "branch",
        "escalate",
    ]


def test_reference_runtime_step_orders_dominant_uncertainty_sources_by_level_then_tag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        reference_runtime,
        "build_reference_executive_state",
        _state_with_tied_uncertainty_sources,
    )
    monkeypatch.setattr(
        reference_runtime,
        "select_reference_soft_control",
        lambda executive_state: _selection(SoftControlFamily.NEUTRAL),
    )

    result = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-uncertainty-order"},
    )

    assert result.control_ledger_summary["dominant_uncertainty_sources"] == [
        "environment",
        "evidence",
    ]


def test_reference_runtime_step_prioritizes_enforcement_as_primary_reason_over_session_warning(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        reference_runtime,
        "build_reference_executive_state",
        _latched_state_with_evidence,
    )
    monkeypatch.setattr(
        reference_runtime,
        "select_reference_soft_control",
        lambda executive_state: _selection(SoftControlFamily.BRANCH),
    )

    result = run_reference_runtime_step(
        "ApprovalResult",
        {
            "session_id": "session-priority-b",
            "commitment_id": "commit-priority",
            "externally_consequential": True,
            "result_artifact_ref": "artifact-priority",
        },
        ReferenceRuntimeSession(session_id="session-priority-a"),
    )

    assert result.warnings == (
        "session-rejected:mismatched-session-id:session-priority-b",
        "latched-brake-enforced:branch:check",
    )
    assert result.control_ledger_summary["primary_reason"] == (
        "latched-brake-enforced:branch:check"
    )
    assert result.commitment_result_kind == "certified"


def test_reference_runtime_step_enforces_latched_brake_to_check_when_evidence_dominates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(reference_runtime, "build_reference_executive_state", _latched_state_with_evidence)
    monkeypatch.setattr(
        reference_runtime,
        "select_reference_soft_control",
        lambda executive_state: _selection(SoftControlFamily.BRANCH),
    )

    result = run_reference_runtime_step(
        "ApprovalResult",
        {
            "session_id": "session-latched-check",
            "commitment_id": "commit-latched-check",
            "externally_consequential": True,
            "result_artifact_ref": "artifact-latched-check",
        },
    )

    assert result.selected_family is SoftControlFamily.BRANCH
    assert result.realized_family is SoftControlFamily.CHECK
    assert result.warnings == ("latched-brake-enforced:branch:check",)
    assert result.control_ledger_summary["selected_family"] == "branch"
    assert result.control_ledger_summary["realized_family"] == "check"
    assert result.control_ledger_summary["primary_reason"] == "latched-brake-enforced:branch:check"
    assert result.commitment_result_kind == "certified"
    assert result.session.last_realization_feedback is not None
    assert result.session.last_realization_feedback.realized_family is SoftControlFamily.CHECK


def test_reference_runtime_step_enforces_latched_brake_to_neutral_without_evidence_or_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(reference_runtime, "build_reference_executive_state", _latched_state_without_evidence)
    monkeypatch.setattr(
        reference_runtime,
        "select_reference_soft_control",
        lambda executive_state: _selection(SoftControlFamily.ESCALATE),
    )

    result = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-latched-neutral"},
    )

    assert result.selected_family is SoftControlFamily.ESCALATE
    assert result.realized_family is SoftControlFamily.NEUTRAL
    assert result.warnings == ("latched-brake-enforced:escalate:neutral",)
    assert result.control_ledger_summary["selected_family"] == "escalate"
    assert result.control_ledger_summary["realized_family"] == "neutral"
    assert result.control_ledger_summary["primary_reason"] == "latched-brake-enforced:escalate:neutral"
    assert result.session.last_realization_feedback is not None
    assert result.session.last_realization_feedback.realized_family is SoftControlFamily.NEUTRAL


def _goal_progress_level(result: object) -> float:
    executive_state = result.executive_state
    for estimate in executive_state.uncertainty_monitoring.classwise_uncertainty:
        if estimate.class_tag == "goal-progress":
            return estimate.level
    raise AssertionError("missing goal-progress uncertainty estimate")


def _selection(selected_family: SoftControlFamily) -> object:
    class _Selection:
        def __init__(self, family: SoftControlFamily) -> None:
            self.selected_family = family

    return _Selection(selected_family)


def _feedback(warning_code: str) -> ReferenceRealizationFeedback:
    warning_codes = (warning_code,) if warning_code else ()
    return ReferenceRealizationFeedback(
        selected_family=SoftControlFamily.NEUTRAL,
        realized_family=SoftControlFamily.NEUTRAL,
        brake_state=BrakeState.QUIESCENT,
        warning_codes=warning_codes,
    )


def _latched_state_with_evidence(*args: object, **kwargs: object) -> ReferenceExecutiveState:
    return ReferenceExecutiveState(
        goal_continuity=ReferenceGoalContinuityView(active_track_ref="review-track"),
        uncertainty_monitoring=ReferenceUncertaintyMonitoringView(
            classwise_uncertainty=(
                UncertaintyEstimate(class_tag="evidence", level=0.95),
                UncertaintyEstimate(class_tag="environment", level=0.75),
                UncertaintyEstimate(class_tag="host-capability", level=0.2),
                UncertaintyEstimate(class_tag="goal-progress", level=0.4),
            )
        ),
        mode_and_gating=ReferenceModeAndGatingView(
            mode_tag="latched_review",
            family_mask=frozenset(
                {
                    SoftControlFamily.NEUTRAL,
                    SoftControlFamily.CHECK,
                    SoftControlFamily.BRANCH,
                    SoftControlFamily.BRAKE,
                }
            ),
        ),
        control_allocation=ReferenceControlAllocationView(
            budget_band="high",
            top_family_set=frozenset(
                {
                    SoftControlFamily.NEUTRAL,
                    SoftControlFamily.BRANCH,
                    SoftControlFamily.BRAKE,
                }
            ),
        ),
        brake=ReferenceBrakeView(brake_state=BrakeState.LATCHED),
    )


def _latched_state_without_evidence(*args: object, **kwargs: object) -> ReferenceExecutiveState:
    return ReferenceExecutiveState(
        goal_continuity=ReferenceGoalContinuityView(active_track_ref="main"),
        uncertainty_monitoring=ReferenceUncertaintyMonitoringView(
            classwise_uncertainty=(
                UncertaintyEstimate(class_tag="host-capability", level=0.9),
                UncertaintyEstimate(class_tag="goal-progress", level=0.8),
                UncertaintyEstimate(class_tag="environment", level=0.2),
                UncertaintyEstimate(class_tag="evidence", level=0.1),
            )
        ),
        mode_and_gating=ReferenceModeAndGatingView(
            mode_tag="latched_review",
            family_mask=frozenset(
                {
                    SoftControlFamily.NEUTRAL,
                    SoftControlFamily.CHECK,
                    SoftControlFamily.ESCALATE,
                    SoftControlFamily.BRAKE,
                }
            ),
        ),
        control_allocation=ReferenceControlAllocationView(
            budget_band="medium",
            top_family_set=frozenset(
                {
                    SoftControlFamily.NEUTRAL,
                    SoftControlFamily.ESCALATE,
                    SoftControlFamily.BRAKE,
                }
            ),
            host_friction_tags=frozenset({"single-process-limit"}),
        ),
        brake=ReferenceBrakeView(brake_state=BrakeState.LATCHED),
    )


def _state_with_ordered_family_mask(*args: object, **kwargs: object) -> ReferenceExecutiveState:
    return ReferenceExecutiveState(
        goal_continuity=ReferenceGoalContinuityView(active_track_ref="main"),
        uncertainty_monitoring=ReferenceUncertaintyMonitoringView(
            classwise_uncertainty=(
                UncertaintyEstimate(class_tag="environment", level=0.6),
                UncertaintyEstimate(class_tag="goal-progress", level=0.4),
            )
        ),
        mode_and_gating=ReferenceModeAndGatingView(
            mode_tag="ordered_mask",
            family_mask=frozenset(
                {
                    SoftControlFamily.ESCALATE,
                    SoftControlFamily.BRANCH,
                    SoftControlFamily.CHECK,
                    SoftControlFamily.REDIRECT,
                }
            ),
        ),
        control_allocation=ReferenceControlAllocationView(
            budget_band="medium",
            top_family_set=frozenset({SoftControlFamily.NEUTRAL}),
        ),
        brake=ReferenceBrakeView(brake_state=BrakeState.QUIESCENT),
    )


def _state_with_tied_uncertainty_sources(
    *args: object,
    **kwargs: object,
) -> ReferenceExecutiveState:
    return ReferenceExecutiveState(
        goal_continuity=ReferenceGoalContinuityView(active_track_ref="main"),
        uncertainty_monitoring=ReferenceUncertaintyMonitoringView(
            classwise_uncertainty=(
                UncertaintyEstimate(class_tag="goal-progress", level=0.8),
                UncertaintyEstimate(class_tag="environment", level=0.8),
                UncertaintyEstimate(class_tag="evidence", level=0.8),
                UncertaintyEstimate(class_tag="host-capability", level=0.2),
            )
        ),
        mode_and_gating=ReferenceModeAndGatingView(
            mode_tag="tied_sources",
            family_mask=frozenset(
                {
                    SoftControlFamily.NEUTRAL,
                    SoftControlFamily.CHECK,
                }
            ),
        ),
        control_allocation=ReferenceControlAllocationView(
            budget_band="medium",
            top_family_set=frozenset({SoftControlFamily.NEUTRAL}),
        ),
        brake=ReferenceBrakeView(brake_state=BrakeState.QUIESCENT),
    )
