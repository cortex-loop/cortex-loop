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


def test_goal_continuity_view_requires_non_empty_active_track_ref_when_provided() -> None:
    view = GoalContinuityView(active_track_ref="track-alpha")

    assert view.active_track_ref == "track-alpha"

    with pytest.raises(
        ValueError,
        match=(
            "GoalContinuityView.active_track_ref must be non-empty after trimming "
            "when provided."
        ),
    ):
        GoalContinuityView(active_track_ref="   ")


def test_goal_continuity_view_requires_non_empty_pending_goal_refs() -> None:
    view = GoalContinuityView(pending_goal_refs=("goal-side-a", "goal-side-b"))

    assert view.pending_goal_refs == ("goal-side-a", "goal-side-b")

    with pytest.raises(
        ValueError,
        match=(
            "GoalContinuityView.pending_goal_refs must contain only non-empty values "
            "after trimming."
        ),
    ):
        GoalContinuityView(pending_goal_refs=("goal-side-a", "   "))


def test_goal_continuity_view_requires_bool_resume_anchor_available() -> None:
    view = GoalContinuityView(resume_anchor_available=True)

    assert view.resume_anchor_available is True

    with pytest.raises(
        TypeError,
        match="GoalContinuityView.resume_anchor_available must be bool",
    ):
        GoalContinuityView(resume_anchor_available="yes")


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


def test_reference_executive_state_requires_typed_goal_continuity() -> None:
    with pytest.raises(
        TypeError,
        match="ReferenceExecutiveState.goal_continuity must be GoalContinuityView",
    ):
        ReferenceExecutiveState(
            goal_continuity="nope",
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


def test_reference_executive_state_requires_typed_uncertainty_monitoring() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "ReferenceExecutiveState.uncertainty_monitoring must be "
            "ReferenceUncertaintyMonitoringView"
        ),
    ):
        ReferenceExecutiveState(
            goal_continuity=GoalContinuityView(
                main_goal_ref="goal-main",
                active_track_ref="track-alpha",
                pending_goal_refs=("goal-side-a",),
                resume_anchor_available=True,
            ),
            uncertainty_monitoring="nope",
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


def test_reference_executive_state_requires_typed_mode_and_gating() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "ReferenceExecutiveState.mode_and_gating must be "
            "ReferenceModeAndGatingView"
        ),
    ):
        ReferenceExecutiveState(
            goal_continuity=GoalContinuityView(
                main_goal_ref="goal-main",
                active_track_ref="track-alpha",
                pending_goal_refs=("goal-side-a",),
                resume_anchor_available=True,
            ),
            uncertainty_monitoring=ReferenceUncertaintyMonitoringView(
                classwise_uncertainty=(UncertaintyEstimate(class_tag="evidence", level=0.2),),
            ),
            mode_and_gating="nope",
            control_allocation=ReferenceControlAllocationView(
                budget_band="low",
                top_family_set=frozenset({SoftControlFamily.NEUTRAL}),
            ),
            brake=ReferenceBrakeView(brake_state=BrakeState.QUIESCENT),
        )


def test_reference_state_surface_keeps_only_a_compatibility_alias_for_goal_view() -> None:
    assert ReferenceGoalContinuityView is GoalContinuityView
