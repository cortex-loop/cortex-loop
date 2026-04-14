"""Unit tests for the bounded reference realization-feedback window carrier."""

from __future__ import annotations

import pytest

from cortex.hosts.reference.runtime import ReferenceRuntimeSession
from cortex.sre.brake import BrakeState
from cortex.sre.feedback import (
    ReferenceFeedbackWindowSummary,
    ReferenceRealizationFeedback,
    ReferenceRealizationFeedbackWindow,
    summarize_reference_feedback_window,
)
from cortex.sre.families import SoftControlFamily
from cortex.sre.operator_routing import OperatorTaskMode


def test_reference_realization_feedback_window_starts_empty() -> None:
    window = ReferenceRealizationFeedbackWindow()

    assert window.entries == ()


def test_reference_realization_feedback_window_keeps_only_three_most_recent_entries() -> None:
    feedback_a = _feedback("warn-a")
    feedback_b = _feedback("warn-b")
    feedback_c = _feedback("warn-c")
    feedback_d = _feedback("warn-d")

    window = ReferenceRealizationFeedbackWindow()
    window = window.append(feedback_a)
    window = window.append(feedback_b)
    window = window.append(feedback_c)
    window = window.append(feedback_d)

    assert window.entries == (feedback_b, feedback_c, feedback_d)


def test_reference_runtime_session_normalizes_last_only_feedback_into_window() -> None:
    feedback = _feedback("session-rejected:mismatched-session-id:runtime-a")

    session = ReferenceRuntimeSession(
        session_id="runtime-a",
        last_realization_feedback=feedback,
    )

    assert session.last_realization_feedback == feedback
    assert session.feedback_window.entries == (feedback,)


def test_reference_runtime_session_normalizes_window_only_feedback_into_last_step_mirror() -> None:
    feedback = _feedback("continuity-rejected:missing-open-track-ref")

    session = ReferenceRuntimeSession(
        session_id="runtime-a",
        feedback_window=ReferenceRealizationFeedbackWindow(entries=(feedback,)),
    )

    assert session.last_realization_feedback == feedback
    assert session.feedback_window.entries == (feedback,)


def test_reference_runtime_session_rejects_mismatched_last_feedback_and_window_newest_entry() -> None:
    with pytest.raises(
        ValueError,
        match="feedback_window newest entry must match last_realization_feedback",
    ):
        ReferenceRuntimeSession(
            session_id="runtime-a",
            last_realization_feedback=_feedback(
                "session-rejected:mismatched-session-id:runtime-a"
            ),
            feedback_window=ReferenceRealizationFeedbackWindow(
                entries=(_feedback("continuity-rejected:missing-open-track-ref"),)
            ),
        )


def test_summarize_reference_feedback_window_reports_zero_pressure_for_clean_window() -> None:
    summary = summarize_reference_feedback_window(
        ReferenceRealizationFeedbackWindow(
            entries=(
                _feedback("clean-a"),
                _feedback("clean-b"),
                _feedback("clean-c"),
            )
        )
    )

    assert summary == ReferenceFeedbackWindowSummary(
        window_size=3,
        rejection_count=0,
        override_count=0,
        latched_count=0,
        clean_success_streak=3,
        goal_progress_floor=0.0,
        degradation_pressure_bonus=0,
        sustained_spike_flags=(),
    )


def test_summarize_reference_feedback_window_reports_single_rejection_floor() -> None:
    summary = summarize_reference_feedback_window(
        ReferenceRealizationFeedbackWindow(entries=(_feedback("continuity-rejected:missing-open-track-ref"),))
    )

    assert summary.goal_progress_floor == 0.55
    assert summary.rejection_count == 1
    assert summary.degradation_pressure_bonus == 1
    assert summary.sustained_spike_flags == ("prior-continuity-rejection",)


def test_summarize_reference_feedback_window_reports_repeated_rejection_floor_and_sustained_disruption() -> None:
    summary = summarize_reference_feedback_window(
        ReferenceRealizationFeedbackWindow(
            entries=(
                _feedback("continuity-rejected:missing-open-track-ref"),
                _feedback("session-rejected:mismatched-session-id:runtime-b"),
            )
        )
    )

    assert summary.goal_progress_floor == 0.70
    assert summary.rejection_count == 2
    assert summary.degradation_pressure_bonus == 2
    assert summary.sustained_spike_flags == (
        "prior-continuity-rejection",
        "prior-session-mismatch",
        "sustained-feedback-disruption",
    )


def test_summarize_reference_feedback_window_reports_repeated_override_floor() -> None:
    summary = summarize_reference_feedback_window(
        ReferenceRealizationFeedbackWindow(
            entries=(
                _feedback("clean-a", selected=SoftControlFamily.BRANCH, realized=SoftControlFamily.CHECK),
                _feedback("clean-b", selected=SoftControlFamily.ESCALATE, realized=SoftControlFamily.NEUTRAL),
            )
        )
    )

    assert summary.goal_progress_floor == 0.60
    assert summary.override_count == 2
    assert summary.degradation_pressure_bonus == 1
    assert summary.sustained_spike_flags == ("prior-enforcement-override",)


def test_summarize_reference_feedback_window_reports_mixed_rejection_and_override_bonus() -> None:
    summary = summarize_reference_feedback_window(
        ReferenceRealizationFeedbackWindow(
            entries=(
                _feedback("session-rejected:mismatched-session-id:runtime-b"),
                _feedback(
                    "clean-b",
                    selected=SoftControlFamily.BRANCH,
                    realized=SoftControlFamily.CHECK,
                    brake_state=BrakeState.LATCHED,
                ),
            )
        )
    )

    assert summary.rejection_count == 1
    assert summary.override_count == 1
    assert summary.latched_count == 1
    assert summary.goal_progress_floor == 0.55
    assert summary.degradation_pressure_bonus == 2
    assert summary.sustained_spike_flags == (
        "prior-session-mismatch",
        "prior-enforcement-override",
        "sustained-feedback-disruption",
    )


def test_summarize_reference_feedback_window_counts_same_context_retry_only_for_repeated_signed_feedback() -> None:
    summary = summarize_reference_feedback_window(
        ReferenceRealizationFeedbackWindow(
            entries=(
                ReferenceRealizationFeedback(
                    selected_family=SoftControlFamily.CHECK,
                    realized_family=SoftControlFamily.CHECK,
                    brake_state=BrakeState.GUARDED,
                    task_mode=OperatorTaskMode.INSPECT,
                    host_friction_tags=("capability-view-missing",),
                    evidence_state_moved=False,
                    continuity_improved=False,
                ),
                ReferenceRealizationFeedback(
                    selected_family=SoftControlFamily.CHECK,
                    realized_family=SoftControlFamily.CHECK,
                    brake_state=BrakeState.GUARDED,
                    task_mode=OperatorTaskMode.INSPECT,
                    host_friction_tags=("capability-view-missing",),
                    evidence_state_moved=False,
                    continuity_improved=False,
                ),
            )
        )
    )

    assert summary.same_family_no_progress_count == 1
    assert summary.same_context_retry_count == 1
    assert summary.degradation_pressure_bonus == 1


def test_summarize_reference_feedback_window_does_not_count_unsigned_legacy_feedback_as_same_context_retry() -> None:
    summary = summarize_reference_feedback_window(
        ReferenceRealizationFeedbackWindow(
            entries=(
                _feedback("clean-a", selected=SoftControlFamily.CHECK),
                _feedback("clean-b", selected=SoftControlFamily.CHECK),
            )
        )
    )

    assert summary.same_family_no_progress_count == 0
    assert summary.same_context_retry_count == 0


def _feedback(
    warning_code: str,
    *,
    selected: SoftControlFamily = SoftControlFamily.NEUTRAL,
    realized: SoftControlFamily = SoftControlFamily.NEUTRAL,
    brake_state: BrakeState = BrakeState.QUIESCENT,
) -> ReferenceRealizationFeedback:
    warning_codes = () if warning_code.startswith("clean-") else (warning_code,)
    return ReferenceRealizationFeedback(
        selected_family=selected,
        realized_family=realized,
        brake_state=brake_state,
        warning_codes=warning_codes,
    )
