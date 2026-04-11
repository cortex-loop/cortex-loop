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


def test_openai_runtime_step_adds_reference_shell_without_changing_product_decision_table() -> None:
    assert hasattr(openai_runtime, "select_reference_soft_control")
    assert hasattr(openai_runtime, "build_reference_executive_state")

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
    assert result.selected_family.value == "seek-context"
    assert result.realized_family.value == "seek-context"
    assert result.brake_state.value == "guarded"
    assert result.executive_state_summary["active_track_ref"] == "main"
    assert result.control_ledger_summary["budget_band"] == "high"
    assert result.feedback_window_summary_payload["window_size"] == 0
    assert result.commitment_result_kind == "certified"
    assert result.journal == {
        "session_id": "oa-product",
        "event_index": 1,
        "branch_registry": ["main"],
        "active_track_ref": "main",
        "active_goal_ref": None,
        "pending_goal_refs": [],
        "confirmed_artifact_refs": ["oa-product-artifact"],
        "budget_history": ["shell-high"],
        "brake_history": ["guarded"],
        "last_selected_family": "seek-context",
        "last_commitment_result_summary": "certified",
        "last_realization_feedback": {
            "selected_family": "seek-context",
            "realized_family": "seek-context",
            "brake_state": "guarded",
            "commitment_result_kind": "certified",
            "warning_codes": [],
            "host_friction_tags": [
                "approval-boundary-present",
                "capability-view-missing",
            ],
        },
        "feedback_window": [
            {
                "selected_family": "seek-context",
                "realized_family": "seek-context",
                "brake_state": "guarded",
                "commitment_result_kind": "certified",
                "warning_codes": [],
                "host_friction_tags": [
                    "approval-boundary-present",
                    "capability-view-missing",
                ],
            }
        ],
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


def test_openai_runtime_step_branch_open_preserves_continuity_without_forcing_check() -> None:
    result = run_openai_runtime_step(
        "response.output_text.delta",
        {
            "session_id": "oa-open",
            "response_id": "resp-open",
            "branch_operation": "open",
            "branch_track_ref": "branch-alpha",
            "delta": "open",
        },
        OpenAIRuntimeSession(session_id="oa-open"),
    )

    assert result.warnings == ()
    assert result.product_decision.as_summary() == {
        "decision": "continue",
        "consequential_write_pending": False,
        "approval_required": False,
        "evidence_gap": False,
        "continuation_debt": False,
        "failure_class": None,
    }
    assert result.session.as_summary()["branch_registry"] == ["main", "branch-alpha"]
    assert result.session.active_track_ref == "branch-alpha"
    assert result.session.active_goal_ref == "branch-alpha"


def test_openai_runtime_step_suspend_surfaces_pending_goal_debt() -> None:
    opened = run_openai_runtime_step(
        "response.output_text.delta",
        {
            "session_id": "oa-suspend",
            "response_id": "resp-suspend",
            "branch_operation": "open",
            "branch_track_ref": "branch-alpha",
            "delta": "open",
        },
        OpenAIRuntimeSession(session_id="oa-suspend"),
    ).session

    suspended = run_openai_runtime_step(
        "response.output_text.delta",
        {
            "session_id": "oa-suspend",
            "response_id": "resp-suspend",
            "branch_operation": "suspend",
            "branch_track_ref": "branch-alpha",
            "delta": "suspend",
        },
        opened,
    )

    assert suspended.warnings == ("continuity-debt:pending-goals",)
    assert suspended.product_decision.as_summary() == {
        "decision": "check",
        "consequential_write_pending": False,
        "approval_required": False,
        "evidence_gap": False,
        "continuation_debt": True,
        "failure_class": None,
    }
    assert suspended.session.active_track_ref == "main"
    assert suspended.session.active_goal_ref is None
    assert suspended.session.pending_goal_refs == ("branch-alpha",)


def test_openai_runtime_step_resume_without_anchor_rejects_and_forces_check() -> None:
    opened = run_openai_runtime_step(
        "response.output_text.delta",
        {
            "session_id": "oa-resume",
            "response_id": "resp-resume",
            "branch_operation": "open",
            "branch_track_ref": "branch-alpha",
            "delta": "open",
        },
        OpenAIRuntimeSession(session_id="oa-resume"),
    ).session

    resumed = run_openai_runtime_step(
        "response.output_text.delta",
        {
            "session_id": "oa-resume",
            "response_id": "resp-resume",
            "branch_operation": "resume",
            "branch_track_ref": "branch-alpha",
            "delta": "resume",
        },
        opened,
    )

    assert resumed.warnings == (
        "continuity-rejected:missing-resume-anchor:branch-alpha",
    )
    assert resumed.product_decision.decision == "check"
    assert resumed.product_decision.continuation_debt is True
    assert resumed.session.active_track_ref == "branch-alpha"
    assert resumed.session.pending_goal_refs == ()


def test_openai_runtime_step_illegal_merge_target_rejects_and_forces_check() -> None:
    opened = run_openai_runtime_step(
        "response.output_text.delta",
        {
            "session_id": "oa-merge",
            "response_id": "resp-merge",
            "branch_operation": "open",
            "branch_track_ref": "branch-alpha",
            "delta": "open",
        },
        OpenAIRuntimeSession(session_id="oa-merge"),
    ).session

    merged = run_openai_runtime_step(
        "response.output_text.delta",
        {
            "session_id": "oa-merge",
            "response_id": "resp-merge",
            "branch_operation": "merge",
            "branch_track_ref": "branch-alpha",
            "merge_target_ref": "branch-beta",
            "delta": "merge",
        },
        opened,
    )

    assert merged.warnings == (
        "continuity-rejected:illegal-merge-target:branch-beta",
    )
    assert merged.product_decision.decision == "check"
    assert merged.product_decision.continuation_debt is True
    assert merged.session.active_track_ref == "branch-alpha"
    assert merged.session.branch_registry == ("main", "branch-alpha")


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
        "branch_registry": ["main"],
        "active_track_ref": "main",
        "active_goal_ref": "verified-work:python_workspace_pytest_v1:src/bookmarks_api/main.py",
        "pending_goal_refs": [],
        "confirmed_artifact_refs": [],
        "budget_history": [],
        "brake_history": [],
        "last_selected_family": None,
        "last_commitment_result_summary": None,
        "last_realization_feedback": None,
        "feedback_window": [],
        "last_failure_class": "import_smoke_failed",
        "next_recommended_move": "repair",
        "preservation_state": {
            "task_anchor": "verified-work:python_workspace_pytest_v1:src/bookmarks_api/main.py",
            "trusted_structure": {
                "checks": [],
                "paths": [],
            },
            "falsified_structure": {
                "failure_class": "import_smoke_failed",
                "checks": ["import_smoke"],
                "failing_tests": [],
                "blocked_message": None,
            },
            "lawful_repair_surface": ["src/bookmarks_api/main.py"],
            "intervention_budget": {
                "allowed_moves": ["repair"],
                "remaining_repairs": 1,
            },
        },
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
    assert updated.active_goal_ref == "verified-work:python_workspace_pytest_v1:src/bookmarks_api/main.py"
    assert updated.preservation_state is not None
    assert updated.preservation_state.lawful_repair_surface == frozenset()
