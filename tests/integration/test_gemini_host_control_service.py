"""Integration tests for the bounded outbound Gemini host-control lane."""

from __future__ import annotations

from pathlib import Path

from experimental.runtime import gemini_host_transport

from tests.integration._gemini_service_harness import EXPECTED_RECORD_KEYS, run_gemini_service


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = REPO_ROOT / "tests" / "integration" / "fixtures"


def test_gemini_host_control_action_endpoint_returns_ordered_g1_records_and_mutates_session() -> None:
    with run_gemini_service(
        env={
            gemini_host_transport._FIXTURE_PATH_ENV: str(
                FIXTURE_DIR / "gemini_host_control_single_call.json"
            )
        }
    ) as service:
        status_code, payload = service.request(
            "POST",
            "/v1/actions/interaction-stream",
            {
                "action_tag": "gemini-interaction-stream",
                "request": {
                    "model": "gemini-2.5-pro",
                    "input": "hello from g1",
                },
            },
        )
        export_status, exported = service.request("GET", "/v1/session/export")

    assert status_code == 200
    assert payload["action_tag"] == "gemini-interaction-stream"
    assert [tuple(record) for record in payload["records"]] == [
        EXPECTED_RECORD_KEYS,
        EXPECTED_RECORD_KEYS,
        EXPECTED_RECORD_KEYS,
    ]
    assert [record["raw_host_event_name"] for record in payload["records"]] == [
        "content.start",
        "content.delta",
        "interaction.complete",
    ]
    assert tuple(payload["records"][-1]["control_ledger"]["allocation_diagnostics"]) == (
        "alpha_t",
        "activation_threshold",
        "selected_delta_over_neutral",
        "scores",
    )
    assert export_status == 200
    assert exported["continuity_truth"]["event_index"] == 3


def test_gemini_host_control_action_endpoint_rejects_out_of_scope_request_keys() -> None:
    with run_gemini_service() as service:
        status_code, payload = service.request(
            "POST",
            "/v1/actions/interaction-stream",
            {
                "action_tag": "gemini-interaction-stream",
                "request": {
                    "model": "gemini-2.5-pro",
                    "input": "hello from g1",
                    "tools": [{"type": "function", "name": "bad"}],
                },
            },
        )

    assert status_code == 400
    assert "strict text-only whitelist" in payload["error"]


def test_gemini_host_control_action_endpoint_undocumented_raw_event_warns_conservatively() -> None:
    with run_gemini_service(
        env={
            gemini_host_transport._FIXTURE_PATH_ENV: str(
                FIXTURE_DIR / "gemini_host_control_gap_call.json"
            )
        }
    ) as service:
        status_code, payload = service.request(
            "POST",
            "/v1/actions/interaction-stream",
            {
                "action_tag": "gemini-interaction-stream",
                "request": {
                    "model": "gemini-2.5-pro",
                    "input": "gap event",
                },
            },
        )

    assert status_code == 200
    assert payload["records"][0]["raw_host_event_name"] == "content.tool_event"
    assert payload["records"][0]["warnings"] == [
        "No documented Gemini lifecycle mapping for 'content.tool_event'; using conservative external/observation binding."
    ]


def test_gemini_host_control_action_endpoint_upstream_failure_returns_502_without_mutating_session() -> None:
    with run_gemini_service(
        env={
            gemini_host_transport._FIXTURE_PATH_ENV: str(
                FIXTURE_DIR / "gemini_host_control_failure.json"
            )
        }
    ) as service:
        status_code, payload = service.request(
            "POST",
            "/v1/actions/interaction-stream",
            {
                "action_tag": "gemini-interaction-stream",
                "request": {
                    "model": "gemini-2.5-pro",
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
    assert exported["continuity_truth"]["event_index"] == 0
