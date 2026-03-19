"""Bounded software-facing views for the reference executive state."""

from __future__ import annotations

from dataclasses import dataclass, field

from .families import SoftControlFamily
from .brake import BrakeState
from .goals import GoalContinuityView
from .uncertainty import UncertaintyEstimate

ReferenceGoalContinuityView = GoalContinuityView


@dataclass(frozen=True, slots=True)
class ReferenceUncertaintyMonitoringView:
    classwise_uncertainty: tuple[UncertaintyEstimate, ...] = field(default_factory=tuple)
    contradiction_spike_flags: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if any(
            not isinstance(estimate, UncertaintyEstimate)
            for estimate in self.classwise_uncertainty
        ):
            raise TypeError(
                "ReferenceUncertaintyMonitoringView.classwise_uncertainty must "
                "contain only UncertaintyEstimate instances."
            )
        if any(not flag.strip() for flag in self.contradiction_spike_flags):
            raise ValueError(
                "ReferenceUncertaintyMonitoringView.contradiction_spike_flags must "
                "contain only non-empty values after trimming."
            )


@dataclass(frozen=True, slots=True)
class ReferenceModeAndGatingView:
    mode_tag: str
    family_mask: frozenset[SoftControlFamily] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if not self.mode_tag.strip():
            raise ValueError(
                "ReferenceModeAndGatingView.mode_tag must be non-empty after trimming."
            )
        if any(not isinstance(family, SoftControlFamily) for family in self.family_mask):
            raise TypeError(
                "ReferenceModeAndGatingView.family_mask must contain only "
                "SoftControlFamily instances."
            )


@dataclass(frozen=True, slots=True)
class ReferenceControlAllocationView:
    budget_band: str
    top_family_set: frozenset[SoftControlFamily] = field(default_factory=frozenset)
    host_friction_tags: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True, slots=True)
class ReferenceBrakeView:
    brake_state: BrakeState
    dominant_cause_family: SoftControlFamily | None = None


@dataclass(frozen=True, slots=True)
class ReferenceExecutiveState:
    goal_continuity: GoalContinuityView
    uncertainty_monitoring: ReferenceUncertaintyMonitoringView
    mode_and_gating: ReferenceModeAndGatingView
    control_allocation: ReferenceControlAllocationView
    brake: ReferenceBrakeView


__all__ = [
    "ReferenceBrakeView",
    "ReferenceControlAllocationView",
    "ReferenceExecutiveState",
    "ReferenceGoalContinuityView",
    "ReferenceModeAndGatingView",
    "ReferenceUncertaintyMonitoringView",
]
