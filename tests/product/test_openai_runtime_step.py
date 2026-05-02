"""Focused tests for direct OpenAI runtime-step behavior."""

from __future__ import annotations

from dataclasses import replace

import cortex.aux.distillation as aux_distillation
import cortex.aux.persistence as aux_persistence
import cortex.aux.publication as aux_publication
import cortex.aux.support_priors as aux_support_priors
from cortex.hosts._executive_closure import (
    probe_result_class_for_runtime,
    public_posture_for_task_mode,
    task_mode_for_runtime,
)
import pytest

import cortex.hosts.openai.runtime as openai_runtime
from cortex.aux.reference_replay import evaluate_aux_reference_q_mem_replay
from cortex.core.envelopes import MetadataField
from cortex.hosts.openai.runtime import (
    OpenAIRuntimeSession,
    run_openai_runtime_step,
    run_openai_runtime_verification_step,
)
from cortex.sre.brake import BrakeState
from cortex.sre.goals import GoalContinuityView
from cortex.sre.executive_summary import ExecutiveSignalSummary
from cortex.sre.families import SoftControlFamily
from cortex.sre.feedback import (
    ReferenceRealizationFeedback,
    ReferenceRealizationFeedbackWindow,
)
from cortex.sre.modulators import ExecutiveModulatorMemory
from cortex.sre.opportunities import BoundedProbeContract, HostNativeOpportunity
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
from tests.experimental._aux_test_support import (
    make_aux_reference_replay_corpus,
    make_support_snapshot,
)


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
    assert (
        result.control_ledger_summary["allocation_diagnostics"]["probe_result_class"]
        == "unsupported"
    )
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
        "probe_result_class": "unsupported",
        "probe_unavailable_reason": "documented-probe-surface-unavailable",
    }
    assert result.feedback_window_summary_payload == {
        "window_size": 1,
        "rejection_count": 0,
        "override_count": 0,
        "latched_count": 0,
        "clean_success_streak": 0,
        "evidence_state_move_count": 1,
        "meaningful_evidence_progress_count": 1,
        "stream_only_progress_count": 0,
        "continuity_improvement_count": 0,
        "family_change_without_evidence_count": 0,
        "same_family_no_progress_count": 0,
        "same_context_retry_count": 0,
        "goal_progress_floor": 0.0,
        "degradation_pressure_bonus": 0,
        "recent_evidence_progress_class": "commitment",
        "recent_continuity_progress_class": "none",
        "sustained_spike_flags": [],
    }
    assert (
        result.feedback_window_summary_payload["recent_evidence_progress_class"]
        == result.journal["last_realization_feedback"]["evidence_progress_class"]
    )
    assert (
        result.feedback_window_summary_payload["recent_continuity_progress_class"]
        == result.journal["last_realization_feedback"]["continuity_progress_class"]
    )
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
            "evidence_progress_class": "commitment",
            "evidence_state_moved": True,
            "continuity_progress_class": "none",
            "continuity_improved": False,
            "probe_result_class": "unsupported",
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
                "evidence_progress_class": "commitment",
                "evidence_state_moved": True,
                "continuity_progress_class": "none",
                "continuity_improved": False,
                "probe_result_class": "unsupported",
            }
        ],
        "expectation_ledger": {
            "active": [],
            "resolved": [
                {
                    "expectation_id": "openai:1:verification:expectation",
                    "commitment_id": "openai:1:verification",
                    "weight": 1.0,
                    "horizon": "immediate",
                    "satisfaction_classes": [
                        "meaningful_evidence",
                        "commitment_certified",
                        "liability_retracted",
                        "blocker_surfaced",
                    ],
                    "opened_at_step": 1,
                    "due_at_step": 1,
                    "suspension_state": "fulfilled",
                    "remaining_weight": 0.0,
                    "evidence_refs": ["openai:1"],
                    "deficit_kind": "verification",
                    "resolution_class": "commitment_certified",
                }
            ],
        },
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
    assert (
        result.control_ledger_summary["allocation_diagnostics"]["probe_result_class"]
        == "unsupported"
    )
    assert result.control_ledger_summary["audit_projection"]["probe_path_state"] == (
        "unavailable"
    )
    assert result.control_ledger_summary["audit_projection"]["probe_result_class"] == "unsupported"
    assert result.feedback_window_summary_payload["window_size"] == 1
    assert (
        result.feedback_window_summary_payload["recent_evidence_progress_class"]
        == "token-stream"
    )
    assert (
        result.feedback_window_summary_payload["recent_continuity_progress_class"]
        == "none"
    )
    assert (
        result.feedback_window_summary_payload["recent_evidence_progress_class"]
        == result.journal["last_realization_feedback"]["evidence_progress_class"]
    )


def test_probe_result_class_for_runtime_scopes_unsupported_to_realized_family_reason() -> None:
    executive_state = replace(
        _reference_state(
            brake_state=BrakeState.GUARDED,
            uncertainty_levels=(("environment", 0.6),),
            family_mask=frozenset(
                {
                    SoftControlFamily.NEUTRAL,
                    SoftControlFamily.CHECK,
                    SoftControlFamily.SEEK_CONTEXT,
                    SoftControlFamily.BRAKE,
                }
            ),
            top_family_set=frozenset(
                {
                    SoftControlFamily.NEUTRAL,
                    SoftControlFamily.CHECK,
                    SoftControlFamily.SEEK_CONTEXT,
                }
            ),
            task_mode=OperatorTaskMode.INSPECT,
        ),
        control_allocation=replace(
            _reference_state(
                brake_state=BrakeState.GUARDED,
                uncertainty_levels=(("environment", 0.6),),
                family_mask=frozenset(
                    {
                        SoftControlFamily.NEUTRAL,
                        SoftControlFamily.CHECK,
                        SoftControlFamily.SEEK_CONTEXT,
                        SoftControlFamily.BRAKE,
                    }
                ),
                top_family_set=frozenset(
                    {
                        SoftControlFamily.NEUTRAL,
                        SoftControlFamily.CHECK,
                        SoftControlFamily.SEEK_CONTEXT,
                    }
                ),
                task_mode=OperatorTaskMode.INSPECT,
            ).control_allocation,
            probe_path_state="unavailable",
            probe_unavailable_reason="documented-probe-surface-unavailable",
        ),
    )
    opportunities = (
        HostNativeOpportunity(
            opportunity_ref="probe.check.unsupported",
            supported_families=frozenset({SoftControlFamily.CHECK}),
            realizable=False,
            degradation_reason="documented-probe-surface-unavailable",
            safer_fallback_family=SoftControlFamily.NEUTRAL,
            probe_contract=BoundedProbeContract(
                uncertainty_target="environment",
                allowed_family=SoftControlFamily.CHECK,
                timeout_seconds=2,
                output_cap=64,
                failure_classes=frozenset({"unsupported"}),
            ),
        ),
        HostNativeOpportunity(
            opportunity_ref="probe.seek-context.other",
            supported_families=frozenset({SoftControlFamily.SEEK_CONTEXT}),
            realizable=False,
            degradation_reason="host-capability-probe-unavailable",
            safer_fallback_family=SoftControlFamily.NEUTRAL,
            probe_contract=BoundedProbeContract(
                uncertainty_target="host-capability",
                allowed_family=SoftControlFamily.SEEK_CONTEXT,
                timeout_seconds=5,
                output_cap=128,
                failure_classes=frozenset({"unsupported"}),
            ),
        ),
    )

    assert (
        probe_result_class_for_runtime(
            realized_family=SoftControlFamily.SEEK_CONTEXT,
            executive_state=executive_state,
            opportunities=opportunities,
        )
        is None
    )
    assert (
        probe_result_class_for_runtime(
            realized_family=SoftControlFamily.CHECK,
            executive_state=executive_state,
            opportunities=opportunities,
        )
        == "unsupported"
    )


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
        "prior-non-productive-family-switch",
    ]
    assert result.closure_required is True
    assert result.closure_reason_tags == (
        "contradiction_spike",
        "degradation_pressure",
        "latched_brake",
    )
    assert result.warnings == ()


def test_openai_runtime_step_without_offline_publication_makes_no_aux_calls_and_keeps_memory_priors_absent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_select = openai_runtime.select_reference_soft_control
    captured: dict[str, object] = {}

    def forbidden_augment(*args, **kwargs):
        raise AssertionError("AUX augmentation should stay inactive without explicit offline publication.")

    def forbidden_prior_builder(*args, **kwargs):
        raise AssertionError("AUX memory priors should stay inactive without explicit offline publication.")

    def forbidden_filter(*args, **kwargs):
        raise AssertionError("Live support-memory filtering should stay inactive without explicit offline publication.")

    def forbidden_distill(*args, **kwargs):
        raise AssertionError("OpenAI runtime must not call AUX distillation on the default path.")

    class ForbiddenStore:
        def __init__(self, *args, **kwargs) -> None:
            raise AssertionError(
                "OpenAI runtime must not instantiate SqliteSupportMemoryStore on the default path."
            )

    def select_wrapper(executive_state, *args, **kwargs):
        captured["selection_memory_priors"] = kwargs.get("memory_priors")
        return original_select(executive_state, *args, **kwargs)

    monkeypatch.setattr(aux_publication, "augment_snapshot_with_offline_publication", forbidden_augment)
    monkeypatch.setattr(aux_support_priors, "build_support_memory_prior_appendix", forbidden_prior_builder)
    monkeypatch.setattr(aux_support_priors, "filter_live_support_memory_prior_appendix", forbidden_filter)
    monkeypatch.setattr(aux_distillation, "distill_offline_support_publication", forbidden_distill)
    monkeypatch.setattr(aux_persistence, "SqliteSupportMemoryStore", ForbiddenStore)
    monkeypatch.setattr(openai_runtime, "select_reference_soft_control", select_wrapper)

    result = run_openai_runtime_step(
        "response.output_text.delta",
        {
            "session_id": "oa-default-memory-off",
            "response_id": "resp-default-memory-off",
            "delta": "hello",
        },
    )

    assert captured["selection_memory_priors"] is None
    assert result.control_ledger_summary["allocation_diagnostics"]["memory_reentry"] == {
        "state": "inactive",
        "source_host_name": None,
        "target_host_name": "openai",
        "eligible_families": [],
        "invalidated_families": [],
        "selected_family_support_refs": [],
        "selected_family_memory_score": 0.0,
        "selected_family_reliability_delta": 0.0,
    }
    assert all(
        score["memory_score"] == 0.0
        for score in result.control_ledger_summary["allocation_diagnostics"]["scores"]
    )


def test_openai_runtime_step_replay_publication_can_lift_branch_allocation_without_default_behavior_change(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case_result = _openai_replay_case_result("branch-resume-recovery")
    scenario = _reference_replay_scenario("branch-resume-recovery")
    monkeypatch.setattr(
        openai_runtime,
        "build_reference_executive_state",
        lambda *args, **kwargs: _scenario_executive_state_with_task_mode(
            scenario,
            kwargs["task_mode"],
        ),
    )
    monkeypatch.setattr(
        openai_runtime,
        "_build_support_snapshot",
        lambda **kwargs: scenario.target_snapshot,
    )

    baseline = run_openai_runtime_step(
        "response.output_text.delta",
        {"session_id": "oa-replay-branch", "response_id": "resp-replay-branch", "delta": "hello"},
    )
    replay = run_openai_runtime_step(
        "response.output_text.delta",
        {"session_id": "oa-replay-branch", "response_id": "resp-replay-branch", "delta": "hello"},
        offline_publication=case_result.publication,
    )

    baseline_branch = _score_payload_for_family(
        baseline.control_ledger_summary["allocation_diagnostics"]["scores"],
        "branch",
    )
    replay_branch = _score_payload_for_family(
        replay.control_ledger_summary["allocation_diagnostics"]["scores"],
        "branch",
    )
    assert baseline_branch["memory_score"] == 0.0
    assert replay_branch["memory_score"] > 0.0
    assert replay_branch["allocated_score"] > baseline_branch["allocated_score"]
    memory_reentry = replay.control_ledger_summary["allocation_diagnostics"]["memory_reentry"]
    assert memory_reentry["state"] == "active"
    assert memory_reentry["source_host_name"] == "openai"
    assert memory_reentry["target_host_name"] == "openai"
    assert memory_reentry["eligible_families"] == [
        "check",
        "seek-context",
        "branch",
        "redirect",
    ]
    assert memory_reentry["invalidated_families"] == []
    assert memory_reentry["selected_family_support_refs"] == [
        {"reference_kind": "branch", "reference_id": "review-track"},
        {"reference_kind": "memory", "reference_id": "review-track-memo"},
        {"reference_kind": "memory", "reference_id": "review-track-goal-memo"},
    ]
    assert memory_reentry["selected_family_memory_score"] == pytest.approx(
        replay_branch["memory_score"]
    )


def test_openai_runtime_step_replay_publication_blocks_cross_host_live_memory_reentry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case_result = _reference_replay_case_result("branch-resume-recovery")
    scenario = _reference_replay_scenario("branch-resume-recovery")
    monkeypatch.setattr(
        openai_runtime,
        "build_reference_executive_state",
        lambda *args, **kwargs: _scenario_executive_state_with_task_mode(
            scenario,
            kwargs["task_mode"],
        ),
    )
    monkeypatch.setattr(
        openai_runtime,
        "_build_support_snapshot",
        lambda **kwargs: scenario.target_snapshot,
    )

    replay = run_openai_runtime_step(
        "response.output_text.delta",
        {
            "session_id": "oa-replay-host-mismatch",
            "response_id": "resp-replay-host-mismatch",
            "delta": "hello",
        },
        offline_publication=_publication_for_host(case_result.publication, "claude"),
    )

    branch_score = _score_payload_for_family(
        replay.control_ledger_summary["allocation_diagnostics"]["scores"],
        "branch",
    )
    assert branch_score["memory_score"] == 0.0
    assert replay.control_ledger_summary["allocation_diagnostics"]["memory_reentry"] == {
        "state": "host-mismatch",
        "source_host_name": "claude",
        "target_host_name": "openai",
        "eligible_families": ["check", "seek-context", "branch", "redirect"],
        "invalidated_families": ["branch", "check", "redirect", "seek-context"],
        "selected_family_support_refs": [],
        "selected_family_memory_score": 0.0,
        "selected_family_reliability_delta": 0.0,
    }


def test_openai_runtime_step_live_memory_reentry_invalidates_resume_context_families_when_fresh_contradiction_overlaps_resume_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case_result = _openai_replay_case_result("branch-resume-recovery")
    scenario = _reference_replay_scenario("branch-resume-recovery")
    contradiction_snapshot = replace(
        scenario.target_snapshot,
        trace=replace(
            scenario.target_snapshot.trace,
            degradation_records=make_support_snapshot().trace.degradation_records,
        ),
    )
    monkeypatch.setattr(
        openai_runtime,
        "build_reference_executive_state",
        lambda *args, **kwargs: _scenario_executive_state_with_task_mode(
            scenario,
            kwargs["task_mode"],
        ),
    )
    monkeypatch.setattr(
        openai_runtime,
        "_build_support_snapshot",
        lambda **kwargs: contradiction_snapshot,
    )

    replay = run_openai_runtime_step(
        "response.output_text.delta",
        {
            "session_id": "oa-replay-branch-contradiction",
            "response_id": "resp-replay-branch-contradiction",
            "delta": "hello",
        },
        offline_publication=case_result.publication,
    )

    branch_score = _score_payload_for_family(
        replay.control_ledger_summary["allocation_diagnostics"]["scores"],
        "branch",
    )
    redirect_score = _score_payload_for_family(
        replay.control_ledger_summary["allocation_diagnostics"]["scores"],
        "redirect",
    )
    assert branch_score["memory_score"] == 0.0
    assert redirect_score["memory_score"] == 0.0
    assert replay.control_ledger_summary["allocation_diagnostics"]["memory_reentry"][
        "invalidated_families"
    ] == ["branch", "redirect"]


def test_openai_runtime_step_live_memory_reentry_zeroes_ttl_expired_branch_family_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case_result = _openai_replay_case_result("branch-resume-recovery")
    scenario = _reference_replay_scenario("branch-resume-recovery")
    assert case_result.publication.host_reliability_prior is not None
    expired_prior = replace(
        case_result.publication.host_reliability_prior,
        ttl_hours=1,
        last_validated_at="2000-01-01T00:00:00+00:00",
    )
    publication = replace(
        case_result.publication,
        host_reliability_prior=expired_prior,
    )
    monkeypatch.setattr(
        openai_runtime,
        "build_reference_executive_state",
        lambda *args, **kwargs: _scenario_executive_state_with_task_mode(
            scenario,
            kwargs["task_mode"],
        ),
    )
    monkeypatch.setattr(
        openai_runtime,
        "_build_support_snapshot",
        lambda **kwargs: scenario.target_snapshot,
    )

    replay = run_openai_runtime_step(
        "response.output_text.delta",
        {"session_id": "oa-replay-ttl", "response_id": "resp-replay-ttl", "delta": "hello"},
        offline_publication=publication,
    )

    branch_score = _score_payload_for_family(
        replay.control_ledger_summary["allocation_diagnostics"]["scores"],
        "branch",
    )
    redirect_score = _score_payload_for_family(
        replay.control_ledger_summary["allocation_diagnostics"]["scores"],
        "redirect",
    )
    assert branch_score["memory_score"] == 0.0
    assert redirect_score["memory_score"] > 0.0
    assert replay.control_ledger_summary["allocation_diagnostics"]["memory_reentry"][
        "invalidated_families"
    ] == ["branch", "seek-context"]
    memory_reentry = replay.control_ledger_summary["allocation_diagnostics"]["memory_reentry"]
    assert memory_reentry["selected_family_reliability_delta"] == 0.0


def test_openai_runtime_step_publication_carried_reliability_prior_lifts_selected_family_delta(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case_result = _openai_replay_case_result("branch-resume-recovery")
    scenario = _reference_replay_scenario("branch-resume-recovery")
    assert case_result.publication.host_reliability_prior is not None
    monkeypatch.setattr(
        openai_runtime,
        "build_reference_executive_state",
        lambda *args, **kwargs: _scenario_executive_state_with_task_mode(
            scenario,
            kwargs["task_mode"],
        ),
    )
    monkeypatch.setattr(
        openai_runtime,
        "_build_support_snapshot",
        lambda **kwargs: scenario.target_snapshot,
    )

    replay = run_openai_runtime_step(
        "response.output_text.delta",
        {
            "session_id": "oa-reliability-delta-active",
            "response_id": "resp-reliability-delta-active",
            "delta": "hello",
        },
        offline_publication=case_result.publication,
    )

    assert replay.selected_family is SoftControlFamily.BRANCH
    memory_reentry = replay.control_ledger_summary["allocation_diagnostics"]["memory_reentry"]
    assert memory_reentry["state"] == "active"
    assert memory_reentry["selected_family_reliability_delta"] > 0.0
    branch_score = _score_payload_for_family(
        replay.control_ledger_summary["allocation_diagnostics"]["scores"],
        "branch",
    )
    assert "q_mem-host:reliability-active" in branch_score["reason_tags"]


def test_openai_runtime_step_without_publication_keeps_reliability_delta_zero() -> None:
    result = run_openai_runtime_step(
        "response.output_text.delta",
        {
            "session_id": "oa-no-publication-delta",
            "response_id": "resp-no-publication-delta",
            "delta": "hello",
        },
    )

    memory_reentry = result.control_ledger_summary["allocation_diagnostics"]["memory_reentry"]
    assert memory_reentry["state"] == "inactive"
    assert memory_reentry["selected_family_reliability_delta"] == 0.0


def test_openai_runtime_step_affordance_mismatch_zeros_reliability_delta_on_seek_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case_result = _openai_replay_case_result("retrieval-reuse")
    scenario = _reference_replay_scenario("retrieval-reuse")
    assert case_result.publication.host_reliability_prior is not None
    disjoint_prior = replace(
        case_result.publication.host_reliability_prior,
        affordance_scope_tags=("restricted-op",),
    )
    publication = replace(
        case_result.publication,
        host_reliability_prior=disjoint_prior,
    )
    monkeypatch.setattr(
        openai_runtime,
        "build_reference_executive_state",
        lambda *args, **kwargs: _scenario_executive_state_with_task_mode(
            scenario,
            kwargs["task_mode"],
        ),
    )
    monkeypatch.setattr(
        openai_runtime,
        "_build_support_snapshot",
        lambda **kwargs: scenario.target_snapshot,
    )

    replay = run_openai_runtime_step(
        "response.output_text.delta",
        {
            "session_id": "oa-reliability-affordance-mismatch",
            "response_id": "resp-reliability-affordance-mismatch",
            "delta": "hello",
        },
        offline_publication=publication,
    )

    memory_reentry = replay.control_ledger_summary["allocation_diagnostics"]["memory_reentry"]
    assert memory_reentry["selected_family_reliability_delta"] == 0.0
    seek_score = _score_payload_for_family(
        replay.control_ledger_summary["allocation_diagnostics"]["scores"],
        "seek-context",
    )
    assert "q_mem-host:affordance-mismatch" in seek_score["reason_tags"]
    assert "q_mem-host:reliability-active" not in seek_score["reason_tags"]


def test_openai_runtime_step_live_memory_reentry_invalidates_uncertainty_families_after_probe_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case_result = _openai_replay_case_result("uncertainty-brake-calibration")
    scenario = _reference_replay_scenario("uncertainty-brake-calibration")
    monkeypatch.setattr(
        openai_runtime,
        "build_reference_executive_state",
        lambda *args, **kwargs: _scenario_executive_state_with_task_mode(
            scenario,
            kwargs["task_mode"],
        ),
    )
    monkeypatch.setattr(
        openai_runtime,
        "_build_support_snapshot",
        lambda **kwargs: scenario.target_snapshot,
    )

    replay = run_openai_runtime_step(
        "response.output_text.delta",
        {
            "session_id": "oa-replay-probe-failure",
            "response_id": "resp-replay-probe-failure",
            "delta": "hello",
        },
        OpenAIRuntimeSession(
            session_id="oa-replay-probe-failure",
            feedback_window=ReferenceRealizationFeedbackWindow(
                entries=(
                    ReferenceRealizationFeedback(
                        selected_family=SoftControlFamily.CHECK,
                        realized_family=SoftControlFamily.CHECK,
                        brake_state=BrakeState.GUARDED,
                        probe_result_class="timed-out",
                    ),
                )
            ),
        ),
        offline_publication=case_result.publication,
    )

    check_score = _score_payload_for_family(
        replay.control_ledger_summary["allocation_diagnostics"]["scores"],
        "check",
    )
    seek_context_score = _score_payload_for_family(
        replay.control_ledger_summary["allocation_diagnostics"]["scores"],
        "seek-context",
    )
    assert check_score["memory_score"] == 0.0
    assert seek_context_score["memory_score"] == 0.0
    assert replay.control_ledger_summary["allocation_diagnostics"]["memory_reentry"][
        "invalidated_families"
    ] == ["check", "seek-context"]


def test_openai_runtime_step_with_explicit_publication_stays_publication_only_without_persistence_or_distillation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case_result = _openai_replay_case_result("branch-resume-recovery")
    scenario = _reference_replay_scenario("branch-resume-recovery")
    original_augment = aux_publication.augment_snapshot_with_offline_publication
    original_prior_builder = aux_support_priors.build_support_memory_prior_appendix
    original_filter = aux_support_priors.filter_live_support_memory_prior_appendix
    captured: dict[str, bool] = {
        "augment_called": False,
        "prior_builder_called": False,
        "filter_called": False,
    }

    def augment_wrapper(snapshot, publication):
        captured["augment_called"] = True
        return original_augment(snapshot, publication)

    def prior_builder_wrapper(snapshot, **kwargs):
        captured["prior_builder_called"] = True
        return original_prior_builder(snapshot, **kwargs)

    def filter_wrapper(snapshot, appendix, **kwargs):
        captured["filter_called"] = True
        return original_filter(snapshot, appendix, **kwargs)

    def forbidden_distill(*args, **kwargs):
        raise AssertionError(
            "OpenAI runtime live memory re-entry must not call AUX distillation on the runtime path."
        )

    class ForbiddenStore:
        def __init__(self, *args, **kwargs) -> None:
            raise AssertionError(
                "OpenAI runtime live memory re-entry must not instantiate SqliteSupportMemoryStore on the runtime path."
            )

    monkeypatch.setattr(
        openai_runtime,
        "build_reference_executive_state",
        lambda *args, **kwargs: _scenario_executive_state_with_task_mode(
            scenario,
            kwargs["task_mode"],
        ),
    )
    monkeypatch.setattr(
        openai_runtime,
        "_build_support_snapshot",
        lambda **kwargs: scenario.target_snapshot,
    )
    monkeypatch.setattr(aux_publication, "augment_snapshot_with_offline_publication", augment_wrapper)
    monkeypatch.setattr(aux_support_priors, "build_support_memory_prior_appendix", prior_builder_wrapper)
    monkeypatch.setattr(aux_support_priors, "filter_live_support_memory_prior_appendix", filter_wrapper)
    monkeypatch.setattr(aux_distillation, "distill_offline_support_publication", forbidden_distill)
    monkeypatch.setattr(aux_persistence, "SqliteSupportMemoryStore", ForbiddenStore)

    replay = run_openai_runtime_step(
        "response.output_text.delta",
        {
            "session_id": "oa-replay-publication-only",
            "response_id": "resp-replay-publication-only",
            "delta": "hello",
        },
        offline_publication=case_result.publication,
    )

    assert captured == {
        "augment_called": True,
        "prior_builder_called": True,
        "filter_called": True,
    }
    assert replay.control_ledger_summary["allocation_diagnostics"]["memory_reentry"][
        "state"
    ] == "active"


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
        "expectation_ledger": {"active": [], "resolved": []},
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


def _publication_for_host(publication, host_name: str):
    return replace(
        publication,
        metadata=tuple(
            MetadataField("host_name", host_name) if field.key == "host_name" else field
            for field in publication.metadata
        ),
    )


def _reference_replay_scenario(scenario_id: str):
    for scenario in make_aux_reference_replay_corpus():
        if scenario.scenario_id == scenario_id:
            return scenario
    raise KeyError(f"Unknown replay scenario {scenario_id!r}.")


def _reference_replay_case_result(scenario_id: str):
    scenario = _reference_replay_scenario(scenario_id)
    return evaluate_aux_reference_q_mem_replay((scenario,)).case_results[0]


def _openai_replay_case_result(scenario_id: str):
    case_result = _reference_replay_case_result(scenario_id)
    return replace(
        case_result,
        publication=_publication_for_host(case_result.publication, "openai"),
    )


def _scenario_executive_state_with_task_mode(
    scenario,
    task_mode: OperatorTaskMode,
) -> ReferenceExecutiveState:
    return replace(
        scenario.executive_state,
        mode_and_gating=replace(
            scenario.executive_state.mode_and_gating,
            task_mode=task_mode,
        ),
    )


def _score_payload_for_family(
    scores: list[dict[str, object]],
    family: str,
) -> dict[str, object]:
    for score in scores:
        if score["family"] == family:
            return score
    raise AssertionError(f"Missing allocation score for family {family!r}.")
