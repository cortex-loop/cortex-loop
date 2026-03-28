"""Unit tests for conservative certification execution and minimal artifacts."""

import pytest

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


def test_certify_commitment_cannot_start_from_blocked_boundary_without_reason() -> None:
    with pytest.raises(ValueError, match="blocked=True requires a non-empty reason_code"):
        certify_commitment(
            _make_context(),
            provenance_manifest=ProvenanceManifest(
                evidence_refs=(
                    ProvenanceEvidenceRef(
                        source_family="external_artifact",
                        reference_id="artifact-blocked-no-reason",
                    ),
                ),
            ),
            boundary_assessment=BoundaryAssessment(
                blocked=True,
                reason_code="   ",
            ),
        )


def test_certify_commitment_cannot_start_from_blank_candidate_id() -> None:
    with pytest.raises(ValueError, match="candidate_id must be non-empty after trimming"):
        certify_commitment(
            CertificationContext(
                candidate=CommitmentCandidate(candidate_id="   "),
                observation=ObservationBundle(
                    event=LifecycleEventEnvelope(native_event_name="turn/complete"),
                    payload_view=PayloadView(),
                ),
                environment_handle=CommitmentEnvironmentHandle(
                    available_query_kinds=frozenset({EXECUTION_TRACE}),
                ),
                wake_reasons=frozenset({"candidate-present"}),
            ),
            provenance_manifest=ProvenanceManifest(
                evidence_refs=(
                    ProvenanceEvidenceRef(
                        source_family="result_artifact",
                        reference_id="artifact-blank-candidate",
                    ),
                ),
            ),
            boundary_assessment=BoundaryAssessment(blocked=False),
        )


def test_certify_commitment_cannot_start_from_blank_evidence_source_family() -> None:
    with pytest.raises(ValueError, match="source_family must be non-empty after trimming"):
        certify_commitment(
            _make_context(),
            provenance_manifest=ProvenanceManifest(
                evidence_refs=(
                    ProvenanceEvidenceRef(
                        source_family="",
                        reference_id="artifact-blank-family",
                    ),
                ),
            ),
            boundary_assessment=BoundaryAssessment(blocked=False),
        )


def test_certify_commitment_cannot_start_from_blank_evidence_reference_id() -> None:
    with pytest.raises(ValueError, match="reference_id must be non-empty after trimming"):
        certify_commitment(
            _make_context(),
            provenance_manifest=ProvenanceManifest(
                evidence_refs=(
                    ProvenanceEvidenceRef(
                        source_family="result_artifact",
                        reference_id="",
                    ),
                ),
            ),
            boundary_assessment=BoundaryAssessment(blocked=False),
        )


def test_certify_commitment_requires_typed_context() -> None:
    verdict = certify_commitment(
        _make_context(),
        provenance_manifest=None,
        boundary_assessment=BoundaryAssessment(blocked=False),
    )

    assert verdict.status is CommitmentStatus.UNCERTIFIED

    with pytest.raises(
        TypeError,
        match=r"certify_commitment\.context must be CertificationContext, got str\.",
    ):
        certify_commitment(
            "not-a-context",
            provenance_manifest=None,
            boundary_assessment=BoundaryAssessment(blocked=False),
        )


def test_certify_commitment_requires_typed_provenance_manifest() -> None:
    verdict = certify_commitment(
        _make_context(),
        provenance_manifest=None,
        boundary_assessment=BoundaryAssessment(blocked=False),
    )

    assert verdict.provenance_manifest is None

    with pytest.raises(
        TypeError,
        match=(
            r"certify_commitment\.provenance_manifest must be "
            r"ProvenanceManifest \| None, got str\."
        ),
    ):
        certify_commitment(
            _make_context(),
            provenance_manifest="not-a-manifest",
            boundary_assessment=BoundaryAssessment(blocked=False),
        )


def test_certify_commitment_requires_typed_boundary_assessment() -> None:
    verdict = certify_commitment(
        _make_context(),
        provenance_manifest=None,
        boundary_assessment=BoundaryAssessment(blocked=False),
    )

    assert verdict.boundary_assessment == BoundaryAssessment(blocked=False)

    with pytest.raises(
        TypeError,
        match=(
            r"certify_commitment\.boundary_assessment must be "
            r"BoundaryAssessment, got str\."
        ),
    ):
        certify_commitment(
            _make_context(),
            provenance_manifest=None,
            boundary_assessment="not-a-boundary",
        )


def test_certify_commitment_requires_typed_degradation_refs() -> None:
    contradiction = ContradictionRecord(
        source_tag="runtime-record",
        summary="runtime record conflicts with visible state",
        evidence_tags=frozenset({"runtime-record"}),
    )
    degradation = DegradationRecord(
        reason_code="partial-provenance",
        capability_tags=frozenset({"external-record"}),
        contradiction_records=(contradiction,),
    )
    verdict = certify_commitment(
        _make_context(),
        provenance_manifest=None,
        boundary_assessment=BoundaryAssessment(blocked=False),
        degradation_refs=(degradation,),
    )

    assert verdict.degradation_refs == (degradation,)

    with pytest.raises(
        TypeError,
        match=(
            r"certify_commitment\.degradation_refs must contain only "
            r"DegradationRecord instances\."
        ),
    ):
        certify_commitment(
            _make_context(),
            provenance_manifest=None,
            boundary_assessment=BoundaryAssessment(blocked=False),
            degradation_refs=("not-a-degradation",),
        )


def test_certify_commitment_requires_typed_contradiction_refs() -> None:
    contradiction = ContradictionRecord(
        source_tag="runtime-record",
        summary="runtime record conflicts with visible state",
        evidence_tags=frozenset({"runtime-record"}),
    )
    verdict = certify_commitment(
        _make_context(),
        provenance_manifest=None,
        boundary_assessment=BoundaryAssessment(blocked=False),
        contradiction_refs=(contradiction,),
    )

    assert verdict.contradiction_refs == (contradiction,)

    with pytest.raises(
        TypeError,
        match=(
            r"certify_commitment\.contradiction_refs must contain only "
            r"ContradictionRecord instances\."
        ),
    ):
        certify_commitment(
            _make_context(),
            provenance_manifest=None,
            boundary_assessment=BoundaryAssessment(blocked=False),
            contradiction_refs=("not-a-contradiction",),
        )


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


def test_blocker_fragment_rejects_empty_or_whitespace_only_reason_code() -> None:
    blocker = BlockerFragment(reason_code="approval-required")

    assert blocker.reason_code == "approval-required"

    with pytest.raises(ValueError, match="reason_code must be non-empty after trimming"):
        BlockerFragment(reason_code="")

    with pytest.raises(ValueError, match="reason_code must be non-empty after trimming"):
        BlockerFragment(reason_code="   ")


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


def test_certified_current_pair_fragment_requires_non_empty_candidate_id() -> None:
    trace = EventTraceArtifact(trace_id="trace-certified")
    fragment = CurrentPairFragment(
        event_trace=trace,
        verdict_status=CommitmentStatus.CERTIFIED,
        candidate_id="candidate-certified",
    )

    assert fragment.candidate_id == "candidate-certified"

    with pytest.raises(
        ValueError,
        match="verdict_status=CERTIFIED requires a non-empty candidate_id",
    ):
        CurrentPairFragment(
            event_trace=trace,
            verdict_status=CommitmentStatus.CERTIFIED,
            candidate_id=None,
        )

    with pytest.raises(
        ValueError,
        match="verdict_status=CERTIFIED requires a non-empty candidate_id",
    ):
        CurrentPairFragment(
            event_trace=trace,
            verdict_status=CommitmentStatus.CERTIFIED,
            candidate_id="   ",
        )


def test_event_trace_and_current_pair_fragments_require_typed_members() -> None:
    contradiction = ContradictionRecord(
        source_tag="artifact",
        summary="artifact set is incomplete",
        evidence_tags=frozenset({"artifact"}),
    )
    degradation = DegradationRecord(
        reason_code="partial-evidence",
        capability_tags=frozenset({"artifact"}),
        contradiction_records=(contradiction,),
    )
    trace = EventTraceArtifact(
        trace_id="trace-typed",
        event_refs=("event-1",),
        record_refs=("record-1",),
        contradiction_refs=(contradiction,),
        degradation_refs=(degradation,),
    )

    assert trace.trace_id == "trace-typed"

    with pytest.raises(
        ValueError,
        match="EventTraceArtifact\\.trace_id must be non-empty after trimming",
    ):
        EventTraceArtifact(trace_id="   ")

    with pytest.raises(
        ValueError,
        match="EventTraceArtifact\\.event_refs must contain only non-empty values after trimming",
    ):
        EventTraceArtifact(event_refs=("   ",))

    with pytest.raises(
        TypeError,
        match="EventTraceArtifact\\.contradiction_refs must contain only ContradictionRecord instances",
    ):
        EventTraceArtifact(contradiction_refs=("not-a-contradiction",))

    with pytest.raises(
        TypeError,
        match="CurrentPairFragment\\.event_trace must be EventTraceArtifact, got str",
    ):
        CurrentPairFragment(
            event_trace="not-a-trace",
            verdict_status=CommitmentStatus.UNCERTIFIED,
        )

    with pytest.raises(
        ValueError,
        match="CurrentPairFragment\\.candidate_id must be non-empty after trimming",
    ):
        CurrentPairFragment(
            event_trace=trace,
            verdict_status=CommitmentStatus.UNCERTIFIED,
            candidate_id="   ",
        )

    with pytest.raises(
        TypeError,
        match="CurrentPairFragment\\.metadata must contain only MetadataField instances",
    ):
        CurrentPairFragment(
            event_trace=trace,
            verdict_status=CommitmentStatus.UNCERTIFIED,
            metadata=("not-a-field",),
        )


def test_blocker_fragment_requires_clean_tags_and_typed_members() -> None:
    contradiction = ContradictionRecord(
        source_tag="boundary-check",
        summary="approval boundary was not satisfied",
        evidence_tags=frozenset({"approval"}),
    )
    degradation = DegradationRecord(
        reason_code="boundary-evidence-partial",
        capability_tags=frozenset({"approval"}),
        contradiction_records=(contradiction,),
    )
    blocker = BlockerFragment(
        reason_code="approval-required",
        boundary_tags=frozenset({"external-boundary"}),
        capability_tags=frozenset({"approval"}),
        contradiction_refs=(contradiction,),
        degradation_refs=(degradation,),
    )

    assert blocker.reason_code == "approval-required"

    with pytest.raises(
        ValueError,
        match="BlockerFragment\\.boundary_tags must contain only non-empty values after trimming",
    ):
        BlockerFragment(reason_code="approval-required", boundary_tags=frozenset({"   "}))

    with pytest.raises(
        TypeError,
        match="BlockerFragment\\.degradation_refs must contain only DegradationRecord instances",
    ):
        BlockerFragment(reason_code="approval-required", degradation_refs=("not-a-degradation",))


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
