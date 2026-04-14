"""Unit tests for bounded reference runtime session artifact I/O."""

from __future__ import annotations

import json

import pytest

from cortex.hosts.reference.runtime import ReferenceRuntimeSession
from cortex.hosts.reference.session_io import (
    build_reference_runtime_session_artifact,
    parse_reference_runtime_session_artifact,
    read_reference_runtime_session_artifact,
    write_reference_runtime_session_artifact,
)
from cortex.sre.brake import BrakeState
from cortex.sre.feedback import ReferenceRealizationFeedback, ReferenceRealizationFeedbackWindow
from cortex.sre.families import SoftControlFamily
from cortex.sre.goals import make_resume_reminder
from cortex.sre.operator_routing import OperatorTaskMode


def test_reference_runtime_session_artifact_roundtrips_empty_session() -> None:
    session = ReferenceRuntimeSession()

    artifact = build_reference_runtime_session_artifact(session)
    payload = artifact.as_payload()
    restored = parse_reference_runtime_session_artifact(payload)

    assert payload == {
        "artifact_kind": "reference-runtime-session",
        "artifact_version": 1,
        "continuity_truth": {
            "session_id": None,
            "event_index": 0,
            "branch_registry": ["main"],
            "active_track_ref": "main",
            "pending_goal_refs": [],
            "continuity_reminders": [],
        },
        "control_residue": {
            "last_budget_band": None,
            "last_commitment_result_summary": None,
            "last_realization_feedback": None,
            "feedback_window": [],
            "executive_modulator_memory": None,
        },
    }
    assert restored == session


def test_reference_runtime_session_artifact_roundtrips_populated_continuity_truth() -> None:
    session = ReferenceRuntimeSession(
        session_id="session-continuity",
        event_index=4,
        branch_registry=("main", "branch-alpha"),
        active_track_ref="branch-alpha",
        pending_goal_refs=("goal-extra",),
        continuity_reminders=(make_resume_reminder("branch-alpha"),),
    )

    restored = parse_reference_runtime_session_artifact(
        build_reference_runtime_session_artifact(session).as_payload()
    )

    assert restored.session_id == "session-continuity"
    assert restored.event_index == 4
    assert restored.branch_registry == ("main", "branch-alpha")
    assert restored.active_track_ref == "branch-alpha"
    assert restored.pending_goal_refs == ("goal-extra",)
    assert restored.continuity_reminders == (make_resume_reminder("branch-alpha"),)
    assert restored.budget_history == ()
    assert restored.brake_history == ()


def test_reference_runtime_session_artifact_normalizes_legacy_continuity_reminders() -> None:
    payload = _base_payload()
    payload["continuity_truth"]["continuity_reminders"] = ["resume branch-alpha after review"]

    restored = parse_reference_runtime_session_artifact(payload)

    assert restored.continuity_reminders == (make_resume_reminder("branch-alpha"),)


def test_reference_runtime_session_artifact_downgrades_unknown_legacy_continuity_reminders() -> None:
    payload = _base_payload()
    payload["continuity_truth"]["continuity_reminders"] = ["review later"]

    restored = parse_reference_runtime_session_artifact(payload)

    assert restored.continuity_reminders == ()


def test_reference_runtime_session_artifact_accepts_legacy_continuity_truth_shape() -> None:
    payload = _base_payload()
    del payload["continuity_truth"]["continuity_reminders"]

    restored = parse_reference_runtime_session_artifact(payload)

    assert restored.continuity_reminders == ()


def test_reference_runtime_session_artifact_roundtrips_bounded_residue_without_full_histories() -> None:
    warning_feedback = _feedback("continuity-rejected:missing-resume-anchor:branch-alpha")
    session = ReferenceRuntimeSession(
        session_id="session-residue",
        event_index=3,
        branch_registry=("main", "branch-alpha"),
        active_track_ref="main",
        pending_goal_refs=("branch-alpha",),
        budget_history=("shell-low", "shell-medium"),
        brake_history=("quiescent", "guarded"),
        last_selected_family=SoftControlFamily.BRANCH,
        last_commitment_result_summary="candidate-only",
        last_realization_feedback=warning_feedback,
        feedback_window=ReferenceRealizationFeedbackWindow(
            entries=(_feedback("warn-earlier"), warning_feedback)
        ),
    )

    artifact = build_reference_runtime_session_artifact(session)
    payload = artifact.as_payload()
    restored = parse_reference_runtime_session_artifact(payload)

    assert payload["control_residue"] == {
        "last_budget_band": "medium",
        "last_commitment_result_summary": "candidate-only",
        "last_realization_feedback": warning_feedback.as_summary(),
        "feedback_window": [
            _feedback("warn-earlier").as_summary(),
            warning_feedback.as_summary(),
        ],
        "executive_modulator_memory": None,
    }
    assert "budget_history" not in payload["control_residue"]
    assert "brake_history" not in payload["control_residue"]
    assert restored.budget_history == ("shell-medium",)
    assert restored.brake_history == ("guarded",)
    assert restored.last_selected_family is SoftControlFamily.BRANCH
    assert restored.last_commitment_result_summary == "candidate-only"
    assert restored.last_realization_feedback == warning_feedback
    assert restored.feedback_window.entries == (
        _feedback("warn-earlier"),
        warning_feedback,
    )


def test_reference_runtime_session_artifact_rejects_wrong_kind_and_version() -> None:
    payload = _base_payload()
    payload["artifact_kind"] = "wrong-kind"
    with pytest.raises(ValueError, match="artifact_kind"):
        parse_reference_runtime_session_artifact(payload)

    payload = _base_payload()
    payload["artifact_version"] = 2
    with pytest.raises(ValueError, match="artifact_version"):
        parse_reference_runtime_session_artifact(payload)


def test_reference_runtime_session_artifact_rejects_unknown_keys_everywhere() -> None:
    payload = _base_payload()
    payload["extra"] = {}
    with pytest.raises(ValueError, match="missing=\\[\\], extra=\\['extra'\\]"):
        parse_reference_runtime_session_artifact(payload)

    payload = _base_payload()
    payload["continuity_truth"]["extra"] = "drift"
    with pytest.raises(ValueError, match="continuity_truth"):
        parse_reference_runtime_session_artifact(payload)

    payload = _base_payload()
    payload["control_residue"]["feedback_window"] = [_feedback_payload(), {"extra": "drift"}]
    with pytest.raises(ValueError, match="feedback_window"):
        parse_reference_runtime_session_artifact(payload)


def test_reference_runtime_session_artifact_rejects_invalid_enums() -> None:
    payload = _base_payload()
    payload["control_residue"]["last_budget_band"] = "depleted"
    with pytest.raises(ValueError, match="last_budget_band"):
        parse_reference_runtime_session_artifact(payload)

    payload = _base_payload()
    feedback = _feedback_payload()
    feedback["selected_family"] = "wrong"
    payload["control_residue"]["last_realization_feedback"] = feedback
    with pytest.raises(ValueError, match="selected_family"):
        parse_reference_runtime_session_artifact(payload)


def test_reference_runtime_session_artifact_rejects_mismatched_last_feedback_and_window() -> None:
    payload = _base_payload()
    payload["control_residue"]["last_realization_feedback"] = _feedback_payload("warn-a")
    payload["control_residue"]["feedback_window"] = [_feedback_payload("warn-b")]

    with pytest.raises(ValueError, match="newest entry must match"):
        parse_reference_runtime_session_artifact(payload)


def test_reference_runtime_session_artifact_one_sided_last_feedback_normalizes_through_session_constructor() -> None:
    payload = _base_payload()
    payload["control_residue"]["last_budget_band"] = "low"
    payload["control_residue"]["last_realization_feedback"] = _feedback_payload(
        "session-rejected:mismatched-session-id:session-b"
    )

    restored = parse_reference_runtime_session_artifact(payload)

    assert restored.budget_history == ("shell-low",)
    assert restored.brake_history == ("guarded",)
    assert restored.last_realization_feedback is not None
    assert restored.feedback_window.entries == (restored.last_realization_feedback,)


def test_reference_runtime_session_artifact_one_sided_window_only_normalizes_through_session_constructor() -> None:
    payload = _base_payload()
    payload["control_residue"]["feedback_window"] = [_feedback_payload("warn-only")]

    restored = parse_reference_runtime_session_artifact(payload)

    assert restored.last_realization_feedback == _feedback("warn-only")
    assert restored.feedback_window.entries == (_feedback("warn-only"),)
    assert restored.last_selected_family is None
    assert restored.brake_history == ()


def test_reference_runtime_session_artifact_read_write_roundtrip_uses_json_file(
    tmp_path,
) -> None:
    session = ReferenceRuntimeSession(
        session_id="session-file",
        event_index=2,
        budget_history=("shell-high",),
        last_realization_feedback=_feedback(),
        feedback_window=ReferenceRealizationFeedbackWindow(entries=(_feedback(),)),
    )
    artifact_path = tmp_path / "session.json"

    write_reference_runtime_session_artifact(artifact_path, session)
    restored = read_reference_runtime_session_artifact(artifact_path)

    assert json.loads(artifact_path.read_text(encoding="utf-8"))["artifact_kind"] == (
        "reference-runtime-session"
    )
    assert restored.session_id == "session-file"
    assert restored.budget_history == ("shell-high",)
    assert restored.brake_history == ("guarded",)


def test_reference_runtime_session_artifact_roundtrips_feedback_task_mode_and_probe_result_class() -> None:
    feedback = ReferenceRealizationFeedback(
        selected_family=SoftControlFamily.CHECK,
        realized_family=SoftControlFamily.CHECK,
        brake_state=BrakeState.GUARDED,
        task_mode=OperatorTaskMode.RESUME_EXECUTE,
        commitment_result_kind="certified",
        host_friction_tags=("approval-boundary-present",),
        evidence_progress_class="artifact",
        continuity_progress_class="none",
        probe_result_class="succeeded",
    )
    payload = _base_payload()
    payload["control_residue"]["last_realization_feedback"] = feedback.as_summary()
    payload["control_residue"]["feedback_window"] = [feedback.as_summary()]

    restored = parse_reference_runtime_session_artifact(payload)

    assert restored.last_realization_feedback == feedback
    assert restored.feedback_window.entries == (feedback,)


def _base_payload() -> dict[str, object]:
    return {
        "artifact_kind": "reference-runtime-session",
        "artifact_version": 1,
        "continuity_truth": {
            "session_id": "session-a",
            "event_index": 1,
            "branch_registry": ["main"],
            "active_track_ref": "main",
            "pending_goal_refs": [],
            "continuity_reminders": [],
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
        selected_family=SoftControlFamily.BRANCH,
        realized_family=SoftControlFamily.CHECK,
        brake_state=BrakeState.GUARDED,
        commitment_result_kind="certified",
        warning_codes=warning_codes,
        host_friction_tags=("approval-boundary-present",),
    )
