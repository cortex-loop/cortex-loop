"""Neutral-dominance policy check for the first active SRE hinge."""

from __future__ import annotations

from dataclasses import dataclass
from numbers import Real

from .allocation import AllocationScore, AllocationScorecard
from .families import SoftControlFamily


@dataclass(frozen=True, slots=True)
class NeutralDominanceDecision:
    selected_family: SoftControlFamily
    neutral_selected: bool
    margin_over_neutral: float
    activation_threshold: float

    def __post_init__(self) -> None:
        if not isinstance(self.selected_family, SoftControlFamily):
            actual_type = type(self.selected_family).__name__
            raise TypeError(
                "NeutralDominanceDecision.selected_family must be SoftControlFamily, "
                f"got {actual_type}."
            )
        if not isinstance(self.neutral_selected, bool):
            actual_type = type(self.neutral_selected).__name__
            raise TypeError(
                "NeutralDominanceDecision.neutral_selected must be bool, "
                f"got {actual_type}."
            )
        if not isinstance(self.margin_over_neutral, Real):
            actual_type = type(self.margin_over_neutral).__name__
            raise TypeError(
                "NeutralDominanceDecision.margin_over_neutral must be numeric, "
                f"got {actual_type}."
            )


def neutral_dominance_decision(scorecard: AllocationScorecard) -> NeutralDominanceDecision:
    scores_by_family = _scores_by_family(scorecard.scores)
    neutral_score = scores_by_family.get(SoftControlFamily.NEUTRAL)
    if neutral_score is None:
        raise ValueError("AllocationScorecard must include SoftControlFamily.NEUTRAL.")
    if not neutral_score.admissible:
        raise ValueError("SoftControlFamily.NEUTRAL must remain admissible.")

    best_non_neutral = _best_non_neutral_score(scores_by_family)
    if best_non_neutral is None:
        return NeutralDominanceDecision(
            selected_family=SoftControlFamily.NEUTRAL,
            neutral_selected=True,
            margin_over_neutral=0.0,
            activation_threshold=scorecard.activation_threshold,
        )

    margin = best_non_neutral.score - neutral_score.score
    if margin <= scorecard.activation_threshold:
        return NeutralDominanceDecision(
            selected_family=SoftControlFamily.NEUTRAL,
            neutral_selected=True,
            margin_over_neutral=margin,
            activation_threshold=scorecard.activation_threshold,
        )
    return NeutralDominanceDecision(
        selected_family=best_non_neutral.family,
        neutral_selected=False,
        margin_over_neutral=margin,
        activation_threshold=scorecard.activation_threshold,
    )


def _scores_by_family(
    scores: tuple[AllocationScore, ...],
) -> dict[SoftControlFamily, AllocationScore]:
    score_map: dict[SoftControlFamily, AllocationScore] = {}
    for score in scores:
        score_map[score.family] = score
    return score_map


def _best_non_neutral_score(
    score_map: dict[SoftControlFamily, AllocationScore],
) -> AllocationScore | None:
    candidates = [
        score
        for family, score in score_map.items()
        if family is not SoftControlFamily.NEUTRAL and score.admissible
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda score: score.score)


__all__ = ["NeutralDominanceDecision", "neutral_dominance_decision"]
