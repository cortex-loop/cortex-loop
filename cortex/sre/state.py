"""Bounded software-facing views for the reference executive state."""

from __future__ import annotations

from dataclasses import dataclass, field

from .families import SoftControlFamily
from .brake import BrakeState
from .uncertainty import UncertaintyEstimate


@dataclass(frozen=True, slots=True)
class ReferenceGoalContinuityView:
    main_goal_ref: str | None = None
    active_track_ref: str | None = None
    pending_goal_refs: tuple[str, ...] = field(default_factory=tuple)
    resume_anchor_available: bool = False


@dataclass(frozen=True, slots=True)
class ReferenceUncertaintyMonitoringView:
    classwise_uncertainty: tuple[UncertaintyEstimate, ...] = field(default_factory=tuple)
    contradiction_spike_flags: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True, slots=True)
class ReferenceModeAndGatingView:
    mode_tag: str
    family_mask: frozenset[SoftControlFamily] = field(default_factory=frozenset)


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
    goal_continuity: ReferenceGoalContinuityView
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
