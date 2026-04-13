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
from .goal_branch import build_reference_goal_branch_coupling
from .memory_priors import SupportMemoryPriorAppendix
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
_HOST_FRICTION_FAMILY_MULTIPLIERS = {
    SoftControlFamily.NEUTRAL: 0.0,
    SoftControlFamily.SEEK_CONTEXT: 0.55,
    SoftControlFamily.REDIRECT: 0.55,
    SoftControlFamily.CHECK: 0.30,
    SoftControlFamily.BRANCH: 0.40,
    SoftControlFamily.ESCALATE: 0.75,
    SoftControlFamily.BRAKE: 0.0,
}
_PROBE_BACKED_HOST_FRICTION_MULTIPLIERS = {
    SoftControlFamily.SEEK_CONTEXT: 0.20,
    SoftControlFamily.CHECK: 0.12,
}
_VISIBLE_BURDEN_FAMILY_COSTS = {
    SoftControlFamily.NEUTRAL: 0.0,
    SoftControlFamily.SEEK_CONTEXT: 0.04,
    SoftControlFamily.REDIRECT: 0.12,
    SoftControlFamily.CHECK: 0.03,
    SoftControlFamily.BRANCH: 0.08,
    SoftControlFamily.ESCALATE: 0.16,
    SoftControlFamily.BRAKE: 0.05,
}
_FAMILY_RELATIVE_BURDEN = {
    SoftControlFamily.NEUTRAL: 0.00,
    SoftControlFamily.CHECK: 0.20,
    SoftControlFamily.SEEK_CONTEXT: 0.25,
    SoftControlFamily.BRAKE: 0.30,
    SoftControlFamily.BRANCH: 0.45,
    SoftControlFamily.REDIRECT: 0.55,
    SoftControlFamily.ESCALATE: 0.75,
}


@dataclass(frozen=True, slots=True)
class ReferenceSoftControlSelection:
    scorecard: AllocationScorecard
    neutral_dominance: NeutralDominanceDecision
    selected_family_before_finalization: SoftControlFamily
    mediation_finalization: ReferenceMediationFinalization
    selected_family: SoftControlFamily
    chi_t: float

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
        if not 0.0 <= float(self.chi_t) <= 1.0:
            raise ValueError("ReferenceSoftControlSelection.chi_t must be between 0.0 and 1.0.")

    @property
    def opportunity_specialization(self) -> OpportunitySpecializationResult:
        return self.mediation_finalization.opportunity_specialization


def build_reference_allocation_scorecard(
    executive_state: ReferenceExecutiveState,
    *,
    memory_priors: SupportMemoryPriorAppendix | None = None,
) -> AllocationScorecard:
    if not isinstance(executive_state, ReferenceExecutiveState):
        actual_type = type(executive_state).__name__
        raise TypeError(
            "build_reference_allocation_scorecard.executive_state must be "
            f"ReferenceExecutiveState, got {actual_type}."
        )
    if memory_priors is not None and not isinstance(memory_priors, SupportMemoryPriorAppendix):
        actual_type = type(memory_priors).__name__
        raise TypeError(
            "build_reference_allocation_scorecard.memory_priors must be "
            f"SupportMemoryPriorAppendix | None, got {actual_type}."
        )

    family_mask = executive_state.mode_and_gating.family_mask
    top_family_set = executive_state.control_allocation.top_family_set
    host_friction_tags = executive_state.control_allocation.host_friction_tags
    brake_state = executive_state.brake.brake_state
    mode_tag = executive_state.mode_and_gating.mode_tag
    alpha_t = compute_reference_alpha_t(executive_state)
    online_components = build_reference_online_score_components(executive_state)
    goal_branch_coupling = build_reference_goal_branch_coupling(executive_state)
    activation_thresholds = {
        family: compute_reference_activation_threshold(
            executive_state,
            family=family,
        )
        for family in SoftControlFamily
    }

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
        if family in executive_state.control_allocation.probe_backed_families:
            reason_tags.add("probe-backed")
        if family is SoftControlFamily.SEEK_CONTEXT and _has_seek_context_pressure(
            executive_state
        ):
            reason_tags.add("seek-context-pressure")
        if family is SoftControlFamily.CHECK and _is_low_burden_check_relief(
            executive_state
        ):
            reason_tags.add("check-relief")
        if not admissible and family is not SoftControlFamily.NEUTRAL:
            reason_tags.add("masked")
        if brake_state is not BrakeState.QUIESCENT and family is SoftControlFamily.BRAKE:
            reason_tags.add(f"brake:{brake_state.value}")
        if family is not SoftControlFamily.NEUTRAL:
            reason_tags.add(f"theta_act:{activation_thresholds[family]:.2f}")
        reason_tags.add(_alpha_reason_tag(alpha_t))
        reason_tags.add(
            f"explain:{executive_state.control_allocation.explainability_profile}"
        )
        if executive_state.control_allocation.recent_probe_result_class is not None:
            reason_tags.add(
                f"probe:{executive_state.control_allocation.recent_probe_result_class}"
            )

        online_score = _online_score(online_components[family])
        memory_prior = (
            memory_priors.score_for(family)
            if memory_priors is not None
            else None
        )
        memory_score = 0.0 if memory_prior is None else float(memory_prior.score)
        goal_branch_score = goal_branch_coupling.score_for(family)
        memory_contribution_active = memory_score > 0.0 and alpha_t < 1.0
        goal_branch_contribution_active = (
            goal_branch_coupling.weight > 0.0 and goal_branch_score.score != 0.0
        )
        if memory_contribution_active and goal_branch_contribution_active:
            reason_tags.add("allocation:full-mixed")
        elif memory_contribution_active:
            reason_tags.add("allocation:online-plus-memory")
        elif goal_branch_contribution_active:
            reason_tags.add("allocation:online-plus-goal-branch")
        else:
            reason_tags.add("allocation:online-only")
        if goal_branch_contribution_active:
            reason_tags.add(_goal_branch_weight_reason_tag(goal_branch_coupling.weight))
            reason_tags.add("goal-branch-coupled")
            reason_tags.update(goal_branch_score.reason_tags)
        if memory_contribution_active:
            reason_tags.update(memory_prior.reason_tags)
        allocated_score = (alpha_t * online_score) + (
            (1.0 - alpha_t) * memory_score
        ) + (
            goal_branch_coupling.weight * goal_branch_score.score
        )
        scores.append(
            AllocationScore(
                family=family,
                score=allocated_score,
                admissible=admissible,
                reason_tags=frozenset(reason_tags),
                activation_threshold=activation_thresholds[family],
                online_score=online_score,
                memory_score=memory_score,
                allocated_score=allocated_score,
            )
        )

    return AllocationScorecard(
        scores=tuple(scores),
        alpha_t=alpha_t,
    )


def select_reference_soft_control(
    executive_state: ReferenceExecutiveState,
    *,
    mediation_mode: ReferenceMediationMode = ReferenceMediationMode.IDENTITY,
    memory_priors: SupportMemoryPriorAppendix | None = None,
    opportunities: Sequence[HostNativeOpportunity] = (),
) -> ReferenceSoftControlSelection:
    scorecard = build_reference_allocation_scorecard(
        executive_state,
        memory_priors=memory_priors,
    )
    dominance = neutral_dominance_decision(scorecard)
    mediation_finalization = finalize_reference_soft_control(
        dominance.selected_family,
        mediation_mode=mediation_mode,
        opportunities=opportunities,
    )
    chi_t = compute_reference_chi_t(
        executive_state,
        neutral_dominance=dominance,
    )
    return ReferenceSoftControlSelection(
        scorecard=scorecard,
        neutral_dominance=dominance,
        selected_family_before_finalization=dominance.selected_family,
        mediation_finalization=mediation_finalization,
        selected_family=mediation_finalization.selected_family_after_finalization,
        chi_t=chi_t,
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
    *,
    family: SoftControlFamily | None = None,
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
    threshold = min(0.45, max(0.20, threshold))
    if family is None:
        return threshold
    if not isinstance(family, SoftControlFamily):
        actual_type = type(family).__name__
        raise TypeError(
            "compute_reference_activation_threshold.family must be "
            f"SoftControlFamily | None, got {actual_type}."
        )
    if family is SoftControlFamily.NEUTRAL:
        return 0.0

    if family is SoftControlFamily.CHECK and _is_low_burden_check_relief(executive_state):
        threshold -= 0.10
    elif family is SoftControlFamily.SEEK_CONTEXT and _has_seek_context_pressure(executive_state):
        threshold -= 0.08
    elif family is SoftControlFamily.BRANCH:
        threshold += 0.08
    elif family is SoftControlFamily.REDIRECT:
        threshold += 0.05
    elif family is SoftControlFamily.ESCALATE:
        threshold += 0.10

    if family in {SoftControlFamily.CHECK, SoftControlFamily.SEEK_CONTEXT}:
        threshold -= executive_state.control_allocation.productive_exploration_bonus
    if family in {
        SoftControlFamily.BRANCH,
        SoftControlFamily.REDIRECT,
        SoftControlFamily.ESCALATE,
    }:
        threshold += executive_state.control_allocation.oscillation_penalty

    return min(0.60, max(0.05, threshold))


def compute_reference_chi_t(
    executive_state: ReferenceExecutiveState,
    *,
    neutral_dominance: NeutralDominanceDecision,
) -> float:
    if not isinstance(executive_state, ReferenceExecutiveState):
        actual_type = type(executive_state).__name__
        raise TypeError(
            "compute_reference_chi_t.executive_state must be "
            f"ReferenceExecutiveState, got {actual_type}."
        )
    if not isinstance(neutral_dominance, NeutralDominanceDecision):
        actual_type = type(neutral_dominance).__name__
        raise TypeError(
            "compute_reference_chi_t.neutral_dominance must be "
            f"NeutralDominanceDecision, got {actual_type}."
        )
    if neutral_dominance.neutral_selected:
        return 0.0

    denominator = max(0.05, 1.0 - neutral_dominance.activation_threshold)
    dominance_margin = max(
        0.0,
        neutral_dominance.margin_over_neutral - neutral_dominance.activation_threshold,
    )
    dominance_strength = min(1.0, dominance_margin / denominator)
    uncertainty = max(
        (
            estimate.level
            for estimate in executive_state.uncertainty_monitoring.classwise_uncertainty
        ),
        default=0.0,
    )
    budget_band = executive_state.control_allocation.budget_band
    quota_pressure = 0.25 if budget_band == "low" else 0.50 if budget_band == "medium" else 0.75
    burden_pressure = 0.0
    if executive_state.control_allocation.host_friction_tags:
        burden_pressure += 0.10
    if executive_state.control_allocation.feedback_pressure_tags:
        burden_pressure += 0.10
    chi_t = max(
        0.0,
        min(
            1.0,
            0.20
            + (0.70 * dominance_strength)
            - (0.30 * uncertainty)
            - (0.15 * quota_pressure)
            - burden_pressure,
        ),
    )
    if executive_state.brake.brake_state is BrakeState.GUARDED:
        return min(0.55, chi_t)
    if executive_state.brake.brake_state is BrakeState.LATCHED:
        return min(0.20, chi_t)
    return chi_t


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
    productive_exploration_bonus = (
        executive_state.control_allocation.productive_exploration_bonus
    )
    oscillation_penalty = executive_state.control_allocation.oscillation_penalty
    probe_backed_families = executive_state.control_allocation.probe_backed_families
    budget_band = executive_state.control_allocation.budget_band
    goal_continuity = executive_state.goal_continuity
    contradiction_spike_flags = (
        executive_state.uncertainty_monitoring.contradiction_spike_flags
    )

    uncertainty_reduction = 0.0
    continuity_value = 0.0
    stability_value = 0.0
    control_burden = 0.0
    host_friction = _family_host_friction_cost(
        family,
        executive_state=executive_state,
    )
    visible_burden = _family_visible_burden_cost(
        family,
        executive_state=executive_state,
    )

    if family in top_family_set and family is not SoftControlFamily.NEUTRAL:
        stability_value += 0.45
    if family in family_mask and family is not SoftControlFamily.NEUTRAL:
        task_progress += 0.1
    if mode_tag == "review_pending" and family is SoftControlFamily.CHECK:
        uncertainty_reduction += 0.25
    if mode_tag == "commitment_path" and family is SoftControlFamily.CHECK:
        uncertainty_reduction += 0.15
    if (
        family is SoftControlFamily.CHECK
        and executive_state.control_allocation.feedback_pressure_tags
    ):
        uncertainty_reduction += 0.10
    if family is SoftControlFamily.BRANCH and family in top_family_set:
        continuity_value += 0.35
    if family is SoftControlFamily.BRAKE:
        if brake_state is BrakeState.GUARDED:
            stability_value += 0.45
        if brake_state is BrakeState.LATCHED:
            stability_value += 0.75
        if oscillation_penalty > 0.0:
            stability_value += 0.5 * oscillation_penalty
    if family is SoftControlFamily.ESCALATE and host_friction_tags:
        stability_value += 0.25
    if family is SoftControlFamily.SEEK_CONTEXT and _has_seek_context_pressure(executive_state):
        # J4B keeps threshold and vigor law fixed, so explicit missing-context
        # pressure needs a route-local lift that creates a real runtime path.
        uncertainty_reduction += 0.70
        if family not in probe_backed_families:
            # When a host lacks a bounded probe route, fallback seek-context still
            # needs enough vigor to beat neutral under genuine capability or
            # environment pressure instead of collapsing into passive continuation.
            uncertainty_reduction += 0.20
    if family is SoftControlFamily.CHECK and _is_low_burden_check_relief(executive_state):
        uncertainty_reduction += 0.18
    if family is SoftControlFamily.CHECK and family in probe_backed_families:
        uncertainty_reduction += 0.20
    if family is SoftControlFamily.SEEK_CONTEXT and family in probe_backed_families:
        uncertainty_reduction += 0.12
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
    if family in {SoftControlFamily.CHECK, SoftControlFamily.SEEK_CONTEXT}:
        stability_value += productive_exploration_bonus
    if family in {
        SoftControlFamily.BRANCH,
        SoftControlFamily.REDIRECT,
        SoftControlFamily.ESCALATE,
    }:
        control_burden += oscillation_penalty

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


def _goal_branch_weight_reason_tag(weight: float) -> str:
    return f"lambda_G:{weight:.2f}"


def _has_seek_context_pressure(
    executive_state: ReferenceExecutiveState,
) -> bool:
    host_friction_tags = executive_state.control_allocation.host_friction_tags
    if (
        SoftControlFamily.SEEK_CONTEXT
        in executive_state.control_allocation.probe_backed_families
        and any(
            class_tag in {"environment", "host-capability"}
            for class_tag in _dominant_uncertainty_classes(executive_state)
        )
    ):
        if executive_state.brake.brake_state is not BrakeState.LATCHED:
            return True
        return _latched_relief_permitted(
            executive_state,
            family=SoftControlFamily.SEEK_CONTEXT,
        )
    if not any(tag in _SEEK_CONTEXT_PRESSURE_TAGS for tag in host_friction_tags):
        return False
    if executive_state.brake.brake_state is not BrakeState.LATCHED:
        return True
    return _latched_relief_permitted(
        executive_state,
        family=SoftControlFamily.SEEK_CONTEXT,
    )


def _is_low_burden_check_relief(
    executive_state: ReferenceExecutiveState,
) -> bool:
    dominant_uncertainty_classes = _dominant_uncertainty_classes(executive_state)
    contradiction_spike_flags = executive_state.uncertainty_monitoring.contradiction_spike_flags
    if contradiction_spike_flags:
        return True
    if any(
        class_tag in {"evidence", "environment"}
        for class_tag in dominant_uncertainty_classes
    ):
        return True
    if (
        SoftControlFamily.CHECK
        in executive_state.control_allocation.probe_backed_families
        and any(
            class_tag in {"environment", "host-capability"}
            for class_tag in dominant_uncertainty_classes
        )
    ):
        return True
    if executive_state.brake.brake_state is BrakeState.LATCHED:
        return _latched_relief_permitted(
            executive_state,
            family=SoftControlFamily.CHECK,
        )
    return False


def _latched_relief_permitted(
    executive_state: ReferenceExecutiveState,
    *,
    family: SoftControlFamily,
) -> bool:
    if executive_state.brake.brake_state is not BrakeState.LATCHED:
        return True
    dominant_uncertainty_classes = _dominant_uncertainty_classes(executive_state)
    if family is SoftControlFamily.CHECK:
        return any(
            class_tag in {"evidence", "environment"}
            for class_tag in dominant_uncertainty_classes
        )
    if family is SoftControlFamily.SEEK_CONTEXT:
        return any(
            class_tag in {"evidence", "environment", "host-capability"}
            for class_tag in dominant_uncertainty_classes
        )
    return False


def _dominant_uncertainty_classes(
    executive_state: ReferenceExecutiveState,
) -> tuple[str, ...]:
    ranked = sorted(
        executive_state.uncertainty_monitoring.classwise_uncertainty,
        key=lambda estimate: (-estimate.level, estimate.class_tag),
    )
    return tuple(estimate.class_tag for estimate in ranked[:2])


def _family_host_friction_cost(
    family: SoftControlFamily,
    *,
    executive_state: ReferenceExecutiveState,
) -> float:
    base_multiplier = _HOST_FRICTION_FAMILY_MULTIPLIERS[family]
    if family in executive_state.control_allocation.probe_backed_families:
        base_multiplier = _PROBE_BACKED_HOST_FRICTION_MULTIPLIERS.get(
            family,
            base_multiplier,
        )
    return min(
        1.0,
        executive_state.control_allocation.host_friction_level * base_multiplier,
    )


def _family_visible_burden_cost(
    family: SoftControlFamily,
    *,
    executive_state: ReferenceExecutiveState,
) -> float:
    return min(
        1.0,
        _VISIBLE_BURDEN_FAMILY_COSTS[family]
        * executive_state.control_allocation.visible_burden_scale,
    )


def rejected_cheaper_families(
    scorecard: AllocationScorecard,
    *,
    selected_family: SoftControlFamily,
) -> tuple[str, ...]:
    if not isinstance(scorecard, AllocationScorecard):
        actual_type = type(scorecard).__name__
        raise TypeError(
            "rejected_cheaper_families.scorecard must be AllocationScorecard, "
            f"got {actual_type}."
        )
    if not isinstance(selected_family, SoftControlFamily):
        actual_type = type(selected_family).__name__
        raise TypeError(
            "rejected_cheaper_families.selected_family must be SoftControlFamily, "
            f"got {actual_type}."
        )

    selected_burden = _FAMILY_RELATIVE_BURDEN[selected_family]
    cheaper: list[str] = []
    for score in scorecard.scores:
        if score.family is selected_family or not score.admissible:
            continue
        if _FAMILY_RELATIVE_BURDEN[score.family] < selected_burden:
            cheaper.append(score.family.value)
    return tuple(cheaper)


__all__ = [
    "ReferenceSoftControlSelection",
    "build_allocation_diagnostics_payload",
    "build_reference_allocation_scorecard",
    "compute_reference_activation_threshold",
    "compute_reference_chi_t",
    "build_reference_online_score_components",
    "compute_reference_alpha_t",
    "rejected_cheaper_families",
    "select_reference_soft_control",
]
