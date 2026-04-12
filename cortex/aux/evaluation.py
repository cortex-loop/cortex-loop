"""Deterministic evaluation-first AUX runners over lawful public support state."""

from __future__ import annotations

from dataclasses import dataclass

from cortex.core.support import SupportSnapshot

from .geometry import AuxGeometryReport, build_aux_geometry_report
from .lift import AuxLiftReport, build_aux_lift_report


@dataclass(frozen=True, slots=True)
class AuxEvaluationResult:
    geometry_report: AuxGeometryReport
    lift_report: AuxLiftReport


def _average_match_score(match_scores: tuple[object, ...]) -> float:
    if not match_scores:
        return 0.0
    total = sum(float(getattr(match, "score")) for match in match_scores)
    return total / len(match_scores)


def evaluate_aux_support_snapshot(
    snapshot: SupportSnapshot,
) -> AuxEvaluationResult:
    if not isinstance(snapshot, SupportSnapshot):
        actual_type = type(snapshot).__name__
        raise TypeError(
            "evaluate_aux_support_snapshot() requires SupportSnapshot, "
            f"got {actual_type}.",
        )

    geometry_report = build_aux_geometry_report(snapshot)
    retrieval_baseline = 0.10 if snapshot.trace.candidate_refs else 0.0
    branch_baseline = 0.15 if snapshot.session.branch_registry else 0.0
    uncertainty_baseline = 0.15 if snapshot.trace.degradation_records else 0.0
    contradiction_baseline = 0.15 if snapshot.trace.degradation_records else 0.0
    uncertainty_aux_value = min(
        1.0,
        0.15 * len(geometry_report.uncertainty_brake_hints),
    )
    contradiction_aux_value = min(
        1.0,
        0.25 * len(geometry_report.contradiction_clusters),
    )
    lift_report = build_aux_lift_report(
        geometry_report,
        retrieval_usefulness=(
            retrieval_baseline,
            _average_match_score(geometry_report.retrieval_shadow_candidates),
        ),
        branch_resume_fidelity=(
            branch_baseline,
            _average_match_score(geometry_report.branch_resume_matches),
        ),
        uncertainty_brake_diagnostic_lift=(
            uncertainty_baseline,
            uncertainty_aux_value,
        ),
        contradiction_preserving_clustering_quality=(
            contradiction_baseline,
            contradiction_aux_value,
        ),
    )
    return AuxEvaluationResult(
        geometry_report=geometry_report,
        lift_report=lift_report,
    )


__all__ = [
    "AuxEvaluationResult",
    "evaluate_aux_support_snapshot",
]
