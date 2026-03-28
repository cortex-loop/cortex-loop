"""Integration tests for Claude service continuity over loopback HTTP."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tests.integration._claude_service_harness import run_claude_service


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = (
    REPO_ROOT
    / "tests"
    / "integration"
    / "fixtures"
    / "claude_ingress_continuity_session.jsonl"
)


def test_claude_service_event_sequence_is_g3_equivalent_to_g2_ingress_shell(
    tmp_path: Path,
) -> None:
    g2_artifact = tmp_path / "g2-ingress.json"
    g2_completed = _run_claude_ingress_cli(
        "--event-file",
        str(FIXTURE_PATH),
        "--save-session",
        str(g2_artifact),
    )

    assert g2_completed.returncode == 0, g2_completed.stderr
    g2_records = _parse_jsonl_output(g2_completed.stdout)
    g2_artifact_payload = _parse_session_artifact(g2_artifact)

    with run_claude_service() as service:
        service_records = [
            service.request("POST", "/v1/events", record)[1]
            for record in _read_fixture_records()
        ]
        export_status, exported = service.request("GET", "/v1/session/export")

    assert export_status == 200
    _assert_g3_equivalent(g2_records, service_records, g2_artifact_payload, exported)


def test_claude_service_export_import_preserves_g3_equivalence_and_keeps_diagnostics_non_equivalent(
    tmp_path: Path,
) -> None:
    uninterrupted_artifact = tmp_path / "uninterrupted.json"
    g2_completed = _run_claude_ingress_cli(
        "--event-file",
        str(FIXTURE_PATH),
        "--save-session",
        str(uninterrupted_artifact),
    )

    assert g2_completed.returncode == 0, g2_completed.stderr
    uninterrupted_records = _parse_jsonl_output(g2_completed.stdout)
    uninterrupted_artifact_payload = _parse_session_artifact(uninterrupted_artifact)
    fixture_records = _read_fixture_records()

    with run_claude_service() as first_service:
        first_records = [
            first_service.request("POST", "/v1/events", record)[1]
            for record in fixture_records[:2]
        ]
        export_status, exported_seed = first_service.request("GET", "/v1/session/export")

    assert export_status == 200

    with run_claude_service() as second_service:
        import_status, imported = second_service.request(
            "POST",
            "/v1/session/import",
            exported_seed,
        )
        assert import_status == 200
        split_records = first_records + [
            second_service.request("POST", "/v1/events", record)[1]
            for record in fixture_records[2:]
        ]
        final_export_status, split_artifact = second_service.request(
            "GET",
            "/v1/session/export",
        )

    assert imported == exported_seed
    assert final_export_status == 200
    _assert_g3_equivalent(
        uninterrupted_records,
        split_records,
        uninterrupted_artifact_payload,
        split_artifact,
    )
    assert (
        uninterrupted_records[-1]["session_summary"]["budget_history"]
        != split_records[-1]["session_summary"]["budget_history"]
    )
    assert (
        uninterrupted_records[-1]["session_summary"]["brake_history"]
        != split_records[-1]["session_summary"]["brake_history"]
    )


def _run_claude_ingress_cli(
    *args: str,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "cortex.runtime.claude_ingress_cli", *args],
        cwd=REPO_ROOT,
        input=input_text,
        capture_output=True,
        text=True,
        check=False,
    )


def _read_fixture_records() -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in FIXTURE_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _parse_jsonl_output(stdout: str) -> list[dict[str, object]]:
    lines = [line for line in stdout.splitlines() if line.strip()]
    return [json.loads(line) for line in lines]


def _parse_session_artifact(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _assert_g3_equivalent(
    expected_records: list[dict[str, object]],
    actual_records: list[dict[str, object]],
    expected_artifact: dict[str, object],
    actual_artifact: dict[str, object],
) -> None:
    assert [
        {
            "selected_family": record["selected_family"],
            "realized_family": record["control_ledger"]["realized_family"],
            "warnings": record["warnings"],
            "commitment_result_kind": record["commitment_result_kind"],
            "feedback_window_summary": record["feedback_window_summary"],
        }
        for record in actual_records
    ] == [
        {
            "selected_family": record["selected_family"],
            "realized_family": record["control_ledger"]["realized_family"],
            "warnings": record["warnings"],
            "commitment_result_kind": record["commitment_result_kind"],
            "feedback_window_summary": record["feedback_window_summary"],
        }
        for record in expected_records
    ]
    assert actual_artifact == expected_artifact
