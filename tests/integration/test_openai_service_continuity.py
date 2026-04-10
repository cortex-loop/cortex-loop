"""Integration tests for OpenAI service continuity over loopback HTTP."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tests.integration._openai_service_harness import run_openai_service


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = (
    REPO_ROOT
    / "tests"
    / "integration"
    / "fixtures"
    / "openai_ingress_continuity_session.jsonl"
)


def test_openai_service_event_sequence_is_o3_equivalent_to_o2_ingress_shell(
    tmp_path: Path,
) -> None:
    o2_artifact = tmp_path / "o2-ingress.json"
    o2_completed = _run_openai_ingress_cli(
        "--event-file",
        str(FIXTURE_PATH),
        "--save-session",
        str(o2_artifact),
    )

    assert o2_completed.returncode == 0, o2_completed.stderr
    o2_records = _parse_jsonl_output(o2_completed.stdout)
    o2_artifact_payload = _parse_session_artifact(o2_artifact)

    with run_openai_service() as service:
        service_records = [
            service.request("POST", "/v1/events", record)[1]
            for record in _read_fixture_records()
        ]
        export_status, exported = service.request("GET", "/v1/session/export")

    assert export_status == 200
    _assert_o3_equivalent(o2_records, service_records, o2_artifact_payload, exported)


def test_openai_service_export_import_preserves_o3_equivalence_and_keeps_diagnostics_non_equivalent(
    tmp_path: Path,
) -> None:
    uninterrupted_artifact = tmp_path / "uninterrupted.json"
    o2_completed = _run_openai_ingress_cli(
        "--event-file",
        str(FIXTURE_PATH),
        "--save-session",
        str(uninterrupted_artifact),
    )

    assert o2_completed.returncode == 0, o2_completed.stderr
    uninterrupted_records = _parse_jsonl_output(o2_completed.stdout)
    uninterrupted_artifact_payload = _parse_session_artifact(uninterrupted_artifact)
    fixture_records = _read_fixture_records()

    with run_openai_service() as first_service:
        first_records = [
            first_service.request("POST", "/v1/events", record)[1]
            for record in fixture_records[:2]
        ]
        export_status, exported_seed = first_service.request("GET", "/v1/session/export")

    assert export_status == 200

    with run_openai_service() as second_service:
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
    _assert_o3_equivalent(
        uninterrupted_records,
        split_records,
        uninterrupted_artifact_payload,
        split_artifact,
    )
    assert "budget_history" not in uninterrupted_records[-1]["journal"]
    assert "brake_history" not in uninterrupted_records[-1]["journal"]


def _run_openai_ingress_cli(
    *args: str,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "cortex.hosts.openai.ingress_cli", *args],
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


def _assert_o3_equivalent(
    expected_records: list[dict[str, object]],
    actual_records: list[dict[str, object]],
    expected_artifact: dict[str, object],
    actual_artifact: dict[str, object],
) -> None:
    assert [
        {
            "decision": record["decision"],
            "warnings": record["warnings"],
            "commitment_result_kind": record["commitment_result_kind"],
            "journal": record["journal"],
        }
        for record in actual_records
    ] == [
        {
            "decision": record["decision"],
            "warnings": record["warnings"],
            "commitment_result_kind": record["commitment_result_kind"],
            "journal": record["journal"],
        }
        for record in expected_records
    ]
    assert actual_artifact == expected_artifact
