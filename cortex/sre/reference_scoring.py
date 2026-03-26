"""Bounded reference-only scoring and family selection over executive state."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from .allocation import AllocationScore, AllocationScorecard
from .brake import BrakeState
from .families import SoftControlFamily
from .opportunities import (
    HostNativeOpportunity,
    OpportunitySpecializationResult,
    specialize_host_native_opportunity,
)
from .policy import NeutralDominanceDecision, neutral_dominance_decision
from .state import ReferenceExecutiveState

_BASE_SCORES = {
    SoftControlFamily.NEUTRAL: 1.0,
    SoftControlFamily.SEEK_CONTEXT: 0.4,
    SoftControlFamily.REDIRECT: 0.35,
    SoftControlFamily.CHECK: 0.45,
    SoftControlFamily.BRANCH: 0.45,
    SoftControlFamily.ESCALATE: 0.35,
    SoftControlFamily.BRAKE: 0.4,
}

_THRESHOLDS = {
    "low": 0.35,
    "medium": 0.25,
    "high": 0.2,
}


@dataclass(frozen=True, slots=True)
class ReferenceSoftControlSelection:
    scorecard: AllocationScorecard
    neutral_dominance: NeutralDominanceDecision
    opportunity_specialization: OpportunitySpecializationResult
    selected_family: SoftControlFamily

    def __post_init__(self) -> None:
        if not isinstance(self.scorecard, AllocationScorecard):
            actual_type = type(self.scorecard).__name__
            raise TypeError(
                "ReferenceSoftControlSelection.scorecard must be AllocationScorecard, "
                f"got {actual_type}."
            )
        if not isinstance(self.neutral_dominance, NeutralDominanceDecision):
            actual_type = type(self.neutral_dominance).__name__
            raise TypeError(
                "ReferenceSoftControlSelection.neutral_dominance must be "
                f"NeutralDominanceDecision, got {actual_type}."
            )
        if not isinstance(
            self.opportunity_specialization,
            OpportunitySpecializationResult,
        ):
            actual_type = type(self.opportunity_specialization).__name__
            raise TypeError(
                "ReferenceSoftControlSelection.opportunity_specialization must be "
                f"OpportunitySpecializationResult, got {actual_type}."
            )
        if not isinstance(self.selected_family, SoftControlFamily):
            actual_type = type(self.selected_family).__name__
            raise TypeError(
                "ReferenceSoftControlSelection.selected_family must be SoftControlFamily, "
                f"got {actual_type}."
            )
        if self.selected_family is not self.opportunity_specialization.selected_family:
            raise ValueError(
                "ReferenceSoftControlSelection.selected_family must match the opportunity-specialized family."
            )


def build_reference_allocation_scorecard(
    executive_state: ReferenceExecutiveState,
) -> AllocationScorecard:
    if not isinstance(executive_state, ReferenceExecutiveState):
        actual_type = type(executive_state).__name__
        raise TypeError(
            "build_reference_allocation_scorecard.executive_state must be "
            f"ReferenceExecutiveState, got {actual_type}."
        )

    family_mask = executive_state.mode_and_gating.family_mask
    top_family_set = executive_state.control_allocation.top_family_set
    host_friction_tags = executive_state.control_allocation.host_friction_tags
    brake_state = executive_state.brake.brake_state
    mode_tag = executive_state.mode_and_gating.mode_tag
    activation_threshold = _activation_threshold(
        executive_state.control_allocation.budget_band
    )

    scores: list[AllocationScore] = []
    for family in SoftControlFamily:
        admissible = family is SoftControlFamily.NEUTRAL or family in family_mask
        reason_tags = {
            f"mode:{mode_tag}",
            f"budget:{executive_state.control_allocation.budget_band}",
        }
        if family in top_family_set:
            reason_tags.add("top-family")
        if family in family_mask:
            reason_tags.add("mask-allowed")
        if host_friction_tags and family is SoftControlFamily.ESCALATE:
            reason_tags.add("host-friction")
        if not admissible and family is not SoftControlFamily.NEUTRAL:
            reason_tags.add("masked")
        if brake_state is not BrakeState.QUIESCENT and family is SoftControlFamily.BRAKE:
            reason_tags.add(f"brake:{brake_state.value}")

        scores.append(
            AllocationScore(
                family=family,
                score=_score_for_family(
                    family,
                    executive_state=executive_state,
                ),
                admissible=admissible,
                reason_tags=frozenset(reason_tags),
            )
        )

    return AllocationScorecard(
        scores=tuple(scores),
        activation_threshold=activation_threshold,
    )


def select_reference_soft_control(
    executive_state: ReferenceExecutiveState,
    *,
    opportunities: Sequence[HostNativeOpportunity] = (),
) -> ReferenceSoftControlSelection:
    scorecard = build_reference_allocation_scorecard(executive_state)
    dominance = neutral_dominance_decision(scorecard)
    opportunity_specialization = specialize_host_native_opportunity(
        dominance.selected_family,
        opportunities,
    )
    return ReferenceSoftControlSelection(
        scorecard=scorecard,
        neutral_dominance=dominance,
        opportunity_specialization=opportunity_specialization,
        selected_family=opportunity_specialization.selected_family,
    )


def _activation_threshold(budget_band: str) -> float:
    return _THRESHOLDS.get(budget_band, 0.3)


def _score_for_family(
    family: SoftControlFamily,
    *,
    executive_state: ReferenceExecutiveState,
) -> float:
    score = _BASE_SCORES[family]
    top_family_set = executive_state.control_allocation.top_family_set
    family_mask = executive_state.mode_and_gating.family_mask
    mode_tag = executive_state.mode_and_gating.mode_tag
    brake_state = executive_state.brake.brake_state
    host_friction_tags = executive_state.control_allocation.host_friction_tags
    budget_band = executive_state.control_allocation.budget_band

    if family in top_family_set and family is not SoftControlFamily.NEUTRAL:
        score += 0.45
    if family in family_mask and family is not SoftControlFamily.NEUTRAL:
        score += 0.1
    if mode_tag == "review_pending" and family is SoftControlFamily.CHECK:
        score += 0.25
    if mode_tag == "commitment_path" and family is SoftControlFamily.CHECK:
        score += 0.15
    if family is SoftControlFamily.BRANCH and family in top_family_set:
        score += 0.35
    if family is SoftControlFamily.BRAKE:
        if brake_state is BrakeState.GUARDED:
            score += 0.45
        if brake_state is BrakeState.LATCHED:
            score += 0.75
    if family is SoftControlFamily.ESCALATE and host_friction_tags:
        score += 0.25
    if family is SoftControlFamily.SEEK_CONTEXT and any(
        tag.endswith("missing") for tag in host_friction_tags
    ):
        score += 0.15
    if budget_band == "high" and family in {
        SoftControlFamily.CHECK,
        SoftControlFamily.BRANCH,
    }:
        score += 0.05
    return score


__all__ = [
    "ReferenceSoftControlSelection",
    "build_reference_allocation_scorecard",
    "select_reference_soft_control",
]
