"""Unit tests for the bounded outbound Claude host-control lane."""

from __future__ import annotations

import json

import pytest

from cortex.hosts.claude.runtime import ClaudeRuntimeSession, run_claude_runtime_step
from cortex.hosts.claude.cli import build_claude_cli_record
from cortex.hosts.claude.host_control import (
    ClaudeHostControlRequest,
    ClaudeHostControlResult,
    run_claude_host_control,
)
from cortex.hosts.claude.host_transport import (
    ClaudeMessageStreamTransportError,
    _parse_sse_events,
)
from cortex.hosts.claude.ingress import parse_claude_host_event_envelope
from cortex.hosts.claude.service import ClaudeServiceState, handle_claude_service_request


def test_claude_host_control_request_constructs_strict_text_only_payload() -> None:
    request = ClaudeHostControlRequest(
        action_tag="claude-message-stream",
        model="claude-sonnet-4-6",
        input_text="hello",
        max_output_tokens=32,
        system="be terse",
        metadata={"trace_id": "cl-1"},
    )

    assert request.as_payload() == {
        "action_tag": "claude-message-stream",
        "request": {
            "model": "claude-sonnet-4-6",
            "input": "hello",
            "max_output_tokens": 32,
            "system": "be terse",
            "metadata": {"trace_id": "cl-1"},
        },
    }


def test_claude_host_control_result_rejects_wrong_action_tag() -> None:
    with pytest.raises(ValueError, match="claude-message-stream"):
        ClaudeHostControlResult(action_tag="bad", records=())


def test_claude_host_control_service_boundary_rejects_out_of_scope_keys() -> None:
    status_code, payload = handle_claude_service_request(
        "POST",
        "/v1/actions/message-stream",
        ClaudeServiceState(),
        json.dumps(
            {
                "action_tag": "claude-message-stream",
                "request": {
                    "model": "claude-sonnet-4-6",
                    "input": "hello",
                    "tools": [{"type": "function", "name": "bad"}],
                },
            }
        ).encode("utf-8"),
    )

    assert status_code == 400
    assert "strict text-only whitelist" in payload["error"]


def test_parse_sse_events_converts_stream_frames_into_g2_shaped_records() -> None:
    events = _parse_sse_events(
        [
            b"event: message_start\n",
            b'data: {"type":"message_start","message":{"id":"cl-msg-1","role":"assistant","model":"claude-sonnet-4-6"}}\n',
            b"\n",
            b"event: content_block_delta\n",
            b'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"hello"}}\n',
            b"\n",
            b"event: message_stop\n",
            b'data: {"type":"message_stop"}\n',
            b"\n",
        ]
    )

    assert events == [
        {
            "type": "message_start",
            "message_id": "cl-msg-1",
            "role": "assistant",
            "model": "claude-sonnet-4-6",
        },
        {
            "type": "content_block_delta",
            "message_id": "cl-msg-1",
            "content_block_index": 0,
            "delta_type": "text_delta",
            "delta": "hello",
        },
        {
            "type": "message_stop",
            "message_id": "cl-msg-1",
            "commitment_id": "claude-commit:cl-msg-1",
            "externally_consequential": True,
            "result_artifact_ref": "claude-artifact:cl-msg-1",
        },
    ]


def test_parse_sse_events_rejects_zero_event_stream() -> None:
    with pytest.raises(ClaudeMessageStreamTransportError, match="zero host events"):
        _parse_sse_events([])


def test_parse_sse_events_rejects_malformed_json_event() -> None:
    with pytest.raises(ClaudeMessageStreamTransportError, match="invalid JSON"):
        _parse_sse_events(
            [
                b"event: message_start\n",
                b"data: {not-json}\n",
                b"\n",
            ]
        )


def test_run_claude_host_control_matches_manual_g1_runtime_projection() -> None:
    raw_events = [
        {
            "type": "message_start",
            "session_id": "cl-control",
            "message_id": "cl-msg-1",
        },
        {
            "type": "content_block_delta",
            "session_id": "cl-control",
            "message_id": "cl-msg-1",
            "delta": "hello",
        },
        {
            "type": "message_stop",
            "session_id": "cl-control",
            "message_id": "cl-msg-1",
            "commitment_id": "cl-commit-1",
            "externally_consequential": True,
            "result_artifact_ref": "cl-artifact-1",
        },
    ]
    request = ClaudeHostControlRequest(
        action_tag="claude-message-stream",
        model="claude-sonnet-4-6",
        input_text="hello",
        max_output_tokens=32,
    )
    result, final_session = run_claude_host_control(
        request,
        transport=lambda _: list(raw_events),
    )

    expected_records = []
    current_session = ClaudeRuntimeSession()
    for raw_event in raw_events:
        envelope = parse_claude_host_event_envelope(raw_event)
        step_result = run_claude_runtime_step(
            envelope.event_type,
            envelope.payload,
            current_session,
        )
        expected_records.append(build_claude_cli_record(step_result))
        current_session = step_result.session

    assert result.as_payload() == {
        "action_tag": "claude-message-stream",
        "records": expected_records,
    }
    assert final_session == current_session
