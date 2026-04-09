"""Unit tests for the bounded reference realization-feedback carrier."""

from __future__ import annotations

import pytest

from experimental.sre.brake import BrakeState
from experimental.sre.families import SoftControlFamily
from experimental.sre.feedback import ReferenceRealizationFeedback


def test_reference_realization_feedback_preserves_last_step_shell_outcome() -> None:
    feedback = ReferenceRealizationFeedback(
        selected_family=SoftControlFamily.BRANCH,
        realized_family=SoftControlFamily.NEUTRAL,
        brake_state=BrakeState.LATCHED,
        commitment_result_kind="certified",
        warning_codes=("continuity-rejected:missing-open-track-ref",),
        host_friction_tags=("approval-boundary-present", "single-process-limit"),
    )

    assert feedback.as_summary() == {
        "selected_family": "branch",
        "realized_family": "neutral",
        "brake_state": "latched",
        "commitment_result_kind": "certified",
        "warning_codes": ["continuity-rejected:missing-open-track-ref"],
        "host_friction_tags": ["approval-boundary-present", "single-process-limit"],
    }


def test_reference_realization_feedback_rejects_noncanonical_commitment_kind() -> None:
    with pytest.raises(
        ValueError,
        match="must be one of the canonical commitment status values or None",
    ):
        ReferenceRealizationFeedback(
            selected_family=SoftControlFamily.NEUTRAL,
            realized_family=SoftControlFamily.NEUTRAL,
            brake_state=BrakeState.QUIESCENT,
            commitment_result_kind="done",
        )
