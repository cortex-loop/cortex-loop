"""Conformance tests for Claude Code Desktop hook-control output."""

from __future__ import annotations

import json

from cortex.hosts.claude_code_desktop.hook_control import (
    build_claude_code_desktop_hook_output,
)
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


def test_pretool_bash_clean_state_emits_no_additional_context() -> None:
    event = _pretool_event("echo ACKNOWLEDGED")

    result = run_claude_code_desktop_runtime_step(
        event,
        ClaudeCodeDesktopRuntimeSession(session_id="ccdt-clean"),
    )
    payload = build_claude_code_desktop_hook_output(result.directive)

    assert result.session.event_index == 1
    assert result.claude_runtime_result is not None
    assert payload == {"continue": True, "suppressOutput": True}


def test_pretool_bash_noisy_prior_feedback_emits_bounded_runtime_context() -> None:
    feedback = ReferenceRealizationFeedback(
        selected_family=SoftControlFamily.CHECK,
        realized_family=SoftControlFamily.CHECK,
        brake_state=BrakeState.GUARDED,
        evidence_progress_class="token-stream",
        continuity_progress_class="none",
        host_friction_tags=("capability-view-missing",),
    )
    session = ClaudeCodeDesktopRuntimeSession(
        session_id="ccdt-noisy",
        last_realization_feedback=feedback,
        feedback_window=ReferenceRealizationFeedbackWindow(entries=(feedback,)),
    )

    result = run_claude_code_desktop_runtime_step(
        _pretool_event("python3 -m pytest tests/conformance -q"),
        session,
    )
    payload = build_claude_code_desktop_hook_output(result.directive)

    hook_output = payload["hookSpecificOutput"]
    assert hook_output["hookEventName"] == "PreToolUse"
    assert hook_output["permissionDecision"] == "allow"
    assert hook_output["permissionDecisionReason"] == (
        "Cortex runtime context from prior realization feedback."
    )
    assert hook_output["additionalContext"] == (
        "Completion is not supported by the evidence yet. An artifact, a "
        "check, or a narrower claim is still needed before closure holds."
    )
    assert "CORTEX_RUNTIME_CONTEXT_V1" not in hook_output["additionalContext"]
    assert "capability-view-missing" not in hook_output["additionalContext"]
    assert "acknowledge" not in hook_output["additionalContext"].lower()
    assert json.dumps(payload)


def test_unsupported_hook_event_returns_noop_without_crashing() -> None:
    event = parse_claude_code_desktop_hook_event(
        {
            "hook_event_name": "PostToolUse",
            "session_id": "ccdt-posttool",
            "tool_name": "Bash",
            "tool_input": {"command": "echo done"},
            "tool_response": {"stdout": "done\n"},
        }
    )

    result = run_claude_code_desktop_runtime_step(event)
    payload = build_claude_code_desktop_hook_output(result.directive)

    assert result.session.event_index == 0
    assert result.claude_runtime_result is None
    assert payload == {"continue": True, "suppressOutput": True}


def test_pretool_bash_observe_mode_updates_state_but_emits_no_hook_context() -> None:
    feedback = ReferenceRealizationFeedback(
        selected_family=SoftControlFamily.CHECK,
        realized_family=SoftControlFamily.CHECK,
        brake_state=BrakeState.GUARDED,
        evidence_progress_class="token-stream",
        continuity_progress_class="none",
    )
    session = ClaudeCodeDesktopRuntimeSession(
        last_realization_feedback=feedback,
        feedback_window=ReferenceRealizationFeedbackWindow(entries=(feedback,)),
    )

    result = run_claude_code_desktop_runtime_step(
        _pretool_event("echo inspect"),
        session,
        mode="observe",
    )
    payload = build_claude_code_desktop_hook_output(result.directive)

    assert result.session.event_index == 1
    assert payload == {"continue": True, "suppressOutput": True}


def _pretool_event(command: str):
    return parse_claude_code_desktop_hook_event(
        {
            "hook_event_name": "PreToolUse",
            "session_id": "ccdt-session",
            "transcript_path": "/tmp/transcript.jsonl",
            "cwd": "/tmp/project",
            "permission_mode": "bypassPermissions",
            "tool_name": "Bash",
            "tool_input": {"command": command, "description": "test command"},
            "tool_use_id": "toolu_test",
        }
    )
