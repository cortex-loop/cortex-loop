"""Bounded software-facing views for the reference executive state."""

from __future__ import annotations

from dataclasses import dataclass, field
from numbers import Real
from typing import TYPE_CHECKING

from .brake import BrakeState, BrakeTonic
from .debt_control import DebtControlPressure
from .families import SoftControlFamily
from .goals import GoalContinuityView
from .opportunities import PROBE_RESULT_CLASSES
from .uncertainty import UncertaintyEstimate

if TYPE_CHECKING:
    from .operator_routing import OperatorTaskMode

_EXPLAINABILITY_PROFILES = frozenset({"minimal", "focused", "structured"})
_PROBE_PATH_STATES = frozenset({"available", "unavailable", "absent"})
_ANTI_THRASH_STATES = frozenset({"inactive", "taxed", "reopened"})
_RISK_ADJUSTMENT_SIGNS = frozenset({"fn-heavy", "fp-heavy", "balanced"})

ReferenceGoalContinuityView = GoalContinuityView


@dataclass(frozen=True, slots=True)
class RiskWeight:
    """Bounded asymmetric-cost carrier for false-negative vs false-positive checking."""

    fn_cost_weight: float = 0.0
    fp_cost_weight: float = 0.0
    dominant_risk_source: str | None = None
    adjustment_sign: str = "balanced"

    def __post_init__(self) -> None:
        for field_name in ("fn_cost_weight", "fp_cost_weight"):
            value = getattr(self, field_name)
            if not isinstance(value, Real):
                actual_type = type(value).__name__
                raise TypeError(
                    f"RiskWeight.{field_name} must be numeric, got {actual_type}."
                )
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(
                    f"RiskWeight.{field_name} must be between 0.0 and 1.0."
                )
        if self.adjustment_sign not in _RISK_ADJUSTMENT_SIGNS:
            raise ValueError(
                f"RiskWeight.adjustment_sign must be one of {sorted(_RISK_ADJUSTMENT_SIGNS)!r}."
            )
        if self.dominant_risk_source is not None and not (
            isinstance(self.dominant_risk_source, str)
            and self.dominant_risk_source.strip()
        ):
            raise ValueError(
                "RiskWeight.dominant_risk_source must be non-empty after trimming when provided."
            )


def _default_task_mode() -> "OperatorTaskMode":
    from .operator_routing import OperatorTaskMode

    return OperatorTaskMode.EXECUTE


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
    task_mode: "OperatorTaskMode" = field(default_factory=_default_task_mode)
    family_mask: frozenset[SoftControlFamily] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        from .operator_routing import OperatorTaskMode

        if not isinstance(self.task_mode, OperatorTaskMode):
            actual_type = type(self.task_mode).__name__
            raise TypeError(
                "ReferenceModeAndGatingView.task_mode must be OperatorTaskMode, "
                f"got {actual_type}."
            )
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
    anti_thrash_state: str = "inactive"
    repetition_tax: float = 0.0
    repetition_target_family: SoftControlFamily | None = None
    anti_thrash_reason_tags: frozenset[str] = field(default_factory=frozenset)
    explainability_profile: str = "minimal"
    probe_path_state: str = "absent"
    probe_unavailable_reason: str | None = None
    recent_probe_result_class: str | None = None
    risk_weight: RiskWeight = field(default_factory=RiskWeight)
    debt_control: DebtControlPressure = field(default_factory=DebtControlPressure)

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
            "repetition_tax",
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
        if self.anti_thrash_state not in _ANTI_THRASH_STATES:
            raise ValueError(
                "ReferenceControlAllocationView.anti_thrash_state must be one of "
                f"{sorted(_ANTI_THRASH_STATES)!r}."
            )
        if self.repetition_target_family is not None and not isinstance(
            self.repetition_target_family, SoftControlFamily
        ):
            raise TypeError(
                "ReferenceControlAllocationView.repetition_target_family must contain only "
                "SoftControlFamily instances when provided."
            )
        if any(not tag.strip() for tag in self.anti_thrash_reason_tags):
            raise ValueError(
                "ReferenceControlAllocationView.anti_thrash_reason_tags must contain only "
                "non-empty values after trimming."
            )
        if self.anti_thrash_state == "taxed" and self.repetition_tax <= 0.0:
            raise ValueError(
                "ReferenceControlAllocationView.repetition_tax must be positive when anti_thrash_state is `taxed`."
            )
        if self.anti_thrash_state in {"inactive", "reopened"} and self.repetition_tax != 0.0:
            raise ValueError(
                "ReferenceControlAllocationView.repetition_tax must be 0.0 when anti_thrash_state is not `taxed`."
            )
        if self.repetition_tax > 0.0 and self.repetition_target_family is None:
            raise ValueError(
                "ReferenceControlAllocationView.repetition_target_family is required when repetition_tax is positive."
            )
        if self.explainability_profile not in _EXPLAINABILITY_PROFILES:
            raise ValueError(
                "ReferenceControlAllocationView.explainability_profile must be one of "
                f"{sorted(_EXPLAINABILITY_PROFILES)!r}."
            )
        if self.probe_path_state not in _PROBE_PATH_STATES:
            raise ValueError(
                "ReferenceControlAllocationView.probe_path_state must be one of "
                f"{sorted(_PROBE_PATH_STATES)!r}."
            )
        if self.probe_unavailable_reason is not None and not (
            isinstance(self.probe_unavailable_reason, str)
            and self.probe_unavailable_reason.strip()
        ):
            raise ValueError(
                "ReferenceControlAllocationView.probe_unavailable_reason must be "
                "non-empty after trimming when provided."
            )
        if self.probe_path_state == "unavailable" and self.probe_unavailable_reason is None:
            raise ValueError(
                "ReferenceControlAllocationView.probe_unavailable_reason is required "
                "when probe_path_state is `unavailable`."
            )
        if self.probe_path_state != "unavailable" and self.probe_unavailable_reason is not None:
            raise ValueError(
                "ReferenceControlAllocationView.probe_unavailable_reason is only valid "
                "when probe_path_state is `unavailable`."
            )
        if (
            self.recent_probe_result_class is not None
            and self.recent_probe_result_class not in PROBE_RESULT_CLASSES
        ):
            raise ValueError(
                "ReferenceControlAllocationView.recent_probe_result_class must be a canonical probe result class or None."
            )
        if not isinstance(self.risk_weight, RiskWeight):
            actual_type = type(self.risk_weight).__name__
            raise TypeError(
                "ReferenceControlAllocationView.risk_weight must be RiskWeight, "
                f"got {actual_type}."
            )
        if not isinstance(self.debt_control, DebtControlPressure):
            actual_type = type(self.debt_control).__name__
            raise TypeError(
                "ReferenceControlAllocationView.debt_control must be "
                f"DebtControlPressure, got {actual_type}."
            )


@dataclass(frozen=True, slots=True)
class ReferenceBrakeView:
    brake_state: BrakeState
    dominant_cause_family: SoftControlFamily | None = None
    tonic: BrakeTonic | None = None

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
        if self.tonic is not None and not isinstance(self.tonic, BrakeTonic):
            actual_type = type(self.tonic).__name__
            raise TypeError(
                f"ReferenceBrakeView.tonic must be BrakeTonic when provided, got {actual_type}."
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
    "RiskWeight",
]
