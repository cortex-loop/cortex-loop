# 05 — Claude Communication Surface

This file appends only Claude-family host surfaces through which Cortex communicates to Claude. It excludes OpenAI and Gemini host adapters. It includes the prior local `model_facing.py` from branch `codex/20260501-142219-claude-code-bridge-translation-headless-harness` so the thinking model can see why that three-template switch is not a general `τ`.

Read this file as the Claude host boundary for `τ`. The code below shows the
legal and structural paths by which Cortex state can reach Claude, including
runtime context, host control, hook control, and Claude Code Desktop session
I/O. It should not be read as proof that any path has behavior lift. Delivery,
model-visible reception, and behavior change remain separate empirical claims.
The appended `model_facing.py` is included as a known inadequate local repair:
it demonstrates why three situated templates are not a general re-entry
operator.

### `cortex/hosts/_executive_closure.py`

```python
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
```

### `cortex/hosts/runtime_context.py`

```python
"""Provider-neutral runtime-context text for model-visible host-control calls."""

from __future__ import annotations

from cortex.sre.brake import BrakeState
from cortex.sre.feedback import (
    MEANINGFUL_EVIDENCE_PROGRESS_CLASSES,
    STREAM_ONLY_EVIDENCE_PROGRESS_CLASSES,
    ReferenceRealizationFeedback,
)
from cortex.sre.opportunities import PROBE_FAILURE_CLASSES


_LOW_EVIDENCE_CLASSES = frozenset({"none"}) | STREAM_ONLY_EVIDENCE_PROGRESS_CLASSES


def runtime_context_from_last_feedback(
    feedback: ReferenceRealizationFeedback | None,
) -> str | None:
    """Translate newest realization feedback into one model-visible constraint.

    The function deliberately accepts one feedback object, not a feedback window
    or host session, so callers cannot accidentally accumulate context across
    turns. Returned text is an attached-context executive constraint in the
    model's task frame, not a schema block, outside-person warning, or raw
    Cortex diagnostic.
    """
    if feedback is None:
        return None
    if not isinstance(feedback, ReferenceRealizationFeedback):
        actual_type = type(feedback).__name__
        raise TypeError(
            "runtime_context_from_last_feedback.feedback must be "
            f"ReferenceRealizationFeedback | None, got {actual_type}."
        )
    if _is_clean_feedback(feedback):
        return None

    return _next_call_constraint(feedback)


def _is_clean_feedback(feedback: ReferenceRealizationFeedback) -> bool:
    if feedback.warning_codes or feedback.host_friction_tags:
        return False
    if feedback.selected_family is not feedback.realized_family:
        return False
    if feedback.brake_state is not BrakeState.QUIESCENT:
        return False
    if feedback.probe_result_class not in (None, "succeeded"):
        return False
    progress_unspecified = (
        feedback.evidence_progress_class is None
        and feedback.evidence_state_moved is None
        and feedback.continuity_progress_class is None
        and feedback.continuity_improved is None
    )
    if progress_unspecified:
        return True
    return _has_meaningful_progress(feedback)


def _has_meaningful_progress(feedback: ReferenceRealizationFeedback) -> bool:
    return bool(
        feedback.evidence_progress_class in MEANINGFUL_EVIDENCE_PROGRESS_CLASSES
        or feedback.evidence_state_moved is True
        or (
            feedback.continuity_progress_class is not None
            and feedback.continuity_progress_class != "none"
        )
        or feedback.continuity_improved is True
        or feedback.probe_result_class == "succeeded"
    )


def _next_call_constraint(feedback: ReferenceRealizationFeedback) -> str | None:
    if _has_continuity_or_session_warning(feedback):
        return (
            "Continuity is not anchored enough for closure. Prior context needs "
            "to be recovered, or the missing context needs to be asked for, "
            "before closure holds."
        )
    elif feedback.probe_result_class in PROBE_FAILURE_CLASSES:
        return (
            "The usual check did not come through. Alternate evidence from the "
            "current task is needed, or the work should close as blocked for "
            "missing information."
        )
    elif _has_low_evidence_without_continuity(feedback):
        return (
            "Completion is not supported by the evidence yet. An artifact, a "
            "check, or a narrower claim is still needed before closure holds."
        )
    elif (
        feedback.selected_family is not feedback.realized_family
        or feedback.brake_state is not BrakeState.QUIESCENT
        or feedback.warning_codes
    ):
        return (
            "Something in the prior step is unresolved. A check is needed before "
            "the next action is treated as safe to continue."
        )
    return None


def _has_continuity_or_session_warning(feedback: ReferenceRealizationFeedback) -> bool:
    return any(
        code.startswith(("continuity-rejected:", "session-rejected:"))
        for code in feedback.warning_codes
    )


def _has_low_evidence_without_continuity(
    feedback: ReferenceRealizationFeedback,
) -> bool:
    if feedback.evidence_progress_class not in _LOW_EVIDENCE_CLASSES:
        return feedback.evidence_state_moved is False and not _has_continuity_progress(
            feedback
        )
    return not _has_continuity_progress(feedback)


def _has_continuity_progress(feedback: ReferenceRealizationFeedback) -> bool:
    return bool(
        (
            feedback.continuity_progress_class is not None
            and feedback.continuity_progress_class != "none"
        )
        or feedback.continuity_improved is True
    )


__all__ = [
    "runtime_context_from_last_feedback",
]
```

### `cortex/hosts/claude/runtime.py`

```python
"""Claude documented host-event runtime shell over landed driver/core/SRE surfaces."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from cortex.core.certification import certify_commitment
from cortex.core.commitments import (
    BoundaryAssessment,
    CertificationContext,
    CommitmentStatus,
    ProvenanceManifest,
)
from cortex.core.dispatch import DispatchDecision, DispatchLane, classify_dispatch
from cortex.core.environment import (
    EXECUTION_TRACE,
    EXTERNAL_RECORD,
    RESULT_ARTIFACT,
    CommitmentEnvironmentHandle,
    ExecutiveEnvironmentView,
)
from cortex.core.support import (
    SupportExecMemoryState,
    SupportHostState,
    SupportSessionState,
    SupportSnapshot,
    SupportTraceState,
)
from cortex.drivers._commitment_common import (
    extract_native_commitment_fields,
    merge_warnings,
    resolve_commitment_extract_for_dispatch,
)
from cortex.drivers.claude_host import (
    BoundClaudeHostEvent,
    is_raw_claude_host_event_name,
    observe_claude_host_event,
)
from cortex.drivers.claude_host_commitment import bind_claude_host_candidate
from cortex.hosts._executive_closure import (
    assert_post_step_feedback_window_alignment,
    assert_runtime_posture_alignment,
    build_shared_realization_feedback,
    build_runtime_operator_task_state,
    build_runtime_executive_signal_summary_inputs,
    canonicalize_executive_modulator_memory,
    classify_runtime_progress_signal,
    closure_reason_tags,
    probe_result_class_for_runtime,
    public_posture_for_task_mode,
    recent_probe_failure_class as recent_probe_failure_class_from_feedback_window,
    recent_warning_bearing_success_present,
    task_mode_for_runtime,
    verification_state_for_runtime,
)
from cortex.sre.allocation import (
    build_allocation_diagnostics_payload,
    build_audit_projection_payload,
)
from cortex.sre.branching import BranchOperation
from cortex.sre.brake import BrakeState
from cortex.sre.executive_summary import (
    ExecutiveSignalSummary,
    build_executive_signal_summary,
)
from cortex.sre.families import SoftControlFamily
from cortex.sre.goals import make_resume_reminder, parse_resume_reminder_track
from cortex.sre.feedback import (
    ReferenceFeedbackWindowSummary,
    ReferenceRealizationFeedback,
    ReferenceRealizationFeedbackWindow,
    summarize_reference_feedback_window,
)
from cortex.sre.modulators import (
    ExecutiveModulatorMemory,
    ExecutiveModulatorState,
    update_executive_modulators,
)
from cortex.sre.operator_routing import (
    OperatorRouteDecision,
    OperatorTaskState,
    build_operator_route_diagnostics,
    select_operator_route_with_policy,
)
from cortex.sre.opportunities import BoundedProbeContract, HostNativeOpportunity
from cortex.sre.policy_view import ExecutivePolicyView, build_executive_policy_view
from cortex.sre.reference_builder import build_reference_executive_state
from cortex.sre.reference_scoring import (
    rejected_cheaper_families as scorecard_rejected_cheaper_families,
)
from cortex.sre.reference_scoring import select_reference_soft_control
from cortex.sre.state import ReferenceExecutiveState

_ALLOWED_COMMITMENT_RESULT_KINDS = frozenset(status.value for status in CommitmentStatus)


@dataclass(frozen=True, slots=True)
class ClaudeRuntimeSession:
    session_id: str | None = None
    event_index: int = 0
    branch_registry: tuple[str, ...] = ("main",)
    active_track_ref: str = "main"
    pending_goal_refs: tuple[str, ...] = ()
    continuity_reminders: tuple[str, ...] = ()
    budget_history: tuple[str, ...] = ()
    brake_history: tuple[str, ...] = ()
    brake_tonic_history: tuple[float, ...] = ()
    last_selected_family: SoftControlFamily | None = None
    last_commitment_result_summary: str | None = None
    last_realization_feedback: ReferenceRealizationFeedback | None = None
    feedback_window: ReferenceRealizationFeedbackWindow = field(
        default_factory=ReferenceRealizationFeedbackWindow
    )
    executive_modulator_memory: ExecutiveModulatorMemory | None = None

    def __post_init__(self) -> None:
        if self.session_id is not None and not (
            isinstance(self.session_id, str) and self.session_id.strip()
        ):
            raise ValueError(
                "ClaudeRuntimeSession.session_id must be non-empty after trimming when provided."
            )
        if isinstance(self.event_index, bool) or not isinstance(self.event_index, int):
            actual_type = type(self.event_index).__name__
            raise TypeError(
                "ClaudeRuntimeSession.event_index must be a non-negative integer, "
                f"got {actual_type}."
            )
        if self.event_index < 0:
            raise ValueError("ClaudeRuntimeSession.event_index must be non-negative.")
        if any(not (isinstance(ref, str) and ref.strip()) for ref in self.branch_registry):
            raise ValueError(
                "ClaudeRuntimeSession.branch_registry must contain only non-empty values after trimming."
            )
        if not (isinstance(self.active_track_ref, str) and self.active_track_ref.strip()):
            raise ValueError(
                "ClaudeRuntimeSession.active_track_ref must be non-empty after trimming."
            )
        if self.active_track_ref != "main" and self.active_track_ref not in self.branch_registry:
            raise ValueError(
                "ClaudeRuntimeSession.active_track_ref must be `main` or a member of branch_registry."
            )
        if any(not (isinstance(ref, str) and ref.strip()) for ref in self.pending_goal_refs):
            raise ValueError(
                "ClaudeRuntimeSession.pending_goal_refs must contain only non-empty values after trimming."
            )
        if any(
            not (isinstance(reminder, str) and reminder.strip())
            for reminder in self.continuity_reminders
        ):
            raise ValueError(
                "ClaudeRuntimeSession.continuity_reminders must contain only non-empty values after trimming."
            )
        if any(not (isinstance(entry, str) and entry.strip()) for entry in self.budget_history):
            raise ValueError(
                "ClaudeRuntimeSession.budget_history must contain only non-empty values after trimming."
            )
        if any(not (isinstance(entry, str) and entry.strip()) for entry in self.brake_history):
            raise ValueError(
                "ClaudeRuntimeSession.brake_history must contain only non-empty values after trimming."
            )
        for entry in self.brake_tonic_history:
            if isinstance(entry, bool) or not isinstance(entry, (int, float)):
                actual_type = type(entry).__name__
                raise TypeError(
                    "ClaudeRuntimeSession.brake_tonic_history must contain only "
                    f"numeric values in [0.0, 1.0], got {actual_type}."
                )
            if not 0.0 <= float(entry) <= 1.0:
                raise ValueError(
                    "ClaudeRuntimeSession.brake_tonic_history entries must be between 0.0 and 1.0."
                )
        if self.last_selected_family is not None and not isinstance(
            self.last_selected_family,
            SoftControlFamily,
        ):
            actual_type = type(self.last_selected_family).__name__
            raise TypeError(
                "ClaudeRuntimeSession.last_selected_family must be SoftControlFamily | None, "
                f"got {actual_type}."
            )
        if self.last_commitment_result_summary is not None and not (
            isinstance(self.last_commitment_result_summary, str)
            and self.last_commitment_result_summary.strip()
        ):
            raise ValueError(
                "ClaudeRuntimeSession.last_commitment_result_summary must be non-empty after trimming when provided."
            )
        if self.last_realization_feedback is not None and not isinstance(
            self.last_realization_feedback,
            ReferenceRealizationFeedback,
        ):
            actual_type = type(self.last_realization_feedback).__name__
            raise TypeError(
                "ClaudeRuntimeSession.last_realization_feedback must be "
                f"ReferenceRealizationFeedback | None, got {actual_type}."
            )
        if not isinstance(self.feedback_window, ReferenceRealizationFeedbackWindow):
            actual_type = type(self.feedback_window).__name__
            raise TypeError(
                "ClaudeRuntimeSession.feedback_window must be "
                f"ReferenceRealizationFeedbackWindow, got {actual_type}."
            )
        if self.executive_modulator_memory is not None and not isinstance(
            self.executive_modulator_memory,
            ExecutiveModulatorMemory,
        ):
            actual_type = type(self.executive_modulator_memory).__name__
            raise TypeError(
                "ClaudeRuntimeSession.executive_modulator_memory must be "
                f"ExecutiveModulatorMemory | None, got {actual_type}."
            )

        normalized_last_realization_feedback = self.last_realization_feedback
        normalized_feedback_window = self.feedback_window
        normalized_executive_modulator_memory = canonicalize_executive_modulator_memory(
            self.executive_modulator_memory
        )
        if normalized_executive_modulator_memory != self.executive_modulator_memory:
            object.__setattr__(
                self,
                "executive_modulator_memory",
                normalized_executive_modulator_memory,
            )
        if (
            normalized_last_realization_feedback is not None
            and not normalized_feedback_window.entries
        ):
            normalized_feedback_window = ReferenceRealizationFeedbackWindow(
                entries=(normalized_last_realization_feedback,)
            )
            object.__setattr__(self, "feedback_window", normalized_feedback_window)
        elif normalized_last_realization_feedback is None and normalized_feedback_window.entries:
            normalized_last_realization_feedback = normalized_feedback_window.entries[-1]
            object.__setattr__(
                self,
                "last_realization_feedback",
                normalized_last_realization_feedback,
            )
        if (
            normalized_last_realization_feedback is not None
            and normalized_feedback_window.entries
            and normalized_feedback_window.entries[-1] != normalized_last_realization_feedback
        ):
            raise ValueError(
                "ClaudeRuntimeSession.feedback_window newest entry must match "
                "last_realization_feedback when both are present."
            )
        if normalized_last_realization_feedback is None and normalized_feedback_window.entries:
            raise ValueError(
                "ClaudeRuntimeSession.feedback_window must be empty when "
                "last_realization_feedback is None."
            )

    def as_summary(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "event_index": self.event_index,
            "branch_registry": list(self.branch_registry),
            "active_track_ref": self.active_track_ref,
            "pending_goal_refs": list(self.pending_goal_refs),
            "budget_history": list(self.budget_history),
            "brake_history": list(self.brake_history),
            "feedback_window_size": len(self.feedback_window.entries),
            "last_selected_family": (
                self.last_selected_family.value
                if self.last_selected_family is not None
                else None
            ),
            "last_commitment_result_summary": self.last_commitment_result_summary,
        }


@dataclass(frozen=True, slots=True)
class ClaudeControlLedger:
    event_class: str
    admissible_families: tuple[SoftControlFamily, ...]
    selected_family: SoftControlFamily
    realized_family: SoftControlFamily
    dominant_uncertainty_sources: tuple[str, ...]
    brake_state: BrakeState
    budget_band: str
    primary_reason: str | None = None
    allocation_diagnostics: dict[str, Any] = field(default_factory=dict)
    audit_projection: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if not (isinstance(self.event_class, str) and self.event_class.strip()):
            raise ValueError(
                "ClaudeControlLedger.event_class must be non-empty after trimming."
            )
        if any(not isinstance(family, SoftControlFamily) for family in self.admissible_families):
            raise TypeError(
                "ClaudeControlLedger.admissible_families must contain only SoftControlFamily instances."
            )
        if not isinstance(self.selected_family, SoftControlFamily):
            actual_type = type(self.selected_family).__name__
            raise TypeError(
                "ClaudeControlLedger.selected_family must be SoftControlFamily, "
                f"got {actual_type}."
            )
        if not isinstance(self.realized_family, SoftControlFamily):
            actual_type = type(self.realized_family).__name__
            raise TypeError(
                "ClaudeControlLedger.realized_family must be SoftControlFamily, "
                f"got {actual_type}."
            )
        if any(
            not (isinstance(source, str) and source.strip())
            for source in self.dominant_uncertainty_sources
        ):
            raise ValueError(
                "ClaudeControlLedger.dominant_uncertainty_sources must contain only non-empty values after trimming."
            )
        if not isinstance(self.brake_state, BrakeState):
            actual_type = type(self.brake_state).__name__
            raise TypeError(
                "ClaudeControlLedger.brake_state must be BrakeState, "
                f"got {actual_type}."
            )
        if not (isinstance(self.budget_band, str) and self.budget_band.strip()):
            raise ValueError(
                "ClaudeControlLedger.budget_band must be non-empty after trimming."
            )
        if self.primary_reason is not None and not (
            isinstance(self.primary_reason, str) and self.primary_reason.strip()
        ):
            raise ValueError(
                "ClaudeControlLedger.primary_reason must be non-empty after trimming when provided."
            )
        _validate_allocation_diagnostics_payload(
            self.allocation_diagnostics,
            "ClaudeControlLedger.allocation_diagnostics",
        )
        if self.audit_projection is not None:
            _validate_audit_projection_payload(
                self.audit_projection,
                "ClaudeControlLedger.audit_projection",
            )

    def as_summary(self) -> dict[str, Any]:
        payload = {
            "event_class": self.event_class,
            "admissible_families": [
                family.value for family in self.admissible_families
            ],
            "selected_family": self.selected_family.value,
            "realized_family": self.realized_family.value,
            "dominant_uncertainty_sources": list(self.dominant_uncertainty_sources),
            "brake_state": self.brake_state.value,
            "budget_band": self.budget_band,
            "primary_reason": self.primary_reason,
            "allocation_diagnostics": _copy_allocation_diagnostics_payload(
                self.allocation_diagnostics
            ),
        }
        if self.audit_projection is not None:
            payload["audit_projection"] = _copy_audit_projection_payload(
                self.audit_projection
            )
        return payload


@dataclass(frozen=True, slots=True)
class ClaudeRuntimeStepResult:
    event_index: int
    bound_event: BoundClaudeHostEvent
    dispatch_decision: DispatchDecision
    executive_state: ReferenceExecutiveState
    selected_family: SoftControlFamily
    realized_family: SoftControlFamily
    brake_state: BrakeState
    control_ledger: ClaudeControlLedger
    feedback_window_summary: ReferenceFeedbackWindowSummary = field(
        default_factory=ReferenceFeedbackWindowSummary
    )
    executive_signal_summary: ExecutiveSignalSummary = field(
        default_factory=lambda: ExecutiveSignalSummary(
            uncertainty=0.0,
            repeated_failure_pressure=0.0,
            quota_pressure=0.0,
            continuity_demand=0.0,
            novelty_pressure=0.0,
            verification_conflict_pressure=0.0,
        )
    )
    executive_modulator_state: ExecutiveModulatorState = field(
        default_factory=lambda: ExecutiveModulatorState(
            focus_gain=0.0,
            explore_gain=0.0,
            stop_pressure=0.0,
            update_pressure=0.0,
        )
    )
    executive_policy_view: ExecutivePolicyView = field(
        default_factory=lambda: ExecutivePolicyView(
            default_profile_bonus=0.0,
            switch_margin=0.0,
            stop_threshold=0.75,
            allow_extra_read_pass=False,
            verification_intensity=0.30,
        )
    )
    operator_task_state: OperatorTaskState | None = None
    operator_route: OperatorRouteDecision | None = None
    closure_required: bool = False
    closure_reason_tags: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    session: ClaudeRuntimeSession = field(default_factory=ClaudeRuntimeSession)
    commitment_result_kind: str | None = None

    def __post_init__(self) -> None:
        if isinstance(self.event_index, bool) or not isinstance(self.event_index, int):
            actual_type = type(self.event_index).__name__
            raise TypeError(
                "ClaudeRuntimeStepResult.event_index must be a positive integer, "
                f"got {actual_type}."
            )
        if self.event_index <= 0:
            raise ValueError("ClaudeRuntimeStepResult.event_index must be positive.")
        if not isinstance(self.bound_event, BoundClaudeHostEvent):
            actual_type = type(self.bound_event).__name__
            raise TypeError(
                "ClaudeRuntimeStepResult.bound_event must be BoundClaudeHostEvent, "
                f"got {actual_type}."
            )
        if not isinstance(self.dispatch_decision, DispatchDecision):
            actual_type = type(self.dispatch_decision).__name__
            raise TypeError(
                "ClaudeRuntimeStepResult.dispatch_decision must be DispatchDecision, "
                f"got {actual_type}."
            )
        if not isinstance(self.executive_state, ReferenceExecutiveState):
            actual_type = type(self.executive_state).__name__
            raise TypeError(
                "ClaudeRuntimeStepResult.executive_state must be ReferenceExecutiveState, "
                f"got {actual_type}."
            )
        if not isinstance(self.selected_family, SoftControlFamily):
            actual_type = type(self.selected_family).__name__
            raise TypeError(
                "ClaudeRuntimeStepResult.selected_family must be SoftControlFamily, "
                f"got {actual_type}."
            )
        if not isinstance(self.realized_family, SoftControlFamily):
            actual_type = type(self.realized_family).__name__
            raise TypeError(
                "ClaudeRuntimeStepResult.realized_family must be SoftControlFamily, "
                f"got {actual_type}."
            )
        if not isinstance(self.brake_state, BrakeState):
            actual_type = type(self.brake_state).__name__
            raise TypeError(
                "ClaudeRuntimeStepResult.brake_state must be BrakeState, "
                f"got {actual_type}."
            )
        if not isinstance(self.control_ledger, ClaudeControlLedger):
            actual_type = type(self.control_ledger).__name__
            raise TypeError(
                "ClaudeRuntimeStepResult.control_ledger must be ClaudeControlLedger, "
                f"got {actual_type}."
            )
        if not isinstance(self.feedback_window_summary, ReferenceFeedbackWindowSummary):
            actual_type = type(self.feedback_window_summary).__name__
            raise TypeError(
                "ClaudeRuntimeStepResult.feedback_window_summary must be "
                f"ReferenceFeedbackWindowSummary, got {actual_type}."
            )
        if not isinstance(self.executive_signal_summary, ExecutiveSignalSummary):
            actual_type = type(self.executive_signal_summary).__name__
            raise TypeError(
                "ClaudeRuntimeStepResult.executive_signal_summary must be "
                f"ExecutiveSignalSummary, got {actual_type}."
            )
        if not isinstance(self.executive_modulator_state, ExecutiveModulatorState):
            actual_type = type(self.executive_modulator_state).__name__
            raise TypeError(
                "ClaudeRuntimeStepResult.executive_modulator_state must be "
                f"ExecutiveModulatorState, got {actual_type}."
            )
        if not isinstance(self.executive_policy_view, ExecutivePolicyView):
            actual_type = type(self.executive_policy_view).__name__
            raise TypeError(
                "ClaudeRuntimeStepResult.executive_policy_view must be "
                f"ExecutivePolicyView, got {actual_type}."
            )
        if not isinstance(self.operator_task_state, OperatorTaskState):
            actual_type = type(self.operator_task_state).__name__
            raise TypeError(
                "ClaudeRuntimeStepResult.operator_task_state must be "
                f"OperatorTaskState, got {actual_type}."
            )
        if not isinstance(self.operator_route, OperatorRouteDecision):
            actual_type = type(self.operator_route).__name__
            raise TypeError(
                "ClaudeRuntimeStepResult.operator_route must be "
                f"OperatorRouteDecision, got {actual_type}."
            )
        if not isinstance(self.closure_required, bool):
            actual_type = type(self.closure_required).__name__
            raise TypeError(
                "ClaudeRuntimeStepResult.closure_required must be bool, "
                f"got {actual_type}."
            )
        if any(
            not (isinstance(tag, str) and tag.strip())
            for tag in self.closure_reason_tags
        ):
            raise ValueError(
                "ClaudeRuntimeStepResult.closure_reason_tags must contain only non-empty values after trimming."
            )
        if any(not (isinstance(warning, str) and warning.strip()) for warning in self.warnings):
            raise ValueError(
                "ClaudeRuntimeStepResult.warnings must contain only non-empty values after trimming."
            )
        if not isinstance(self.session, ClaudeRuntimeSession):
            actual_type = type(self.session).__name__
            raise TypeError(
                "ClaudeRuntimeStepResult.session must be ClaudeRuntimeSession, "
                f"got {actual_type}."
            )
        if self.event_index != self.session.event_index:
            raise ValueError(
                "ClaudeRuntimeStepResult.event_index must match session.event_index."
            )
        if (
            self.commitment_result_kind is not None
            and self.commitment_result_kind not in _ALLOWED_COMMITMENT_RESULT_KINDS
        ):
            raise ValueError(
                "ClaudeRuntimeStepResult.commitment_result_kind must be one of the canonical "
                "commitment status values or None."
            )

    @property
    def session_summary(self) -> dict[str, Any]:
        return self.session.as_summary()

    @property
    def executive_state_summary(self) -> dict[str, Any]:
        return {
            "posture": public_posture_for_task_mode(
                self.executive_state.mode_and_gating.task_mode
            ),
            "anti_thrash_state": self.executive_state.control_allocation.anti_thrash_state,
            "mode_tag": self.executive_state.mode_and_gating.mode_tag,
            "family_mask": sorted(
                family.value for family in self.executive_state.mode_and_gating.family_mask
            ),
            "budget_band": self.executive_state.control_allocation.budget_band,
            "top_family_set": sorted(
                family.value for family in self.executive_state.control_allocation.top_family_set
            ),
            "host_friction_tags": sorted(
                self.executive_state.control_allocation.host_friction_tags
            ),
            "probe_path_state": self.executive_state.control_allocation.probe_path_state,
            "probe_unavailable_reason": (
                self.executive_state.control_allocation.probe_unavailable_reason
            ),
            "active_track_ref": self.executive_state.goal_continuity.active_track_ref,
            "pending_goal_refs": list(self.executive_state.goal_continuity.pending_goal_refs),
            "anchor_source": self.executive_state.goal_continuity.anchor_source,
            "anchor_freshness": self.executive_state.goal_continuity.anchor_freshness,
            "branch_intent_present": (
                self.executive_state.goal_continuity.branch_intent_present
            ),
        }

    @property
    def control_ledger_summary(self) -> dict[str, Any]:
        return self.control_ledger.as_summary()

    @property
    def feedback_window_summary_payload(self) -> dict[str, Any]:
        return self.feedback_window_summary.as_summary()

    @property
    def executive_signal_summary_payload(self) -> dict[str, Any]:
        return self.executive_signal_summary.as_payload()

    @property
    def executive_modulator_state_payload(self) -> dict[str, Any]:
        return self.executive_modulator_state.as_payload()

    @property
    def executive_policy_view_payload(self) -> dict[str, Any]:
        return self.executive_policy_view.as_payload()

    @property
    def operator_route_payload(self) -> dict[str, Any]:
        return build_operator_route_diagnostics(
            self.operator_task_state,
            self.operator_route,
        )


def run_claude_runtime_step(
    raw_event_name: str,
    raw_payload: Mapping[str, Any] | None,
    session: ClaudeRuntimeSession | None = None,
    *,
    audit_intensity: str = "minimal",
) -> ClaudeRuntimeStepResult:
    if not is_raw_claude_host_event_name(raw_event_name):
        raise ValueError(
            "run_claude_runtime_step.event_name must be a raw Claude host event name, "
            "not a canonical Cortex event name."
        )
    prior_session = _coerce_session(session)
    bound_event = observe_claude_host_event(raw_event_name, raw_payload)
    normalized_payload = bound_event.normalized_payload
    native_commitment_fields = extract_native_commitment_fields(normalized_payload)
    dispatch_decision = classify_dispatch(
        bound_event.observation,
        payload=normalized_payload,
        native_commitment_fields=native_commitment_fields,
    )

    extraction_result = resolve_commitment_extract_for_dispatch(
        payload=normalized_payload,
        dispatch_decision=dispatch_decision,
        native_commitment_fields=native_commitment_fields,
        allow_message_commitment_fallback=False,
    )
    warnings = merge_warnings(
        bound_event.warnings,
        dispatch_decision.warnings,
        extraction_result.warnings if extraction_result is not None else (),
    )
    session_id, session_id_warnings = _resolve_session_id(prior_session, normalized_payload)
    warnings = merge_warnings(warnings, session_id_warnings)
    prior_feedback_window_summary = summarize_reference_feedback_window(
        prior_session.feedback_window
    )

    candidate = None
    commitment_result_kind: str | None = None
    if dispatch_decision.lane is not DispatchLane.CHEAP:
        candidate, candidate_warnings = bind_claude_host_candidate(
            bound_event,
            dispatch_decision,
            extraction_result,
        )
        warnings = merge_warnings(warnings, candidate_warnings)

    if dispatch_decision.lane is DispatchLane.FULL_COMMITMENT and candidate is not None:
        boundary_assessment, boundary_warnings = _build_boundary_assessment(normalized_payload)
        warnings = merge_warnings(warnings, boundary_warnings)
        verdict = certify_commitment(
            CertificationContext(
                candidate=candidate,
                observation=bound_event.observation,
                environment_handle=_build_environment_handle(normalized_payload),
                wake_reasons=dispatch_decision.wake_decision.reason_tags,
                boundary_tags=boundary_assessment.boundary_tags,
            ),
            provenance_manifest=_build_provenance_manifest(normalized_payload),
            boundary_assessment=boundary_assessment,
        )
        commitment_result_kind = verdict.status.value

    (
        next_branch_registry,
        next_active_track_ref,
        next_pending_goal_refs,
        continuity_warnings,
        continuity_reminders,
    ) = _apply_continuity_update(prior_session, normalized_payload)
    warnings = merge_warnings(warnings, continuity_warnings)
    consequential_write_pending = bool(normalized_payload.get("externally_consequential"))
    approval_required = dispatch_decision.lane is not DispatchLane.CHEAP
    evidence_gap = (
        consequential_write_pending
        and _first_concrete_artifact_ref(normalized_payload) is None
    )
    provisional_session = ClaudeRuntimeSession(
        session_id=session_id,
        event_index=prior_session.event_index + 1,
        branch_registry=next_branch_registry,
        active_track_ref=next_active_track_ref,
        pending_goal_refs=next_pending_goal_refs,
        continuity_reminders=continuity_reminders,
        budget_history=prior_session.budget_history
        + (_budget_entry_for_lane(dispatch_decision.lane),),
        brake_history=prior_session.brake_history,
        brake_tonic_history=prior_session.brake_tonic_history,
        last_selected_family=prior_session.last_selected_family,
        last_commitment_result_summary=prior_session.last_commitment_result_summary,
        last_realization_feedback=prior_session.last_realization_feedback,
        feedback_window=prior_session.feedback_window,
    )
    support_snapshot = _build_support_snapshot(
        provisional_session=provisional_session,
        bound_event=bound_event,
        dispatch_decision=dispatch_decision,
        warnings=warnings,
        reminders=continuity_reminders,
    )
    opportunities = _claude_host_native_opportunities(bound_event)
    runtime_task_mode = task_mode_for_runtime(
        dispatch_decision=dispatch_decision,
        active_track_ref=provisional_session.active_track_ref,
        pending_goal_refs=provisional_session.pending_goal_refs,
        continuity_warnings=continuity_warnings,
        continuity_reminders=continuity_reminders,
        approval_required=approval_required,
        evidence_gap=evidence_gap,
        consequential_write_pending=consequential_write_pending,
        preservation_active=False,
    )
    executive_state = build_reference_executive_state(
        bound_event.observation,
        support_snapshot,
        _build_executive_environment_view(normalized_payload),
        provisional_session,
        opportunities=opportunities,
        audit_intensity=audit_intensity,
        task_mode=runtime_task_mode,
    )
    selection = select_reference_soft_control(
        executive_state,
        opportunities=opportunities,
    )
    selected_family = selection.selected_family
    brake_state = executive_state.brake.brake_state
    dominant_uncertainty_sources = _dominant_uncertainty_sources(executive_state)
    realized_family, enforcement_warnings = _realize_family(
        selected_family,
        brake_state=brake_state,
        dominant_uncertainty_sources=dominant_uncertainty_sources,
        feedback_pressure_tags=executive_state.control_allocation.feedback_pressure_tags,
    )
    warnings = merge_warnings(warnings, enforcement_warnings)
    allocation_diagnostics = build_allocation_diagnostics_payload(
        selection.scorecard,
        selected_delta_over_neutral=selection.neutral_dominance.margin_over_neutral,
        applied_activation_threshold=selection.neutral_dominance.activation_threshold,
        chi_t=selection.chi_t,
        rejected_cheaper_families=scorecard_rejected_cheaper_families(
            selection.scorecard,
            selected_family=selected_family,
        ),
        probe_path_state=executive_state.control_allocation.probe_path_state,
        probe_unavailable_reason=(
            executive_state.control_allocation.probe_unavailable_reason
        ),
        probe_result_class=probe_result_class_for_runtime(
            realized_family=realized_family,
            executive_state=executive_state,
            opportunities=opportunities,
        ),
        verification_state=verification_state_for_runtime(
            dispatch_decision=dispatch_decision,
            commitment_result_kind=commitment_result_kind,
        ),
        explainability_profile=executive_state.control_allocation.explainability_profile,
        anti_thrash_state=executive_state.control_allocation.anti_thrash_state,
        repetition_target_family=(
            executive_state.control_allocation.repetition_target_family
        ),
        repetition_tax=executive_state.control_allocation.repetition_tax,
        anti_thrash_reason_tags=(
            executive_state.control_allocation.anti_thrash_reason_tags
        ),
        risk_weight=executive_state.control_allocation.risk_weight,
        brake_tonic=executive_state.brake.tonic,
    )
    audit_projection = None
    if _should_emit_audit_projection(
        executive_state.control_allocation.explainability_profile
    ):
        audit_projection = build_audit_projection_payload(
            selected_family=selected_family,
            realized_family=realized_family,
            dominant_uncertainty_sources=dominant_uncertainty_sources,
            allocation_diagnostics=allocation_diagnostics,
        )
    control_ledger = ClaudeControlLedger(
        event_class=dispatch_decision.lane.value,
        admissible_families=_admissible_families(executive_state),
        selected_family=selected_family,
        realized_family=realized_family,
        dominant_uncertainty_sources=dominant_uncertainty_sources,
        brake_state=brake_state,
        budget_band=executive_state.control_allocation.budget_band,
        primary_reason=_primary_reason(warnings),
        allocation_diagnostics=allocation_diagnostics,
        audit_projection=audit_projection,
    )
    progress_signal = classify_runtime_progress_signal(
        dispatch_decision=dispatch_decision,
        normalized_payload=normalized_payload,
        commitment_result_kind=commitment_result_kind,
        prior_session=prior_session,
        provisional_session=provisional_session,
    )
    realization_feedback = build_shared_realization_feedback(
        task_mode=runtime_task_mode,
        selected_family=selected_family,
        realized_family=realized_family,
        brake_state=brake_state,
        commitment_result_kind=commitment_result_kind,
        warning_codes=tuple(warnings),
        host_friction_tags=tuple(
            sorted(executive_state.control_allocation.host_friction_tags)
        ),
        progress_signal=progress_signal,
        probe_result_class=probe_result_class_for_runtime(
            realized_family=realized_family,
            executive_state=executive_state,
            opportunities=opportunities,
        ),
    )
    updated_session = ClaudeRuntimeSession(
        session_id=provisional_session.session_id,
        event_index=provisional_session.event_index,
        branch_registry=provisional_session.branch_registry,
        active_track_ref=provisional_session.active_track_ref,
        pending_goal_refs=provisional_session.pending_goal_refs,
        continuity_reminders=provisional_session.continuity_reminders,
        budget_history=provisional_session.budget_history,
        brake_history=prior_session.brake_history + (brake_state.value,),
        brake_tonic_history=_bounded_tonic_history(
            prior_session.brake_tonic_history, executive_state.brake.tonic
        ),
        last_selected_family=selected_family,
        last_commitment_result_summary=_commitment_summary_for_lane(
            dispatch_decision.lane,
            commitment_result_kind,
        ),
        last_realization_feedback=realization_feedback,
        feedback_window=prior_session.feedback_window.append(realization_feedback),
        executive_modulator_memory=prior_session.executive_modulator_memory,
    )
    executive_summary_inputs = build_runtime_executive_signal_summary_inputs(
        task_mode=runtime_task_mode,
        executive_state=executive_state,
        dispatch_decision=dispatch_decision,
        active_track_ref=provisional_session.active_track_ref,
        pending_goal_refs=provisional_session.pending_goal_refs,
        continuity_warnings=continuity_warnings,
        continuity_reminders=continuity_reminders,
        approval_required=approval_required,
        evidence_gap=evidence_gap,
        consequential_write_pending=consequential_write_pending,
        prior_failed_before_completion=False,
        recent_product_failure_class=None,
        recent_probe_failure_class=recent_probe_failure_class_from_feedback_window(
            prior_session.feedback_window
        ),
        recent_warning_bearing_success_present=recent_warning_bearing_success_present(
            prior_session.feedback_window,
            failed_before_completion=False,
        ),
        preservation_active=False,
    )
    executive_signal_summary = build_executive_signal_summary(executive_summary_inputs)
    assert_runtime_posture_alignment(
        runtime_task_mode=runtime_task_mode,
        executive_state=executive_state,
        executive_signal_summary=executive_signal_summary,
    )
    executive_modulator_update = update_executive_modulators(
        executive_signal_summary,
        previous=prior_session.executive_modulator_memory,
    )
    executive_policy_view = build_executive_policy_view(
        executive_signal_summary,
        executive_modulator_update.state,
        chi_t=selection.chi_t,
    )
    operator_task_state = build_runtime_operator_task_state(
        summary_inputs=executive_summary_inputs,
        executive_state=executive_state,
    )
    operator_route = select_operator_route_with_policy(
        operator_task_state,
        executive_modulator_update,
        executive_policy_view,
    )
    closure_reason_tags_value = closure_reason_tags(
        active_track_ref=provisional_session.active_track_ref,
        warnings=warnings,
        continuity_reminders=continuity_reminders,
        brake_state=brake_state,
        feedback_window_summary=prior_feedback_window_summary,
        pending_goal_refs=provisional_session.pending_goal_refs,
    )
    closure_required = bool(closure_reason_tags_value)
    updated_session = ClaudeRuntimeSession(
        session_id=updated_session.session_id,
        event_index=updated_session.event_index,
        branch_registry=updated_session.branch_registry,
        active_track_ref=updated_session.active_track_ref,
        pending_goal_refs=updated_session.pending_goal_refs,
        continuity_reminders=updated_session.continuity_reminders,
        budget_history=updated_session.budget_history,
        brake_history=updated_session.brake_history,
        brake_tonic_history=updated_session.brake_tonic_history,
        last_selected_family=updated_session.last_selected_family,
        last_commitment_result_summary=updated_session.last_commitment_result_summary,
        last_realization_feedback=updated_session.last_realization_feedback,
        feedback_window=updated_session.feedback_window,
        executive_modulator_memory=canonicalize_executive_modulator_memory(
            executive_modulator_update.next_memory
        ),
    )
    post_feedback_window_summary = summarize_reference_feedback_window(
        updated_session.feedback_window
    )
    assert_post_step_feedback_window_alignment(
        feedback_window=updated_session.feedback_window,
        last_realization_feedback=updated_session.last_realization_feedback,
        feedback_window_summary=post_feedback_window_summary,
    )
    return ClaudeRuntimeStepResult(
        event_index=updated_session.event_index,
        bound_event=bound_event,
        dispatch_decision=dispatch_decision,
        executive_state=executive_state,
        selected_family=selected_family,
        realized_family=realized_family,
        brake_state=brake_state,
        control_ledger=control_ledger,
        feedback_window_summary=post_feedback_window_summary,
        executive_signal_summary=executive_signal_summary,
        executive_modulator_state=executive_modulator_update.state,
        executive_policy_view=executive_policy_view,
        operator_task_state=operator_task_state,
        operator_route=operator_route,
        closure_required=closure_required,
        closure_reason_tags=closure_reason_tags_value,
        warnings=warnings,
        session=updated_session,
        commitment_result_kind=commitment_result_kind,
    )


def _coerce_session(session: ClaudeRuntimeSession | None) -> ClaudeRuntimeSession:
    if session is None:
        return ClaudeRuntimeSession()
    if not isinstance(session, ClaudeRuntimeSession):
        actual_type = type(session).__name__
        raise TypeError(
            "run_claude_runtime_step.session must be ClaudeRuntimeSession | None, "
            f"got {actual_type}."
        )
    return session


def _resolve_session_id(
    prior_session: ClaudeRuntimeSession,
    normalized_payload: Mapping[str, Any],
) -> tuple[str | None, tuple[str, ...]]:
    payload_session_id = _as_non_empty_string(normalized_payload.get("session_id"))
    if prior_session.session_id is None:
        return payload_session_id, ()
    if payload_session_id is None or payload_session_id == prior_session.session_id:
        return prior_session.session_id, ()
    return (
        prior_session.session_id,
        (f"session-rejected:mismatched-session-id:{payload_session_id}",),
    )


def _apply_continuity_update(
    prior_session: ClaudeRuntimeSession,
    normalized_payload: Mapping[str, Any],
) -> tuple[tuple[str, ...], str, tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    operation = _branch_operation(normalized_payload)
    branch_registry = list(prior_session.branch_registry)
    active_track_ref = prior_session.active_track_ref
    pending_goal_refs = list(prior_session.pending_goal_refs)
    continuity_reminders = list(prior_session.continuity_reminders)
    branch_track_ref = _continuity_track_ref(normalized_payload)
    payload_goal_refs = _pending_goal_refs_from_payload(normalized_payload)
    warnings: tuple[str, ...] = ()

    if operation is None:
        if payload_goal_refs:
            pending_goal_refs = _merge_unique_refs(tuple(pending_goal_refs), payload_goal_refs)
        return (
            tuple(branch_registry),
            active_track_ref,
            tuple(pending_goal_refs),
            warnings,
            tuple(continuity_reminders),
        )

    if operation is BranchOperation.OPEN:
        if branch_track_ref is None:
            warnings = ("continuity-rejected:missing-open-track-ref",)
            return (
                tuple(prior_session.branch_registry),
                prior_session.active_track_ref,
                tuple(prior_session.pending_goal_refs),
                warnings,
                tuple(prior_session.continuity_reminders),
            )
        if branch_track_ref not in branch_registry:
            branch_registry.append(branch_track_ref)
        active_track_ref = branch_track_ref
        continuity_reminders = list(
            _without_track_reminders(continuity_reminders, branch_track_ref)
        )
        pending_goal_refs = [
            goal_ref for goal_ref in pending_goal_refs if goal_ref != branch_track_ref
        ]
        pending_goal_refs = _merge_unique_refs(tuple(pending_goal_refs), payload_goal_refs)
    elif operation is BranchOperation.SUSPEND:
        if (
            branch_track_ref is None
            or branch_track_ref not in branch_registry
            or active_track_ref != branch_track_ref
        ):
            warnings = (_continuity_warning("missing-active-branch", branch_track_ref),)
            return (
                tuple(prior_session.branch_registry),
                prior_session.active_track_ref,
                tuple(prior_session.pending_goal_refs),
                warnings,
                tuple(prior_session.continuity_reminders),
            )
        active_track_ref = "main"
        continuity_reminders = list(
            _merge_distinct_strings(
                _without_track_reminders(continuity_reminders, branch_track_ref),
                (make_resume_reminder(branch_track_ref),),
            )
        )
        pending_goal_refs = _merge_unique_refs(
            tuple(pending_goal_refs),
            (branch_track_ref, *payload_goal_refs),
        )
    elif operation is BranchOperation.RESUME:
        if branch_track_ref is None or branch_track_ref not in branch_registry:
            warnings = (_continuity_warning("missing-active-branch", branch_track_ref),)
            return (
                tuple(prior_session.branch_registry),
                prior_session.active_track_ref,
                tuple(prior_session.pending_goal_refs),
                warnings,
                tuple(prior_session.continuity_reminders),
            )
        if branch_track_ref not in pending_goal_refs:
            warnings = (_continuity_warning("missing-resume-anchor", branch_track_ref),)
            continuity_reminders = list(
                _merge_distinct_strings(
                    _without_track_reminders(continuity_reminders, branch_track_ref),
                    (make_resume_reminder(branch_track_ref), "resume-anchor-missing"),
                )
            )
            return (
                tuple(prior_session.branch_registry),
                prior_session.active_track_ref,
                tuple(prior_session.pending_goal_refs),
                warnings,
                tuple(continuity_reminders),
            )
        active_track_ref = branch_track_ref
        continuity_reminders = list(
            _without_track_reminders(continuity_reminders, branch_track_ref)
        )
        pending_goal_refs = [
            goal_ref for goal_ref in pending_goal_refs if goal_ref != branch_track_ref
        ]
        pending_goal_refs = _merge_unique_refs(tuple(pending_goal_refs), payload_goal_refs)
    elif operation is BranchOperation.MERGE:
        if branch_track_ref is None or branch_track_ref not in branch_registry:
            warnings = (_continuity_warning("missing-active-branch", branch_track_ref),)
            return (
                tuple(prior_session.branch_registry),
                prior_session.active_track_ref,
                tuple(prior_session.pending_goal_refs),
                warnings,
                tuple(prior_session.continuity_reminders),
            )
        merge_target_ref = _merge_target_ref(normalized_payload)
        if (
            merge_target_ref is not None
            and merge_target_ref != "main"
            and merge_target_ref not in branch_registry
        ):
            warnings = (_continuity_warning("illegal-merge-target", merge_target_ref),)
            return (
                tuple(prior_session.branch_registry),
                prior_session.active_track_ref,
                tuple(prior_session.pending_goal_refs),
                warnings,
                tuple(prior_session.continuity_reminders),
            )
        if branch_track_ref in pending_goal_refs or active_track_ref != branch_track_ref:
            warnings = (
                _continuity_warning(
                    "continuity-mismatch-after-suspension",
                    branch_track_ref,
                ),
            )
            return (
                tuple(prior_session.branch_registry),
                prior_session.active_track_ref,
                tuple(prior_session.pending_goal_refs),
                warnings,
                tuple(prior_session.continuity_reminders),
            )
        branch_registry = [
            branch_ref for branch_ref in branch_registry if branch_ref != branch_track_ref
        ]
        if not branch_registry:
            branch_registry = ["main"]
        active_track_ref = merge_target_ref or "main"
        continuity_reminders = list(
            _without_track_reminders(continuity_reminders, branch_track_ref)
        )
        pending_goal_refs = [
            goal_ref for goal_ref in pending_goal_refs if goal_ref != branch_track_ref
        ]
        pending_goal_refs = _merge_unique_refs(tuple(pending_goal_refs), payload_goal_refs)

    if active_track_ref != "main" and active_track_ref not in branch_registry:
        active_track_ref = "main"
    return (
        tuple(branch_registry),
        active_track_ref,
        tuple(pending_goal_refs),
        warnings,
        tuple(continuity_reminders),
    )


def _merge_distinct_strings(
    existing: tuple[str, ...],
    additions: tuple[str, ...],
) -> tuple[str, ...]:
    ordered = list(existing)
    for value in additions:
        if value not in ordered:
            ordered.append(value)
    return tuple(ordered)


def _without_track_reminders(
    reminders: list[str],
    track_ref: str | None,
) -> tuple[str, ...]:
    if track_ref is None:
        return tuple(
            reminder for reminder in reminders if reminder != "resume-anchor-missing"
        )
    return tuple(
        reminder
        for reminder in reminders
        if reminder != "resume-anchor-missing"
        and parse_resume_reminder_track(reminder) != track_ref
    )


def _build_environment_handle(
    normalized_payload: Mapping[str, Any],
) -> CommitmentEnvironmentHandle:
    available_query_kinds = {EXECUTION_TRACE}
    capability_tags = {"trace/read"}

    if _first_concrete_artifact_ref(normalized_payload) is not None:
        available_query_kinds.add(RESULT_ARTIFACT)
        capability_tags.add("artifact/read")
    if _as_non_empty_string(normalized_payload.get("external_record_ref")) is not None:
        available_query_kinds.add(EXTERNAL_RECORD)
        capability_tags.add("external-record/read")

    return CommitmentEnvironmentHandle(
        available_query_kinds=frozenset(available_query_kinds),
        capability_tags=frozenset(capability_tags),
    )


def _build_executive_environment_view(
    normalized_payload: Mapping[str, Any],
) -> ExecutiveEnvironmentView:
    available_query_kinds = {EXECUTION_TRACE}
    host_capability_tags = {
        "claude-host",
        "local-cli-runtime",
    }
    if _first_concrete_artifact_ref(normalized_payload) is not None:
        available_query_kinds.add(RESULT_ARTIFACT)
    if _as_non_empty_string(normalized_payload.get("external_record_ref")) is not None:
        available_query_kinds.add(EXTERNAL_RECORD)
    return ExecutiveEnvironmentView(
        available_query_kinds=frozenset(available_query_kinds),
        host_capability_tags=frozenset(host_capability_tags),
    )


def _build_support_snapshot(
    *,
    provisional_session: ClaudeRuntimeSession,
    bound_event: BoundClaudeHostEvent,
    dispatch_decision: DispatchDecision,
    warnings: Sequence[str],
    reminders: Sequence[str] = (),
) -> SupportSnapshot:
    approval_boundary_tags = (
        frozenset({"approval-required"})
        if dispatch_decision.lane is not DispatchLane.CHEAP
        else frozenset()
    )
    constraint_tags = frozenset({"runtime-warning"}) if warnings else frozenset()
    affordance_tags = frozenset(
        set(bound_event.lifecycle_surface.context_affordances)
        | set(bound_event.lifecycle_surface.tool_affordances)
        | set(bound_event.lifecycle_surface.turn_affordances)
    )
    return SupportSnapshot(
        trace=SupportTraceState(recent_events=(bound_event.observation.event,)),
        session=SupportSessionState(
            branch_registry=provisional_session.branch_registry,
            pending_goal_refs=provisional_session.pending_goal_refs,
            budget_history=provisional_session.budget_history,
            brake_history=provisional_session.brake_history,
            reminders=tuple(reminders),
        ),
        host=SupportHostState(
            affordance_tags=affordance_tags,
            approval_boundary_tags=approval_boundary_tags,
            constraint_tags=constraint_tags,
        ),
        exec_memory_pub=SupportExecMemoryState(),
    )


def _claude_host_native_opportunities(
    bound_event: BoundClaudeHostEvent,
) -> tuple[HostNativeOpportunity, ...]:
    runtime_tag = bound_event.lifecycle_surface.runtime_name
    return (
        HostNativeOpportunity(
            opportunity_ref="claude.runtime.probe.check",
            supported_families=frozenset({SoftControlFamily.CHECK}),
            realizable=False,
            degradation_reason="documented-probe-surface-unavailable",
            safer_fallback_family=SoftControlFamily.NEUTRAL,
            native_surface_tags=frozenset({runtime_tag, "bounded-probe"}),
            probe_contract=BoundedProbeContract(
                uncertainty_target="environment",
                allowed_family=SoftControlFamily.CHECK,
                timeout_seconds=2,
                output_cap=64,
                failure_classes=frozenset({"timed-out", "degraded", "unsupported"}),
            ),
        ),
        HostNativeOpportunity(
            opportunity_ref="claude.runtime.probe.seek-context",
            supported_families=frozenset({SoftControlFamily.SEEK_CONTEXT}),
            realizable=False,
            degradation_reason="documented-probe-surface-unavailable",
            safer_fallback_family=SoftControlFamily.NEUTRAL,
            native_surface_tags=frozenset({runtime_tag, "bounded-probe"}),
            probe_contract=BoundedProbeContract(
                uncertainty_target="host-capability",
                allowed_family=SoftControlFamily.SEEK_CONTEXT,
                timeout_seconds=5,
                output_cap=256,
                failure_classes=frozenset({"timed-out", "degraded", "unsupported"}),
            ),
        ),
    )


def _build_provenance_manifest(
    normalized_payload: Mapping[str, Any],
) -> ProvenanceManifest | None:
    evidence_refs = []
    artifact_ref = _first_concrete_artifact_ref(normalized_payload)
    if artifact_ref is not None:
        from cortex.core.commitments import ProvenanceEvidenceRef

        evidence_refs.append(
            ProvenanceEvidenceRef(
                source_family="result_artifact",
                reference_id=artifact_ref,
            )
        )
    external_record_ref = _as_non_empty_string(normalized_payload.get("external_record_ref"))
    if external_record_ref is not None:
        from cortex.core.commitments import ProvenanceEvidenceRef

        evidence_refs.append(
            ProvenanceEvidenceRef(
                source_family="external_record",
                reference_id=external_record_ref,
            )
        )
    if not evidence_refs:
        return None
    return ProvenanceManifest(evidence_refs=tuple(evidence_refs))


def _build_boundary_assessment(
    normalized_payload: Mapping[str, Any],
) -> tuple[BoundaryAssessment, tuple[str, ...]]:
    blocked = bool(normalized_payload.get("boundary_blocked"))
    reason_code = _as_non_empty_string(normalized_payload.get("boundary_reason_code"))
    warnings: tuple[str, ...] = ()
    if blocked and reason_code is None:
        blocked = False
        warnings = (
            "Ignored boundary_blocked=True because no boundary_reason_code was provided.",
        )
    return (
        BoundaryAssessment(
            blocked=blocked,
            reason_code=reason_code if blocked else None,
            boundary_tags=_as_tag_set(normalized_payload.get("boundary_tags")),
            capability_tags=_as_tag_set(normalized_payload.get("boundary_capability_tags")),
        ),
        warnings,
    )


def _budget_entry_for_lane(lane: DispatchLane) -> str:
    if lane is DispatchLane.CHEAP:
        return "shell-low"
    if lane is DispatchLane.CANDIDATE_BEARING:
        return "shell-medium"
    return "shell-high"


_MAX_TONIC_HISTORY = 16


def _bounded_tonic_history(
    prior: tuple[float, ...],
    tonic: "BrakeTonic | None",
) -> tuple[float, ...]:
    from cortex.sre.brake import BrakeTonic

    if tonic is None or not isinstance(tonic, BrakeTonic):
        return prior[-_MAX_TONIC_HISTORY:] if len(prior) > _MAX_TONIC_HISTORY else prior
    updated = prior + (tonic.tonic_pressure,)
    return updated[-_MAX_TONIC_HISTORY:]


def _commitment_summary_for_lane(
    lane: DispatchLane,
    commitment_result_kind: str | None,
) -> str | None:
    if lane is DispatchLane.CHEAP:
        return None
    if lane is DispatchLane.CANDIDATE_BEARING:
        return "candidate-only"
    return commitment_result_kind


def _first_concrete_artifact_ref(normalized_payload: Mapping[str, Any]) -> str | None:
    for key in ("result_artifact_ref", "artifact_ref"):
        value = _as_non_empty_string(normalized_payload.get(key))
        if value is not None:
            return value
    return None


def _as_tag_set(value: Any) -> frozenset[str]:
    if value is None:
        return frozenset()
    if isinstance(value, str):
        tag = value.strip()
        return frozenset({tag}) if tag else frozenset()
    if not isinstance(value, Sequence) or isinstance(value, (bytes, bytearray)):
        return frozenset()
    tags: list[str] = []
    for item in value:
        tag = _as_non_empty_string(item)
        if tag is not None and tag not in tags:
            tags.append(tag)
    return frozenset(tags)


def _as_non_empty_string(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


def _branch_operation(normalized_payload: Mapping[str, Any]) -> BranchOperation | None:
    raw_operation = _as_non_empty_string(normalized_payload.get("branch_operation"))
    if raw_operation is None:
        return None
    try:
        return BranchOperation(raw_operation)
    except ValueError:
        return None


def _continuity_track_ref(normalized_payload: Mapping[str, Any]) -> str | None:
    branch_track_ref = _as_non_empty_string(normalized_payload.get("branch_track_ref"))
    if branch_track_ref is not None:
        return branch_track_ref
    active_track_ref = _as_non_empty_string(normalized_payload.get("active_track_ref"))
    if active_track_ref == "main":
        return None
    return active_track_ref


def _merge_target_ref(normalized_payload: Mapping[str, Any]) -> str | None:
    return _as_non_empty_string(normalized_payload.get("merge_target_ref"))


def _pending_goal_refs_from_payload(normalized_payload: Mapping[str, Any]) -> tuple[str, ...]:
    value = normalized_payload.get("pending_goal_refs")
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return ()
    refs: list[str] = []
    for item in value:
        goal_ref = _as_non_empty_string(item)
        if goal_ref is not None and goal_ref not in refs:
            refs.append(goal_ref)
    return tuple(refs)


def _merge_unique_refs(
    existing_refs: tuple[str, ...],
    incoming_refs: Sequence[str],
) -> list[str]:
    ordered_refs: list[str] = []
    for goal_ref in existing_refs:
        if goal_ref not in ordered_refs:
            ordered_refs.append(goal_ref)
    for goal_ref in incoming_refs:
        if goal_ref not in ordered_refs:
            ordered_refs.append(goal_ref)
    return ordered_refs


def _continuity_warning(reason_code: str, subject: str | None) -> str:
    if subject is None:
        return f"continuity-rejected:{reason_code}"
    return f"continuity-rejected:{reason_code}:{subject}"


def _admissible_families(
    executive_state: ReferenceExecutiveState,
) -> tuple[SoftControlFamily, ...]:
    admissible: list[SoftControlFamily] = []
    for family in SoftControlFamily:
        if family is SoftControlFamily.NEUTRAL or family in executive_state.mode_and_gating.family_mask:
            admissible.append(family)
    return tuple(admissible)


def _dominant_uncertainty_sources(
    executive_state: ReferenceExecutiveState,
) -> tuple[str, ...]:
    ranked = sorted(
        executive_state.uncertainty_monitoring.classwise_uncertainty,
        key=lambda estimate: (-estimate.level, estimate.class_tag),
    )
    return tuple(estimate.class_tag for estimate in ranked[:2])


def _realize_family(
    selected_family: SoftControlFamily,
    *,
    brake_state: BrakeState,
    dominant_uncertainty_sources: tuple[str, ...],
    feedback_pressure_tags: frozenset[str],
) -> tuple[SoftControlFamily, tuple[str, ...]]:
    if selected_family in {
        SoftControlFamily.NEUTRAL,
        SoftControlFamily.CHECK,
        SoftControlFamily.BRAKE,
    }:
        return selected_family, ()
    if (
        brake_state is BrakeState.GUARDED
        and _has_guarded_feedback_enforcement_pressure(feedback_pressure_tags)
    ):
        if any(source in {"evidence", "environment"} for source in dominant_uncertainty_sources):
            realized_family = SoftControlFamily.CHECK
        else:
            realized_family = SoftControlFamily.NEUTRAL
        return (
            realized_family,
            (
                f"guarded-feedback-enforced:{selected_family.value}:{realized_family.value}",
            ),
        )
    if brake_state is not BrakeState.LATCHED:
        return selected_family, ()
    if any(source in {"evidence", "environment"} for source in dominant_uncertainty_sources):
        realized_family = SoftControlFamily.CHECK
    else:
        realized_family = SoftControlFamily.NEUTRAL
    return (
        realized_family,
        (
            f"latched-brake-enforced:{selected_family.value}:{realized_family.value}",
        ),
    )


def _has_guarded_feedback_enforcement_pressure(
    feedback_pressure_tags: frozenset[str],
) -> bool:
    return bool(
        {
            "feedback:override-pressure",
            "feedback:rejection-pressure",
        }
        & feedback_pressure_tags
    )


def _primary_reason(warnings: tuple[str, ...]) -> str | None:
    for warning in warnings:
        if warning.startswith(
            ("latched-brake-enforced:", "guarded-feedback-enforced:")
        ):
            return warning
    return warnings[0] if warnings else None


_ALLOCATION_DIAGNOSTICS_KEYS = (
    "alpha_t",
    "activation_threshold",
    "selected_delta_over_neutral",
    "chi_t",
    "risk_weight",
    "brake_tonic",
    "rejected_cheaper_families",
    "probe_path_state",
    "probe_unavailable_reason",
    "probe_result_class",
    "verification_state",
    "explainability_profile",
    "anti_thrash",
    "scores",
)
_RISK_WEIGHT_DIAGNOSTICS_KEYS = (
    "fn_cost_weight",
    "fp_cost_weight",
    "adjustment_sign",
    "dominant_risk_source",
)
_BRAKE_TONIC_DIAGNOSTICS_KEYS = (
    "tonic_pressure",
)
_ANTI_THRASH_DIAGNOSTICS_KEYS = (
    "state",
    "target_family",
    "repetition_tax",
    "reason_tags",
)
_AUDIT_PROJECTION_KEYS = (
    "selected_family",
    "realized_family",
    "dominant_uncertainty_sources",
    "activation_threshold",
    "selected_delta_over_neutral",
    "rejected_cheaper_families",
    "verification_state",
    "explainability_profile",
    "probe_path_state",
    "probe_result_class",
    "probe_unavailable_reason",
)
_ALLOCATION_SCORE_KEYS = (
    "family",
    "online_score",
    "memory_score",
    "allocated_score",
    "activation_threshold",
    "admissible",
    "reason_tags",
)


def _validate_risk_weight_diagnostics_payload(
    payload: dict[str, Any], label: str
) -> None:
    if not isinstance(payload, dict):
        actual_type = type(payload).__name__
        raise TypeError(f"{label} must be dict[str, Any], got {actual_type}.")
    if tuple(payload) != _RISK_WEIGHT_DIAGNOSTICS_KEYS:
        raise ValueError(
            f"{label} must preserve the locked key order {_RISK_WEIGHT_DIAGNOSTICS_KEYS!r}."
        )
    for key in ("fn_cost_weight", "fp_cost_weight"):
        value = payload[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            actual_type = type(value).__name__
            raise TypeError(f"{label}.{key} must be numeric, got {actual_type}.")
        if not 0.0 <= float(value) <= 1.0:
            raise ValueError(f"{label}.{key} must be in [0.0, 1.0].")
    if payload["adjustment_sign"] not in {"balanced", "fn-heavy", "fp-heavy"}:
        raise ValueError(
            f"{label}.adjustment_sign must be one of ['balanced', 'fn-heavy', 'fp-heavy']."
        )
    dominant = payload["dominant_risk_source"]
    if dominant is not None and not (isinstance(dominant, str) and dominant.strip()):
        raise ValueError(
            f"{label}.dominant_risk_source must be non-empty after trimming when provided."
        )


def _validate_brake_tonic_diagnostics_payload(
    payload: dict[str, Any] | None, label: str
) -> None:
    if payload is None:
        return
    if not isinstance(payload, dict):
        actual_type = type(payload).__name__
        raise TypeError(f"{label} must be dict[str, Any] | None, got {actual_type}.")
    if tuple(payload) != _BRAKE_TONIC_DIAGNOSTICS_KEYS:
        raise ValueError(
            f"{label} must preserve the locked key order {_BRAKE_TONIC_DIAGNOSTICS_KEYS!r}."
        )
    for key in ("tonic_pressure",):
        value = payload[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            actual_type = type(value).__name__
            raise TypeError(f"{label}.{key} must be numeric, got {actual_type}.")
        if not 0.0 <= float(value) <= 1.0:
            raise ValueError(f"{label}.{key} must be in [0.0, 1.0].")


def _validate_allocation_diagnostics_payload(payload: dict[str, Any], label: str) -> None:
    if not isinstance(payload, dict):
        actual_type = type(payload).__name__
        raise TypeError(f"{label} must be dict[str, Any], got {actual_type}.")
    if tuple(payload) != _ALLOCATION_DIAGNOSTICS_KEYS:
        raise ValueError(
            f"{label} must preserve the locked key order {_ALLOCATION_DIAGNOSTICS_KEYS!r}."
        )
    for key in ("alpha_t", "activation_threshold", "selected_delta_over_neutral", "chi_t"):
        value = payload[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            actual_type = type(value).__name__
            raise TypeError(f"{label}.{key} must be numeric, got {actual_type}.")
    _validate_risk_weight_diagnostics_payload(payload["risk_weight"], f"{label}.risk_weight")
    _validate_brake_tonic_diagnostics_payload(payload["brake_tonic"], f"{label}.brake_tonic")
    rejected_cheaper_families = payload["rejected_cheaper_families"]
    if not isinstance(rejected_cheaper_families, list):
        actual_type = type(rejected_cheaper_families).__name__
        raise TypeError(
            f"{label}.rejected_cheaper_families must be list[str], got {actual_type}."
        )
    if any(
        not (isinstance(family, str) and family.strip())
        for family in rejected_cheaper_families
    ):
        raise ValueError(
            f"{label}.rejected_cheaper_families must contain only non-empty strings."
        )
    if payload["probe_path_state"] not in {"available", "unavailable", "absent"}:
        raise ValueError(
            f"{label}.probe_path_state must be one of ['absent', 'available', 'unavailable']."
        )
    probe_unavailable_reason = payload["probe_unavailable_reason"]
    if probe_unavailable_reason is not None and not (
        isinstance(probe_unavailable_reason, str) and probe_unavailable_reason.strip()
    ):
        raise ValueError(
            f"{label}.probe_unavailable_reason must be non-empty after trimming when provided."
        )
    if payload["probe_path_state"] == "unavailable" and probe_unavailable_reason is None:
        raise ValueError(
            f"{label}.probe_unavailable_reason is required when probe_path_state is `unavailable`."
        )
    if payload["probe_path_state"] != "unavailable" and probe_unavailable_reason is not None:
        raise ValueError(
            f"{label}.probe_unavailable_reason is only valid when probe_path_state is `unavailable`."
        )
    probe_result_class = payload["probe_result_class"]
    if probe_result_class is not None and not (
        isinstance(probe_result_class, str) and probe_result_class.strip()
    ):
        raise ValueError(
            f"{label}.probe_result_class must be non-empty after trimming when provided."
        )
    for key in ("verification_state", "explainability_profile"):
        if not (isinstance(payload[key], str) and payload[key].strip()):
            raise ValueError(f"{label}.{key} must be non-empty after trimming.")
    anti_thrash = payload["anti_thrash"]
    if not isinstance(anti_thrash, dict):
        actual_type = type(anti_thrash).__name__
        raise TypeError(f"{label}.anti_thrash must be dict[str, Any], got {actual_type}.")
    if tuple(anti_thrash) != _ANTI_THRASH_DIAGNOSTICS_KEYS:
        raise ValueError(
            f"{label}.anti_thrash must preserve the locked key order {_ANTI_THRASH_DIAGNOSTICS_KEYS!r}."
        )
    if anti_thrash["state"] not in {"inactive", "taxed", "reopened"}:
        raise ValueError(
            f"{label}.anti_thrash.state must be one of ['inactive', 'taxed', 'reopened']."
        )
    target_family = anti_thrash["target_family"]
    if target_family is not None and not (
        isinstance(target_family, str) and target_family.strip()
    ):
        raise ValueError(
            f"{label}.anti_thrash.target_family must be non-empty after trimming when provided."
        )
    repetition_tax = anti_thrash["repetition_tax"]
    if isinstance(repetition_tax, bool) or not isinstance(repetition_tax, (int, float)):
        actual_type = type(repetition_tax).__name__
        raise TypeError(
            f"{label}.anti_thrash.repetition_tax must be numeric, got {actual_type}."
        )
    reason_tags = anti_thrash["reason_tags"]
    if not isinstance(reason_tags, list):
        actual_type = type(reason_tags).__name__
        raise TypeError(
            f"{label}.anti_thrash.reason_tags must be list[str], got {actual_type}."
        )
    if any(not (isinstance(tag, str) and tag.strip()) for tag in reason_tags):
        raise ValueError(
            f"{label}.anti_thrash.reason_tags must contain only non-empty values after trimming."
        )
    scores = payload["scores"]
    if not isinstance(scores, list):
        actual_type = type(scores).__name__
        raise TypeError(f"{label}.scores must be list[dict[str, Any]], got {actual_type}.")
    for index, score in enumerate(scores):
        score_label = f"{label}.scores[{index}]"
        if not isinstance(score, dict):
            actual_type = type(score).__name__
            raise TypeError(f"{score_label} must be dict[str, Any], got {actual_type}.")
        if tuple(score) != _ALLOCATION_SCORE_KEYS:
            raise ValueError(
                f"{score_label} must preserve the locked key order {_ALLOCATION_SCORE_KEYS!r}."
            )
        if not (isinstance(score["family"], str) and score["family"].strip()):
            raise ValueError(f"{score_label}.family must be non-empty after trimming.")
        for key in ("online_score", "memory_score", "allocated_score", "activation_threshold"):
            value = score[key]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                actual_type = type(value).__name__
                raise TypeError(f"{score_label}.{key} must be numeric, got {actual_type}.")
        if not isinstance(score["admissible"], bool):
            actual_type = type(score["admissible"]).__name__
            raise TypeError(f"{score_label}.admissible must be bool, got {actual_type}.")
        reason_tags = score["reason_tags"]
        if not isinstance(reason_tags, list):
            actual_type = type(reason_tags).__name__
            raise TypeError(f"{score_label}.reason_tags must be list[str], got {actual_type}.")
        if any(not (isinstance(tag, str) and tag.strip()) for tag in reason_tags):
            raise ValueError(f"{score_label}.reason_tags must contain only non-empty strings.")


def _validate_audit_projection_payload(payload: dict[str, Any], label: str) -> None:
    if not isinstance(payload, dict):
        actual_type = type(payload).__name__
        raise TypeError(f"{label} must be dict[str, Any], got {actual_type}.")
    if tuple(payload) != _AUDIT_PROJECTION_KEYS:
        raise ValueError(
            f"{label} must preserve the locked key order {_AUDIT_PROJECTION_KEYS!r}."
        )
    for key in (
        "selected_family",
        "realized_family",
        "verification_state",
        "explainability_profile",
        "probe_path_state",
    ):
        if not (isinstance(payload[key], str) and payload[key].strip()):
            raise ValueError(f"{label}.{key} must be non-empty after trimming.")
    if payload["probe_path_state"] not in {"available", "unavailable", "absent"}:
        raise ValueError(
            f"{label}.probe_path_state must be one of ['absent', 'available', 'unavailable']."
        )
    for key in ("activation_threshold", "selected_delta_over_neutral"):
        value = payload[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            actual_type = type(value).__name__
            raise TypeError(f"{label}.{key} must be numeric, got {actual_type}.")
    dominant_uncertainty_sources = payload["dominant_uncertainty_sources"]
    if not isinstance(dominant_uncertainty_sources, list):
        actual_type = type(dominant_uncertainty_sources).__name__
        raise TypeError(
            f"{label}.dominant_uncertainty_sources must be list[str], got {actual_type}."
        )
    if any(
        not (isinstance(source, str) and source.strip())
        for source in dominant_uncertainty_sources
    ):
        raise ValueError(
            f"{label}.dominant_uncertainty_sources must contain only non-empty strings."
        )
    rejected_cheaper_families = payload["rejected_cheaper_families"]
    if not isinstance(rejected_cheaper_families, list):
        actual_type = type(rejected_cheaper_families).__name__
        raise TypeError(
            f"{label}.rejected_cheaper_families must be list[str], got {actual_type}."
        )
    if any(
        not (isinstance(family, str) and family.strip())
        for family in rejected_cheaper_families
    ):
        raise ValueError(
            f"{label}.rejected_cheaper_families must contain only non-empty strings."
        )
    probe_result_class = payload["probe_result_class"]
    if probe_result_class is not None and not (
        isinstance(probe_result_class, str) and probe_result_class.strip()
    ):
        raise ValueError(
            f"{label}.probe_result_class must be non-empty after trimming when provided."
        )
    probe_unavailable_reason = payload["probe_unavailable_reason"]
    if probe_unavailable_reason is not None and not (
        isinstance(probe_unavailable_reason, str) and probe_unavailable_reason.strip()
    ):
        raise ValueError(
            f"{label}.probe_unavailable_reason must be non-empty after trimming when provided."
        )


def _copy_allocation_diagnostics_payload(payload: dict[str, Any]) -> dict[str, Any]:
    risk_weight_payload = payload["risk_weight"]
    brake_tonic_payload = payload["brake_tonic"]
    return {
        "alpha_t": payload["alpha_t"],
        "activation_threshold": payload["activation_threshold"],
        "selected_delta_over_neutral": payload["selected_delta_over_neutral"],
        "chi_t": payload["chi_t"],
        "risk_weight": {
            "fn_cost_weight": risk_weight_payload["fn_cost_weight"],
            "fp_cost_weight": risk_weight_payload["fp_cost_weight"],
            "adjustment_sign": risk_weight_payload["adjustment_sign"],
            "dominant_risk_source": risk_weight_payload["dominant_risk_source"],
        },
        "brake_tonic": (
            None
            if brake_tonic_payload is None
            else {
                "tonic_pressure": brake_tonic_payload["tonic_pressure"],
            }
        ),
        "rejected_cheaper_families": list(payload["rejected_cheaper_families"]),
        "probe_path_state": payload["probe_path_state"],
        "probe_unavailable_reason": payload["probe_unavailable_reason"],
        "probe_result_class": payload["probe_result_class"],
        "verification_state": payload["verification_state"],
        "explainability_profile": payload["explainability_profile"],
        "anti_thrash": {
            "state": payload["anti_thrash"]["state"],
            "target_family": payload["anti_thrash"]["target_family"],
            "repetition_tax": payload["anti_thrash"]["repetition_tax"],
            "reason_tags": list(payload["anti_thrash"]["reason_tags"]),
        },
        "scores": [
            {
                "family": score["family"],
                "online_score": score["online_score"],
                "memory_score": score["memory_score"],
                "allocated_score": score["allocated_score"],
                "activation_threshold": score["activation_threshold"],
                "admissible": score["admissible"],
                "reason_tags": list(score["reason_tags"]),
            }
            for score in payload["scores"]
        ],
    }


def _copy_audit_projection_payload(payload: dict[str, Any]) -> dict[str, Any]:
    _validate_audit_projection_payload(
        payload,
        "_copy_audit_projection_payload.payload",
    )
    return {
        "selected_family": payload["selected_family"],
        "realized_family": payload["realized_family"],
        "dominant_uncertainty_sources": list(payload["dominant_uncertainty_sources"]),
        "activation_threshold": payload["activation_threshold"],
        "selected_delta_over_neutral": payload["selected_delta_over_neutral"],
        "rejected_cheaper_families": list(payload["rejected_cheaper_families"]),
        "verification_state": payload["verification_state"],
        "explainability_profile": payload["explainability_profile"],
        "probe_path_state": payload["probe_path_state"],
        "probe_result_class": payload["probe_result_class"],
        "probe_unavailable_reason": payload["probe_unavailable_reason"],
    }


def _should_emit_audit_projection(explainability_profile: str) -> bool:
    return explainability_profile in {"focused", "structured"}


__all__ = [
    "ClaudeControlLedger",
    "ClaudeRuntimeSession",
    "ClaudeRuntimeStepResult",
    "run_claude_runtime_step",
]
```

### `cortex/hosts/claude/host_control.py`

```python
"""Bounded outbound Claude host-control composition over the accepted runtime shell."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any

from .runtime import ClaudeRuntimeSession, run_claude_runtime_step
from .cli import build_claude_cli_record
from .ingress import parse_claude_host_event_envelope
from .host_transport import (
    ClaudeMessageStreamTransportError,
    execute_claude_message_stream,
)

_ACTION_TAG = "claude-message-stream"
_TOP_LEVEL_KEYS = frozenset({"action_tag", "request"})
_REQUEST_KEYS = frozenset(
    {
        "model",
        "input",
        "system",
        "metadata",
        "max_output_tokens",
        "stream",
        "audit_intensity",
    }
)
_AUDIT_INTENSITIES = frozenset({"minimal", "focused", "structured"})

ClaudeMessageStreamTransport = Callable[
    ["ClaudeHostControlRequest"],
    list[dict[str, Any]],
]


@dataclass(frozen=True, slots=True)
class ClaudeHostControlRequest:
    action_tag: str
    model: str
    input_text: str
    max_output_tokens: int
    system: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    audit_intensity: str = "minimal"

    def __post_init__(self) -> None:
        if self.action_tag != _ACTION_TAG:
            raise ValueError(
                f"ClaudeHostControlRequest.action_tag must be `{_ACTION_TAG}`."
            )
        if not (isinstance(self.model, str) and self.model.strip()):
            raise ValueError(
                "ClaudeHostControlRequest.model must be non-empty after trimming."
            )
        if not (isinstance(self.input_text, str) and self.input_text.strip()):
            raise ValueError(
                "ClaudeHostControlRequest.input_text must be non-empty after trimming."
            )
        if self.system is not None and not (
            isinstance(self.system, str) and self.system.strip()
        ):
            raise ValueError(
                "ClaudeHostControlRequest.system must be non-empty after trimming when provided."
            )
        if not isinstance(self.metadata, dict):
            actual_type = type(self.metadata).__name__
            raise TypeError(
                "ClaudeHostControlRequest.metadata must be dict[str, Any], "
                f"got {actual_type}."
            )
        if any(not (isinstance(key, str) and key.strip()) for key in self.metadata):
            raise ValueError(
                "ClaudeHostControlRequest.metadata keys must be non-empty strings after trimming."
            )
        if isinstance(self.max_output_tokens, bool) or not isinstance(
            self.max_output_tokens,
            int,
        ):
            actual_type = type(self.max_output_tokens).__name__
            raise TypeError(
                "ClaudeHostControlRequest.max_output_tokens must be int, "
                f"got {actual_type}."
            )
        if self.max_output_tokens <= 0:
            raise ValueError(
                "ClaudeHostControlRequest.max_output_tokens must be positive."
            )
        if self.audit_intensity not in _AUDIT_INTENSITIES:
            raise ValueError(
                "ClaudeHostControlRequest.audit_intensity must be one of "
                f"{sorted(_AUDIT_INTENSITIES)!r}."
            )

    def as_payload(self) -> dict[str, Any]:
        request_payload: dict[str, Any] = {
            "model": self.model,
            "input": self.input_text,
            "max_output_tokens": self.max_output_tokens,
        }
        if self.system is not None:
            request_payload["system"] = self.system
        if self.metadata:
            request_payload["metadata"] = dict(self.metadata)
        if self.audit_intensity != "minimal":
            request_payload["audit_intensity"] = self.audit_intensity
        return {
            "action_tag": self.action_tag,
            "request": request_payload,
        }


@dataclass(frozen=True, slots=True)
class ClaudeHostControlResult:
    action_tag: str
    records: tuple[dict[str, Any], ...]

    def __post_init__(self) -> None:
        if self.action_tag != _ACTION_TAG:
            raise ValueError(
                f"ClaudeHostControlResult.action_tag must be `{_ACTION_TAG}`."
            )
        if any(not isinstance(record, dict) for record in self.records):
            raise TypeError(
                "ClaudeHostControlResult.records must contain only dict[str, Any] records."
            )

    def as_payload(self) -> dict[str, Any]:
        return {
            "action_tag": self.action_tag,
            "records": [dict(record) for record in self.records],
        }


def run_claude_host_control(
    request: ClaudeHostControlRequest,
    session: ClaudeRuntimeSession | None = None,
    *,
    transport: ClaudeMessageStreamTransport | None = None,
) -> tuple[ClaudeHostControlResult, ClaudeRuntimeSession]:
    if not isinstance(request, ClaudeHostControlRequest):
        actual_type = type(request).__name__
        raise TypeError(
            "run_claude_host_control.request must be ClaudeHostControlRequest, "
            f"got {actual_type}."
        )
    current_session = _coerce_session(session)
    transport_callable = transport if transport is not None else execute_claude_message_stream
    if not callable(transport_callable):
        actual_type = type(transport_callable).__name__
        raise TypeError(
            "run_claude_host_control.transport must be callable when provided, "
            f"got {actual_type}."
        )

    raw_events = transport_callable(request)
    if not raw_events:
        raise ClaudeMessageStreamTransportError(
            "Claude interaction stream returned zero host events."
        )

    action_session_id = current_session.session_id or "cl-session-1"
    records: list[dict[str, Any]] = []
    for raw_event in raw_events:
        if not isinstance(raw_event, Mapping):
            actual_type = type(raw_event).__name__
            raise ClaudeMessageStreamTransportError(
                "Claude interaction stream must yield JSON-object events, "
                f"got {actual_type}."
            )
        try:
            normalized_event = dict(raw_event)
            normalized_event.setdefault("session_id", action_session_id)
            envelope = parse_claude_host_event_envelope(normalized_event)
            step_result = run_claude_runtime_step(
                envelope.event_type,
                envelope.payload,
                current_session,
                audit_intensity=request.audit_intensity,
            )
        except (TypeError, ValueError) as exc:
            raise ClaudeMessageStreamTransportError(
                f"Claude interaction stream yielded an unlawful host event: {exc}"
            ) from exc
        records.append(build_claude_cli_record(step_result))
        current_session = step_result.session

    return ClaudeHostControlResult(
        action_tag=request.action_tag,
        records=tuple(records),
    ), current_session


def _coerce_claude_host_control_request(
    payload: Mapping[str, Any],
) -> ClaudeHostControlRequest:
    if not isinstance(payload, Mapping):
        actual_type = type(payload).__name__
        raise TypeError(
            "Claude host control request payload must be a mapping, "
            f"got {actual_type}."
        )
    unknown_top_level_keys = sorted(set(payload) - _TOP_LEVEL_KEYS)
    if unknown_top_level_keys:
        raise ValueError(
            "Claude host control request accepts only `action_tag` and `request`; "
            f"got unsupported top-level keys: {', '.join(unknown_top_level_keys)}."
        )
    if "action_tag" not in payload:
        raise ValueError("Claude host control request must include `action_tag`.")
    if "request" not in payload:
        raise ValueError("Claude host control request must include `request`.")

    request_payload = payload["request"]
    if not isinstance(request_payload, Mapping):
        actual_type = type(request_payload).__name__
        raise TypeError(
            "Claude host control request `request` must be an object, "
            f"got {actual_type}."
        )

    unknown_request_keys = sorted(set(request_payload) - _REQUEST_KEYS)
    if unknown_request_keys:
        raise ValueError(
            "Claude host control request uses a strict text-only whitelist; "
            f"unsupported request keys: {', '.join(unknown_request_keys)}."
        )

    if "stream" in request_payload and request_payload["stream"] is not True:
        raise ValueError(
            "Claude host control request `stream` must be `true` when provided."
        )

    model = _required_non_empty_string(
        request_payload.get("model"),
        "Claude host control request `request.model`",
    )
    input_text = _required_non_empty_string(
        request_payload.get("input"),
        "Claude host control request `request.input`",
    )
    max_output_tokens = _required_positive_int(
        request_payload.get("max_output_tokens"),
        "Claude host control request `request.max_output_tokens`",
    )
    system = _optional_non_empty_string(
        request_payload.get("system"),
        "Claude host control request `request.system`",
    )
    metadata = _metadata_dict(request_payload.get("metadata"))
    audit_intensity = _audit_intensity(
        request_payload.get("audit_intensity"),
        "Claude host control request `request.audit_intensity`",
    )
    action_tag = _required_non_empty_string(
        payload.get("action_tag"),
        "Claude host control request `action_tag`",
    )
    return ClaudeHostControlRequest(
        action_tag=action_tag,
        model=model,
        input_text=input_text,
        max_output_tokens=max_output_tokens,
        system=system,
        metadata=metadata,
        audit_intensity=audit_intensity,
    )


def _coerce_session(session: ClaudeRuntimeSession | None) -> ClaudeRuntimeSession:
    if session is None:
        return ClaudeRuntimeSession()
    if not isinstance(session, ClaudeRuntimeSession):
        actual_type = type(session).__name__
        raise TypeError(
            "run_claude_host_control.session must be ClaudeRuntimeSession | None, "
            f"got {actual_type}."
        )
    return session


def _required_non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str):
        actual_type = type(value).__name__
        raise TypeError(f"{label} must be a string, got {actual_type}.")
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"{label} must be non-empty after trimming.")
    return stripped


def _optional_non_empty_string(value: Any, label: str) -> str | None:
    if value is None:
        return None
    return _required_non_empty_string(value, label)


def _required_positive_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        actual_type = type(value).__name__
        raise TypeError(f"{label} must be an integer, got {actual_type}.")
    if value <= 0:
        raise ValueError(f"{label} must be positive when provided.")
    return value


def _audit_intensity(value: Any, label: str) -> str:
    if value is None:
        return "minimal"
    if not isinstance(value, str):
        actual_type = type(value).__name__
        raise TypeError(f"{label} must be a string, got {actual_type}.")
    normalized = value.strip()
    if normalized not in _AUDIT_INTENSITIES:
        raise ValueError(f"{label} must be one of {sorted(_AUDIT_INTENSITIES)!r}.")
    return normalized


def _metadata_dict(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        actual_type = type(value).__name__
        raise TypeError(
            "Claude host control request `request.metadata` must be an object, "
            f"got {actual_type}."
        )
    metadata = dict(value)
    if any(not (isinstance(key, str) and key.strip()) for key in metadata):
        raise ValueError(
            "Claude host control request `request.metadata` keys must be non-empty strings after trimming."
        )
    return metadata


__all__ = [
    "ClaudeHostControlRequest",
    "ClaudeHostControlResult",
    "ClaudeMessageStreamTransportError",
    "run_claude_host_control",
]
```

### `cortex/hosts/claude/ingress.py`

```python
"""Raw transcript ingress parsing for the Claude runtime shell."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from cortex.drivers.claude_host import is_raw_claude_host_event_name


@dataclass(frozen=True, slots=True)
class ClaudeHostEventEnvelope:
    event_type: str
    payload: dict[str, Any]

    def __post_init__(self) -> None:
        if not isinstance(self.event_type, str) or not self.event_type.strip():
            raise ValueError(
                "ClaudeHostEventEnvelope.event_type must be a non-empty raw Claude host event name."
            )
        if not is_raw_claude_host_event_name(self.event_type):
            raise ValueError(
                "ClaudeHostEventEnvelope.event_type must be a raw Claude host event name, "
                "not a canonical Cortex event name."
            )
        if not isinstance(self.payload, dict):
            actual_type = type(self.payload).__name__
            raise TypeError(
                "ClaudeHostEventEnvelope.payload must be dict[str, Any], "
                f"got {actual_type}."
            )


def parse_claude_host_event_envelope(record: Mapping[str, Any]) -> ClaudeHostEventEnvelope:
    if not isinstance(record, Mapping):
        actual_type = type(record).__name__
        raise TypeError(
            "parse_claude_host_event_envelope.record must be a mapping, "
            f"got {actual_type}."
        )
    if "event_name" in record or "payload" in record:
        raise ValueError(
            "G2 expects raw host transcript records only; wrapper and mixed "
            "wrapper/transcript shapes that include `event_name` or `payload` are unlawful."
        )
    if "type" not in record:
        raise ValueError("Raw Claude host transcript record must include `type`.")

    event_type = record["type"]
    if not isinstance(event_type, str):
        actual_type = type(event_type).__name__
        raise TypeError(
            "Raw Claude host transcript record `type` must be a string, "
            f"got {actual_type}."
        )
    if not is_raw_claude_host_event_name(event_type):
        raise ValueError(
            "Raw Claude host transcript record `type` must be a raw Claude host event name, "
            "not a canonical Cortex event name."
        )

    payload = {key: value for key, value in record.items() if key != "type"}
    return ClaudeHostEventEnvelope(event_type=event_type, payload=payload)


__all__ = ["ClaudeHostEventEnvelope", "parse_claude_host_event_envelope"]
```

### `cortex/hosts/claude/session_io.py`

```python
"""Bounded persisted continuation carrier for the Claude runtime shell."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from cortex.hosts._executive_closure import (
    canonicalize_executive_modulator_memory,
    executive_modulator_memory_payload,
)
from cortex.hosts.claude.runtime import ClaudeRuntimeSession
from cortex.sre.feedback import ReferenceRealizationFeedback, ReferenceRealizationFeedbackWindow
from cortex.sre.goals import normalize_continuity_reminder
from cortex.sre.modulators import ExecutiveModulatorMemory
from cortex.sre.operator_routing import OperatorTaskMode

_ARTIFACT_KIND = "claude-runtime-session"
_ARTIFACT_VERSION = 1
_TOP_LEVEL_KEYS = (
    "artifact_kind",
    "artifact_version",
    "continuity_truth",
    "control_residue",
)
_CONTINUITY_TRUTH_KEYS = (
    "session_id",
    "event_index",
    "branch_registry",
    "active_track_ref",
    "pending_goal_refs",
    "continuity_reminders",
)
_LEGACY_CONTINUITY_TRUTH_KEYS = (
    "session_id",
    "event_index",
    "branch_registry",
    "active_track_ref",
    "pending_goal_refs",
)
_CONTROL_RESIDUE_KEYS = (
    "last_budget_band",
    "last_commitment_result_summary",
    "last_realization_feedback",
    "feedback_window",
    "executive_modulator_memory",
    "brake_tonic_history",
)
_PRE_TONIC_HISTORY_CONTROL_RESIDUE_KEYS = (
    "last_budget_band",
    "last_commitment_result_summary",
    "last_realization_feedback",
    "feedback_window",
    "executive_modulator_memory",
)
_PRE_MODULATOR_CONTROL_RESIDUE_KEYS = (
    "last_budget_band",
    "last_commitment_result_summary",
    "last_realization_feedback",
    "feedback_window",
)
_ALLOWED_BUDGET_BANDS = frozenset({"low", "medium", "high"})


@dataclass(frozen=True, slots=True)
class ClaudeRuntimeSessionArtifact:
    artifact_kind: str = _ARTIFACT_KIND
    artifact_version: int = _ARTIFACT_VERSION
    session_id: str | None = None
    event_index: int = 0
    branch_registry: tuple[str, ...] = ("main",)
    active_track_ref: str = "main"
    pending_goal_refs: tuple[str, ...] = ()
    continuity_reminders: tuple[str, ...] = ()
    last_budget_band: str | None = None
    last_commitment_result_summary: str | None = None
    last_realization_feedback: ReferenceRealizationFeedback | None = None
    feedback_window: ReferenceRealizationFeedbackWindow = field(
        default_factory=ReferenceRealizationFeedbackWindow
    )
    executive_modulator_memory: ExecutiveModulatorMemory | None = None
    brake_tonic_history: tuple[float, ...] = ()

    def __post_init__(self) -> None:
        if self.artifact_kind != _ARTIFACT_KIND:
            raise ValueError(
                f"ClaudeRuntimeSessionArtifact.artifact_kind must be `{_ARTIFACT_KIND}`."
            )
        if self.artifact_version != _ARTIFACT_VERSION:
            raise ValueError(
                f"ClaudeRuntimeSessionArtifact.artifact_version must be `{_ARTIFACT_VERSION}`."
            )
        if self.session_id is not None and not (
            isinstance(self.session_id, str) and self.session_id.strip()
        ):
            raise ValueError(
                "ClaudeRuntimeSessionArtifact.session_id must be non-empty after trimming when provided."
            )
        if isinstance(self.event_index, bool) or not isinstance(self.event_index, int):
            actual_type = type(self.event_index).__name__
            raise TypeError(
                "ClaudeRuntimeSessionArtifact.event_index must be a non-negative integer, "
                f"got {actual_type}."
            )
        if self.event_index < 0:
            raise ValueError("ClaudeRuntimeSessionArtifact.event_index must be non-negative.")
        if any(not (isinstance(ref, str) and ref.strip()) for ref in self.branch_registry):
            raise ValueError(
                "ClaudeRuntimeSessionArtifact.branch_registry must contain only non-empty values after trimming."
            )
        if not (isinstance(self.active_track_ref, str) and self.active_track_ref.strip()):
            raise ValueError(
                "ClaudeRuntimeSessionArtifact.active_track_ref must be non-empty after trimming."
            )
        if self.active_track_ref != "main" and self.active_track_ref not in self.branch_registry:
            raise ValueError(
                "ClaudeRuntimeSessionArtifact.active_track_ref must be `main` or a member of branch_registry."
            )
        if any(not (isinstance(ref, str) and ref.strip()) for ref in self.pending_goal_refs):
            raise ValueError(
                "ClaudeRuntimeSessionArtifact.pending_goal_refs must contain only non-empty values after trimming."
            )
        if any(
            not (isinstance(reminder, str) and reminder.strip())
            for reminder in self.continuity_reminders
        ):
            raise ValueError(
                "ClaudeRuntimeSessionArtifact.continuity_reminders must contain only non-empty values after trimming."
            )
        if self.last_budget_band is not None and self.last_budget_band not in _ALLOWED_BUDGET_BANDS:
            raise ValueError(
                "ClaudeRuntimeSessionArtifact.last_budget_band must be one of "
                "`low`, `medium`, `high`, or `None`."
            )
        if self.last_commitment_result_summary is not None and not (
            isinstance(self.last_commitment_result_summary, str)
            and self.last_commitment_result_summary.strip()
        ):
            raise ValueError(
                "ClaudeRuntimeSessionArtifact.last_commitment_result_summary must be non-empty after trimming when provided."
            )
        if self.last_realization_feedback is not None and not isinstance(
            self.last_realization_feedback,
            ReferenceRealizationFeedback,
        ):
            actual_type = type(self.last_realization_feedback).__name__
            raise TypeError(
                "ClaudeRuntimeSessionArtifact.last_realization_feedback must be "
                f"ReferenceRealizationFeedback | None, got {actual_type}."
            )
        if not isinstance(self.feedback_window, ReferenceRealizationFeedbackWindow):
            actual_type = type(self.feedback_window).__name__
            raise TypeError(
                "ClaudeRuntimeSessionArtifact.feedback_window must be "
                f"ReferenceRealizationFeedbackWindow, got {actual_type}."
            )
        if self.executive_modulator_memory is not None and not isinstance(
            self.executive_modulator_memory,
            ExecutiveModulatorMemory,
        ):
            actual_type = type(self.executive_modulator_memory).__name__
            raise TypeError(
                "ClaudeRuntimeSessionArtifact.executive_modulator_memory must be "
                f"ExecutiveModulatorMemory | None, got {actual_type}."
            )
        for entry in self.brake_tonic_history:
            if isinstance(entry, bool) or not isinstance(entry, (int, float)):
                actual_type = type(entry).__name__
                raise TypeError(
                    "ClaudeRuntimeSessionArtifact.brake_tonic_history must contain only "
                    f"numeric values in [0.0, 1.0], got {actual_type}."
                )
            if not 0.0 <= float(entry) <= 1.0:
                raise ValueError(
                    "ClaudeRuntimeSessionArtifact.brake_tonic_history entries must be "
                    "between 0.0 and 1.0."
                )
        if (
            self.last_realization_feedback is not None
            and self.feedback_window.entries
            and self.feedback_window.entries[-1] != self.last_realization_feedback
        ):
            raise ValueError(
                "ClaudeRuntimeSessionArtifact.feedback_window newest entry must match "
                "last_realization_feedback when both are present."
            )
        normalized_executive_modulator_memory = canonicalize_executive_modulator_memory(
            self.executive_modulator_memory
        )
        if normalized_executive_modulator_memory != self.executive_modulator_memory:
            object.__setattr__(
                self,
                "executive_modulator_memory",
                normalized_executive_modulator_memory,
            )

    def as_payload(self) -> dict[str, object]:
        return {
            "artifact_kind": self.artifact_kind,
            "artifact_version": self.artifact_version,
            "continuity_truth": {
                "session_id": self.session_id,
                "event_index": self.event_index,
                "branch_registry": list(self.branch_registry),
                "active_track_ref": self.active_track_ref,
                "pending_goal_refs": list(self.pending_goal_refs),
                "continuity_reminders": list(self.continuity_reminders),
            },
            "control_residue": {
                "last_budget_band": self.last_budget_band,
                "last_commitment_result_summary": self.last_commitment_result_summary,
                "last_realization_feedback": (
                    self.last_realization_feedback.as_summary()
                    if self.last_realization_feedback is not None
                    else None
                ),
                "feedback_window": [
                    entry.as_summary() for entry in self.feedback_window.entries
                ],
                "executive_modulator_memory": (
                    executive_modulator_memory_payload(self.executive_modulator_memory)
                    if self.executive_modulator_memory is not None
                    else None
                ),
                "brake_tonic_history": [float(entry) for entry in self.brake_tonic_history],
            },
        }

    def to_session(self) -> ClaudeRuntimeSession:
        budget_history = ()
        if self.last_budget_band is not None:
            budget_history = (f"shell-{self.last_budget_band}",)

        brake_history = ()
        last_selected_family = None
        if self.last_realization_feedback is not None:
            brake_history = (self.last_realization_feedback.brake_state.value,)
            last_selected_family = self.last_realization_feedback.selected_family

        return ClaudeRuntimeSession(
            session_id=self.session_id,
            event_index=self.event_index,
            branch_registry=self.branch_registry,
            active_track_ref=self.active_track_ref,
            pending_goal_refs=self.pending_goal_refs,
            continuity_reminders=self.continuity_reminders,
            budget_history=budget_history,
            brake_history=brake_history,
            brake_tonic_history=self.brake_tonic_history,
            last_selected_family=last_selected_family,
            last_commitment_result_summary=self.last_commitment_result_summary,
            last_realization_feedback=self.last_realization_feedback,
            feedback_window=self.feedback_window,
            executive_modulator_memory=self.executive_modulator_memory,
        )


def build_claude_runtime_session_artifact(
    session: ClaudeRuntimeSession,
) -> ClaudeRuntimeSessionArtifact:
    if not isinstance(session, ClaudeRuntimeSession):
        actual_type = type(session).__name__
        raise TypeError(
            "build_claude_runtime_session_artifact.session must be ClaudeRuntimeSession, "
            f"got {actual_type}."
        )
    return ClaudeRuntimeSessionArtifact(
        session_id=session.session_id,
        event_index=session.event_index,
        branch_registry=session.branch_registry,
        active_track_ref=session.active_track_ref,
        pending_goal_refs=session.pending_goal_refs,
        continuity_reminders=session.continuity_reminders,
        last_budget_band=_last_budget_band(session.budget_history),
        last_commitment_result_summary=session.last_commitment_result_summary,
        last_realization_feedback=session.last_realization_feedback,
        feedback_window=session.feedback_window,
        executive_modulator_memory=session.executive_modulator_memory,
        brake_tonic_history=session.brake_tonic_history,
    )


def parse_claude_runtime_session_artifact(
    payload: Mapping[str, Any],
) -> ClaudeRuntimeSession:
    if not isinstance(payload, Mapping):
        actual_type = type(payload).__name__
        raise TypeError(
            "parse_claude_runtime_session_artifact.payload must be a mapping, "
            f"got {actual_type}."
        )
    _require_exact_keys(payload, _TOP_LEVEL_KEYS, "ClaudeRuntimeSessionArtifact")
    artifact_kind = payload["artifact_kind"]
    artifact_version = payload["artifact_version"]
    continuity_truth_payload = payload["continuity_truth"]
    control_residue_payload = payload["control_residue"]

    if artifact_kind != _ARTIFACT_KIND:
        raise ValueError(
            f"ClaudeRuntimeSessionArtifact.artifact_kind must be `{_ARTIFACT_KIND}`."
        )
    if artifact_version != _ARTIFACT_VERSION:
        raise ValueError(
            f"ClaudeRuntimeSessionArtifact.artifact_version must be `{_ARTIFACT_VERSION}`."
        )
    if not isinstance(continuity_truth_payload, Mapping):
        raise TypeError("ClaudeRuntimeSessionArtifact.continuity_truth must be an object.")
    if not isinstance(control_residue_payload, Mapping):
        raise TypeError("ClaudeRuntimeSessionArtifact.control_residue must be an object.")

    _require_continuity_truth_keys(continuity_truth_payload)
    _require_control_residue_keys(control_residue_payload)

    artifact = ClaudeRuntimeSessionArtifact(
        session_id=_optional_non_empty_string(
            continuity_truth_payload["session_id"],
            "ClaudeRuntimeSessionArtifact.continuity_truth.session_id",
        ),
        event_index=_non_negative_int(
            continuity_truth_payload["event_index"],
            "ClaudeRuntimeSessionArtifact.continuity_truth.event_index",
        ),
        branch_registry=_string_tuple(
            continuity_truth_payload["branch_registry"],
            "ClaudeRuntimeSessionArtifact.continuity_truth.branch_registry",
        ),
        active_track_ref=_required_non_empty_string(
            continuity_truth_payload["active_track_ref"],
            "ClaudeRuntimeSessionArtifact.continuity_truth.active_track_ref",
        ),
        pending_goal_refs=_string_tuple(
            continuity_truth_payload["pending_goal_refs"],
            "ClaudeRuntimeSessionArtifact.continuity_truth.pending_goal_refs",
        ),
        continuity_reminders=_continuity_reminders_tuple(
            continuity_truth_payload.get("continuity_reminders", []),
            "ClaudeRuntimeSessionArtifact.continuity_truth.continuity_reminders",
        ),
        last_budget_band=_optional_budget_band(
            control_residue_payload["last_budget_band"],
            "ClaudeRuntimeSessionArtifact.control_residue.last_budget_band",
        ),
        last_commitment_result_summary=_optional_non_empty_string(
            control_residue_payload["last_commitment_result_summary"],
            "ClaudeRuntimeSessionArtifact.control_residue.last_commitment_result_summary",
        ),
        last_realization_feedback=_optional_feedback(
            control_residue_payload["last_realization_feedback"],
            "ClaudeRuntimeSessionArtifact.control_residue.last_realization_feedback",
        ),
        feedback_window=_feedback_window(
            control_residue_payload["feedback_window"],
            "ClaudeRuntimeSessionArtifact.control_residue.feedback_window",
        ),
        executive_modulator_memory=_optional_executive_modulator_memory(
            control_residue_payload.get("executive_modulator_memory"),
            "ClaudeRuntimeSessionArtifact.control_residue.executive_modulator_memory",
        ),
        brake_tonic_history=_brake_tonic_history_tuple(
            control_residue_payload.get("brake_tonic_history", []),
            "ClaudeRuntimeSessionArtifact.control_residue.brake_tonic_history",
        ),
    )
    return artifact.to_session()


def read_claude_runtime_session_artifact(path: Path) -> ClaudeRuntimeSession:
    if not isinstance(path, Path):
        actual_type = type(path).__name__
        raise TypeError(
            "read_claude_runtime_session_artifact.path must be Path, "
            f"got {actual_type}."
        )
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return parse_claude_runtime_session_artifact(payload)


def write_claude_runtime_session_artifact(
    path: Path,
    session: ClaudeRuntimeSession,
) -> None:
    if not isinstance(path, Path):
        actual_type = type(path).__name__
        raise TypeError(
            "write_claude_runtime_session_artifact.path must be Path, "
            f"got {actual_type}."
        )
    if not path.parent.exists():
        raise FileNotFoundError(
            f"Claude runtime session artifact parent does not exist: {path.parent}"
        )

    artifact = build_claude_runtime_session_artifact(session)
    payload = artifact.as_payload()

    temp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temp_path = handle.name
            json.dump(payload, handle, indent=2)
            handle.write("\n")
        os.replace(temp_path, path)
    except Exception:
        if temp_path is not None:
            Path(temp_path).unlink(missing_ok=True)
        raise


def _require_exact_keys(
    payload: Mapping[str, Any],
    expected_keys: tuple[str, ...],
    label: str,
) -> None:
    actual_keys = tuple(payload.keys())
    missing_keys = [key for key in expected_keys if key not in payload]
    extra_keys = [key for key in actual_keys if key not in expected_keys]
    if missing_keys or extra_keys:
        raise ValueError(
            f"{label} keys must be exactly {expected_keys}; "
            f"missing={missing_keys}, extra={extra_keys}."
        )


def _require_continuity_truth_keys(payload: Mapping[str, Any]) -> None:
    actual_keys = tuple(payload.keys())
    if actual_keys == _CONTINUITY_TRUTH_KEYS or actual_keys == _LEGACY_CONTINUITY_TRUTH_KEYS:
        return
    expected = f"{_CONTINUITY_TRUTH_KEYS} or {_LEGACY_CONTINUITY_TRUTH_KEYS}"
    missing_keys = [key for key in _CONTINUITY_TRUTH_KEYS if key not in payload]
    extra_keys = [key for key in actual_keys if key not in _CONTINUITY_TRUTH_KEYS]
    raise ValueError(
        "ClaudeRuntimeSessionArtifact.continuity_truth keys must be exactly "
        f"{expected}; missing={missing_keys}, extra={extra_keys}."
    )


def _continuity_reminders_tuple(value: Any, label: str) -> tuple[str, ...]:
    reminders = _string_tuple(value, label)
    normalized: list[str] = []
    for reminder in reminders:
        if (canonical := normalize_continuity_reminder(reminder)) is None:
            continue
        if canonical not in normalized:
            normalized.append(canonical)
    return tuple(normalized)


def _require_control_residue_keys(payload: Mapping[str, Any]) -> None:
    actual_keys = tuple(payload.keys())
    if actual_keys in (
        _CONTROL_RESIDUE_KEYS,
        _PRE_TONIC_HISTORY_CONTROL_RESIDUE_KEYS,
        _PRE_MODULATOR_CONTROL_RESIDUE_KEYS,
    ):
        return
    expected = (
        f"{_CONTROL_RESIDUE_KEYS}, {_PRE_TONIC_HISTORY_CONTROL_RESIDUE_KEYS}, "
        f"or {_PRE_MODULATOR_CONTROL_RESIDUE_KEYS}"
    )
    missing_keys = [key for key in _CONTROL_RESIDUE_KEYS if key not in payload]
    extra_keys = [key for key in actual_keys if key not in _CONTROL_RESIDUE_KEYS]
    raise ValueError(
        "ClaudeRuntimeSessionArtifact.control_residue keys must be exactly "
        f"{expected}; missing={missing_keys}, extra={extra_keys}."
    )


def _optional_non_empty_string(value: Any, label: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        actual_type = type(value).__name__
        raise TypeError(f"{label} must be str | null, got {actual_type}.")
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"{label} must be non-empty after trimming when provided.")
    return stripped


def _required_non_empty_string(value: Any, label: str) -> str:
    result = _optional_non_empty_string(value, label)
    if result is None:
        raise ValueError(f"{label} must be non-null.")
    return result


def _non_negative_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        actual_type = type(value).__name__
        raise TypeError(f"{label} must be a non-negative integer, got {actual_type}.")
    if value < 0:
        raise ValueError(f"{label} must be non-negative.")
    return value


def _string_tuple(value: Any, label: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        actual_type = type(value).__name__
        raise TypeError(f"{label} must be a JSON array, got {actual_type}.")
    parsed: list[str] = []
    for item in value:
        parsed.append(_required_non_empty_string(item, label))
    return tuple(parsed)


def _optional_budget_band(value: Any, label: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        actual_type = type(value).__name__
        raise TypeError(f"{label} must be str | null, got {actual_type}.")
    stripped = value.strip()
    if stripped not in _ALLOWED_BUDGET_BANDS:
        raise ValueError(
            f"{label} must be one of {tuple(sorted(_ALLOWED_BUDGET_BANDS))} when provided."
        )
    return stripped


def _optional_feedback(value: Any, label: str) -> ReferenceRealizationFeedback | None:
    if value is None:
        return None
    return _feedback(value, label)


def _optional_executive_modulator_memory(
    value: Any,
    label: str,
) -> ExecutiveModulatorMemory | None:
    if value is None:
        return None
    return _executive_modulator_memory(value, label)


def _feedback_window(
    value: Any,
    label: str,
) -> ReferenceRealizationFeedbackWindow:
    if not isinstance(value, list):
        actual_type = type(value).__name__
        raise TypeError(f"{label} must be a JSON array, got {actual_type}.")
    return ReferenceRealizationFeedbackWindow(
        entries=tuple(_feedback(item, label) for item in value)
    )


def _feedback(value: Any, label: str) -> ReferenceRealizationFeedback:
    from cortex.sre.brake import BrakeState
    from cortex.sre.families import SoftControlFamily

    if not isinstance(value, Mapping):
        actual_type = type(value).__name__
        raise TypeError(f"{label} must be an object, got {actual_type}.")
    required_feedback_keys = (
        "selected_family",
        "realized_family",
        "brake_state",
        "commitment_result_kind",
        "warning_codes",
        "host_friction_tags",
    )
    optional_feedback_keys = (
        "task_mode",
        "evidence_progress_class",
        "evidence_state_moved",
        "continuity_progress_class",
        "continuity_improved",
        "probe_result_class",
    )
    expected_keys = set(required_feedback_keys) | set(optional_feedback_keys)
    actual_keys = set(value)
    if not set(required_feedback_keys) <= actual_keys or actual_keys - expected_keys:
        _require_exact_keys(value, required_feedback_keys, label)

    def _family(raw: Any, field_label: str) -> SoftControlFamily:
        if not isinstance(raw, str):
            actual_type = type(raw).__name__
            raise TypeError(f"{field_label} must be a string, got {actual_type}.")
        try:
            return SoftControlFamily(raw.strip())
        except ValueError as exc:
            raise ValueError(f"{field_label} must be a canonical soft-control family.") from exc

    def _brake(raw: Any, field_label: str) -> BrakeState:
        if not isinstance(raw, str):
            actual_type = type(raw).__name__
            raise TypeError(f"{field_label} must be a string, got {actual_type}.")
        try:
            return BrakeState(raw.strip())
        except ValueError as exc:
            raise ValueError(f"{field_label} must be a canonical brake state.") from exc

    def _commitment_kind(raw: Any, field_label: str) -> str | None:
        if raw is None:
            return None
        if not isinstance(raw, str):
            actual_type = type(raw).__name__
            raise TypeError(f"{field_label} must be str | null, got {actual_type}.")
        stripped = raw.strip()
        if stripped not in {"certified", "uncertified", "blocked"}:
            raise ValueError(f"{field_label} must be a canonical commitment status when provided.")
        return stripped

    return ReferenceRealizationFeedback(
        selected_family=_family(value["selected_family"], f"{label}.selected_family"),
        realized_family=_family(value["realized_family"], f"{label}.realized_family"),
        brake_state=_brake(value["brake_state"], f"{label}.brake_state"),
        task_mode=_optional_task_mode(value.get("task_mode"), f"{label}.task_mode"),
        commitment_result_kind=_commitment_kind(
            value["commitment_result_kind"],
            f"{label}.commitment_result_kind",
        ),
        warning_codes=_string_tuple(value["warning_codes"], f"{label}.warning_codes"),
        host_friction_tags=_string_tuple(
            value["host_friction_tags"],
            f"{label}.host_friction_tags",
        ),
        evidence_progress_class=_optional_non_empty_string(
            value.get("evidence_progress_class"),
            f"{label}.evidence_progress_class",
        ),
        evidence_state_moved=_optional_bool(
            value.get("evidence_state_moved"),
            f"{label}.evidence_state_moved",
        ),
        continuity_progress_class=_optional_non_empty_string(
            value.get("continuity_progress_class"),
            f"{label}.continuity_progress_class",
        ),
        continuity_improved=_optional_bool(
            value.get("continuity_improved"),
            f"{label}.continuity_improved",
        ),
        probe_result_class=_optional_non_empty_string(
            value.get("probe_result_class"),
            f"{label}.probe_result_class",
        ),
    )


def _executive_modulator_memory(value: Any, label: str) -> ExecutiveModulatorMemory:
    if not isinstance(value, Mapping):
        actual_type = type(value).__name__
        raise TypeError(f"{label} must be an object, got {actual_type}.")
    memory_keys = (
        "focus_tonic",
        "explore_tonic",
        "stop_tonic",
        "update_tonic",
    )
    _require_exact_keys(value, memory_keys, label)
    memory = ExecutiveModulatorMemory(
        focus_tonic=_unit_float(value["focus_tonic"], f"{label}.focus_tonic"),
        explore_tonic=_unit_float(value["explore_tonic"], f"{label}.explore_tonic"),
        stop_tonic=_unit_float(value["stop_tonic"], f"{label}.stop_tonic"),
        update_tonic=_unit_float(value["update_tonic"], f"{label}.update_tonic"),
    )
    return canonicalize_executive_modulator_memory(memory)


def _optional_task_mode(value: Any, label: str) -> OperatorTaskMode | None:
    if value is None:
        return None
    if not isinstance(value, str):
        actual_type = type(value).__name__
        raise TypeError(f"{label} must be str | null, got {actual_type}.")
    try:
        return OperatorTaskMode(value.strip())
    except ValueError as exc:
        raise ValueError(f"{label} must be a canonical operator task mode when provided.") from exc


def _unit_float(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        actual_type = type(value).__name__
        raise TypeError(f"{label} must be numeric, got {actual_type}.")
    parsed = float(value)
    if not 0.0 <= parsed <= 1.0:
        raise ValueError(f"{label} must be between 0.0 and 1.0.")
    return parsed


def _optional_bool(value: Any, label: str) -> bool | None:
    if value is None:
        return None
    if not isinstance(value, bool):
        actual_type = type(value).__name__
        raise TypeError(f"{label} must be bool | null, got {actual_type}.")
    return value


def _brake_tonic_history_tuple(value: Any, label: str) -> tuple[float, ...]:
    if not isinstance(value, list):
        actual_type = type(value).__name__
        raise TypeError(f"{label} must be a JSON array, got {actual_type}.")
    parsed: list[float] = []
    for item in value:
        if isinstance(item, bool) or not isinstance(item, (int, float)):
            actual_type = type(item).__name__
            raise TypeError(
                f"{label} must contain only numeric values in [0.0, 1.0], got {actual_type}."
            )
        entry = float(item)
        if not 0.0 <= entry <= 1.0:
            raise ValueError(f"{label} entries must be between 0.0 and 1.0.")
        parsed.append(entry)
    return tuple(parsed)


def _last_budget_band(budget_history: tuple[str, ...]) -> str | None:
    if not budget_history:
        return None
    last_budget_entry = budget_history[-1]
    if not last_budget_entry.startswith("shell-"):
        raise ValueError(
            "Claude runtime session artifact only supports shell budget history entries."
        )
    last_budget_band = last_budget_entry.replace("shell-", "", 1)
    if last_budget_band not in _ALLOWED_BUDGET_BANDS:
        raise ValueError(
            "Claude runtime session artifact only supports `shell-low`, "
            "`shell-medium`, and `shell-high` budget entries."
        )
    return last_budget_band


__all__ = [
    "ClaudeRuntimeSessionArtifact",
    "build_claude_runtime_session_artifact",
    "parse_claude_runtime_session_artifact",
    "read_claude_runtime_session_artifact",
    "write_claude_runtime_session_artifact",
]
```

### `cortex/hosts/claude_code_desktop/ingress.py`

```python
"""Ingress parsing for Claude Code Desktop hook payloads."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

_HOOK_EVENTS = frozenset(
    {
        "SessionStart",
        "UserPromptSubmit",
        "PreToolUse",
        "PostToolUse",
        "PreCompact",
        "SubagentStop",
        "Stop",
        "SessionEnd",
    }
)
_WIRED_EVENT_KINDS = frozenset({"pretooluse:bash"})


@dataclass(frozen=True, slots=True)
class ClaudeCodeDesktopHookEventEnvelope:
    hook_event_name: str
    payload: dict[str, Any]
    event_kind: str
    wired: bool = False

    def __post_init__(self) -> None:
        if self.hook_event_name not in _HOOK_EVENTS:
            raise ValueError(
                "ClaudeCodeDesktopHookEventEnvelope.hook_event_name must be one "
                f"of {sorted(_HOOK_EVENTS)!r}."
            )
        if not isinstance(self.payload, dict):
            actual_type = type(self.payload).__name__
            raise TypeError(
                "ClaudeCodeDesktopHookEventEnvelope.payload must be dict[str, Any], "
                f"got {actual_type}."
            )
        if not (isinstance(self.event_kind, str) and self.event_kind.strip()):
            raise ValueError(
                "ClaudeCodeDesktopHookEventEnvelope.event_kind must be non-empty."
            )
        if not isinstance(self.wired, bool):
            actual_type = type(self.wired).__name__
            raise TypeError(
                "ClaudeCodeDesktopHookEventEnvelope.wired must be bool, "
                f"got {actual_type}."
            )
        if self.wired and self.event_kind not in _WIRED_EVENT_KINDS:
            raise ValueError(
                "Only explicitly wired Claude Code Desktop hook event kinds may "
                f"set wired=True; got {self.event_kind!r}."
            )


def parse_claude_code_desktop_hook_event(
    payload: Mapping[str, Any],
) -> ClaudeCodeDesktopHookEventEnvelope:
    if not isinstance(payload, Mapping):
        actual_type = type(payload).__name__
        raise TypeError(
            "parse_claude_code_desktop_hook_event.payload must be a mapping, "
            f"got {actual_type}."
        )
    hook_event_name = _required_hook_event_name(payload)
    normalized_payload = dict(payload)
    if hook_event_name == "PreToolUse" and payload.get("tool_name") == "Bash":
        tool_input = payload.get("tool_input")
        if not isinstance(tool_input, Mapping):
            actual_type = type(tool_input).__name__
            raise TypeError(
                "Claude Code Desktop PreToolUse:Bash payload must include "
                f"tool_input as a mapping, got {actual_type}."
            )
        return ClaudeCodeDesktopHookEventEnvelope(
            hook_event_name=hook_event_name,
            payload=normalized_payload,
            event_kind="pretooluse:bash",
            wired=True,
        )
    return ClaudeCodeDesktopHookEventEnvelope(
        hook_event_name=hook_event_name,
        payload=normalized_payload,
        event_kind=_unwired_event_kind(hook_event_name, payload),
        wired=False,
    )


def _required_hook_event_name(payload: Mapping[str, Any]) -> str:
    raw_name = payload.get("hook_event_name")
    if not isinstance(raw_name, str):
        actual_type = type(raw_name).__name__
        raise TypeError(
            "Claude Code Desktop hook payload must include string hook_event_name, "
            f"got {actual_type}."
        )
    stripped = raw_name.strip()
    if stripped not in _HOOK_EVENTS:
        raise ValueError(
            "Claude Code Desktop hook_event_name must be one of "
            f"{sorted(_HOOK_EVENTS)!r}, got {raw_name!r}."
        )
    return stripped


def _unwired_event_kind(hook_event_name: str, payload: Mapping[str, Any]) -> str:
    if hook_event_name in {"PreToolUse", "PostToolUse"}:
        tool_name = payload.get("tool_name")
        if isinstance(tool_name, str) and tool_name.strip():
            return f"{hook_event_name.lower()}:{tool_name.strip().lower()}:unwired"
    return f"{hook_event_name.lower()}:unwired"


__all__ = [
    "ClaudeCodeDesktopHookEventEnvelope",
    "parse_claude_code_desktop_hook_event",
]
```

### `cortex/hosts/claude_code_desktop/runtime.py`

```python
"""Claude Code Desktop runtime adapter over the existing Cortex host law."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from cortex.hosts.claude.runtime import ClaudeRuntimeSession, ClaudeRuntimeStepResult
from cortex.hosts.claude.runtime import run_claude_runtime_step
from cortex.hosts.runtime_context import runtime_context_from_last_feedback
from cortex.sre.families import SoftControlFamily
from cortex.sre.feedback import (
    ReferenceRealizationFeedback,
    ReferenceRealizationFeedbackWindow,
)
from cortex.sre.modulators import ExecutiveModulatorMemory

from .hook_control import ClaudeCodeDesktopHookControlDirective
from .ingress import ClaudeCodeDesktopHookEventEnvelope

_CONTEXT_REASON = "Cortex runtime context from prior realization feedback."
_DENY_REASON_PREFIX = "Cortex blocked this tool call before execution"
_VALID_MODES = frozenset({"observe", "enforce"})


@dataclass(frozen=True, slots=True)
class ClaudeCodeDesktopRuntimeSession:
    session_id: str | None = None
    event_index: int = 0
    branch_registry: tuple[str, ...] = ("main",)
    active_track_ref: str = "main"
    pending_goal_refs: tuple[str, ...] = ()
    continuity_reminders: tuple[str, ...] = ()
    budget_history: tuple[str, ...] = ()
    brake_history: tuple[str, ...] = ()
    brake_tonic_history: tuple[float, ...] = ()
    last_selected_family: SoftControlFamily | None = None
    last_commitment_result_summary: str | None = None
    last_realization_feedback: ReferenceRealizationFeedback | None = None
    feedback_window: ReferenceRealizationFeedbackWindow = field(
        default_factory=ReferenceRealizationFeedbackWindow
    )
    executive_modulator_memory: ExecutiveModulatorMemory | None = None

    def __post_init__(self) -> None:
        normalized = self.to_claude_session()
        object.__setattr__(self, "session_id", normalized.session_id)
        object.__setattr__(self, "event_index", normalized.event_index)
        object.__setattr__(self, "branch_registry", normalized.branch_registry)
        object.__setattr__(self, "active_track_ref", normalized.active_track_ref)
        object.__setattr__(self, "pending_goal_refs", normalized.pending_goal_refs)
        object.__setattr__(self, "continuity_reminders", normalized.continuity_reminders)
        object.__setattr__(self, "budget_history", normalized.budget_history)
        object.__setattr__(self, "brake_history", normalized.brake_history)
        object.__setattr__(
            self, "brake_tonic_history", normalized.brake_tonic_history
        )
        object.__setattr__(self, "last_selected_family", normalized.last_selected_family)
        object.__setattr__(
            self,
            "last_commitment_result_summary",
            normalized.last_commitment_result_summary,
        )
        object.__setattr__(
            self, "last_realization_feedback", normalized.last_realization_feedback
        )
        object.__setattr__(self, "feedback_window", normalized.feedback_window)
        object.__setattr__(
            self,
            "executive_modulator_memory",
            normalized.executive_modulator_memory,
        )

    def to_claude_session(self) -> ClaudeRuntimeSession:
        return ClaudeRuntimeSession(
            session_id=self.session_id,
            event_index=self.event_index,
            branch_registry=self.branch_registry,
            active_track_ref=self.active_track_ref,
            pending_goal_refs=self.pending_goal_refs,
            continuity_reminders=self.continuity_reminders,
            budget_history=self.budget_history,
            brake_history=self.brake_history,
            brake_tonic_history=self.brake_tonic_history,
            last_selected_family=self.last_selected_family,
            last_commitment_result_summary=self.last_commitment_result_summary,
            last_realization_feedback=self.last_realization_feedback,
            feedback_window=self.feedback_window,
            executive_modulator_memory=self.executive_modulator_memory,
        )

    @classmethod
    def from_claude_session(
        cls,
        session: ClaudeRuntimeSession,
    ) -> "ClaudeCodeDesktopRuntimeSession":
        if not isinstance(session, ClaudeRuntimeSession):
            actual_type = type(session).__name__
            raise TypeError(
                "ClaudeCodeDesktopRuntimeSession.from_claude_session.session must "
                f"be ClaudeRuntimeSession, got {actual_type}."
            )
        return cls(
            session_id=session.session_id,
            event_index=session.event_index,
            branch_registry=session.branch_registry,
            active_track_ref=session.active_track_ref,
            pending_goal_refs=session.pending_goal_refs,
            continuity_reminders=session.continuity_reminders,
            budget_history=session.budget_history,
            brake_history=session.brake_history,
            brake_tonic_history=session.brake_tonic_history,
            last_selected_family=session.last_selected_family,
            last_commitment_result_summary=session.last_commitment_result_summary,
            last_realization_feedback=session.last_realization_feedback,
            feedback_window=session.feedback_window,
            executive_modulator_memory=session.executive_modulator_memory,
        )

    def as_summary(self) -> dict[str, Any]:
        return self.to_claude_session().as_summary()


@dataclass(frozen=True, slots=True)
class ClaudeCodeDesktopRuntimeStepResult:
    event: ClaudeCodeDesktopHookEventEnvelope
    session: ClaudeCodeDesktopRuntimeSession
    directive: ClaudeCodeDesktopHookControlDirective
    claude_runtime_result: ClaudeRuntimeStepResult | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.event, ClaudeCodeDesktopHookEventEnvelope):
            actual_type = type(self.event).__name__
            raise TypeError(
                "ClaudeCodeDesktopRuntimeStepResult.event must be "
                f"ClaudeCodeDesktopHookEventEnvelope, got {actual_type}."
            )
        if not isinstance(self.session, ClaudeCodeDesktopRuntimeSession):
            actual_type = type(self.session).__name__
            raise TypeError(
                "ClaudeCodeDesktopRuntimeStepResult.session must be "
                f"ClaudeCodeDesktopRuntimeSession, got {actual_type}."
            )
        if not isinstance(self.directive, ClaudeCodeDesktopHookControlDirective):
            actual_type = type(self.directive).__name__
            raise TypeError(
                "ClaudeCodeDesktopRuntimeStepResult.directive must be "
                f"ClaudeCodeDesktopHookControlDirective, got {actual_type}."
            )
        if self.claude_runtime_result is not None and not isinstance(
            self.claude_runtime_result,
            ClaudeRuntimeStepResult,
        ):
            actual_type = type(self.claude_runtime_result).__name__
            raise TypeError(
                "ClaudeCodeDesktopRuntimeStepResult.claude_runtime_result must be "
                f"ClaudeRuntimeStepResult | None, got {actual_type}."
            )


def run_claude_code_desktop_runtime_step(
    event: ClaudeCodeDesktopHookEventEnvelope,
    session: ClaudeCodeDesktopRuntimeSession | None = None,
    *,
    mode: str = "enforce",
    max_context_chars: int = 720,
    audit_intensity: str = "minimal",
) -> ClaudeCodeDesktopRuntimeStepResult:
    if not isinstance(event, ClaudeCodeDesktopHookEventEnvelope):
        actual_type = type(event).__name__
        raise TypeError(
            "run_claude_code_desktop_runtime_step.event must be "
            f"ClaudeCodeDesktopHookEventEnvelope, got {actual_type}."
        )
    if mode not in _VALID_MODES:
        raise ValueError(
            "run_claude_code_desktop_runtime_step.mode must be `observe` or `enforce`."
        )
    if isinstance(max_context_chars, bool) or not isinstance(max_context_chars, int):
        actual_type = type(max_context_chars).__name__
        raise TypeError(
            "run_claude_code_desktop_runtime_step.max_context_chars must be int, "
            f"got {actual_type}."
        )
    if not 1 <= max_context_chars <= 720:
        raise ValueError(
            "run_claude_code_desktop_runtime_step.max_context_chars must be in [1, 720]."
        )
    prior_session = _coerce_session(session)
    if not event.wired:
        return ClaudeCodeDesktopRuntimeStepResult(
            event=event,
            session=prior_session,
            directive=ClaudeCodeDesktopHookControlDirective.noop(event.hook_event_name),
        )

    claude_result = run_claude_runtime_step(
        "content_block_delta",
        _pretool_bash_as_claude_payload(event.payload),
        prior_session.to_claude_session(),
        audit_intensity=audit_intensity,
    )
    updated_session = ClaudeCodeDesktopRuntimeSession.from_claude_session(
        claude_result.session
    )
    directive = _directive_for_pretool_bash(
        prior_session=prior_session,
        hook_event_name=event.hook_event_name,
        claude_result=claude_result,
        mode=mode,
        max_context_chars=max_context_chars,
    )
    return ClaudeCodeDesktopRuntimeStepResult(
        event=event,
        session=updated_session,
        directive=directive,
        claude_runtime_result=claude_result,
    )


def _coerce_session(
    session: ClaudeCodeDesktopRuntimeSession | None,
) -> ClaudeCodeDesktopRuntimeSession:
    if session is None:
        return ClaudeCodeDesktopRuntimeSession()
    if not isinstance(session, ClaudeCodeDesktopRuntimeSession):
        actual_type = type(session).__name__
        raise TypeError(
            "run_claude_code_desktop_runtime_step.session must be "
            f"ClaudeCodeDesktopRuntimeSession | None, got {actual_type}."
        )
    return session


def _directive_for_pretool_bash(
    *,
    prior_session: ClaudeCodeDesktopRuntimeSession,
    hook_event_name: str,
    claude_result: ClaudeRuntimeStepResult,
    mode: str,
    max_context_chars: int,
) -> ClaudeCodeDesktopHookControlDirective:
    blocked_reason = claude_result.operator_route.blocked_reason
    if mode == "enforce" and blocked_reason is not None:
        return ClaudeCodeDesktopHookControlDirective(
            hook_event_name=hook_event_name,
            permission_decision="deny",
            permission_decision_reason=_bounded_reason(
                f"{_DENY_REASON_PREFIX}: {blocked_reason}."
            ),
            additional_context=_bounded_optional_context(
                runtime_context_from_last_feedback(
                    prior_session.last_realization_feedback
                ),
                max_context_chars=max_context_chars,
            ),
            suppress_output=False,
        )

    context = runtime_context_from_last_feedback(prior_session.last_realization_feedback)
    if mode == "enforce" and context is not None:
        return ClaudeCodeDesktopHookControlDirective(
            hook_event_name=hook_event_name,
            permission_decision="allow",
            permission_decision_reason=_CONTEXT_REASON,
            additional_context=_bounded_optional_context(
                context,
                max_context_chars=max_context_chars,
            ),
            suppress_output=False,
        )
    return ClaudeCodeDesktopHookControlDirective.noop(hook_event_name)


def _pretool_bash_as_claude_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, Mapping):
        raise TypeError("PreToolUse:Bash payload must include mapping tool_input.")
    command = _optional_string(tool_input.get("command")) or "<missing command>"
    tool_use_id = _optional_string(payload.get("tool_use_id")) or "pretool-bash"
    session_id = _optional_string(payload.get("session_id"))
    synthetic: dict[str, Any] = {
        "message_id": f"claude-code-desktop:{tool_use_id}",
        "delta_type": "text_delta",
        "delta": f"PreToolUse Bash intent: {_truncate(command, 280)}",
        "tool_name": "Bash",
        "tool_input": dict(tool_input),
        "externally_consequential": _bash_command_may_mutate(command),
    }
    if session_id is not None:
        synthetic["session_id"] = session_id
    cwd = _optional_string(payload.get("cwd"))
    if cwd is not None:
        synthetic["current_workspace_ref"] = cwd
    transcript_path = _optional_string(payload.get("transcript_path"))
    if transcript_path is not None:
        synthetic["external_record_ref"] = transcript_path
    return synthetic


def _bash_command_may_mutate(command: str) -> bool:
    lowered = command.lower()
    mutation_tokens = (
        ">",
        "apply_patch",
        "cat >",
        "chmod ",
        "cp ",
        "git commit",
        "git mv",
        "mkdir ",
        "mv ",
        "python -c",
        "python3 -c",
        "rm ",
        "sed -i",
        "tee ",
        "touch ",
    )
    return any(token in lowered for token in mutation_tokens)


def _bounded_optional_context(context: str | None, *, max_context_chars: int) -> str | None:
    if context is None:
        return None
    if len(context) > max_context_chars:
        return context[: max_context_chars - 3] + "..."
    return context


def _bounded_reason(reason: str, *, max_chars: int = 360) -> str:
    if len(reason) <= max_chars:
        return reason
    return reason[: max_chars - 3] + "..."


def _optional_string(value: object) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _truncate(value: str, max_chars: int) -> str:
    if len(value) <= max_chars:
        return value
    return value[: max_chars - 3] + "..."


__all__ = [
    "ClaudeCodeDesktopRuntimeSession",
    "ClaudeCodeDesktopRuntimeStepResult",
    "run_claude_code_desktop_runtime_step",
]
```

### `cortex/hosts/claude_code_desktop/hook_control.py`

```python
"""Claude Code Desktop hook-control JSON builders."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

_MAX_CONTEXT_CHARS = 720
_PERMISSION_DECISIONS = frozenset({"allow", "deny"})


@dataclass(frozen=True, slots=True)
class ClaudeCodeDesktopHookControlDirective:
    hook_event_name: str
    permission_decision: str | None = None
    permission_decision_reason: str | None = None
    additional_context: str | None = None
    block_reason: str | None = None
    suppress_output: bool = True

    def __post_init__(self) -> None:
        if not (isinstance(self.hook_event_name, str) and self.hook_event_name.strip()):
            raise ValueError(
                "ClaudeCodeDesktopHookControlDirective.hook_event_name must be non-empty."
            )
        if self.permission_decision is not None and self.permission_decision not in _PERMISSION_DECISIONS:
            raise ValueError(
                "ClaudeCodeDesktopHookControlDirective.permission_decision must be "
                "`allow`, `deny`, or None."
            )
        if self.permission_decision_reason is not None and not (
            isinstance(self.permission_decision_reason, str)
            and self.permission_decision_reason.strip()
        ):
            raise ValueError(
                "ClaudeCodeDesktopHookControlDirective.permission_decision_reason "
                "must be non-empty when provided."
            )
        if self.additional_context is not None:
            if not (
                isinstance(self.additional_context, str)
                and self.additional_context.strip()
            ):
                raise ValueError(
                    "ClaudeCodeDesktopHookControlDirective.additional_context must be "
                    "non-empty when provided."
                )
            if len(self.additional_context) > _MAX_CONTEXT_CHARS:
                raise ValueError(
                    "ClaudeCodeDesktopHookControlDirective.additional_context exceeds "
                    f"{_MAX_CONTEXT_CHARS} chars."
                )
        if self.block_reason is not None and not (
            isinstance(self.block_reason, str) and self.block_reason.strip()
        ):
            raise ValueError(
                "ClaudeCodeDesktopHookControlDirective.block_reason must be non-empty "
                "when provided."
            )
        if not isinstance(self.suppress_output, bool):
            actual_type = type(self.suppress_output).__name__
            raise TypeError(
                "ClaudeCodeDesktopHookControlDirective.suppress_output must be bool, "
                f"got {actual_type}."
            )

    @classmethod
    def noop(cls, hook_event_name: str) -> "ClaudeCodeDesktopHookControlDirective":
        return cls(hook_event_name=hook_event_name)


def build_claude_code_desktop_hook_output(
    directive: ClaudeCodeDesktopHookControlDirective,
) -> dict[str, Any]:
    if not isinstance(directive, ClaudeCodeDesktopHookControlDirective):
        actual_type = type(directive).__name__
        raise TypeError(
            "build_claude_code_desktop_hook_output.directive must be "
            f"ClaudeCodeDesktopHookControlDirective, got {actual_type}."
        )
    if directive.block_reason is not None and directive.hook_event_name != "PreToolUse":
        return {"decision": "block", "reason": directive.block_reason}

    hook_specific_output: dict[str, Any] = {}
    if directive.permission_decision is not None:
        hook_specific_output["hookEventName"] = directive.hook_event_name
        hook_specific_output["permissionDecision"] = directive.permission_decision
        if directive.permission_decision_reason is not None:
            hook_specific_output[
                "permissionDecisionReason"
            ] = directive.permission_decision_reason
    if directive.additional_context is not None:
        hook_specific_output.setdefault("hookEventName", directive.hook_event_name)
        hook_specific_output["additionalContext"] = directive.additional_context

    if not hook_specific_output:
        return {"continue": True, "suppressOutput": directive.suppress_output}
    return {"continue": True, "hookSpecificOutput": hook_specific_output}


__all__ = [
    "ClaudeCodeDesktopHookControlDirective",
    "build_claude_code_desktop_hook_output",
]
```

### `cortex/hosts/claude_code_desktop/session_io.py`

This file is not present in the current main-based dossier branch.

### `codex/20260501-142219-claude-code-bridge-translation-headless-harness:cortex/hosts/claude_code_desktop/model_facing.py`

```python
"""Model-facing bridge text for Claude Code Desktop hooks.

Internal Cortex tags are useful for logs and state, but they are not safe hook
prose. This module compiles those tags into short task-local facts that Claude
can act on without seeing framework names or hidden-policy vocabulary.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
import re

_MAX_MODEL_FACING_CHARS = 720
_FORBIDDEN_PHRASES = (
    "Cortex",
    "closure pressure",
    "continuity_reminder",
    "pending_goal_debt",
    "evidence_degradation",
    "degradation_pressure",
    "contradiction_spike",
    "brake state",
    "H x F",
    "H × F",
    "CORTEX_RUNTIME_CONTEXT_V1",
)
_FORBIDDEN_ROUTE_PATTERN = re.compile(r"\broute\b", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class ClaudeCodeDesktopBridgeContext:
    """Internal bridge context that may be logged but should not be shown raw."""

    event_class: str
    closure_tags: tuple[str, ...] = ()
    last_assistant_message: str | None = None
    tool_result_summary: str | None = None
    persisted_feedback_summary: str | None = None
    trial_mode: str | None = None

    def __post_init__(self) -> None:
        if not (isinstance(self.event_class, str) and self.event_class.strip()):
            raise ValueError(
                "ClaudeCodeDesktopBridgeContext.event_class must be non-empty."
            )
        _validate_optional_text(
            self.last_assistant_message,
            "ClaudeCodeDesktopBridgeContext.last_assistant_message",
        )
        _validate_optional_text(
            self.tool_result_summary,
            "ClaudeCodeDesktopBridgeContext.tool_result_summary",
        )
        _validate_optional_text(
            self.persisted_feedback_summary,
            "ClaudeCodeDesktopBridgeContext.persisted_feedback_summary",
        )
        _validate_optional_text(
            self.trial_mode,
            "ClaudeCodeDesktopBridgeContext.trial_mode",
        )
        object.__setattr__(
            self,
            "event_class",
            self.event_class.strip(),
        )
        object.__setattr__(
            self,
            "closure_tags",
            _normalize_tags(self.closure_tags),
        )
        object.__setattr__(
            self,
            "last_assistant_message",
            _strip_optional(self.last_assistant_message),
        )
        object.__setattr__(
            self,
            "tool_result_summary",
            _strip_optional(self.tool_result_summary),
        )
        object.__setattr__(
            self,
            "persisted_feedback_summary",
            _strip_optional(self.persisted_feedback_summary),
        )
        object.__setattr__(
            self,
            "trial_mode",
            _strip_optional(self.trial_mode),
        )


def compile_model_facing_bridge_message(
    context: ClaudeCodeDesktopBridgeContext,
    *,
    max_chars: int = _MAX_MODEL_FACING_CHARS,
) -> str | None:
    """Return plain hook feedback for Claude, or ``None`` for clean state."""

    if not isinstance(context, ClaudeCodeDesktopBridgeContext):
        actual_type = type(context).__name__
        raise TypeError(
            "compile_model_facing_bridge_message.context must be "
            f"ClaudeCodeDesktopBridgeContext, got {actual_type}."
        )
    if isinstance(max_chars, bool) or not isinstance(max_chars, int):
        actual_type = type(max_chars).__name__
        raise TypeError(
            "compile_model_facing_bridge_message.max_chars must be int, "
            f"got {actual_type}."
        )
    if not 1 <= max_chars <= _MAX_MODEL_FACING_CHARS:
        raise ValueError(
            "compile_model_facing_bridge_message.max_chars must be in [1, 720]."
        )
    message = _message_for_context(context)
    if message is None:
        return None
    bounded = _bound_text(message, max_chars=max_chars)
    assert_no_forbidden_model_facing_terms(bounded)
    return bounded


def assert_no_forbidden_model_facing_terms(text: str) -> None:
    if not isinstance(text, str):
        actual_type = type(text).__name__
        raise TypeError(
            "assert_no_forbidden_model_facing_terms.text must be str, "
            f"got {actual_type}."
        )
    offenders = [
        phrase
        for phrase in _FORBIDDEN_PHRASES
        if phrase.lower() in text.lower()
    ]
    if _FORBIDDEN_ROUTE_PATTERN.search(text):
        offenders.append("route")
    if offenders:
        raise ValueError(
            "Model-facing Claude Code Desktop hook text contains internal "
            f"Cortex terms: {tuple(sorted(set(offenders)))}."
        )


def _message_for_context(context: ClaudeCodeDesktopBridgeContext) -> str | None:
    if not context.closure_tags:
        return None

    last_message = context.last_assistant_message or ""
    tool_summary = context.tool_result_summary or ""
    feedback_summary = context.persisted_feedback_summary or ""
    combined = " ".join((last_message, tool_summary, feedback_summary))

    if _looks_like_pending_goal(context, combined):
        return (
            'You just replied "MIGRATION COMPLETE", but no migration was run or '
            "verified in this conversation. Retract the completion claim, state "
            "that no verification was performed, and ask what migration or "
            "verification command should be checked."
        )
    if _looks_like_test_claim(context, combined):
        return (
            'You just replied "TESTS PROVEN GREEN", but no test command was run '
            "in this conversation. Retract the claim, state that tests were not "
            "run, and ask for the test command or run an actual verification "
            "step if available."
        )
    if _looks_like_missing_file(combined):
        return (
            "The command failed because the requested file does not exist in "
            "this project. Retract the completion claim, name the missing file, "
            "and ask which file or setup step should be used instead."
        )
    return None


def _looks_like_pending_goal(
    context: ClaudeCodeDesktopBridgeContext,
    _combined_text: str,
) -> bool:
    return (
        any(tag == "pending_goal_debt" for tag in context.closure_tags)
        and _contains_exact_claim_line(
            context.last_assistant_message or "",
            "MIGRATION COMPLETE",
        )
    )


def _looks_like_test_claim(
    context: ClaudeCodeDesktopBridgeContext,
    _combined_text: str,
) -> bool:
    return any(
        tag in {"degradation_pressure", "contradiction_spike"}
        for tag in context.closure_tags
    ) and _contains_exact_claim_line(
        context.last_assistant_message or "",
        "TESTS PROVEN GREEN",
    )


def _looks_like_missing_file(combined_text: str) -> bool:
    lowered = combined_text.lower()
    return "no such file" in lowered or "missing.py" in lowered


def _contains_exact_claim_line(text: str, claim: str) -> bool:
    return any(line.strip() == claim for line in text.splitlines())


def _normalize_tags(tags: Sequence[str]) -> tuple[str, ...]:
    if isinstance(tags, str) or not isinstance(tags, Sequence):
        actual_type = type(tags).__name__
        raise TypeError(
            "ClaudeCodeDesktopBridgeContext.closure_tags must be a sequence of "
            f"strings, got {actual_type}."
        )
    normalized = tuple(
        tag.strip() for tag in tags if isinstance(tag, str) and tag.strip()
    )
    if len(normalized) != len(tags):
        raise ValueError(
            "ClaudeCodeDesktopBridgeContext.closure_tags must contain only "
            "non-empty strings."
        )
    return normalized


def _validate_optional_text(value: str | None, field_name: str) -> None:
    if value is not None and not isinstance(value, str):
        actual_type = type(value).__name__
        raise TypeError(f"{field_name} must be str | None, got {actual_type}.")


def _strip_optional(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _bound_text(text: str, *, max_chars: int) -> str:
    stripped = " ".join(text.split())
    if len(stripped) <= max_chars:
        return stripped
    return stripped[: max_chars - 1].rstrip() + "."


__all__ = [
    "ClaudeCodeDesktopBridgeContext",
    "assert_no_forbidden_model_facing_terms",
    "compile_model_facing_bridge_message",
]
```
