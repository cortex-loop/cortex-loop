"""Unit tests for the bounded outbound Gemini host-control lane."""

from __future__ import annotations

import json

import pytest

from experimental.runtime.gemini import GeminiRuntimeSession, run_gemini_runtime_step
from experimental.runtime.gemini_cli import build_gemini_cli_record
from experimental.runtime.gemini_host_control import (
    GeminiHostControlRequest,
    GeminiHostControlResult,
    run_gemini_host_control,
)
from experimental.runtime.gemini_host_transport import (
    GeminiInteractionStreamTransportError,
    _parse_sse_events,
)
from experimental.runtime.gemini_ingress import parse_gemini_host_event_envelope
from experimental.runtime.gemini_service import GeminiServiceState, handle_gemini_service_request


def test_gemini_host_control_request_constructs_strict_text_only_payload() -> None:
    request = GeminiHostControlRequest(
        action_tag="gemini-interaction-stream",
        model="gemini-2.5-pro",
        input_text="hello",
        instructions="be terse",
        metadata={"trace_id": "gm-1"},
        max_output_tokens=32,
    )

    assert request.as_payload() == {
        "action_tag": "gemini-interaction-stream",
        "request": {
            "model": "gemini-2.5-pro",
            "input": "hello",
            "instructions": "be terse",
            "metadata": {"trace_id": "gm-1"},
            "max_output_tokens": 32,
        },
    }


def test_gemini_host_control_result_rejects_wrong_action_tag() -> None:
    with pytest.raises(ValueError, match="gemini-interaction-stream"):
        GeminiHostControlResult(action_tag="bad", records=())


def test_gemini_host_control_service_boundary_rejects_out_of_scope_keys() -> None:
    status_code, payload = handle_gemini_service_request(
        "POST",
        "/v1/actions/interaction-stream",
        GeminiServiceState(),
        json.dumps(
            {
                "action_tag": "gemini-interaction-stream",
                "request": {
                    "model": "gemini-2.5-pro",
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
            b"event: content.start\n",
            b'data: {"session_id":"gm-stream","interaction_id":"gm-int-1"}\n',
            b"\n",
            b"event: content.delta\n",
            b'data: {"session_id":"gm-stream","interaction_id":"gm-int-1","delta":"hello"}\n',
            b"\n",
            b"event: interaction.complete\n",
            (
                b'data: {"session_id":"gm-stream","interaction_id":"gm-int-1",'
                b'"commitment_id":"gm-commit-1","externally_consequential":true,'
                b'"result_artifact_ref":"gm-artifact-1"}\n'
            ),
            b"\n",
        ]
    )

    assert events == [
        {
            "type": "content.start",
            "session_id": "gm-stream",
            "interaction_id": "gm-int-1",
        },
        {
            "type": "content.delta",
            "session_id": "gm-stream",
            "interaction_id": "gm-int-1",
            "delta": "hello",
        },
        {
            "type": "interaction.complete",
            "session_id": "gm-stream",
            "interaction_id": "gm-int-1",
            "commitment_id": "gm-commit-1",
            "externally_consequential": True,
            "result_artifact_ref": "gm-artifact-1",
        },
    ]


def test_parse_sse_events_rejects_zero_event_stream() -> None:
    with pytest.raises(GeminiInteractionStreamTransportError, match="zero host events"):
        _parse_sse_events([])


def test_parse_sse_events_rejects_malformed_json_event() -> None:
    with pytest.raises(GeminiInteractionStreamTransportError, match="invalid JSON"):
        _parse_sse_events(
            [
                b"event: content.start\n",
                b"data: {not-json}\n",
                b"\n",
            ]
        )


def test_run_gemini_host_control_matches_manual_g1_runtime_projection() -> None:
    raw_events = [
        {
            "type": "content.start",
            "session_id": "gm-control",
            "interaction_id": "gm-int-1",
        },
        {
            "type": "content.delta",
            "session_id": "gm-control",
            "interaction_id": "gm-int-1",
            "delta": "hello",
        },
        {
            "type": "interaction.complete",
            "session_id": "gm-control",
            "interaction_id": "gm-int-1",
            "commitment_id": "gm-commit-1",
            "externally_consequential": True,
            "result_artifact_ref": "gm-artifact-1",
        },
    ]
    request = GeminiHostControlRequest(
        action_tag="gemini-interaction-stream",
        model="gemini-2.5-pro",
        input_text="hello",
    )
    result, final_session = run_gemini_host_control(
        request,
        transport=lambda _: list(raw_events),
    )

    expected_records = []
    current_session = GeminiRuntimeSession()
    for raw_event in raw_events:
        envelope = parse_gemini_host_event_envelope(raw_event)
        step_result = run_gemini_runtime_step(
            envelope.event_type,
            envelope.payload,
            current_session,
        )
        expected_records.append(build_gemini_cli_record(step_result))
        current_session = step_result.session

    assert result.as_payload() == {
        "action_tag": "gemini-interaction-stream",
        "records": expected_records,
    }
    assert final_session == current_session
