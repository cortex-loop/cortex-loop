"""Integration tests for outbound Gemini host-control continuity."""

from __future__ import annotations

from pathlib import Path

from cortex.hosts.gemini import host_transport as gemini_host_transport

from tests.conformance.integration._gemini_service_harness import run_gemini_service


REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_DIR = REPO_ROOT / "tests" / "conformance" / "fixtures"
CONTINUITY_FIXTURE_PATH = FIXTURE_DIR / "gemini_host_control_continuity.json"


def test_gemini_host_control_export_import_preserves_control_truth() -> None:
    uninterrupted_records, uninterrupted_artifact = _run_uninterrupted()
    split_records, split_artifact = _run_split()

    assert _project_records(split_records) == _project_records(uninterrupted_records)
    assert split_artifact == uninterrupted_artifact
    assert "allocation_diagnostics" not in split_artifact["continuity_truth"]
    assert "allocation_diagnostics" not in split_artifact["control_residue"]


def _run_uninterrupted() -> tuple[list[dict[str, object]], dict[str, object]]:
    env = {
        gemini_host_transport._FIXTURE_PATH_ENV: str(CONTINUITY_FIXTURE_PATH),
    }
    with run_gemini_service(env=env) as service:
        first_status, first_payload = service.request(
            "POST",
            "/v1/actions/interaction-stream",
            _action_payload("first step"),
        )
        second_status, second_payload = service.request(
            "POST",
            "/v1/actions/interaction-stream",
            _action_payload("second step"),
        )
        export_status, exported = service.request("GET", "/v1/session/export")

    assert first_status == 200
    assert second_status == 200
    assert export_status == 200
    return first_payload["records"] + second_payload["records"], exported


def _run_split() -> tuple[list[dict[str, object]], dict[str, object]]:
    first_env = {
        gemini_host_transport._FIXTURE_PATH_ENV: str(CONTINUITY_FIXTURE_PATH),
        gemini_host_transport._FIXTURE_START_INDEX_ENV: "0",
    }
    with run_gemini_service(env=first_env) as first_service:
        first_status, first_payload = first_service.request(
            "POST",
            "/v1/actions/interaction-stream",
            _action_payload("first step"),
        )
        export_status, exported_seed = first_service.request("GET", "/v1/session/export")

    assert first_status == 200
    assert export_status == 200

    second_env = {
        gemini_host_transport._FIXTURE_PATH_ENV: str(CONTINUITY_FIXTURE_PATH),
        gemini_host_transport._FIXTURE_START_INDEX_ENV: "1",
    }
    with run_gemini_service(env=second_env) as second_service:
        import_status, _ = second_service.request(
            "POST",
            "/v1/session/import",
            exported_seed,
        )
        second_status, second_payload = second_service.request(
            "POST",
            "/v1/actions/interaction-stream",
            _action_payload("second step"),
        )
        final_export_status, split_exported = second_service.request(
            "GET",
            "/v1/session/export",
        )

    assert import_status == 200
    assert second_status == 200
    assert final_export_status == 200
    return first_payload["records"] + second_payload["records"], split_exported


def _action_payload(input_text: str) -> dict[str, object]:
    return {
        "action_tag": "gemini-interaction-stream",
        "request": {
            "model": "gemini-2.5-pro",
            "input": input_text,
        },
    }


def _project_records(records: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "selected_family": record["selected_family"],
            "realized_family": record["control_ledger"]["realized_family"],
            "warnings": record["warnings"],
            "commitment_result_kind": record["commitment_result_kind"],
            "feedback_window_summary": record["feedback_window_summary"],
            "allocation_diagnostics": record["control_ledger"]["allocation_diagnostics"],
        }
        for record in records
    ]
