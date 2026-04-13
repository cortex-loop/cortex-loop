from __future__ import annotations

import pytest

from cortex.sre.brake import BrakeState
from cortex.sre.goal_debt import (
    build_closure_pressure_state,
    build_goal_debt_state,
)
from cortex.sre.goals import make_resume_reminder


def test_goal_debt_state_surfaces_explicit_debt_buckets() -> None:
    state = build_goal_debt_state(
        active_track_ref="review-track",
        pending_goal_refs=("goal-1",),
        continuity_warnings=("continuity-rejected:review-track",),
        continuity_reminders=(make_resume_reminder("review-track"),),
        degradation_pressure_bonus=2,
        sustained_spike_flags=("host/runtime",),
        repeated_failure_pressure=0.75,
        verification_conflict_pressure=0.65,
        quota_pressure=0.50,
        brake_state=BrakeState.GUARDED,
    )

    assert state.unfinished_goal_debt == 1.0
    assert state.contradiction_rejection_debt > 0.9
    assert state.verification_debt > 0.65
    assert state.quota_burden_stop_pressure > 0.50


def test_closure_pressure_state_preserves_compact_runtime_reason_tags() -> None:
    closure = build_closure_pressure_state(
        active_track_ref="main",
        pending_goal_refs=("goal-1",),
        continuity_warnings=("continuity-rejected:goal-1",),
        continuity_reminders=(make_resume_reminder("goal-1"),),
        degradation_pressure_bonus=1,
        sustained_spike_flags=("host/runtime",),
        repeated_failure_pressure=0.35,
        verification_conflict_pressure=0.45,
        quota_pressure=0.25,
        brake_state=BrakeState.LATCHED,
    )

    assert closure.closure_required is True
    assert closure.closure_pressure >= 1.0
    assert closure.closure_reason_tags == (
        "continuity_rejection",
        "continuity_reminder",
        "contradiction_spike",
        "degradation_pressure",
        "latched_brake",
        "pending_goal_debt",
    )


def test_goal_debt_state_requires_brake_type() -> None:
    with pytest.raises(TypeError, match="BrakeState"):
        build_goal_debt_state(
            active_track_ref="main",
            pending_goal_refs=(),
            continuity_warnings=(),
            continuity_reminders=(),
            degradation_pressure_bonus=0,
            sustained_spike_flags=(),
            repeated_failure_pressure=0.0,
            verification_conflict_pressure=0.0,
            quota_pressure=0.0,
            brake_state="guarded",
        )
