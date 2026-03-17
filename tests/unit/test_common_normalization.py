"""Focused tests for common driver normalization."""

from cortex.drivers.common_normalization import (
    normalize_driver_event,
    normalize_driver_payload,
    normalize_event_name,
)


def test_event_name_alias_and_casing_normalization() -> None:
    assert normalize_event_name("SessionStart") == "session/start"
    assert normalize_event_name("pre_tool_use") == "tool/pre"
    assert normalize_event_name("TURN_COMPLETED") == "turn/complete"
    assert normalize_event_name("approval-request") == "approval/request"


def test_normalized_event_carrier_returns_normalized_name_and_payload_copy() -> None:
    payload = {"tool": " apply_patch ", "session_id": " session-1 ", "custom": "value"}

    event = normalize_driver_event("PreToolUse", payload)

    assert event.native_event_name == "PreToolUse"
    assert event.event_name == "tool/pre"
    assert event.payload == {
        "tool": " apply_patch ",
        "tool_name": "apply_patch",
        "session_id": "session-1",
        "custom": "value",
    }
    assert event.payload is not payload
    assert "tool_name" not in payload


def test_payload_normalization_keeps_existing_native_commitment_fields_intact() -> None:
    payload = {
        "commitment_fields": {" claim_id ": "abc-123"},
        "session_id": " session-2 ",
    }

    normalized, warnings = normalize_driver_payload(payload)

    assert normalized["commitment_fields"] == {"claim_id": "abc-123"}
    assert normalized["commitment_fields_source"] == "native"
    assert normalized["session_id"] == "session-2"
    assert warnings == ()


def test_generic_payload_normalization_does_not_impose_host_specific_doctrine() -> None:
    payload = {
        "tool": " edit ",
        "custom_host_token": "host-123",
        "message": 'COMMITMENT_FIELDS_JSON: {"claim_summary": "done"}',
    }

    normalized, warnings = normalize_driver_payload(payload)

    assert normalized["tool_name"] == "edit"
    assert normalized["custom_host_token"] == "host-123"
    assert "runtime_mode" not in normalized
    assert "stop_trailer_marker" not in normalized
    assert "status" not in normalized
    assert "commitment_fields" not in normalized
    assert warnings == ()
