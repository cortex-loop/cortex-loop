"""Integration tests for one-process reference runtime continuity."""

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
    / "reference_runtime_continuity_session.jsonl"
)


def test_reference_runtime_cli_preserves_open_suspend_resume_merge_continuity_in_one_session() -> None:
    completed = _run_reference_cli("--event-file", str(FIXTURE_PATH))

    assert completed.returncode == 0, completed.stderr
    assert completed.stderr == ""

    records = _parse_jsonl_output(completed.stdout)

    assert len(records) == 4
    assert [record["event_index"] for record in records] == [1, 2, 3, 4]
    assert [record["selected_family"] for record in records] == [
        "brake",
        "brake",
        "brake",
        "neutral",
    ]
    assert [record["brake_state"] for record in records] == [
        "guarded",
        "guarded",
        "guarded",
        "quiescent",
    ]
    assert [record["session_summary"]["branch_registry"] for record in records] == [
        ["main", "branch-alpha"],
        ["main", "branch-alpha"],
        ["main", "branch-alpha"],
        ["main"],
    ]
    assert [record["session_summary"]["active_track_ref"] for record in records] == [
        "branch-alpha",
        "main",
        "branch-alpha",
        "main",
    ]
    assert [record["session_summary"]["pending_goal_refs"] for record in records] == [
        [],
        ["branch-alpha"],
        [],
        [],
    ]
    assert [record["executive_state_summary"]["active_track_ref"] for record in records] == [
        "branch-alpha",
        "main",
        "branch-alpha",
        "main",
    ]
    assert [record["executive_state_summary"]["pending_goal_refs"] for record in records] == [
        [],
        ["branch-alpha"],
        [],
        [],
    ]
    assert records[-1]["commitment_result_kind"] == "certified"
    assert records[-1]["session_summary"]["budget_history"] == [
        "shell-low",
        "shell-medium",
        "shell-low",
        "shell-high",
    ]


def _run_reference_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "cortex.runtime.reference_cli", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def _parse_jsonl_output(stdout: str) -> list[dict[str, object]]:
    lines = [line for line in stdout.splitlines() if line.strip()]
    return [json.loads(line) for line in lines]
