"""Unit tests for bounded OpenAI runtime session artifact I/O."""

from __future__ import annotations

import json

import pytest

from cortex.hosts.openai.runtime import OpenAIRuntimeSession
from cortex.hosts.openai.session_io import (
    build_openai_runtime_session_artifact,
    parse_openai_runtime_session_artifact,
    read_openai_runtime_session_artifact,
    write_openai_runtime_session_artifact,
)
from cortex.sre.modulators import ExecutiveModulatorMemory
from cortex.sre.preservation import (
    FalsifiedStructure,
    InterventionBudget,
    PreservationState,
    TrustedStructure,
)


def test_openai_runtime_session_artifact_roundtrips_compact_product_journal() -> None:
    session = OpenAIRuntimeSession(
        session_id="oa-session",
        event_index=3,
        active_goal_ref="verified-work:python_workspace_pytest_v1:src/bookmarks_api/main.py",
        pending_goal_refs=("goal-follow-up",),
        confirmed_artifact_refs=("artifact-a", "artifact-b"),
        last_failure_class="patch_apply_failed",
        next_recommended_move="repair",
        executive_modulator_memory=ExecutiveModulatorMemory(
            focus_tonic=0.1,
            explore_tonic=0.2,
            stop_tonic=0.3,
            update_tonic=0.4,
        ),
        preservation_state=PreservationState(
            task_anchor="verified-work:python_workspace_pytest_v1:src/bookmarks_api/main.py",
            trusted_structure=TrustedStructure(
                checks=frozenset({"parse"}),
                paths=frozenset({"src/bookmarks_api/main.py"}),
            ),
            falsified_structure=FalsifiedStructure(
                failure_class="patch_apply_failed",
                checks=frozenset(),
                failing_tests=frozenset(),
                blocked_message=None,
            ),
            lawful_repair_surface=frozenset({"src/bookmarks_api/main.py"}),
            intervention_budget=InterventionBudget(
                allowed_moves=frozenset({"repair"}),
                remaining_repairs=1,
            ),
        ),
    )

    artifact = build_openai_runtime_session_artifact(session)
    payload = artifact.as_payload()
    restored = parse_openai_runtime_session_artifact(payload)

    assert payload == {
        "artifact_kind": "openai_product_journal",
        "artifact_version": 1,
        "journal": {
            "session_id": "oa-session",
            "event_index": 3,
            "branch_registry": ["main"],
            "active_track_ref": "main",
            "active_goal_ref": "verified-work:python_workspace_pytest_v1:src/bookmarks_api/main.py",
            "pending_goal_refs": ["goal-follow-up"],
            "confirmed_artifact_refs": ["artifact-a", "artifact-b"],
            "budget_history": [],
            "brake_history": [],
            "last_selected_family": None,
            "last_commitment_result_summary": None,
            "last_realization_feedback": None,
            "feedback_window": [],
            "executive_modulator_memory": {
                "focus_tonic": 0.1,
                "explore_tonic": 0.2,
                "stop_tonic": 0.3,
                "update_tonic": 0.4,
            },
            "last_failure_class": "patch_apply_failed",
            "next_recommended_move": "repair",
            "preservation_state": {
                "task_anchor": "verified-work:python_workspace_pytest_v1:src/bookmarks_api/main.py",
                "trusted_structure": {
                    "checks": ["parse"],
                    "paths": ["src/bookmarks_api/main.py"],
                },
                "falsified_structure": {
                    "failure_class": "patch_apply_failed",
                    "checks": [],
                    "failing_tests": [],
                    "blocked_message": None,
                },
                "lawful_repair_surface": ["src/bookmarks_api/main.py"],
                "intervention_budget": {
                    "allowed_moves": ["repair"],
                    "remaining_repairs": 1,
                },
            },
        },
    }
    assert restored == session


def test_openai_runtime_session_artifact_rejects_legacy_shape_unknown_keys_and_invalid_fields() -> None:
    with pytest.raises(ValueError, match="openai_product_journal"):
        parse_openai_runtime_session_artifact(
            {
                "artifact_kind": "openai-runtime-session",
                "artifact_version": 1,
                "continuity_truth": {},
                "control_residue": {},
            }
        )

    payload = _base_payload()
    payload["extra"] = {}
    with pytest.raises(ValueError, match="extra"):
        parse_openai_runtime_session_artifact(payload)

    payload = _base_payload()
    payload["journal"]["next_recommended_move"] = "branch"
    with pytest.raises(ValueError, match="next_recommended_move"):
        parse_openai_runtime_session_artifact(payload)

    payload = _base_payload()
    payload["journal"]["last_failure_class"] = "degraded"
    with pytest.raises(ValueError, match="last_failure_class"):
        parse_openai_runtime_session_artifact(payload)


def test_openai_runtime_session_artifact_same_path_overwrite_safety(tmp_path) -> None:
    session = OpenAIRuntimeSession(
        session_id="oa-file",
        event_index=1,
        next_recommended_move="check",
    )
    path = tmp_path / "openai-session.json"

    write_openai_runtime_session_artifact(path, session)
    original_payload = json.loads(path.read_text(encoding="utf-8"))
    restored = read_openai_runtime_session_artifact(path)

    assert original_payload["artifact_kind"] == "openai_product_journal"
    assert restored.session_id == "oa-file"

    updated_session = OpenAIRuntimeSession(
        session_id=restored.session_id,
        event_index=2,
        pending_goal_refs=("goal-next",),
        confirmed_artifact_refs=("artifact-next",),
        next_recommended_move="continue",
    )
    write_openai_runtime_session_artifact(path, updated_session)
    updated_payload = json.loads(path.read_text(encoding="utf-8"))

    assert updated_payload["journal"]["event_index"] == 2
    assert updated_payload["journal"]["confirmed_artifact_refs"] == ["artifact-next"]
    assert updated_payload["journal"]["executive_modulator_memory"] is None


def test_openai_runtime_session_artifact_accepts_pre_modulator_full_journal_shape() -> None:
    payload = {
        "artifact_kind": "openai_product_journal",
        "artifact_version": 1,
        "journal": {
            "session_id": "oa-pre-modulator",
            "event_index": 2,
            "branch_registry": ["main", "branch-alpha"],
            "active_track_ref": "branch-alpha",
            "active_goal_ref": "branch-alpha",
            "pending_goal_refs": [],
            "confirmed_artifact_refs": ["artifact-a"],
            "budget_history": ["shell-low"],
            "brake_history": ["guarded"],
            "last_selected_family": "seek-context",
            "last_commitment_result_summary": "candidate-only",
            "last_realization_feedback": None,
            "feedback_window": [],
            "last_failure_class": None,
            "next_recommended_move": "check",
        },
    }

    restored = parse_openai_runtime_session_artifact(payload)

    assert restored.executive_modulator_memory is None
    assert restored.active_track_ref == "branch-alpha"


def _base_payload() -> dict[str, object]:
    return {
        "artifact_kind": "openai_product_journal",
        "artifact_version": 1,
        "journal": {
            "session_id": "oa-session",
            "event_index": 1,
            "active_goal_ref": None,
            "pending_goal_refs": [],
            "confirmed_artifact_refs": [],
            "last_failure_class": None,
            "next_recommended_move": "continue",
        },
    }
