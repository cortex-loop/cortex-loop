"""Cross-host shadow proof over explicit AUX-owned host/tool reliability priors."""

from __future__ import annotations

import pytest

from cortex.aux.cross_host_shadow import (
    AuxCrossHostShadowCaseResult,
    AuxCrossHostShadowEvaluationResult,
    AuxCrossHostShadowScenario,
    evaluate_aux_cross_host_shadow,
)

from ._aux_test_support import make_aux_cross_host_shadow_corpus, make_support_snapshot


def test_aux_cross_host_shadow_scenarios_require_time_separated_support_snapshots_and_canonical_host_name() -> None:
    snapshot = make_support_snapshot()
    scenario = make_aux_cross_host_shadow_corpus()[0]

    with pytest.raises(ValueError, match="time-separated source and target"):
        AuxCrossHostShadowScenario(
            scenario_id="same-snapshot",
            host_name="reference",
            source_snapshots=(snapshot,),
            target_snapshot=snapshot,
            executive_state=scenario.executive_state,
            preferred_family=scenario.preferred_family,
            expect_improvement=True,
        )

    with pytest.raises(ValueError, match="must be one of"):
        AuxCrossHostShadowScenario(
            scenario_id="bad-host",
            host_name="openai",
            source_snapshots=scenario.source_snapshots,
            target_snapshot=scenario.target_snapshot,
            executive_state=scenario.executive_state,
            preferred_family=scenario.preferred_family,
            expect_improvement=True,
        )


def test_evaluate_aux_cross_host_shadow_reports_repeat_stable_host_lift_and_invalidation_truth() -> None:
    result = evaluate_aux_cross_host_shadow(make_aux_cross_host_shadow_corpus())

    assert isinstance(result, AuxCrossHostShadowEvaluationResult)
    assert result.acceptance_passed is True
    assert dict(result.per_host_positive_case_counts) == {
        "claude": 2,
        "gemini": 2,
        "reference": 2,
    }
    assert dict(result.per_host_improved_case_counts) == {
        "claude": 2,
        "gemini": 2,
        "reference": 2,
    }
    assert dict(result.per_host_negative_stable_counts) == {
        "claude": 2,
        "gemini": 2,
        "reference": 2,
    }
    assert result.repeat_stable_hosts == ("claude", "gemini", "reference")
    assert result.counterexample_case_count == 0
    assert result.dominant_failure_label is None
    assert result.failure_labels == ()
    assert result.failure_reasons == ()

    case_map = {(case.host_name, case.scenario_id): case for case in result.case_results}
    claude_retrieval = case_map[("claude", "claude-retrieval-reuse")]
    gemini_contradiction = case_map[("gemini", "gemini-contradiction-review")]
    reference_invalidation = case_map[
        ("reference", "reference-fresh-contradiction-invalidation")
    ]

    assert isinstance(claude_retrieval, AuxCrossHostShadowCaseResult)
    assert claude_retrieval.preferred_family_allocated_delta > 0.0
    assert claude_retrieval.baseline_selected_family.value == "seek-context"
    assert claude_retrieval.replay_selected_family.value == "seek-context"
    assert claude_retrieval.reliability_component_active is True
    assert claude_retrieval.memory_removal_reverts_to_baseline is True

    assert gemini_contradiction.preferred_family_allocated_delta > 0.0
    assert gemini_contradiction.contradiction_invalidated_prior is True
    assert gemini_contradiction.reliability_component_active is False
    assert "q_mem-host:contradiction-invalidated" in _preferred_score(
        gemini_contradiction
    )["reason_tags"]

    assert reference_invalidation.expect_improvement is False
    assert reference_invalidation.contradiction_invalidated_prior is True
    assert reference_invalidation.reliability_component_active is False
    assert reference_invalidation.preferred_family_allocated_delta == pytest.approx(0.0)
    assert reference_invalidation.failure_labels == ()


def test_aux_cross_host_shadow_case_results_carry_host_truth_and_reversion_flags() -> None:
    result = evaluate_aux_cross_host_shadow(make_aux_cross_host_shadow_corpus())
    case_map = {(case.host_name, case.scenario_id): case for case in result.case_results}

    claude_retrieval = case_map[("claude", "claude-retrieval-reuse")]
    gemini_invalidation = case_map[("gemini", "gemini-fresh-contradiction-invalidation")]

    assert isinstance(claude_retrieval, AuxCrossHostShadowCaseResult)
    assert claude_retrieval.host_name == "claude"
    assert claude_retrieval.reliability_component_active is True
    assert claude_retrieval.contradiction_invalidated_prior is False
    assert claude_retrieval.memory_removal_reverts_to_baseline is True
    assert "aux/cross-host-shadow" in claude_retrieval.publication.publication_tags

    assert gemini_invalidation.host_name == "gemini"
    assert gemini_invalidation.expect_improvement is False
    assert gemini_invalidation.contradiction_invalidated_prior is True
    assert gemini_invalidation.reliability_component_active is False
    assert gemini_invalidation.memory_removal_reverts_to_baseline is True
    assert gemini_invalidation.failure_labels == ()


def test_evaluate_aux_cross_host_shadow_emits_machine_readable_failure_labels_for_single_host_only_lift() -> None:
    corpus = make_aux_cross_host_shadow_corpus()
    claude_only = tuple(
        scenario for scenario in corpus if scenario.host_name == "claude"
    )

    result = evaluate_aux_cross_host_shadow(claude_only)

    assert result.acceptance_passed is False
    assert "missing_repeat_stable_host_lift" in result.failure_labels
    assert "single_host_only_lift" in result.failure_labels
    assert result.dominant_failure_label in {
        "missing_repeat_stable_host_lift",
        "single_host_only_lift",
    }


@pytest.mark.parametrize(
    ("value", "expected_error", "message"),
    (
        ((), ValueError, "requires at least one scenario"),
        ("not-a-tuple", TypeError, "requires tuple\\[AuxCrossHostShadowScenario, ...\\]"),
        ((object(),), TypeError, "requires only AuxCrossHostShadowScenario instances"),
    ),
)
def test_evaluate_aux_cross_host_shadow_validates_input_shape(
    value: object,
    expected_error: type[Exception],
    message: str,
) -> None:
    with pytest.raises(expected_error, match=message):
        evaluate_aux_cross_host_shadow(value)  # type: ignore[arg-type]


def _preferred_score(case_result: AuxCrossHostShadowCaseResult) -> dict[str, object]:
    for score in case_result.replay_scorecard.scores:
        if score.family is case_result.preferred_family:
            return {
                "family": score.family.value,
                "reason_tags": tuple(sorted(score.reason_tags)),
                "allocated_score": score.allocated_score,
                "memory_score": score.memory_score,
            }
    raise AssertionError(f"Missing preferred family payload for {case_result.scenario_id}.")
