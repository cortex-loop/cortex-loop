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


def test_reference_mode_and_gating_view_requires_typed_family_mask() -> None:
    view = ReferenceModeAndGatingView(
        mode_tag="pass_through",
        family_mask=frozenset({SoftControlFamily.NEUTRAL}),
    )

    assert view.family_mask == frozenset({SoftControlFamily.NEUTRAL})

    with pytest.raises(
        TypeError,
        match=(
            "ReferenceModeAndGatingView.family_mask must contain only "
            "SoftControlFamily instances."
        ),
    ):
        ReferenceModeAndGatingView(
            mode_tag="pass_through",
            family_mask=frozenset({"neutral"}),
        )


def test_reference_control_allocation_view_requires_non_empty_budget_band() -> None:
    view = ReferenceControlAllocationView(budget_band="low")

    assert view.budget_band == "low"

    with pytest.raises(
        ValueError,
        match=(
            "ReferenceControlAllocationView.budget_band must be non-empty after trimming."
        ),
    ):
        ReferenceControlAllocationView(budget_band="   ")


def test_reference_control_allocation_view_requires_typed_top_family_set() -> None:
    view = ReferenceControlAllocationView(
        budget_band="low",
        top_family_set=frozenset({SoftControlFamily.NEUTRAL}),
    )

    assert view.top_family_set == frozenset({SoftControlFamily.NEUTRAL})

    with pytest.raises(
        TypeError,
        match=(
            "ReferenceControlAllocationView.top_family_set must contain only "
            "SoftControlFamily instances."
        ),
    ):
        ReferenceControlAllocationView(
            budget_band="low",
            top_family_set=frozenset({"neutral"}),
        )


def test_reference_control_allocation_view_requires_non_empty_host_friction_tags() -> None:
    view = ReferenceControlAllocationView(
        budget_band="low",
        host_friction_tags=frozenset({"low-friction"}),
    )

    assert view.host_friction_tags == frozenset({"low-friction"})

    with pytest.raises(
        ValueError,
        match=(
            "ReferenceControlAllocationView.host_friction_tags must contain only "
            "non-empty values after trimming."
        ),
    ):
        ReferenceControlAllocationView(
            budget_band="low",
            host_friction_tags=frozenset({"   "}),
        )


def test_reference_brake_view_requires_typed_brake_state() -> None:
    view = ReferenceBrakeView(brake_state=BrakeState.GUARDED)

    assert view.brake_state is BrakeState.GUARDED

    with pytest.raises(
        TypeError,
        match="ReferenceBrakeView.brake_state must be BrakeState",
    ):
        ReferenceBrakeView(brake_state="guarded")


def test_reference_brake_view_requires_typed_dominant_cause_family() -> None:
    view = ReferenceBrakeView(
        brake_state=BrakeState.GUARDED,
        dominant_cause_family=SoftControlFamily.BRAKE,
    )

    assert view.dominant_cause_family is SoftControlFamily.BRAKE

    with pytest.raises(
        TypeError,
        match=(
            "ReferenceBrakeView.dominant_cause_family must be SoftControlFamily "
            "when provided"
        ),
    ):
        ReferenceBrakeView(
            brake_state=BrakeState.GUARDED,
            dominant_cause_family="brake",
        )


def test_reference_state_surface_does_not_export_duplicate_uncertainty_carrier() -> None:
    from cortex.sre import state as state_module

    assert not hasattr(state_module, "ReferenceUncertaintyReading")


def test_allocation_score_requires_typed_family() -> None:
    score = AllocationScore(SoftControlFamily.NEUTRAL, 1.0)

    assert score.family is SoftControlFamily.NEUTRAL

    with pytest.raises(
        TypeError,
        match="AllocationScore.family must be SoftControlFamily",
    ):
        AllocationScore("neutral", 1.0)


def test_allocation_score_requires_numeric_score() -> None:
    score = AllocationScore(SoftControlFamily.NEUTRAL, 1.0)

    assert score.score == 1.0
    assert score.online_score == 1.0
    assert score.memory_score == 0.0
    assert score.allocated_score == 1.0

    with pytest.raises(
        TypeError,
        match="AllocationScore.score must be numeric",
    ):
        AllocationScore(SoftControlFamily.NEUTRAL, "1.0")


def test_allocation_score_defaults_online_and_allocated_to_score() -> None:
    score = AllocationScore(
        SoftControlFamily.CHECK,
        1.25,
        reason_tags=frozenset({"top-family"}),
    )

    assert score.as_summary() == {
        "family": "check",
        "online_score": 1.25,
        "memory_score": 0.0,
        "allocated_score": 1.25,
        "admissible": True,
        "reason_tags": ["top-family"],
    }


def test_allocation_score_requires_bool_admissible() -> None:
    score = AllocationScore(SoftControlFamily.NEUTRAL, 1.0, admissible=True)

    assert score.admissible is True

    with pytest.raises(
        TypeError,
        match="AllocationScore.admissible must be bool",
    ):
        AllocationScore(SoftControlFamily.NEUTRAL, 1.0, admissible="yes")


def test_allocation_score_requires_non_empty_reason_tags() -> None:
    score = AllocationScore(
        SoftControlFamily.NEUTRAL,
        1.0,
        reason_tags=frozenset({"baseline-neutral"}),
    )

    assert score.reason_tags == frozenset({"baseline-neutral"})

    with pytest.raises(
        ValueError,
        match=(
            "AllocationScore.reason_tags must contain only non-empty values "
            "after trimming."
        ),
    ):
        AllocationScore(
            SoftControlFamily.NEUTRAL,
            1.0,
            reason_tags=frozenset({"   "}),
        )


def test_allocation_scorecard_requires_typed_scores() -> None:
    scorecard = AllocationScorecard(
        scores=(AllocationScore(SoftControlFamily.NEUTRAL, 1.0),),
        activation_threshold=0.1,
    )

    assert len(scorecard.scores) == 1

    with pytest.raises(
        TypeError,
        match="AllocationScorecard.scores must contain only AllocationScore instances.",
    ):
        AllocationScorecard(scores=("not-score",), activation_threshold=0.1)


def test_allocation_scorecard_requires_numeric_activation_threshold() -> None:
    scorecard = AllocationScorecard(
        scores=(AllocationScore(SoftControlFamily.NEUTRAL, 1.0),),
        activation_threshold=0.1,
    )

    assert scorecard.activation_threshold == 0.1

    with pytest.raises(
        TypeError,
        match="AllocationScorecard.activation_threshold must be numeric",
    ):
        AllocationScorecard(
            scores=(AllocationScore(SoftControlFamily.NEUTRAL, 1.0),),
            activation_threshold="0.1",
        )


def test_allocation_scorecard_requires_alpha_in_unit_interval() -> None:
    scorecard = AllocationScorecard(
        scores=(AllocationScore(SoftControlFamily.NEUTRAL, 1.0),),
        activation_threshold=0.1,
        alpha_t=1.0,
    )

    assert scorecard.alpha_t == 1.0

    with pytest.raises(
        TypeError,
        match="AllocationScorecard.alpha_t must be numeric",
    ):
        AllocationScorecard(
            scores=(AllocationScore(SoftControlFamily.NEUTRAL, 1.0),),
            activation_threshold=0.1,
            alpha_t="1.0",
        )

    with pytest.raises(
        ValueError,
        match="AllocationScorecard.alpha_t must be between 0.0 and 1.0",
    ):
        AllocationScorecard(
            scores=(AllocationScore(SoftControlFamily.NEUTRAL, 1.0),),
            activation_threshold=0.1,
            alpha_t=1.5,
        )


def test_neutral_dominance_decision_requires_typed_selected_family() -> None:
    decision = neutral_dominance_decision(
        AllocationScorecard(
            scores=(
                AllocationScore(SoftControlFamily.NEUTRAL, 1.0),
                AllocationScore(SoftControlFamily.CHECK, 1.2),
            ),
            activation_threshold=0.1,
        )
    )

    assert isinstance(decision.selected_family, SoftControlFamily)

    with pytest.raises(
        TypeError,
        match="NeutralDominanceDecision.selected_family must be SoftControlFamily",
    ):
        from cortex.sre.policy import NeutralDominanceDecision

        NeutralDominanceDecision(
            selected_family="neutral",
            neutral_selected=True,
            margin_over_neutral=0.0,
            activation_threshold=0.1,
        )


def test_neutral_dominance_decision_requires_bool_neutral_selected() -> None:
    from cortex.sre.policy import NeutralDominanceDecision

    decision = NeutralDominanceDecision(
        selected_family=SoftControlFamily.NEUTRAL,
        neutral_selected=True,
        margin_over_neutral=0.0,
        activation_threshold=0.1,
    )

    assert decision.neutral_selected is True

    with pytest.raises(
        TypeError,
        match="NeutralDominanceDecision.neutral_selected must be bool",
    ):
        NeutralDominanceDecision(
            selected_family=SoftControlFamily.NEUTRAL,
            neutral_selected="yes",
            margin_over_neutral=0.0,
            activation_threshold=0.1,
        )


def test_neutral_dominance_decision_requires_numeric_margin() -> None:
    from cortex.sre.policy import NeutralDominanceDecision

    decision = NeutralDominanceDecision(
        selected_family=SoftControlFamily.NEUTRAL,
        neutral_selected=True,
        margin_over_neutral=0.0,
        activation_threshold=0.1,
    )

    assert decision.margin_over_neutral == 0.0

    with pytest.raises(
        TypeError,
        match="NeutralDominanceDecision.margin_over_neutral must be numeric",
    ):
        NeutralDominanceDecision(
            selected_family=SoftControlFamily.NEUTRAL,
            neutral_selected=True,
            margin_over_neutral="0.0",
            activation_threshold=0.1,
        )


def test_neutral_dominance_decision_requires_numeric_activation_threshold() -> None:
    from cortex.sre.policy import NeutralDominanceDecision

    decision = NeutralDominanceDecision(
        selected_family=SoftControlFamily.NEUTRAL,
        neutral_selected=True,
        margin_over_neutral=0.0,
        activation_threshold=0.1,
    )

    assert decision.activation_threshold == 0.1

    with pytest.raises(
        TypeError,
        match="NeutralDominanceDecision.activation_threshold must be numeric",
    ):
        NeutralDominanceDecision(
            selected_family=SoftControlFamily.NEUTRAL,
            neutral_selected=True,
            margin_over_neutral=0.0,
            activation_threshold="0.1",
        )


def test_neutral_dominance_requires_typed_scorecard() -> None:
    with pytest.raises(
        TypeError,
        match="neutral_dominance_decision.scorecard must be AllocationScorecard",
    ):
        neutral_dominance_decision("not-scorecard")


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


def test_neutral_dominance_ranks_by_allocated_score_not_raw_online_score() -> None:
    decision = neutral_dominance_decision(
        AllocationScorecard(
            scores=(
                AllocationScore(
                    SoftControlFamily.NEUTRAL,
                    1.0,
                    online_score=1.0,
                    allocated_score=1.0,
                ),
                AllocationScore(
                    SoftControlFamily.CHECK,
                    1.05,
                    online_score=1.4,
                    allocated_score=1.05,
                ),
                AllocationScore(
                    SoftControlFamily.REDIRECT,
                    1.08,
                    online_score=1.2,
                    allocated_score=1.08,
                ),
            ),
            activation_threshold=0.05,
            alpha_t=0.75,
        )
    )

    assert decision.selected_family is SoftControlFamily.REDIRECT
    assert decision.neutral_selected is False
    assert abs(decision.margin_over_neutral - 0.08) < 1e-12


def test_neutral_dominance_uses_allocated_margin_for_threshold() -> None:
    decision = neutral_dominance_decision(
        AllocationScorecard(
            scores=(
                AllocationScore(
                    SoftControlFamily.NEUTRAL,
                    1.0,
                    online_score=1.0,
                    allocated_score=1.0,
                ),
                AllocationScore(
                    SoftControlFamily.CHECK,
                    1.04,
                    online_score=1.4,
                    allocated_score=1.04,
                ),
            ),
            activation_threshold=0.05,
            alpha_t=0.75,
        )
    )

    assert decision.selected_family is SoftControlFamily.NEUTRAL
    assert decision.neutral_selected is True
    assert abs(decision.margin_over_neutral - 0.04) < 1e-12


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
