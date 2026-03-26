"""Unit tests for the loopback OpenAI service shell."""

from __future__ import annotations

from cortex.runtime.openai import OpenAIRuntimeSession
from cortex.runtime.openai_service import (
    OpenAIServiceState,
    build_openai_service_server,
    export_openai_service_session,
    handle_openai_service_action,
    handle_openai_service_request,
    import_openai_service_session,
)


def test_openai_service_state_constructs_cleanly() -> None:
    state = OpenAIServiceState()

    assert isinstance(state.session, OpenAIRuntimeSession)
    assert state.session.event_index == 0
    assert state.session_loaded is False


def test_openai_service_import_export_preserves_exact_artifact_shape() -> None:
    state = OpenAIServiceState()
    state.replace_session(
        OpenAIRuntimeSession(
            session_id="oa-service",
            event_index=2,
            budget_history=("shell-low", "shell-medium"),
        ),
        session_loaded=True,
    )

    exported = export_openai_service_session(state)
    imported = import_openai_service_session(exported, OpenAIServiceState())

    assert tuple(exported) == (
        "artifact_kind",
        "artifact_version",
        "continuity_truth",
        "control_residue",
    )
    assert imported == exported


def test_openai_service_server_binds_loopback_only() -> None:
    server = build_openai_service_server(0)
    try:
        assert server.server_address[0] == "127.0.0.1"
    finally:
        server.server_close()


def test_openai_service_invalid_import_becomes_400_error_payload() -> None:
    status_code, payload = handle_openai_service_request(
        "POST",
        "/v1/session/import",
        OpenAIServiceState(),
        b'{"artifact_kind":"bad","artifact_version":1,"continuity_truth":{},"control_residue":{}}',
    )

    assert status_code == 400
    assert payload["error"].startswith("OpenAIRuntimeSessionArtifact.artifact_kind")


def test_openai_service_action_roundtrips_records_with_fake_transport() -> None:
    payload = {
        "action_tag": "openai-response-stream",
        "request": {
            "model": "gpt-5",
            "input": "hello",
        },
    }
    state = OpenAIServiceState()

    result = handle_openai_service_action(
        payload,
        state,
        outbound_transport=lambda _: [
            {
                "type": "response.created",
                "session_id": "oa-service-action",
                "response_id": "resp-action-1",
            },
            {
                "type": "response.completed",
                "session_id": "oa-service-action",
                "response_id": "resp-action-1",
                "commitment_id": "oa-service-action-commit-1",
                "externally_consequential": True,
                "result_artifact_ref": "oa-service-action-artifact-1",
            },
        ],
    )

    assert result["action_tag"] == "openai-response-stream"
    assert [record["raw_host_event_name"] for record in result["records"]] == [
        "response.created",
        "response.completed",
    ]
    assert state.session.event_index == 2
    assert state.session_loaded is True
