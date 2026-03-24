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


def _selection(selected_family: SoftControlFamily) -> object:
    class _Selection:
        def __init__(self, family: SoftControlFamily) -> None:
            self.selected_family = family

    return _Selection(selected_family)


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
