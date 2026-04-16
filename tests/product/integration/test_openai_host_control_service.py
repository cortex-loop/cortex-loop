"""Integration tests for the bounded outbound OpenAI host-control lane."""

from __future__ import annotations

from pathlib import Path

from cortex.hosts.openai import host_transport as openai_host_transport

from tests.product.integration._openai_service_harness import EXPECTED_RECORD_KEYS, run_openai_service


REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_DIR = REPO_ROOT / "tests" / "conformance" / "fixtures"


def test_openai_host_control_action_endpoint_returns_ordered_o1_records_and_mutates_session() -> None:
    with run_openai_service(
        env={
            openai_host_transport._FIXTURE_PATH_ENV: str(
                FIXTURE_DIR / "openai_host_control_single_call.json"
            )
        }
    ) as service:
        status_code, payload = service.request(
            "POST",
            "/v1/actions/response-stream",
            {
                "action_tag": "openai-response-stream",
                "request": {
                    "model": "gpt-5.4",
                    "input": "hello from k2",
                },
            },
        )
        export_status, exported = service.request("GET", "/v1/session/export")

    assert status_code == 200
    assert payload["action_tag"] == "openai-response-stream"
    assert [tuple(record) for record in payload["records"]] == [
        EXPECTED_RECORD_KEYS,
        EXPECTED_RECORD_KEYS,
        EXPECTED_RECORD_KEYS,
    ]
    assert [record["raw_host_event_name"] for record in payload["records"]] == [
        "response.created",
        "response.output_text.delta",
        "response.completed",
    ]
    assert [record["decision"] for record in payload["records"]] == [
        "check",
        "continue",
        "check",
    ]
    assert [record["closure_required"] for record in payload["records"]] == [
        False,
        False,
        True,
    ]
    assert export_status == 200
    assert exported["journal"]["event_index"] == 3
    assert exported["journal"]["confirmed_artifact_refs"] == ["oa-k2-artifact-1"]
    assert exported["journal"]["executive_modulator_memory"] is not None


def test_openai_host_control_action_endpoint_rejects_out_of_scope_request_keys() -> None:
    with run_openai_service() as service:
        status_code, payload = service.request(
            "POST",
            "/v1/actions/response-stream",
            {
                "action_tag": "openai-response-stream",
                "request": {
                    "model": "gpt-5.4",
                    "input": "hello from k2",
                    "tools": [{"type": "function", "name": "bad"}],
                },
            },
        )

    assert status_code == 400
    assert "strict text-only whitelist" in payload["error"]


def test_openai_host_control_action_endpoint_undocumented_raw_event_warns_conservatively() -> None:
    with run_openai_service(
        env={
            openai_host_transport._FIXTURE_PATH_ENV: str(
                FIXTURE_DIR / "openai_host_control_gap_call.json"
            )
        }
    ) as service:
        status_code, payload = service.request(
            "POST",
            "/v1/actions/response-stream",
            {
                "action_tag": "openai-response-stream",
                "request": {
                    "model": "gpt-5.4",
                    "input": "gap event",
                },
            },
        )

    assert status_code == 200
    assert payload["records"][0]["raw_host_event_name"] == "response.tool_event"
    assert payload["records"][0]["warnings"] == [
        "No documented OpenAI lifecycle mapping for 'response.tool_event'; using conservative external/observation binding."
    ]


def test_openai_host_control_action_endpoint_upstream_failure_returns_502_without_mutating_session() -> None:
    with run_openai_service(
        env={
            openai_host_transport._FIXTURE_PATH_ENV: str(
                FIXTURE_DIR / "openai_host_control_failure.json"
            )
        }
    ) as service:
        status_code, payload = service.request(
            "POST",
            "/v1/actions/response-stream",
            {
                "action_tag": "openai-response-stream",
                "request": {
                    "model": "gpt-5.4",
                    "input": "upstream failure",
                },
            },
        )
        health_status, health = service.request("GET", "/health")
        export_status, exported = service.request("GET", "/v1/session/export")

    assert status_code == 502
    assert payload == {"error": "fixture upstream unavailable"}
    assert health_status == 200
    assert health["session_loaded"] is False
    assert export_status == 200
    assert exported["journal"]["event_index"] == 0


def test_openai_host_control_action_endpoint_reports_verified_work_blocked_result() -> None:
    with run_openai_service(
        env={
            openai_host_transport._FIXTURE_PATH_ENV: str(
                FIXTURE_DIR / "openai_host_control_verified_work_blocked.json"
            )
        }
    ) as service:
        status_code, payload = service.request(
            "POST",
            "/v1/actions/response-stream",
            {
                "action_tag": "openai-response-stream",
                "request": {
                    "model": "gpt-5.4",
                    "input": "build bookmarks app",
                    "work_contract": {
                        "allowed_write_paths": [
                            "src/bookmarks_api/main.py",
                            "src/bookmarks_api/models.py",
                            "src/bookmarks_api/store.py",
                        ],
                        "verification_profile": "python_workspace_pytest_v1",
                        "output_carrier": "full_files",
                        "max_repair_turns": 0,
                    },
                },
            },
        )
        export_status, exported = service.request("GET", "/v1/session/export")

    assert status_code == 200
    assert payload["attempt_count"] == 1
    assert payload["verification"]["status"] == "blocked"
    assert payload["verification"]["failure_class"] == "blocked_missing_info"
    assert payload["verification"]["blocked_message"] == (
        "Need a retention policy for archived bookmarks."
    )
    assert export_status == 200
    assert exported["journal"]["next_recommended_move"] == "check"
    assert exported["journal"]["last_failure_class"] == "blocked_missing_info"
