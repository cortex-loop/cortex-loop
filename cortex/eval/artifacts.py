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

    def __post_init__(self) -> None:
        if self.trace_id is not None:
            if not isinstance(self.trace_id, str):
                actual_type = type(self.trace_id).__name__
                raise TypeError(
                    "EventTraceArtifact.trace_id must be str | None, "
                    f"got {actual_type}.",
                )
            if not self.trace_id.strip():
                raise ValueError("EventTraceArtifact.trace_id must be non-empty after trimming.")
        _validate_string_tuple(self.event_refs, "EventTraceArtifact.event_refs")
        _validate_string_tuple(self.record_refs, "EventTraceArtifact.record_refs")
        _validate_typed_tuple(
            self.contradiction_refs,
            ContradictionRecord,
            "EventTraceArtifact.contradiction_refs",
        )
        _validate_typed_tuple(
            self.degradation_refs,
            DegradationRecord,
            "EventTraceArtifact.degradation_refs",
        )
        _validate_typed_tuple(
            self.metadata,
            MetadataField,
            "EventTraceArtifact.metadata",
        )


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
        if not isinstance(self.event_trace, EventTraceArtifact):
            actual_type = type(self.event_trace).__name__
            raise TypeError(
                "CurrentPairFragment.event_trace must be EventTraceArtifact, "
                f"got {actual_type}.",
            )
        if not isinstance(self.verdict_status, CommitmentStatus):
            actual_type = type(self.verdict_status).__name__
            raise TypeError(
                "CurrentPairFragment.verdict_status must be CommitmentStatus, "
                f"got {actual_type}.",
            )
        if self.candidate_id is not None:
            if not isinstance(self.candidate_id, str):
                actual_type = type(self.candidate_id).__name__
                raise TypeError(
                    "CurrentPairFragment.candidate_id must be str | None, "
                    f"got {actual_type}.",
                )
        if self.verdict_reason_code is not None:
            if not isinstance(self.verdict_reason_code, str):
                actual_type = type(self.verdict_reason_code).__name__
                raise TypeError(
                    "CurrentPairFragment.verdict_reason_code must be str | None, "
                    f"got {actual_type}.",
                )
            if not self.verdict_reason_code.strip():
                raise ValueError(
                    "CurrentPairFragment.verdict_reason_code must be non-empty after trimming.",
                )
        _validate_typed_tuple(
            self.contradiction_refs,
            ContradictionRecord,
            "CurrentPairFragment.contradiction_refs",
        )
        _validate_typed_tuple(
            self.degradation_refs,
            DegradationRecord,
            "CurrentPairFragment.degradation_refs",
        )
        _validate_typed_tuple(
            self.metadata,
            MetadataField,
            "CurrentPairFragment.metadata",
        )
        if (
            self.verdict_status is CommitmentStatus.CERTIFIED
            and not (isinstance(self.candidate_id, str) and self.candidate_id.strip())
        ):
            raise ValueError(
                "CurrentPairFragment verdict_status=CERTIFIED requires a non-empty candidate_id.",
            )
        if isinstance(self.candidate_id, str) and not self.candidate_id.strip():
            raise ValueError(
                "CurrentPairFragment.candidate_id must be non-empty after trimming.",
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
        _validate_tag_set(self.boundary_tags, "BlockerFragment.boundary_tags")
        _validate_tag_set(self.capability_tags, "BlockerFragment.capability_tags")
        _validate_typed_tuple(
            self.contradiction_refs,
            ContradictionRecord,
            "BlockerFragment.contradiction_refs",
        )
        _validate_typed_tuple(
            self.degradation_refs,
            DegradationRecord,
            "BlockerFragment.degradation_refs",
        )
        _validate_typed_tuple(
            self.metadata,
            MetadataField,
            "BlockerFragment.metadata",
        )


def _validate_string_tuple(values: tuple[str, ...], label: str) -> None:
    for value in values:
        if not isinstance(value, str):
            actual_type = type(value).__name__
            raise TypeError(f"{label} must contain only str instances, got {actual_type}.")
        if not value.strip():
            raise ValueError(f"{label} must contain only non-empty values after trimming.")


def _validate_tag_set(values: frozenset[str], label: str) -> None:
    for value in values:
        if not isinstance(value, str):
            actual_type = type(value).__name__
            raise TypeError(f"{label} must contain only str instances, got {actual_type}.")
        if not value.strip():
            raise ValueError(f"{label} must contain only non-empty values after trimming.")


def _validate_typed_tuple(values: tuple[object, ...], expected_type: type[object], label: str) -> None:
    for value in values:
        if not isinstance(value, expected_type):
            raise TypeError(
                f"{label} must contain only {expected_type.__name__} instances.",
            )


__all__ = [
    "BlockerFragment",
    "CurrentPairFragment",
    "EventTraceArtifact",
]
