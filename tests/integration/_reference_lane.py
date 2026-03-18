"""Reference-lane-specific builders for integration test setup reuse."""

from __future__ import annotations

from cortex.core.commitments import ProvenanceEvidenceRef, ProvenanceManifest
from cortex.core.environment import CommitmentEnvironmentHandle, EXECUTION_TRACE


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
