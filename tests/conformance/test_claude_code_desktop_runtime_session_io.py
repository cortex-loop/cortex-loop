"""Conformance tests for Claude Code Desktop runtime session wiring."""

from __future__ import annotations

from cortex.hosts.claude.runtime import ClaudeRuntimeSession
from cortex.hosts.claude_code_desktop.ingress import (
    parse_claude_code_desktop_hook_event,
)
from cortex.hosts.claude_code_desktop.runtime import (
    ClaudeCodeDesktopRuntimeSession,
    run_claude_code_desktop_runtime_step,
)
from cortex.sre.brake import BrakeState
from cortex.sre.families import SoftControlFamily
from cortex.sre.feedback import ReferenceRealizationFeedback, ReferenceRealizationFeedbackWindow
from cortex.sre.operator_routing import OperatorTaskMode


def test_claude_code_desktop_session_roundtrips_through_existing_claude_runtime_shape() -> None:
    feedback = _noisy_feedback()
    session = ClaudeCodeDesktopRuntimeSession(
        session_id="ccdt-session",
        event_index=4,
        branch_registry=("main", "feature-x"),
        active_track_ref="feature-x",
        pending_goal_refs=("goal-a",),
        continuity_reminders=("resume track feature-x",),
        budget_history=("shell-low",),
        brake_history=("guarded",),
        brake_tonic_history=(0.2, 0.3),
        last_selected_family=SoftControlFamily.CHECK,
        last_commitment_result_summary="candidate-only",
        last_realization_feedback=feedback,
        feedback_window=ReferenceRealizationFeedbackWindow(entries=(feedback,)),
    )

    claude_session = session.to_claude_session()
    restored = ClaudeCodeDesktopRuntimeSession.from_claude_session(claude_session)

    assert isinstance(claude_session, ClaudeRuntimeSession)
    assert restored == session
    assert restored.as_summary()["session_id"] == "ccdt-session"
    assert restored.feedback_window.entries[-1] == feedback


def test_claude_code_desktop_session_constructor_normalizes_one_sided_feedback_window() -> None:
    feedback = _noisy_feedback()

    session = ClaudeCodeDesktopRuntimeSession(
        last_realization_feedback=feedback,
    )

    assert session.feedback_window.entries == (feedback,)


def test_unwired_hook_event_does_not_mutate_session() -> None:
    event = parse_claude_code_desktop_hook_event(
        {
            "hook_event_name": "SessionStart",
            "session_id": "ccdt-session",
            "cwd": "/tmp/project",
        }
    )
    session = ClaudeCodeDesktopRuntimeSession(session_id="ccdt-session")

    result = run_claude_code_desktop_runtime_step(event, session)

    assert result.session == session
    assert result.claude_runtime_result is None
    assert result.directive.additional_context is None
    assert result.directive.permission_decision is None


def _noisy_feedback() -> ReferenceRealizationFeedback:
    return ReferenceRealizationFeedback(
        selected_family=SoftControlFamily.CHECK,
        realized_family=SoftControlFamily.CHECK,
        brake_state=BrakeState.GUARDED,
        task_mode=OperatorTaskMode.INSPECT,
        evidence_progress_class="token-stream",
        continuity_progress_class="none",
        host_friction_tags=("capability-view-missing",),
    )
