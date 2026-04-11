"""Explicit goal-branch contribution law for reference soft-control scoring."""

from __future__ import annotations

from dataclasses import dataclass, field
from numbers import Real

from .brake import BrakeState
from .families import SoftControlFamily
from .state import ReferenceExecutiveState


def _clip_score(value: float) -> float:
    return max(-1.0, min(1.0, float(value)))


def _clip_weight(value: float) -> float:
    return max(0.0, min(0.5, float(value)))


@dataclass(frozen=True, slots=True)
class GoalBranchScore:
    family: SoftControlFamily
    score: float
    reason_tags: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if not isinstance(self.family, SoftControlFamily):
            actual_type = type(self.family).__name__
            raise TypeError(
                "GoalBranchScore.family must be SoftControlFamily, "
                f"got {actual_type}."
            )
        if not isinstance(self.score, Real):
            actual_type = type(self.score).__name__
            raise TypeError(
                "GoalBranchScore.score must be numeric, "
                f"got {actual_type}."
            )
        if any(not tag.strip() for tag in self.reason_tags):
            raise ValueError(
                "GoalBranchScore.reason_tags must contain only non-empty values after trimming."
            )
        object.__setattr__(self, "score", _clip_score(float(self.score)))


@dataclass(frozen=True, slots=True)
class GoalBranchCoupling:
    weight: float
    scores: tuple[GoalBranchScore, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.weight, Real):
            actual_type = type(self.weight).__name__
            raise TypeError(
                "GoalBranchCoupling.weight must be numeric, "
                f"got {actual_type}."
            )
        if any(not isinstance(score, GoalBranchScore) for score in self.scores):
            raise TypeError(
                "GoalBranchCoupling.scores must contain only GoalBranchScore instances."
            )
        object.__setattr__(self, "weight", _clip_weight(float(self.weight)))

    def score_for(self, family: SoftControlFamily) -> GoalBranchScore:
        if not isinstance(family, SoftControlFamily):
            actual_type = type(family).__name__
            raise TypeError(
                "GoalBranchCoupling.score_for.family must be SoftControlFamily, "
                f"got {actual_type}."
            )
        for score in self.scores:
            if score.family is family:
                return score
        raise KeyError(f"Missing goal-branch score for family {family.value!r}.")


def build_reference_goal_branch_coupling(
    executive_state: ReferenceExecutiveState,
) -> GoalBranchCoupling:
    if not isinstance(executive_state, ReferenceExecutiveState):
        actual_type = type(executive_state).__name__
        raise TypeError(
            "build_reference_goal_branch_coupling.executive_state must be "
            f"ReferenceExecutiveState, got {actual_type}."
        )

    goal_continuity = executive_state.goal_continuity
    brake_state = executive_state.brake.brake_state
    pending_goal_count = len(goal_continuity.pending_goal_refs)
    active_branch = goal_continuity.active_track_ref not in (None, "main")
    has_resume_anchor = goal_continuity.resume_anchor_available
    continuity_debt = active_branch or pending_goal_count > 0

    weight = 0.0
    if continuity_debt:
        weight = 0.18
        if active_branch:
            weight += 0.12
        if pending_goal_count:
            weight += min(0.10, 0.04 * pending_goal_count)
        if has_resume_anchor:
            weight += 0.05
        elif active_branch:
            weight += 0.03
        if brake_state is BrakeState.GUARDED:
            weight += 0.04
        elif brake_state is BrakeState.LATCHED:
            weight += 0.02
    weight = _clip_weight(weight)

    branch_score = 0.0
    redirect_score = 0.0
    check_score = 0.0
    neutral_score = 0.0
    reason_tags: set[str] = set()

    if active_branch:
        branch_score += 0.60
        neutral_score -= 0.22
        reason_tags.add("active-track")
    if pending_goal_count:
        branch_score += min(0.18, 0.06 * pending_goal_count)
        redirect_score += min(0.22, 0.08 * pending_goal_count)
        check_score += min(0.10, 0.04 * pending_goal_count)
        neutral_score -= min(0.10, 0.03 * pending_goal_count)
        reason_tags.add("pending-goal-debt")
    if has_resume_anchor:
        branch_score += 0.10
        reason_tags.add("resume-anchor-available")
    elif active_branch:
        branch_score -= 0.12
        check_score += 0.18
        reason_tags.add("resume-anchor-missing")
    if brake_state is BrakeState.GUARDED:
        branch_score -= 0.08
        check_score += 0.06
        reason_tags.add("guarded-brake")
    elif brake_state is BrakeState.LATCHED:
        branch_score -= 0.22
        check_score += 0.12
        neutral_score -= 0.04
        reason_tags.add("latched-brake")

    family_scores = {
        SoftControlFamily.NEUTRAL: neutral_score,
        SoftControlFamily.SEEK_CONTEXT: 0.0,
        SoftControlFamily.REDIRECT: redirect_score,
        SoftControlFamily.CHECK: check_score,
        SoftControlFamily.BRANCH: branch_score,
        SoftControlFamily.ESCALATE: 0.0,
        SoftControlFamily.BRAKE: 0.0,
    }
    shared_reason_tags = frozenset(reason_tags)
    return GoalBranchCoupling(
        weight=weight,
        scores=tuple(
            GoalBranchScore(
                family=family,
                score=score,
                reason_tags=shared_reason_tags if score != 0.0 else frozenset(),
            )
            for family, score in family_scores.items()
        ),
    )


__all__ = [
    "GoalBranchCoupling",
    "GoalBranchScore",
    "build_reference_goal_branch_coupling",
]
