"""Time-separated AUX corpus proof over source-to-target support scenarios."""

from __future__ import annotations

import pytest

from cortex.aux.evaluation import (
    AuxCorpusEvaluationResult,
    AuxTemporalScenario,
    evaluate_aux_support_corpus,
)

from ._aux_test_support import (
    make_aux_prune_candidate_corpus,
    make_aux_temporal_corpus,
    make_support_snapshot,
)


def test_aux_temporal_scenarios_require_time_separated_source_and_target() -> None:
    snapshot = make_support_snapshot()

    with pytest.raises(ValueError, match="time-separated source and target"):
        AuxTemporalScenario(
            scenario_id="same-snapshot",
            source_snapshots=(snapshot,),
            target_snapshot=snapshot,
        )


def test_evaluate_aux_support_corpus_reports_time_separated_lift_and_acceptance() -> None:
    result = evaluate_aux_support_corpus(make_aux_temporal_corpus())

    assert isinstance(result, AuxCorpusEvaluationResult)
    assert result.acceptance_passed is True
    assert result.retention_recommendation == "keep-experimental"
    assert len(result.case_results) == 6
    assert result.total_burden >= result.worst_case_burden > 0.0

    metric_map = {summary.metric_tag: summary for summary in result.metric_summaries}
    assert metric_map["retrieval_usefulness"].improved_case_count >= 1
    assert metric_map["branch_resume_fidelity"].improved_case_count >= 1
    assert metric_map["uncertainty_brake_diagnostic_lift"].improved_case_count >= 1
    assert metric_map["contradiction_preserving_clustering_quality"].regressed_case_count == 0

    case_map = {case.scenario_id: case for case in result.case_results}
    retrieval_case = case_map["retrieval-reuse"]
    no_lift_case = case_map["no-lift-counterexample"]
    contradiction_case = case_map["contradiction-review"]

    assert retrieval_case.support_memory_priors.active is True
    assert "q_mem:explicit-aux" in retrieval_case.support_memory_priors.appendix_tags
    assert no_lift_case.failure_reasons == (
        "no quality lift over baseline target",
        "burden increased without offsetting quality lift",
    )
    assert contradiction_case.geometry_report.contradiction_clusters
    assert "offline contradiction summary reused on later target" in contradiction_case.geometry_report.contradiction_clusters[0].notes
    assert any(
        ref.reference_kind == "contradiction"
        for ref in contradiction_case.geometry_report.contradiction_clusters[0].member_refs
    )


def test_evaluate_aux_support_corpus_can_recommend_prune_candidate_for_weak_cases() -> None:
    result = evaluate_aux_support_corpus(make_aux_prune_candidate_corpus())

    assert result.acceptance_passed is False
    assert result.retention_recommendation == "prune-candidate"
    assert "fewer than 3 fixed metrics improved across corpus" in result.failure_reasons
    assert any(case.failure_reasons for case in result.case_results)
