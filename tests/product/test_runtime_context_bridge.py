"""Tests for model-visible runtime context built from last feedback only."""

from __future__ import annotations

from cortex.hosts.runtime_context import runtime_context_from_last_feedback
from cortex.sre.brake import BrakeState
from cortex.sre.families import SoftControlFamily
from cortex.sre.feedback import (
    ReferenceRealizationFeedback,
    ReferenceRealizationFeedbackWindow,
)
from cortex.sre.operator_routing import OperatorTaskMode


def test_runtime_context_absent_for_missing_feedback() -> None:
    assert runtime_context_from_last_feedback(None) is None


def test_runtime_context_absent_for_clean_feedback() -> None:
    feedback = _feedback(
        selected=SoftControlFamily.CHECK,
        realized=SoftControlFamily.CHECK,
        brake_state=BrakeState.QUIESCENT,
        evidence_progress_class="artifact",
        continuity_progress_class="pending-goals-reduced",
        probe_result_class="succeeded",
    )

    assert runtime_context_from_last_feedback(feedback) is None


def test_runtime_context_uses_newest_feedback_only() -> None:
    noisy_old = _feedback(
        warning_codes=("continuity-rejected:old-anchor",),
        host_friction_tags=("old-friction-token",),
    )
    clean_new = _feedback(
        selected=SoftControlFamily.CHECK,
        realized=SoftControlFamily.CHECK,
        brake_state=BrakeState.QUIESCENT,
        evidence_progress_class="artifact",
    )
    window = ReferenceRealizationFeedbackWindow(entries=(noisy_old, clean_new))

    context = runtime_context_from_last_feedback(window.entries[-1])

    assert context is None


def test_runtime_context_emits_single_constraint_for_newest_noisy_feedback() -> None:
    feedback = _feedback(
        selected=SoftControlFamily.CHECK,
        realized=SoftControlFamily.CHECK,
        brake_state=BrakeState.GUARDED,
        evidence_progress_class="token-stream",
        continuity_progress_class="none",
        host_friction_tags=("capability-view-missing",),
    )

    context = runtime_context_from_last_feedback(feedback)

    assert context is not None
    assert context == (
        "Completion is not supported by the evidence yet. An artifact, a "
        "check, or a narrower claim is still needed before closure holds."
    )
    assert "old-friction-token" not in context
    assert "\n" not in context


def test_runtime_context_single_constraint_has_no_schema_or_internal_terms() -> None:
    feedback = _feedback(
        warning_codes=(
            "continuity-rejected:abcdefghijklmnopqrstuvwxyz",
            "session-rejected:abcdefghijklmnopqrstuvwxyz",
            "third-warning-ignored",
        ),
        host_friction_tags=(
            "friction-token-abcdefghijklmnopqrstuvwxyz",
            "second-friction-token-abcdefghijklmnopqrstuvwxyz",
            "third-friction-ignored",
        ),
        evidence_progress_class="none",
        continuity_progress_class="none",
    )

    context = runtime_context_from_last_feedback(feedback)

    assert context is not None
    assert context == (
        "Continuity is not anchored enough for closure. Prior context needs "
        "to be recovered, or the missing context needs to be asked for, "
        "before closure holds."
    )
    forbidden_fragments = (
        "CORTEX_RUNTIME_CONTEXT_V1",
        "source:",
        "prior_result:",
        "progress_signal:",
        "disruption_signal:",
        "next_call_constraint:",
        "closure_pressure",
        "pending_goal_debt",
        "brake",
        "tonic",
        "EMA",
        "AUX",
        "route_profile",
        "selected_margin",
        "Cortex says",
        "PreToolUse",
        "UserPromptSubmit",
        "session_id",
        "you should",
        "you must",
        "Do not",
    )
    for fragment in forbidden_fragments:
        assert fragment not in context


def test_runtime_context_priority_uses_continuity_warning_first() -> None:
    feedback = _feedback(
        warning_codes=("continuity-rejected:missing-open-track-ref",),
        probe_result_class="unsupported",
        evidence_progress_class="token-stream",
        continuity_progress_class="none",
    )

    context = runtime_context_from_last_feedback(feedback)

    assert context is not None
    assert context.startswith("Continuity is not anchored enough for closure.")
    assert "usual check" not in context


def test_runtime_context_priority_uses_probe_failure_before_low_evidence() -> None:
    feedback = _feedback(
        probe_result_class="unsupported",
        evidence_progress_class="token-stream",
        continuity_progress_class="none",
    )

    context = runtime_context_from_last_feedback(feedback)

    assert context is not None
    assert context == (
        "The usual check did not come through. Alternate evidence from the "
        "current task is needed, or the work should close as blocked for "
        "missing information."
    )
    assert "blocked_missing_info" not in context
    assert "Completion is not supported" not in context


def test_runtime_context_priority_uses_guarded_check_for_override_or_brake() -> None:
    feedback = _feedback(
        selected=SoftControlFamily.BRANCH,
        realized=SoftControlFamily.CHECK,
        brake_state=BrakeState.GUARDED,
        evidence_progress_class="artifact",
    )

    context = runtime_context_from_last_feedback(feedback)

    assert context is not None
    assert context == (
        "Something in the prior step is unresolved. A check is needed before "
        "the next action is treated as safe to continue."
    )


def test_runtime_context_retires_generic_friction_fallback() -> None:
    feedback = _feedback(host_friction_tags=("capability-view-missing",))

    context = runtime_context_from_last_feedback(feedback)

    assert context is None


def _feedback(
    *,
    selected: SoftControlFamily = SoftControlFamily.CHECK,
    realized: SoftControlFamily = SoftControlFamily.CHECK,
    brake_state: BrakeState = BrakeState.QUIESCENT,
    warning_codes: tuple[str, ...] = (),
    host_friction_tags: tuple[str, ...] = (),
    evidence_progress_class: str | None = None,
    continuity_progress_class: str | None = None,
    probe_result_class: str | None = None,
) -> ReferenceRealizationFeedback:
    return ReferenceRealizationFeedback(
        selected_family=selected,
        realized_family=realized,
        brake_state=brake_state,
        task_mode=OperatorTaskMode.INSPECT,
        warning_codes=warning_codes,
        host_friction_tags=host_friction_tags,
        evidence_progress_class=evidence_progress_class,
        continuity_progress_class=continuity_progress_class,
        probe_result_class=probe_result_class,
    )
