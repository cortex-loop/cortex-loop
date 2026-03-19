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

    def __post_init__(self) -> None:
        if not self.budget_band.strip():
            raise ValueError(
                "ReferenceControlAllocationView.budget_band must be non-empty after trimming."
            )
        if any(not isinstance(family, SoftControlFamily) for family in self.top_family_set):
            raise TypeError(
                "ReferenceControlAllocationView.top_family_set must contain only "
                "SoftControlFamily instances."
            )
        if any(not tag.strip() for tag in self.host_friction_tags):
            raise ValueError(
                "ReferenceControlAllocationView.host_friction_tags must contain only "
                "non-empty values after trimming."
            )


@dataclass(frozen=True, slots=True)
class ReferenceBrakeView:
    brake_state: BrakeState
    dominant_cause_family: SoftControlFamily | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.brake_state, BrakeState):
            actual_type = type(self.brake_state).__name__
            raise TypeError(
                "ReferenceBrakeView.brake_state must be BrakeState, "
                f"got {actual_type}."
            )
        if self.dominant_cause_family is not None and not isinstance(
            self.dominant_cause_family, SoftControlFamily
        ):
            actual_type = type(self.dominant_cause_family).__name__
            raise TypeError(
                "ReferenceBrakeView.dominant_cause_family must be SoftControlFamily "
                f"when provided, got {actual_type}."
            )


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
