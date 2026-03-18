"""Reference-lane-specific builders for integration test setup reuse."""

from __future__ import annotations

from cortex.core.errors import ContradictionRecord, DegradationRecord
from cortex.core.commitments import ProvenanceEvidenceRef, ProvenanceManifest
from cortex.core.environment import CommitmentEnvironmentHandle, EXECUTION_TRACE
from cortex.drivers.reference_host_commitment import ReferenceHostCommitmentResult
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
