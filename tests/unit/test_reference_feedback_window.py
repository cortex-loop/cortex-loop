"""Unit tests for the bounded reference realization-feedback window carrier."""

from __future__ import annotations

from cortex.sre.brake import BrakeState
from cortex.sre.feedback import (
    ReferenceRealizationFeedback,
    ReferenceRealizationFeedbackWindow,
)
from cortex.sre.families import SoftControlFamily


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


def _feedback(warning_code: str) -> ReferenceRealizationFeedback:
    return ReferenceRealizationFeedback(
        selected_family=SoftControlFamily.NEUTRAL,
        realized_family=SoftControlFamily.NEUTRAL,
        brake_state=BrakeState.QUIESCENT,
        warning_codes=(warning_code,),
    )
