"""Focused tests for raw Claude transcript ingress parsing."""

import pytest

from experimental.runtime.claude_ingress import (
    ClaudeHostEventEnvelope,
    parse_claude_host_event_envelope,
)


def test_documented_raw_claude_event_parses_cleanly() -> None:
    envelope = parse_claude_host_event_envelope(
        {
            "type": "content_block_delta",
            "session_id": "cl-ingress",
            "message_id": "cl-msg-1",
            "delta": "hello",
        }
    )

    assert envelope == ClaudeHostEventEnvelope(
        event_type="content_block_delta",
        payload={
            "session_id": "cl-ingress",
            "message_id": "cl-msg-1",
            "delta": "hello",
        },
    )


def test_undocumented_raw_response_event_still_parses_cleanly() -> None:
    envelope = parse_claude_host_event_envelope(
        {"type": "content_block_magic", "session_id": "cl-ingress", "message_id": "cl-msg-1"}
    )

    assert envelope.event_type == "content_block_magic"
    assert envelope.payload["session_id"] == "cl-ingress"


def test_canonical_cortex_event_name_is_rejected() -> None:
    with pytest.raises(ValueError, match="raw Claude host event name"):
        parse_claude_host_event_envelope(
            {"type": "external/observation", "session_id": "cl-ingress"}
        )


def test_dev_shell_wrapper_shape_is_rejected() -> None:
    with pytest.raises(ValueError, match="wrapper and mixed wrapper/transcript"):
        parse_claude_host_event_envelope(
            {
                "event_name": "message_stop",
                "payload": {"session_id": "cl-ingress"},
            }
        )


def test_mixed_wrapper_and_transcript_shape_is_rejected() -> None:
    with pytest.raises(ValueError, match="wrapper and mixed wrapper/transcript"):
        parse_claude_host_event_envelope(
            {
                "type": "message_stop",
                "event_name": "message_stop",
                "payload": {"session_id": "cl-ingress"},
                "session_id": "cl-ingress",
            }
        )


def test_missing_type_and_non_object_record_are_rejected() -> None:
    with pytest.raises(ValueError, match="include `type`"):
        parse_claude_host_event_envelope({"session_id": "cl-ingress"})

    with pytest.raises(TypeError, match="must be a mapping"):
        parse_claude_host_event_envelope(["not-an-object"])
