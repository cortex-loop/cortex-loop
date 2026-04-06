"""Unit tests for bounded OpenAI runtime session artifact I/O."""

from __future__ import annotations

import json

import pytest

from cortex.runtime.openai import OpenAIRuntimeSession
from cortex.runtime.openai_session_io import (
    build_openai_runtime_session_artifact,
    parse_openai_runtime_session_artifact,
    read_openai_runtime_session_artifact,
    write_openai_runtime_session_artifact,
)


def test_openai_runtime_session_artifact_roundtrips_compact_product_journal() -> None:
    session = OpenAIRuntimeSession(
        session_id="oa-session",
        event_index=3,
        active_goal_ref="goal-fix-port-guard",
        pending_goal_refs=("goal-follow-up",),
        confirmed_artifact_refs=("artifact-a", "artifact-b"),
        last_failure_class="patch_apply_failed",
        next_recommended_move="repair",
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
            "active_goal_ref": "goal-fix-port-guard",
            "pending_goal_refs": ["goal-follow-up"],
            "confirmed_artifact_refs": ["artifact-a", "artifact-b"],
            "last_failure_class": "patch_apply_failed",
            "next_recommended_move": "repair",
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
