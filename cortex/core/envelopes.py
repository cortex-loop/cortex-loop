"""Extensible lifecycle-event envelope carriers."""

from __future__ import annotations

from dataclasses import dataclass, field

MetadataScalar = str | int | float | bool | None


@dataclass(frozen=True, slots=True)
class MetadataField:
    key: str
    value: MetadataScalar


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


__all__ = [
    "EventPayloadHandle",
    "LifecycleEventEnvelope",
    "MetadataField",
    "MetadataScalar",
]
