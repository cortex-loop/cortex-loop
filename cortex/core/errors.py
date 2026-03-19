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


@dataclass(frozen=True, slots=True)
class DegradationRecord:
    reason_code: str
    capability_tags: frozenset[str] = field(default_factory=frozenset)
    contradiction_records: tuple[ContradictionRecord, ...] = field(default_factory=tuple)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class CoreErrorRecord:
    reason_code: str
    capability_tags: frozenset[str] = field(default_factory=frozenset)
    contradiction_records: tuple[ContradictionRecord, ...] = field(default_factory=tuple)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)


__all__ = ["ContradictionRecord", "CoreErrorRecord", "DegradationRecord"]
