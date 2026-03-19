"""Minimal commitment-side carriers for the core substrate."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .environment import CommitmentEnvironmentHandle
from .envelopes import EventPayloadHandle, MetadataField
from .errors import ContradictionRecord, DegradationRecord
from .observation import ObservationBundle


class CommitmentStatus(Enum):
    CERTIFIED = "certified"
    UNCERTIFIED = "uncertified"
    BLOCKED = "blocked"


@dataclass(frozen=True, slots=True)
class CommitmentCandidate:
    candidate_id: str
    surface_tags: frozenset[str] = field(default_factory=frozenset)
    payload_handle: EventPayloadHandle | None = None
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not (isinstance(self.candidate_id, str) and self.candidate_id.strip()):
            raise ValueError(
                "CommitmentCandidate.candidate_id must be non-empty after trimming.",
            )
        if any(not (isinstance(tag, str) and tag.strip()) for tag in self.surface_tags):
            raise ValueError(
                "CommitmentCandidate.surface_tags must contain only non-empty values after trimming.",
            )
        if self.payload_handle is not None and not isinstance(
            self.payload_handle,
            EventPayloadHandle,
        ):
            actual_type = type(self.payload_handle).__name__
            raise TypeError(
                "CommitmentCandidate.payload_handle must be EventPayloadHandle when provided, "
                f"got {actual_type}.",
            )
        if any(not isinstance(field, MetadataField) for field in self.metadata):
            raise TypeError(
                "CommitmentCandidate.metadata must contain only MetadataField instances.",
            )


@dataclass(frozen=True, slots=True)
class ProvenanceEvidenceRef:
    source_family: str
    reference_id: str
    source_tags: frozenset[str] = field(default_factory=frozenset)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not (isinstance(self.source_family, str) and self.source_family.strip()):
            raise ValueError(
                "ProvenanceEvidenceRef.source_family must be non-empty after trimming.",
            )
        if not (isinstance(self.reference_id, str) and self.reference_id.strip()):
            raise ValueError(
                "ProvenanceEvidenceRef.reference_id must be non-empty after trimming.",
            )
        if any(not (isinstance(tag, str) and tag.strip()) for tag in self.source_tags):
            raise ValueError(
                "ProvenanceEvidenceRef.source_tags must contain only non-empty values after trimming.",
            )
        if any(not isinstance(field, MetadataField) for field in self.metadata):
            raise TypeError(
                "ProvenanceEvidenceRef.metadata must contain only MetadataField instances.",
            )


@dataclass(frozen=True, slots=True)
class ProvenanceManifest:
    evidence_refs: tuple[ProvenanceEvidenceRef, ...] = field(default_factory=tuple)
    contradiction_refs: tuple[ContradictionRecord, ...] = field(default_factory=tuple)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if any(not isinstance(ref, ProvenanceEvidenceRef) for ref in self.evidence_refs):
            raise TypeError(
                "ProvenanceManifest.evidence_refs must contain only ProvenanceEvidenceRef instances.",
            )
        if any(not isinstance(ref, ContradictionRecord) for ref in self.contradiction_refs):
            raise TypeError(
                "ProvenanceManifest.contradiction_refs must contain only ContradictionRecord instances.",
            )


def _has_concrete_evidence_ref(provenance_manifest: ProvenanceManifest | None) -> bool:
    if not isinstance(provenance_manifest, ProvenanceManifest):
        return False
    return any(ref.reference_id.strip() for ref in provenance_manifest.evidence_refs)


@dataclass(frozen=True, slots=True)
class BoundaryAssessment:
    blocked: bool
    reason_code: str | None = None
    boundary_tags: frozenset[str] = field(default_factory=frozenset)
    capability_tags: frozenset[str] = field(default_factory=frozenset)
    contradiction_refs: tuple[ContradictionRecord, ...] = field(default_factory=tuple)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.blocked and not (isinstance(self.reason_code, str) and self.reason_code.strip()):
            raise ValueError(
                "BoundaryAssessment blocked=True requires a non-empty reason_code.",
            )


@dataclass(frozen=True, slots=True)
class CertificationContext:
    candidate: CommitmentCandidate
    observation: ObservationBundle
    environment_handle: CommitmentEnvironmentHandle
    wake_reasons: frozenset[str] = field(default_factory=frozenset)
    boundary_tags: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if not isinstance(self.environment_handle, CommitmentEnvironmentHandle):
            actual_type = type(self.environment_handle).__name__
            raise TypeError(
                "CertificationContext requires CommitmentEnvironmentHandle, "
                f"got {actual_type}."
            )


@dataclass(frozen=True, slots=True)
class CommitmentVerdict:
    status: CommitmentStatus
    candidate: CommitmentCandidate
    provenance_manifest: ProvenanceManifest | None = None
    boundary_assessment: BoundaryAssessment | None = None
    degradation_refs: tuple[DegradationRecord, ...] = field(default_factory=tuple)
    contradiction_refs: tuple[ContradictionRecord, ...] = field(default_factory=tuple)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        boundary_is_blocked = (
            isinstance(self.boundary_assessment, BoundaryAssessment)
            and self.boundary_assessment.blocked
        )
        has_concrete_provenance = _has_concrete_evidence_ref(self.provenance_manifest)
        if self.status is CommitmentStatus.BLOCKED and not boundary_is_blocked:
            raise ValueError(
                "CommitmentVerdict status=BLOCKED requires boundary_assessment with blocked=True.",
            )
        if self.status is not CommitmentStatus.BLOCKED and boundary_is_blocked:
            raise ValueError(
                "CommitmentVerdict boundary_assessment blocked=True requires status=BLOCKED.",
            )
        if self.status is CommitmentStatus.CERTIFIED and not has_concrete_provenance:
            raise ValueError(
                "CommitmentVerdict status=CERTIFIED requires provenance_manifest with at least one concrete evidence reference.",
            )


__all__ = [
    "BoundaryAssessment",
    "CertificationContext",
    "CommitmentCandidate",
    "CommitmentStatus",
    "CommitmentVerdict",
    "ProvenanceEvidenceRef",
    "ProvenanceManifest",
]
