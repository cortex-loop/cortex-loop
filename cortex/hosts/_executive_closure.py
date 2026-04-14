"""Shared host-side helpers for closure-shell runtime projection."""

from __future__ import annotations

from collections.abc import Sequence

from cortex.core.dispatch import DispatchDecision, DispatchLane
from cortex.sre.brake import BrakeState
from cortex.sre.executive_summary import ExecutiveSignalSummaryInputs
from cortex.sre.feedback import (
    ReferenceFeedbackWindowSummary,
    ReferenceRealizationFeedback,
    ReferenceRealizationFeedbackWindow,
)
from cortex.sre.goal_debt import build_closure_pressure_state
from cortex.sre.modulators import ExecutiveModulatorMemory
from cortex.sre.operator_routing import OperatorTaskMode, OperatorTaskState
from cortex.sre.state import ReferenceExecutiveState


def build_runtime_executive_signal_summary_inputs(
    *,
    task_mode: OperatorTaskMode,
    executive_state: ReferenceExecutiveState,
    dispatch_decision: DispatchDecision,
    active_track_ref: str,
    pending_goal_refs: tuple[str, ...],
    continuity_warnings: tuple[str, ...],
    continuity_reminders: tuple[str, ...],
    approval_required: bool,
    evidence_gap: bool,
    consequential_write_pending: bool,
    prior_failed_before_completion: bool,
    recent_product_failure_class: str | None,
    recent_probe_failure_class: str | None,
    recent_warning_bearing_success_present: bool,
    preservation_active: bool,
) -> ExecutiveSignalSummaryInputs:
    if not isinstance(task_mode, OperatorTaskMode):
        actual_type = type(task_mode).__name__
        raise TypeError(
            "build_runtime_executive_signal_summary_inputs.task_mode must be "
            f"OperatorTaskMode, got {actual_type}."
        )
    closure_pressure_state = build_closure_pressure_state(
        active_track_ref=active_track_ref,
        pending_goal_refs=pending_goal_refs,
        continuity_warnings=continuity_warnings,
        continuity_reminders=continuity_reminders,
        degradation_pressure_bonus=0,
        sustained_spike_flags=(),
        repeated_failure_pressure=(
            1.0 if prior_failed_before_completion else 0.35 if recent_warning_bearing_success_present else 0.0
        ),
        verification_conflict_pressure=1.0 if approval_required or evidence_gap or consequential_write_pending else 0.0,
        quota_pressure=quota_pressure_for_budget_band(
            executive_state.control_allocation.budget_band
        ),
        brake_state=executive_state.brake.brake_state,
    )
    return ExecutiveSignalSummaryInputs(
        task_mode=task_mode,
        uncertainty=max_uncertainty_level(executive_state),
        quota_pressure=quota_pressure_for_budget_band(
            executive_state.control_allocation.budget_band
        ),
        continuity_demand=max(
            continuity_demand(
                active_track_ref=active_track_ref,
                pending_goal_refs=pending_goal_refs,
                continuity_warnings=continuity_warnings,
                continuity_reminders=continuity_reminders,
            ),
            closure_pressure_state.goal_debt.unfinished_goal_debt,
        ),
        previous_same_host_run_failed_before_completion=prior_failed_before_completion,
        recent_product_failure_class=recent_product_failure_class,
        recent_probe_failure_class=recent_probe_failure_class,
        recent_warning_bearing_success_present=recent_warning_bearing_success_present,
        verification_required=(
            dispatch_decision.lane is not DispatchLane.CHEAP
            or approval_required
            or evidence_gap
            or consequential_write_pending
            or preservation_active
        ),
    )


def assert_runtime_posture_alignment(
    *,
    runtime_task_mode: OperatorTaskMode,
    executive_state: ReferenceExecutiveState,
    executive_signal_summary,
) -> None:
    from cortex.sre.executive_summary import ExecutiveSignalSummary

    if not isinstance(runtime_task_mode, OperatorTaskMode):
        actual_type = type(runtime_task_mode).__name__
        raise TypeError(
            "assert_runtime_posture_alignment.runtime_task_mode must be "
            f"OperatorTaskMode, got {actual_type}."
        )
    if not isinstance(executive_state, ReferenceExecutiveState):
        actual_type = type(executive_state).__name__
        raise TypeError(
            "assert_runtime_posture_alignment.executive_state must be "
            f"ReferenceExecutiveState, got {actual_type}."
        )
    if not isinstance(executive_signal_summary, ExecutiveSignalSummary):
        actual_type = type(executive_signal_summary).__name__
        raise TypeError(
            "assert_runtime_posture_alignment.executive_signal_summary must be "
            f"ExecutiveSignalSummary, got {actual_type}."
        )
    executive_task_mode = executive_state.mode_and_gating.task_mode
    summary_task_mode = executive_signal_summary.task_mode
    public_posture = public_posture_for_task_mode(runtime_task_mode)
    if executive_task_mode is not runtime_task_mode:
        raise ValueError(
            "runtime posture drift: executive_state.mode_and_gating.task_mode "
            f"{executive_task_mode.value!r} != runtime_task_mode {runtime_task_mode.value!r}."
        )
    if summary_task_mode is not runtime_task_mode:
        raise ValueError(
            "runtime posture drift: executive_signal_summary.task_mode "
            f"{summary_task_mode.value!r} != runtime_task_mode {runtime_task_mode.value!r}."
        )
    if public_posture_for_task_mode(executive_task_mode) != public_posture:
        raise ValueError(
            "runtime posture drift: executive_state public posture "
            f"{public_posture_for_task_mode(executive_task_mode)!r} != runtime public posture {public_posture!r}."
        )
    if public_posture_for_task_mode(summary_task_mode) != public_posture:
        raise ValueError(
            "runtime posture drift: executive_signal_summary public posture "
            f"{public_posture_for_task_mode(summary_task_mode)!r} != runtime public posture {public_posture!r}."
        )


def task_mode_for_runtime(
    *,
    dispatch_decision: DispatchDecision,
    active_track_ref: str,
    pending_goal_refs: tuple[str, ...],
    continuity_warnings: tuple[str, ...],
    continuity_reminders: tuple[str, ...],
    approval_required: bool,
    evidence_gap: bool,
    consequential_write_pending: bool,
    preservation_active: bool,
) -> OperatorTaskMode:
    if (
        active_track_ref != "main"
        or pending_goal_refs
        or continuity_reminders
        or _has_continuity_rejection(continuity_warnings)
    ):
        return OperatorTaskMode.RESUME_EXECUTE
    if (
        dispatch_decision.lane is DispatchLane.CHEAP
        and not approval_required
        and not evidence_gap
        and not consequential_write_pending
        and not preservation_active
    ):
        return OperatorTaskMode.INSPECT
    return OperatorTaskMode.EXECUTE


def public_posture_for_task_mode(task_mode: OperatorTaskMode) -> str:
    if not isinstance(task_mode, OperatorTaskMode):
        actual_type = type(task_mode).__name__
        raise TypeError(
            "public_posture_for_task_mode.task_mode must be OperatorTaskMode, "
            f"got {actual_type}."
        )
    if task_mode is OperatorTaskMode.RESUME_EXECUTE:
        return "resume"
    return task_mode.value


def max_uncertainty_level(executive_state: ReferenceExecutiveState) -> float:
    return max(
        (
            float(estimate.level)
            for estimate in executive_state.uncertainty_monitoring.classwise_uncertainty
        ),
        default=0.0,
    )


def quota_pressure_for_budget_band(budget_band: str) -> float:
    if budget_band == "low":
        return 0.25
    if budget_band == "medium":
        return 0.50
    return 0.75


def continuity_demand(
    *,
    active_track_ref: str,
    pending_goal_refs: tuple[str, ...],
    continuity_warnings: tuple[str, ...],
    continuity_reminders: tuple[str, ...],
) -> float:
    if (
        pending_goal_refs
        or continuity_reminders
        or _has_continuity_rejection(continuity_warnings)
    ):
        return 1.0
    if active_track_ref != "main":
        return 0.7
    return 0.0


def build_runtime_operator_task_state(
    *,
    summary_inputs: ExecutiveSignalSummaryInputs,
    executive_state: ReferenceExecutiveState,
) -> OperatorTaskState:
    if not isinstance(summary_inputs, ExecutiveSignalSummaryInputs):
        actual_type = type(summary_inputs).__name__
        raise TypeError(
            "build_runtime_operator_task_state.summary_inputs must be "
            f"ExecutiveSignalSummaryInputs, got {actual_type}."
        )
    if not isinstance(executive_state, ReferenceExecutiveState):
        actual_type = type(executive_state).__name__
        raise TypeError(
            "build_runtime_operator_task_state.executive_state must be "
            f"ReferenceExecutiveState, got {actual_type}."
        )
    return OperatorTaskState(
        task_mode=summary_inputs.task_mode,
        complexity=_route_complexity_for_task_mode(summary_inputs.task_mode),
        continuity_demand=float(summary_inputs.continuity_demand),
        verification_demand=0.8 if summary_inputs.verification_required else 0.0,
        uncertainty=float(summary_inputs.uncertainty),
        host_friction=float(executive_state.control_allocation.host_friction_level),
        quota_pressure=float(summary_inputs.quota_pressure),
        visible_burden_sensitivity=float(
            executive_state.control_allocation.visible_burden_scale
        ),
    )


def recent_warning_bearing_success_present(
    feedback_window: ReferenceRealizationFeedbackWindow,
    *,
    failed_before_completion: bool,
) -> bool:
    latest_feedback = feedback_window.entries[-1] if feedback_window.entries else None
    return bool(
        latest_feedback is not None
        and latest_feedback.warning_codes
        and not failed_before_completion
    )


def closure_reason_tags(
    *,
    active_track_ref: str = "main",
    warnings: tuple[str, ...],
    continuity_reminders: tuple[str, ...],
    brake_state: BrakeState,
    feedback_window_summary: ReferenceFeedbackWindowSummary,
    pending_goal_refs: tuple[str, ...],
) -> tuple[str, ...]:
    return build_closure_pressure_state(
        active_track_ref=active_track_ref,
        pending_goal_refs=pending_goal_refs,
        continuity_warnings=warnings,
        continuity_reminders=continuity_reminders,
        degradation_pressure_bonus=feedback_window_summary.degradation_pressure_bonus,
        sustained_spike_flags=feedback_window_summary.sustained_spike_flags,
        repeated_failure_pressure=0.35 if feedback_window_summary.degradation_pressure_bonus > 0 else 0.0,
        verification_conflict_pressure=0.0,
        quota_pressure=0.0,
        brake_state=brake_state,
    ).closure_reason_tags


def recent_probe_failure_class(
    feedback_window: ReferenceRealizationFeedbackWindow,
) -> str | None:
    latest = _latest_probe_feedback(feedback_window)
    if latest is None:
        return None
    if latest.probe_result_class == "succeeded":
        return None
    return latest.probe_result_class


def verification_state_for_runtime(
    *,
    dispatch_decision: DispatchDecision,
    commitment_result_kind: str | None,
) -> str:
    if commitment_result_kind is not None:
        return "completed"
    if dispatch_decision.lane is DispatchLane.CHEAP:
        return "not-required"
    return "required"


def canonicalize_executive_modulator_memory(
    memory: ExecutiveModulatorMemory | None,
) -> ExecutiveModulatorMemory | None:
    if memory is None:
        return None
    payload = memory.as_payload()
    return ExecutiveModulatorMemory(
        focus_tonic=payload["focus_tonic"],
        explore_tonic=payload["explore_tonic"],
        stop_tonic=payload["stop_tonic"],
        update_tonic=payload["update_tonic"],
    )


def executive_modulator_memory_payload(
    memory: ExecutiveModulatorMemory,
) -> dict[str, float]:
    canonical_memory = canonicalize_executive_modulator_memory(memory)
    assert canonical_memory is not None
    return canonical_memory.as_payload()


def _has_continuity_rejection(warnings: Sequence[str]) -> bool:
    return any(warning.startswith("continuity-rejected:") for warning in warnings)


def _route_complexity_for_task_mode(task_mode: OperatorTaskMode) -> float:
    if task_mode is OperatorTaskMode.INSPECT:
        return 0.20
    if task_mode is OperatorTaskMode.RESUME_EXECUTE:
        return 0.55
    return 0.45


def _latest_probe_feedback(
    feedback_window: ReferenceRealizationFeedbackWindow,
) -> ReferenceRealizationFeedback | None:
    for feedback in reversed(feedback_window.entries):
        if feedback.probe_result_class is not None:
            return feedback
    return None


__all__ = [
    "assert_runtime_posture_alignment",
    "build_runtime_operator_task_state",
    "build_runtime_executive_signal_summary_inputs",
    "canonicalize_executive_modulator_memory",
    "closure_reason_tags",
    "continuity_demand",
    "executive_modulator_memory_payload",
    "max_uncertainty_level",
    "public_posture_for_task_mode",
    "quota_pressure_for_budget_band",
    "recent_probe_failure_class",
    "recent_warning_bearing_success_present",
    "task_mode_for_runtime",
    "verification_state_for_runtime",
]
