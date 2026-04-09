"""Integration tests for the Gemini documented host-event runtime CLI shell."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = (
    REPO_ROOT / "tests" / "integration" / "fixtures" / "gemini_runtime_cli_session.jsonl"
)
EXPECTED_RECORD_KEYS = (
    "event_index",
    "raw_host_event_name",
    "native_event_name",
    "dispatch_lane",
    "selected_family",
    "brake_state",
    "executive_state_summary",
    "control_ledger",
    "warnings",
    "session_summary",
    "commitment_result_kind",
    "feedback_window_summary",
)


def test_gemini_runtime_cli_reads_documented_raw_events_and_preserves_host_name() -> None:
    completed = _run_gemini_cli("--event-file", str(FIXTURE_PATH))

    assert completed.returncode == 0, completed.stderr
    records = _parse_jsonl_output(completed.stdout)

    assert len(records) == 3
    assert tuple(records[0]) == EXPECTED_RECORD_KEYS
    assert [record["event_index"] for record in records] == [1, 2, 3]
    assert [record["raw_host_event_name"] for record in records] == [
        "content.delta",
        "content.delta",
        "interaction.complete",
    ]
    assert [record["native_event_name"] for record in records] == [
        "external/observation",
        "external/observation",
        "turn/complete",
    ]
    assert [record["dispatch_lane"] for record in records] == [
        "cheap",
        "candidate-bearing",
        "full-commitment",
    ]
    assert [record["commitment_result_kind"] for record in records] == [
        None,
        None,
        "certified",
    ]
    assert tuple(records[-1]["control_ledger"]) == (
        "event_class",
        "admissible_families",
        "selected_family",
        "realized_family",
        "dominant_uncertainty_sources",
        "brake_state",
        "budget_band",
        "primary_reason",
        "allocation_diagnostics",
    )
    assert tuple(records[-1]["control_ledger"]["allocation_diagnostics"]) == (
        "alpha_t",
        "activation_threshold",
        "selected_delta_over_neutral",
        "scores",
    )


def test_gemini_runtime_cli_explicit_load_save_works(tmp_path: Path) -> None:
    artifact_path = tmp_path / "gemini-session.json"

    first_completed = _run_gemini_cli(
        "--save-session",
        str(artifact_path),
        input_text='{"event_name":"content.delta","payload":{"session_id":"gm-resume","interaction_id":"gm-int-1","delta":"hello"}}\n',
    )
    second_completed = _run_gemini_cli(
        "--load-session",
        str(artifact_path),
        "--save-session",
        str(artifact_path),
        input_text='{"event_name":"interaction.complete","payload":{"session_id":"gm-resume","interaction_id":"gm-int-1","commitment_id":"gm-commit","externally_consequential":true,"result_artifact_ref":"gm-artifact"}}\n',
    )

    assert first_completed.returncode == 0, first_completed.stderr
    assert second_completed.returncode == 0, second_completed.stderr

    records = _parse_jsonl_output(second_completed.stdout)
    assert records[0]["event_index"] == 2
    assert records[0]["raw_host_event_name"] == "interaction.complete"
    assert _parse_session_artifact(artifact_path)["continuity_truth"]["event_index"] == 2


def test_gemini_runtime_cli_rejects_canonical_cortex_event_names() -> None:
    completed = _run_gemini_cli(
        input_text='{"event_name":"external/observation","payload":{"session_id":"gm-bad","interaction_id":"resp"}}\n'
    )

    assert completed.returncode == 1
    assert completed.stdout == ""
    assert (
        completed.stderr
        == "gemini_cli error: line 1: event_name must be a raw Gemini host event name, not a canonical Cortex event name.\n"
    )


def test_gemini_runtime_cli_load_save_failure_emits_no_stdout(tmp_path: Path) -> None:
    broken_path = tmp_path / "broken.json"
    broken_path.write_text("{not-json\n", encoding="utf-8")

    load_failed = _run_gemini_cli(
        "--load-session",
        str(broken_path),
        input_text='{"event_name":"content.delta","payload":{"session_id":"gm-broken","interaction_id":"resp"}}\n',
    )
    save_failed = _run_gemini_cli(
        "--save-session",
        str(tmp_path / "missing" / "session.json"),
        input_text='{"event_name":"content.delta","payload":{"session_id":"gm-save","interaction_id":"resp"}}\n',
    )

    assert load_failed.returncode == 1
    assert load_failed.stdout == ""
    assert load_failed.stderr.startswith("gemini_cli error:")

    assert save_failed.returncode == 1
    assert save_failed.stdout == ""
    assert save_failed.stderr.startswith("gemini_cli error:")


def test_gemini_runtime_cli_undocumented_raw_host_event_warns_without_fabricating_parity() -> None:
    completed = _run_gemini_cli(
        input_text='{"event_name":"content.tool_event","payload":{"session_id":"gm-gap","interaction_id":"gm-int-gap","commitment_id":"gm-gap-commit","externally_consequential":true,"result_artifact_ref":"gm-gap-artifact"}}\n'
    )

    assert completed.returncode == 0, completed.stderr
    records = _parse_jsonl_output(completed.stdout)

    assert records[0]["raw_host_event_name"] == "content.tool_event"
    assert records[0]["native_event_name"] == "external/observation"
    assert records[0]["commitment_result_kind"] == "certified"
    assert records[0]["warnings"] == [
        "No documented Gemini lifecycle mapping for 'content.tool_event'; using conservative external/observation binding."
    ]


def _run_gemini_cli(*args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "experimental.runtime.gemini_cli", *args],
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
