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


@dataclass(frozen=True, slots=True)
class RuntimeRecord:
    record_type: str
    record_id: str | None = None
    tags: frozenset[str] = field(default_factory=frozenset)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class StructuredObservation:
    observation_type: str
    tags: frozenset[str] = field(default_factory=frozenset)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)


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
