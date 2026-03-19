"""Focused unit tests for the first active SRE hinge."""

import pytest

from cortex.sre.allocation import AllocationScore, AllocationScorecard
from cortex.sre.brake import BrakeState
from cortex.sre.families import REFERENCE_SOFT_CONTROL_FAMILIES, SoftControlFamily
from cortex.sre.policy import neutral_dominance_decision
from cortex.sre.state import (
    ReferenceBrakeView,
    ReferenceControlAllocationView,
    ReferenceExecutiveState,
    ReferenceGoalContinuityView,
    ReferenceModeAndGatingView,
    ReferenceUncertaintyMonitoringView,
)
from cortex.sre.uncertainty import UncertaintyEstimate


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
            classwise_uncertainty=(UncertaintyEstimate("evidence", 0.25),),
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
            brake_state=BrakeState.QUIESCENT,
            dominant_cause_family=None,
        ),
    )

    assert state.goal_continuity.main_goal_ref == "goal-1"
    assert state.uncertainty_monitoring.classwise_uncertainty[0].class_tag == "evidence"
    assert state.mode_and_gating.family_mask == frozenset(
        {SoftControlFamily.NEUTRAL, SoftControlFamily.CHECK}
    )
    assert state.control_allocation.budget_band == "medium"
    assert state.brake.brake_state is BrakeState.QUIESCENT


def test_reference_executive_state_uses_canonical_uncertainty_and_brake_types() -> None:
    state = ReferenceExecutiveState(
        goal_continuity=ReferenceGoalContinuityView(),
        uncertainty_monitoring=ReferenceUncertaintyMonitoringView(
            classwise_uncertainty=(
                UncertaintyEstimate(
                    class_tag="host-capability",
                    level=0.6,
                    spike_tags=frozenset({"environment-inconsistency"}),
                ),
            ),
            contradiction_spike_flags=frozenset({"environment-inconsistency"}),
        ),
        mode_and_gating=ReferenceModeAndGatingView(mode_tag="pass_through"),
        control_allocation=ReferenceControlAllocationView(budget_band="low"),
        brake=ReferenceBrakeView(brake_state=BrakeState.GUARDED),
    )

    assert isinstance(
        state.uncertainty_monitoring.classwise_uncertainty[0],
        UncertaintyEstimate,
    )
    assert isinstance(state.brake.brake_state, BrakeState)


def test_reference_uncertainty_monitoring_view_requires_typed_classwise_uncertainty() -> None:
    view = ReferenceUncertaintyMonitoringView(
        classwise_uncertainty=(UncertaintyEstimate("evidence", 0.25),),
    )

    assert isinstance(view.classwise_uncertainty[0], UncertaintyEstimate)

    with pytest.raises(
        TypeError,
        match=(
            "ReferenceUncertaintyMonitoringView.classwise_uncertainty must "
            "contain only UncertaintyEstimate instances."
        ),
    ):
        ReferenceUncertaintyMonitoringView(classwise_uncertainty=("not-estimate",))


def test_reference_uncertainty_monitoring_view_requires_non_empty_contradiction_spike_flags() -> None:
    view = ReferenceUncertaintyMonitoringView(
        contradiction_spike_flags=frozenset({"host-spike"}),
    )

    assert view.contradiction_spike_flags == frozenset({"host-spike"})

    with pytest.raises(
        ValueError,
        match=(
            "ReferenceUncertaintyMonitoringView.contradiction_spike_flags must "
            "contain only non-empty values after trimming."
        ),
    ):
        ReferenceUncertaintyMonitoringView(
            contradiction_spike_flags=frozenset({"   "})
        )


def test_reference_mode_and_gating_view_requires_non_empty_mode_tag() -> None:
    view = ReferenceModeAndGatingView(mode_tag="pass_through")

    assert view.mode_tag == "pass_through"

    with pytest.raises(
        ValueError,
        match=(
            "ReferenceModeAndGatingView.mode_tag must be non-empty after trimming."
        ),
    ):
        ReferenceModeAndGatingView(mode_tag="   ")


def test_reference_state_surface_does_not_export_duplicate_uncertainty_carrier() -> None:
    from cortex.sre import state as state_module

    assert not hasattr(state_module, "ReferenceUncertaintyReading")


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


def test_neutral_dominance_keeps_neutral_on_exact_threshold_tie() -> None:
    decision = neutral_dominance_decision(
        AllocationScorecard(
            scores=(
                AllocationScore(SoftControlFamily.NEUTRAL, 1.0),
                AllocationScore(SoftControlFamily.CHECK, 1.0),
            ),
            activation_threshold=0.0,
        )
    )

    assert decision.selected_family is SoftControlFamily.NEUTRAL
    assert decision.neutral_selected is True
    assert decision.margin_over_neutral == 0.0


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
