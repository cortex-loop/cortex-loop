"""Focused tests for direct OpenAI runtime-step behavior."""

from __future__ import annotations

import pytest

import cortex.hosts.openai.runtime as openai_runtime
from cortex.hosts.openai.runtime import (
    OpenAIRuntimeSession,
    run_openai_runtime_step,
    run_openai_runtime_verification_step,
)
from cortex.sre.verified_work import VerificationOutcome, WorkContract


def test_openai_runtime_step_rejects_canonical_cortex_event_name_before_runtime_processing() -> None:
    with pytest.raises(
        ValueError,
        match="raw OpenAI host event name, not a canonical Cortex event name",
    ):
        run_openai_runtime_step(
            "external/observation",
            {"session_id": "oa-bad", "response_id": "resp-1", "delta": "hello"},
        )


def test_openai_runtime_step_uses_compact_decision_table_without_reference_soft_control() -> None:
    assert not hasattr(openai_runtime, "select_reference_soft_control")
    assert not hasattr(openai_runtime, "build_reference_executive_state")

    result = run_openai_runtime_step(
        "response.completed",
        {
            "session_id": "oa-product",
            "response_id": "resp-product",
            "commitment_id": "oa-product-commit",
            "externally_consequential": True,
            "result_artifact_ref": "oa-product-artifact",
        },
        OpenAIRuntimeSession(session_id="oa-product"),
    )

    assert result.product_decision.decision == "check"
    assert result.product_decision.as_summary() == {
        "decision": "check",
        "consequential_write_pending": True,
        "approval_required": True,
        "evidence_gap": False,
        "continuation_debt": False,
        "failure_class": None,
    }
    assert result.commitment_result_kind == "certified"
    assert result.journal == {
        "session_id": "oa-product",
        "event_index": 1,
        "active_goal_ref": None,
        "pending_goal_refs": [],
        "confirmed_artifact_refs": ["oa-product-artifact"],
        "last_failure_class": None,
        "next_recommended_move": "check",
    }


def test_openai_runtime_step_preserves_session_mismatch_as_stop_without_reassigning_session() -> None:
    result = run_openai_runtime_step(
        "response.output_text.delta",
        {
            "session_id": "oa-mismatch-b",
            "response_id": "resp-mismatch",
            "delta": "hello",
        },
        OpenAIRuntimeSession(session_id="oa-mismatch-a"),
    )

    assert result.warnings == ("session-rejected:mismatched-session-id:oa-mismatch-b",)
    assert result.product_decision.decision == "stop"
    assert result.product_decision.failure_class == "session_mismatch"
    assert result.session.session_id == "oa-mismatch-a"


def test_openai_runtime_verification_step_updates_runtime_truth_from_external_failure() -> None:
    contract = WorkContract(
        allowed_write_paths=("src/bookmarks_api/main.py",),
        verification_profile="python_workspace_pytest_v1",
        output_carrier="full_files",
        max_repair_turns=1,
    )
    updated = run_openai_runtime_verification_step(
        VerificationOutcome(
            status="failed",
            failure_class="import_smoke_failed",
            import_smoke_ok=False,
            first_failure_excerpt="E   SyntaxError: invalid syntax",
        ),
        OpenAIRuntimeSession(session_id="oa-verified", event_index=3),
        work_contract=contract,
        remaining_repairs=1,
    )

    assert updated.as_summary() == {
        "session_id": "oa-verified",
        "event_index": 3,
        "active_goal_ref": None,
        "pending_goal_refs": [],
        "confirmed_artifact_refs": [],
        "last_failure_class": "import_smoke_failed",
        "next_recommended_move": "repair",
    }


def test_openai_runtime_verification_step_maps_blocked_missing_info_to_check() -> None:
    contract = WorkContract(
        allowed_write_paths=("src/bookmarks_api/main.py",),
        verification_profile="python_workspace_pytest_v1",
        output_carrier="full_files",
        max_repair_turns=1,
    )
    updated = run_openai_runtime_verification_step(
        VerificationOutcome(
            status="blocked",
            failure_class="blocked_missing_info",
            blocked_message="Need one more field.",
        ),
        OpenAIRuntimeSession(),
        work_contract=contract,
        remaining_repairs=1,
    )

    assert updated.last_failure_class == "blocked_missing_info"
    assert updated.next_recommended_move == "check"
