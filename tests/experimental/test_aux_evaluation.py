"""Integration-lite tests for deterministic AUX evaluation runners."""

from __future__ import annotations

import pytest

from cortex.aux.evaluation import AuxEvaluationResult, evaluate_aux_support_snapshot
from cortex.core.support import SupportState

from ._aux_test_support import make_support_snapshot


def test_evaluate_aux_support_snapshot_emits_geometry_and_lift_reports_with_quality_improvement() -> None:
    result = evaluate_aux_support_snapshot(make_support_snapshot())

    assert isinstance(result, AuxEvaluationResult)
    assert result.geometry_report.retrieval_shadow_candidates
    assert result.geometry_report.branch_resume_matches
    assert result.geometry_report.contradiction_clusters
    assert result.lift_report.retention_recommendation == "keep-experimental"
    metric_map = {metric.metric_tag: metric for metric in result.lift_report.metrics}
    assert metric_map["retrieval_usefulness"].improved is True
    assert metric_map["branch_resume_fidelity"].improved is True
    assert metric_map["uncertainty_brake_diagnostic_lift"].improved is True
    assert metric_map["contradiction_preserving_clustering_quality"].improved is True


def test_evaluate_aux_support_snapshot_requires_support_snapshot() -> None:
    with pytest.raises(TypeError, match="SupportSnapshot"):
        evaluate_aux_support_snapshot(SupportState())
