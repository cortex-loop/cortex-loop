"""Mechanical AUX-scoped drift checks for evaluation-first support geometry rows."""

from __future__ import annotations

from dataclasses import dataclass
import importlib
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class PromisedTestSurface:
    test_file: str
    test_names: tuple[str, ...]


@dataclass(frozen=True)
class AuxCorrespondenceExpectation:
    row_label: str
    module_path: str
    symbol_name: str
    promised_surfaces: tuple[PromisedTestSurface, ...]


EXPECTATIONS = (
    AuxCorrespondenceExpectation(
        row_label="AuxGeometryReport",
        module_path="cortex.aux.geometry",
        symbol_name="AuxGeometryReport",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/experimental/test_aux_geometry.py",
                test_names=(
                    "test_build_aux_geometry_report_derives_only_support_side_hints_and_preserves_snapshot_truth",
                    "test_aux_geometry_types_require_typed_support_refs_and_bounded_scores",
                ),
            ),
        ),
    ),
    AuxCorrespondenceExpectation(
        row_label="build_aux_geometry_report",
        module_path="cortex.aux.geometry",
        symbol_name="build_aux_geometry_report",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/experimental/test_aux_geometry.py",
                test_names=(
                    "test_build_aux_geometry_report_derives_only_support_side_hints_and_preserves_snapshot_truth",
                    "test_build_aux_geometry_report_accepts_explicit_matches_and_contradiction_clusters",
                ),
            ),
        ),
    ),
    AuxCorrespondenceExpectation(
        row_label="AuxEvaluationResult",
        module_path="cortex.aux.evaluation",
        symbol_name="AuxEvaluationResult",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/experimental/test_aux_evaluation.py",
                test_names=("test_evaluate_aux_support_snapshot_emits_geometry_and_lift_reports_with_quality_improvement",),
            ),
        ),
    ),
    AuxCorrespondenceExpectation(
        row_label="AuxTemporalScenario",
        module_path="cortex.aux.evaluation",
        symbol_name="AuxTemporalScenario",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/experimental/test_aux_corpus.py",
                test_names=("test_aux_temporal_scenarios_require_time_separated_source_and_target",),
            ),
        ),
    ),
    AuxCorrespondenceExpectation(
        row_label="AuxCorpusEvaluationResult",
        module_path="cortex.aux.evaluation",
        symbol_name="AuxCorpusEvaluationResult",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/experimental/test_aux_corpus.py",
                test_names=("test_evaluate_aux_support_corpus_reports_time_separated_lift_and_acceptance",),
            ),
        ),
    ),
    AuxCorrespondenceExpectation(
        row_label="AuxCorpusCaseResult",
        module_path="cortex.aux.evaluation",
        symbol_name="AuxCorpusCaseResult",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/experimental/test_aux_corpus.py",
                test_names=("test_aux_corpus_case_result_carries_support_priors_and_failure_reasons",),
            ),
        ),
    ),
    AuxCorrespondenceExpectation(
        row_label="AuxCorpusMetricSummary",
        module_path="cortex.aux.evaluation",
        symbol_name="AuxCorpusMetricSummary",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/experimental/test_aux_corpus.py",
                test_names=("test_aux_corpus_metric_summaries_cover_fixed_metrics_and_case_accounting",),
            ),
        ),
    ),
    AuxCorrespondenceExpectation(
        row_label="evaluate_aux_support_corpus",
        module_path="cortex.aux.evaluation",
        symbol_name="evaluate_aux_support_corpus",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/experimental/test_aux_corpus.py",
                test_names=(
                    "test_evaluate_aux_support_corpus_reports_time_separated_lift_and_acceptance",
                    "test_evaluate_aux_support_corpus_can_recommend_prune_candidate_for_weak_cases",
                    "test_evaluate_aux_support_corpus_validates_input_shape",
                ),
            ),
        ),
    ),
    AuxCorrespondenceExpectation(
        row_label="evaluate_aux_support_snapshot",
        module_path="cortex.aux.evaluation",
        symbol_name="evaluate_aux_support_snapshot",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/experimental/test_aux_evaluation.py",
                test_names=(
                    "test_evaluate_aux_support_snapshot_emits_geometry_and_lift_reports_with_quality_improvement",
                    "test_evaluate_aux_support_snapshot_requires_support_snapshot",
                ),
            ),
        ),
    ),
    AuxCorrespondenceExpectation(
        row_label="AuxLiftReport",
        module_path="cortex.aux.lift",
        symbol_name="AuxLiftReport",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/experimental/test_aux_lift.py",
                test_names=(
                    "test_build_aux_lift_report_keeps_experimental_when_quality_metric_improves",
                    "test_build_aux_lift_report_marks_prune_candidate_when_quality_does_not_improve",
                ),
            ),
        ),
    ),
    AuxCorrespondenceExpectation(
        row_label="build_aux_lift_report",
        module_path="cortex.aux.lift",
        symbol_name="build_aux_lift_report",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/experimental/test_aux_lift.py",
                test_names=(
                    "test_build_aux_lift_report_keeps_experimental_when_quality_metric_improves",
                    "test_build_aux_lift_report_requires_full_fixed_metric_set_and_non_negative_values",
                ),
            ),
        ),
    ),
    AuxCorrespondenceExpectation(
        row_label="OfflineSupportPublication",
        module_path="cortex.aux.publication",
        symbol_name="OfflineSupportPublication",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/experimental/test_aux_publication.py",
                test_names=(
                    "test_offline_support_publication_augments_snapshot_only_through_explicit_aux_appendix",
                    "test_offline_support_publication_requires_typed_support_refs_and_metadata",
                ),
            ),
        ),
    ),
    AuxCorrespondenceExpectation(
        row_label="build_offline_support_publication",
        module_path="cortex.aux.publication",
        symbol_name="build_offline_support_publication",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/experimental/test_aux_publication.py",
                test_names=("test_build_offline_support_publication_derives_only_support_side_refs_from_snapshot",),
            ),
        ),
    ),
    AuxCorrespondenceExpectation(
        row_label="augment_snapshot_with_offline_publication",
        module_path="cortex.aux.publication",
        symbol_name="augment_snapshot_with_offline_publication",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/experimental/test_aux_publication.py",
                test_names=("test_offline_support_publication_augments_snapshot_only_through_explicit_aux_appendix",),
            ),
            PromisedTestSurface(
                test_file="tests/experimental/integration/test_aux_claim_conservative.py",
                test_names=("test_offline_publication_augmentation_is_claim_conservative",),
            ),
        ),
    ),
    AuxCorrespondenceExpectation(
        row_label="build_support_memory_prior_appendix",
        module_path="cortex.aux.support_priors",
        symbol_name="build_support_memory_prior_appendix",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/experimental/test_aux_support_priors.py",
                test_names=(
                    "test_build_support_memory_prior_appendix_derives_nonzero_family_priors_from_offline_publication",
                    "test_build_support_memory_prior_appendix_stays_inactive_without_offline_publication_tag",
                ),
            ),
        ),
    ),
    AuxCorrespondenceExpectation(
        row_label="AuxReferenceReplayScenario",
        module_path="cortex.aux.reference_replay",
        symbol_name="AuxReferenceReplayScenario",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/experimental/test_aux_reference_replay.py",
                test_names=(
                    "test_aux_reference_replay_scenarios_require_time_separated_support_snapshots_and_reference_state",
                ),
            ),
        ),
    ),
    AuxCorrespondenceExpectation(
        row_label="AuxReferenceReplayCaseResult",
        module_path="cortex.aux.reference_replay",
        symbol_name="AuxReferenceReplayCaseResult",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/experimental/test_aux_reference_replay.py",
                test_names=(
                    "test_aux_reference_replay_case_results_carry_publication_support_priors_and_machine_readable_failures",
                ),
            ),
        ),
    ),
    AuxCorrespondenceExpectation(
        row_label="AuxReferenceReplayEvaluationResult",
        module_path="cortex.aux.reference_replay",
        symbol_name="AuxReferenceReplayEvaluationResult",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/experimental/test_aux_reference_replay.py",
                test_names=(
                    "test_evaluate_aux_reference_q_mem_replay_reports_reference_only_acceptance_and_failure_labels",
                ),
            ),
        ),
    ),
    AuxCorrespondenceExpectation(
        row_label="evaluate_aux_reference_q_mem_replay",
        module_path="cortex.aux.reference_replay",
        symbol_name="evaluate_aux_reference_q_mem_replay",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/experimental/test_aux_reference_replay.py",
                test_names=(
                    "test_evaluate_aux_reference_q_mem_replay_reports_reference_only_acceptance_and_failure_labels",
                    "test_evaluate_aux_reference_q_mem_replay_validates_input_shape",
                ),
            ),
        ),
    ),
)


@pytest.mark.parametrize("expectation", EXPECTATIONS, ids=lambda item: item.row_label)
def test_aux_correspondence_registry_resolves_code_home_and_test_surface(
    expectation: AuxCorrespondenceExpectation,
) -> None:
    module_home = REPO_ROOT.joinpath(*expectation.module_path.split(".")).with_suffix(".py")
    assert module_home.is_file(), (
        f"{expectation.row_label}: expected module home {module_home.relative_to(REPO_ROOT)}"
    )

    module = importlib.import_module(expectation.module_path)
    assert hasattr(module, expectation.symbol_name), (
        f"{expectation.row_label}: missing symbol {expectation.symbol_name} "
        f"in module {expectation.module_path}"
    )

    for promised_surface in expectation.promised_surfaces:
        test_file = REPO_ROOT / promised_surface.test_file
        assert test_file.is_file(), (
            f"{expectation.row_label}: expected promised test file {promised_surface.test_file}"
        )

        test_text = test_file.read_text(encoding="utf-8")
        for test_name in promised_surface.test_names:
            assert f"def {test_name}(" in test_text, (
                f"{expectation.row_label}: missing promised test function {test_name} "
                f"in {promised_surface.test_file}"
            )


def test_aux_correspondence_text_keeps_geometry_lift_and_publication_rows_explicit() -> None:
    correspondence_text = (
        REPO_ROOT / "docs" / "archive" / "internal" / "CORTEX_V2_MATH_TO_CODE_CORRESPONDENCE.md"
    ).read_text(encoding="utf-8")

    assert "| `GeomEval` evaluation-first geometry/support report over lawful public support state | `AuxGeometryReport` + `AuxMatchScore` + `AuxContradictionCluster` |" in correspondence_text
    assert "| retention-law lift comparison over fixed support-quality and burden metrics | `AuxLiftReport` + `AuxLiftMetric` + `build_aux_lift_report()` |" in correspondence_text
    assert "| deterministic evaluation-first AUX runner over lawful public support state | `AuxEvaluationResult` + `evaluate_aux_support_snapshot()` |" in correspondence_text
    assert "| time-separated source→target AUX corpus carrier over lawful support snapshots | `AuxTemporalScenario` |" in correspondence_text
    assert "| time-separated AUX corpus casewise result over offline publication, augmented target, support priors, geometry, lift, and failure carriage | `AuxCorpusCaseResult` |" in correspondence_text
    assert "| time-separated AUX corpus aggregate metric summary over improved/regressed case accounting and fixed-metric coverage | `AuxCorpusMetricSummary` |" in correspondence_text
    assert "| time-separated AUX corpus result over casewise lift, aggregate metric passes, burden totals, and retention | `AuxCorpusEvaluationResult` |" in correspondence_text
    assert "| time-separated AUX corpus runner over source publication and later target evaluation | `evaluate_aux_support_corpus()` |" in correspondence_text
    assert "| deterministic support-only offline publication builder over lawful public support state | `build_offline_support_publication()` |" in correspondence_text
    assert "| AUX-to-SRE explicit support-memory prior appendix over support-only offline publication | `build_support_memory_prior_appendix()` |" in correspondence_text
    assert "| `W_t^{pub+} = Augment^{aux}(W_t^{pub}, M_t^{offline})` support-only offline publication contract and augmentation-only re-entry | `OfflineSupportPublication` + `augment_snapshot_with_offline_publication()` |" in correspondence_text
    assert "| reference-only replay scenario over explicit AUX-owned offline publication, later target snapshot, and fixed preferred-family acceptance | `AuxReferenceReplayScenario` |" in correspondence_text
    assert "| reference-only replay case result over merged publication, explicit support priors, baseline vs replay scorecards, and fixed failure labels | `AuxReferenceReplayCaseResult` |" in correspondence_text
    assert "| reference-only replay aggregate result over preferred-family lift, selected-family flips, and truthful cut reasons | `AuxReferenceReplayEvaluationResult` |" in correspondence_text
    assert "| reference-only replay runner over `OfflineSupportPublication -> augment_snapshot_with_offline_publication() -> build_support_memory_prior_appendix() -> select_reference_soft_control(memory_priors=...)` | `evaluate_aux_reference_q_mem_replay()` |" in correspondence_text
