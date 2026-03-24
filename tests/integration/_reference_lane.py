"""Reference-lane-specific builders for integration test setup reuse."""

from __future__ import annotations

from cortex.core.commitments import (
    BoundaryAssessment,
    CommitmentStatus,
    ProvenanceEvidenceRef,
    ProvenanceManifest,
)
from cortex.core.dispatch import DispatchLane
from cortex.core.errors import ContradictionRecord, DegradationRecord
from cortex.core.environment import CommitmentEnvironmentHandle, EXECUTION_TRACE
from cortex.drivers.reference_host_commitment import (
    ReferenceHostCommitmentResult,
    evaluate_reference_host_commitment,
)
from cortex.drivers.reference_host_neutral import (
    NeutralContinuationCode,
    ReferenceHostNeutralResult,
    evaluate_reference_host_neutral,
)
from cortex.eval.artifacts import CurrentPairFragment
from cortex.eval.packets import EvaluationPacket


def cheap_path_event(
    *,
    event_name: str = "ContextLoad",
    session_id: str = " session-1 ",
) -> tuple[str, dict[str, object]]:
    return event_name, {"session_id": session_id}


def candidate_bearing_event(
    *,
    event_name: str = "ApprovalRequest",
    candidate_id: str = "candidate-1",
) -> tuple[str, dict[str, object]]:
    return event_name, {"candidate_id": candidate_id}


def full_commitment_event(
    *,
    event_name: str = "ApprovalResult",
    commitment_id: str = "commit-1",
    session_id: str | None = None,
    externally_consequential: bool = True,
) -> tuple[str, dict[str, object]]:
    payload: dict[str, object] = {
        "commitment_id": commitment_id,
        "externally_consequential": externally_consequential,
    }
    if session_id is not None:
        payload["session_id"] = session_id
    return event_name, payload


def reference_environment_handle() -> CommitmentEnvironmentHandle:
    return CommitmentEnvironmentHandle(
        available_query_kinds=frozenset({EXECUTION_TRACE}),
        capability_tags=frozenset({"trace/read"}),
    )


def provenance_manifest_for(
    reference_id: str,
    *,
    source_family: str = "result_artifact",
) -> ProvenanceManifest:
    return ProvenanceManifest(
        evidence_refs=(
            ProvenanceEvidenceRef(
                source_family=source_family,
                reference_id=reference_id,
            ),
        ),
    )


def evaluate_reference_cheap_path_case(
    *,
    event_name: str = "ContextLoad",
    session_id: str = " session-1 ",
    allow_message_commitment_fallback: bool = False,
) -> ReferenceHostNeutralResult:
    return evaluate_reference_host_neutral(
        *cheap_path_event(
            event_name=event_name,
            session_id=session_id,
        ),
        allow_message_commitment_fallback=allow_message_commitment_fallback,
    )


def evaluate_reference_candidate_bearing_case(
    *,
    event_name: str = "ApprovalRequest",
    candidate_id: str = "candidate-1",
    allow_message_commitment_fallback: bool = False,
) -> ReferenceHostCommitmentResult:
    return evaluate_reference_host_commitment(
        *candidate_bearing_event(
            event_name=event_name,
            candidate_id=candidate_id,
        ),
        environment_handle=reference_environment_handle(),
        allow_message_commitment_fallback=allow_message_commitment_fallback,
    )


def evaluate_reference_full_commitment_case(
    *,
    commitment_id: str,
    provenance_reference_id: str | None = None,
    provenance_source_family: str = "result_artifact",
    session_id: str | None = None,
    boundary_assessment: BoundaryAssessment | None = None,
    degradation_refs: tuple[DegradationRecord, ...] = (),
    contradiction_refs: tuple[ContradictionRecord, ...] = (),
) -> ReferenceHostCommitmentResult:
    event_name, payload = full_commitment_event(
        commitment_id=commitment_id,
        session_id=session_id,
    )
    provenance_manifest = None
    if provenance_reference_id is not None:
        provenance_manifest = provenance_manifest_for(
            provenance_reference_id,
            source_family=provenance_source_family,
        )
    return evaluate_reference_host_commitment(
        event_name,
        payload,
        environment_handle=reference_environment_handle(),
        provenance_manifest=provenance_manifest,
        boundary_assessment=boundary_assessment,
        degradation_refs=degradation_refs,
        contradiction_refs=contradiction_refs,
    )


def assert_reference_cheap_path_neutral_allowed(
    result: ReferenceHostNeutralResult,
) -> None:
    assert result.dispatch_decision.lane is DispatchLane.CHEAP
    assert result.neutral_decision.allowed is True
    assert result.neutral_decision.result_code is NeutralContinuationCode.NEUTRAL_ALLOWED


def assert_reference_candidate_bearing_without_verdict(
    result: ReferenceHostCommitmentResult,
    *,
    expected_candidate_id: str = "candidate-1",
) -> None:
    assert result.dispatch_decision.lane is DispatchLane.CANDIDATE_BEARING
    assert result.candidate is not None
    assert result.candidate.candidate_id == expected_candidate_id
    assert result.verdict is None


def assert_reference_full_commitment_certified(
    result: ReferenceHostCommitmentResult,
) -> None:
    assert result.dispatch_decision.lane is DispatchLane.FULL_COMMITMENT
    assert_reference_verdict_status(result, CommitmentStatus.CERTIFIED)


def host_surface_degradation_pair(
    *,
    source_tag: str = "host-check",
    summary: str = "expected write receipt was absent",
    evidence_tags: frozenset[str] = frozenset({"receipt-missing"}),
    reason_code: str = "host-surface-degraded",
    capability_tags: frozenset[str] = frozenset({"external/write"}),
) -> tuple[ContradictionRecord, DegradationRecord]:
    contradiction = ContradictionRecord(
        source_tag=source_tag,
        summary=summary,
        evidence_tags=evidence_tags,
    )
    degradation = DegradationRecord(
        reason_code=reason_code,
        capability_tags=capability_tags,
        contradiction_records=(contradiction,),
    )
    return contradiction, degradation


def assert_reference_commitment_result_preserves_degradation_pair(
    result: ReferenceHostCommitmentResult,
    contradiction: ContradictionRecord,
    degradation: DegradationRecord,
) -> None:
    assert result.verdict is not None
    assert result.verdict.degradation_refs == (degradation,)
    assert contradiction in result.verdict.contradiction_refs


def assert_reference_packet_preserves_degradation_pair(
    current_pair: CurrentPairFragment,
    packet: EvaluationPacket,
    contradiction: ContradictionRecord,
    degradation: DegradationRecord,
) -> None:
    assert current_pair.contradiction_refs == (contradiction,)
    assert current_pair.degradation_refs == (degradation,)
    assert packet.contradiction_refs == (contradiction,)
    assert packet.degradation_refs == (degradation,)


def assert_reference_verdict_status(
    result: ReferenceHostCommitmentResult,
    expected_status: CommitmentStatus,
) -> None:
    assert result.verdict is not None
    assert result.verdict.status is expected_status


def assert_same_verdict(
    baseline: ReferenceHostCommitmentResult,
    with_aux_present: ReferenceHostCommitmentResult,
) -> None:
    assert with_aux_present.verdict == baseline.verdict
