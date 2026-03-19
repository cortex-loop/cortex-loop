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


__all__ = [
    "EventPayloadHandle",
    "LifecycleEventEnvelope",
    "MetadataField",
    "MetadataScalar",
]
