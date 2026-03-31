"""Bounded reference-only scoring and family selection over executive state."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from .allocation import (
    AllocationScore,
    AllocationScorecard,
)
from .brake import BrakeState
from .families import SoftControlFamily
from .mediation import (
    ReferenceMediationFinalization,
    ReferenceMediationMode,
    finalize_reference_soft_control,
)
from .opportunities import (
    HostNativeOpportunity,
    OpportunitySpecializationResult,
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

_BASE_ACTIVATION_THRESHOLDS = {
    "low": 0.35,
    "medium": 0.25,
    "high": 0.2,
}

_SEEK_CONTEXT_PRESSURE_TAGS = frozenset(
    {
        "missing-capability",
        "capability-view-missing",
        "execution-trace-missing",
    }
)


@dataclass(frozen=True, slots=True)
class ReferenceSoftControlSelection:
    scorecard: AllocationScorecard
    neutral_dominance: NeutralDominanceDecision
    selected_family_before_finalization: SoftControlFamily
    mediation_finalization: ReferenceMediationFinalization
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
            self.selected_family_before_finalization,
            SoftControlFamily,
        ):
            actual_type = type(self.selected_family_before_finalization).__name__
            raise TypeError(
                "ReferenceSoftControlSelection.selected_family_before_finalization "
                f"must be SoftControlFamily, got {actual_type}."
            )
        if not isinstance(
            self.mediation_finalization,
            ReferenceMediationFinalization,
        ):
            actual_type = type(self.mediation_finalization).__name__
            raise TypeError(
                "ReferenceSoftControlSelection.mediation_finalization must be "
                f"ReferenceMediationFinalization, got {actual_type}."
            )
        if not isinstance(self.selected_family, SoftControlFamily):
            actual_type = type(self.selected_family).__name__
            raise TypeError(
                "ReferenceSoftControlSelection.selected_family must be SoftControlFamily, "
                f"got {actual_type}."
            )
        if self.selected_family_before_finalization is not self.neutral_dominance.selected_family:
            raise ValueError(
                "ReferenceSoftControlSelection.selected_family_before_finalization "
                "must match the neutral-dominance family."
            )
        if self.selected_family is not self.mediation_finalization.selected_family_after_finalization:
            raise ValueError(
                "ReferenceSoftControlSelection.selected_family must match the mediation-finalized family."
            )

    @property
    def opportunity_specialization(self) -> OpportunitySpecializationResult:
        return self.mediation_finalization.opportunity_specialization


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
    activation_threshold = compute_reference_activation_threshold(executive_state)
    alpha_t = compute_reference_alpha_t(executive_state)
    online_components = build_reference_online_score_components(executive_state)

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
        if family is SoftControlFamily.SEEK_CONTEXT and _has_seek_context_pressure(
            host_friction_tags,
            brake_state=brake_state,
        ):
            reason_tags.add("seek-context-pressure")
        if not admissible and family is not SoftControlFamily.NEUTRAL:
            reason_tags.add("masked")
        if brake_state is not BrakeState.QUIESCENT and family is SoftControlFamily.BRAKE:
            reason_tags.add(f"brake:{brake_state.value}")
        reason_tags.add("allocation:online-only")
        reason_tags.add(_alpha_reason_tag(alpha_t))

        online_score = _online_score(online_components[family])
        allocated_score = alpha_t * online_score
        scores.append(
            AllocationScore(
                family=family,
                score=allocated_score,
                admissible=admissible,
                reason_tags=frozenset(reason_tags),
                online_score=online_score,
                memory_score=0.0,
                allocated_score=allocated_score,
            )
        )

    return AllocationScorecard(
        scores=tuple(scores),
        activation_threshold=activation_threshold,
        alpha_t=alpha_t,
    )


def select_reference_soft_control(
    executive_state: ReferenceExecutiveState,
    *,
    mediation_mode: ReferenceMediationMode = ReferenceMediationMode.IDENTITY,
    opportunities: Sequence[HostNativeOpportunity] = (),
) -> ReferenceSoftControlSelection:
    scorecard = build_reference_allocation_scorecard(executive_state)
    dominance = neutral_dominance_decision(scorecard)
    mediation_finalization = finalize_reference_soft_control(
        dominance.selected_family,
        mediation_mode=mediation_mode,
        opportunities=opportunities,
    )
    return ReferenceSoftControlSelection(
        scorecard=scorecard,
        neutral_dominance=dominance,
        selected_family_before_finalization=dominance.selected_family,
        mediation_finalization=mediation_finalization,
        selected_family=mediation_finalization.selected_family_after_finalization,
    )


def _baseline_activation_threshold(budget_band: str) -> float:
    return _BASE_ACTIVATION_THRESHOLDS.get(budget_band, 0.3)


def compute_reference_alpha_t(
    executive_state: ReferenceExecutiveState,
) -> float:
    if not isinstance(executive_state, ReferenceExecutiveState):
        actual_type = type(executive_state).__name__
        raise TypeError(
            "compute_reference_alpha_t.executive_state must be "
            f"ReferenceExecutiveState, got {actual_type}."
        )

    brake_state = executive_state.brake.brake_state
    host_friction_tags = executive_state.control_allocation.host_friction_tags
    contradiction_spike_flags = executive_state.uncertainty_monitoring.contradiction_spike_flags
    max_uncertainty = max(
        (estimate.level for estimate in executive_state.uncertainty_monitoring.classwise_uncertainty),
        default=0.0,
    )
    pressure = bool(host_friction_tags or contradiction_spike_flags or max_uncertainty >= 0.55)

    if brake_state is BrakeState.LATCHED:
        return 0.65
    if brake_state is BrakeState.GUARDED and pressure:
        return 0.75
    if pressure:
        return 0.85
    return 1.0


def compute_reference_activation_threshold(
    executive_state: ReferenceExecutiveState,
) -> float:
    if not isinstance(executive_state, ReferenceExecutiveState):
        actual_type = type(executive_state).__name__
        raise TypeError(
            "compute_reference_activation_threshold.executive_state must be "
            f"ReferenceExecutiveState, got {actual_type}."
        )

    threshold = _baseline_activation_threshold(
        executive_state.control_allocation.budget_band
    )
    brake_state = executive_state.brake.brake_state
    if brake_state is BrakeState.LATCHED:
        threshold += 0.10
    elif brake_state is BrakeState.GUARDED:
        threshold += 0.05
    if _has_current_visible_pressure(executive_state):
        threshold += 0.05
    if executive_state.control_allocation.feedback_pressure_tags:
        threshold += 0.05
    return min(0.45, max(0.20, threshold))


def build_reference_online_score_components(
    executive_state: ReferenceExecutiveState,
) -> dict[SoftControlFamily, dict[str, float]]:
    if not isinstance(executive_state, ReferenceExecutiveState):
        actual_type = type(executive_state).__name__
        raise TypeError(
            "build_reference_online_score_components.executive_state must be "
            f"ReferenceExecutiveState, got {actual_type}."
        )

    return {
        family: _online_score_components_for_family(
            family,
            executive_state=executive_state,
        )
        for family in SoftControlFamily
    }


def _has_current_visible_pressure(
    executive_state: ReferenceExecutiveState,
) -> bool:
    contradiction_spike_flags = executive_state.uncertainty_monitoring.contradiction_spike_flags
    current_visible_contradictions = any(
        not (flag.startswith("prior-") or flag.startswith("sustained-"))
        for flag in contradiction_spike_flags
    )
    non_goal_uncertainty = max(
        (
            estimate.level
            for estimate in executive_state.uncertainty_monitoring.classwise_uncertainty
            if estimate.class_tag != "goal-progress"
        ),
        default=0.0,
    )
    return bool(
        executive_state.control_allocation.host_friction_tags
        or current_visible_contradictions
        or non_goal_uncertainty >= 0.55
    )


def _online_score_components_for_family(
    family: SoftControlFamily,
    *,
    executive_state: ReferenceExecutiveState,
) -> dict[str, float]:
    task_progress = float(_BASE_SCORES[family])
    top_family_set = executive_state.control_allocation.top_family_set
    family_mask = executive_state.mode_and_gating.family_mask
    mode_tag = executive_state.mode_and_gating.mode_tag
    brake_state = executive_state.brake.brake_state
    host_friction_tags = executive_state.control_allocation.host_friction_tags
    budget_band = executive_state.control_allocation.budget_band
    goal_continuity = executive_state.goal_continuity
    contradiction_spike_flags = (
        executive_state.uncertainty_monitoring.contradiction_spike_flags
    )

    uncertainty_reduction = 0.0
    continuity_value = 0.0
    stability_value = 0.0
    control_burden = 0.0
    host_friction = 0.0
    visible_burden = 0.0

    if family in top_family_set and family is not SoftControlFamily.NEUTRAL:
        stability_value += 0.45
    if family in family_mask and family is not SoftControlFamily.NEUTRAL:
        task_progress += 0.1
    if mode_tag == "review_pending" and family is SoftControlFamily.CHECK:
        uncertainty_reduction += 0.25
    if mode_tag == "commitment_path" and family is SoftControlFamily.CHECK:
        uncertainty_reduction += 0.15
    if family is SoftControlFamily.BRANCH and family in top_family_set:
        continuity_value += 0.35
    if family is SoftControlFamily.BRAKE:
        if brake_state is BrakeState.GUARDED:
            stability_value += 0.45
        if brake_state is BrakeState.LATCHED:
            stability_value += 0.75
    if family is SoftControlFamily.ESCALATE and host_friction_tags:
        stability_value += 0.25
    if family is SoftControlFamily.SEEK_CONTEXT and _has_seek_context_pressure(
        host_friction_tags,
        brake_state=brake_state,
    ):
        # J4B keeps threshold and vigor law fixed, so explicit missing-context
        # pressure needs a route-local lift that creates a real runtime path.
        uncertainty_reduction += 0.70
    if budget_band == "high" and family in {
        SoftControlFamily.CHECK,
        SoftControlFamily.BRANCH,
    }:
        task_progress += 0.05

    if goal_continuity.pending_goal_refs and family is SoftControlFamily.REDIRECT:
        continuity_value += 0.05
    if goal_continuity.active_track_ref != "main" and family is SoftControlFamily.BRANCH:
        continuity_value += 0.05
    if goal_continuity.resume_anchor_available and family is SoftControlFamily.BRANCH:
        continuity_value += 0.05

    if contradiction_spike_flags:
        if family is SoftControlFamily.CHECK:
            uncertainty_reduction += 0.05
        if family is SoftControlFamily.BRAKE:
            stability_value += 0.05

    if family is SoftControlFamily.BRANCH:
        if brake_state is BrakeState.GUARDED:
            control_burden += 0.5
        if brake_state is BrakeState.LATCHED:
            control_burden += 0.8

    return {
        "task_progress": task_progress,
        "uncertainty_reduction": uncertainty_reduction,
        "goal_continuity": continuity_value,
        "stability": stability_value,
        "control_burden": control_burden,
        "host_friction": host_friction,
        "visible_burden": visible_burden,
    }


def _online_score(components: dict[str, float]) -> float:
    return (
        components["task_progress"]
        + components["uncertainty_reduction"]
        + components["goal_continuity"]
        + components["stability"]
        - components["control_burden"]
        - components["host_friction"]
        - components["visible_burden"]
    )


def _alpha_reason_tag(alpha_t: float) -> str:
    if alpha_t == 1.0:
        return "alpha:1.0"
    if alpha_t == 0.85:
        return "alpha:0.85"
    if alpha_t == 0.75:
        return "alpha:0.75"
    if alpha_t == 0.65:
        return "alpha:0.65"
    return f"alpha:{alpha_t:.2f}"


def _has_seek_context_pressure(
    host_friction_tags: frozenset[str],
    *,
    brake_state: BrakeState,
) -> bool:
    if brake_state is BrakeState.LATCHED:
        return False
    return any(tag in _SEEK_CONTEXT_PRESSURE_TAGS for tag in host_friction_tags)


__all__ = [
    "ReferenceSoftControlSelection",
    "build_allocation_diagnostics_payload",
    "build_reference_allocation_scorecard",
    "compute_reference_activation_threshold",
    "build_reference_online_score_components",
    "compute_reference_alpha_t",
    "select_reference_soft_control",
]
