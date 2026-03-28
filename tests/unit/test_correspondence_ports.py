"""Mechanical Section 2 drift checks for landed ports correspondence rows."""

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
class PortsCorrespondenceExpectation:
    row_label: str
    home_path: str
    module_path: str
    symbol_name: str
    promised_surfaces: tuple[PromisedTestSurface, ...]


EXPECTATIONS = (
    PortsCorrespondenceExpectation(
        row_label="CommitmentPayloadExtraction",
        home_path="cortex/core/commitment_payload.py",
        module_path="cortex.core.commitment_payload",
        symbol_name="CommitmentPayloadExtraction",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_commitment_payload.py",
                test_names=(
                    "test_native_commitment_carrier_wins_when_present",
                    "test_message_fallback_only_runs_when_allowed_and_normalizes_keys",
                ),
            ),
        ),
    ),
    PortsCorrespondenceExpectation(
        row_label="extract_commitment_payload",
        home_path="cortex/core/commitment_payload.py",
        module_path="cortex.core.commitment_payload",
        symbol_name="extract_commitment_payload",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_commitment_payload.py",
                test_names=(
                    "test_native_commitment_carrier_wins_when_present",
                    "test_message_fallback_only_runs_when_allowed_and_normalizes_keys",
                ),
            ),
        ),
    ),
    PortsCorrespondenceExpectation(
        row_label="CommitmentExtractionResult",
        home_path="cortex/core/commitment_extract.py",
        module_path="cortex.core.commitment_extract",
        symbol_name="CommitmentExtractionResult",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_commitment_extract.py",
                test_names=(
                    "test_source_labeling_matches_resolution_path",
                    "test_strict_mode_rejects_fallback_only_structured_claims",
                ),
            ),
        ),
    ),
    PortsCorrespondenceExpectation(
        row_label="resolve_commitment_extract",
        home_path="cortex/core/commitment_extract.py",
        module_path="cortex.core.commitment_extract",
        symbol_name="resolve_commitment_extract",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_commitment_extract.py",
                test_names=(
                    "test_source_labeling_matches_resolution_path",
                    "test_strict_mode_rejects_fallback_only_structured_claims",
                ),
            ),
        ),
    ),
    PortsCorrespondenceExpectation(
        row_label="CommitmentFieldResolution",
        home_path="cortex/core/commitment_extract.py",
        module_path="cortex.core.commitment_extract",
        symbol_name="CommitmentFieldResolution",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_commitment_extract.py",
                test_names=(
                    "test_reconcile_commitment_field_prefers_direct_payload_value",
                    "test_reconcile_commitment_field_falls_back_to_extracted_fields_when_missing",
                ),
            ),
        ),
    ),
    PortsCorrespondenceExpectation(
        row_label="reconcile_commitment_field",
        home_path="cortex/core/commitment_extract.py",
        module_path="cortex.core.commitment_extract",
        symbol_name="reconcile_commitment_field",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_commitment_extract.py",
                test_names=(
                    "test_reconcile_commitment_field_prefers_direct_payload_value",
                    "test_reconcile_commitment_field_falls_back_to_extracted_fields_when_missing",
                ),
            ),
        ),
    ),
    PortsCorrespondenceExpectation(
        row_label="RepositorySnapshot",
        home_path="cortex/core/provenance.py",
        module_path="cortex.core.provenance",
        symbol_name="RepositorySnapshot",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_provenance_helpers.py",
                test_names=("test_repository_snapshot_reports_unavailable_without_git_marker",),
            ),
        ),
    ),
    PortsCorrespondenceExpectation(
        row_label="repository_snapshot",
        home_path="cortex/core/provenance.py",
        module_path="cortex.core.provenance",
        symbol_name="repository_snapshot",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_provenance_helpers.py",
                test_names=("test_repository_snapshot_reports_unavailable_without_git_marker",),
            ),
        ),
    ),
    PortsCorrespondenceExpectation(
        row_label="ChangedFilesDelta",
        home_path="cortex/core/provenance.py",
        module_path="cortex.core.provenance",
        symbol_name="ChangedFilesDelta",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_provenance_helpers.py",
                test_names=(
                    "test_changed_files_since_baseline_returns_delta_when_snapshots_are_available",
                    "test_changed_files_since_baseline_returns_reason_when_snapshot_unavailable",
                ),
            ),
        ),
    ),
    PortsCorrespondenceExpectation(
        row_label="changed_files_since_baseline",
        home_path="cortex/core/provenance.py",
        module_path="cortex.core.provenance",
        symbol_name="changed_files_since_baseline",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_provenance_helpers.py",
                test_names=(
                    "test_changed_files_since_baseline_returns_delta_when_snapshots_are_available",
                    "test_changed_files_since_baseline_returns_reason_when_snapshot_unavailable",
                ),
            ),
        ),
    ),
    PortsCorrespondenceExpectation(
        row_label="extract_requirement_ids",
        home_path="cortex/core/provenance.py",
        module_path="cortex.core.provenance",
        symbol_name="extract_requirement_ids",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_provenance_helpers.py",
                test_names=(
                    "test_requirement_id_extraction_prefers_direct_ids_and_deduplicates",
                    "test_requirement_id_extraction_falls_back_to_nested_contract_ids",
                ),
            ),
        ),
    ),
    PortsCorrespondenceExpectation(
        row_label="EvidenceReferenceEvaluation",
        home_path="cortex/core/provenance.py",
        module_path="cortex.core.provenance",
        symbol_name="EvidenceReferenceEvaluation",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_provenance_evidence.py",
                test_names=(
                    "test_path_reference_verifies_when_file_exists_and_fails_when_missing",
                    "test_tool_reference_verifies_or_becomes_uncheckable_without_tool_evidence",
                ),
            ),
        ),
    ),
    PortsCorrespondenceExpectation(
        row_label="evaluate_evidence_reference",
        home_path="cortex/core/provenance.py",
        module_path="cortex.core.provenance",
        symbol_name="evaluate_evidence_reference",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_provenance_evidence.py",
                test_names=(
                    "test_path_reference_verifies_when_file_exists_and_fails_when_missing",
                    "test_tool_reference_verifies_or_becomes_uncheckable_without_tool_evidence",
                ),
            ),
        ),
    ),
    PortsCorrespondenceExpectation(
        row_label="normalize_command_claim",
        home_path="cortex/core/provenance.py",
        module_path="cortex.core.provenance",
        symbol_name="normalize_command_claim",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_provenance_evidence.py",
                test_names=("test_command_reference_matches_normalized_wrapper_variants",),
            ),
        ),
    ),
    PortsCorrespondenceExpectation(
        row_label="command_claim_matches",
        home_path="cortex/core/provenance.py",
        module_path="cortex.core.provenance",
        symbol_name="command_claim_matches",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_provenance_evidence.py",
                test_names=("test_command_reference_matches_normalized_wrapper_variants",),
            ),
        ),
    ),
    PortsCorrespondenceExpectation(
        row_label="normalize_repo_relative_file_claims",
        home_path="cortex/core/provenance.py",
        module_path="cortex.core.provenance",
        symbol_name="normalize_repo_relative_file_claims",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_provenance_evidence.py",
                test_names=("test_repo_relative_file_claim_normalization_dedupes_and_strips_suffixes",),
            ),
        ),
    ),
    PortsCorrespondenceExpectation(
        row_label="NormalizedDriverEvent",
        home_path="cortex/drivers/common_normalization.py",
        module_path="cortex.drivers.common_normalization",
        symbol_name="NormalizedDriverEvent",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_common_normalization.py",
                test_names=(
                    "test_event_name_alias_and_casing_normalization",
                    "test_normalized_event_carrier_returns_normalized_name_and_payload_copy",
                ),
            ),
        ),
    ),
    PortsCorrespondenceExpectation(
        row_label="normalize_driver_event",
        home_path="cortex/drivers/common_normalization.py",
        module_path="cortex.drivers.common_normalization",
        symbol_name="normalize_driver_event",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_common_normalization.py",
                test_names=(
                    "test_event_name_alias_and_casing_normalization",
                    "test_normalized_event_carrier_returns_normalized_name_and_payload_copy",
                ),
            ),
        ),
    ),
    PortsCorrespondenceExpectation(
        row_label="normalize_driver_payload",
        home_path="cortex/drivers/common_normalization.py",
        module_path="cortex.drivers.common_normalization",
        symbol_name="normalize_driver_payload",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_common_normalization.py",
                test_names=(
                    "test_payload_normalization_keeps_existing_native_commitment_fields_intact",
                    "test_generic_payload_normalization_does_not_impose_host_specific_doctrine",
                ),
            ),
        ),
    ),
    PortsCorrespondenceExpectation(
        row_label="CANONICAL_EVENT_ALIASES",
        home_path="cortex/drivers/common_normalization.py",
        module_path="cortex.drivers.common_normalization",
        symbol_name="CANONICAL_EVENT_ALIASES",
        promised_surfaces=(
            PromisedTestSurface(
                test_file="tests/unit/test_common_normalization.py",
                test_names=("test_event_name_alias_and_casing_normalization",),
            ),
        ),
    ),
)


@pytest.mark.parametrize("expectation", EXPECTATIONS, ids=lambda item: item.row_label)
def test_ports_correspondence_registry_resolves_code_home_and_test_surface(
    expectation: PortsCorrespondenceExpectation,
) -> None:
    home_path = REPO_ROOT / expectation.home_path
    assert home_path.is_file(), (
        f"{expectation.row_label}: expected module home {expectation.home_path}"
    )

    module = importlib.import_module(expectation.module_path)
    assert hasattr(module, expectation.symbol_name), (
        f"{expectation.row_label}: missing symbol {expectation.symbol_name} "
        f"in module {expectation.module_path}"
    )

    for surface in expectation.promised_surfaces:
        test_file = REPO_ROOT / surface.test_file
        assert test_file.is_file(), (
            f"{expectation.row_label}: expected promised test file {surface.test_file}"
        )

        test_text = test_file.read_text(encoding="utf-8")
        for test_name in surface.test_names:
            assert f"def {test_name}(" in test_text, (
                f"{expectation.row_label}: missing promised test function {test_name} "
                f"in {surface.test_file}"
            )
