"""Unit tests for the bounded outbound OpenAI host-control lane."""

from __future__ import annotations

import json

import pytest

from cortex.runtime.openai import OpenAIRuntimeSession, run_openai_runtime_step
from cortex.runtime.openai_cli import build_openai_cli_record
from cortex.runtime.openai_host_control import (
    OpenAIHostControlRequest,
    OpenAIHostControlResult,
    run_openai_host_control,
)
from cortex.runtime.openai_host_transport import (
    OpenAIResponseStreamTransportError,
    _parse_sse_events,
)
from cortex.runtime.openai_ingress import parse_openai_host_event_envelope
from cortex.runtime.openai_service import OpenAIServiceState, handle_openai_service_request


def test_openai_host_control_request_constructs_strict_text_only_payload() -> None:
    request = OpenAIHostControlRequest(
        action_tag="openai-response-stream",
        model="gpt-5",
        input_text="hello",
        instructions="be terse",
        metadata={"trace_id": "oa-1"},
        max_output_tokens=32,
    )

    assert request.as_payload() == {
        "action_tag": "openai-response-stream",
        "request": {
            "model": "gpt-5",
            "input": "hello",
            "instructions": "be terse",
            "metadata": {"trace_id": "oa-1"},
            "max_output_tokens": 32,
        },
    }


def test_openai_host_control_result_rejects_wrong_action_tag() -> None:
    with pytest.raises(ValueError, match="openai-response-stream"):
        OpenAIHostControlResult(action_tag="bad", records=())


def test_openai_host_control_service_boundary_rejects_out_of_scope_keys() -> None:
    status_code, payload = handle_openai_service_request(
        "POST",
        "/v1/actions/response-stream",
        OpenAIServiceState(),
        json.dumps(
            {
                "action_tag": "openai-response-stream",
                "request": {
                    "model": "gpt-5",
                    "input": "hello",
                    "tools": [{"type": "function", "name": "bad"}],
                },
            }
        ).encode("utf-8"),
    )

    assert status_code == 400
    assert "strict text-only whitelist" in payload["error"]


def test_parse_sse_events_converts_stream_frames_into_o2_shaped_records() -> None:
    events = _parse_sse_events(
        [
            b"event: response.created\n",
            b'data: {"session_id":"oa-stream","response_id":"resp-1"}\n',
            b"\n",
            b"event: response.output_text.delta\n",
            b'data: {"session_id":"oa-stream","response_id":"resp-1","delta":"hello"}\n',
            b"\n",
            b"event: response.completed\n",
            (
                b'data: {"session_id":"oa-stream","response_id":"resp-1",'
                b'"commitment_id":"oa-commit-1","externally_consequential":true,'
                b'"result_artifact_ref":"oa-artifact-1"}\n'
            ),
            b"\n",
        ]
    )

    assert events == [
        {
            "type": "response.created",
            "session_id": "oa-stream",
            "response_id": "resp-1",
        },
        {
            "type": "response.output_text.delta",
            "session_id": "oa-stream",
            "response_id": "resp-1",
            "delta": "hello",
        },
        {
            "type": "response.completed",
            "session_id": "oa-stream",
            "response_id": "resp-1",
            "commitment_id": "oa-commit-1",
            "externally_consequential": True,
            "result_artifact_ref": "oa-artifact-1",
        },
    ]


def test_parse_sse_events_rejects_zero_event_stream() -> None:
    with pytest.raises(OpenAIResponseStreamTransportError, match="zero host events"):
        _parse_sse_events([])


def test_parse_sse_events_rejects_malformed_json_event() -> None:
    with pytest.raises(OpenAIResponseStreamTransportError, match="invalid JSON"):
        _parse_sse_events(
            [
                b"event: response.created\n",
                b"data: {not-json}\n",
                b"\n",
            ]
        )


def test_run_openai_host_control_matches_manual_o1_runtime_projection() -> None:
    raw_events = [
        {
            "type": "response.created",
            "session_id": "oa-control",
            "response_id": "resp-1",
        },
        {
            "type": "response.output_text.delta",
            "session_id": "oa-control",
            "response_id": "resp-1",
            "delta": "hello",
        },
        {
            "type": "response.completed",
            "session_id": "oa-control",
            "response_id": "resp-1",
            "commitment_id": "oa-commit-1",
            "externally_consequential": True,
            "result_artifact_ref": "oa-artifact-1",
        },
    ]
    request = OpenAIHostControlRequest(
        action_tag="openai-response-stream",
        model="gpt-5",
        input_text="hello",
    )
    result, final_session = run_openai_host_control(
        request,
        transport=lambda _: list(raw_events),
    )

    expected_records = []
    current_session = OpenAIRuntimeSession()
    for raw_event in raw_events:
        envelope = parse_openai_host_event_envelope(raw_event)
        step_result = run_openai_runtime_step(
            envelope.event_type,
            envelope.payload,
            current_session,
        )
        expected_records.append(build_openai_cli_record(step_result))
        current_session = step_result.session

    assert result.as_payload() == {
        "action_tag": "openai-response-stream",
        "records": expected_records,
    }
    assert final_session == current_session
