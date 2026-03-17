"""Focused unit tests for the first active SRE hinge."""

from cortex.sre.allocation import AllocationScore, AllocationScorecard
from cortex.sre.families import REFERENCE_SOFT_CONTROL_FAMILIES, SoftControlFamily
from cortex.sre.policy import neutral_dominance_decision
from cortex.sre.state import (
    ReferenceBrakeView,
    ReferenceControlAllocationView,
    ReferenceExecutiveState,
    ReferenceGoalContinuityView,
    ReferenceModeAndGatingView,
    ReferenceUncertaintyMonitoringView,
    ReferenceUncertaintyReading,
)


def test_exact_soft_control_family_set_matches_the_packet() -> None:
    assert {family.value for family in SoftControlFamily} == {
        "neutral",
        "seek-context",
        "redirect",
        "check",
        "branch",
        "escalate",
        "brake",
    }
    assert REFERENCE_SOFT_CONTROL_FAMILIES == frozenset(SoftControlFamily)


def test_reference_executive_state_exposes_minimum_software_facing_views() -> None:
    state = ReferenceExecutiveState(
        goal_continuity=ReferenceGoalContinuityView(
            main_goal_ref="goal-1",
            active_track_ref="main",
            pending_goal_refs=("goal-2",),
            resume_anchor_available=True,
        ),
        uncertainty_monitoring=ReferenceUncertaintyMonitoringView(
            classwise_uncertainty=(ReferenceUncertaintyReading("evidence", 0.25),),
            contradiction_spike_flags=frozenset({"host-spike"}),
        ),
        mode_and_gating=ReferenceModeAndGatingView(
            mode_tag="pass_through",
            family_mask=frozenset({SoftControlFamily.NEUTRAL, SoftControlFamily.CHECK}),
        ),
        control_allocation=ReferenceControlAllocationView(
            budget_band="medium",
            top_family_set=frozenset({SoftControlFamily.NEUTRAL}),
            host_friction_tags=frozenset({"low-friction"}),
        ),
        brake=ReferenceBrakeView(
            brake_state="quiescent",
            dominant_cause_family=None,
        ),
    )

    assert state.goal_continuity.main_goal_ref == "goal-1"
    assert state.uncertainty_monitoring.classwise_uncertainty[0].class_tag == "evidence"
    assert state.mode_and_gating.family_mask == frozenset(
        {SoftControlFamily.NEUTRAL, SoftControlFamily.CHECK}
    )
    assert state.control_allocation.budget_band == "medium"
    assert state.brake.brake_state == "quiescent"


def test_neutral_dominance_returns_neutral_when_margin_is_below_threshold() -> None:
    decision = neutral_dominance_decision(
        AllocationScorecard(
            scores=(
                AllocationScore(SoftControlFamily.NEUTRAL, 1.0),
                AllocationScore(SoftControlFamily.CHECK, 1.19),
                AllocationScore(SoftControlFamily.SEEK_CONTEXT, 0.8),
            ),
            activation_threshold=0.2,
        )
    )

    assert decision.selected_family is SoftControlFamily.NEUTRAL
    assert decision.neutral_selected is True
    assert abs(decision.margin_over_neutral - 0.19) < 1e-12


def test_neutral_dominance_returns_strongest_non_neutral_when_threshold_is_met() -> None:
    decision = neutral_dominance_decision(
        AllocationScorecard(
            scores=(
                AllocationScore(SoftControlFamily.NEUTRAL, 1.0),
                AllocationScore(SoftControlFamily.CHECK, 1.25),
                AllocationScore(SoftControlFamily.REDIRECT, 1.4),
            ),
            activation_threshold=0.2,
        )
    )

    assert decision.selected_family is SoftControlFamily.REDIRECT
    assert decision.neutral_selected is False
    assert abs(decision.margin_over_neutral - 0.4) < 1e-12


def test_neutral_path_law_rejects_scorecards_that_omit_neutral() -> None:
    try:
        neutral_dominance_decision(
            AllocationScorecard(
                scores=(AllocationScore(SoftControlFamily.CHECK, 1.0),),
                activation_threshold=0.1,
            )
        )
    except ValueError as exc:
        assert "NEUTRAL" in str(exc)
    else:
        raise AssertionError("Neutral dominance accepted a scorecard without neutral.")
