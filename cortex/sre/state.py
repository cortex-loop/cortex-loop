"""Bounded software-facing views for the reference executive state."""

from __future__ import annotations

from dataclasses import dataclass, field
from numbers import Real

from .brake import BrakeState
from .families import SoftControlFamily
from .goals import GoalContinuityView
from .opportunities import PROBE_RESULT_CLASSES
from .uncertainty import UncertaintyEstimate

_EXPLAINABILITY_PROFILES = frozenset({"minimal", "focused", "structured"})

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
    feedback_pressure_tags: frozenset[str] = field(default_factory=frozenset)
    probe_backed_families: frozenset[SoftControlFamily] = field(default_factory=frozenset)
    productive_exploration_bonus: float = 0.0
    oscillation_penalty: float = 0.0
    host_friction_level: float = 0.0
    visible_burden_scale: float = 1.0
    explainability_profile: str = "minimal"
    recent_probe_result_class: str | None = None

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
        if any(not tag.strip() for tag in self.feedback_pressure_tags):
            raise ValueError(
                "ReferenceControlAllocationView.feedback_pressure_tags must contain only "
                "non-empty values after trimming."
            )
        if any(
            not isinstance(family, SoftControlFamily)
            for family in self.probe_backed_families
        ):
            raise TypeError(
                "ReferenceControlAllocationView.probe_backed_families must contain only "
                "SoftControlFamily instances."
            )
        for field_name in (
            "productive_exploration_bonus",
            "oscillation_penalty",
            "host_friction_level",
            "visible_burden_scale",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, Real):
                actual_type = type(value).__name__
                raise TypeError(
                    f"ReferenceControlAllocationView.{field_name} must be numeric, "
                    f"got {actual_type}."
                )
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(
                    f"ReferenceControlAllocationView.{field_name} must be between 0.0 and 1.0."
                )
        if self.explainability_profile not in _EXPLAINABILITY_PROFILES:
            raise ValueError(
                "ReferenceControlAllocationView.explainability_profile must be one of "
                f"{sorted(_EXPLAINABILITY_PROFILES)!r}."
            )
        if (
            self.recent_probe_result_class is not None
            and self.recent_probe_result_class not in PROBE_RESULT_CLASSES
        ):
            raise ValueError(
                "ReferenceControlAllocationView.recent_probe_result_class must be a canonical probe result class or None."
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

    def __post_init__(self) -> None:
        if not isinstance(self.goal_continuity, GoalContinuityView):
            actual_type = type(self.goal_continuity).__name__
            raise TypeError(
                "ReferenceExecutiveState.goal_continuity must be GoalContinuityView, "
                f"got {actual_type}."
            )
        if not isinstance(
            self.uncertainty_monitoring,
            ReferenceUncertaintyMonitoringView,
        ):
            actual_type = type(self.uncertainty_monitoring).__name__
            raise TypeError(
                "ReferenceExecutiveState.uncertainty_monitoring must be "
                f"ReferenceUncertaintyMonitoringView, got {actual_type}."
            )
        if not isinstance(self.mode_and_gating, ReferenceModeAndGatingView):
            actual_type = type(self.mode_and_gating).__name__
            raise TypeError(
                "ReferenceExecutiveState.mode_and_gating must be "
                f"ReferenceModeAndGatingView, got {actual_type}."
            )
        if not isinstance(
            self.control_allocation,
            ReferenceControlAllocationView,
        ):
            actual_type = type(self.control_allocation).__name__
            raise TypeError(
                "ReferenceExecutiveState.control_allocation must be "
                f"ReferenceControlAllocationView, got {actual_type}."
            )
        if not isinstance(self.brake, ReferenceBrakeView):
            actual_type = type(self.brake).__name__
            raise TypeError(
                "ReferenceExecutiveState.brake must be ReferenceBrakeView, "
                f"got {actual_type}."
            )


__all__ = [
    "ReferenceBrakeView",
    "ReferenceControlAllocationView",
    "ReferenceExecutiveState",
    "ReferenceGoalContinuityView",
    "ReferenceModeAndGatingView",
    "ReferenceUncertaintyMonitoringView",
]
