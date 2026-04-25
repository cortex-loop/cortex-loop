"""Stdlib-only transport for the bounded outbound Claude message-stream lane."""

from __future__ import annotations

import json
import os
from pathlib import Path
import urllib.error
import urllib.request
from collections.abc import Iterable, Mapping
from http.client import HTTPResponse
from typing import TYPE_CHECKING, Any

from cortex.drivers.claude_host import is_raw_claude_host_event_name

if TYPE_CHECKING:
    from .host_control import ClaudeHostControlRequest

_FIXTURE_PATH_ENV = "CORTEX_CLAUDE_HOST_CONTROL_FIXTURE_PATH"
_FIXTURE_START_INDEX_ENV = "CORTEX_CLAUDE_HOST_CONTROL_FIXTURE_START_INDEX"
_FIXTURE_CALL_INDEX: dict[str, int] = {}


class ClaudeMessageStreamTransportError(RuntimeError):
    """Raised when the bounded Claude message-stream transport fails."""


def execute_claude_message_stream(request: ClaudeHostControlRequest) -> list[dict[str, Any]]:
    fixture_path = os.environ.get(_FIXTURE_PATH_ENV)
    if fixture_path:
        return _execute_fixture_message_stream(request, Path(fixture_path))

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ClaudeMessageStreamTransportError(
            "ANTHROPIC_API_KEY is required for the live Claude host-control transport."
        )

    url = "https://api.anthropic.com/v1/messages"
    body = _build_live_request_body(request)
    http_request = urllib.request.Request(
        url,
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
            return _parse_sse_events(response)
    except urllib.error.HTTPError as exc:
        raise ClaudeMessageStreamTransportError(
            f"Claude message-stream transport failed with HTTP {exc.code}: {_http_error_message(exc)}"
        ) from exc
    except urllib.error.URLError as exc:
        raise ClaudeMessageStreamTransportError(
            f"Claude message-stream transport connection failed: {exc.reason}"
        ) from exc
    except OSError as exc:
        raise ClaudeMessageStreamTransportError(
            f"Claude message-stream transport failed: {exc}"
        ) from exc


def _build_live_request_body(request: ClaudeHostControlRequest) -> dict[str, Any]:
    body: dict[str, Any] = {
        "model": request.model,
        "max_tokens": request.max_output_tokens,
        "messages": [{"role": "user", "content": request.input_text}],
        "stream": True,
    }
    if request.system is not None:
        body["system"] = request.system
    if request.metadata:
        body["metadata"] = dict(request.metadata)
    return body


def _execute_fixture_message_stream(
    request: ClaudeHostControlRequest,
    fixture_path: Path,
) -> list[dict[str, Any]]:
    fixture_payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    calls = _fixture_calls(fixture_payload)
    fixture_key = str(fixture_path)
    if fixture_key not in _FIXTURE_CALL_INDEX:
        _FIXTURE_CALL_INDEX[fixture_key] = int(
            os.environ.get(_FIXTURE_START_INDEX_ENV, "0")
        )
    call_index = _FIXTURE_CALL_INDEX[fixture_key]
    if call_index >= len(calls):
        raise ClaudeMessageStreamTransportError(
            f"Claude host-control fixture exhausted at call index {call_index}."
        )
    _FIXTURE_CALL_INDEX[fixture_key] = call_index + 1
    call = calls[call_index]
    expected_request = call.get("expected_request")
    if expected_request is not None and expected_request != request.as_payload():
        raise ClaudeMessageStreamTransportError(
            "Claude host-control fixture expected request "
            f"{expected_request!r}, got {request.as_payload()!r}."
        )
    expected_request_subset = call.get("expected_request_subset")
    if expected_request_subset is not None and not _payload_contains(
        request.as_payload(),
        expected_request_subset,
    ):
        raise ClaudeMessageStreamTransportError(
            "Claude host-control fixture expected request subset "
            f"{expected_request_subset!r}, got {request.as_payload()!r}."
        )
    if "error" in call:
        error = call["error"]
        if not isinstance(error, str) or not error.strip():
            raise ClaudeMessageStreamTransportError(
                "Claude host-control fixture `error` must be a non-empty string."
            )
        raise ClaudeMessageStreamTransportError(error)
    events = call.get("events")
    if not isinstance(events, list):
        raise ClaudeMessageStreamTransportError(
            "Claude host-control fixture call must contain an `events` list."
        )
    normalized_events: list[dict[str, Any]] = []
    for event in events:
        if not isinstance(event, Mapping):
            actual_type = type(event).__name__
            raise ClaudeMessageStreamTransportError(
                "Claude host-control fixture events must be JSON objects, "
                f"got {actual_type}."
            )
        normalized_events.append(dict(event))
    if not normalized_events:
        raise ClaudeMessageStreamTransportError(
            "Claude host-control fixture returned zero host events."
        )
    return normalized_events


def _fixture_calls(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [{"events": payload}]
    if not isinstance(payload, Mapping):
        actual_type = type(payload).__name__
        raise ClaudeMessageStreamTransportError(
            "Claude host-control fixture payload must be an object or list, "
            f"got {actual_type}."
        )
    if "calls" in payload:
        calls = payload["calls"]
        if not isinstance(calls, list):
            raise ClaudeMessageStreamTransportError(
                "Claude host-control fixture `calls` must be a list."
            )
        return [dict(call) for call in calls]
    return [dict(payload)]


def _payload_contains(actual: Any, expected: Any) -> bool:
    if isinstance(expected, Mapping):
        if not isinstance(actual, Mapping):
            return False
        return all(
            key in actual and _payload_contains(actual[key], expected_value)
            for key, expected_value in expected.items()
        )
    if isinstance(expected, list):
        if not isinstance(actual, list) or len(actual) < len(expected):
            return False
        return all(
            _payload_contains(actual_item, expected_item)
            for actual_item, expected_item in zip(actual, expected, strict=False)
        )
    return actual == expected


def _parse_sse_events(response: HTTPResponse | Iterable[bytes]) -> list[dict[str, Any]]:
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
            raise ClaudeMessageStreamTransportError(
                "Claude message stream emitted an event without a data payload."
            )
        try:
            payload = json.loads(data)
        except json.JSONDecodeError as exc:
            raise ClaudeMessageStreamTransportError(
                "Claude message stream emitted invalid JSON data."
            ) from exc
        if not isinstance(payload, dict):
            actual_type = type(payload).__name__
            raise ClaudeMessageStreamTransportError(
                "Claude message stream emitted a non-object JSON event, "
                f"got {actual_type}."
            )
        if event_name == "error":
            raise ClaudeMessageStreamTransportError(
                f"Claude message stream error: {_event_error_message(payload)}"
            )
        normalized_payload = _normalize_claude_stream_event(dict(payload), event_name)
        if active_message_id is not None and "message_id" not in normalized_payload:
            normalized_payload["message_id"] = active_message_id
        message_id = normalized_payload.get("message_id")
        if isinstance(message_id, str) and message_id.strip():
            active_message_id = message_id
            if normalized_payload.get("type") == "message_stop":
                normalized_payload.setdefault("commitment_id", f"claude-commit:{message_id}")
                normalized_payload.setdefault("externally_consequential", True)
                normalized_payload.setdefault(
                    "result_artifact_ref", f"claude-artifact:{message_id}"
                )
        payload_type = normalized_payload.get("type")
        if not (isinstance(payload_type, str) and payload_type.strip()):
            raise ClaudeMessageStreamTransportError(
                "Claude message stream event must contain a non-empty `type`."
            )
        if not is_raw_claude_host_event_name(payload_type):
            raise ClaudeMessageStreamTransportError(
                "Claude message stream emitted a non-host event type "
                f"{payload_type!r}."
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
        raise ClaudeMessageStreamTransportError(
            "Claude message stream returned zero host events."
        )
    return events


def _normalize_claude_stream_event(
    payload: dict[str, Any],
    event_name: str | None,
) -> dict[str, Any]:
    if event_name is not None and is_raw_claude_host_event_name(event_name):
        normalized = _base_stream_payload(payload, event_name)
        normalized["type"] = event_name
        return normalized
    if "type" in payload:
        return payload
    raise ClaudeMessageStreamTransportError(
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
        if message_id is not None:
            normalized["commitment_id"] = f"claude-commit:{message_id}"
            normalized["externally_consequential"] = True
            normalized["result_artifact_ref"] = f"claude-artifact:{message_id}"
        return normalized
    return normalized


def _http_error_message(exc: urllib.error.HTTPError) -> str:
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


def _event_error_message(payload: Mapping[str, Any]) -> str:
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


__all__ = [
    "ClaudeMessageStreamTransportError",
    "execute_claude_message_stream",
]
