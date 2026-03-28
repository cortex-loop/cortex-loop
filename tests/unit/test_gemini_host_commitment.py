"""Focused tests for the Gemini host commitment-path slice."""

import pytest

from cortex.core.commitment_extract import CommitmentExtractionResult
from cortex.core.commitments import (
    BoundaryAssessment,
    CommitmentCandidate,
    CommitmentStatus,
    ProvenanceEvidenceRef,
    ProvenanceManifest,
)
from cortex.core.dispatch import DispatchLane
from cortex.core.environment import CommitmentEnvironmentHandle, EXECUTION_TRACE
from cortex.drivers.gemini_host import observe_gemini_host_event
from cortex.drivers.gemini_host_commitment import (
    GeminiHostCommitmentResult,
    bind_gemini_host_candidate,
    evaluate_gemini_host_commitment,
)


def test_full_commitment_gemini_event_with_concrete_provenance_yields_certified() -> None:
    result = evaluate_gemini_host_commitment(
        "interaction.complete",
        {
            "commitment_id": "gemini-commit-1",
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
    assert result.candidate.candidate_id == "gemini-commit-1"
    assert result.verdict is not None
    assert result.verdict.status is CommitmentStatus.CERTIFIED


def test_malformed_native_commitment_carrier_surfaces_warning_while_preserving_full_commitment_path() -> None:
    result = evaluate_gemini_host_commitment(
        "interaction.complete",
        {
            "commitment_fields_source": "native",
            "commitment_fields": ["not", "a", "mapping"],
            "externally_consequential": True,
        },
        environment_handle=_make_environment_handle(),
        provenance_manifest=ProvenanceManifest(
            evidence_refs=(
                ProvenanceEvidenceRef(
                    source_family="result_artifact",
                    reference_id="artifact-native-warning-2",
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
    result = evaluate_gemini_host_commitment(
        "interaction.complete",
        {
            "commitment_id": "gemini-commit-2",
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
    result = evaluate_gemini_host_commitment(
        "interaction.complete",
        {
            "commitment_id": "gemini-commit-3",
            "externally_consequential": True,
        },
        environment_handle=_make_environment_handle(),
    )

    assert result.verdict is not None
    assert result.verdict.status is CommitmentStatus.UNCERTIFIED


def test_candidate_bearing_gemini_event_stays_out_of_certification_and_returns_no_verdict() -> None:
    result = evaluate_gemini_host_commitment(
        "content.delta",
        {"stop_fields": {"claim_id": "candidate-1"}},
        environment_handle=_make_environment_handle(),
    )

    assert result.dispatch_decision.lane is DispatchLane.CANDIDATE_BEARING
    assert result.candidate is not None
    assert result.candidate.candidate_id == "candidate-1"
    assert result.verdict is None


def test_candidate_binding_prefers_direct_payload_id_then_extracted_then_synthesized() -> None:
    direct = evaluate_gemini_host_commitment(
        "content.delta",
        {
            "candidate_id": "direct-1",
            "stop_fields": {"claim_id": "structured-1"},
        },
        environment_handle=_make_environment_handle(),
    )
    extracted = evaluate_gemini_host_commitment(
        "content.delta",
        {
            "stop_fields": {"claim_id": "structured-2"},
        },
        environment_handle=_make_environment_handle(),
    )
    first_synthesized = evaluate_gemini_host_commitment(
        "content.delta",
        {
            "interaction": {"id": "gm-7"},
            "stop_fields": {"claim_summary": "done"},
        },
        environment_handle=_make_environment_handle(),
    )
    second_synthesized = evaluate_gemini_host_commitment(
        "content.delta",
        {
            "interaction": {"id": "gm-7"},
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


def test_gemini_host_commitment_result_requires_typed_components_and_clean_warnings() -> None:
    bound = observe_gemini_host_event("content.delta", {"interaction": {"id": "gm-result-1"}})
    result = evaluate_gemini_host_commitment(
        "content.delta",
        {},
        environment_handle=_make_environment_handle(),
    )

    with pytest.raises(
        TypeError,
        match="bound_event must be BoundGeminiHostEvent, got str",
    ):
        GeminiHostCommitmentResult(
            bound_event="not-a-bound-event",
            dispatch_decision=result.dispatch_decision,
        )

    with pytest.raises(
        TypeError,
        match="dispatch_decision must be DispatchDecision, got str",
    ):
        GeminiHostCommitmentResult(
            bound_event=bound,
            dispatch_decision="not-a-dispatch",
        )

    with pytest.raises(
        TypeError,
        match="extraction_result must be CommitmentExtractionResult \\| None, got str",
    ):
        GeminiHostCommitmentResult(
            bound_event=bound,
            dispatch_decision=result.dispatch_decision,
            extraction_result="not-an-extraction",
        )

    with pytest.raises(
        TypeError,
        match="candidate must be CommitmentCandidate \\| None, got str",
    ):
        GeminiHostCommitmentResult(
            bound_event=bound,
            dispatch_decision=result.dispatch_decision,
            candidate="not-a-candidate",
        )

    with pytest.raises(
        ValueError,
        match="warnings must contain only non-empty values after trimming",
    ):
        GeminiHostCommitmentResult(
            bound_event=bound,
            dispatch_decision=result.dispatch_decision,
            warnings=("   ",),
        )

    with pytest.raises(
        TypeError,
        match="warnings must be tuple\\[str, \\.\\.\\.\\], got list",
    ):
        GeminiHostCommitmentResult(
            bound_event=bound,
            dispatch_decision=result.dispatch_decision,
            warnings=["x"],
        )


def test_gemini_commitment_entrypoints_require_typed_inputs() -> None:
    bound = observe_gemini_host_event("content.delta", {"interaction": {"id": "gm-bind-1"}})
    result = evaluate_gemini_host_commitment(
        "content.delta",
        {},
        environment_handle=_make_environment_handle(),
    )
    extraction = CommitmentExtractionResult(
        commitment_fields=None,
        carrier_source="none",
        fallback_used=False,
        normalization_count=0,
        warnings=(),
        structured_payload_violation=False,
    )

    candidate, warnings = bind_gemini_host_candidate(
        bound,
        result.dispatch_decision,
        extraction,
    )
    assert isinstance(candidate, CommitmentCandidate)
    assert warnings == (
        "Synthesized deterministic local candidate id because no direct or extracted identifier was present.",
    )

    with pytest.raises(
        TypeError,
        match="bind_gemini_host_candidate\\.bound_event must be BoundGeminiHostEvent, got str",
    ):
        bind_gemini_host_candidate("not-a-bound-event", result.dispatch_decision)

    with pytest.raises(
        TypeError,
        match="bind_gemini_host_candidate\\.dispatch_decision must be DispatchDecision, got str",
    ):
        bind_gemini_host_candidate(bound, "not-a-dispatch")

    with pytest.raises(
        TypeError,
        match="bind_gemini_host_candidate\\.extraction_result must be CommitmentExtractionResult \\| None, got str",
    ):
        bind_gemini_host_candidate(bound, result.dispatch_decision, "not-an-extraction")

    with pytest.raises(
        TypeError,
        match="evaluate_gemini_host_commitment\\.environment_handle must be CommitmentEnvironmentHandle, got str",
    ):
        evaluate_gemini_host_commitment("content.delta", {}, environment_handle="not-an-environment")

    with pytest.raises(
        TypeError,
        match="evaluate_gemini_host_commitment\\.provenance_manifest must be ProvenanceManifest \\| None, got str",
    ):
        evaluate_gemini_host_commitment(
            "content.delta",
            {},
            environment_handle=_make_environment_handle(),
            provenance_manifest="not-a-manifest",
        )

    with pytest.raises(
        TypeError,
        match="evaluate_gemini_host_commitment\\.boundary_assessment must be BoundaryAssessment \\| None, got str",
    ):
        evaluate_gemini_host_commitment(
            "content.delta",
            {},
            environment_handle=_make_environment_handle(),
            boundary_assessment="not-a-boundary",
        )

    with pytest.raises(
        TypeError,
        match="evaluate_gemini_host_commitment\\.degradation_refs must contain only DegradationRecord instances",
    ):
        evaluate_gemini_host_commitment(
            "content.delta",
            {},
            environment_handle=_make_environment_handle(),
            degradation_refs=("not-a-degradation",),
        )

    with pytest.raises(
        TypeError,
        match="evaluate_gemini_host_commitment\\.contradiction_refs must contain only ContradictionRecord instances",
    ):
        evaluate_gemini_host_commitment(
            "content.delta",
            {},
            environment_handle=_make_environment_handle(),
            contradiction_refs=("not-a-contradiction",),
        )
