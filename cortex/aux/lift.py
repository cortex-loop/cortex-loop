"""Support-side AUX lift evaluation over fixed quality and burden metrics."""

from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite
from numbers import Real

from cortex.core.envelopes import MetadataField

from .cost import AuxBurdenReport
from .geometry import AuxGeometryReport


AUX_LIFT_DIRECTIONS = {
    "retrieval_usefulness": "higher_is_better",
    "branch_resume_fidelity": "higher_is_better",
    "uncertainty_brake_diagnostic_lift": "higher_is_better",
    "contradiction_preserving_clustering_quality": "higher_is_better",
    "burden_overhead_cost": "lower_is_better",
}

QUALITY_METRIC_TAGS = frozenset(
    tag for tag in AUX_LIFT_DIRECTIONS if tag != "burden_overhead_cost"
)


def _validate_metric_value(value: float, *, field_name: str) -> None:
    if isinstance(value, bool):
        raise TypeError(f"{field_name} must be numeric, got bool.")
    if not isinstance(value, Real):
        actual_type = type(value).__name__
        raise TypeError(f"{field_name} must be numeric, got {actual_type}.")
    if not isfinite(value):
        raise ValueError(f"{field_name} must be finite.")
    if value < 0:
        raise ValueError(f"{field_name} must be non-negative.")


def _validate_metadata(
    metadata: tuple[MetadataField, ...],
    *,
    field_name: str,
) -> None:
    if not isinstance(metadata, tuple):
        actual_type = type(metadata).__name__
        raise TypeError(f"{field_name} must be tuple[MetadataField, ...], got {actual_type}.")
    if any(not isinstance(item, MetadataField) for item in metadata):
        raise TypeError(f"{field_name} must contain only MetadataField instances.")


def total_aux_burden(burden: AuxBurdenReport) -> float:
    if not isinstance(burden, AuxBurdenReport):
        actual_type = type(burden).__name__
        raise TypeError(f"total_aux_burden() requires AuxBurdenReport, got {actual_type}.")
    return float(
        burden.compute_overhead
        + burden.memory_overhead
        + burden.latency_overhead
        + burden.environment_query_cost
        + burden.retrieval_cost
        + burden.intervention_burden
    )


@dataclass(frozen=True, slots=True)
class AuxLiftMetric:
    metric_tag: str
    baseline_value: float
    aux_value: float
    delta_value: float
    direction: str
    improved: bool

    def __post_init__(self) -> None:
        if self.metric_tag not in AUX_LIFT_DIRECTIONS:
            raise ValueError(
                "AuxLiftMetric.metric_tag must be one of the fixed AUX lift metrics.",
            )
        _validate_metric_value(
            self.baseline_value,
            field_name="AuxLiftMetric.baseline_value",
        )
        _validate_metric_value(
            self.aux_value,
            field_name="AuxLiftMetric.aux_value",
        )
        if not isinstance(self.delta_value, Real) or not isfinite(self.delta_value):
            raise ValueError("AuxLiftMetric.delta_value must be finite.")
        if self.direction != AUX_LIFT_DIRECTIONS[self.metric_tag]:
            raise ValueError(
                "AuxLiftMetric.direction must match the fixed metric direction map.",
            )
        if not isinstance(self.improved, bool):
            actual_type = type(self.improved).__name__
            raise TypeError(
                f"AuxLiftMetric.improved must be bool, got {actual_type}.",
            )


@dataclass(frozen=True, slots=True)
class AuxLiftReport:
    geometry_report: AuxGeometryReport
    metrics: tuple[AuxLiftMetric, ...]
    burden: AuxBurdenReport
    retention_recommendation: str
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not isinstance(self.geometry_report, AuxGeometryReport):
            actual_type = type(self.geometry_report).__name__
            raise TypeError(
                "AuxLiftReport.geometry_report must be AuxGeometryReport, "
                f"got {actual_type}.",
            )
        if any(not isinstance(metric, AuxLiftMetric) for metric in self.metrics):
            raise TypeError("AuxLiftReport.metrics must contain only AuxLiftMetric instances.")
        metric_tags = {metric.metric_tag for metric in self.metrics}
        if metric_tags != set(AUX_LIFT_DIRECTIONS):
            raise ValueError(
                "AuxLiftReport.metrics must cover the full fixed AUX metric set exactly once.",
            )
        if not isinstance(self.burden, AuxBurdenReport):
            actual_type = type(self.burden).__name__
            raise TypeError(
                "AuxLiftReport.burden must be AuxBurdenReport, "
                f"got {actual_type}.",
            )
        if self.retention_recommendation not in {
            "keep-experimental",
            "observe",
            "prune-candidate",
        }:
            raise ValueError(
                "AuxLiftReport.retention_recommendation must be a fixed AUX retention label.",
            )
        _validate_metadata(self.metadata, field_name="AuxLiftReport.metadata")


def _build_metric(metric_tag: str, baseline_value: float, aux_value: float) -> AuxLiftMetric:
    direction = AUX_LIFT_DIRECTIONS[metric_tag]
    delta_value = float(aux_value) - float(baseline_value)
    improved = delta_value > 0 if direction == "higher_is_better" else delta_value < 0
    return AuxLiftMetric(
        metric_tag=metric_tag,
        baseline_value=float(baseline_value),
        aux_value=float(aux_value),
        delta_value=delta_value,
        direction=direction,
        improved=improved,
    )


def _choose_retention_recommendation(metrics: tuple[AuxLiftMetric, ...]) -> str:
    quality_improved = any(
        metric.improved for metric in metrics if metric.metric_tag in QUALITY_METRIC_TAGS
    )
    burden_improved = next(
        metric.improved for metric in metrics if metric.metric_tag == "burden_overhead_cost"
    )
    if quality_improved:
        return "keep-experimental"
    if burden_improved:
        return "observe"
    return "prune-candidate"


def build_aux_lift_report(
    geometry_report: AuxGeometryReport,
    *,
    retrieval_usefulness: tuple[float, float],
    branch_resume_fidelity: tuple[float, float],
    uncertainty_brake_diagnostic_lift: tuple[float, float],
    contradiction_preserving_clustering_quality: tuple[float, float],
    burden_overhead_cost: tuple[float, float] | None = None,
    metadata: tuple[MetadataField, ...] = (),
) -> AuxLiftReport:
    if not isinstance(geometry_report, AuxGeometryReport):
        actual_type = type(geometry_report).__name__
        raise TypeError(
            "build_aux_lift_report() requires AuxGeometryReport, "
            f"got {actual_type}.",
        )
    if burden_overhead_cost is None:
        burden_overhead_cost = (0.0, total_aux_burden(geometry_report.burden))

    metrics = (
        _build_metric("retrieval_usefulness", *retrieval_usefulness),
        _build_metric("branch_resume_fidelity", *branch_resume_fidelity),
        _build_metric(
            "uncertainty_brake_diagnostic_lift",
            *uncertainty_brake_diagnostic_lift,
        ),
        _build_metric(
            "contradiction_preserving_clustering_quality",
            *contradiction_preserving_clustering_quality,
        ),
        _build_metric("burden_overhead_cost", *burden_overhead_cost),
    )
    return AuxLiftReport(
        geometry_report=geometry_report,
        metrics=metrics,
        burden=geometry_report.burden,
        retention_recommendation=_choose_retention_recommendation(metrics),
        metadata=metadata,
    )


__all__ = [
    "AUX_LIFT_DIRECTIONS",
    "AuxLiftMetric",
    "AuxLiftReport",
    "build_aux_lift_report",
    "total_aux_burden",
]
