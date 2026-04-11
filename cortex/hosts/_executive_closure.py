"""Shared host-side helpers for closure-shell runtime projection."""

from __future__ import annotations

from collections.abc import Sequence

from cortex.core.dispatch import DispatchDecision, DispatchLane
from cortex.sre.brake import BrakeState
from cortex.sre.executive_summary import ExecutiveSignalSummaryInputs
from cortex.sre.feedback import (
    ReferenceFeedbackWindowSummary,
    ReferenceRealizationFeedbackWindow,
)
from cortex.sre.modulators import ExecutiveModulatorMemory
from cortex.sre.operator_routing import OperatorTaskMode
from cortex.sre.state import ReferenceExecutiveState


def build_runtime_executive_signal_summary_inputs(
    *,
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
    recent_warning_bearing_success_present: bool,
    preservation_active: bool,
) -> ExecutiveSignalSummaryInputs:
    return ExecutiveSignalSummaryInputs(
        task_mode=task_mode_for_runtime(
            active_track_ref=active_track_ref,
            pending_goal_refs=pending_goal_refs,
            continuity_warnings=continuity_warnings,
            continuity_reminders=continuity_reminders,
        ),
        uncertainty=max_uncertainty_level(executive_state),
        quota_pressure=quota_pressure_for_budget_band(
            executive_state.control_allocation.budget_band
        ),
        continuity_demand=continuity_demand(
            active_track_ref=active_track_ref,
            pending_goal_refs=pending_goal_refs,
            continuity_warnings=continuity_warnings,
            continuity_reminders=continuity_reminders,
        ),
        previous_same_host_run_failed_before_completion=prior_failed_before_completion,
        recent_product_failure_class=recent_product_failure_class,
        recent_probe_failure_class=None,
        recent_warning_bearing_success_present=recent_warning_bearing_success_present,
        verification_required=(
            dispatch_decision.lane is not DispatchLane.CHEAP
            or approval_required
            or evidence_gap
            or consequential_write_pending
            or preservation_active
        ),
    )


def task_mode_for_runtime(
    *,
    active_track_ref: str,
    pending_goal_refs: tuple[str, ...],
    continuity_warnings: tuple[str, ...],
    continuity_reminders: tuple[str, ...],
) -> OperatorTaskMode:
    if (
        active_track_ref != "main"
        or pending_goal_refs
        or continuity_reminders
        or _has_continuity_rejection(continuity_warnings)
    ):
        return OperatorTaskMode.RESUME_EXECUTE
    return OperatorTaskMode.EXECUTE


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
    warnings: tuple[str, ...],
    continuity_reminders: tuple[str, ...],
    brake_state: BrakeState,
    feedback_window_summary: ReferenceFeedbackWindowSummary,
    pending_goal_refs: tuple[str, ...],
) -> tuple[str, ...]:
    tags: set[str] = set()
    if pending_goal_refs:
        tags.add("pending_goal_debt")
    if _has_continuity_rejection(warnings):
        tags.add("continuity_rejection")
    if continuity_reminders:
        tags.add("continuity_reminder")
    if brake_state is BrakeState.LATCHED:
        tags.add("latched_brake")
    if feedback_window_summary.degradation_pressure_bonus > 0:
        tags.add("degradation_pressure")
    if feedback_window_summary.sustained_spike_flags:
        tags.add("contradiction_spike")
    return tuple(sorted(tags))


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


__all__ = [
    "build_runtime_executive_signal_summary_inputs",
    "canonicalize_executive_modulator_memory",
    "closure_reason_tags",
    "continuity_demand",
    "executive_modulator_memory_payload",
    "max_uncertainty_level",
    "quota_pressure_for_budget_band",
    "recent_warning_bearing_success_present",
    "task_mode_for_runtime",
]
