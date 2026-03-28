"""Reference-host observe/bind realization over the common normalization layer."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from cortex.core.envelopes import EventPayloadHandle, LifecycleEventEnvelope, MetadataField
from cortex.core.lifecycle import LifecycleEffectBinding, LifecycleSurface
from cortex.core.observation import ObservationBundle, PayloadView

from .common_normalization import (
    CANONICAL_EVENT_ALIASES,
    NormalizedDriverEvent,
    normalize_driver_event,
)

REFERENCE_HOST_SURFACE = LifecycleSurface(
    runtime_name="reference-host",
    event_substrate=frozenset(CANONICAL_EVENT_ALIASES.values()),
    context_affordances=frozenset({"session/start", "context/load"}),
    tool_affordances=frozenset(
        {
            "tool/pre",
            "tool/post",
            "approval/request",
            "approval/result",
            "external/observation",
        }
    ),
    turn_affordances=frozenset({"turn/complete"}),
    effect_map=(
        LifecycleEffectBinding(
            action_tag="tool-call",
            consequence_tags=frozenset({"tool/pre", "tool/post"}),
        ),
        LifecycleEffectBinding(
            action_tag="approval-flow",
            consequence_tags=frozenset({"approval/request", "approval/result"}),
        ),
        LifecycleEffectBinding(
            action_tag="turn-close",
            consequence_tags=frozenset({"turn/complete"}),
        ),
    ),
)


@dataclass(frozen=True, slots=True)
class BoundReferenceHostEvent:
    lifecycle_surface: LifecycleSurface
    observation: ObservationBundle
    normalized_payload: dict[str, Any]
    warnings: tuple[str, ...] = ()


def bind_reference_event_envelope(
    normalized_event: NormalizedDriverEvent,
) -> LifecycleEventEnvelope:
    routing_event_name = normalized_event.event_name or normalized_event.native_event_name
    payload_metadata = _build_payload_metadata(normalized_event)
    payload_handle = EventPayloadHandle(
        payload_kind="reference-host-payload",
        payload_ref=_payload_ref(normalized_event.payload),
        metadata=_build_payload_handle_metadata(normalized_event),
    )
    return LifecycleEventEnvelope(
        native_event_name=routing_event_name,
        facet_tags=_facet_tags(routing_event_name),
        channel_tags=_channel_tags(routing_event_name),
        payload_metadata=payload_metadata,
        payload_handle=payload_handle,
    )


def observe_reference_host_event(
    raw_event_name: str,
    raw_payload: Mapping[str, Any] | None = None,
    *,
    allow_message_commitment_fallback: bool = False,
) -> BoundReferenceHostEvent:
    normalized_event = normalize_driver_event(
        raw_event_name,
        raw_payload,
        allow_message_commitment_fallback=allow_message_commitment_fallback,
    )
    envelope = bind_reference_event_envelope(normalized_event)
    observation = ObservationBundle(
        event=envelope,
        payload_view=PayloadView(
            payload_handle=envelope.payload_handle,
        ),
    )
    return BoundReferenceHostEvent(
        lifecycle_surface=REFERENCE_HOST_SURFACE,
        observation=observation,
        normalized_payload=normalized_event.payload,
        warnings=normalized_event.warnings,
    )


def _facet_tags(event_name: str) -> frozenset[str]:
    if not event_name:
        return frozenset()
    return frozenset({event_name})


def _channel_tags(event_name: str) -> frozenset[str]:
    if not event_name:
        return frozenset()
    return frozenset({event_name.split("/", 1)[0]})


def _payload_ref(payload: Mapping[str, Any]) -> str | None:
    session_id = payload.get("session_id")
    if isinstance(session_id, str) and session_id:
        return session_id
    return None


def _build_payload_metadata(
    normalized_event: NormalizedDriverEvent,
) -> tuple[MetadataField, ...]:
    fields: list[MetadataField] = [
        MetadataField("raw_host_event_name", normalized_event.native_event_name),
    ]
    session_id = normalized_event.payload.get("session_id")
    if isinstance(session_id, str):
        fields.append(MetadataField("session_id", session_id))
    tool_name = normalized_event.payload.get("tool_name")
    if isinstance(tool_name, str):
        fields.append(MetadataField("tool_name", tool_name))
    return tuple(fields)


def _build_payload_handle_metadata(
    normalized_event: NormalizedDriverEvent,
) -> tuple[MetadataField, ...]:
    commitment_source = normalized_event.payload.get("commitment_fields_source")
    if isinstance(commitment_source, str):
        return (MetadataField("commitment_fields_source", commitment_source),)
    return ()


__all__ = [
    "BoundReferenceHostEvent",
    "REFERENCE_HOST_SURFACE",
    "bind_reference_event_envelope",
    "observe_reference_host_event",
]
