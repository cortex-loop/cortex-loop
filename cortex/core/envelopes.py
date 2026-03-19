"""Extensible lifecycle-event envelope carriers."""

from __future__ import annotations

from dataclasses import dataclass, field

MetadataScalar = str | int | float | bool | None


@dataclass(frozen=True, slots=True)
class MetadataField:
    key: str
    value: MetadataScalar

    def __post_init__(self) -> None:
        if not (isinstance(self.key, str) and self.key.strip()):
            raise ValueError(
                "MetadataField.key must be non-empty after trimming.",
            )


@dataclass(frozen=True, slots=True)
class EventPayloadHandle:
    payload_kind: str
    payload_ref: str | None = None
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not (isinstance(self.payload_kind, str) and self.payload_kind.strip()):
            raise ValueError(
                "EventPayloadHandle.payload_kind must be non-empty after trimming.",
            )
        if any(not isinstance(field, MetadataField) for field in self.metadata):
            raise TypeError(
                "EventPayloadHandle.metadata must contain only MetadataField instances.",
            )


@dataclass(frozen=True, slots=True)
class LifecycleEventEnvelope:
    native_event_name: str
    facet_tags: frozenset[str] = field(default_factory=frozenset)
    channel_tags: frozenset[str] = field(default_factory=frozenset)
    extension_tags: frozenset[str] = field(default_factory=frozenset)
    payload_metadata: tuple[MetadataField, ...] = field(default_factory=tuple)
    payload_handle: EventPayloadHandle | None = None

    def __post_init__(self) -> None:
        if not self.native_event_name.strip():
            raise ValueError(
                "LifecycleEventEnvelope.native_event_name must be non-empty after trimming.",
            )
        if self.payload_handle is not None and not isinstance(
            self.payload_handle,
            EventPayloadHandle,
        ):
            actual_type = type(self.payload_handle).__name__
            raise TypeError(
                "LifecycleEventEnvelope.payload_handle must be EventPayloadHandle when provided, "
                f"got {actual_type}.",
            )


__all__ = [
    "EventPayloadHandle",
    "LifecycleEventEnvelope",
    "MetadataField",
    "MetadataScalar",
]
