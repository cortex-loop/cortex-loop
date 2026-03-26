"""Focused tests for raw OpenAI transcript ingress parsing."""

import pytest

from cortex.runtime.openai_ingress import (
    OpenAIHostEventEnvelope,
    parse_openai_host_event_envelope,
)


def test_documented_raw_openai_event_parses_cleanly() -> None:
    envelope = parse_openai_host_event_envelope(
        {
            "type": "response.output_text.delta",
            "session_id": "oa-ingress",
            "response_id": "resp-1",
            "delta": "hello",
        }
    )

    assert envelope == OpenAIHostEventEnvelope(
        event_type="response.output_text.delta",
        payload={
            "session_id": "oa-ingress",
            "response_id": "resp-1",
            "delta": "hello",
        },
    )


def test_undocumented_raw_response_event_still_parses_cleanly() -> None:
    envelope = parse_openai_host_event_envelope(
        {"type": "response.tool_event", "session_id": "oa-ingress", "response_id": "resp-1"}
    )

    assert envelope.event_type == "response.tool_event"
    assert envelope.payload["session_id"] == "oa-ingress"


def test_canonical_cortex_event_name_is_rejected() -> None:
    with pytest.raises(ValueError, match="raw OpenAI host event name"):
        parse_openai_host_event_envelope(
            {"type": "external/observation", "session_id": "oa-ingress"}
        )


def test_dev_shell_wrapper_shape_is_rejected() -> None:
    with pytest.raises(ValueError, match="dev-shell wrapper shape"):
        parse_openai_host_event_envelope(
            {
                "event_name": "response.completed",
                "payload": {"session_id": "oa-ingress"},
            }
        )


def test_missing_type_and_non_object_record_are_rejected() -> None:
    with pytest.raises(ValueError, match="include `type`"):
        parse_openai_host_event_envelope({"session_id": "oa-ingress"})

    with pytest.raises(TypeError, match="must be a mapping"):
        parse_openai_host_event_envelope(["not-an-object"])
