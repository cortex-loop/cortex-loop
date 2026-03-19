"""Lightweight observation carriers for the canonical cheap path."""

from __future__ import annotations

from dataclasses import dataclass, field

from .envelopes import EventPayloadHandle, LifecycleEventEnvelope, MetadataField


@dataclass(frozen=True, slots=True)
class PayloadView:
    payload_handle: EventPayloadHandle | None = None
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)
    summary_tags: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if self.payload_handle is not None and not isinstance(
            self.payload_handle,
            EventPayloadHandle,
        ):
            actual_type = type(self.payload_handle).__name__
            raise TypeError(
                "PayloadView.payload_handle must be EventPayloadHandle when provided, "
                f"got {actual_type}.",
            )
        if any(not isinstance(field, MetadataField) for field in self.metadata):
            raise TypeError(
                "PayloadView.metadata must contain only MetadataField instances.",
            )
        if any(not (isinstance(tag, str) and tag.strip()) for tag in self.summary_tags):
            raise ValueError(
                "PayloadView.summary_tags must contain only non-empty values after trimming.",
            )


@dataclass(frozen=True, slots=True)
class RuntimeRecord:
    record_type: str
    record_id: str | None = None
    tags: frozenset[str] = field(default_factory=frozenset)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not (isinstance(self.record_type, str) and self.record_type.strip()):
            raise ValueError(
                "RuntimeRecord.record_type must be non-empty after trimming.",
            )
        if self.record_id is not None and not (
            isinstance(self.record_id, str) and self.record_id.strip()
        ):
            raise ValueError(
                "RuntimeRecord.record_id must be non-empty after trimming when provided.",
            )
        if any(not (isinstance(tag, str) and tag.strip()) for tag in self.tags):
            raise ValueError(
                "RuntimeRecord.tags must contain only non-empty values after trimming.",
            )
        if any(not isinstance(field, MetadataField) for field in self.metadata):
            raise TypeError(
                "RuntimeRecord.metadata must contain only MetadataField instances.",
            )


@dataclass(frozen=True, slots=True)
class StructuredObservation:
    observation_type: str
    tags: frozenset[str] = field(default_factory=frozenset)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not (isinstance(self.observation_type, str) and self.observation_type.strip()):
            raise ValueError(
                "StructuredObservation.observation_type must be non-empty after trimming.",
            )
        if any(not (isinstance(tag, str) and tag.strip()) for tag in self.tags):
            raise ValueError(
                "StructuredObservation.tags must contain only non-empty values after trimming.",
            )


@dataclass(frozen=True, slots=True)
class ObservationBundle:
    event: LifecycleEventEnvelope
    payload_view: PayloadView
    runtime_records: tuple[RuntimeRecord, ...] = field(default_factory=tuple)
    structured_observations: tuple[StructuredObservation, ...] = field(default_factory=tuple)


__all__ = [
    "ObservationBundle",
    "PayloadView",
    "RuntimeRecord",
    "StructuredObservation",
]
