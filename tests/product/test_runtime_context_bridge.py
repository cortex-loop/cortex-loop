"""Tests for model-visible runtime context built from last feedback only."""

from __future__ import annotations

from cortex.hosts.runtime_context import (
    RUNTIME_CONTEXT_HEADER,
    runtime_context_from_last_feedback,
)
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


def test_runtime_context_emits_fixed_fields_for_newest_noisy_feedback() -> None:
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
    lines = context.splitlines()
    assert lines[0] == RUNTIME_CONTEXT_HEADER
    assert lines[1] == "source: last_feedback_only; no_accumulation=true"
    assert lines[2].startswith("prior_result: selected=check; realized=check; brake=guarded")
    assert lines[3] == (
        "progress_signal: evidence=token-stream; continuity=none; probe=none"
    )
    assert lines[4] == (
        "disruption_signal: warnings=none; "
        "friction=capability-view-missing; override=no"
    )
    assert lines[5].startswith(
        "next_call_constraint: Do not treat generated text as evidence;"
    )
    assert "old-friction-token" not in context


def test_runtime_context_field_bounds_and_token_truncation() -> None:
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
    assert len(context) <= 720
    lines = context.splitlines()
    assert len(lines[1]) <= 64
    assert 40 <= len(lines[2]) <= 96
    assert 45 <= len(lines[3]) <= 120
    assert 30 <= len(lines[4]) <= 160
    assert 80 <= len(lines[5]) <= 180
    assert "third-warning-ignored" not in context
    assert "third-friction-ignored" not in context
    assert "..." in lines[4]


def test_runtime_context_priority_uses_continuity_warning_first() -> None:
    feedback = _feedback(
        warning_codes=("continuity-rejected:missing-open-track-ref",),
        probe_result_class="unsupported",
        evidence_progress_class="token-stream",
        continuity_progress_class="none",
    )

    context = runtime_context_from_last_feedback(feedback)

    assert context is not None
    assert "recover the missing continuity/session anchor" in context
    assert "unavailable probe" not in context


def test_runtime_context_priority_uses_probe_failure_before_low_evidence() -> None:
    feedback = _feedback(
        probe_result_class="unsupported",
        evidence_progress_class="token-stream",
        continuity_progress_class="none",
    )

    context = runtime_context_from_last_feedback(feedback)

    assert context is not None
    assert "Do not rely on the unavailable probe" in context
    assert "Do not treat generated text as evidence" not in context


def test_runtime_context_priority_uses_guarded_check_for_override_or_brake() -> None:
    feedback = _feedback(
        selected=SoftControlFamily.BRANCH,
        realized=SoftControlFamily.CHECK,
        brake_state=BrakeState.GUARDED,
        evidence_progress_class="artifact",
    )

    context = runtime_context_from_last_feedback(feedback)

    assert context is not None
    assert "Use a guarded check before acting or closing" in context


def test_runtime_context_priority_uses_friction_fallback() -> None:
    feedback = _feedback(host_friction_tags=("capability-view-missing",))

    context = runtime_context_from_last_feedback(feedback)

    assert context is not None
    assert "Account for prior host friction" in context


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
