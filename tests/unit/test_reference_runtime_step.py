"""Unit tests for the first reference-host runtime step kernel."""

from cortex.core.dispatch import DispatchLane
from cortex.runtime.reference import (
    ReferenceRuntimeSession,
    run_reference_runtime_step,
)
from cortex.sre.brake import BrakeState
from cortex.sre.families import SoftControlFamily


def test_reference_runtime_session_tracks_minimum_live_state() -> None:
    session = ReferenceRuntimeSession(session_id="session-1")

    assert session.session_id == "session-1"
    assert session.event_index == 0
    assert session.branch_registry == ("main",)
    assert session.pending_goal_refs == ()
    assert session.budget_history == ()
    assert session.brake_history == ()
    assert session.last_selected_family is None
    assert session.last_commitment_result_summary is None
    assert session.as_summary()["branch_registry"] == ["main"]


def test_reference_runtime_step_result_surfaces_cheap_reference_event_without_commitment_kind() -> None:
    result = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "session-1"},
    )

    assert result.event_index == 1
    assert result.bound_event.observation.event.native_event_name == "context/load"
    assert result.dispatch_decision.lane is DispatchLane.CHEAP
    assert result.selected_family is SoftControlFamily.NEUTRAL
    assert result.brake_state is BrakeState.QUIESCENT
    assert result.commitment_result_kind is None
    assert result.session.session_id == "session-1"
    assert result.session.budget_history == ("shell-low",)
    assert result.session.brake_history == ("quiescent",)
    assert result.session.last_selected_family is SoftControlFamily.NEUTRAL
    assert result.session.last_commitment_result_summary is None


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
    assert second.session.session_id == "session-2"
    assert second.session.budget_history == ("shell-low", "shell-medium")
    assert second.session.brake_history == ("quiescent", "quiescent")
    assert second.session.last_commitment_result_summary == "candidate-only"
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
    assert result.brake_state is BrakeState.QUIESCENT
    assert result.session.budget_history == ("shell-high",)
    assert result.session.last_commitment_result_summary == "certified"
