"""Shared adapter protocol and transport helpers for Cortex v3 providers."""

from __future__ import annotations

import json
import urllib.error
from collections.abc import Mapping
from typing import Any, Protocol, runtime_checkable

from cortex_v3.contracts import ProviderTurnRequest, ProviderTurnResponse


class ProviderExecutionError(RuntimeError):
    """Raised when a provider adapter cannot complete a turn."""


@runtime_checkable
class ProviderAdapter(Protocol):
    provider: str

    def execute_turn(self, request: ProviderTurnRequest) -> ProviderTurnResponse:
        """Execute one provider-native turn and normalize the response."""


def http_error_message(exc: urllib.error.HTTPError) -> str:
    try:
        payload = json.loads(exc.read().decode("utf-8"))
    except Exception:
        return exc.reason or "unknown upstream error"
    if isinstance(payload, Mapping):
        error = payload.get("error")
        if isinstance(error, Mapping):
            message = error.get("message")
            if isinstance(message, str) and message.strip():
                return message.strip()
        if isinstance(error, str) and error.strip():
            return error.strip()
    return exc.reason or "unknown upstream error"


def stream_error_message(payload: Mapping[str, Any]) -> str:
    error = payload.get("error")
    if isinstance(error, Mapping):
        message = error.get("message")
        if isinstance(message, str) and message.strip():
            return message.strip()
    if isinstance(error, str) and error.strip():
        return error.strip()
    message = payload.get("message")
    if isinstance(message, str) and message.strip():
        return message.strip()
    return "unknown stream error"


def fixture_calls(payload: Any, *, label: str) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [{"events": payload}]
    if not isinstance(payload, Mapping):
        actual_type = type(payload).__name__
        raise ProviderExecutionError(
            f"{label} fixture payload must be an object or list, got {actual_type}."
        )
    if "calls" in payload:
        calls = payload["calls"]
        if not isinstance(calls, list):
            raise ProviderExecutionError(f"{label} fixture `calls` must be a list.")
        return [dict(call) for call in calls]
    return [dict(payload)]


def normalized_fixture_events(events: Any, *, label: str) -> list[dict[str, Any]]:
    if not isinstance(events, list):
        raise ProviderExecutionError(f"{label} fixture call must contain an `events` list.")
    normalized: list[dict[str, Any]] = []
    for event in events:
        if not isinstance(event, Mapping):
            actual_type = type(event).__name__
            raise ProviderExecutionError(
                f"{label} fixture events must be JSON objects, got {actual_type}."
            )
        normalized.append(dict(event))
    if not normalized:
        raise ProviderExecutionError(f"{label} fixture returned zero host events.")
    return normalized


__all__ = [
    "ProviderAdapter",
    "ProviderExecutionError",
    "fixture_calls",
    "http_error_message",
    "normalized_fixture_events",
    "stream_error_message",
]
