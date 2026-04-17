"""Shared host-side helpers for closure-shell runtime projection."""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Mapping, Sequence
from typing import Any, Protocol

from cortex.core.dispatch import DispatchDecision, DispatchLane
from cortex.sre.brake import BrakeState
from cortex.sre.executive_summary import ExecutiveSignalSummaryInputs
from cortex.sre.feedback import (
    CONTINUITY_PROGRESS_CLASSES,
    EVIDENCE_PROGRESS_CLASSES,
    MEANINGFUL_EVIDENCE_PROGRESS_CLASSES,
    ReferenceFeedbackWindowSummary,
    ReferenceRealizationFeedback,
    ReferenceRealizationFeedbackWindow,
)
from cortex.sre.families import SoftControlFamily
from cortex.sre.goal_debt import build_closure_pressure_state
from cortex.sre.modulators import ExecutiveModulatorMemory
from cortex.sre.operator_routing import OperatorTaskMode, OperatorTaskState
from cortex.runtime.operator_brain_capability import (
    operator_brain_capability_for_band,
    operator_brain_capability_for_openai_model,
)
from cortex.sre.state import ReferenceExecutiveState


class RuntimeContinuityProgressSessionLike(Protocol):
    branch_registry: tuple[str, ...]
    active_track_ref: str
    pending_goal_refs: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RuntimeProgressSignal:
    evidence_progress_class: str
    continuity_progress_class: str
    evidence_state_moved: bool
    continuity_improved: bool

    def __post_init__(self) -> None:
        if self.evidence_progress_class not in EVIDENCE_PROGRESS_CLASSES:
            raise ValueError(
                "RuntimeProgressSignal.evidence_progress_class must be a canonical evidence progress class."
            )
        if self.continuity_progress_class not in CONTINUITY_PROGRESS_CLASSES:
            raise ValueError(
                "RuntimeProgressSignal.continuity_progress_class must be a canonical continuity progress class."
            )
        if self.evidence_state_moved is not (
            self.evidence_progress_class in MEANINGFUL_EVIDENCE_PROGRESS_CLASSES
        ):
            raise ValueError(
                "RuntimeProgressSignal.evidence_state_moved must match the derived evidence progress value."
            )
        if self.continuity_improved is not (self.continuity_progress_class != "none"):
            raise ValueError(
                "RuntimeProgressSignal.continuity_improved must match the derived continuity progress value."
            )


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


def evidence_state_moved_for_runtime(
    *,
    dispatch_decision: DispatchDecision,
    normalized_payload: Mapping[str, Any],
    commitment_result_kind: str | None,
) -> bool:
    return (
        evidence_progress_class_for_runtime(
            dispatch_decision=dispatch_decision,
            normalized_payload=normalized_payload,
            commitment_result_kind=commitment_result_kind,
        )
        in MEANINGFUL_EVIDENCE_PROGRESS_CLASSES
    )


def continuity_improved_for_runtime(
    *,
    prior_session: RuntimeContinuityProgressSessionLike,
    provisional_session: RuntimeContinuityProgressSessionLike,
) -> bool:
    return (
        continuity_progress_class_for_runtime(
            prior_session=prior_session,
            provisional_session=provisional_session,
        )
        != "none"
    )


def evidence_progress_class_for_runtime(
    *,
    dispatch_decision: DispatchDecision,
    normalized_payload: Mapping[str, Any],
    commitment_result_kind: str | None,
) -> str:
    if commitment_result_kind is not None or _first_stop_field_commitment_progress_id(
        normalized_payload
    ):
        return "commitment"
    if _as_non_empty_string(normalized_payload.get("external_record_ref")) is not None:
        return "external-record"
    if _first_concrete_artifact_ref(normalized_payload) is not None:
        return "artifact"
    if _first_candidate_progress_id(normalized_payload) is not None:
        return "candidate"
    if _has_structured_output_progress(normalized_payload):
        return "structured-stream"
    if _has_token_output_progress(normalized_payload):
        return "token-stream"
    return "none"


def continuity_progress_class_for_runtime(
    *,
    prior_session: RuntimeContinuityProgressSessionLike,
    provisional_session: RuntimeContinuityProgressSessionLike,
) -> str:
    prior_open_branch_count = sum(
        1 for branch_ref in prior_session.branch_registry if branch_ref != "main"
    )
    next_open_branch_count = sum(
        1 for branch_ref in provisional_session.branch_registry if branch_ref != "main"
    )
    if (
        prior_session.active_track_ref != "main"
        and provisional_session.active_track_ref == "main"
    ):
        return "returned-to-main"
    if next_open_branch_count < prior_open_branch_count:
        return "branch-closed"
    if len(provisional_session.pending_goal_refs) < len(prior_session.pending_goal_refs):
        return "pending-goals-reduced"
    return "none"


def classify_runtime_progress_signal(
    *,
    dispatch_decision: DispatchDecision,
    normalized_payload: Mapping[str, Any],
    commitment_result_kind: str | None,
    prior_session: RuntimeContinuityProgressSessionLike,
    provisional_session: RuntimeContinuityProgressSessionLike,
) -> RuntimeProgressSignal:
    evidence_progress_class = evidence_progress_class_for_runtime(
        dispatch_decision=dispatch_decision,
        normalized_payload=normalized_payload,
        commitment_result_kind=commitment_result_kind,
    )
    continuity_progress_class = continuity_progress_class_for_runtime(
        prior_session=prior_session,
        provisional_session=provisional_session,
    )
    return RuntimeProgressSignal(
        evidence_progress_class=evidence_progress_class,
        continuity_progress_class=continuity_progress_class,
        evidence_state_moved=(
            evidence_progress_class in MEANINGFUL_EVIDENCE_PROGRESS_CLASSES
        ),
        continuity_improved=continuity_progress_class != "none",
    )


def build_shared_realization_feedback(
    *,
    task_mode: OperatorTaskMode,
    selected_family: SoftControlFamily,
    realized_family: SoftControlFamily,
    brake_state: BrakeState,
    commitment_result_kind: str | None,
    warning_codes: tuple[str, ...],
    host_friction_tags: frozenset[str],
    probe_result_class: str | None,
    progress_signal: RuntimeProgressSignal,
) -> ReferenceRealizationFeedback:
    return ReferenceRealizationFeedback(
        selected_family=selected_family,
        realized_family=realized_family,
        brake_state=brake_state,
        task_mode=task_mode,
        commitment_result_kind=commitment_result_kind,
        warning_codes=warning_codes,
        host_friction_tags=tuple(sorted(host_friction_tags)),
        evidence_progress_class=progress_signal.evidence_progress_class,
        evidence_state_moved=progress_signal.evidence_state_moved,
        continuity_progress_class=progress_signal.continuity_progress_class,
        continuity_improved=progress_signal.continuity_improved,
        probe_result_class=probe_result_class,
    )


def assert_post_step_feedback_window_alignment(
    *,
    feedback_window: ReferenceRealizationFeedbackWindow,
    last_realization_feedback: ReferenceRealizationFeedback | None,
    feedback_window_summary: ReferenceFeedbackWindowSummary,
) -> None:
    if not isinstance(feedback_window, ReferenceRealizationFeedbackWindow):
        actual_type = type(feedback_window).__name__
        raise TypeError(
            "assert_post_step_feedback_window_alignment.feedback_window must be "
            f"ReferenceRealizationFeedbackWindow, got {actual_type}."
        )
    if (
        last_realization_feedback is not None
        and not isinstance(last_realization_feedback, ReferenceRealizationFeedback)
    ):
        actual_type = type(last_realization_feedback).__name__
        raise TypeError(
            "assert_post_step_feedback_window_alignment.last_realization_feedback must be "
            f"ReferenceRealizationFeedback | None, got {actual_type}."
        )
    if not isinstance(feedback_window_summary, ReferenceFeedbackWindowSummary):
        actual_type = type(feedback_window_summary).__name__
        raise TypeError(
            "assert_post_step_feedback_window_alignment.feedback_window_summary must be "
            f"ReferenceFeedbackWindowSummary, got {actual_type}."
        )
    if feedback_window_summary.window_size != len(feedback_window.entries):
        raise ValueError(
            "post-step feedback truth drift: feedback_window_summary.window_size "
            f"{feedback_window_summary.window_size} != len(feedback_window.entries) "
            f"{len(feedback_window.entries)}."
        )

    latest_feedback = feedback_window.entries[-1] if feedback_window.entries else None
    if last_realization_feedback is not latest_feedback:
        raise ValueError(
            "post-step feedback truth drift: session.last_realization_feedback does not "
            "match the tail feedback-window entry."
        )

    expected_evidence_progress_class = (
        last_realization_feedback.evidence_progress_class
        if last_realization_feedback is not None
        else None
    )
    expected_continuity_progress_class = (
        last_realization_feedback.continuity_progress_class
        if last_realization_feedback is not None
        else None
    )
    if (
        feedback_window_summary.recent_evidence_progress_class
        != expected_evidence_progress_class
    ):
        raise ValueError(
            "post-step feedback truth drift: recent_evidence_progress_class "
            f"{feedback_window_summary.recent_evidence_progress_class!r} != "
            "last_realization_feedback.evidence_progress_class "
            f"{expected_evidence_progress_class!r}."
        )
    if (
        feedback_window_summary.recent_continuity_progress_class
        != expected_continuity_progress_class
    ):
        raise ValueError(
            "post-step feedback truth drift: recent_continuity_progress_class "
            f"{feedback_window_summary.recent_continuity_progress_class!r} != "
            "last_realization_feedback.continuity_progress_class "
            f"{expected_continuity_progress_class!r}."
        )


def build_runtime_operator_task_state(
    *,
    summary_inputs: ExecutiveSignalSummaryInputs,
    executive_state: ReferenceExecutiveState,
    operator_model: str | None = None,
    contract_binding_demand: float = 0.0,
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
    if not isinstance(contract_binding_demand, (int, float)):
        actual_type = type(contract_binding_demand).__name__
        raise TypeError(
            "build_runtime_operator_task_state.contract_binding_demand must be numeric, "
            f"got {actual_type}."
        )
    if operator_model is None:
        brain_capability = operator_brain_capability_for_band("frontier")
    else:
        _band, brain_capability = operator_brain_capability_for_openai_model(
            operator_model
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
        contract_binding_demand=float(contract_binding_demand),
        brain_capability=brain_capability,
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


def _first_concrete_artifact_ref(normalized_payload: Mapping[str, Any]) -> str | None:
    for key in ("result_artifact_ref", "artifact_ref", "verified_work_ref"):
        value = _as_non_empty_string(normalized_payload.get(key))
        if value is not None:
            return value
    return None


def _as_non_empty_string(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


def _has_token_output_progress(normalized_payload: Mapping[str, Any]) -> bool:
    direct_delta = normalized_payload.get("delta")
    if _as_non_empty_string(direct_delta) is not None:
        return True
    if isinstance(direct_delta, Mapping):
        return _as_non_empty_string(direct_delta.get("text")) is not None
    return False


def _has_structured_output_progress(normalized_payload: Mapping[str, Any]) -> bool:
    direct_delta = normalized_payload.get("delta")
    if isinstance(direct_delta, Mapping) and _as_non_empty_string(
        direct_delta.get("partial_json")
    ) is not None:
        return True
    return _as_non_empty_string(normalized_payload.get("partial_json")) is not None


def _first_candidate_progress_id(normalized_payload: Mapping[str, Any]) -> str | None:
    candidate_id = _as_non_empty_string(normalized_payload.get("candidate_id"))
    if candidate_id is not None:
        return candidate_id
    raw = normalized_payload.get("stop_fields")
    if not isinstance(raw, Mapping):
        return None
    value = _as_non_empty_string(raw.get("candidate_id"))
    if value is not None:
        return value
    return None


def _first_stop_field_commitment_progress_id(
    normalized_payload: Mapping[str, Any],
) -> str | None:
    raw = normalized_payload.get("stop_fields")
    if not isinstance(raw, Mapping):
        return None
    for key in ("claim_id", "commitment_id"):
        value = _as_non_empty_string(raw.get(key))
        if value is not None:
            return value
    return None


def probe_result_class_for_runtime(
    *,
    realized_family: SoftControlFamily,
    executive_state: ReferenceExecutiveState,
    opportunities: Sequence[Any],
) -> str | None:
    relevant_probe_opportunities = tuple(
        opportunity
        for opportunity in opportunities
        if getattr(opportunity, "probe_contract", None) is not None
        and opportunity.probe_contract.allowed_family is realized_family
    )
    if not relevant_probe_opportunities:
        return None
    for opportunity in relevant_probe_opportunities:
        if getattr(opportunity, "realizable", False):
            return "succeeded"
    if any(
        getattr(opportunity, "degradation_reason", None)
        == "documented-probe-surface-unavailable"
        for opportunity in relevant_probe_opportunities
    ):
        return "unsupported"
    return None


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
    "assert_post_step_feedback_window_alignment",
    "assert_runtime_posture_alignment",
    "build_shared_realization_feedback",
    "classify_runtime_progress_signal",
    "build_runtime_operator_task_state",
    "build_runtime_executive_signal_summary_inputs",
    "canonicalize_executive_modulator_memory",
    "closure_reason_tags",
    "continuity_demand",
    "continuity_progress_class_for_runtime",
    "continuity_improved_for_runtime",
    "evidence_progress_class_for_runtime",
    "evidence_state_moved_for_runtime",
    "executive_modulator_memory_payload",
    "max_uncertainty_level",
    "probe_result_class_for_runtime",
    "public_posture_for_task_mode",
    "quota_pressure_for_budget_band",
    "recent_probe_failure_class",
    "recent_warning_bearing_success_present",
    "RuntimeProgressSignal",
    "task_mode_for_runtime",
    "verification_state_for_runtime",
]
