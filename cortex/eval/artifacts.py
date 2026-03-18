"""Minimal contradiction-preserving evaluation artifact schemas."""

from __future__ import annotations

from dataclasses import dataclass, field

from cortex.core.commitments import CommitmentStatus
from cortex.core.envelopes import MetadataField
from cortex.core.errors import ContradictionRecord, DegradationRecord


@dataclass(frozen=True, slots=True)
class EventTraceArtifact:
    trace_id: str | None = None
    event_refs: tuple[str, ...] = field(default_factory=tuple)
    record_refs: tuple[str, ...] = field(default_factory=tuple)
    contradiction_refs: tuple[ContradictionRecord, ...] = field(default_factory=tuple)
    degradation_refs: tuple[DegradationRecord, ...] = field(default_factory=tuple)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class CurrentPairFragment:
    event_trace: EventTraceArtifact
    verdict_status: CommitmentStatus
    candidate_id: str | None = None
    verdict_reason_code: str | None = None
    contradiction_refs: tuple[ContradictionRecord, ...] = field(default_factory=tuple)
    degradation_refs: tuple[DegradationRecord, ...] = field(default_factory=tuple)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if (
            self.verdict_status is CommitmentStatus.CERTIFIED
            and not (isinstance(self.candidate_id, str) and self.candidate_id.strip())
        ):
            raise ValueError(
                "CurrentPairFragment verdict_status=CERTIFIED requires a non-empty candidate_id.",
            )


@dataclass(frozen=True, slots=True)
class BlockerFragment:
    reason_code: str
    boundary_tags: frozenset[str] = field(default_factory=frozenset)
    capability_tags: frozenset[str] = field(default_factory=frozenset)
    contradiction_refs: tuple[ContradictionRecord, ...] = field(default_factory=tuple)
    degradation_refs: tuple[DegradationRecord, ...] = field(default_factory=tuple)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.reason_code.strip():
            raise ValueError("BlockerFragment.reason_code must be non-empty after trimming.")


__all__ = [
    "BlockerFragment",
    "CurrentPairFragment",
    "EventTraceArtifact",
]
