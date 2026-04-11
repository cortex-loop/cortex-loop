"""Focused tests for the explicit goal-branch coupling law."""

from __future__ import annotations

import pytest

from cortex.sre.brake import BrakeState
from cortex.sre.families import SoftControlFamily
from cortex.sre.goal_branch import build_reference_goal_branch_coupling
from cortex.sre.state import (
    ReferenceBrakeView,
    ReferenceControlAllocationView,
    ReferenceExecutiveState,
    ReferenceGoalContinuityView,
    ReferenceModeAndGatingView,
    ReferenceUncertaintyMonitoringView,
)


def test_goal_branch_coupling_is_zero_without_continuity_debt() -> None:
    coupling = build_reference_goal_branch_coupling(_state())

    assert coupling.weight == pytest.approx(0.0)
    assert all(score.score == 0.0 for score in coupling.scores)


def test_goal_branch_coupling_lifts_branch_and_redirect_under_pending_goals() -> None:
    coupling = build_reference_goal_branch_coupling(
        _state(
            pending_goal_refs=("goal-a", "goal-b"),
        )
    )

    assert coupling.weight > 0.0
    assert coupling.score_for(SoftControlFamily.BRANCH).score > 0.0
    assert coupling.score_for(SoftControlFamily.REDIRECT).score > 0.0
    assert coupling.score_for(SoftControlFamily.NEUTRAL).score < 0.0
    assert "pending-goal-debt" in coupling.score_for(SoftControlFamily.BRANCH).reason_tags


def test_goal_branch_coupling_shifts_toward_check_without_resume_anchor() -> None:
    coupling = build_reference_goal_branch_coupling(
        _state(
            active_track_ref="review-track",
            resume_anchor_available=False,
        )
    )

    assert coupling.weight > 0.0
    assert coupling.score_for(SoftControlFamily.CHECK).score > 0.0
    assert coupling.score_for(SoftControlFamily.BRANCH).score > 0.0
    assert "resume-anchor-missing" in coupling.score_for(SoftControlFamily.CHECK).reason_tags


def test_goal_branch_coupling_reduces_branch_score_under_latched_brake() -> None:
    guarded = build_reference_goal_branch_coupling(
        _state(
            active_track_ref="review-track",
            resume_anchor_available=True,
            brake_state=BrakeState.GUARDED,
        )
    )
    latched = build_reference_goal_branch_coupling(
        _state(
            active_track_ref="review-track",
            resume_anchor_available=True,
            brake_state=BrakeState.LATCHED,
        )
    )

    assert latched.score_for(SoftControlFamily.BRANCH).score < guarded.score_for(
        SoftControlFamily.BRANCH
    ).score
    assert latched.score_for(SoftControlFamily.CHECK).score > guarded.score_for(
        SoftControlFamily.CHECK
    ).score


def _state(
    *,
    pending_goal_refs: tuple[str, ...] = (),
    active_track_ref: str = "main",
    resume_anchor_available: bool = False,
    brake_state: BrakeState = BrakeState.QUIESCENT,
) -> ReferenceExecutiveState:
    return ReferenceExecutiveState(
        goal_continuity=ReferenceGoalContinuityView(
            active_track_ref=active_track_ref,
            pending_goal_refs=pending_goal_refs,
            resume_anchor_available=resume_anchor_available,
        ),
        uncertainty_monitoring=ReferenceUncertaintyMonitoringView(),
        mode_and_gating=ReferenceModeAndGatingView(
            mode_tag="pass_through",
            family_mask=frozenset(SoftControlFamily),
        ),
        control_allocation=ReferenceControlAllocationView(
            budget_band="medium",
            top_family_set=frozenset({SoftControlFamily.NEUTRAL, SoftControlFamily.BRANCH}),
        ),
        brake=ReferenceBrakeView(brake_state=brake_state),
    )
