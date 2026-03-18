"""Unit tests for conservative certification execution and minimal artifacts."""

from cortex.core.certification import certify_commitment
from cortex.core.commitments import (
    BoundaryAssessment,
    CertificationContext,
    CommitmentCandidate,
    CommitmentStatus,
    ProvenanceEvidenceRef,
    ProvenanceManifest,
)
from cortex.core.environment import CommitmentEnvironmentHandle, EXECUTION_TRACE
from cortex.core.errors import ContradictionRecord, DegradationRecord
from cortex.core.observation import ObservationBundle, PayloadView
from cortex.core.envelopes import LifecycleEventEnvelope
from cortex.eval.artifacts import BlockerFragment, CurrentPairFragment, EventTraceArtifact


def test_certify_commitment_returns_certified_with_concrete_evidence() -> None:
    verdict = certify_commitment(
        _make_context(),
        provenance_manifest=ProvenanceManifest(
            evidence_refs=(
                ProvenanceEvidenceRef(
                    source_family="result_artifact",
                    reference_id="artifact-1",
                ),
            ),
        ),
        boundary_assessment=BoundaryAssessment(blocked=False),
    )

    assert verdict.status is CommitmentStatus.CERTIFIED


def test_certify_commitment_returns_uncertified_without_concrete_evidence() -> None:
    verdict = certify_commitment(
        _make_context(),
        provenance_manifest=ProvenanceManifest(),
        boundary_assessment=BoundaryAssessment(blocked=False),
    )

    assert verdict.status is CommitmentStatus.UNCERTIFIED


def test_certify_commitment_returns_blocked_when_boundary_is_blocked() -> None:
    verdict = certify_commitment(
        _make_context(),
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

    assert verdict.status is CommitmentStatus.BLOCKED


def test_certify_commitment_preserves_contradictions_and_degradations() -> None:
    contradiction = ContradictionRecord(
        source_tag="runtime-record",
        summary="runtime record conflicts with visible state",
        evidence_tags=frozenset({"runtime-record", "external-state"}),
    )
    degradation = DegradationRecord(
        reason_code="partial-provenance",
        capability_tags=frozenset({"external-record"}),
        contradiction_records=(contradiction,),
    )
    verdict = certify_commitment(
        _make_context(),
        provenance_manifest=ProvenanceManifest(
            evidence_refs=(
                ProvenanceEvidenceRef(
                    source_family="lifecycle_trace",
                    reference_id="trace-1",
                ),
            ),
            contradiction_refs=(contradiction,),
        ),
        boundary_assessment=BoundaryAssessment(
            blocked=False,
            contradiction_refs=(contradiction,),
        ),
        degradation_refs=(degradation,),
        contradiction_refs=(contradiction,),
    )

    assert verdict.status is CommitmentStatus.CERTIFIED
    assert verdict.degradation_refs == (degradation,)
    assert verdict.contradiction_refs == (contradiction,)


def test_blocker_fragment_preserves_reason_and_contradictions() -> None:
    contradiction = ContradictionRecord(
        source_tag="boundary-check",
        summary="approval boundary was not satisfied",
        evidence_tags=frozenset({"approval"}),
    )
    blocker = BlockerFragment(
        reason_code="approval-required",
        boundary_tags=frozenset({"external-boundary"}),
        contradiction_refs=(contradiction,),
    )

    assert blocker.reason_code == "approval-required"
    assert blocker.boundary_tags == frozenset({"external-boundary"})
    assert blocker.contradiction_refs == (contradiction,)


def test_current_pair_fragment_carries_event_trace_and_verdict_summary() -> None:
    contradiction = ContradictionRecord(
        source_tag="artifact",
        summary="artifact set is incomplete",
        evidence_tags=frozenset({"artifact"}),
    )
    trace = EventTraceArtifact(
        trace_id="trace-1",
        event_refs=("event-1", "event-2"),
        record_refs=("record-1",),
        contradiction_refs=(contradiction,),
    )
    fragment = CurrentPairFragment(
        event_trace=trace,
        verdict_status=CommitmentStatus.UNCERTIFIED,
        candidate_id="candidate-1",
        verdict_reason_code="insufficient-evidence",
        contradiction_refs=(contradiction,),
    )

    assert fragment.event_trace is trace
    assert fragment.verdict_status is CommitmentStatus.UNCERTIFIED
    assert fragment.verdict_reason_code == "insufficient-evidence"
    assert fragment.contradiction_refs == (contradiction,)


def _make_context() -> CertificationContext:
    return CertificationContext(
        candidate=CommitmentCandidate(candidate_id="candidate-1"),
        observation=ObservationBundle(
            event=LifecycleEventEnvelope(native_event_name="turn/complete"),
            payload_view=PayloadView(),
        ),
        environment_handle=CommitmentEnvironmentHandle(
            available_query_kinds=frozenset({EXECUTION_TRACE}),
        ),
        wake_reasons=frozenset({"candidate-present"}),
    )
