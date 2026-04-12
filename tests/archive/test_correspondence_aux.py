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
    assert "| deterministic support-only offline publication builder over lawful public support state | `build_offline_support_publication()` |" in correspondence_text
    assert "| AUX-to-SRE explicit support-memory prior appendix over support-only offline publication | `build_support_memory_prior_appendix()` |" in correspondence_text
    assert "| `W_t^{pub+} = Augment^{aux}(W_t^{pub}, M_t^{offline})` support-only offline publication contract and augmentation-only re-entry | `OfflineSupportPublication` + `augment_snapshot_with_offline_publication()` |" in correspondence_text
