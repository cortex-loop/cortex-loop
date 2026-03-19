"""OpenAI Responses observe/bind realization over a minimal documented streaming surface."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from cortex.core.envelopes import EventPayloadHandle, LifecycleEventEnvelope, MetadataField
from cortex.core.lifecycle import LifecycleEffectBinding, LifecycleSurface
from cortex.core.observation import ObservationBundle, PayloadView

from .common_normalization import NormalizedDriverEvent, normalize_driver_event

OPENAI_EVENT_ALIASES = {
    "response.created": "external/observation",
    "response_created": "external/observation",
    "responsecreated": "external/observation",
    "response.output_text.delta": "external/observation",
    "response_output_text_delta": "external/observation",
    "responseoutputtextdelta": "external/observation",
    "response.completed": "turn/complete",
    "response_completed": "turn/complete",
    "responsecompleted": "turn/complete",
}

OPENAI_HOST_SURFACE = LifecycleSurface(
    runtime_name="openai-host",
    event_substrate=frozenset({"external/observation", "turn/complete"}),
    turn_affordances=frozenset({"turn/complete"}),
    effect_map=(
        LifecycleEffectBinding(
            action_tag="openai-response-stream",
            consequence_tags=frozenset({"external/observation"}),
        ),
        LifecycleEffectBinding(
            action_tag="openai-response-complete",
            consequence_tags=frozenset({"turn/complete"}),
        ),
    ),
)


@dataclass(frozen=True, slots=True)
class BoundOpenAIHostEvent:
    lifecycle_surface: LifecycleSurface
    observation: ObservationBundle
    normalized_payload: dict[str, Any]
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.lifecycle_surface, LifecycleSurface):
            actual_type = type(self.lifecycle_surface).__name__
            raise TypeError(
                "BoundOpenAIHostEvent.lifecycle_surface must be LifecycleSurface, "
                f"got {actual_type}.",
            )
        if not isinstance(self.observation, ObservationBundle):
            actual_type = type(self.observation).__name__
            raise TypeError(
                "BoundOpenAIHostEvent.observation must be ObservationBundle, "
                f"got {actual_type}.",
            )
        if not isinstance(self.normalized_payload, dict):
            actual_type = type(self.normalized_payload).__name__
            raise TypeError(
                "BoundOpenAIHostEvent.normalized_payload must be dict[str, Any], "
                f"got {actual_type}.",
            )
        _validate_warning_tuple(self.warnings, "BoundOpenAIHostEvent.warnings")


def bind_openai_event_envelope(
    normalized_event: NormalizedDriverEvent,
) -> LifecycleEventEnvelope:
    if not isinstance(normalized_event, NormalizedDriverEvent):
        actual_type = type(normalized_event).__name__
        raise TypeError(
            "bind_openai_event_envelope.normalized_event must be NormalizedDriverEvent, "
            f"got {actual_type}.",
        )
    routing_event_name = _routing_event_name(normalized_event)
    payload_handle = EventPayloadHandle(
        payload_kind="openai-host-payload",
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


def observe_openai_host_event(
    raw_event_name: str,
    raw_payload: Mapping[str, Any] | None = None,
    *,
    allow_message_commitment_fallback: bool = False,
) -> BoundOpenAIHostEvent:
    normalized_event = normalize_driver_event(
        raw_event_name,
        raw_payload,
        allow_message_commitment_fallback=allow_message_commitment_fallback,
        aliases=OPENAI_EVENT_ALIASES,
    )
    warnings = (*normalized_event.warnings, *_surface_warnings(normalized_event))
    envelope = bind_openai_event_envelope(normalized_event)
    observation = ObservationBundle(
        event=envelope,
        payload_view=PayloadView(payload_handle=envelope.payload_handle),
    )
    return BoundOpenAIHostEvent(
        lifecycle_surface=OPENAI_HOST_SURFACE,
        observation=observation,
        normalized_payload=normalized_event.payload,
        warnings=warnings,
    )


def _routing_event_name(normalized_event: NormalizedDriverEvent) -> str:
    if _is_documented_openai_event(normalized_event.native_event_name):
        return normalized_event.event_name
    return "external/observation"


def _surface_warnings(normalized_event: NormalizedDriverEvent) -> tuple[str, ...]:
    if _is_documented_openai_event(normalized_event.native_event_name):
        return ()
    raw_name = normalized_event.native_event_name or "<empty>"
    return (
        "No documented OpenAI lifecycle mapping for "
        f"{raw_name!r}; using conservative external/observation binding.",
    )


def _is_documented_openai_event(event_name: str) -> bool:
    if not event_name.strip():
        return False
    return any(variant in OPENAI_EVENT_ALIASES for variant in _event_name_variants(event_name))


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
    response_id = _response_id(payload)
    if response_id is not None:
        return response_id
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
    response_id = _response_id(normalized_event.payload)
    if response_id is not None:
        fields.append(MetadataField("response_id", response_id))
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
    return tuple(fields)


def _response_id(payload: Mapping[str, Any]) -> str | None:
    direct_id = payload.get("response_id")
    if isinstance(direct_id, str) and direct_id:
        return direct_id

    response = payload.get("response")
    if isinstance(response, Mapping):
        nested_id = response.get("id")
        if isinstance(nested_id, str) and nested_id:
            return nested_id
    return None


def _validate_warning_tuple(warnings: tuple[str, ...], label: str) -> None:
    for warning in warnings:
        if not isinstance(warning, str):
            actual_type = type(warning).__name__
            raise TypeError(f"{label} must contain only str instances, got {actual_type}.")
        if not warning.strip():
            raise ValueError(f"{label} must contain only non-empty values after trimming.")


__all__ = [
    "BoundOpenAIHostEvent",
    "OPENAI_HOST_SURFACE",
    "bind_openai_event_envelope",
    "observe_openai_host_event",
]
