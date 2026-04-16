"""Focused unit tests for reference-only scoring and family selection."""

from __future__ import annotations

import pytest

from cortex.aux.distillation import _distill_offline_support_publication_from_snapshots
from cortex.aux.publication import augment_snapshot_with_offline_publication
from cortex.aux.support_priors import build_support_memory_prior_appendix
from cortex.sre.brake import BrakeState, BrakeTonic
from cortex.sre.families import SoftControlFamily
from cortex.sre.mediation import ReferenceMediationMode
from cortex.sre.memory_priors import (
    SupportMemoryPriorAppendix,
    SupportMemoryPriorScore,
)
from cortex.sre.opportunities import HostNativeOpportunity
from cortex.sre.operator_routing import OperatorTaskMode
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
    RiskWeight,
)
from cortex.sre.uncertainty import UncertaintyEstimate
from tests.experimental._aux_test_support import make_aux_reference_replay_corpus, make_aux_temporal_corpus


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
    assert seek_context_score.activation_threshold == pytest.approx(0.37)
    assert (
        selection.neutral_dominance.margin_over_neutral
        > selection.neutral_dominance.activation_threshold
    )
    assert selection.neutral_dominance.activation_threshold == pytest.approx(0.37)
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


def test_reference_scoring_applies_anti_thrash_tax_only_to_repeated_family() -> None:
    taxed = _state(
        mode_tag="guarded_review",
        family_mask=frozenset(
            {
                SoftControlFamily.NEUTRAL,
                SoftControlFamily.CHECK,
                SoftControlFamily.SEEK_CONTEXT,
            }
        ),
        budget_band="low",
        top_family_set=frozenset(
            {
                SoftControlFamily.NEUTRAL,
                SoftControlFamily.CHECK,
                SoftControlFamily.SEEK_CONTEXT,
            }
        ),
        brake_state=BrakeState.GUARDED,
        anti_thrash_state="taxed",
        repetition_tax=0.16,
        repetition_target_family=SoftControlFamily.CHECK,
        anti_thrash_reason_tags=frozenset({"same-context-repeat"}),
        task_mode=OperatorTaskMode.INSPECT,
        host_friction_tags=frozenset({"capability-view-missing"}),
    )
    untaxed = _state(
        mode_tag="guarded_review",
        family_mask=taxed.mode_and_gating.family_mask,
        budget_band="low",
        top_family_set=taxed.control_allocation.top_family_set,
        brake_state=BrakeState.GUARDED,
        task_mode=OperatorTaskMode.INSPECT,
        host_friction_tags=frozenset({"capability-view-missing"}),
    )

    taxed_components = build_reference_online_score_components(taxed)
    untaxed_components = build_reference_online_score_components(untaxed)
    taxed_scorecard = build_reference_allocation_scorecard(taxed)

    assert taxed_components[SoftControlFamily.CHECK]["control_burden"] == pytest.approx(
        untaxed_components[SoftControlFamily.CHECK]["control_burden"] + 0.16
    )
    assert taxed_components[SoftControlFamily.SEEK_CONTEXT]["control_burden"] == pytest.approx(
        untaxed_components[SoftControlFamily.SEEK_CONTEXT]["control_burden"]
    )
    check_score = next(
        score for score in taxed_scorecard.scores if score.family is SoftControlFamily.CHECK
    )
    seek_context_score = next(
        score
        for score in taxed_scorecard.scores
        if score.family is SoftControlFamily.SEEK_CONTEXT
    )
    assert "anti-thrash:taxed" in check_score.reason_tags
    assert "anti-thrash:taxed" not in seek_context_score.reason_tags


def test_reference_scoring_reopened_state_clears_tax_and_preserves_stronger_verification_path() -> None:
    reopened = _state(
        mode_tag="guarded_review",
        family_mask=frozenset(
            {
                SoftControlFamily.NEUTRAL,
                SoftControlFamily.CHECK,
                SoftControlFamily.SEEK_CONTEXT,
            }
        ),
        budget_band="low",
        top_family_set=frozenset(
            {
                SoftControlFamily.NEUTRAL,
                SoftControlFamily.CHECK,
                SoftControlFamily.SEEK_CONTEXT,
            }
        ),
        brake_state=BrakeState.GUARDED,
        anti_thrash_state="reopened",
        repetition_target_family=SoftControlFamily.CHECK,
        anti_thrash_reason_tags=frozenset({"reopened:posture-shift"}),
        task_mode=OperatorTaskMode.EXECUTE,
        host_friction_tags=frozenset({"capability-view-missing"}),
    )

    components = build_reference_online_score_components(reopened)
    selection = select_reference_soft_control(reopened)
    check_score = next(
        score
        for score in build_reference_allocation_scorecard(reopened).scores
        if score.family is SoftControlFamily.CHECK
    )

    assert components[SoftControlFamily.CHECK]["control_burden"] >= 0.0
    assert "anti-thrash:reopened" in check_score.reason_tags
    assert selection.selected_family is SoftControlFamily.SEEK_CONTEXT


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
        open_branch_count=1,
        resume_anchor_quality=0.85,
        merge_confidence=0.70,
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
    assert "merge-confidence" in branch_score.reason_tags
    assert any(tag.startswith("lambda_G:") for tag in branch_score.reason_tags)
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


def test_reference_scoring_uses_family_sensitive_thresholds_for_probe_relief_vs_branching() -> None:
    state = _state(
        mode_tag="guarded_review",
        family_mask=frozenset(
            {
                SoftControlFamily.NEUTRAL,
                SoftControlFamily.CHECK,
                SoftControlFamily.SEEK_CONTEXT,
                SoftControlFamily.BRANCH,
                SoftControlFamily.ESCALATE,
            }
        ),
        budget_band="low",
        top_family_set=frozenset(
            {
                SoftControlFamily.NEUTRAL,
                SoftControlFamily.SEEK_CONTEXT,
            }
        ),
        brake_state=BrakeState.GUARDED,
        host_friction_tags=frozenset({"missing-capability", "capability-view-missing"}),
    )
    evidence_relief_state = _state(
        mode_tag="review_pending",
        family_mask=frozenset(
            {
                SoftControlFamily.NEUTRAL,
                SoftControlFamily.CHECK,
                SoftControlFamily.BRANCH,
            }
        ),
        budget_band="high",
        top_family_set=frozenset(
            {
                SoftControlFamily.NEUTRAL,
                SoftControlFamily.CHECK,
            }
        ),
        brake_state=BrakeState.GUARDED,
        uncertainty_levels=(("evidence", 0.75),),
    )

    assert compute_reference_activation_threshold(state) == pytest.approx(0.45)
    assert compute_reference_activation_threshold(
        state,
        family=SoftControlFamily.CHECK,
    ) == pytest.approx(0.45)
    assert compute_reference_activation_threshold(
        state,
        family=SoftControlFamily.SEEK_CONTEXT,
    ) == pytest.approx(0.37)
    assert compute_reference_activation_threshold(
        state,
        family=SoftControlFamily.BRANCH,
    ) == pytest.approx(0.53)
    assert compute_reference_activation_threshold(
        state,
        family=SoftControlFamily.ESCALATE,
    ) == pytest.approx(0.55)
    assert compute_reference_activation_threshold(
        evidence_relief_state,
        family=SoftControlFamily.CHECK,
    ) == pytest.approx(0.20)


def test_reference_scoring_balanced_risk_weight_produces_zero_threshold_shift() -> None:
    # SRE_2 §6.6.1 backward-compat lock: balanced RiskWeight must leave CHECK/SEEK_CONTEXT
    # thresholds identical to the pre-train baseline.
    family_mask = frozenset(
        {
            SoftControlFamily.NEUTRAL,
            SoftControlFamily.CHECK,
            SoftControlFamily.SEEK_CONTEXT,
        }
    )
    baseline = _state(
        mode_tag="review_pending",
        family_mask=family_mask,
        budget_band="medium",
        top_family_set=frozenset({SoftControlFamily.NEUTRAL, SoftControlFamily.CHECK}),
        brake_state=BrakeState.QUIESCENT,
        uncertainty_levels=(("evidence", 0.55),),
    )
    balanced = _state(
        mode_tag="review_pending",
        family_mask=family_mask,
        budget_band="medium",
        top_family_set=frozenset({SoftControlFamily.NEUTRAL, SoftControlFamily.CHECK}),
        brake_state=BrakeState.QUIESCENT,
        uncertainty_levels=(("evidence", 0.55),),
        risk_weight=RiskWeight(
            fn_cost_weight=0.40,
            fp_cost_weight=0.40,
            adjustment_sign="balanced",
        ),
    )
    for family in (SoftControlFamily.CHECK, SoftControlFamily.SEEK_CONTEXT):
        assert compute_reference_activation_threshold(
            balanced, family=family
        ) == pytest.approx(
            compute_reference_activation_threshold(baseline, family=family)
        )


def test_reference_scoring_fn_heavy_risk_weight_lowers_check_and_seek_context_thresholds() -> None:
    # SRE_2 §6.6.1: missing real uncertainty is expensive → cheaper to verify.
    family_mask = frozenset(
        {
            SoftControlFamily.NEUTRAL,
            SoftControlFamily.CHECK,
            SoftControlFamily.SEEK_CONTEXT,
            SoftControlFamily.BRANCH,
        }
    )
    baseline = _state(
        mode_tag="review_pending",
        family_mask=family_mask,
        budget_band="medium",
        top_family_set=frozenset({SoftControlFamily.NEUTRAL, SoftControlFamily.CHECK}),
        brake_state=BrakeState.QUIESCENT,
        uncertainty_levels=(("evidence", 0.70),),
    )
    fn_heavy = _state(
        mode_tag="review_pending",
        family_mask=family_mask,
        budget_band="medium",
        top_family_set=frozenset({SoftControlFamily.NEUTRAL, SoftControlFamily.CHECK}),
        brake_state=BrakeState.QUIESCENT,
        uncertainty_levels=(("evidence", 0.70),),
        risk_weight=RiskWeight(
            fn_cost_weight=0.80,
            fp_cost_weight=0.10,
            adjustment_sign="fn-heavy",
            dominant_risk_source="evidence-contradiction-spike",
        ),
    )
    for family in (SoftControlFamily.CHECK, SoftControlFamily.SEEK_CONTEXT):
        assert compute_reference_activation_threshold(
            fn_heavy, family=family
        ) < compute_reference_activation_threshold(baseline, family=family)
    # Non-verification families must not shift under fn-heavy.
    assert compute_reference_activation_threshold(
        fn_heavy, family=SoftControlFamily.BRANCH
    ) == pytest.approx(
        compute_reference_activation_threshold(baseline, family=SoftControlFamily.BRANCH)
    )


def test_reference_scoring_fp_heavy_risk_weight_raises_check_and_seek_context_thresholds() -> None:
    # SRE_2 §6.6.1: overchecking a productive flow is expensive → stay compact.
    family_mask = frozenset(
        {
            SoftControlFamily.NEUTRAL,
            SoftControlFamily.CHECK,
            SoftControlFamily.SEEK_CONTEXT,
            SoftControlFamily.BRANCH,
        }
    )
    baseline = _state(
        mode_tag="review_pending",
        family_mask=family_mask,
        budget_band="medium",
        top_family_set=frozenset({SoftControlFamily.NEUTRAL, SoftControlFamily.CHECK}),
        brake_state=BrakeState.QUIESCENT,
        uncertainty_levels=(("evidence", 0.20),),
    )
    fp_heavy = _state(
        mode_tag="review_pending",
        family_mask=family_mask,
        budget_band="medium",
        top_family_set=frozenset({SoftControlFamily.NEUTRAL, SoftControlFamily.CHECK}),
        brake_state=BrakeState.QUIESCENT,
        uncertainty_levels=(("evidence", 0.20),),
        risk_weight=RiskWeight(
            fn_cost_weight=0.10,
            fp_cost_weight=0.70,
            adjustment_sign="fp-heavy",
            dominant_risk_source="productive-flow",
        ),
    )
    for family in (SoftControlFamily.CHECK, SoftControlFamily.SEEK_CONTEXT):
        assert compute_reference_activation_threshold(
            fp_heavy, family=family
        ) > compute_reference_activation_threshold(baseline, family=family)
    assert compute_reference_activation_threshold(
        fp_heavy, family=SoftControlFamily.BRANCH
    ) == pytest.approx(
        compute_reference_activation_threshold(baseline, family=SoftControlFamily.BRANCH)
    )


def test_reference_scoring_risk_weight_shift_stays_within_bounded_range() -> None:
    # SRE_2 §6.6.1: shift is bounded by the (fp - fn) * 0.10 cap and the 0.05..0.60 clip.
    family_mask = frozenset(
        {
            SoftControlFamily.NEUTRAL,
            SoftControlFamily.CHECK,
            SoftControlFamily.SEEK_CONTEXT,
        }
    )
    maximum_fn_heavy = _state(
        mode_tag="review_pending",
        family_mask=family_mask,
        budget_band="medium",
        top_family_set=frozenset({SoftControlFamily.NEUTRAL, SoftControlFamily.CHECK}),
        brake_state=BrakeState.QUIESCENT,
        uncertainty_levels=(("evidence", 0.50),),
        risk_weight=RiskWeight(
            fn_cost_weight=1.0,
            fp_cost_weight=0.0,
            adjustment_sign="fn-heavy",
            dominant_risk_source="hard-fn-bound",
        ),
    )
    maximum_fp_heavy = _state(
        mode_tag="review_pending",
        family_mask=family_mask,
        budget_band="medium",
        top_family_set=frozenset({SoftControlFamily.NEUTRAL, SoftControlFamily.CHECK}),
        brake_state=BrakeState.QUIESCENT,
        uncertainty_levels=(("evidence", 0.50),),
        risk_weight=RiskWeight(
            fn_cost_weight=0.0,
            fp_cost_weight=1.0,
            adjustment_sign="fp-heavy",
            dominant_risk_source="hard-fp-bound",
        ),
    )
    for family in (SoftControlFamily.CHECK, SoftControlFamily.SEEK_CONTEXT):
        low = compute_reference_activation_threshold(maximum_fn_heavy, family=family)
        high = compute_reference_activation_threshold(maximum_fp_heavy, family=family)
        assert 0.05 <= low <= high <= 0.60


def test_reference_scoring_rewards_anchored_branch_work_and_penalizes_orphaned_branch_trees() -> None:
    anchored = _state(
        mode_tag="review_pending",
        family_mask=frozenset(
            {
                SoftControlFamily.NEUTRAL,
                SoftControlFamily.BRANCH,
                SoftControlFamily.CHECK,
                SoftControlFamily.REDIRECT,
            }
        ),
        budget_band="low",
        top_family_set=frozenset(
            {
                SoftControlFamily.NEUTRAL,
                SoftControlFamily.BRANCH,
            }
        ),
        brake_state=BrakeState.GUARDED,
        active_track_ref="review-track",
        resume_anchor_available=True,
        open_branch_count=1,
        resume_anchor_quality=0.85,
        merge_confidence=0.70,
    )
    orphaned = _state(
        mode_tag="review_pending",
        family_mask=anchored.mode_and_gating.family_mask,
        budget_band="low",
        top_family_set=anchored.control_allocation.top_family_set,
        brake_state=BrakeState.GUARDED,
        active_track_ref="review-track",
        resume_anchor_available=False,
        open_branch_count=3,
        resume_anchor_quality=0.0,
        merge_confidence=0.0,
    )

    anchored_branch = next(
        score
        for score in build_reference_allocation_scorecard(anchored).scores
        if score.family is SoftControlFamily.BRANCH
    )
    orphaned_branch = next(
        score
        for score in build_reference_allocation_scorecard(orphaned).scores
        if score.family is SoftControlFamily.BRANCH
    )

    assert anchored_branch.allocated_score > orphaned_branch.allocated_score
    assert "merge-confidence" in anchored_branch.reason_tags
    assert "multi-branch-burden" in orphaned_branch.reason_tags
    assert "resume-anchor-missing" in orphaned_branch.reason_tags


def test_reference_scoring_distinguishes_productive_exploration_from_oscillation() -> None:
    baseline = _state(
        mode_tag="review_pending",
        family_mask=frozenset(
            {
                SoftControlFamily.NEUTRAL,
                SoftControlFamily.CHECK,
                SoftControlFamily.SEEK_CONTEXT,
                SoftControlFamily.BRANCH,
                SoftControlFamily.REDIRECT,
            }
        ),
        budget_band="medium",
        top_family_set=frozenset(
            {
                SoftControlFamily.NEUTRAL,
                SoftControlFamily.CHECK,
            }
        ),
        brake_state=BrakeState.GUARDED,
        host_friction_tags=frozenset({"missing-capability", "capability-view-missing"}),
    )
    feedback_shaped = _state(
        mode_tag=baseline.mode_and_gating.mode_tag,
        family_mask=baseline.mode_and_gating.family_mask,
        budget_band=baseline.control_allocation.budget_band,
        top_family_set=baseline.control_allocation.top_family_set,
        brake_state=baseline.brake.brake_state,
        host_friction_tags=baseline.control_allocation.host_friction_tags,
        productive_exploration_bonus=0.08,
        oscillation_penalty=0.12,
    )

    assert compute_reference_activation_threshold(
        feedback_shaped,
        family=SoftControlFamily.CHECK,
    ) < compute_reference_activation_threshold(
        baseline,
        family=SoftControlFamily.CHECK,
    )
    assert compute_reference_activation_threshold(
        feedback_shaped,
        family=SoftControlFamily.BRANCH,
    ) > compute_reference_activation_threshold(
        baseline,
        family=SoftControlFamily.BRANCH,
    )


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
    assert "q_mem-signal:branch" in branch_score.reason_tags
    assert check_score.memory_score == pytest.approx(0.2)


def test_reference_scoring_surfaces_calibrated_q_mem_signal_tags_on_reference_replay_path() -> None:
    branch_scenario = _reference_replay_scenario("branch-resume-recovery")
    contradiction_scenario = _reference_replay_scenario("contradiction-review")
    uncertainty_scenario = _reference_replay_scenario("uncertainty-brake-calibration")

    branch_scorecard = build_reference_allocation_scorecard(
        branch_scenario.executive_state,
        memory_priors=_support_memory_priors_from_temporal_case("branch-resume-recovery"),
    )
    contradiction_scorecard = build_reference_allocation_scorecard(
        contradiction_scenario.executive_state,
        memory_priors=_support_memory_priors_from_temporal_case("contradiction-review"),
    )
    uncertainty_scorecard = build_reference_allocation_scorecard(
        uncertainty_scenario.executive_state,
        memory_priors=_support_memory_priors_from_temporal_case("uncertainty-brake-calibration"),
    )

    branch_score = next(
        score for score in branch_scorecard.scores if score.family is SoftControlFamily.BRANCH
    )
    check_score = next(
        score for score in contradiction_scorecard.scores if score.family is SoftControlFamily.CHECK
    )
    brake_score = next(
        score for score in uncertainty_scorecard.scores if score.family is SoftControlFamily.BRAKE
    )

    assert branch_score.memory_score > 0.0
    assert "q_mem-signal:branch" in branch_score.reason_tags
    assert "q_mem-signal:retrieval" in branch_score.reason_tags
    assert check_score.memory_score > 0.0
    assert "q_mem-signal:contradiction" in check_score.reason_tags
    assert brake_score.memory_score > 0.0
    assert "q_mem-signal:uncertainty" in brake_score.reason_tags


def test_reference_scoring_burden_heavy_publication_does_not_create_false_positive_check_lift() -> None:
    scenario = _reference_replay_scenario("burden-heavy-counterexample")
    memory_priors = _support_memory_priors_from_temporal_case("burden-heavy-counterexample")

    baseline = build_reference_allocation_scorecard(scenario.executive_state)
    replay = build_reference_allocation_scorecard(
        scenario.executive_state,
        memory_priors=memory_priors,
    )
    baseline_check = next(
        score for score in baseline.scores if score.family is SoftControlFamily.CHECK
    )
    replay_check = next(
        score for score in replay.scores if score.family is SoftControlFamily.CHECK
    )

    assert memory_priors.active is False
    assert replay_check.memory_score == 0.0
    assert replay_check.allocated_score == pytest.approx(baseline_check.allocated_score)


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
    task_mode: OperatorTaskMode = OperatorTaskMode.EXECUTE,
    host_friction_tags: frozenset[str] = frozenset(),
    feedback_pressure_tags: frozenset[str] = frozenset(),
    active_track_ref: str = "main",
    resume_anchor_available: bool = False,
    open_branch_count: int = 0,
    resume_anchor_quality: float = 0.0,
    merge_confidence: float = 0.0,
    productive_exploration_bonus: float = 0.0,
    oscillation_penalty: float = 0.0,
    anti_thrash_state: str = "inactive",
    repetition_tax: float = 0.0,
    repetition_target_family: SoftControlFamily | None = None,
    anti_thrash_reason_tags: frozenset[str] = frozenset(),
    uncertainty_levels: tuple[tuple[str, float], ...] = (),
    contradiction_spike_flags: frozenset[str] = frozenset(),
    risk_weight: RiskWeight | None = None,
    brake_tonic: BrakeTonic | None = None,
) -> ReferenceExecutiveState:
    return ReferenceExecutiveState(
        goal_continuity=ReferenceGoalContinuityView(
            active_track_ref=active_track_ref,
            resume_anchor_available=resume_anchor_available,
            open_branch_count=open_branch_count,
            resume_anchor_quality=resume_anchor_quality,
            merge_confidence=merge_confidence,
        ),
        uncertainty_monitoring=ReferenceUncertaintyMonitoringView(
            classwise_uncertainty=tuple(
                UncertaintyEstimate(class_tag=class_tag, level=level)
                for class_tag, level in uncertainty_levels
            ),
            contradiction_spike_flags=contradiction_spike_flags,
        ),
        mode_and_gating=ReferenceModeAndGatingView(
            task_mode=task_mode,
            mode_tag=mode_tag,
            family_mask=family_mask,
        ),
        control_allocation=ReferenceControlAllocationView(
            budget_band=budget_band,
            top_family_set=top_family_set,
            host_friction_tags=host_friction_tags,
            feedback_pressure_tags=feedback_pressure_tags,
            productive_exploration_bonus=productive_exploration_bonus,
            oscillation_penalty=oscillation_penalty,
            anti_thrash_state=anti_thrash_state,
            repetition_tax=repetition_tax,
            repetition_target_family=repetition_target_family,
            anti_thrash_reason_tags=anti_thrash_reason_tags,
            risk_weight=risk_weight if risk_weight is not None else RiskWeight(),
        ),
        brake=ReferenceBrakeView(brake_state=brake_state, tonic=brake_tonic),
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
                    reason_tags=frozenset({"q_mem:active", "q_mem-signal:branch"}),
                )
                if branch_score > 0.0
                else None,
                SupportMemoryPriorScore(
                    family=SoftControlFamily.CHECK,
                    score=check_score,
                    reason_tags=frozenset({"q_mem:active", "q_mem-signal:contradiction"}),
                )
                if check_score > 0.0
                else None,
            )
            if score is not None
        ),
        appendix_tags=frozenset({"q_mem:explicit-aux"}),
        notes=("explicit AUX support-memory priors",),
    )


def _reference_replay_scenario(scenario_id: str):
    for scenario in make_aux_reference_replay_corpus():
        if scenario.scenario_id == scenario_id:
            return scenario
    raise AssertionError(f"Missing reference replay scenario {scenario_id!r}.")


def _support_memory_priors_from_temporal_case(
    scenario_id: str,
) -> SupportMemoryPriorAppendix:
    temporal_case = {
        scenario.scenario_id: scenario
        for scenario in make_aux_temporal_corpus()
    }[scenario_id]
    publication = _distill_offline_support_publication_from_snapshots(
        temporal_case.source_snapshots,
        host_name="reference",
        source_label="tests/product/test_reference_runtime_scoring",
        publication_tags=frozenset({"aux/offline-publication", "aux/reference-replay"}),
        notes=("product scoring replay prior test",),
    )
    augmented = augment_snapshot_with_offline_publication(
        temporal_case.target_snapshot,
        publication,
    )
    return build_support_memory_prior_appendix(augmented)
