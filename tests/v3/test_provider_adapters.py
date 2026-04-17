"""Provider adapter request-shape and event-normalization tests for Cortex v3."""

from __future__ import annotations

import os

import pytest

from cortex_v3.contracts import ProviderTurnRequest
from cortex_v3.providers.base import ProviderExecutionError
from cortex_v3.providers.claude import (
    ClaudeAdapter,
    build_claude_request_body,
    extract_claude_output_text,
    parse_claude_sse_events,
)
from cortex_v3.providers.gemini import (
    GeminiAdapter,
    build_gemini_request_body,
    extract_gemini_output_text,
    parse_gemini_sse_events,
)
from cortex_v3.providers.openai import (
    OpenAIAdapter,
    build_openai_request_body,
    extract_openai_output_text,
    parse_openai_sse_events,
)


def _request(provider: str) -> ProviderTurnRequest:
    return ProviderTurnRequest(
        provider=provider,
        model="test-model",
        prompt="return a protocol block",
        instructions="Return protocol blocks only.",
        metadata={"task_id": "fixture"},
        max_output_tokens=256,
    )


def test_openai_request_body_and_sse_parsing() -> None:
    request = _request("openai")
    body = build_openai_request_body(request)

    assert body["model"] == "test-model"
    assert "previous_response_id" not in body
    events = parse_openai_sse_events(
        [
            b"event: response.created\n",
            b'data: {"response_id":"resp-1"}\n',
            b"\n",
            b"event: response.output_text.delta\n",
            b'data: {"response_id":"resp-1","delta":"hello"}\n',
            b"\n",
            b"data: [DONE]\n",
            b"\n",
        ]
    )

    assert extract_openai_output_text(events) == "hello"


def test_claude_request_body_and_sse_parsing() -> None:
    request = _request("claude")
    body = build_claude_request_body(request)

    assert body["model"] == "test-model"
    assert body["max_tokens"] == 256
    events = parse_claude_sse_events(
        [
            b"event: content_block_delta\n",
            b'data: {"type":"content_block_delta","message":{"id":"msg-1"},"index":0,"delta":{"type":"text_delta","text":"hello"}}\n',
            b"\n",
            b"event: message_stop\n",
            b'data: {"type":"message_stop","message":{"id":"msg-1"}}\n',
            b"\n",
        ]
    )

    assert extract_claude_output_text(events) == "hello"


def test_gemini_request_body_and_sse_parsing() -> None:
    request = _request("gemini")
    body = build_gemini_request_body(request)

    assert body["contents"][0]["parts"][0]["text"] == "return a protocol block"
    events = parse_gemini_sse_events(
        [
            b"data: {\"responseId\":\"gm-1\",\"candidates\":[{\"content\":{\"parts\":[{\"text\":\"hello\"}]}}]}\n",
            b"\n",
            b"data: [DONE]\n",
            b"\n",
        ]
    )

    assert extract_gemini_output_text(events) == "hello"


@pytest.mark.parametrize(
    ("adapter", "env_var"),
    [
        (OpenAIAdapter(), "CORTEX_V3_OPENAI_FIXTURE_PATH"),
        (ClaudeAdapter(), "CORTEX_V3_CLAUDE_FIXTURE_PATH"),
        (GeminiAdapter(), "CORTEX_V3_GEMINI_FIXTURE_PATH"),
    ],
)
def test_provider_fixture_errors_raise_shared_adapter_contract(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
    adapter,
    env_var: str,
) -> None:
    fixture_path = tmp_path / "fixture.json"
    fixture_path.write_text('{"calls":[{"error":"boom"}]}', encoding="utf-8")
    monkeypatch.setenv(env_var, str(fixture_path))
    request = _request(adapter.provider)

    with pytest.raises(ProviderExecutionError):
        adapter.execute_turn(request)

    monkeypatch.delenv(env_var)
    os.environ.pop(env_var, None)
