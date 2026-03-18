"""Mechanical Core-scoped drift checks for landed correspondence rows."""

from __future__ import annotations

from dataclasses import dataclass
import importlib
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class CoreCorrespondenceExpectation:
    row_label: str
    module_path: str
    symbol_name: str
    test_file: str
    test_names: tuple[str, ...]


EXPECTATIONS = (
    CoreCorrespondenceExpectation(
        row_label="LifecycleSurface",
        module_path="cortex.core.lifecycle",
        symbol_name="LifecycleSurface",
        test_file="tests/unit/test_core_substrate.py",
        test_names=("test_lifecycle_event_and_observation_carriers_construct_cleanly",),
    ),
    CoreCorrespondenceExpectation(
        row_label="LifecycleEffectBinding",
        module_path="cortex.core.lifecycle",
        symbol_name="LifecycleEffectBinding",
        test_file="tests/unit/test_core_substrate.py",
        test_names=("test_lifecycle_event_and_observation_carriers_construct_cleanly",),
    ),
    CoreCorrespondenceExpectation(
        row_label="LifecycleEventEnvelope",
        module_path="cortex.core.envelopes",
        symbol_name="LifecycleEventEnvelope",
        test_file="tests/unit/test_core_substrate.py",
        test_names=("test_lifecycle_event_and_observation_carriers_construct_cleanly",),
    ),
    CoreCorrespondenceExpectation(
        row_label="EventPayloadHandle",
        module_path="cortex.core.envelopes",
        symbol_name="EventPayloadHandle",
        test_file="tests/unit/test_core_substrate.py",
        test_names=("test_lifecycle_event_and_observation_carriers_construct_cleanly",),
    ),
    CoreCorrespondenceExpectation(
        row_label="MetadataField",
        module_path="cortex.core.envelopes",
        symbol_name="MetadataField",
        test_file="tests/unit/test_core_substrate.py",
        test_names=("test_lifecycle_event_and_observation_carriers_construct_cleanly",),
    ),
    CoreCorrespondenceExpectation(
        row_label="ObservationBundle",
        module_path="cortex.core.observation",
        symbol_name="ObservationBundle",
        test_file="tests/unit/test_core_substrate.py",
        test_names=("test_lifecycle_event_and_observation_carriers_construct_cleanly",),
    ),
    CoreCorrespondenceExpectation(
        row_label="PayloadView",
        module_path="cortex.core.observation",
        symbol_name="PayloadView",
        test_file="tests/unit/test_core_substrate.py",
        test_names=("test_lifecycle_event_and_observation_carriers_construct_cleanly",),
    ),
    CoreCorrespondenceExpectation(
        row_label="RuntimeRecord",
        module_path="cortex.core.observation",
        symbol_name="RuntimeRecord",
        test_file="tests/unit/test_core_substrate.py",
        test_names=("test_lifecycle_event_and_observation_carriers_construct_cleanly",),
    ),
    CoreCorrespondenceExpectation(
        row_label="StructuredObservation",
        module_path="cortex.core.observation",
        symbol_name="StructuredObservation",
        test_file="tests/unit/test_core_substrate.py",
        test_names=("test_lifecycle_event_and_observation_carriers_construct_cleanly",),
    ),
    CoreCorrespondenceExpectation(
        row_label="ExecutiveEnvironmentView",
        module_path="cortex.core.environment",
        symbol_name="ExecutiveEnvironmentView",
        test_file="tests/unit/test_core_substrate.py",
        test_names=("test_certification_context_rejects_executive_environment_view",),
    ),
    CoreCorrespondenceExpectation(
        row_label="CommitmentEnvironmentHandle",
        module_path="cortex.core.environment",
        symbol_name="CommitmentEnvironmentHandle",
        test_file="tests/unit/test_core_substrate.py",
        test_names=("test_certification_context_accepts_commitment_environment_handle",),
    ),
    CoreCorrespondenceExpectation(
        row_label="EnvironmentQuery",
        module_path="cortex.core.environment",
        symbol_name="EnvironmentQuery",
        test_file="tests/unit/test_core_substrate.py",
        test_names=(
            "test_certification_context_rejects_executive_environment_view",
            "test_certification_context_accepts_commitment_environment_handle",
        ),
    ),
    CoreCorrespondenceExpectation(
        row_label="STATE_SNAPSHOT",
        module_path="cortex.core.environment",
        symbol_name="STATE_SNAPSHOT",
        test_file="tests/unit/test_core_substrate.py",
        test_names=(
            "test_certification_context_rejects_executive_environment_view",
            "test_certification_context_accepts_commitment_environment_handle",
        ),
    ),
    CoreCorrespondenceExpectation(
        row_label="STATE_DIFF",
        module_path="cortex.core.environment",
        symbol_name="STATE_DIFF",
        test_file="tests/unit/test_core_substrate.py",
        test_names=(
            "test_certification_context_rejects_executive_environment_view",
            "test_certification_context_accepts_commitment_environment_handle",
        ),
    ),
    CoreCorrespondenceExpectation(
        row_label="EXECUTION_TRACE",
        module_path="cortex.core.environment",
        symbol_name="EXECUTION_TRACE",
        test_file="tests/unit/test_core_substrate.py",
        test_names=(
            "test_certification_context_rejects_executive_environment_view",
            "test_certification_context_accepts_commitment_environment_handle",
        ),
    ),
    CoreCorrespondenceExpectation(
        row_label="RESULT_ARTIFACT",
        module_path="cortex.core.environment",
        symbol_name="RESULT_ARTIFACT",
        test_file="tests/unit/test_core_substrate.py",
        test_names=(
            "test_certification_context_rejects_executive_environment_view",
            "test_certification_context_accepts_commitment_environment_handle",
        ),
    ),
    CoreCorrespondenceExpectation(
        row_label="CAPABILITY_VIEW",
        module_path="cortex.core.environment",
        symbol_name="CAPABILITY_VIEW",
        test_file="tests/unit/test_core_substrate.py",
        test_names=(
            "test_certification_context_rejects_executive_environment_view",
            "test_certification_context_accepts_commitment_environment_handle",
        ),
    ),
    CoreCorrespondenceExpectation(
        row_label="EXTERNAL_RECORD",
        module_path="cortex.core.environment",
        symbol_name="EXTERNAL_RECORD",
        test_file="tests/unit/test_core_substrate.py",
        test_names=(
            "test_certification_context_rejects_executive_environment_view",
            "test_certification_context_accepts_commitment_environment_handle",
        ),
    ),
    CoreCorrespondenceExpectation(
        row_label="SupportState",
        module_path="cortex.core.support",
        symbol_name="SupportState",
        test_file="tests/unit/test_core_substrate.py",
        test_names=("test_support_state_and_snapshot_are_distinct_types",),
    ),
    CoreCorrespondenceExpectation(
        row_label="SupportSnapshot",
        module_path="cortex.core.support",
        symbol_name="SupportSnapshot",
        test_file="tests/unit/test_core_substrate.py",
        test_names=("test_support_state_and_snapshot_are_distinct_types",),
    ),
    CoreCorrespondenceExpectation(
        row_label="SupportTraceState",
        module_path="cortex.core.support",
        symbol_name="SupportTraceState",
        test_file="tests/unit/test_core_substrate.py",
        test_names=("test_support_state_and_snapshot_are_distinct_types",),
    ),
    CoreCorrespondenceExpectation(
        row_label="SupportSessionState",
        module_path="cortex.core.support",
        symbol_name="SupportSessionState",
        test_file="tests/unit/test_core_substrate.py",
        test_names=("test_support_state_and_snapshot_are_distinct_types",),
    ),
    CoreCorrespondenceExpectation(
        row_label="SupportHostState",
        module_path="cortex.core.support",
        symbol_name="SupportHostState",
        test_file="tests/unit/test_core_substrate.py",
        test_names=("test_support_state_and_snapshot_are_distinct_types",),
    ),
    CoreCorrespondenceExpectation(
        row_label="SupportExecMemoryState",
        module_path="cortex.core.support",
        symbol_name="SupportExecMemoryState",
        test_file="tests/unit/test_core_substrate.py",
        test_names=("test_support_state_and_snapshot_are_distinct_types",),
    ),
    CoreCorrespondenceExpectation(
        row_label="WakeReceipt",
        module_path="cortex.core.support",
        symbol_name="WakeReceipt",
        test_file="tests/unit/test_core_substrate.py",
        test_names=("test_support_state_and_snapshot_are_distinct_types",),
    ),
    CoreCorrespondenceExpectation(
        row_label="CommitmentStatus",
        module_path="cortex.core.commitments",
        symbol_name="CommitmentStatus",
        test_file="tests/unit/test_core_substrate.py",
        test_names=("test_commitment_status_is_the_exact_three_state_lattice",),
    ),
    CoreCorrespondenceExpectation(
        row_label="CommitmentCandidate",
        module_path="cortex.core.commitments",
        symbol_name="CommitmentCandidate",
        test_file="tests/unit/test_core_substrate.py",
        test_names=("test_commitment_verdict_holds_typed_certification_references",),
    ),
    CoreCorrespondenceExpectation(
        row_label="ProvenanceManifest",
        module_path="cortex.core.commitments",
        symbol_name="ProvenanceManifest",
        test_file="tests/unit/test_core_substrate.py",
        test_names=(
            "test_provenance_manifest_supports_multiple_domain_agnostic_source_families",
            "test_commitment_verdict_holds_typed_certification_references",
        ),
    ),
    CoreCorrespondenceExpectation(
        row_label="ProvenanceEvidenceRef",
        module_path="cortex.core.commitments",
        symbol_name="ProvenanceEvidenceRef",
        test_file="tests/unit/test_core_substrate.py",
        test_names=(
            "test_provenance_manifest_supports_multiple_domain_agnostic_source_families",
            "test_commitment_verdict_holds_typed_certification_references",
        ),
    ),
    CoreCorrespondenceExpectation(
        row_label="BoundaryAssessment",
        module_path="cortex.core.commitments",
        symbol_name="BoundaryAssessment",
        test_file="tests/unit/test_core_substrate.py",
        test_names=("test_boundary_assessment_keeps_blockedness_separate_from_commitment_status",),
    ),
    CoreCorrespondenceExpectation(
        row_label="CommitmentVerdict",
        module_path="cortex.core.commitments",
        symbol_name="CommitmentVerdict",
        test_file="tests/unit/test_core_substrate.py",
        test_names=("test_commitment_verdict_holds_typed_certification_references",),
    ),
    CoreCorrespondenceExpectation(
        row_label="CertificationContext",
        module_path="cortex.core.commitments",
        symbol_name="CertificationContext",
        test_file="tests/unit/test_core_substrate.py",
        test_names=(
            "test_certification_context_rejects_executive_environment_view",
            "test_certification_context_accepts_commitment_environment_handle",
        ),
    ),
    CoreCorrespondenceExpectation(
        row_label="ContradictionRecord",
        module_path="cortex.core.errors",
        symbol_name="ContradictionRecord",
        test_file="tests/unit/test_core_substrate.py",
        test_names=("test_degradation_and_error_records_preserve_reason_and_capabilities",),
    ),
    CoreCorrespondenceExpectation(
        row_label="DegradationRecord",
        module_path="cortex.core.errors",
        symbol_name="DegradationRecord",
        test_file="tests/unit/test_core_substrate.py",
        test_names=("test_degradation_and_error_records_preserve_reason_and_capabilities",),
    ),
    CoreCorrespondenceExpectation(
        row_label="CoreErrorRecord",
        module_path="cortex.core.errors",
        symbol_name="CoreErrorRecord",
        test_file="tests/unit/test_core_substrate.py",
        test_names=("test_degradation_and_error_records_preserve_reason_and_capabilities",),
    ),
    CoreCorrespondenceExpectation(
        row_label="DispatchLane",
        module_path="cortex.core.dispatch",
        symbol_name="DispatchLane",
        test_file="tests/unit/test_dispatch.py",
        test_names=(
            "test_cheap_event_stays_cheap_with_no_evidence_burden",
            "test_proposal_like_event_becomes_candidate_bearing",
            "test_explicit_full_commitment_wake_becomes_full_commitment",
        ),
    ),
    CoreCorrespondenceExpectation(
        row_label="DispatchDecision",
        module_path="cortex.core.dispatch",
        symbol_name="DispatchDecision",
        test_file="tests/unit/test_dispatch.py",
        test_names=("test_candidate_presence_alone_becomes_candidate_bearing",),
    ),
    CoreCorrespondenceExpectation(
        row_label="WakeDecision",
        module_path="cortex.core.dispatch",
        symbol_name="WakeDecision",
        test_file="tests/unit/test_dispatch.py",
        test_names=(
            "test_boundary_required_marker_forces_full_commitment",
            "test_candidate_presence_alone_does_not_overwake_to_full_commitment",
        ),
    ),
    CoreCorrespondenceExpectation(
        row_label="EvidencePlan",
        module_path="cortex.core.dispatch",
        symbol_name="EvidencePlan",
        test_file="tests/unit/test_dispatch.py",
        test_names=("test_evidence_plan_matches_the_dispatched_lane",),
    ),
    CoreCorrespondenceExpectation(
        row_label="classify_dispatch",
        module_path="cortex.core.dispatch",
        symbol_name="classify_dispatch",
        test_file="tests/unit/test_dispatch.py",
        test_names=(
            "test_cheap_event_stays_cheap_with_no_evidence_burden",
            "test_candidate_presence_alone_becomes_candidate_bearing",
            "test_candidate_presence_alone_does_not_overwake_to_full_commitment",
        ),
    ),
    CoreCorrespondenceExpectation(
        row_label="certify_commitment",
        module_path="cortex.core.certification",
        symbol_name="certify_commitment",
        test_file="tests/unit/test_certification_artifacts.py",
        test_names=(
            "test_certify_commitment_returns_certified_with_concrete_evidence",
            "test_certify_commitment_returns_uncertified_without_concrete_evidence",
            "test_certify_commitment_returns_blocked_when_boundary_is_blocked",
            "test_certify_commitment_preserves_contradictions_and_degradations",
        ),
    ),
)


def _module_home(module_path: str) -> Path:
    return REPO_ROOT.joinpath(*module_path.split(".")).with_suffix(".py")


@pytest.mark.parametrize("expectation", EXPECTATIONS, ids=lambda item: item.row_label)
def test_core_correspondence_registry_resolves_code_home_and_test_surface(
    expectation: CoreCorrespondenceExpectation,
) -> None:
    module_home = _module_home(expectation.module_path)
    assert module_home.is_file(), (
        f"{expectation.row_label}: expected module home {module_home.relative_to(REPO_ROOT)}"
    )

    module = importlib.import_module(expectation.module_path)
    assert hasattr(module, expectation.symbol_name), (
        f"{expectation.row_label}: missing symbol {expectation.symbol_name} "
        f"in module {expectation.module_path}"
    )

    test_file = REPO_ROOT / expectation.test_file
    assert test_file.is_file(), (
        f"{expectation.row_label}: expected promised test file {expectation.test_file}"
    )

    test_text = test_file.read_text(encoding="utf-8")
    for test_name in expectation.test_names:
        assert f"def {test_name}(" in test_text, (
            f"{expectation.row_label}: missing promised test function {test_name} "
            f"in {expectation.test_file}"
        )
