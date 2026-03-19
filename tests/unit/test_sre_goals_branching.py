"""Focused unit tests for SRE goal continuity and branch operations."""

import pytest

from cortex.sre.branching import BranchOperation
from cortex.sre.brake import BrakeState
from cortex.sre.families import SoftControlFamily
from cortex.sre.goals import GoalContinuityView
from cortex.sre.state import (
    ReferenceBrakeView,
    ReferenceControlAllocationView,
    ReferenceExecutiveState,
    ReferenceGoalContinuityView,
    ReferenceModeAndGatingView,
    ReferenceUncertaintyMonitoringView,
)
from cortex.sre.uncertainty import UncertaintyEstimate


def test_goal_continuity_view_preserves_goal_and_pending_goal_fields() -> None:
    view = GoalContinuityView(
        main_goal_ref="goal-main",
        active_track_ref="track-alpha",
        pending_goal_refs=("goal-side-a", "goal-side-b"),
        resume_anchor_available=True,
    )

    assert view.main_goal_ref == "goal-main"
    assert view.active_track_ref == "track-alpha"
    assert view.pending_goal_refs == ("goal-side-a", "goal-side-b")
    assert view.resume_anchor_available is True


def test_goal_continuity_view_requires_non_empty_main_goal_ref_when_provided() -> None:
    view = GoalContinuityView(main_goal_ref="goal-main")

    assert view.main_goal_ref == "goal-main"

    with pytest.raises(
        ValueError,
        match=(
            "GoalContinuityView.main_goal_ref must be non-empty after trimming "
            "when provided."
        ),
    ):
        GoalContinuityView(main_goal_ref="   ")


def test_branch_operation_set_is_exact() -> None:
    assert {operation.value for operation in BranchOperation} == {
        "open",
        "suspend",
        "resume",
        "merge",
        "abandon",
    }


def test_reference_executive_state_uses_canonical_goal_carrier_directly() -> None:
    state = ReferenceExecutiveState(
        goal_continuity=GoalContinuityView(
            main_goal_ref="goal-main",
            active_track_ref="track-alpha",
            pending_goal_refs=("goal-side-a",),
            resume_anchor_available=True,
        ),
        uncertainty_monitoring=ReferenceUncertaintyMonitoringView(
            classwise_uncertainty=(UncertaintyEstimate(class_tag="evidence", level=0.2),),
        ),
        mode_and_gating=ReferenceModeAndGatingView(
            mode_tag="pass_through",
            family_mask=frozenset({SoftControlFamily.NEUTRAL}),
        ),
        control_allocation=ReferenceControlAllocationView(
            budget_band="low",
            top_family_set=frozenset({SoftControlFamily.NEUTRAL}),
        ),
        brake=ReferenceBrakeView(brake_state=BrakeState.QUIESCENT),
    )

    assert isinstance(state.goal_continuity, GoalContinuityView)
    assert state.goal_continuity.main_goal_ref == "goal-main"


def test_reference_state_surface_keeps_only_a_compatibility_alias_for_goal_view() -> None:
    assert ReferenceGoalContinuityView is GoalContinuityView
