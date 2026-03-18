"""Focused tests for the OpenAI commitment-path slice."""

from cortex.core.commitments import (
    BoundaryAssessment,
    CommitmentStatus,
    ProvenanceEvidenceRef,
    ProvenanceManifest,
)
from cortex.core.dispatch import DispatchLane
from cortex.core.environment import CommitmentEnvironmentHandle, EXECUTION_TRACE
from cortex.drivers.openai_host_commitment import evaluate_openai_host_commitment


def test_full_commitment_openai_event_with_concrete_provenance_yields_certified() -> None:
    result = evaluate_openai_host_commitment(
        "response.completed",
        {
            "commitment_id": "openai-commit-1",
            "externally_consequential": True,
        },
        environment_handle=_make_environment_handle(),
        provenance_manifest=ProvenanceManifest(
            evidence_refs=(
                ProvenanceEvidenceRef(
                    source_family="result_artifact",
                    reference_id="artifact-1",
                ),
            ),
        ),
    )

    assert result.dispatch_decision.lane is DispatchLane.FULL_COMMITMENT
    assert result.candidate is not None
    assert result.candidate.candidate_id == "openai-commit-1"
    assert result.verdict is not None
    assert result.verdict.status is CommitmentStatus.CERTIFIED


def test_malformed_native_commitment_carrier_surfaces_warning_while_preserving_full_commitment_path() -> None:
    result = evaluate_openai_host_commitment(
        "response.completed",
        {
            "commitment_fields_source": "native",
            "commitment_fields": 42,
            "externally_consequential": True,
        },
        environment_handle=_make_environment_handle(),
        provenance_manifest=ProvenanceManifest(
            evidence_refs=(
                ProvenanceEvidenceRef(
                    source_family="result_artifact",
                    reference_id="artifact-native-warning-3",
                ),
            ),
        ),
    )

    assert result.dispatch_decision.lane is DispatchLane.FULL_COMMITMENT
    assert result.candidate is not None
    assert result.candidate.candidate_id.startswith("local-candidate-")
    assert result.verdict is not None
    assert result.verdict.status is CommitmentStatus.CERTIFIED
    assert "Ignoring invalid native commitment carrier; expected an object." in result.warnings


def test_blocked_boundary_yields_blocked_even_when_provenance_exists() -> None:
    result = evaluate_openai_host_commitment(
        "response.completed",
        {
            "commitment_id": "openai-commit-2",
            "externally_consequential": True,
        },
        environment_handle=_make_environment_handle(),
        provenance_manifest=ProvenanceManifest(
            evidence_refs=(
                ProvenanceEvidenceRef(
                    source_family="external_artifact",
                    reference_id="artifact-2",
                ),
            ),
        ),
        boundary_assessment=BoundaryAssessment(
            blocked=True,
            reason_code="approval-required",
            boundary_tags=frozenset({"external-boundary"}),
        ),
    )

    assert result.verdict is not None
    assert result.verdict.status is CommitmentStatus.BLOCKED


def test_missing_evidence_yields_uncertified() -> None:
    result = evaluate_openai_host_commitment(
        "response.completed",
        {
            "commitment_id": "openai-commit-3",
            "externally_consequential": True,
        },
        environment_handle=_make_environment_handle(),
    )

    assert result.verdict is not None
    assert result.verdict.status is CommitmentStatus.UNCERTIFIED


def test_candidate_bearing_openai_event_stays_out_of_certification_and_returns_no_verdict() -> None:
    result = evaluate_openai_host_commitment(
        "response.output_text.delta",
        {"stop_fields": {"claim_id": "candidate-1"}},
        environment_handle=_make_environment_handle(),
    )

    assert result.dispatch_decision.lane is DispatchLane.CANDIDATE_BEARING
    assert result.candidate is not None
    assert result.candidate.candidate_id == "candidate-1"
    assert result.verdict is None


def test_candidate_binding_prefers_direct_payload_id_then_extracted_then_synthesized() -> None:
    direct = evaluate_openai_host_commitment(
        "response.output_text.delta",
        {
            "candidate_id": "direct-1",
            "stop_fields": {"claim_id": "structured-1"},
        },
        environment_handle=_make_environment_handle(),
    )
    extracted = evaluate_openai_host_commitment(
        "response.output_text.delta",
        {
            "stop_fields": {"claim_id": "structured-2"},
        },
        environment_handle=_make_environment_handle(),
    )
    first_synthesized = evaluate_openai_host_commitment(
        "response.output_text.delta",
        {
            "response_id": "oa-7",
            "stop_fields": {"claim_summary": "done"},
        },
        environment_handle=_make_environment_handle(),
    )
    second_synthesized = evaluate_openai_host_commitment(
        "response.output_text.delta",
        {
            "response_id": "oa-7",
            "stop_fields": {"claim_summary": "done"},
        },
        environment_handle=_make_environment_handle(),
    )

    direct_metadata = {field.key: field.value for field in direct.candidate.metadata} if direct.candidate else {}
    extracted_metadata = (
        {field.key: field.value for field in extracted.candidate.metadata}
        if extracted.candidate
        else {}
    )
    synthesized_metadata = (
        {field.key: field.value for field in first_synthesized.candidate.metadata}
        if first_synthesized.candidate
        else {}
    )

    assert direct.candidate is not None
    assert direct.candidate.candidate_id == "direct-1"
    assert direct_metadata["candidate_id_source"] == "payload:candidate_id"

    assert extracted.candidate is not None
    assert extracted.candidate.candidate_id == "structured-2"
    assert extracted_metadata["candidate_id_source"] == "payload.stop_fields:claim_id"

    assert first_synthesized.candidate is not None
    assert second_synthesized.candidate is not None
    assert first_synthesized.candidate.candidate_id == second_synthesized.candidate.candidate_id
    assert first_synthesized.candidate.candidate_id.startswith("local-candidate-")
    assert synthesized_metadata["candidate_id_source"] == "synthesized-local"
    assert synthesized_metadata["candidate_id_synthesized"] is True


def _make_environment_handle() -> CommitmentEnvironmentHandle:
    return CommitmentEnvironmentHandle(
        available_query_kinds=frozenset({EXECUTION_TRACE}),
        capability_tags=frozenset({"trace/read"}),
    )
