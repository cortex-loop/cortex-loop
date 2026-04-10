"""Integration tests for the loopback Gemini service shell."""

from __future__ import annotations

from pathlib import Path

from cortex.hosts.gemini.runtime import GeminiRuntimeSession
from cortex.hosts.gemini.session_io import write_gemini_runtime_session_artifact

from tests.integration._gemini_service_harness import (
    EXPECTED_RECORD_KEYS,
    run_gemini_service,
)


def test_gemini_service_health_and_documented_event_flow() -> None:
    with run_gemini_service() as service:
        status_code, health = service.request("GET", "/health")

        assert status_code == 200
        assert health == {
            "status": "ok",
            "runtime": "gemini-service",
            "session_loaded": False,
        }

        event_status, record = service.request(
            "POST",
            "/v1/events",
            {
                "type": "content.delta",
                "session_id": "gm-service",
                "interaction_id": "gm-int-1",
                "delta": "hello",
            },
        )

        assert event_status == 200
        assert tuple(record) == EXPECTED_RECORD_KEYS
        assert record["event_index"] == 1
        assert record["raw_host_event_name"] == "content.delta"
        assert record["dispatch_lane"] == "cheap"
        assert tuple(record["control_ledger"]["allocation_diagnostics"]) == (
            "alpha_t",
            "activation_threshold",
            "selected_delta_over_neutral",
            "scores",
        )

        health_status, updated_health = service.request("GET", "/health")
        assert health_status == 200
        assert updated_health["session_loaded"] is True


def test_gemini_service_rejects_canonical_wrapper_and_mixed_records() -> None:
    with run_gemini_service() as service:
        canonical_status, canonical_payload = service.request(
            "POST",
            "/v1/events",
            {
                "type": "external/observation",
                "session_id": "gm-bad",
                "interaction_id": "gm-int-1",
            },
        )
        wrapper_status, wrapper_payload = service.request(
            "POST",
            "/v1/events",
            {
                "event_name": "interaction.complete",
                "payload": {
                    "session_id": "gm-bad",
                    "interaction_id": "gm-int-1",
                },
            },
        )
        mixed_status, mixed_payload = service.request(
            "POST",
            "/v1/events",
            {
                "type": "interaction.complete",
                "event_name": "interaction.complete",
                "payload": {
                    "session_id": "gm-bad",
                    "interaction_id": "gm-int-1",
                },
                "session_id": "gm-bad",
                "interaction_id": "gm-int-1",
                "commitment_id": "gm-bad-commit",
                "externally_consequential": True,
                "result_artifact_ref": "gm-bad-artifact",
            },
        )

        assert canonical_status == 400
        assert "raw Gemini host event name" in canonical_payload["error"]

        assert wrapper_status == 400
        assert "wrapper and mixed wrapper/transcript" in wrapper_payload["error"]

        assert mixed_status == 400
        assert "wrapper and mixed wrapper/transcript" in mixed_payload["error"]


def test_gemini_service_unknown_path_and_wrong_method_return_json_errors() -> None:
    with run_gemini_service() as service:
        unknown_status, unknown_payload = service.request("GET", "/v1/missing")
        method_status, method_payload = service.request("GET", "/v1/events")

        assert unknown_status == 404
        assert unknown_payload == {"error": "Unknown path: /v1/missing"}

        assert method_status == 405
        assert method_payload == {"error": "GET is not allowed for /v1/events."}


def test_gemini_service_undocumented_raw_event_warns_without_fabricating_parity() -> None:
    with run_gemini_service() as service:
        status_code, payload = service.request(
            "POST",
            "/v1/events",
            {
                "type": "content.tool_event",
                "session_id": "gm-gap",
                "interaction_id": "gm-int-gap",
                "commitment_id": "gm-gap-commit",
                "externally_consequential": True,
                "result_artifact_ref": "gm-gap-artifact",
            },
        )

        assert status_code == 200
        assert payload["raw_host_event_name"] == "content.tool_event"
        assert payload["native_event_name"] == "external/observation"
        assert payload["commitment_result_kind"] == "certified"
        assert payload["warnings"] == [
            "No documented Gemini lifecycle mapping for 'content.tool_event'; using conservative external/observation binding."
        ]
        assert tuple(payload["control_ledger"]["allocation_diagnostics"]) == (
            "alpha_t",
            "activation_threshold",
            "selected_delta_over_neutral",
            "scores",
        )


def test_gemini_service_session_export_import_and_startup_load_roundtrip(tmp_path: Path) -> None:
    with run_gemini_service() as service:
        event_status, _ = service.request(
            "POST",
            "/v1/events",
            {
                "type": "interaction.complete",
                "session_id": "gm-export",
                "interaction_id": "gm-int-export",
                "commitment_id": "gm-export-commit",
                "externally_consequential": True,
                "result_artifact_ref": "gm-export-artifact",
            },
        )
        assert event_status == 200

        export_status, exported = service.request("GET", "/v1/session/export")
        assert export_status == 200
        assert tuple(exported) == (
            "artifact_kind",
            "artifact_version",
            "continuity_truth",
            "control_residue",
        )
        assert exported["continuity_truth"]["event_index"] == 1

    with run_gemini_service() as imported_service:
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

    artifact_path = tmp_path / "gemini-service-session.json"
    write_gemini_runtime_session_artifact(
        artifact_path,
        GeminiRuntimeSession(
            session_id="gm-startup",
            event_index=2,
            budget_history=("shell-low", "shell-medium"),
        ),
    )
    with run_gemini_service("--load-session", str(artifact_path)) as loaded_service:
        health_status, health = loaded_service.request("GET", "/health")
        export_status, exported_loaded = loaded_service.request("GET", "/v1/session/export")

        assert health_status == 200
        assert health["session_loaded"] is True
        assert export_status == 200
        assert exported_loaded["continuity_truth"]["event_index"] == 2
