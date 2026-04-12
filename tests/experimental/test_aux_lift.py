"""Focused tests for AUX lift evaluation and retention recommendations."""

from __future__ import annotations

import pytest

from cortex.aux.cost import AuxBurdenReport
from cortex.aux.geometry import build_aux_geometry_report
from cortex.aux.lift import (
    AuxLiftReport,
    build_aux_lift_report,
    total_aux_burden,
)

from ._aux_test_support import make_support_snapshot


def test_build_aux_lift_report_keeps_experimental_when_quality_metric_improves() -> None:
    report = build_aux_geometry_report(
        make_support_snapshot(),
        burden=AuxBurdenReport(
            compute_overhead=0.1,
            retrieval_cost=0.2,
            intervention_burden=0.1,
        ),
    )

    lift = build_aux_lift_report(
        report,
        retrieval_usefulness=(0.3, 0.7),
        branch_resume_fidelity=(0.4, 0.6),
        uncertainty_brake_diagnostic_lift=(0.2, 0.5),
        contradiction_preserving_clustering_quality=(0.2, 0.45),
    )

    assert isinstance(lift, AuxLiftReport)
    assert lift.retention_recommendation == "keep-experimental"
    assert total_aux_burden(report.burden) == pytest.approx(0.4)
    metric_map = {metric.metric_tag: metric for metric in lift.metrics}
    assert metric_map["retrieval_usefulness"].improved is True
    assert metric_map["burden_overhead_cost"].aux_value == pytest.approx(0.4)
    assert metric_map["burden_overhead_cost"].improved is False


def test_build_aux_lift_report_marks_prune_candidate_when_quality_does_not_improve() -> None:
    report = build_aux_geometry_report(make_support_snapshot())

    lift = build_aux_lift_report(
        report,
        retrieval_usefulness=(0.5, 0.5),
        branch_resume_fidelity=(0.5, 0.4),
        uncertainty_brake_diagnostic_lift=(0.3, 0.3),
        contradiction_preserving_clustering_quality=(0.6, 0.4),
        burden_overhead_cost=(0.0, 0.0),
    )

    assert lift.retention_recommendation == "prune-candidate"
    assert sum(metric.improved for metric in lift.metrics) == 0


def test_build_aux_lift_report_requires_full_fixed_metric_set_and_non_negative_values() -> None:
    report = build_aux_geometry_report(make_support_snapshot())

    with pytest.raises(ValueError, match="non-negative"):
        build_aux_lift_report(
            report,
            retrieval_usefulness=(0.5, -0.1),
            branch_resume_fidelity=(0.5, 0.5),
            uncertainty_brake_diagnostic_lift=(0.5, 0.5),
            contradiction_preserving_clustering_quality=(0.5, 0.5),
            burden_overhead_cost=(0.0, 0.1),
        )
