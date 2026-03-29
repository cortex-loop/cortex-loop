"""Focused unit tests for reference-only scoring and family selection."""

from __future__ import annotations

import pytest

from cortex.sre.brake import BrakeState
from cortex.sre.families import SoftControlFamily
from cortex.sre.reference_scoring import (
    build_reference_allocation_scorecard,
    build_reference_online_score_components,
    compute_reference_alpha_t,
    select_reference_soft_control,
)
from cortex.sre.state import (
    ReferenceBrakeView,
    ReferenceControlAllocationView,
    ReferenceExecutiveState,
    ReferenceGoalContinuityView,
    ReferenceModeAndGatingView,
    ReferenceUncertaintyMonitoringView,
)


def test_reference_scoring_defaults_to_neutral_when_margin_is_below_threshold() -> None:
    selection = select_reference_soft_control(
        _state(
            mode_tag="pass_through",
            family_mask=frozenset(
                {
                    SoftControlFamily.NEUTRAL,
                    SoftControlFamily.CHECK,
                }
            ),
            budget_band="low",
            top_family_set=frozenset({SoftControlFamily.NEUTRAL}),
            brake_state=BrakeState.QUIESCENT,
        )
    )

    assert selection.selected_family is SoftControlFamily.NEUTRAL
    assert selection.neutral_dominance.neutral_selected is True


def test_reference_scoring_promotes_brake_when_guarded_pressure_is_present() -> None:
    selection = select_reference_soft_control(
        _state(
            mode_tag="guarded_review",
            family_mask=frozenset(
                {
                    SoftControlFamily.NEUTRAL,
                    SoftControlFamily.CHECK,
                    SoftControlFamily.BRAKE,
                }
            ),
            budget_band="medium",
            top_family_set=frozenset(
                {
                    SoftControlFamily.NEUTRAL,
                    SoftControlFamily.BRAKE,
                }
            ),
            host_friction_tags=frozenset({"single-process-limit"}),
            brake_state=BrakeState.GUARDED,
        )
    )

    assert selection.selected_family is SoftControlFamily.BRAKE
    assert selection.neutral_dominance.neutral_selected is False


def test_reference_scoring_promotes_branch_under_branch_pressure() -> None:
    selection = select_reference_soft_control(
        _state(
            mode_tag="pass_through",
            family_mask=frozenset(
                {
                    SoftControlFamily.NEUTRAL,
                    SoftControlFamily.CHECK,
                    SoftControlFamily.BRANCH,
                }
            ),
            budget_band="medium",
            top_family_set=frozenset(
                {
                    SoftControlFamily.NEUTRAL,
                    SoftControlFamily.BRANCH,
                }
            ),
            brake_state=BrakeState.QUIESCENT,
            active_track_ref="review-track",
            resume_anchor_available=True,
        )
    )

    assert selection.selected_family is SoftControlFamily.BRANCH
    assert selection.neutral_dominance.neutral_selected is False


def test_reference_scoring_keeps_masked_family_inadmissible_even_when_top_ranked() -> None:
    state = _state(
        mode_tag="pass_through",
        family_mask=frozenset(
            {
                SoftControlFamily.NEUTRAL,
                SoftControlFamily.CHECK,
            }
        ),
        budget_band="medium",
        top_family_set=frozenset(
            {
                SoftControlFamily.NEUTRAL,
                SoftControlFamily.BRANCH,
            }
        ),
        brake_state=BrakeState.QUIESCENT,
        active_track_ref="review-track",
        resume_anchor_available=True,
    )

    scorecard = build_reference_allocation_scorecard(state)
    selection = select_reference_soft_control(state)

    branch_score = next(
        score for score in scorecard.scores if score.family is SoftControlFamily.BRANCH
    )
    assert branch_score.admissible is False
    assert selection.selected_family is SoftControlFamily.NEUTRAL


def test_reference_scoring_keeps_brake_selected_under_latched_pressure() -> None:
    selection = select_reference_soft_control(
        _state(
            mode_tag="latched_review",
            family_mask=frozenset(
                {
                    SoftControlFamily.NEUTRAL,
                    SoftControlFamily.CHECK,
                    SoftControlFamily.BRAKE,
                    SoftControlFamily.BRANCH,
                }
            ),
            budget_band="high",
            top_family_set=frozenset(
                {
                    SoftControlFamily.NEUTRAL,
                    SoftControlFamily.BRAKE,
                    SoftControlFamily.BRANCH,
                }
            ),
            brake_state=BrakeState.LATCHED,
            active_track_ref="review-track",
            resume_anchor_available=True,
        )
    )

    assert selection.selected_family is SoftControlFamily.BRAKE
    assert selection.neutral_dominance.neutral_selected is False


def test_reference_scoring_exposes_explicit_online_allocation_diagnostics() -> None:
    state = _state(
        mode_tag="review_pending",
        family_mask=frozenset(
            {
                SoftControlFamily.NEUTRAL,
                SoftControlFamily.CHECK,
                SoftControlFamily.BRAKE,
            }
        ),
        budget_band="medium",
        top_family_set=frozenset({SoftControlFamily.NEUTRAL, SoftControlFamily.CHECK}),
        brake_state=BrakeState.GUARDED,
        host_friction_tags=frozenset({"single-process-limit"}),
    )

    components = build_reference_online_score_components(state)
    scorecard = build_reference_allocation_scorecard(state)

    assert scorecard.alpha_t == 0.75
    assert all(score.memory_score == 0.0 for score in scorecard.scores)
    assert all(score.allocated_score == pytest.approx(score.online_score * 0.75) for score in scorecard.scores)
    assert components[SoftControlFamily.CHECK]["uncertainty_reduction"] > 0.0
    assert components[SoftControlFamily.BRAKE]["stability"] > 0.0
    assert all("allocation:online-only" in score.reason_tags for score in scorecard.scores)
    assert all("alpha:0.75" in score.reason_tags for score in scorecard.scores)


def test_reference_alpha_t_changes_with_visible_pressure_only() -> None:
    calm = _state(
        mode_tag="pass_through",
        family_mask=frozenset({SoftControlFamily.NEUTRAL, SoftControlFamily.CHECK}),
        budget_band="medium",
        top_family_set=frozenset({SoftControlFamily.NEUTRAL}),
        brake_state=BrakeState.QUIESCENT,
    )
    pressured = _state(
        mode_tag="pass_through",
        family_mask=frozenset({SoftControlFamily.NEUTRAL, SoftControlFamily.CHECK}),
        budget_band="medium",
        top_family_set=frozenset({SoftControlFamily.NEUTRAL}),
        brake_state=BrakeState.GUARDED,
        host_friction_tags=frozenset({"single-process-limit"}),
    )

    assert compute_reference_alpha_t(calm) == 1.0
    assert compute_reference_alpha_t(pressured) == 0.75


def test_reference_scoring_selection_can_change_under_allocated_score_semantics() -> None:
    unpressured = _state(
        mode_tag="review_pending",
        family_mask=frozenset({SoftControlFamily.NEUTRAL, SoftControlFamily.CHECK}),
        budget_band="high",
        top_family_set=frozenset({SoftControlFamily.NEUTRAL, SoftControlFamily.CHECK}),
        brake_state=BrakeState.QUIESCENT,
    )
    pressured = _state(
        mode_tag="review_pending",
        family_mask=frozenset(
            {
                SoftControlFamily.NEUTRAL,
                SoftControlFamily.CHECK,
                SoftControlFamily.BRAKE,
            }
        ),
        budget_band="medium",
        top_family_set=frozenset({SoftControlFamily.NEUTRAL, SoftControlFamily.CHECK}),
        brake_state=BrakeState.GUARDED,
        host_friction_tags=frozenset({"single-process-limit"}),
    )

    assert build_reference_allocation_scorecard(unpressured).alpha_t == 1.0
    assert select_reference_soft_control(unpressured).selected_family is SoftControlFamily.CHECK
    assert build_reference_allocation_scorecard(pressured).alpha_t == 0.75
    assert select_reference_soft_control(pressured).selected_family is SoftControlFamily.NEUTRAL


def _state(
    *,
    mode_tag: str,
    family_mask: frozenset[SoftControlFamily],
    budget_band: str,
    top_family_set: frozenset[SoftControlFamily],
    brake_state: BrakeState,
    host_friction_tags: frozenset[str] = frozenset(),
    active_track_ref: str = "main",
    resume_anchor_available: bool = False,
) -> ReferenceExecutiveState:
    return ReferenceExecutiveState(
        goal_continuity=ReferenceGoalContinuityView(
            active_track_ref=active_track_ref,
            resume_anchor_available=resume_anchor_available,
        ),
        uncertainty_monitoring=ReferenceUncertaintyMonitoringView(),
        mode_and_gating=ReferenceModeAndGatingView(
            mode_tag=mode_tag,
            family_mask=family_mask,
        ),
        control_allocation=ReferenceControlAllocationView(
            budget_band=budget_band,
            top_family_set=top_family_set,
            host_friction_tags=host_friction_tags,
        ),
        brake=ReferenceBrakeView(brake_state=brake_state),
    )
