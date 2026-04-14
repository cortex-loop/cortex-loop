"""Focused tests for direct OpenAI runtime-step behavior."""

from __future__ import annotations

from cortex.hosts._executive_closure import (
    public_posture_for_task_mode,
    task_mode_for_runtime,
)
import pytest

import cortex.hosts.openai.runtime as openai_runtime
from cortex.hosts.openai.runtime import (
    OpenAIRuntimeSession,
    run_openai_runtime_step,
    run_openai_runtime_verification_step,
)
from cortex.sre.brake import BrakeState
from cortex.sre.goals import GoalContinuityView
from cortex.sre.executive_summary import ExecutiveSignalSummary
from cortex.sre.families import SoftControlFamily
from cortex.sre.modulators import ExecutiveModulatorMemory
from cortex.sre.operator_routing import OperatorTaskMode
from cortex.sre.policy_view import ExecutivePolicyView
from cortex.sre.state import (
    ReferenceBrakeView,
    ReferenceControlAllocationView,
    ReferenceExecutiveState,
    ReferenceModeAndGatingView,
    ReferenceUncertaintyMonitoringView,
)
from cortex.sre.uncertainty import UncertaintyEstimate
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


def test_openai_runtime_family_shim_keeps_neutral_continue_and_brake_latched_stop() -> None:
    assert openai_runtime._action_for_realized_family(
        realized_family=SoftControlFamily.NEUTRAL,
        brake_state=BrakeState.QUIESCENT,
    ) == "continue"
    assert openai_runtime._action_for_realized_family(
        realized_family=SoftControlFamily.SEEK_CONTEXT,
        brake_state=BrakeState.GUARDED,
    ) == "check"
    assert openai_runtime._action_for_realized_family(
        realized_family=SoftControlFamily.BRAKE,
        brake_state=BrakeState.GUARDED,
    ) == "check"
    assert openai_runtime._action_for_realized_family(
        realized_family=SoftControlFamily.BRAKE,
        brake_state=BrakeState.LATCHED,
    ) == "stop"


def test_openai_runtime_step_keeps_hard_product_guards_ahead_of_reference_control() -> None:
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
    assert result.executive_state_summary["probe_path_state"] == "unavailable"
    assert (
        result.executive_state_summary["probe_unavailable_reason"]
        == "documented-probe-surface-unavailable"
    )
    assert result.control_ledger_summary["budget_band"] == "high"
    assert result.control_ledger_summary["allocation_diagnostics"]["probe_path_state"] == (
        "unavailable"
    )
    assert (
        result.control_ledger_summary["allocation_diagnostics"]["probe_unavailable_reason"]
        == "documented-probe-surface-unavailable"
    )
    assert result.control_ledger_summary["allocation_diagnostics"]["probe_result_class"] is None
    assert result.control_ledger_summary["audit_projection"] == {
        "selected_family": "seek-context",
        "realized_family": "seek-context",
        "dominant_uncertainty_sources": ["host-capability", "environment"],
        "activation_threshold": pytest.approx(0.22),
        "selected_delta_over_neutral": pytest.approx(0.3705),
        "rejected_cheaper_families": ["neutral", "check"],
        "verification_state": "completed",
        "explainability_profile": "focused",
        "probe_path_state": "unavailable",
        "probe_result_class": None,
        "probe_unavailable_reason": "documented-probe-surface-unavailable",
    }
    assert result.feedback_window_summary_payload["window_size"] == 0
    assert result.executive_signal_summary_payload == {
        "uncertainty": 0.55,
        "repeated_failure_pressure": 0.0,
        "quota_pressure": 0.75,
        "continuity_demand": 0.0,
        "novelty_pressure": 0.2,
        "verification_conflict_pressure": 0.15,
    }
    assert result.executive_modulator_state_payload == {
        "focus_gain": 0.0,
        "explore_gain": 0.3375,
        "stop_pressure": 0.6,
        "update_pressure": 0.4025,
    }
    assert result.executive_policy_view_payload == {
        "default_profile_bonus": 0.0,
        "switch_margin": 0.053,
        "stop_threshold": 0.585,
        "allow_extra_read_pass": False,
        "verification_intensity": 0.3805,
    }
    assert result.closure_required is False
    assert result.closure_reason_tags == ()
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
            "task_mode": "execute",
            "commitment_result_kind": "certified",
            "warning_codes": [],
            "host_friction_tags": [
                "approval-boundary-present",
                "capability-view-missing",
            ],
            "evidence_state_moved": True,
            "continuity_improved": False,
        },
        "feedback_window": [
            {
                "selected_family": "seek-context",
                "realized_family": "seek-context",
                "brake_state": "guarded",
                "task_mode": "execute",
                "commitment_result_kind": "certified",
                "warning_codes": [],
                "host_friction_tags": [
                    "approval-boundary-present",
                    "capability-view-missing",
                ],
                "evidence_state_moved": True,
                "continuity_improved": False,
            }
        ],
        "executive_modulator_memory": {
            "focus_tonic": 0.0,
            "explore_tonic": 0.3375,
            "stop_tonic": 0.6,
            "update_tonic": 0.4025,
        },
        "last_failure_class": None,
        "next_recommended_move": "check",
    }


def test_openai_runtime_step_surfaces_typed_probe_unavailability_without_probe_result() -> None:
    result = run_openai_runtime_step(
        "response.output_text.delta",
        {
            "session_id": "oa-probe-unavailable",
            "response_id": "resp-probe-unavailable",
            "delta": "hello",
        },
        OpenAIRuntimeSession(session_id="oa-probe-unavailable"),
    )

    assert result.executive_state_summary["probe_path_state"] == "unavailable"
    assert (
        result.executive_state_summary["probe_unavailable_reason"]
        == "documented-probe-surface-unavailable"
    )
    assert result.control_ledger_summary["allocation_diagnostics"]["probe_path_state"] == (
        "unavailable"
    )
    assert (
        result.control_ledger_summary["allocation_diagnostics"]["probe_unavailable_reason"]
        == "documented-probe-surface-unavailable"
    )
    assert result.control_ledger_summary["allocation_diagnostics"]["probe_result_class"] is None
    assert result.control_ledger_summary["audit_projection"]["probe_path_state"] == (
        "unavailable"
    )
    assert result.control_ledger_summary["audit_projection"]["probe_result_class"] is None


def test_openai_runtime_step_can_raise_audit_projection_from_explicit_request() -> None:
    result = run_openai_runtime_step(
        "response.output_text.delta",
        {
            "session_id": "oa-explicit-audit",
            "response_id": "resp-explicit-audit",
            "delta": "hello",
        },
        OpenAIRuntimeSession(session_id="oa-explicit-audit"),
        audit_intensity="structured",
    )

    assert result.control_ledger_summary["allocation_diagnostics"]["explainability_profile"] == (
        "structured"
    )
    assert result.control_ledger_summary["audit_projection"]["explainability_profile"] == (
        "structured"
    )
    assert result.control_ledger_summary["audit_projection"]["selected_family"] == (
        result.control_ledger_summary["selected_family"]
    )


def test_openai_runtime_session_canonicalizes_executive_modulator_memory_at_session_truth_boundary() -> None:
    session = OpenAIRuntimeSession(
        executive_modulator_memory=ExecutiveModulatorMemory(
            focus_tonic=0.0,
            explore_tonic=0.3375,
            stop_tonic=0.6000000000000001,
            update_tonic=0.40249999999999997,
        )
    )

    assert session.executive_modulator_memory == ExecutiveModulatorMemory(
        focus_tonic=0.0,
        explore_tonic=0.3375,
        stop_tonic=0.6,
        update_tonic=0.4025,
    )
    assert session.as_summary()["executive_modulator_memory"] == {
        "focus_tonic": 0.0,
        "explore_tonic": 0.3375,
        "stop_tonic": 0.6,
        "update_tonic": 0.4025,
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


def test_openai_runtime_step_cheap_seek_context_pressure_now_checks() -> None:
    result = run_openai_runtime_step(
        "response.output_text.delta",
        {
            "session_id": "oa-cheap-pressure",
            "response_id": "resp-cheap-pressure",
            "delta": "hello",
        },
        OpenAIRuntimeSession(session_id="oa-cheap-pressure"),
    )

    assert result.selected_family.value == "seek-context"
    assert result.realized_family.value == "seek-context"
    assert result.product_decision.as_summary() == {
        "decision": "check",
        "consequential_write_pending": False,
        "approval_required": False,
        "evidence_gap": False,
        "continuation_debt": False,
        "failure_class": None,
    }
    assert result.executive_signal_summary_payload["quota_pressure"] == 0.25
    assert result.executive_state_summary["posture"] == "inspect"
    assert result.executive_policy_view_payload["switch_margin"] == pytest.approx(0.045)
    assert result.executive_policy_view_payload["allow_extra_read_pass"] is True
    assert result.operator_route_payload["route_profile"] == "inspect_light"
    assert result.operator_route_payload["route_budget"]["allow_extra_read_pass"] is True
    assert result.operator_route_payload["route_budget"]["max_retries"] == 1
    assert result.executive_state.mode_and_gating.task_mode is OperatorTaskMode.INSPECT
    assert result.executive_signal_summary.task_mode is OperatorTaskMode.INSPECT
    assert result.executive_state_summary["posture"] == public_posture_for_task_mode(
        result.executive_signal_summary.task_mode
    )
    assert task_mode_for_runtime(
        dispatch_decision=result.dispatch_decision,
        active_track_ref=result.executive_state.goal_continuity.active_track_ref,
        pending_goal_refs=result.executive_state.goal_continuity.pending_goal_refs,
        continuity_warnings=result.warnings,
        continuity_reminders=(),
        approval_required=False,
        evidence_gap=False,
        consequential_write_pending=False,
        preservation_active=False,
    ) is result.executive_signal_summary.task_mode
    assert result.closure_required is False
    assert result.closure_reason_tags == ()
    assert result.session.next_recommended_move == "check"


def test_openai_runtime_step_branch_open_preserves_continuity_without_blunt_debt() -> None:
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
        "decision": "check",
        "consequential_write_pending": False,
        "approval_required": False,
        "evidence_gap": False,
        "continuation_debt": False,
        "failure_class": None,
    }
    assert result.selected_family.value == "seek-context"
    assert result.realized_family.value == "seek-context"
    assert result.executive_signal_summary_payload["continuity_demand"] == 0.7
    assert result.executive_modulator_state_payload["focus_gain"] == pytest.approx(0.37)
    assert result.executive_policy_view_payload["default_profile_bonus"] == pytest.approx(0.0724)
    assert result.closure_required is False
    assert result.closure_reason_tags == ()
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
    assert suspended.executive_signal_summary_payload["continuity_demand"] == 1.0
    assert suspended.closure_required is True
    assert suspended.closure_reason_tags == (
        "continuity_reminder",
        "pending_goal_debt",
    )
    assert suspended.session.next_recommended_move == "check"


def test_openai_runtime_step_cheap_continuity_debt_surfaces_resume_posture_and_alignment() -> None:
    result = run_openai_runtime_step(
        "response.output_text.delta",
        {
            "session_id": "oa-resume-posture",
            "response_id": "resp-resume-posture",
            "branch_operation": "open",
            "branch_track_ref": "branch-alpha",
            "delta": "open",
        },
        OpenAIRuntimeSession(session_id="oa-resume-posture"),
    )

    assert result.executive_state.mode_and_gating.task_mode is OperatorTaskMode.RESUME_EXECUTE
    assert result.executive_signal_summary.task_mode is OperatorTaskMode.RESUME_EXECUTE
    assert result.executive_state_summary["posture"] == "resume"
    assert result.executive_state_summary["posture"] == public_posture_for_task_mode(
        result.executive_signal_summary.task_mode
    )
    assert task_mode_for_runtime(
        dispatch_decision=result.dispatch_decision,
        active_track_ref=result.executive_state.goal_continuity.active_track_ref,
        pending_goal_refs=result.executive_state.goal_continuity.pending_goal_refs,
        continuity_warnings=result.warnings,
        continuity_reminders=(),
        approval_required=False,
        evidence_gap=False,
        consequential_write_pending=False,
        preservation_active=False,
    ) is result.executive_signal_summary.task_mode
    assert result.operator_route_payload["route_profile"] == "continuity_standard"
    assert result.operator_route_payload["route_budget"]["allow_resume"] is True
    assert result.operator_route_payload["visible_burden_sensitivity"] == pytest.approx(
        result.executive_state.control_allocation.visible_burden_scale
    )


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
    assert resumed.closure_required is True
    assert resumed.closure_reason_tags == (
        "continuity_rejection",
        "continuity_reminder",
    )


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


def test_openai_runtime_step_latched_brake_requires_closure_even_when_product_decision_stays_continue(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        openai_runtime,
        "build_reference_executive_state",
        lambda *args, **kwargs: _reference_state(
            brake_state=BrakeState.LATCHED,
            uncertainty_levels=(("goal-progress", 0.1),),
            family_mask=frozenset(
                {
                    SoftControlFamily.NEUTRAL,
                    SoftControlFamily.CHECK,
                    SoftControlFamily.BRAKE,
                }
            ),
            top_family_set=frozenset({SoftControlFamily.NEUTRAL}),
            task_mode=kwargs.get("task_mode", OperatorTaskMode.EXECUTE),
        ),
    )

    result = run_openai_runtime_step(
        "response.output_text.delta",
        {
            "session_id": "oa-latched",
            "response_id": "resp-latched",
            "delta": "hello",
        },
        OpenAIRuntimeSession(session_id="oa-latched"),
    )

    assert result.product_decision.decision == "continue"
    assert result.closure_required is True
    assert result.closure_reason_tags == ("latched_brake",)
    assert result.session.next_recommended_move == "check"


def test_openai_runtime_step_blocked_route_remains_non_sovereign_and_surfaces_burden_diagnostics() -> None:
    result = run_openai_runtime_step(
        "response.completed",
        {
            "session_id": "oa-blocked-route",
            "response_id": "resp-blocked-route",
            "commitment_id": "oa-blocked-route-commit",
            "externally_consequential": True,
            "result_artifact_ref": "oa-blocked-route-artifact",
        },
        OpenAIRuntimeSession(session_id="oa-blocked-route"),
    )

    assert result.operator_route_payload["route_profile"] == "blocked"
    assert result.operator_route_payload["blocked_reason"] == (
        "blocked_by_modulator_stop_pressure"
    )
    assert result.operator_route_payload["visible_burden_sensitivity"] == pytest.approx(
        result.executive_state.control_allocation.visible_burden_scale
    )
    assert result.product_decision.as_summary() == {
        "decision": "check",
        "consequential_write_pending": True,
        "approval_required": True,
        "evidence_gap": False,
        "continuation_debt": False,
        "failure_class": None,
    }
    assert result.commitment_result_kind == "certified"


def test_openai_runtime_step_degradation_pressure_requires_closure_without_new_warning_strings() -> None:
    prior_session = OpenAIRuntimeSession(
        session_id="oa-degradation",
        feedback_window=openai_runtime.ReferenceRealizationFeedbackWindow(
            entries=(
                openai_runtime.ReferenceRealizationFeedback(
                    selected_family=SoftControlFamily.SEEK_CONTEXT,
                    realized_family=SoftControlFamily.CHECK,
                    brake_state=BrakeState.GUARDED,
                    warning_codes=("continuity-rejected:missing-resume-anchor:branch-a",),
                    host_friction_tags=(),
                ),
            )
        ),
        next_recommended_move="check",
    )

    result = run_openai_runtime_step(
        "response.output_text.delta",
        {
            "session_id": "oa-degradation",
            "response_id": "resp-degradation",
            "delta": "hello",
        },
        prior_session,
    )

    assert result.feedback_window_summary_payload["degradation_pressure_bonus"] == 2
    assert result.feedback_window_summary_payload["sustained_spike_flags"] == [
        "prior-continuity-rejection",
        "prior-enforcement-override",
        "sustained-feedback-disruption",
    ]
    assert result.closure_required is True
    assert result.closure_reason_tags == (
        "contradiction_spike",
        "degradation_pressure",
        "latched_brake",
    )
    assert result.warnings == ()


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
        "executive_modulator_memory": None,
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


def test_openai_runtime_verification_step_carries_executive_modulator_memory() -> None:
    contract = WorkContract(
        allowed_write_paths=("src/bookmarks_api/main.py",),
        verification_profile="python_workspace_pytest_v1",
        output_carrier="full_files",
        max_repair_turns=1,
    )
    updated = run_openai_runtime_verification_step(
        VerificationOutcome(
            status="passed",
            failure_class=None,
            parsed_paths=("src/bookmarks_api/main.py",),
            import_smoke_ok=True,
            pytest_ok=True,
            pytest_exit_code=0,
            pytest_passed=1,
            pytest_failed=0,
        ),
        OpenAIRuntimeSession(
            session_id="oa-verified-memory",
            executive_modulator_memory=ExecutiveModulatorMemory(
                focus_tonic=0.1,
                explore_tonic=0.2,
                stop_tonic=0.3,
                update_tonic=0.4,
            ),
        ),
        work_contract=contract,
        remaining_repairs=0,
    )

    assert updated.executive_modulator_memory == ExecutiveModulatorMemory(
        focus_tonic=0.1,
        explore_tonic=0.2,
        stop_tonic=0.3,
        update_tonic=0.4,
    )


def _reference_state(
    *,
    brake_state: BrakeState,
    uncertainty_levels: tuple[tuple[str, float], ...],
    family_mask: frozenset[SoftControlFamily],
    top_family_set: frozenset[SoftControlFamily],
    task_mode: OperatorTaskMode = OperatorTaskMode.EXECUTE,
) -> ReferenceExecutiveState:
    return ReferenceExecutiveState(
        goal_continuity=GoalContinuityView(active_track_ref="main"),
        uncertainty_monitoring=ReferenceUncertaintyMonitoringView(
            classwise_uncertainty=tuple(
                UncertaintyEstimate(class_tag=class_tag, level=level)
                for class_tag, level in uncertainty_levels
            ),
            contradiction_spike_flags=frozenset(),
        ),
        mode_and_gating=ReferenceModeAndGatingView(
            mode_tag="pass_through",
            task_mode=task_mode,
            family_mask=family_mask,
        ),
        control_allocation=ReferenceControlAllocationView(
            budget_band="low",
            top_family_set=top_family_set,
            host_friction_tags=frozenset(),
            feedback_pressure_tags=frozenset(),
        ),
        brake=ReferenceBrakeView(brake_state=brake_state),
    )
