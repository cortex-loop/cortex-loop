"""Claude host observe/bind realization over a minimal documented event surface."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from cortex.core.envelopes import EventPayloadHandle, LifecycleEventEnvelope, MetadataField
from cortex.core.lifecycle import LifecycleEffectBinding, LifecycleSurface
from cortex.core.observation import ObservationBundle, PayloadView

from cortex.drivers.common_normalization import NormalizedDriverEvent, normalize_driver_event

CLAUDE_EVENT_ALIASES = {
    "message_start": "external/observation",
    "messagestart": "external/observation",
    "content_block_start": "external/observation",
    "contentblockstart": "external/observation",
    "content_block_delta": "external/observation",
    "contentblockdelta": "external/observation",
    "content_block_stop": "external/observation",
    "contentblockstop": "external/observation",
    "message_delta": "external/observation",
    "messagedelta": "external/observation",
    "message_stop": "turn/complete",
    "messagestop": "turn/complete",
}

CLAUDE_HOST_SURFACE = LifecycleSurface(
    runtime_name="claude-host",
    event_substrate=frozenset({"external/observation", "turn/complete"}),
    turn_affordances=frozenset({"turn/complete"}),
    effect_map=(
        LifecycleEffectBinding(
            action_tag="claude-message-stream",
            consequence_tags=frozenset({"external/observation"}),
        ),
    ),
)


@dataclass(frozen=True, slots=True)
class BoundClaudeHostEvent:
    lifecycle_surface: LifecycleSurface
    observation: ObservationBundle
    normalized_payload: dict[str, Any]
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.lifecycle_surface, LifecycleSurface):
            actual_type = type(self.lifecycle_surface).__name__
            raise TypeError(
                "BoundClaudeHostEvent.lifecycle_surface must be LifecycleSurface, "
                f"got {actual_type}.",
            )
        if not isinstance(self.observation, ObservationBundle):
            actual_type = type(self.observation).__name__
            raise TypeError(
                "BoundClaudeHostEvent.observation must be ObservationBundle, "
                f"got {actual_type}.",
            )
        if not isinstance(self.normalized_payload, dict):
            actual_type = type(self.normalized_payload).__name__
            raise TypeError(
                "BoundClaudeHostEvent.normalized_payload must be dict[str, Any], "
                f"got {actual_type}.",
            )
        _validate_warning_tuple(self.warnings, "BoundClaudeHostEvent.warnings")


def bind_claude_event_envelope(
    normalized_event: NormalizedDriverEvent,
) -> LifecycleEventEnvelope:
    if not isinstance(normalized_event, NormalizedDriverEvent):
        actual_type = type(normalized_event).__name__
        raise TypeError(
            "bind_claude_event_envelope.normalized_event must be NormalizedDriverEvent, "
            f"got {actual_type}.",
        )
    routing_event_name = _routing_event_name(normalized_event)
    payload_handle = EventPayloadHandle(
        payload_kind="claude-host-payload",
        payload_ref=_payload_ref(normalized_event.payload),
        metadata=_build_payload_handle_metadata(normalized_event),
    )
    return LifecycleEventEnvelope(
        native_event_name=routing_event_name,
        facet_tags=_facet_tags(routing_event_name),
        channel_tags=_channel_tags(routing_event_name),
        payload_metadata=_build_payload_metadata(normalized_event),
        payload_handle=payload_handle,
    )


def observe_claude_host_event(
    raw_event_name: str,
    raw_payload: Mapping[str, Any] | None = None,
    *,
    allow_message_commitment_fallback: bool = False,
) -> BoundClaudeHostEvent:
    normalized_event = normalize_driver_event(
        raw_event_name,
        raw_payload,
        allow_message_commitment_fallback=allow_message_commitment_fallback,
        aliases=CLAUDE_EVENT_ALIASES,
    )
    warnings = (*normalized_event.warnings, *_surface_warnings(normalized_event))
    envelope = bind_claude_event_envelope(normalized_event)
    observation = ObservationBundle(
        event=envelope,
        payload_view=PayloadView(payload_handle=envelope.payload_handle),
    )
    return BoundClaudeHostEvent(
        lifecycle_surface=CLAUDE_HOST_SURFACE,
        observation=observation,
        normalized_payload=normalized_event.payload,
        warnings=warnings,
    )


def _routing_event_name(normalized_event: NormalizedDriverEvent) -> str:
    if _is_documented_claude_event(normalized_event.native_event_name):
        return normalized_event.event_name
    return "external/observation"


def _surface_warnings(normalized_event: NormalizedDriverEvent) -> tuple[str, ...]:
    if _is_documented_claude_event(normalized_event.native_event_name):
        subtype_warning = _subtype_warning(normalized_event)
        if subtype_warning is None:
            return ()
        return (subtype_warning,)
    raw_name = normalized_event.native_event_name or "<empty>"
    return (
        "No documented Claude lifecycle mapping for "
        f"{raw_name!r}; using conservative external/observation binding.",
    )


def _is_documented_claude_event(event_name: str) -> bool:
    if not event_name.strip():
        return False
    return any(variant in CLAUDE_EVENT_ALIASES for variant in _event_name_variants(event_name))


def is_raw_claude_host_event_name(event_name: str) -> bool:
    if not isinstance(event_name, str):
        return False
    stripped = event_name.strip()
    if not stripped or "/" in stripped:
        return False
    return any(
        variant.startswith("message_") or variant.startswith("content_block_")
        for variant in _event_name_variants(stripped)
    )


def _event_name_variants(raw: str) -> tuple[str, ...]:
    camel_split = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", raw)
    lowered = camel_split.lower()
    token = re.sub(r"[\s./-]+", "_", lowered).strip("_")
    collapsed = token.replace("_", "")
    return tuple(variant for variant in (lowered, token, collapsed) if variant)


def _facet_tags(event_name: str) -> frozenset[str]:
    if not event_name:
        return frozenset()
    return frozenset({event_name})


def _channel_tags(event_name: str) -> frozenset[str]:
    if not event_name:
        return frozenset()
    return frozenset({event_name.split("/", 1)[0]})


def _payload_ref(payload: Mapping[str, Any]) -> str | None:
    message_id = _message_id(payload)
    if message_id is not None:
        return message_id
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
    message_id = _message_id(normalized_event.payload)
    if message_id is not None:
        fields.append(MetadataField("message_id", message_id))
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
    fields: list[MetadataField] = []
    commitment_source = normalized_event.payload.get("commitment_fields_source")
    if isinstance(commitment_source, str):
        fields.append(MetadataField("commitment_fields_source", commitment_source))
    delta_type = _delta_type(normalized_event.payload)
    if delta_type is not None:
        fields.append(MetadataField("delta_type", delta_type))
    return tuple(fields)


def _message_id(payload: Mapping[str, Any]) -> str | None:
    direct_id = payload.get("message_id")
    if isinstance(direct_id, str) and direct_id:
        return direct_id

    message = payload.get("message")
    if isinstance(message, Mapping):
        nested_id = message.get("id")
        if isinstance(nested_id, str) and nested_id:
            return nested_id
    return None


def _delta_type(payload: Mapping[str, Any]) -> str | None:
    direct_delta_type = payload.get("delta_type")
    if isinstance(direct_delta_type, str) and direct_delta_type:
        return direct_delta_type
    delta = payload.get("delta")
    if isinstance(delta, Mapping):
        delta_type = delta.get("type")
        if isinstance(delta_type, str) and delta_type:
            return delta_type
    return None


def _subtype_warning(normalized_event: NormalizedDriverEvent) -> str | None:
    event_name = normalized_event.native_event_name.strip()
    if event_name == "content_block_start":
        block_type = normalized_event.payload.get("content_block_type")
        if isinstance(block_type, str) and block_type != "text":
            return (
                "No documented Claude text-block start mapping for "
                f"{block_type!r}; using conservative external/observation binding."
            )
    if event_name == "content_block_delta":
        delta_type = _delta_type(normalized_event.payload)
        if isinstance(delta_type, str) and delta_type != "text_delta":
            return (
                "No documented Claude text delta mapping for "
                f"{delta_type!r}; using conservative external/observation binding."
            )
    return None


def _validate_warning_tuple(warnings: tuple[str, ...], label: str) -> None:
    if not isinstance(warnings, tuple):
        actual_type = type(warnings).__name__
        raise TypeError(f"{label} must be tuple[str, ...], got {actual_type}.")
    for warning in warnings:
        if not isinstance(warning, str):
            actual_type = type(warning).__name__
            raise TypeError(f"{label} must contain only str instances, got {actual_type}.")
        if not warning.strip():
            raise ValueError(f"{label} must contain only non-empty values after trimming.")


__all__ = [
    "BoundClaudeHostEvent",
    "CLAUDE_HOST_SURFACE",
    "bind_claude_event_envelope",
    "is_raw_claude_host_event_name",
    "observe_claude_host_event",
]
