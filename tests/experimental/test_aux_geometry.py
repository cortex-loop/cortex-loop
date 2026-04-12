"""Focused tests for evaluation-first AUX geometry reports."""

from __future__ import annotations

import pytest

from cortex.aux.cost import AuxBurdenReport
from cortex.aux.geometry import (
    AuxContradictionCluster,
    AuxGeometryReport,
    AuxMatchScore,
    build_aux_geometry_report,
)
from cortex.core.envelopes import MetadataField
from cortex.core.support import SupportState

from ._aux_test_support import make_support_ref, make_support_snapshot


def test_build_aux_geometry_report_derives_only_support_side_hints_and_preserves_snapshot_truth() -> None:
    snapshot = make_support_snapshot()

    report = build_aux_geometry_report(snapshot)

    assert isinstance(report, AuxGeometryReport)
    assert report.source_snapshot is snapshot
    assert report.retrieval_shadow_candidates
    assert report.branch_resume_matches
    assert report.contradiction_clusters
    assert isinstance(report.burden, AuxBurdenReport)
    assert report.uncertainty_brake_hints == (
        "support-evidence-present",
        "branch-resume-pressure",
        "uncertainty-brake-pressure",
        "continuity-reminder-present",
    )
    assert all(
        "retrieval-shadow" in match.tags for match in report.retrieval_shadow_candidates
    )
    assert all("resume-match" in match.tags for match in report.branch_resume_matches)
    assert report.contradiction_clusters[0].cluster_tag == "host-degraded"

    with pytest.raises(TypeError, match="SupportSnapshot"):
        build_aux_geometry_report(SupportState())


def test_build_aux_geometry_report_accepts_explicit_matches_and_contradiction_clusters() -> None:
    snapshot = make_support_snapshot()
    retrieval_match = AuxMatchScore(
        source_ref=make_support_ref("query", "query-1"),
        candidate_ref=make_support_ref("memory", "memo-1"),
        score=0.9,
        tags=frozenset({"retrieval-shadow"}),
    )
    branch_match = AuxMatchScore(
        source_ref=make_support_ref("branch", "review-track"),
        candidate_ref=make_support_ref("goal", "goal-1"),
        score=0.75,
        tags=frozenset({"resume-match"}),
    )
    cluster = AuxContradictionCluster(
        cluster_tag="cluster-1",
        member_refs=(
            make_support_ref("artifact", "artifact-1"),
            make_support_ref("memory", "memo-1"),
        ),
        contradiction_tags=frozenset({"capability-drift"}),
        notes=("preserve contradiction instead of smoothing",),
        metadata=(MetadataField("source", "aux-eval"),),
    )
    burden = AuxBurdenReport(retrieval_cost=0.4, intervention_burden=0.1)

    report = build_aux_geometry_report(
        snapshot,
        retrieval_shadow_candidates=(retrieval_match,),
        branch_resume_matches=(branch_match,),
        uncertainty_brake_hints=("explicit-hint",),
        contradiction_clusters=(cluster,),
        burden=burden,
        metadata=(MetadataField("report", "geometry"),),
    )

    assert report.retrieval_shadow_candidates[0] is retrieval_match
    assert report.branch_resume_matches[0] is branch_match
    assert report.contradiction_clusters[0] is cluster
    assert report.burden is burden
    assert report.metadata[0].key == "report"
    assert report.uncertainty_brake_hints[-1] == "explicit-hint"


def test_aux_geometry_types_require_typed_support_refs_and_bounded_scores() -> None:
    with pytest.raises(TypeError, match="SupportReference"):
        AuxMatchScore(
            source_ref="query-1",
            candidate_ref=make_support_ref("memory", "memo-1"),
            score=0.5,
        )

    with pytest.raises(ValueError, match="between 0.0 and 1.0"):
        AuxMatchScore(
            source_ref=make_support_ref("query", "query-1"),
            candidate_ref=make_support_ref("memory", "memo-1"),
            score=1.5,
        )

    with pytest.raises(TypeError, match="AuxContradictionCluster.member_refs"):
        AuxContradictionCluster(
            cluster_tag="cluster-1",
            member_refs=("artifact-1",),
        )

    with pytest.raises(TypeError, match="AuxGeometryReport.retrieval_shadow_candidates"):
        AuxGeometryReport(
            source_snapshot=make_support_snapshot(),
            retrieval_shadow_candidates=("not-a-match",),
        )
