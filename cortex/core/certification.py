"""Conservative certification execution over the existing core carriers."""

from __future__ import annotations

from .commitments import (
    BoundaryAssessment,
    CertificationContext,
    CommitmentStatus,
    CommitmentVerdict,
    ProvenanceManifest,
)
from .errors import ContradictionRecord, DegradationRecord


def certify_commitment(
    context: CertificationContext,
    *,
    provenance_manifest: ProvenanceManifest | None,
    boundary_assessment: BoundaryAssessment,
    degradation_refs: tuple[DegradationRecord, ...] = (),
    contradiction_refs: tuple[ContradictionRecord, ...] = (),
) -> CommitmentVerdict:
    preserved_contradictions = _merge_contradiction_refs(
        contradiction_refs,
        provenance_manifest.contradiction_refs if provenance_manifest is not None else (),
        boundary_assessment.contradiction_refs,
        *(degradation.contradiction_records for degradation in degradation_refs),
    )

    if boundary_assessment.blocked:
        status = CommitmentStatus.BLOCKED
    elif _has_concrete_evidence(provenance_manifest):
        status = CommitmentStatus.CERTIFIED
    else:
        status = CommitmentStatus.UNCERTIFIED

    return CommitmentVerdict(
        status=status,
        candidate=context.candidate,
        provenance_manifest=provenance_manifest,
        boundary_assessment=boundary_assessment,
        degradation_refs=degradation_refs,
        contradiction_refs=preserved_contradictions,
    )


def _has_concrete_evidence(provenance_manifest: ProvenanceManifest | None) -> bool:
    if provenance_manifest is None:
        return False
    return any(ref.reference_id.strip() for ref in provenance_manifest.evidence_refs)


def _merge_contradiction_refs(
    *groups: tuple[ContradictionRecord, ...],
) -> tuple[ContradictionRecord, ...]:
    merged: list[ContradictionRecord] = []
    for group in groups:
        for record in group:
            if record not in merged:
                merged.append(record)
    return tuple(merged)


__all__ = ["certify_commitment"]
