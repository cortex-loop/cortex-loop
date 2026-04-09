"""Unit tests for the loopback Claude service shell."""

from __future__ import annotations

from experimental.runtime.claude import ClaudeRuntimeSession
from experimental.runtime.claude_service import (
    ClaudeServiceState,
    build_claude_service_server,
    export_claude_service_session,
    handle_claude_service_action,
    handle_claude_service_request,
    import_claude_service_session,
)


def test_claude_service_state_constructs_cleanly() -> None:
    state = ClaudeServiceState()

    assert isinstance(state.session, ClaudeRuntimeSession)
    assert state.session.event_index == 0
    assert state.session_loaded is False


def test_claude_service_import_export_preserves_exact_artifact_shape() -> None:
    state = ClaudeServiceState()
    state.replace_session(
        ClaudeRuntimeSession(
            session_id="cl-service",
            event_index=2,
            budget_history=("shell-low", "shell-medium"),
        ),
        session_loaded=True,
    )

    exported = export_claude_service_session(state)
    imported = import_claude_service_session(exported, ClaudeServiceState())

    assert tuple(exported) == (
        "artifact_kind",
        "artifact_version",
        "continuity_truth",
        "control_residue",
    )
    assert imported == exported


def test_claude_service_server_binds_loopback_only() -> None:
    server = build_claude_service_server(0)
    try:
        assert server.server_address[0] == "127.0.0.1"
    finally:
        server.server_close()


def test_claude_service_invalid_import_becomes_400_error_payload() -> None:
    status_code, payload = handle_claude_service_request(
        "POST",
        "/v1/session/import",
        ClaudeServiceState(),
        b'{"artifact_kind":"bad","artifact_version":1,"continuity_truth":{},"control_residue":{}}',
    )

    assert status_code == 400
    assert payload["error"].startswith("ClaudeRuntimeSessionArtifact.artifact_kind")


def test_claude_service_action_roundtrips_records_with_fake_transport() -> None:
    payload = {
        "action_tag": "claude-message-stream",
        "request": {
            "model": "claude-sonnet-4-6",
            "input": "hello",
            "max_output_tokens": 32,
        },
    }
    state = ClaudeServiceState()

    result = handle_claude_service_action(
        payload,
        state,
        outbound_transport=lambda _: [
            {
                "type": "message_start",
                "session_id": "cl-service-action",
                "message_id": "cl-msg-action-1",
            },
            {
                "type": "message_stop",
                "session_id": "cl-service-action",
                "message_id": "cl-msg-action-1",
                "commitment_id": "cl-service-action-commit-1",
                "externally_consequential": True,
                "result_artifact_ref": "cl-service-action-artifact-1",
            },
        ],
    )

    assert result["action_tag"] == "claude-message-stream"
    assert [record["raw_host_event_name"] for record in result["records"]] == [
        "message_start",
        "message_stop",
    ]
    assert state.session.event_index == 2
    assert state.session_loaded is True
