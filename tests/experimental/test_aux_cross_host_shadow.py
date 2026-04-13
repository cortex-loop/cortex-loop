"""Cross-host shadow proof over explicit AUX-owned host/tool reliability priors."""

from __future__ import annotations

import pytest

from cortex.aux.cross_host_shadow import (
    AuxCrossHostShadowCaseResult,
    AuxCrossHostShadowEvaluationResult,
    AuxCrossHostShadowScenario,
    evaluate_aux_cross_host_shadow,
)

from ._aux_test_support import (
    make_aux_cross_host_shadow_corpus,
    make_aux_reference_replay_corpus,
    make_support_snapshot,
)


def test_aux_cross_host_shadow_scenarios_require_time_separated_support_snapshots_and_canonical_host_name() -> None:
    snapshot = make_support_snapshot()
    scenario = make_aux_cross_host_shadow_corpus()[0]

    with pytest.raises(ValueError, match="time-separated source and target"):
        AuxCrossHostShadowScenario(
            scenario_id="same-snapshot",
            scenario_class=scenario.scenario_class,
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
            scenario_class=scenario.scenario_class,
            host_name="openai",
            source_snapshots=scenario.source_snapshots,
            target_snapshot=scenario.target_snapshot,
            executive_state=scenario.executive_state,
            preferred_family=scenario.preferred_family,
            expect_improvement=True,
        )


def test_evaluate_aux_cross_host_shadow_reports_remaining_branch_gap_and_claim_limitation_truth() -> None:
    result = evaluate_aux_cross_host_shadow(make_aux_cross_host_shadow_corpus())

    assert isinstance(result, AuxCrossHostShadowEvaluationResult)
    assert result.acceptance_passed is False
    assert result.host_aliasing_detected is True
    assert dict(result.per_host_positive_case_counts) == {
        "claude": 3,
        "gemini": 3,
        "reference": 3,
    }
    assert dict(result.per_host_improved_case_counts) == {
        "claude": 3,
        "gemini": 3,
        "reference": 3,
    }
    assert dict(result.per_host_negative_stable_counts) == {
        "claude": 2,
        "gemini": 2,
        "reference": 2,
    }
    assert result.repeat_stable_hosts == ()
    assert result.counterexample_case_count == 0
    assert result.dominant_failure_label == "missing_branch_family_lift"
    assert result.failure_labels == (
        "missing_repeat_stable_host_lift",
        "missing_branch_family_lift",
        "host_aliasing_detected",
    )
    assert any("branch-family lift" in reason for reason in result.failure_reasons)
    assert any("shared documented non-reference shell" in reason for reason in result.failure_reasons)

    case_map = {(case.host_name, case.scenario_id): case for case in result.case_results}
    claude_retrieval = case_map[("claude", "claude-retrieval-reuse")]
    gemini_branch = case_map[("gemini", "gemini-branch-resume")]
    gemini_check = case_map[("gemini", "gemini-check-review")]
    reference_invalidation = case_map[
        ("reference", "reference-fresh-contradiction-invalidation")
    ]

    assert isinstance(claude_retrieval, AuxCrossHostShadowCaseResult)
    assert claude_retrieval.scenario_class == "retrieval_reuse"
    assert claude_retrieval.preferred_family_total_delta > 0.0
    assert claude_retrieval.preferred_family_reliability_delta > 0.0
    assert claude_retrieval.baseline_selected_family.value == "seek-context"
    assert claude_retrieval.replay_selected_family.value == "seek-context"
    assert claude_retrieval.reliability_component_active is True
    assert claude_retrieval.preferred_family_uses_reliability_weight is True
    assert claude_retrieval.memory_removal_reverts_to_baseline is True

    assert gemini_branch.scenario_class == "branch_resume"
    assert gemini_branch.preferred_family_total_delta > 0.0
    assert gemini_branch.preferred_family_reliability_delta > 0.0
    assert gemini_branch.replay_selected_family.value == "seek-context"

    assert gemini_check.scenario_class == "check_review"
    assert gemini_check.preferred_family_total_delta > 0.0
    assert gemini_check.preferred_family_reliability_delta > 0.0
    assert gemini_check.contradiction_invalidated_prior is False
    assert gemini_check.reliability_component_active is True
    assert "q_mem-host:reliability-active" in _preferred_score(gemini_check)["reason_tags"]

    assert reference_invalidation.expect_improvement is False
    assert reference_invalidation.scenario_class == "fresh_contradiction_invalidation"
    assert reference_invalidation.contradiction_invalidated_prior is True
    assert reference_invalidation.reliability_component_active is False
    assert reference_invalidation.preferred_family_reliability_delta == pytest.approx(0.0)
    assert reference_invalidation.failure_labels == ()


def test_aux_cross_host_shadow_case_results_carry_host_truth_reliability_delta_and_signature() -> None:
    result = evaluate_aux_cross_host_shadow(make_aux_cross_host_shadow_corpus())
    case_map = {(case.host_name, case.scenario_id): case for case in result.case_results}

    claude_retrieval = case_map[("claude", "claude-retrieval-reuse")]
    gemini_invalidation = case_map[("gemini", "gemini-fresh-contradiction-invalidation")]

    assert isinstance(claude_retrieval, AuxCrossHostShadowCaseResult)
    assert claude_retrieval.host_name == "claude"
    assert claude_retrieval.scenario_class == "retrieval_reuse"
    assert claude_retrieval.reliability_component_active is True
    assert claude_retrieval.contradiction_invalidated_prior is False
    assert claude_retrieval.preferred_family_reliability_delta > 0.0
    assert claude_retrieval.memory_removal_reverts_to_baseline is True
    assert claude_retrieval.host_signature
    assert any(entry.startswith("family-mask:") for entry in claude_retrieval.host_signature)
    assert "aux/cross-host-shadow" in claude_retrieval.publication.publication_tags

    assert gemini_invalidation.host_name == "gemini"
    assert gemini_invalidation.expect_improvement is False
    assert gemini_invalidation.scenario_class == "fresh_contradiction_invalidation"
    assert gemini_invalidation.contradiction_invalidated_prior is True
    assert gemini_invalidation.reliability_component_active is False
    assert gemini_invalidation.preferred_family_reliability_delta == pytest.approx(0.0)
    assert gemini_invalidation.memory_removal_reverts_to_baseline is True
    assert gemini_invalidation.failure_labels == ()


def test_evaluate_aux_cross_host_shadow_keeps_weighted_burden_counterexamples_stable() -> None:
    result = evaluate_aux_cross_host_shadow(make_aux_cross_host_shadow_corpus())
    weighted_cases = [
        case
        for case in result.case_results
        if case.scenario_class == "weighted_burden_counterexample"
    ]

    assert len(weighted_cases) == 3
    for case in weighted_cases:
        assert case.expect_improvement is False
        assert case.preferred_family.value == "branch"
        assert case.preferred_family_uses_reliability_weight is False
        assert case.preferred_family_total_delta == pytest.approx(0.0)
        assert case.preferred_family_reliability_delta == pytest.approx(0.0)
        assert case.failure_labels == ()


def test_evaluate_aux_cross_host_shadow_memory_removal_reverts_to_online_only_baseline() -> None:
    result = evaluate_aux_cross_host_shadow(make_aux_cross_host_shadow_corpus())

    assert result.case_results
    for case in result.case_results:
        assert case.memory_removal_reverts_to_baseline is True


def test_evaluate_aux_cross_host_shadow_emits_machine_readable_failure_labels_for_single_host_only_lift() -> None:
    corpus = list(make_aux_cross_host_shadow_corpus())
    branch_state = next(
        scenario.executive_state
        for scenario in make_aux_reference_replay_corpus()
        if scenario.scenario_id == "branch-resume-recovery"
    )
    claude_only = []
    for scenario in corpus:
        if scenario.host_name != "claude":
            continue
        if scenario.scenario_class == "branch_resume":
            scenario = AuxCrossHostShadowScenario(
                scenario_id=scenario.scenario_id,
                scenario_class=scenario.scenario_class,
                host_name=scenario.host_name,
                source_snapshots=scenario.source_snapshots,
                target_snapshot=scenario.target_snapshot,
                executive_state=branch_state,
                preferred_family=scenario.preferred_family,
                expect_improvement=scenario.expect_improvement,
                notes=scenario.notes,
                metadata=scenario.metadata,
            )
        claude_only.append(scenario)

    result = evaluate_aux_cross_host_shadow(tuple(claude_only))

    assert result.acceptance_passed is False
    assert "missing_repeat_stable_host_lift" in result.failure_labels
    assert "single_host_only_lift" in result.failure_labels
    assert result.dominant_failure_label in {
        "missing_repeat_stable_host_lift",
        "single_host_only_lift",
        "missing_branch_family_lift",
    }


def test_evaluate_aux_cross_host_shadow_detects_non_reference_host_aliasing_and_forces_claim_limitation() -> None:
    result = evaluate_aux_cross_host_shadow(make_aux_cross_host_shadow_corpus())

    claude_signatures = {
        case.scenario_class: case.host_signature
        for case in result.case_results
        if case.host_name == "claude"
    }
    gemini_signatures = {
        case.scenario_class: case.host_signature
        for case in result.case_results
        if case.host_name == "gemini"
    }

    assert claude_signatures == gemini_signatures
    assert result.host_aliasing_detected is True
    assert "host_aliasing_detected" in result.failure_labels
    assert result.acceptance_passed is False


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
