"""Explicit degradation and error carriers for contradiction-preserving core state."""

from __future__ import annotations

from dataclasses import dataclass, field

from .envelopes import MetadataField


@dataclass(frozen=True, slots=True)
class ContradictionRecord:
    source_tag: str
    summary: str
    evidence_tags: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if not (isinstance(self.source_tag, str) and self.source_tag.strip()):
            raise ValueError(
                "ContradictionRecord.source_tag must be non-empty after trimming.",
            )
        if not (isinstance(self.summary, str) and self.summary.strip()):
            raise ValueError(
                "ContradictionRecord.summary must be non-empty after trimming.",
            )
        if any(not (isinstance(tag, str) and tag.strip()) for tag in self.evidence_tags):
            raise ValueError(
                "ContradictionRecord.evidence_tags must contain only non-empty values after trimming.",
            )


@dataclass(frozen=True, slots=True)
class DegradationRecord:
    reason_code: str
    capability_tags: frozenset[str] = field(default_factory=frozenset)
    contradiction_records: tuple[ContradictionRecord, ...] = field(default_factory=tuple)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not (isinstance(self.reason_code, str) and self.reason_code.strip()):
            raise ValueError(
                "DegradationRecord.reason_code must be non-empty after trimming.",
            )
        if any(not (isinstance(tag, str) and tag.strip()) for tag in self.capability_tags):
            raise ValueError(
                "DegradationRecord.capability_tags must contain only non-empty values after trimming.",
            )
        if any(
            not isinstance(record, ContradictionRecord)
            for record in self.contradiction_records
        ):
            raise TypeError(
                "DegradationRecord.contradiction_records must contain only ContradictionRecord instances.",
            )
        if any(not isinstance(field, MetadataField) for field in self.metadata):
            raise TypeError(
                "DegradationRecord.metadata must contain only MetadataField instances.",
            )


@dataclass(frozen=True, slots=True)
class CoreErrorRecord:
    reason_code: str
    capability_tags: frozenset[str] = field(default_factory=frozenset)
    contradiction_records: tuple[ContradictionRecord, ...] = field(default_factory=tuple)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not (isinstance(self.reason_code, str) and self.reason_code.strip()):
            raise ValueError(
                "CoreErrorRecord.reason_code must be non-empty after trimming.",
            )


__all__ = ["ContradictionRecord", "CoreErrorRecord", "DegradationRecord"]
