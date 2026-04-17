"""Thin OpenAI Responses adapter for the Cortex v3 verified-work engine."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from collections.abc import Callable, Iterable, Mapping
from http.client import HTTPResponse
from pathlib import Path
from typing import Any

from cortex_v3.contracts import ProviderTurnRequest, ProviderTurnResponse
from cortex_v3.providers.base import (
    ProviderExecutionError,
    fixture_calls,
    http_error_message,
    normalized_fixture_events,
    stream_error_message,
)


_RESPONSES_API_URL = "https://api.openai.com/v1/responses"
_FIXTURE_PATH_ENV = "CORTEX_V3_OPENAI_FIXTURE_PATH"
_FIXTURE_START_INDEX_ENV = "CORTEX_V3_OPENAI_FIXTURE_START_INDEX"
_FIXTURE_CALL_INDEX: dict[str, int] = {}

OpenAITransport = Callable[[ProviderTurnRequest], list[dict[str, Any]]]


class OpenAIProviderError(ProviderExecutionError):
    """Raised when the OpenAI adapter cannot complete a turn."""


class OpenAIAdapter:
    provider = "openai"

    def __init__(self, *, transport: OpenAITransport | None = None) -> None:
        self._transport = transport

    def execute_turn(self, request: ProviderTurnRequest) -> ProviderTurnResponse:
        events = self._execute_events(request)
        return ProviderTurnResponse(
            provider=self.provider,
            output_text=extract_openai_output_text(events),
            raw_events=tuple(events),
        )

    def _execute_events(self, request: ProviderTurnRequest) -> list[dict[str, Any]]:
        if self._transport is not None:
            events = self._transport(request)
            if not isinstance(events, list):
                actual_type = type(events).__name__
                raise OpenAIProviderError(
                    "OpenAIAdapter transport must return list[dict[str, Any]], "
                    f"got {actual_type}."
                )
            return [dict(event) for event in events]
        fixture_path = os.environ.get(_FIXTURE_PATH_ENV)
        if fixture_path:
            return _execute_fixture_turn(request, Path(fixture_path))
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise OpenAIProviderError(
                "OPENAI_API_KEY is required for the live OpenAI V3 adapter."
            )

        body = build_openai_request_body(request)
        http_request = urllib.request.Request(
            _RESPONSES_API_URL,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "text/event-stream",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(http_request, timeout=60.0) as response:
                return parse_openai_sse_events(response)
        except urllib.error.HTTPError as exc:
            raise OpenAIProviderError(
                f"OpenAI Responses transport failed with HTTP {exc.code}: {http_error_message(exc)}"
            ) from exc
        except urllib.error.URLError as exc:
            raise OpenAIProviderError(
                f"OpenAI Responses transport connection failed: {exc.reason}"
            ) from exc
        except OSError as exc:
            raise OpenAIProviderError(f"OpenAI Responses transport failed: {exc}") from exc


def build_openai_request_body(request: ProviderTurnRequest) -> dict[str, Any]:
    body: dict[str, Any] = {
        "model": request.model,
        "input": [
            {
                "role": "user",
                "content": request.prompt,
            }
        ],
        "stream": True,
    }
    if request.instructions is not None:
        body["instructions"] = request.instructions
    if request.metadata:
        body["metadata"] = dict(request.metadata)
    if request.max_output_tokens is not None:
        body["max_output_tokens"] = request.max_output_tokens
    return body


def parse_openai_sse_events(response: HTTPResponse | Iterable[bytes]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    current_event_name: str | None = None
    data_lines: list[str] = []

    def flush() -> bool:
        nonlocal current_event_name, data_lines
        if current_event_name is None and not data_lines:
            return False
        data = "\n".join(data_lines)
        event_name = current_event_name
        current_event_name = None
        data_lines = []
        if data == "[DONE]":
            return True
        if not data:
            raise OpenAIProviderError(
                "OpenAI response stream emitted an event without a data payload."
            )
        try:
            payload = json.loads(data)
        except json.JSONDecodeError as exc:
            raise OpenAIProviderError(
                "OpenAI response stream emitted invalid JSON data."
            ) from exc
        if not isinstance(payload, dict):
            actual_type = type(payload).__name__
            raise OpenAIProviderError(
                "OpenAI response stream emitted a non-object JSON event, "
                f"got {actual_type}."
            )
        normalized_payload = dict(payload)
        payload_type = normalized_payload.get("type")
        if event_name is not None and not (isinstance(payload_type, str) and payload_type.strip()):
            normalized_payload["type"] = event_name
            payload_type = event_name
        if not (isinstance(payload_type, str) and payload_type.strip()):
            raise OpenAIProviderError(
                "OpenAI response stream event must contain a non-empty `type`."
            )
        if payload_type == "error":
            raise OpenAIProviderError(
                f"OpenAI response stream error: {stream_error_message(normalized_payload)}"
            )
        events.append(normalized_payload)
        return False

    for raw_line in response:
        line = raw_line.decode("utf-8").rstrip("\r\n")
        if not line:
            if flush():
                break
            continue
        if line.startswith(":"):
            continue
        field, _, value = line.partition(":")
        value = value.lstrip(" ")
        if field == "event":
            current_event_name = value
        elif field == "data":
            data_lines.append(value)

    if current_event_name is not None or data_lines:
        flush()
    if not events:
        raise OpenAIProviderError("OpenAI response stream returned zero host events.")
    return events


def extract_openai_output_text(events: Iterable[Mapping[str, Any]]) -> str | None:
    chunks: list[str] = []
    for event in events:
        if event.get("type") != "response.output_text.delta":
            continue
        delta = event.get("delta")
        if isinstance(delta, str) and delta:
            chunks.append(delta)
    if not chunks:
        return None
    joined = "".join(chunks).strip()
    return joined or None


def _execute_fixture_turn(
    request: ProviderTurnRequest,
    fixture_path: Path,
) -> list[dict[str, Any]]:
    fixture_payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    calls = fixture_calls(fixture_payload, label="OpenAI V3")
    fixture_key = str(fixture_path)
    if fixture_key not in _FIXTURE_CALL_INDEX:
        _FIXTURE_CALL_INDEX[fixture_key] = int(
            os.environ.get(_FIXTURE_START_INDEX_ENV, "0")
        )
    call_index = _FIXTURE_CALL_INDEX[fixture_key]
    if call_index >= len(calls):
        raise OpenAIProviderError(
            f"OpenAI V3 fixture exhausted at call index {call_index}."
        )
    _FIXTURE_CALL_INDEX[fixture_key] = call_index + 1
    call = calls[call_index]
    expected_request = call.get("expected_request")
    if expected_request is not None and expected_request != request.as_payload():
        raise OpenAIProviderError(
            "OpenAI V3 fixture expected request "
            f"{expected_request!r}, got {request.as_payload()!r}."
        )
    expected_body = call.get("expected_body")
    live_body = build_openai_request_body(request)
    if expected_body is not None and expected_body != live_body:
        raise OpenAIProviderError(
            "OpenAI V3 fixture expected body "
            f"{expected_body!r}, got {live_body!r}."
        )
    if "error" in call:
        error = call["error"]
        if not isinstance(error, str) or not error.strip():
            raise OpenAIProviderError(
                "OpenAI V3 fixture `error` must be a non-empty string."
            )
        raise OpenAIProviderError(error)
    return normalized_fixture_events(call.get("events"), label="OpenAI V3")


__all__ = [
    "OpenAIAdapter",
    "OpenAIProviderError",
    "build_openai_request_body",
    "extract_openai_output_text",
    "parse_openai_sse_events",
]
