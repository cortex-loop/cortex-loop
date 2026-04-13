"""Reference-only replay proof over explicit AUX-owned Q_mem priors."""

from __future__ import annotations

import pytest

from cortex.aux.reference_replay import (
    AuxReferenceReplayCaseResult,
    AuxReferenceReplayEvaluationResult,
    AuxReferenceReplayScenario,
    evaluate_aux_reference_q_mem_replay,
)

from ._aux_test_support import (
    make_aux_reference_replay_corpus,
    make_support_snapshot,
)


def test_aux_reference_replay_scenarios_require_time_separated_support_snapshots_and_reference_state() -> None:
    snapshot = make_support_snapshot()
    scenario = make_aux_reference_replay_corpus()[0]

    with pytest.raises(ValueError, match="time-separated source and target"):
        AuxReferenceReplayScenario(
            scenario_id="same-snapshot",
            source_snapshots=(snapshot,),
            target_snapshot=snapshot,
            executive_state=scenario.executive_state,
            preferred_family=scenario.preferred_family,
            expect_improvement=True,
        )


def test_evaluate_aux_reference_q_mem_replay_reports_reference_only_acceptance_and_failure_labels() -> None:
    result = evaluate_aux_reference_q_mem_replay(make_aux_reference_replay_corpus())

    assert isinstance(result, AuxReferenceReplayEvaluationResult)
    assert result.acceptance_passed is True
    assert result.improved_preferred_family_case_count == 4
    assert result.selected_family_change_case_count == 1
    assert result.negative_case_stable_count == 4
    assert result.counterexample_case_count == 0
    assert result.dominant_failure_label is None
    assert result.failure_labels == ()
    assert result.failure_reasons == ()

    case_map = {case.scenario_id: case for case in result.case_results}
    retrieval_case = case_map["retrieval-reuse"]
    branch_case = case_map["branch-resume-recovery"]
    contradiction_case = case_map["contradiction-review"]
    uncertainty_case = case_map["uncertainty-brake-calibration"]
    no_lift_case = case_map["no-lift-counterexample"]
    burden_case = case_map["burden-heavy-counterexample"]
    prune_no_lift_case = case_map["prune-no-lift"]
    prune_burden_case = case_map["prune-burden-heavy"]

    assert retrieval_case.preferred_family_allocated_delta > 0.0
    assert branch_case.preferred_family_allocated_delta > 0.0
    assert contradiction_case.preferred_family_allocated_delta > 0.0
    assert uncertainty_case.preferred_family_allocated_delta > 0.0
    assert retrieval_case.selected_family_changed_to_preferred is False
    assert branch_case.selected_family_changed_to_preferred is True
    assert contradiction_case.baseline_selected_family.value == "check"
    assert contradiction_case.replay_selected_family.value == "check"
    assert contradiction_case.selected_family_changed_to_preferred is False
    assert "q_mem-signal:contradiction" in _preferred_score(contradiction_case)["reason_tags"]
    assert "q_mem-signal:uncertainty" in _preferred_score(uncertainty_case)["reason_tags"]
    assert no_lift_case.failure_labels == ()
    assert no_lift_case.preferred_family_allocated_delta == pytest.approx(0.0)
    assert burden_case.failure_labels == ()
    assert burden_case.preferred_family_allocated_delta == pytest.approx(0.0)
    assert prune_no_lift_case.failure_labels == ()
    assert prune_no_lift_case.preferred_family_allocated_delta == pytest.approx(0.0)
    assert prune_burden_case.failure_labels == ()
    assert prune_burden_case.preferred_family_allocated_delta == pytest.approx(0.0)


def test_aux_reference_replay_case_results_carry_publication_support_priors_and_machine_readable_failures() -> None:
    scenario_map = {
        scenario.scenario_id: scenario
        for scenario in make_aux_reference_replay_corpus()
    }
    counterexample = scenario_map["contradiction-review"]
    no_lift = scenario_map["burden-heavy-counterexample"]

    result = evaluate_aux_reference_q_mem_replay(
        (
            AuxReferenceReplayScenario(
                scenario_id="forced-counterexample",
                source_snapshots=counterexample.source_snapshots,
                target_snapshot=counterexample.target_snapshot,
                executive_state=counterexample.executive_state,
                preferred_family=counterexample.preferred_family,
                expect_improvement=False,
            ),
            AuxReferenceReplayScenario(
                scenario_id="forced-no-lift",
                source_snapshots=no_lift.source_snapshots,
                target_snapshot=no_lift.target_snapshot,
                executive_state=no_lift.executive_state,
                preferred_family=no_lift.preferred_family,
                expect_improvement=True,
            ),
        )
    )

    case_map = {case.scenario_id: case for case in result.case_results}
    forced_counterexample = case_map["forced-counterexample"]
    forced_no_lift = case_map["forced-no-lift"]

    assert isinstance(forced_counterexample, AuxReferenceReplayCaseResult)
    assert "aux/reference-replay" in forced_counterexample.publication.publication_tags
    assert forced_counterexample.support_memory_priors.active is True
    assert forced_counterexample.failure_labels == ("counterexample_dominates",)
    assert forced_no_lift.failure_labels == (
        "no_preferred_family_lift",
        "no_selected_family_change",
    )
    assert result.counterexample_case_count == 1
    assert result.negative_case_stable_count == 0
    assert result.dominant_failure_label in {
        "counterexample_dominates",
        "no_preferred_family_lift",
        "no_selected_family_change",
    }


@pytest.mark.parametrize(
    ("value", "expected_error", "message"),
    (
        ((), ValueError, "requires at least one scenario"),
        ("not-a-tuple", TypeError, "requires tuple\\[AuxReferenceReplayScenario, ...\\]"),
        ((object(),), TypeError, "requires only AuxReferenceReplayScenario instances"),
    ),
)
def test_evaluate_aux_reference_q_mem_replay_validates_input_shape(
    value: object,
    expected_error: type[Exception],
    message: str,
) -> None:
    with pytest.raises(expected_error, match=message):
        evaluate_aux_reference_q_mem_replay(value)  # type: ignore[arg-type]


def _preferred_score(case_result: AuxReferenceReplayCaseResult) -> dict[str, object]:
    for score in case_result.replay_scorecard.scores:
        if score.family is case_result.preferred_family:
            return {
                "family": score.family.value,
                "reason_tags": tuple(sorted(score.reason_tags)),
                "allocated_score": score.allocated_score,
                "memory_score": score.memory_score,
            }
    raise AssertionError(f"Missing preferred family payload for {case_result.scenario_id}.")
