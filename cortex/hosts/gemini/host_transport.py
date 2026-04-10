"""Stdlib-only transport for the bounded outbound Gemini interaction-stream lane."""

from __future__ import annotations

import json
import os
from pathlib import Path
import urllib.error
import urllib.request
from collections.abc import Iterable, Mapping
from http.client import HTTPResponse
from typing import TYPE_CHECKING, Any

from cortex.drivers.gemini_host import is_raw_gemini_host_event_name

if TYPE_CHECKING:
    from .host_control import GeminiHostControlRequest

_FIXTURE_PATH_ENV = "CORTEX_GEMINI_HOST_CONTROL_FIXTURE_PATH"
_FIXTURE_START_INDEX_ENV = "CORTEX_GEMINI_HOST_CONTROL_FIXTURE_START_INDEX"
_FIXTURE_CALL_INDEX: dict[str, int] = {}


class GeminiInteractionStreamTransportError(RuntimeError):
    """Raised when the bounded Gemini interaction-stream transport fails."""


def execute_gemini_interaction_stream(request: GeminiHostControlRequest) -> list[dict[str, Any]]:
    fixture_path = os.environ.get(_FIXTURE_PATH_ENV)
    if fixture_path:
        return _execute_fixture_interaction_stream(request, Path(fixture_path))

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise GeminiInteractionStreamTransportError(
            "GEMINI_API_KEY is required for the live Gemini host-control transport."
        )

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{request.model}:streamGenerateContent?alt=sse&key={api_key}"
    )
    body = _build_live_request_body(request)
    http_request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(http_request, timeout=60.0) as response:
            return _parse_sse_events(response)
    except urllib.error.HTTPError as exc:
        raise GeminiInteractionStreamTransportError(
            f"Gemini interaction-stream transport failed with HTTP {exc.code}: {_http_error_message(exc)}"
        ) from exc
    except urllib.error.URLError as exc:
        raise GeminiInteractionStreamTransportError(
            f"Gemini interaction-stream transport connection failed: {exc.reason}"
        ) from exc
    except OSError as exc:
        raise GeminiInteractionStreamTransportError(
            f"Gemini interaction-stream transport failed: {exc}"
        ) from exc


def _build_live_request_body(request: GeminiHostControlRequest) -> dict[str, Any]:
    body: dict[str, Any] = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": request.input_text}],
            }
        ]
    }
    if request.instructions is not None:
        body["systemInstruction"] = {
            "parts": [{"text": request.instructions}],
        }
    if request.max_output_tokens is not None:
        body["generationConfig"] = {"maxOutputTokens": request.max_output_tokens}
    return body


def _execute_fixture_interaction_stream(
    request: GeminiHostControlRequest,
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
        raise GeminiInteractionStreamTransportError(
            f"Gemini host-control fixture exhausted at call index {call_index}."
        )
    _FIXTURE_CALL_INDEX[fixture_key] = call_index + 1
    call = calls[call_index]
    expected_request = call.get("expected_request")
    if expected_request is not None and expected_request != request.as_payload():
        raise GeminiInteractionStreamTransportError(
            "Gemini host-control fixture expected request "
            f"{expected_request!r}, got {request.as_payload()!r}."
        )
    if "error" in call:
        error = call["error"]
        if not isinstance(error, str) or not error.strip():
            raise GeminiInteractionStreamTransportError(
                "Gemini host-control fixture `error` must be a non-empty string."
            )
        raise GeminiInteractionStreamTransportError(error)
    events = call.get("events")
    if not isinstance(events, list):
        raise GeminiInteractionStreamTransportError(
            "Gemini host-control fixture call must contain an `events` list."
        )
    normalized_events: list[dict[str, Any]] = []
    for event in events:
        if not isinstance(event, Mapping):
            actual_type = type(event).__name__
            raise GeminiInteractionStreamTransportError(
                "Gemini host-control fixture events must be JSON objects, "
                f"got {actual_type}."
            )
        normalized_events.append(dict(event))
    if not normalized_events:
        raise GeminiInteractionStreamTransportError(
            "Gemini host-control fixture returned zero host events."
        )
    return normalized_events


def _fixture_calls(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [{"events": payload}]
    if not isinstance(payload, Mapping):
        actual_type = type(payload).__name__
        raise GeminiInteractionStreamTransportError(
            "Gemini host-control fixture payload must be an object or list, "
            f"got {actual_type}."
        )
    if "calls" in payload:
        calls = payload["calls"]
        if not isinstance(calls, list):
            raise GeminiInteractionStreamTransportError(
                "Gemini host-control fixture `calls` must be a list."
            )
        return [dict(call) for call in calls]
    return [dict(payload)]


def _parse_sse_events(response: HTTPResponse | Iterable[bytes]) -> list[dict[str, Any]]:
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
            raise GeminiInteractionStreamTransportError(
                "Gemini interaction stream emitted an event without a data payload."
            )
        try:
            payload = json.loads(data)
        except json.JSONDecodeError as exc:
            raise GeminiInteractionStreamTransportError(
                "Gemini interaction stream emitted invalid JSON data."
            ) from exc
        if not isinstance(payload, dict):
            actual_type = type(payload).__name__
            raise GeminiInteractionStreamTransportError(
                "Gemini interaction stream emitted a non-object JSON event, "
                f"got {actual_type}."
            )
        normalized_payload = _normalize_gemini_stream_event(dict(payload), event_name)
        payload_type = normalized_payload.get("type")
        if not (isinstance(payload_type, str) and payload_type.strip()):
            raise GeminiInteractionStreamTransportError(
                "Gemini interaction stream event must contain a non-empty `type`."
            )
        if payload_type == "error":
            raise GeminiInteractionStreamTransportError(
                f"Gemini interaction stream error: {_event_error_message(normalized_payload)}"
            )
        if not is_raw_gemini_host_event_name(payload_type):
            raise GeminiInteractionStreamTransportError(
                "Gemini interaction stream emitted a non-host event type "
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
        raise GeminiInteractionStreamTransportError(
            "Gemini interaction stream returned zero host events."
        )
    return events


def _normalize_gemini_stream_event(
    payload: dict[str, Any],
    event_name: str | None,
) -> dict[str, Any]:
    if event_name == "error":
        payload["type"] = "error"
        return payload
    if event_name is not None and is_raw_gemini_host_event_name(event_name):
        normalized = dict(payload)
        normalized["type"] = event_name
        return normalized
    if "type" in payload:
        return payload

    candidates = payload.get("candidates")
    if isinstance(candidates, list) and candidates:
        first = candidates[0]
        if isinstance(first, Mapping):
            content = first.get("content")
            if isinstance(content, Mapping):
                parts = content.get("parts")
                if isinstance(parts, list) and parts:
                    text_chunks: list[str] = []
                    for part in parts:
                        if isinstance(part, Mapping):
                            text = part.get("text")
                            if isinstance(text, str) and text:
                                text_chunks.append(text)
                    if text_chunks:
                        return {
                            "type": "content.delta",
                            "interaction_id": _interaction_id(payload),
                            "delta": {"type": "text", "text": "".join(text_chunks)},
                        }
    if event_name == "message":
        return {
            "type": "content.start",
            "interaction_id": _interaction_id(payload),
        }
    return {
        "type": "interaction.complete",
        "interaction_id": _interaction_id(payload),
    }


def _interaction_id(payload: Mapping[str, Any]) -> str:
    response_id = payload.get("responseId")
    if isinstance(response_id, str) and response_id.strip():
        return response_id.strip()
    model_version = payload.get("modelVersion")
    if isinstance(model_version, str) and model_version.strip():
        return f"local-{model_version.strip()}"
    return "local-gemini-interaction"


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
    "GeminiInteractionStreamTransportError",
    "execute_gemini_interaction_stream",
]
