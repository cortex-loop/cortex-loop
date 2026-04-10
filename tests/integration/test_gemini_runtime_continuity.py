"""Integration tests for Gemini runtime continuity over documented host events."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = (
    REPO_ROOT
    / "tests"
    / "integration"
    / "fixtures"
    / "gemini_runtime_continuity_session.jsonl"
)


def test_gemini_runtime_split_session_is_g1_equivalent_to_uninterrupted_run(tmp_path: Path) -> None:
    one_process_artifact = tmp_path / "one-process.json"
    split_seed_artifact = tmp_path / "split-seed.json"
    split_final_artifact = tmp_path / "split-final.json"
    fixture_lines = FIXTURE_PATH.read_text(encoding="utf-8").splitlines()

    one_process_completed = _run_gemini_cli(
        "--event-file",
        str(FIXTURE_PATH),
        "--save-session",
        str(one_process_artifact),
    )
    split_first_completed = _run_gemini_cli(
        "--save-session",
        str(split_seed_artifact),
        input_text="\n".join(fixture_lines[:2]) + "\n",
    )
    split_second_completed = _run_gemini_cli(
        "--load-session",
        str(split_seed_artifact),
        "--save-session",
        str(split_final_artifact),
        input_text="\n".join(fixture_lines[2:]) + "\n",
    )

    assert one_process_completed.returncode == 0, one_process_completed.stderr
    assert split_first_completed.returncode == 0, split_first_completed.stderr
    assert split_second_completed.returncode == 0, split_second_completed.stderr

    one_process_records = _parse_jsonl_output(one_process_completed.stdout)
    split_records = _parse_jsonl_output(split_first_completed.stdout) + _parse_jsonl_output(
        split_second_completed.stdout
    )

    _assert_g1_equivalent(
        one_process_records,
        split_records,
        _parse_session_artifact(one_process_artifact),
        _parse_session_artifact(split_final_artifact),
    )
    assert (
        one_process_records[-1]["session_summary"]["budget_history"]
        != split_records[-1]["session_summary"]["budget_history"]
    )
    assert (
        one_process_records[-1]["session_summary"]["brake_history"]
        != split_records[-1]["session_summary"]["brake_history"]
    )


def test_gemini_runtime_continuity_rejection_survives_restart(tmp_path: Path) -> None:
    artifact_path = tmp_path / "session.json"

    first_completed = _run_gemini_cli(
        "--save-session",
        str(artifact_path),
        input_text='{"event_name":"content.delta","payload":{"session_id":"gm-reject","interaction_id":"gm-int-1","branch_operation":"open","branch_track_ref":"branch-alpha","delta":"open"}}\n',
    )
    second_completed = _run_gemini_cli(
        "--load-session",
        str(artifact_path),
        input_text='{"event_name":"content.delta","payload":{"session_id":"gm-reject","interaction_id":"gm-int-1","branch_operation":"resume","branch_track_ref":"branch-alpha","delta":"resume"}}\n',
    )

    assert first_completed.returncode == 0, first_completed.stderr
    assert second_completed.returncode == 0, second_completed.stderr

    records = _parse_jsonl_output(second_completed.stdout)
    assert records[-1]["warnings"] == [
        "continuity-rejected:missing-resume-anchor:branch-alpha"
    ]
    assert records[-1]["session_summary"]["branch_registry"] == ["main", "branch-alpha"]
    assert records[-1]["session_summary"]["active_track_ref"] == "branch-alpha"


def test_gemini_runtime_host_warning_and_certified_commitment_can_coexist_across_restart(
    tmp_path: Path,
) -> None:
    artifact_path = tmp_path / "session.json"

    first_completed = _run_gemini_cli(
        "--save-session",
        str(artifact_path),
        input_text='{"event_name":"content.delta","payload":{"session_id":"gm-host-warning","interaction_id":"gm-int-1","delta":"seed"}}\n',
    )
    second_completed = _run_gemini_cli(
        "--load-session",
        str(artifact_path),
        input_text='{"event_name":"content.tool_event","payload":{"session_id":"gm-host-warning","interaction_id":"gm-int-1","commitment_id":"gm-host-warning-commit","externally_consequential":true,"result_artifact_ref":"gm-host-warning-artifact"}}\n',
    )

    assert first_completed.returncode == 0, first_completed.stderr
    assert second_completed.returncode == 0, second_completed.stderr

    records = _parse_jsonl_output(second_completed.stdout)
    assert records[-1]["warnings"] == [
        "No documented Gemini lifecycle mapping for 'content.tool_event'; using conservative external/observation binding."
    ]
    assert records[-1]["commitment_result_kind"] == "certified"


def _run_gemini_cli(*args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "cortex.hosts.gemini.cli", *args],
        cwd=REPO_ROOT,
        input=input_text,
        capture_output=True,
        text=True,
        check=False,
    )


def _parse_jsonl_output(stdout: str) -> list[dict[str, object]]:
    lines = [line for line in stdout.splitlines() if line.strip()]
    return [json.loads(line) for line in lines]


def _parse_session_artifact(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _assert_g1_equivalent(
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
