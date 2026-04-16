"""Compact SRE executive summary carrier over bounded observable control signals."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from numbers import Real
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .operator_routing import OperatorTaskMode


def _default_task_mode() -> "OperatorTaskMode":
    from .operator_routing import OperatorTaskMode

    return OperatorTaskMode.EXECUTE


@dataclass(frozen=True, slots=True)
class ExecutiveSignalSummaryInputs:
    task_mode: "OperatorTaskMode"
    uncertainty: float
    quota_pressure: float
    continuity_demand: float
    previous_same_host_run_failed_before_completion: bool
    recent_product_failure_class: str | None
    recent_probe_failure_class: str | None
    recent_warning_bearing_success_present: bool
    verification_required: bool

    def __post_init__(self) -> None:
        from .operator_routing import OperatorTaskMode

        if not isinstance(self.task_mode, OperatorTaskMode):
            actual_type = type(self.task_mode).__name__
            raise TypeError(
                "ExecutiveSignalSummaryInputs.task_mode must be OperatorTaskMode, "
                f"got {actual_type}."
            )
        for field_name in ("uncertainty", "quota_pressure", "continuity_demand"):
            value = getattr(self, field_name)
            if not isinstance(value, Real):
                actual_type = type(value).__name__
                raise TypeError(
                    f"ExecutiveSignalSummaryInputs.{field_name} must be numeric, got {actual_type}."
                )
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(
                    f"ExecutiveSignalSummaryInputs.{field_name} must be between 0.0 and 1.0."
                )
        for field_name in (
            "previous_same_host_run_failed_before_completion",
            "recent_warning_bearing_success_present",
            "verification_required",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, bool):
                actual_type = type(value).__name__
                raise TypeError(
                    f"ExecutiveSignalSummaryInputs.{field_name} must be bool, got {actual_type}."
                )
        for field_name in ("recent_product_failure_class", "recent_probe_failure_class"):
            value = getattr(self, field_name)
            if value is not None and not isinstance(value, str):
                actual_type = type(value).__name__
                raise TypeError(
                    f"ExecutiveSignalSummaryInputs.{field_name} must be str | None, got {actual_type}."
                )


@dataclass(frozen=True, slots=True)
class ExecutiveSignalSummary:
    uncertainty: float
    repeated_failure_pressure: float
    quota_pressure: float
    continuity_demand: float
    novelty_pressure: float
    verification_conflict_pressure: float
    task_mode: "OperatorTaskMode" = field(default_factory=_default_task_mode)

    def __post_init__(self) -> None:
        from .operator_routing import OperatorTaskMode

        if not isinstance(self.task_mode, OperatorTaskMode):
            actual_type = type(self.task_mode).__name__
            raise TypeError(
                "ExecutiveSignalSummary.task_mode must be OperatorTaskMode, "
                f"got {actual_type}."
            )
        for field_name in (
            "uncertainty",
            "repeated_failure_pressure",
            "quota_pressure",
            "continuity_demand",
            "novelty_pressure",
            "verification_conflict_pressure",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, Real):
                actual_type = type(value).__name__
                raise TypeError(
                    f"ExecutiveSignalSummary.{field_name} must be numeric, got {actual_type}."
                )
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(
                    f"ExecutiveSignalSummary.{field_name} must be between 0.0 and 1.0."
                )

    def as_vector(self) -> tuple[float, ...]:
        return (
            float(self.uncertainty),
            float(self.repeated_failure_pressure),
            float(self.quota_pressure),
            float(self.continuity_demand),
            float(self.novelty_pressure),
            float(self.verification_conflict_pressure),
        )

    def as_payload(self) -> dict[str, float]:
        return {
            field_name: round(float(value), 4)
            for field_name, value in asdict(self).items()
            if field_name != "task_mode"
        }


_NON_LIMIT_FAILURE_CLASSES = {
    "quota_exhausted",
    "capacity_exhausted",
    "continuity_rollout_missing",
    None,
}


def build_executive_signal_summary(
    inputs: ExecutiveSignalSummaryInputs,
) -> ExecutiveSignalSummary:
    from .operator_routing import OperatorTaskMode

    if not isinstance(inputs, ExecutiveSignalSummaryInputs):
        actual_type = type(inputs).__name__
        raise TypeError(
            "build_executive_signal_summary.inputs must be ExecutiveSignalSummaryInputs, "
            f"got {actual_type}."
        )

    non_limit_failure = inputs.recent_product_failure_class not in _NON_LIMIT_FAILURE_CLASSES
    repeated_failure_pressure = (
        0.75
        if inputs.previous_same_host_run_failed_before_completion
        else 0.55
        if non_limit_failure
        else 0.35
        if inputs.recent_warning_bearing_success_present
        else 0.0
    )
    novelty_pressure = (
        0.70
        if inputs.task_mode is OperatorTaskMode.INSPECT
        else 0.55
        if inputs.previous_same_host_run_failed_before_completion
        else 0.35
        if non_limit_failure
        else 0.20
    )
    verification_conflict_pressure = (
        0.65
        if inputs.verification_required and non_limit_failure
        else 0.45
        if inputs.verification_required and inputs.recent_warning_bearing_success_present
        else 0.15
        if inputs.verification_required
        else 0.0
    )
    return ExecutiveSignalSummary(
        task_mode=inputs.task_mode,
        uncertainty=float(inputs.uncertainty),
        repeated_failure_pressure=float(repeated_failure_pressure),
        quota_pressure=float(inputs.quota_pressure),
        continuity_demand=float(inputs.continuity_demand),
        novelty_pressure=float(novelty_pressure),
        verification_conflict_pressure=float(verification_conflict_pressure),
    )


__all__ = [
    "ExecutiveSignalSummary",
    "ExecutiveSignalSummaryInputs",
    "build_executive_signal_summary",
]
