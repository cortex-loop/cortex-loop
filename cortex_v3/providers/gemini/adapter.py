"""Thin Gemini adapter for the Cortex v3 verified-work engine."""

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


_FIXTURE_PATH_ENV = "CORTEX_V3_GEMINI_FIXTURE_PATH"
_FIXTURE_START_INDEX_ENV = "CORTEX_V3_GEMINI_FIXTURE_START_INDEX"
_FIXTURE_CALL_INDEX: dict[str, int] = {}

GeminiTransport = Callable[[ProviderTurnRequest], list[dict[str, Any]]]


class GeminiProviderError(ProviderExecutionError):
    """Raised when the Gemini adapter cannot complete a turn."""


class GeminiAdapter:
    provider = "gemini"

    def __init__(self, *, transport: GeminiTransport | None = None) -> None:
        self._transport = transport

    def execute_turn(self, request: ProviderTurnRequest) -> ProviderTurnResponse:
        events = self._execute_events(request)
        return ProviderTurnResponse(
            provider=self.provider,
            output_text=extract_gemini_output_text(events),
            raw_events=tuple(events),
        )

    def _execute_events(self, request: ProviderTurnRequest) -> list[dict[str, Any]]:
        if self._transport is not None:
            events = self._transport(request)
            if not isinstance(events, list):
                actual_type = type(events).__name__
                raise GeminiProviderError(
                    "GeminiAdapter transport must return list[dict[str, Any]], "
                    f"got {actual_type}."
                )
            return [dict(event) for event in events]
        fixture_path = os.environ.get(_FIXTURE_PATH_ENV)
        if fixture_path:
            return _execute_fixture_turn(request, Path(fixture_path))
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise GeminiProviderError(
                "GEMINI_API_KEY is required for the live Gemini V3 adapter."
            )

        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{request.model}:streamGenerateContent?alt=sse&key={api_key}"
        )
        body = build_gemini_request_body(request)
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
                return parse_gemini_sse_events(response)
        except urllib.error.HTTPError as exc:
            raise GeminiProviderError(
                f"Gemini interaction-stream transport failed with HTTP {exc.code}: {http_error_message(exc)}"
            ) from exc
        except urllib.error.URLError as exc:
            raise GeminiProviderError(
                f"Gemini interaction-stream transport connection failed: {exc.reason}"
            ) from exc
        except OSError as exc:
            raise GeminiProviderError(
                f"Gemini interaction-stream transport failed: {exc}"
            ) from exc


def build_gemini_request_body(request: ProviderTurnRequest) -> dict[str, Any]:
    body: dict[str, Any] = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": request.prompt}],
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


def parse_gemini_sse_events(response: HTTPResponse | Iterable[bytes]) -> list[dict[str, Any]]:
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
            raise GeminiProviderError(
                "Gemini interaction stream emitted an event without a data payload."
            )
        try:
            payload = json.loads(data)
        except json.JSONDecodeError as exc:
            raise GeminiProviderError(
                "Gemini interaction stream emitted invalid JSON data."
            ) from exc
        if not isinstance(payload, dict):
            actual_type = type(payload).__name__
            raise GeminiProviderError(
                "Gemini interaction stream emitted a non-object JSON event, "
                f"got {actual_type}."
            )
        normalized_payload = _normalize_gemini_stream_event(dict(payload), event_name)
        payload_type = normalized_payload.get("type")
        if not (isinstance(payload_type, str) and payload_type.strip()):
            raise GeminiProviderError(
                "Gemini interaction stream event must contain a non-empty `type`."
            )
        if payload_type == "error":
            raise GeminiProviderError(
                f"Gemini interaction stream error: {stream_error_message(normalized_payload)}"
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
        raise GeminiProviderError("Gemini interaction stream returned zero host events.")
    return events


def extract_gemini_output_text(events: Iterable[Mapping[str, Any]]) -> str | None:
    chunks: list[str] = []
    for event in events:
        if event.get("type") != "content.delta":
            continue
        delta = event.get("delta")
        if isinstance(delta, Mapping):
            text = delta.get("text")
            if isinstance(text, str) and text:
                chunks.append(text)
        elif isinstance(delta, str) and delta:
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
    calls = fixture_calls(fixture_payload, label="Gemini V3")
    fixture_key = str(fixture_path)
    if fixture_key not in _FIXTURE_CALL_INDEX:
        _FIXTURE_CALL_INDEX[fixture_key] = int(
            os.environ.get(_FIXTURE_START_INDEX_ENV, "0")
        )
    call_index = _FIXTURE_CALL_INDEX[fixture_key]
    if call_index >= len(calls):
        raise GeminiProviderError(
            f"Gemini V3 fixture exhausted at call index {call_index}."
        )
    _FIXTURE_CALL_INDEX[fixture_key] = call_index + 1
    call = calls[call_index]
    expected_request = call.get("expected_request")
    if expected_request is not None and expected_request != request.as_payload():
        raise GeminiProviderError(
            "Gemini V3 fixture expected request "
            f"{expected_request!r}, got {request.as_payload()!r}."
        )
    expected_body = call.get("expected_body")
    live_body = build_gemini_request_body(request)
    if expected_body is not None and expected_body != live_body:
        raise GeminiProviderError(
            "Gemini V3 fixture expected body "
            f"{expected_body!r}, got {live_body!r}."
        )
    if "error" in call:
        error = call["error"]
        if not isinstance(error, str) or not error.strip():
            raise GeminiProviderError(
                "Gemini V3 fixture `error` must be a non-empty string."
            )
        raise GeminiProviderError(error)
    return normalized_fixture_events(call.get("events"), label="Gemini V3")


def _normalize_gemini_stream_event(
    payload: dict[str, Any],
    event_name: str | None,
) -> dict[str, Any]:
    if event_name == "error":
        payload["type"] = "error"
        return payload
    if event_name is not None:
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


__all__ = [
    "GeminiAdapter",
    "GeminiProviderError",
    "build_gemini_request_body",
    "extract_gemini_output_text",
    "parse_gemini_sse_events",
]
