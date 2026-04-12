"""Time-separated AUX corpus proof over source-to-target support scenarios."""

from __future__ import annotations

import pytest

from cortex.aux.evaluation import (
    AuxCorpusCaseResult,
    AuxCorpusEvaluationResult,
    AuxCorpusMetricSummary,
    AuxTemporalScenario,
    evaluate_aux_support_corpus,
)
from cortex.sre.families import SoftControlFamily

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


def test_aux_corpus_case_result_carries_support_priors_and_failure_reasons() -> None:
    result = evaluate_aux_support_corpus(make_aux_temporal_corpus())

    case_map = {case.scenario_id: case for case in result.case_results}
    burden_case = case_map["burden-heavy-counterexample"]
    no_lift_case = case_map["no-lift-counterexample"]

    assert isinstance(burden_case, AuxCorpusCaseResult)
    assert burden_case.support_memory_priors.active is False
    assert "q_mem-penalty:burden" in burden_case.support_memory_priors.score_for(
        SoftControlFamily.CHECK
    ).reason_tags
    assert burden_case.publication.publication_tags >= {
        "aux/offline-publication",
        "aux/temporal-corpus",
    }
    assert burden_case.augmented_target.core_snapshot is burden_case.geometry_report.source_snapshot
    assert burden_case.augmented_target.auxiliary_support.derived_tags >= {
        "aux/offline-publication",
        "aux/temporal-corpus",
    }
    assert no_lift_case.failure_reasons == (
        "no quality lift over baseline target",
        "burden increased without offsetting quality lift",
    )


def test_aux_corpus_metric_summaries_cover_fixed_metrics_and_case_accounting() -> None:
    result = evaluate_aux_support_corpus(make_aux_temporal_corpus())

    assert all(isinstance(summary, AuxCorpusMetricSummary) for summary in result.metric_summaries)
    assert {summary.metric_tag for summary in result.metric_summaries} == {
        "retrieval_usefulness",
        "branch_resume_fidelity",
        "uncertainty_brake_diagnostic_lift",
        "contradiction_preserving_clustering_quality",
        "burden_overhead_cost",
    }
    for summary in result.metric_summaries:
        assert summary.case_count == len(result.case_results)
        assert summary.improved_case_count == len(summary.improved_case_ids)
        assert summary.regressed_case_count == len(summary.regressed_case_ids)

    contradiction_summary = next(
        summary
        for summary in result.metric_summaries
        if summary.metric_tag == "contradiction_preserving_clustering_quality"
    )
    burden_summary = next(
        summary
        for summary in result.metric_summaries
        if summary.metric_tag == "burden_overhead_cost"
    )
    assert contradiction_summary.regressed_case_count == 0
    assert burden_summary.improved_case_count == 0
    assert burden_summary.regressed_case_count >= 1


def test_evaluate_aux_support_corpus_can_recommend_prune_candidate_for_weak_cases() -> None:
    result = evaluate_aux_support_corpus(make_aux_prune_candidate_corpus())

    assert result.acceptance_passed is False
    assert result.retention_recommendation == "prune-candidate"
    assert "fewer than 3 fixed metrics improved across corpus" in result.failure_reasons
    assert any(case.failure_reasons for case in result.case_results)


@pytest.mark.parametrize(
    ("value", "expected_error", "message"),
    (
        ((), ValueError, "requires at least one scenario"),
        ("not-a-tuple", TypeError, "requires tuple\\[AuxTemporalScenario, ...\\]"),
        ((object(),), TypeError, "requires only AuxTemporalScenario instances"),
    ),
)
def test_evaluate_aux_support_corpus_validates_input_shape(
    value: object,
    expected_error: type[Exception],
    message: str,
) -> None:
    with pytest.raises(expected_error, match=message):
        evaluate_aux_support_corpus(value)  # type: ignore[arg-type]
