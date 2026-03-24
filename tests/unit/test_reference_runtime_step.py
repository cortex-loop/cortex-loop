"""Unit tests for the first reference-host runtime step kernel."""

from cortex.core.dispatch import DispatchLane
from cortex.runtime.reference import (
    ReferenceRuntimeSession,
    run_reference_runtime_step,
)
from cortex.sre.brake import BrakeState
from cortex.sre.feedback import ReferenceRealizationFeedback
from cortex.sre.families import SoftControlFamily


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
