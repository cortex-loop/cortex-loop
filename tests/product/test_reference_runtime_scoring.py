"""Focused unit tests for reference-only scoring and family selection."""

from __future__ import annotations

import pytest

from cortex.sre.brake import BrakeState
from cortex.sre.families import SoftControlFamily
from cortex.sre.mediation import ReferenceMediationMode
from cortex.sre.memory_priors import (
    SupportMemoryPriorAppendix,
    SupportMemoryPriorScore,
)
from cortex.sre.opportunities import HostNativeOpportunity
from cortex.sre.reference_scoring import (
    build_reference_allocation_scorecard,
    build_reference_online_score_components,
    compute_reference_activation_threshold,
    compute_reference_alpha_t,
    compute_reference_chi_t,
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


def test_reference_scoring_selects_seek_context_under_missing_capability_pressure_when_admitted() -> None:
    state = _state(
        mode_tag="guarded_review",
        family_mask=frozenset(
            {
                SoftControlFamily.NEUTRAL,
                SoftControlFamily.CHECK,
                SoftControlFamily.BRAKE,
                SoftControlFamily.SEEK_CONTEXT,
            }
        ),
        budget_band="low",
        top_family_set=frozenset(
            {
                SoftControlFamily.NEUTRAL,
                SoftControlFamily.BRAKE,
                SoftControlFamily.SEEK_CONTEXT,
            }
        ),
        brake_state=BrakeState.GUARDED,
        host_friction_tags=frozenset(
            {
                "missing-capability",
                "capability-view-missing",
            }
        ),
    )

    scorecard = build_reference_allocation_scorecard(state)
    selection = select_reference_soft_control(state)
    neutral_score = next(
        score for score in scorecard.scores if score.family is SoftControlFamily.NEUTRAL
    )
    brake_score = next(
        score for score in scorecard.scores if score.family is SoftControlFamily.BRAKE
    )
    seek_context_score = next(
        score
        for score in scorecard.scores
        if score.family is SoftControlFamily.SEEK_CONTEXT
    )

    assert seek_context_score.admissible is True
    assert seek_context_score.allocated_score > neutral_score.allocated_score
    assert seek_context_score.allocated_score > brake_score.allocated_score
    assert selection.neutral_dominance.margin_over_neutral == pytest.approx(
        seek_context_score.allocated_score - neutral_score.allocated_score
    )
    assert "seek-context-pressure" in seek_context_score.reason_tags
    assert (
        selection.neutral_dominance.margin_over_neutral
        > selection.neutral_dominance.activation_threshold
    )
    assert selection.neutral_dominance.activation_threshold == pytest.approx(0.45)
    assert selection.selected_family is SoftControlFamily.SEEK_CONTEXT
    assert selection.neutral_dominance.neutral_selected is False


def test_reference_scoring_keeps_seek_context_neutral_dominated_under_generic_host_friction_even_if_admitted() -> None:
    state = _state(
        mode_tag="guarded_review",
        family_mask=frozenset(
            {
                SoftControlFamily.NEUTRAL,
                SoftControlFamily.CHECK,
                SoftControlFamily.BRAKE,
                SoftControlFamily.SEEK_CONTEXT,
            }
        ),
        budget_band="low",
        top_family_set=frozenset(
            {
                SoftControlFamily.NEUTRAL,
                SoftControlFamily.BRAKE,
                SoftControlFamily.SEEK_CONTEXT,
            }
        ),
        brake_state=BrakeState.GUARDED,
        host_friction_tags=frozenset({"single-process-limit"}),
    )

    scorecard = build_reference_allocation_scorecard(state)
    selection = select_reference_soft_control(state)
    seek_context_score = next(
        score
        for score in scorecard.scores
        if score.family is SoftControlFamily.SEEK_CONTEXT
    )

    assert seek_context_score.admissible is True
    assert "seek-context-pressure" not in seek_context_score.reason_tags
    assert selection.selected_family is SoftControlFamily.NEUTRAL
    assert selection.neutral_dominance.neutral_selected is True


def test_reference_scoring_identity_mode_preserves_seek_context_without_direct_specialization() -> None:
    selection = select_reference_soft_control(
        _state(
            mode_tag="guarded_review",
            family_mask=frozenset(
                {
                    SoftControlFamily.NEUTRAL,
                    SoftControlFamily.CHECK,
                    SoftControlFamily.BRAKE,
                    SoftControlFamily.SEEK_CONTEXT,
                }
            ),
            budget_band="low",
            top_family_set=frozenset(
                {
                    SoftControlFamily.NEUTRAL,
                    SoftControlFamily.BRAKE,
                    SoftControlFamily.SEEK_CONTEXT,
                }
            ),
            brake_state=BrakeState.GUARDED,
            host_friction_tags=frozenset({"missing-capability", "capability-view-missing"}),
        ),
        opportunities=(
            HostNativeOpportunity(
                opportunity_ref="mcp.query",
                supported_families=frozenset({SoftControlFamily.SEEK_CONTEXT}),
                clearly_superior=True,
                native_surface_tags=frozenset({"mcp", "structured-query"}),
            ),
        ),
    )

    assert selection.selected_family_before_finalization is SoftControlFamily.SEEK_CONTEXT
    assert selection.selected_family is SoftControlFamily.SEEK_CONTEXT
    assert selection.opportunity_specialization.direct_opportunity_specialization_used is False
    assert selection.mediation_finalization.as_payload()["mediation_active"] is False


def test_reference_scoring_experimental_mode_specializes_only_seek_context() -> None:
    selection = select_reference_soft_control(
        _state(
            mode_tag="guarded_review",
            family_mask=frozenset(
                {
                    SoftControlFamily.NEUTRAL,
                    SoftControlFamily.CHECK,
                    SoftControlFamily.BRAKE,
                    SoftControlFamily.SEEK_CONTEXT,
                }
            ),
            budget_band="low",
            top_family_set=frozenset(
                {
                    SoftControlFamily.NEUTRAL,
                    SoftControlFamily.BRAKE,
                    SoftControlFamily.SEEK_CONTEXT,
                }
            ),
            brake_state=BrakeState.GUARDED,
            host_friction_tags=frozenset({"missing-capability", "capability-view-missing"}),
        ),
        mediation_mode=ReferenceMediationMode.HOST_REALIZATION_EXPERIMENTAL,
        opportunities=(
            HostNativeOpportunity(
                opportunity_ref="mcp.query",
                supported_families=frozenset({SoftControlFamily.SEEK_CONTEXT}),
                clearly_superior=True,
                native_surface_tags=frozenset({"mcp", "structured-query"}),
            ),
        ),
    )

    assert selection.selected_family_before_finalization is SoftControlFamily.SEEK_CONTEXT
    assert selection.selected_family is SoftControlFamily.SEEK_CONTEXT
    assert selection.opportunity_specialization.direct_opportunity_specialization_used is True
    assert selection.opportunity_specialization.preferred_opportunity is not None
    assert selection.opportunity_specialization.preferred_opportunity.opportunity_ref == "mcp.query"
    assert selection.mediation_finalization.as_payload()["mediation_active"] is True


def test_reference_scoring_tightens_to_neutral_when_guarded_pressure_is_present() -> None:
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

    assert selection.selected_family is SoftControlFamily.NEUTRAL
    assert selection.neutral_dominance.neutral_selected is True


def test_reference_scoring_promotes_branch_under_branch_pressure() -> None:
    state = _state(
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
    selection = select_reference_soft_control(state)
    scorecard = build_reference_allocation_scorecard(state)
    branch_score = next(
        score for score in scorecard.scores if score.family is SoftControlFamily.BRANCH
    )
    neutral_score = next(
        score for score in scorecard.scores if score.family is SoftControlFamily.NEUTRAL
    )

    assert selection.selected_family is SoftControlFamily.BRANCH
    assert selection.neutral_dominance.neutral_selected is False
    assert branch_score.allocated_score > neutral_score.allocated_score
    assert "allocation:online-plus-goal-branch" in branch_score.reason_tags
    assert "allocation:online-only" not in branch_score.reason_tags
    assert "goal-branch-coupled" in branch_score.reason_tags
    assert "lambda_G:0.35" in branch_score.reason_tags
    assert "allocation:online-plus-goal-branch" in neutral_score.reason_tags
    assert "allocation:online-only" not in neutral_score.reason_tags
    unaffected_score = next(
        score
        for score in scorecard.scores
        if score.family is SoftControlFamily.SEEK_CONTEXT
    )
    assert unaffected_score.allocated_score == unaffected_score.online_score
    assert "allocation:online-only" in unaffected_score.reason_tags
    assert "allocation:online-plus-goal-branch" not in unaffected_score.reason_tags
    assert "goal-branch-coupled" not in unaffected_score.reason_tags
    assert not any(
        tag.startswith("lambda_G:") for tag in unaffected_score.reason_tags
    )


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
    assert all(
        score.allocated_score == pytest.approx(score.online_score * 0.75)
        for score in scorecard.scores
    )
    assert components[SoftControlFamily.CHECK]["uncertainty_reduction"] > 0.0
    assert components[SoftControlFamily.BRAKE]["stability"] > 0.0
    assert all("allocation:online-only" in score.reason_tags for score in scorecard.scores)
    assert all(
        "allocation:online-plus-goal-branch" not in score.reason_tags
        for score in scorecard.scores
    )
    assert all(
        not any(tag.startswith("lambda_G:") for tag in score.reason_tags)
        for score in scorecard.scores
    )
    assert all("alpha:0.75" in score.reason_tags for score in scorecard.scores)


def test_reference_scoring_activates_q_mem_only_when_explicit_support_memory_priors_are_present() -> None:
    state = _state(
        mode_tag="review_pending",
        family_mask=frozenset(
            {
                SoftControlFamily.NEUTRAL,
                SoftControlFamily.CHECK,
                SoftControlFamily.BRANCH,
            }
        ),
        budget_band="medium",
        top_family_set=frozenset({SoftControlFamily.NEUTRAL, SoftControlFamily.BRANCH}),
        brake_state=BrakeState.GUARDED,
        host_friction_tags=frozenset({"single-process-limit"}),
    )

    scorecard = build_reference_allocation_scorecard(
        state,
        memory_priors=_memory_priors(
            branch_score=0.9,
            check_score=0.2,
        ),
    )

    branch_score = next(
        score for score in scorecard.scores if score.family is SoftControlFamily.BRANCH
    )
    check_score = next(
        score for score in scorecard.scores if score.family is SoftControlFamily.CHECK
    )

    assert branch_score.memory_score == pytest.approx(0.9)
    assert branch_score.allocated_score == pytest.approx(
        (0.75 * branch_score.online_score) + (0.25 * 0.9)
    )
    assert "allocation:online-plus-memory" in branch_score.reason_tags
    assert "support-memory:branch" in branch_score.reason_tags
    assert check_score.memory_score == pytest.approx(0.2)


def test_reference_scoring_emits_full_mixed_path_when_memory_and_goal_branch_are_both_active() -> None:
    state = _state(
        mode_tag="review_pending",
        family_mask=frozenset(
            {
                SoftControlFamily.NEUTRAL,
                SoftControlFamily.CHECK,
                SoftControlFamily.BRANCH,
            }
        ),
        budget_band="medium",
        top_family_set=frozenset({SoftControlFamily.NEUTRAL, SoftControlFamily.BRANCH}),
        brake_state=BrakeState.GUARDED,
        host_friction_tags=frozenset({"single-process-limit"}),
        active_track_ref="review-track",
        resume_anchor_available=True,
    )

    scorecard = build_reference_allocation_scorecard(
        state,
        memory_priors=_memory_priors(branch_score=0.6),
    )
    branch_score = next(
        score for score in scorecard.scores if score.family is SoftControlFamily.BRANCH
    )

    assert branch_score.memory_score == pytest.approx(0.6)
    assert "allocation:full-mixed" in branch_score.reason_tags
    assert "allocation:online-plus-memory" not in branch_score.reason_tags
    assert "allocation:online-plus-goal-branch" not in branch_score.reason_tags
    assert "goal-branch-coupled" in branch_score.reason_tags
    assert any(tag.startswith("lambda_G:") for tag in branch_score.reason_tags)


def test_reference_selection_exposes_bounded_chi_t_and_lowers_it_under_guarded_pressure() -> None:
    calm = _state(
        mode_tag="guarded_review",
        family_mask=frozenset(
            {
                SoftControlFamily.NEUTRAL,
                SoftControlFamily.CHECK,
                SoftControlFamily.BRAKE,
                SoftControlFamily.SEEK_CONTEXT,
            }
        ),
        budget_band="low",
        top_family_set=frozenset(
            {
                SoftControlFamily.NEUTRAL,
                SoftControlFamily.BRAKE,
                SoftControlFamily.SEEK_CONTEXT,
            }
        ),
        brake_state=BrakeState.QUIESCENT,
        host_friction_tags=frozenset({"missing-capability", "capability-view-missing"}),
    )
    guarded = _state(
        mode_tag="guarded_review",
        family_mask=frozenset(
            {
                SoftControlFamily.NEUTRAL,
                SoftControlFamily.CHECK,
                SoftControlFamily.BRAKE,
                SoftControlFamily.SEEK_CONTEXT,
            }
        ),
        budget_band="medium",
        top_family_set=frozenset(
            {
                SoftControlFamily.NEUTRAL,
                SoftControlFamily.BRAKE,
                SoftControlFamily.SEEK_CONTEXT,
            }
        ),
        brake_state=BrakeState.GUARDED,
        host_friction_tags=frozenset({"missing-capability", "capability-view-missing"}),
    )

    calm_selection = select_reference_soft_control(calm)
    guarded_selection = select_reference_soft_control(guarded)

    assert 0.0 <= calm_selection.chi_t <= 1.0
    assert 0.0 <= guarded_selection.chi_t <= 1.0
    assert guarded_selection.chi_t < calm_selection.chi_t
    assert compute_reference_chi_t(
        guarded,
        neutral_dominance=guarded_selection.neutral_dominance,
    ) == pytest.approx(guarded_selection.chi_t)


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


def test_reference_activation_threshold_uses_feedback_pressure_without_touching_alpha() -> None:
    guarded = _state(
        mode_tag="review_pending",
        family_mask=frozenset(
            {
                SoftControlFamily.NEUTRAL,
                SoftControlFamily.CHECK,
                SoftControlFamily.BRAKE,
            }
        ),
        budget_band="high",
        top_family_set=frozenset({SoftControlFamily.NEUTRAL, SoftControlFamily.CHECK}),
        brake_state=BrakeState.GUARDED,
    )
    feedback_pressured = _state(
        mode_tag="review_pending",
        family_mask=frozenset(
            {
                SoftControlFamily.NEUTRAL,
                SoftControlFamily.CHECK,
                SoftControlFamily.BRAKE,
            }
        ),
        budget_band="high",
        top_family_set=frozenset({SoftControlFamily.NEUTRAL, SoftControlFamily.CHECK}),
        brake_state=BrakeState.GUARDED,
        feedback_pressure_tags=frozenset({"feedback:override-pressure"}),
    )

    assert compute_reference_alpha_t(guarded) == 1.0
    assert compute_reference_activation_threshold(guarded) == pytest.approx(0.25)
    assert select_reference_soft_control(guarded).selected_family is SoftControlFamily.CHECK

    assert compute_reference_alpha_t(feedback_pressured) == 1.0
    assert compute_reference_activation_threshold(feedback_pressured) == pytest.approx(0.30)
    assert select_reference_soft_control(feedback_pressured).selected_family is SoftControlFamily.CHECK


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
    feedback_pressure_tags: frozenset[str] = frozenset(),
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
            feedback_pressure_tags=feedback_pressure_tags,
        ),
        brake=ReferenceBrakeView(brake_state=brake_state),
    )


def _memory_priors(
    *,
    branch_score: float = 0.0,
    check_score: float = 0.0,
) -> SupportMemoryPriorAppendix:
    return SupportMemoryPriorAppendix(
        scores=tuple(
            score
            for score in (
                SupportMemoryPriorScore(
                    family=SoftControlFamily.BRANCH,
                    score=branch_score,
                    reason_tags=frozenset({"q_mem:active", "support-memory:branch"}),
                )
                if branch_score > 0.0
                else None,
                SupportMemoryPriorScore(
                    family=SoftControlFamily.CHECK,
                    score=check_score,
                    reason_tags=frozenset({"q_mem:active", "support-memory:verification"}),
                )
                if check_score > 0.0
                else None,
            )
            if score is not None
        ),
        appendix_tags=frozenset({"q_mem:explicit-aux"}),
        notes=("explicit AUX support-memory priors",),
    )
