"""Gemini host observe/bind realization over a minimal documented event surface."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from cortex.core.envelopes import EventPayloadHandle, LifecycleEventEnvelope, MetadataField
from cortex.core.lifecycle import LifecycleEffectBinding, LifecycleSurface
from cortex.core.observation import ObservationBundle, PayloadView

from cortex.drivers.common_normalization import NormalizedDriverEvent, normalize_driver_event

GEMINI_EVENT_ALIASES = {
    "content.start": "external/observation",
    "content_start": "external/observation",
    "contentstart": "external/observation",
    "content.delta": "external/observation",
    "content_delta": "external/observation",
    "contentdelta": "external/observation",
    "interaction.complete": "turn/complete",
    "interaction_complete": "turn/complete",
    "interactioncomplete": "turn/complete",
}

GEMINI_HOST_SURFACE = LifecycleSurface(
    runtime_name="gemini-host",
    event_substrate=frozenset({"external/observation", "turn/complete"}),
    turn_affordances=frozenset({"turn/complete"}),
    effect_map=(
        LifecycleEffectBinding(
            action_tag="gemini-interaction-stream",
            consequence_tags=frozenset({"external/observation"}),
        ),
        LifecycleEffectBinding(
            action_tag="gemini-interaction-complete",
            consequence_tags=frozenset({"turn/complete"}),
        ),
    ),
)


@dataclass(frozen=True, slots=True)
class BoundGeminiHostEvent:
    lifecycle_surface: LifecycleSurface
    observation: ObservationBundle
    normalized_payload: dict[str, Any]
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.lifecycle_surface, LifecycleSurface):
            actual_type = type(self.lifecycle_surface).__name__
            raise TypeError(
                "BoundGeminiHostEvent.lifecycle_surface must be LifecycleSurface, "
                f"got {actual_type}.",
            )
        if not isinstance(self.observation, ObservationBundle):
            actual_type = type(self.observation).__name__
            raise TypeError(
                "BoundGeminiHostEvent.observation must be ObservationBundle, "
                f"got {actual_type}.",
            )
        if not isinstance(self.normalized_payload, dict):
            actual_type = type(self.normalized_payload).__name__
            raise TypeError(
                "BoundGeminiHostEvent.normalized_payload must be dict[str, Any], "
                f"got {actual_type}.",
            )
        _validate_warning_tuple(self.warnings, "BoundGeminiHostEvent.warnings")


def bind_gemini_event_envelope(
    normalized_event: NormalizedDriverEvent,
) -> LifecycleEventEnvelope:
    if not isinstance(normalized_event, NormalizedDriverEvent):
        actual_type = type(normalized_event).__name__
        raise TypeError(
            "bind_gemini_event_envelope.normalized_event must be NormalizedDriverEvent, "
            f"got {actual_type}.",
        )
    routing_event_name = _routing_event_name(normalized_event)
    payload_handle = EventPayloadHandle(
        payload_kind="gemini-host-payload",
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


def observe_gemini_host_event(
    raw_event_name: str,
    raw_payload: Mapping[str, Any] | None = None,
    *,
    allow_message_commitment_fallback: bool = False,
) -> BoundGeminiHostEvent:
    normalized_event = normalize_driver_event(
        raw_event_name,
        raw_payload,
        allow_message_commitment_fallback=allow_message_commitment_fallback,
        aliases=GEMINI_EVENT_ALIASES,
    )
    warnings = (*normalized_event.warnings, *_surface_warnings(normalized_event))
    envelope = bind_gemini_event_envelope(normalized_event)
    observation = ObservationBundle(
        event=envelope,
        payload_view=PayloadView(payload_handle=envelope.payload_handle),
    )
    return BoundGeminiHostEvent(
        lifecycle_surface=GEMINI_HOST_SURFACE,
        observation=observation,
        normalized_payload=normalized_event.payload,
        warnings=warnings,
    )


def _routing_event_name(normalized_event: NormalizedDriverEvent) -> str:
    if _is_documented_gemini_event(normalized_event.native_event_name):
        return normalized_event.event_name
    return "external/observation"


def _surface_warnings(normalized_event: NormalizedDriverEvent) -> tuple[str, ...]:
    if _is_documented_gemini_event(normalized_event.native_event_name):
        return ()
    raw_name = normalized_event.native_event_name or "<empty>"
    return (
        "No documented Gemini lifecycle mapping for "
        f"{raw_name!r}; using conservative external/observation binding.",
    )


def _is_documented_gemini_event(event_name: str) -> bool:
    if not event_name.strip():
        return False
    return any(variant in GEMINI_EVENT_ALIASES for variant in _event_name_variants(event_name))


def is_raw_gemini_host_event_name(event_name: str) -> bool:
    if not isinstance(event_name, str):
        return False
    stripped = event_name.strip()
    if not stripped or "/" in stripped:
        return False
    return any(
        variant.startswith("content") or variant.startswith("interaction")
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
    interaction_id = _interaction_id(payload)
    if interaction_id is not None:
        return interaction_id
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
    interaction_id = _interaction_id(normalized_event.payload)
    if interaction_id is not None:
        fields.append(MetadataField("interaction_id", interaction_id))
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


def _interaction_id(payload: Mapping[str, Any]) -> str | None:
    direct_id = payload.get("interaction_id")
    if isinstance(direct_id, str) and direct_id:
        return direct_id

    interaction = payload.get("interaction")
    if isinstance(interaction, Mapping):
        nested_id = interaction.get("id")
        if isinstance(nested_id, str) and nested_id:
            return nested_id
    return None


def _delta_type(payload: Mapping[str, Any]) -> str | None:
    delta = payload.get("delta")
    if isinstance(delta, Mapping):
        delta_type = delta.get("type")
        if isinstance(delta_type, str) and delta_type:
            return delta_type
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
    "BoundGeminiHostEvent",
    "GEMINI_HOST_SURFACE",
    "bind_gemini_event_envelope",
    "is_raw_gemini_host_event_name",
    "observe_gemini_host_event",
]
