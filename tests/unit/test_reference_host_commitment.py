"""Focused tests for the reference-host commitment-path slice."""

from cortex.core.commitments import (
    BoundaryAssessment,
    CommitmentStatus,
    ProvenanceEvidenceRef,
    ProvenanceManifest,
)
from cortex.core.dispatch import DispatchLane
from cortex.core.environment import CommitmentEnvironmentHandle, EXECUTION_TRACE
from cortex.drivers.reference_host_commitment import evaluate_reference_host_commitment


def test_full_commitment_reference_host_event_with_concrete_provenance_yields_certified() -> None:
    result = evaluate_reference_host_commitment(
        "ApprovalResult",
        {
            "commitment_id": "commit-1",
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
    assert result.candidate.candidate_id == "commit-1"
    assert result.verdict is not None
    assert result.verdict.status is CommitmentStatus.CERTIFIED


def test_blocked_boundary_yields_blocked_even_when_provenance_exists() -> None:
    result = evaluate_reference_host_commitment(
        "ApprovalResult",
        {
            "commitment_id": "commit-2",
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
    result = evaluate_reference_host_commitment(
        "ApprovalResult",
        {
            "commitment_id": "commit-3",
            "externally_consequential": True,
        },
        environment_handle=_make_environment_handle(),
    )

    assert result.verdict is not None
    assert result.verdict.status is CommitmentStatus.UNCERTIFIED


def test_proposal_like_event_stays_out_of_certification_and_returns_no_verdict() -> None:
    result = evaluate_reference_host_commitment(
        "ApprovalRequest",
        {"candidate_id": "candidate-1"},
        environment_handle=_make_environment_handle(),
    )

    assert result.dispatch_decision.lane is DispatchLane.CANDIDATE_BEARING
    assert result.candidate is not None
    assert result.candidate.candidate_id == "candidate-1"
    assert result.verdict is None


def test_candidate_binding_prefers_direct_payload_id_over_extracted_structured_id() -> None:
    result = evaluate_reference_host_commitment(
        "ApprovalRequest",
        {
            "candidate_id": "direct-1",
            "stop_fields": {"claim_id": "structured-1"},
        },
        environment_handle=_make_environment_handle(),
    )

    metadata = {field.key: field.value for field in result.candidate.metadata} if result.candidate else {}

    assert result.candidate is not None
    assert result.candidate.candidate_id == "direct-1"
    assert result.extraction_result is not None
    assert result.extraction_result.carrier_source == "payload.stop_fields"
    assert metadata["candidate_id_source"] == "payload:candidate_id"


def test_candidate_binding_falls_back_to_extracted_structured_id() -> None:
    result = evaluate_reference_host_commitment(
        "ApprovalRequest",
        {
            "stop_fields": {"claim_id": "structured-2"},
        },
        environment_handle=_make_environment_handle(),
    )

    metadata = {field.key: field.value for field in result.candidate.metadata} if result.candidate else {}

    assert result.candidate is not None
    assert result.candidate.candidate_id == "structured-2"
    assert metadata["candidate_id_source"] == "payload.stop_fields:claim_id"


def test_candidate_binding_synthesizes_deterministic_local_id_when_none_is_present() -> None:
    first = evaluate_reference_host_commitment(
        "ApprovalRequest",
        {"session_id": "session-7"},
        environment_handle=_make_environment_handle(),
    )
    second = evaluate_reference_host_commitment(
        "ApprovalRequest",
        {"session_id": "session-7"},
        environment_handle=_make_environment_handle(),
    )

    metadata = {field.key: field.value for field in first.candidate.metadata} if first.candidate else {}

    assert first.candidate is not None
    assert second.candidate is not None
    assert first.candidate.candidate_id == second.candidate.candidate_id
    assert first.candidate.candidate_id.startswith("local-candidate-")
    assert metadata["candidate_id_source"] == "synthesized-local"
    assert metadata["candidate_id_synthesized"] is True


def _make_environment_handle() -> CommitmentEnvironmentHandle:
    return CommitmentEnvironmentHandle(
        available_query_kinds=frozenset({EXECUTION_TRACE}),
        capability_tags=frozenset({"trace/read"}),
    )
