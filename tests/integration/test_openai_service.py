"""Integration tests for the loopback OpenAI service shell."""

from __future__ import annotations

from pathlib import Path

from cortex.runtime.openai import OpenAIRuntimeSession
from cortex.runtime.openai_session_io import write_openai_runtime_session_artifact

from tests.integration._openai_service_harness import (
    EXPECTED_RECORD_KEYS,
    run_openai_service,
)


def test_openai_service_health_and_documented_event_flow() -> None:
    with run_openai_service() as service:
        status_code, health = service.request("GET", "/health")

        assert status_code == 200
        assert health == {
            "status": "ok",
            "runtime": "openai-service",
            "session_loaded": False,
        }

        event_status, record = service.request(
            "POST",
            "/v1/events",
            {
                "type": "response.output_text.delta",
                "session_id": "oa-service",
                "response_id": "resp-1",
                "delta": "hello",
            },
        )

        assert event_status == 200
        assert tuple(record) == EXPECTED_RECORD_KEYS
        assert record["event_index"] == 1
        assert record["raw_host_event_name"] == "response.output_text.delta"
        assert record["dispatch_lane"] == "cheap"
        assert record["decision"] == "continue"
        assert record["journal"]["event_index"] == 1

        health_status, updated_health = service.request("GET", "/health")
        assert health_status == 200
        assert updated_health["session_loaded"] is True


def test_openai_service_rejects_canonical_wrapper_and_mixed_records() -> None:
    with run_openai_service() as service:
        canonical_status, canonical_payload = service.request(
            "POST",
            "/v1/events",
            {
                "type": "external/observation",
                "session_id": "oa-bad",
                "response_id": "resp-1",
            },
        )
        wrapper_status, wrapper_payload = service.request(
            "POST",
            "/v1/events",
            {
                "event_name": "response.completed",
                "payload": {
                    "session_id": "oa-bad",
                    "response_id": "resp-1",
                },
            },
        )
        mixed_status, mixed_payload = service.request(
            "POST",
            "/v1/events",
            {
                "type": "response.completed",
                "event_name": "response.completed",
                "payload": {
                    "session_id": "oa-bad",
                    "response_id": "resp-1",
                },
                "session_id": "oa-bad",
                "response_id": "resp-1",
                "commitment_id": "oa-bad-commit",
                "externally_consequential": True,
                "result_artifact_ref": "oa-bad-artifact",
            },
        )

        assert canonical_status == 400
        assert "raw OpenAI host event name" in canonical_payload["error"]

        assert wrapper_status == 400
        assert "wrapper and mixed wrapper/transcript" in wrapper_payload["error"]

        assert mixed_status == 400
        assert "wrapper and mixed wrapper/transcript" in mixed_payload["error"]


def test_openai_service_unknown_path_and_wrong_method_return_json_errors() -> None:
    with run_openai_service() as service:
        unknown_status, unknown_payload = service.request("GET", "/v1/missing")
        method_status, method_payload = service.request("GET", "/v1/events")

        assert unknown_status == 404
        assert unknown_payload == {"error": "Unknown path: /v1/missing"}

        assert method_status == 405
        assert method_payload == {"error": "GET is not allowed for /v1/events."}


def test_openai_service_undocumented_raw_event_warns_without_fabricating_parity() -> None:
    with run_openai_service() as service:
        status_code, payload = service.request(
            "POST",
            "/v1/events",
            {
                "type": "response.tool_event",
                "session_id": "oa-gap",
                "response_id": "resp-gap",
                "commitment_id": "oa-gap-commit",
                "externally_consequential": True,
                "result_artifact_ref": "oa-gap-artifact",
            },
        )

        assert status_code == 200
        assert payload["raw_host_event_name"] == "response.tool_event"
        assert payload["native_event_name"] == "external/observation"
        assert payload["commitment_result_kind"] == "certified"
        assert payload["warnings"] == [
            "No documented OpenAI lifecycle mapping for 'response.tool_event'; using conservative external/observation binding."
        ]
        assert payload["decision"] == "check"
        assert payload["journal"]["confirmed_artifact_refs"] == ["oa-gap-artifact"]


def test_openai_service_session_export_import_and_startup_load_roundtrip(tmp_path: Path) -> None:
    with run_openai_service() as service:
        event_status, _ = service.request(
            "POST",
            "/v1/events",
            {
                "type": "response.completed",
                "session_id": "oa-export",
                "response_id": "resp-export",
                "commitment_id": "oa-export-commit",
                "externally_consequential": True,
                "result_artifact_ref": "oa-export-artifact",
            },
        )
        assert event_status == 200

        export_status, exported = service.request("GET", "/v1/session/export")
        assert export_status == 200
        assert tuple(exported) == (
            "artifact_kind",
            "artifact_version",
            "journal",
        )
        assert exported["journal"]["event_index"] == 1

    with run_openai_service() as imported_service:
        import_status, imported = imported_service.request(
            "POST",
            "/v1/session/import",
            exported,
        )
        assert import_status == 200
        assert imported == exported

        health_status, imported_health = imported_service.request("GET", "/health")
        assert health_status == 200
        assert imported_health["session_loaded"] is True

    artifact_path = tmp_path / "openai-service-session.json"
    write_openai_runtime_session_artifact(
        artifact_path,
        OpenAIRuntimeSession(
            session_id="oa-startup",
            event_index=2,
            confirmed_artifact_refs=("oa-startup-artifact",),
            next_recommended_move="check",
        ),
    )
    with run_openai_service("--load-session", str(artifact_path)) as loaded_service:
        health_status, health = loaded_service.request("GET", "/health")
        export_status, exported_loaded = loaded_service.request("GET", "/v1/session/export")

        assert health_status == 200
        assert health["session_loaded"] is True
        assert export_status == 200
        assert exported_loaded["journal"]["event_index"] == 2
