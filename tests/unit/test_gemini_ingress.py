"""Focused tests for raw Gemini transcript ingress parsing."""

import pytest

from cortex.hosts.gemini.ingress import (
    GeminiHostEventEnvelope,
    parse_gemini_host_event_envelope,
)


def test_documented_raw_gemini_event_parses_cleanly() -> None:
    envelope = parse_gemini_host_event_envelope(
        {
            "type": "content.delta",
            "session_id": "gm-ingress",
            "interaction_id": "gm-int-1",
            "delta": "hello",
        }
    )

    assert envelope == GeminiHostEventEnvelope(
        event_type="content.delta",
        payload={
            "session_id": "gm-ingress",
            "interaction_id": "gm-int-1",
            "delta": "hello",
        },
    )


def test_undocumented_raw_response_event_still_parses_cleanly() -> None:
    envelope = parse_gemini_host_event_envelope(
        {"type": "content.tool_event", "session_id": "gm-ingress", "interaction_id": "gm-int-1"}
    )

    assert envelope.event_type == "content.tool_event"
    assert envelope.payload["session_id"] == "gm-ingress"


def test_canonical_cortex_event_name_is_rejected() -> None:
    with pytest.raises(ValueError, match="raw Gemini host event name"):
        parse_gemini_host_event_envelope(
            {"type": "external/observation", "session_id": "gm-ingress"}
        )


def test_dev_shell_wrapper_shape_is_rejected() -> None:
    with pytest.raises(ValueError, match="wrapper and mixed wrapper/transcript"):
        parse_gemini_host_event_envelope(
            {
                "event_name": "interaction.complete",
                "payload": {"session_id": "gm-ingress"},
            }
        )


def test_mixed_wrapper_and_transcript_shape_is_rejected() -> None:
    with pytest.raises(ValueError, match="wrapper and mixed wrapper/transcript"):
        parse_gemini_host_event_envelope(
            {
                "type": "interaction.complete",
                "event_name": "interaction.complete",
                "payload": {"session_id": "gm-ingress"},
                "session_id": "gm-ingress",
            }
        )


def test_missing_type_and_non_object_record_are_rejected() -> None:
    with pytest.raises(ValueError, match="include `type`"):
        parse_gemini_host_event_envelope({"session_id": "gm-ingress"})

    with pytest.raises(TypeError, match="must be a mapping"):
        parse_gemini_host_event_envelope(["not-an-object"])
