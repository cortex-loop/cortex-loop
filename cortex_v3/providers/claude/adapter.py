"""Thin Claude Messages adapter for the Cortex v3 verified-work engine."""

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


_MESSAGES_API_URL = "https://api.anthropic.com/v1/messages"
_FIXTURE_PATH_ENV = "CORTEX_V3_CLAUDE_FIXTURE_PATH"
_FIXTURE_START_INDEX_ENV = "CORTEX_V3_CLAUDE_FIXTURE_START_INDEX"
_FIXTURE_CALL_INDEX: dict[str, int] = {}

ClaudeTransport = Callable[[ProviderTurnRequest], list[dict[str, Any]]]


class ClaudeProviderError(ProviderExecutionError):
    """Raised when the Claude adapter cannot complete a turn."""


class ClaudeAdapter:
    provider = "claude"

    def __init__(self, *, transport: ClaudeTransport | None = None) -> None:
        self._transport = transport

    def execute_turn(self, request: ProviderTurnRequest) -> ProviderTurnResponse:
        events = self._execute_events(request)
        return ProviderTurnResponse(
            provider=self.provider,
            output_text=extract_claude_output_text(events),
            raw_events=tuple(events),
        )

    def _execute_events(self, request: ProviderTurnRequest) -> list[dict[str, Any]]:
        if self._transport is not None:
            events = self._transport(request)
            if not isinstance(events, list):
                actual_type = type(events).__name__
                raise ClaudeProviderError(
                    "ClaudeAdapter transport must return list[dict[str, Any]], "
                    f"got {actual_type}."
                )
            return [dict(event) for event in events]
        fixture_path = os.environ.get(_FIXTURE_PATH_ENV)
        if fixture_path:
            return _execute_fixture_turn(request, Path(fixture_path))
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ClaudeProviderError(
                "ANTHROPIC_API_KEY is required for the live Claude V3 adapter."
            )

        body = build_claude_request_body(request)
        http_request = urllib.request.Request(
            _MESSAGES_API_URL,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Accept": "text/event-stream",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(http_request, timeout=60.0) as response:
                return parse_claude_sse_events(response)
        except urllib.error.HTTPError as exc:
            raise ClaudeProviderError(
                f"Claude message-stream transport failed with HTTP {exc.code}: {http_error_message(exc)}"
            ) from exc
        except urllib.error.URLError as exc:
            raise ClaudeProviderError(
                f"Claude message-stream transport connection failed: {exc.reason}"
            ) from exc
        except OSError as exc:
            raise ClaudeProviderError(f"Claude message-stream transport failed: {exc}") from exc


def build_claude_request_body(request: ProviderTurnRequest) -> dict[str, Any]:
    body: dict[str, Any] = {
        "model": request.model,
        "max_tokens": request.max_output_tokens or 1024,
        "messages": [{"role": "user", "content": request.prompt}],
        "stream": True,
    }
    if request.instructions is not None:
        body["system"] = request.instructions
    if request.metadata:
        body["metadata"] = dict(request.metadata)
    return body


def parse_claude_sse_events(response: HTTPResponse | Iterable[bytes]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    current_event_name: str | None = None
    data_lines: list[str] = []
    active_message_id: str | None = None

    def flush() -> bool:
        nonlocal current_event_name, data_lines, active_message_id
        if current_event_name is None and not data_lines:
            return False
        data = "\n".join(data_lines)
        event_name = current_event_name
        current_event_name = None
        data_lines = []
        if data == "[DONE]":
            return True
        if event_name == "ping":
            return False
        if not data:
            raise ClaudeProviderError(
                "Claude message stream emitted an event without a data payload."
            )
        try:
            payload = json.loads(data)
        except json.JSONDecodeError as exc:
            raise ClaudeProviderError(
                "Claude message stream emitted invalid JSON data."
            ) from exc
        if not isinstance(payload, dict):
            actual_type = type(payload).__name__
            raise ClaudeProviderError(
                "Claude message stream emitted a non-object JSON event, "
                f"got {actual_type}."
            )
        if event_name == "error":
            raise ClaudeProviderError(
                f"Claude message stream error: {stream_error_message(payload)}"
            )
        normalized_payload = _normalize_claude_stream_event(dict(payload), event_name)
        if active_message_id is not None and "message_id" not in normalized_payload:
            normalized_payload["message_id"] = active_message_id
        message_id = normalized_payload.get("message_id")
        if isinstance(message_id, str) and message_id.strip():
            active_message_id = message_id
        payload_type = normalized_payload.get("type")
        if not (isinstance(payload_type, str) and payload_type.strip()):
            raise ClaudeProviderError(
                "Claude message stream event must contain a non-empty `type`."
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
        raise ClaudeProviderError("Claude message stream returned zero host events.")
    return events


def extract_claude_output_text(events: Iterable[Mapping[str, Any]]) -> str | None:
    chunks: list[str] = []
    for event in events:
        if event.get("type") not in {"content_block_start", "content_block_delta"}:
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
    calls = fixture_calls(fixture_payload, label="Claude V3")
    fixture_key = str(fixture_path)
    if fixture_key not in _FIXTURE_CALL_INDEX:
        _FIXTURE_CALL_INDEX[fixture_key] = int(
            os.environ.get(_FIXTURE_START_INDEX_ENV, "0")
        )
    call_index = _FIXTURE_CALL_INDEX[fixture_key]
    if call_index >= len(calls):
        raise ClaudeProviderError(
            f"Claude V3 fixture exhausted at call index {call_index}."
        )
    _FIXTURE_CALL_INDEX[fixture_key] = call_index + 1
    call = calls[call_index]
    expected_request = call.get("expected_request")
    if expected_request is not None and expected_request != request.as_payload():
        raise ClaudeProviderError(
            "Claude V3 fixture expected request "
            f"{expected_request!r}, got {request.as_payload()!r}."
        )
    expected_body = call.get("expected_body")
    live_body = build_claude_request_body(request)
    if expected_body is not None and expected_body != live_body:
        raise ClaudeProviderError(
            "Claude V3 fixture expected body "
            f"{expected_body!r}, got {live_body!r}."
        )
    if "error" in call:
        error = call["error"]
        if not isinstance(error, str) or not error.strip():
            raise ClaudeProviderError(
                "Claude V3 fixture `error` must be a non-empty string."
            )
        raise ClaudeProviderError(error)
    return normalized_fixture_events(call.get("events"), label="Claude V3")


def _normalize_claude_stream_event(
    payload: dict[str, Any],
    event_name: str | None,
) -> dict[str, Any]:
    if event_name is not None:
        normalized = _base_stream_payload(payload, event_name)
        normalized["type"] = event_name
        return normalized
    if "type" in payload:
        return payload
    raise ClaudeProviderError(
        "Claude message stream event must use a documented Messages SSE event name."
    )


def _message_id(payload: Mapping[str, Any]) -> str | None:
    direct_id = payload.get("message_id")
    if isinstance(direct_id, str) and direct_id.strip():
        return direct_id.strip()
    message = payload.get("message")
    if isinstance(message, Mapping):
        nested_id = message.get("id")
        if isinstance(nested_id, str) and nested_id.strip():
            return nested_id.strip()
    return None


def _base_stream_payload(payload: dict[str, Any], event_name: str) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    message_id = _message_id(payload)
    if message_id is not None:
        normalized["message_id"] = message_id
    if event_name == "message_start":
        message = payload.get("message")
        if isinstance(message, Mapping):
            role = message.get("role")
            if isinstance(role, str) and role:
                normalized["role"] = role
            model = message.get("model")
            if isinstance(model, str) and model:
                normalized["model"] = model
        return normalized
    if event_name == "content_block_start":
        normalized["content_block_index"] = payload.get("index")
        content_block = payload.get("content_block")
        if isinstance(content_block, Mapping):
            block_type = content_block.get("type")
            if isinstance(block_type, str) and block_type:
                normalized["content_block_type"] = block_type
            text = content_block.get("text")
            if isinstance(text, str) and text:
                normalized["delta"] = text
        return normalized
    if event_name == "content_block_delta":
        normalized["content_block_index"] = payload.get("index")
        delta = payload.get("delta")
        if isinstance(delta, Mapping):
            delta_type = delta.get("type")
            if isinstance(delta_type, str) and delta_type:
                normalized["delta_type"] = delta_type
            text = delta.get("text")
            if isinstance(text, str) and text:
                normalized["delta"] = text
            partial_json = delta.get("partial_json")
            if isinstance(partial_json, str) and partial_json:
                normalized["partial_json"] = partial_json
        elif isinstance(delta, str) and delta:
            normalized["delta"] = delta
        return normalized
    if event_name == "content_block_stop":
        normalized["content_block_index"] = payload.get("index")
        return normalized
    if event_name == "message_delta":
        delta = payload.get("delta")
        if isinstance(delta, Mapping):
            stop_reason = delta.get("stop_reason")
            if isinstance(stop_reason, str) and stop_reason:
                normalized["stop_reason"] = stop_reason
            stop_sequence = delta.get("stop_sequence")
            if isinstance(stop_sequence, str) and stop_sequence:
                normalized["stop_sequence"] = stop_sequence
        return normalized
    if event_name == "message_stop":
        return normalized
    return normalized


__all__ = [
    "ClaudeAdapter",
    "ClaudeProviderError",
    "build_claude_request_body",
    "extract_claude_output_text",
    "parse_claude_sse_events",
]
