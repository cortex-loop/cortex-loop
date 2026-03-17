"""Thin common driver-side normalization helpers."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from cortex.core.commitment_payload import extract_commitment_payload

CANONICAL_EVENT_ALIASES = {
    "session/start": "session/start",
    "session_start": "session/start",
    "sessionstart": "session/start",
    "context/load": "context/load",
    "context_load": "context/load",
    "contextload": "context/load",
    "tool/pre": "tool/pre",
    "pre_tool_use": "tool/pre",
    "pretooluse": "tool/pre",
    "tool/post": "tool/post",
    "post_tool_use": "tool/post",
    "posttooluse": "tool/post",
    "post_tool_use_failure": "tool/post",
    "posttoolusefailure": "tool/post",
    "turn/complete": "turn/complete",
    "turn_complete": "turn/complete",
    "turn_completed": "turn/complete",
    "turncompleted": "turn/complete",
    "stop": "turn/complete",
    "approval/request": "approval/request",
    "approval_request": "approval/request",
    "approvalrequest": "approval/request",
    "request_approval": "approval/request",
    "requestapproval": "approval/request",
    "approval/result": "approval/result",
    "approval_result": "approval/result",
    "approvalresult": "approval/result",
    "external/observation": "external/observation",
    "external_observation": "external/observation",
    "externalobservation": "external/observation",
}


@dataclass(frozen=True, slots=True)
class NormalizedDriverEvent:
    native_event_name: str
    event_name: str
    payload: dict[str, Any]
    warnings: tuple[str, ...] = ()


def normalize_event_name(
    event_name: str,
    *,
    aliases: Mapping[str, str] = CANONICAL_EVENT_ALIASES,
) -> str:
    raw = str(event_name or "").strip()
    if not raw:
        return ""

    variants = _event_name_variants(raw)
    for variant in variants:
        if variant in aliases:
            return aliases[variant]
    return variants[0].replace("_", "/")


def normalize_driver_payload(
    payload: Mapping[str, Any] | None,
    *,
    allow_message_commitment_fallback: bool = False,
) -> tuple[dict[str, Any], tuple[str, ...]]:
    data = dict(payload) if isinstance(payload, Mapping) else {}

    _normalize_session_id(data)
    _normalize_tool_name(data, candidate_keys=("tool_name", "tool", "action"))

    native_commitment_fields = data.get("commitment_fields")
    extraction = extract_commitment_payload(
        data,
        native_commitment_fields=native_commitment_fields if isinstance(native_commitment_fields, Mapping) else None,
        allow_message_fallback=allow_message_commitment_fallback,
    )
    if extraction.commitment_fields is not None:
        data["commitment_fields"] = extraction.commitment_fields
        data["commitment_fields_source"] = extraction.source

    if isinstance(data.get("stop_fields"), Mapping):
        data["stop_fields"] = dict(data["stop_fields"])

    return data, extraction.warnings


def normalize_driver_event(
    event_name: str,
    payload: Mapping[str, Any] | None = None,
    *,
    allow_message_commitment_fallback: bool = False,
    aliases: Mapping[str, str] = CANONICAL_EVENT_ALIASES,
) -> NormalizedDriverEvent:
    normalized_payload, warnings = normalize_driver_payload(
        payload,
        allow_message_commitment_fallback=allow_message_commitment_fallback,
    )
    return NormalizedDriverEvent(
        native_event_name=str(event_name or "").strip(),
        event_name=normalize_event_name(event_name, aliases=aliases),
        payload=normalized_payload,
        warnings=warnings,
    )


def _event_name_variants(raw: str) -> tuple[str, ...]:
    camel_split = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", raw)
    lowered = camel_split.lower()
    token = re.sub(r"[\s./-]+", "_", lowered).strip("_")
    collapsed = token.replace("_", "")
    return tuple(variant for variant in (token, collapsed, lowered) if variant)


def _normalize_session_id(payload: dict[str, Any]) -> None:
    raw_session_id = payload.get("session_id")
    if isinstance(raw_session_id, str):
        session_id = raw_session_id.strip()
        if session_id:
            payload["session_id"] = session_id
            return
    payload.pop("session_id", None)


def _normalize_tool_name(payload: dict[str, Any], *, candidate_keys: tuple[str, ...]) -> None:
    primary = payload.get("tool_name")
    if isinstance(primary, str) and primary.strip():
        payload["tool_name"] = primary.strip()
        return

    payload.pop("tool_name", None)
    for key in candidate_keys:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            payload["tool_name"] = value.strip()
            return


__all__ = [
    "CANONICAL_EVENT_ALIASES",
    "NormalizedDriverEvent",
    "normalize_driver_event",
    "normalize_driver_payload",
    "normalize_event_name",
]
