"""Unit tests for bounded Claude runtime session artifact I/O."""

from __future__ import annotations

import json

import pytest

from cortex.hosts.claude.runtime import ClaudeRuntimeSession
from cortex.hosts.claude.session_io import (
    build_claude_runtime_session_artifact,
    parse_claude_runtime_session_artifact,
    read_claude_runtime_session_artifact,
    write_claude_runtime_session_artifact,
)
from cortex.sre.brake import BrakeState
from cortex.sre.feedback import ReferenceRealizationFeedback, ReferenceRealizationFeedbackWindow
from cortex.sre.families import SoftControlFamily


def test_claude_runtime_session_artifact_roundtrips_bounded_residue() -> None:
    session = ClaudeRuntimeSession(
        session_id="cl-session",
        event_index=3,
        branch_registry=("main", "branch-alpha"),
        active_track_ref="branch-alpha",
        pending_goal_refs=("goal-extra",),
        budget_history=("shell-low", "shell-medium"),
        brake_history=("quiescent", "guarded"),
        last_selected_family=SoftControlFamily.CHECK,
        last_commitment_result_summary="candidate-only",
        last_realization_feedback=_feedback("warn-current"),
        feedback_window=ReferenceRealizationFeedbackWindow(
            entries=(_feedback("warn-old"), _feedback("warn-current"))
        ),
    )

    artifact = build_claude_runtime_session_artifact(session)
    payload = artifact.as_payload()
    restored = parse_claude_runtime_session_artifact(payload)

    assert payload["artifact_kind"] == "claude-runtime-session"
    assert payload["control_residue"]["last_budget_band"] == "medium"
    assert "budget_history" not in payload["control_residue"]
    assert restored.budget_history == ("shell-medium",)
    assert restored.brake_history == ("guarded",)
    assert restored.last_selected_family is SoftControlFamily.CHECK
    assert restored.feedback_window.entries[-1] == restored.last_realization_feedback


def test_claude_runtime_session_artifact_rejects_unknown_keys_and_invalid_enums() -> None:
    payload = _base_payload()
    payload["extra"] = {}
    with pytest.raises(ValueError, match="extra"):
        parse_claude_runtime_session_artifact(payload)

    payload = _base_payload()
    payload["control_residue"]["last_budget_band"] = "depleted"
    with pytest.raises(ValueError, match="last_budget_band"):
        parse_claude_runtime_session_artifact(payload)

    payload = _base_payload()
    payload["control_residue"]["last_realization_feedback"] = _feedback_payload()
    payload["control_residue"]["last_realization_feedback"]["selected_family"] = "wrong"
    with pytest.raises(ValueError, match="selected_family"):
        parse_claude_runtime_session_artifact(payload)


def test_claude_runtime_session_artifact_one_sided_last_feedback_normalizes_through_session_constructor() -> None:
    payload = _base_payload()
    payload["control_residue"]["last_budget_band"] = "high"
    payload["control_residue"]["last_realization_feedback"] = _feedback_payload(
        "session-rejected:mismatched-session-id:other"
    )

    restored = parse_claude_runtime_session_artifact(payload)

    assert restored.budget_history == ("shell-high",)
    assert restored.brake_history == ("guarded",)
    assert restored.feedback_window.entries == (restored.last_realization_feedback,)


def test_claude_runtime_session_artifact_same_path_overwrite_safety(tmp_path) -> None:
    session = ClaudeRuntimeSession(
        session_id="cl-file",
        event_index=1,
        budget_history=("shell-low",),
        last_realization_feedback=_feedback(),
        feedback_window=ReferenceRealizationFeedbackWindow(entries=(_feedback(),)),
    )
    path = tmp_path / "claude-session.json"

    write_claude_runtime_session_artifact(path, session)
    original_payload = json.loads(path.read_text(encoding="utf-8"))
    restored = read_claude_runtime_session_artifact(path)

    assert original_payload["artifact_kind"] == "claude-runtime-session"
    assert restored.session_id == "cl-file"

    updated_session = ClaudeRuntimeSession(
        session_id=restored.session_id,
        event_index=2,
        budget_history=("shell-medium",),
        last_realization_feedback=_feedback("warn-next"),
        feedback_window=ReferenceRealizationFeedbackWindow(
            entries=(_feedback(), _feedback("warn-next"))
        ),
    )
    write_claude_runtime_session_artifact(path, updated_session)
    updated_payload = json.loads(path.read_text(encoding="utf-8"))

    assert updated_payload["continuity_truth"]["event_index"] == 2
    assert updated_payload["control_residue"]["last_budget_band"] == "medium"


def _base_payload() -> dict[str, object]:
    return {
        "artifact_kind": "claude-runtime-session",
        "artifact_version": 1,
        "continuity_truth": {
            "session_id": "cl-session",
            "event_index": 1,
            "branch_registry": ["main"],
            "active_track_ref": "main",
            "pending_goal_refs": [],
        },
        "control_residue": {
            "last_budget_band": None,
            "last_commitment_result_summary": None,
            "last_realization_feedback": None,
            "feedback_window": [],
        },
    }


def _feedback_payload(warning: str | None = None) -> dict[str, object]:
    return _feedback(warning).as_summary()


def _feedback(warning: str | None = None) -> ReferenceRealizationFeedback:
    warning_codes = ()
    if warning is not None:
        warning_codes = (warning,)
    return ReferenceRealizationFeedback(
        selected_family=SoftControlFamily.CHECK,
        realized_family=SoftControlFamily.CHECK,
        brake_state=BrakeState.GUARDED,
        commitment_result_kind="certified",
        warning_codes=warning_codes,
        host_friction_tags=("approval-boundary-present",),
    )
