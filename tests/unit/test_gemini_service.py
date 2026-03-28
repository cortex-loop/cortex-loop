"""Unit tests for the loopback Gemini service shell."""

from __future__ import annotations

from cortex.runtime.gemini import GeminiRuntimeSession
from cortex.runtime.gemini_service import (
    GeminiServiceState,
    build_gemini_service_server,
    export_gemini_service_session,
    handle_gemini_service_action,
    handle_gemini_service_request,
    import_gemini_service_session,
)


def test_gemini_service_state_constructs_cleanly() -> None:
    state = GeminiServiceState()

    assert isinstance(state.session, GeminiRuntimeSession)
    assert state.session.event_index == 0
    assert state.session_loaded is False


def test_gemini_service_import_export_preserves_exact_artifact_shape() -> None:
    state = GeminiServiceState()
    state.replace_session(
        GeminiRuntimeSession(
            session_id="gm-service",
            event_index=2,
            budget_history=("shell-low", "shell-medium"),
        ),
        session_loaded=True,
    )

    exported = export_gemini_service_session(state)
    imported = import_gemini_service_session(exported, GeminiServiceState())

    assert tuple(exported) == (
        "artifact_kind",
        "artifact_version",
        "continuity_truth",
        "control_residue",
    )
    assert imported == exported


def test_gemini_service_server_binds_loopback_only() -> None:
    server = build_gemini_service_server(0)
    try:
        assert server.server_address[0] == "127.0.0.1"
    finally:
        server.server_close()


def test_gemini_service_invalid_import_becomes_400_error_payload() -> None:
    status_code, payload = handle_gemini_service_request(
        "POST",
        "/v1/session/import",
        GeminiServiceState(),
        b'{"artifact_kind":"bad","artifact_version":1,"continuity_truth":{},"control_residue":{}}',
    )

    assert status_code == 400
    assert payload["error"].startswith("GeminiRuntimeSessionArtifact.artifact_kind")


def test_gemini_service_action_roundtrips_records_with_fake_transport() -> None:
    payload = {
        "action_tag": "gemini-interaction-stream",
        "request": {
            "model": "gpt-5.4",
            "input": "hello",
        },
    }
    state = GeminiServiceState()

    result = handle_gemini_service_action(
        payload,
        state,
        outbound_transport=lambda _: [
            {
                "type": "content.start",
                "session_id": "gm-service-action",
                "interaction_id": "gm-int-action-1",
            },
            {
                "type": "interaction.complete",
                "session_id": "gm-service-action",
                "interaction_id": "gm-int-action-1",
                "commitment_id": "gm-service-action-commit-1",
                "externally_consequential": True,
                "result_artifact_ref": "gm-service-action-artifact-1",
            },
        ],
    )

    assert result["action_tag"] == "gemini-interaction-stream"
    assert [record["raw_host_event_name"] for record in result["records"]] == [
        "content.start",
        "interaction.complete",
    ]
    assert state.session.event_index == 2
    assert state.session_loaded is True
