"""Integration tests for raw Gemini transcript ingress CLI."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_PATH = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "gemini_ingress_cli_session.jsonl"
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


def test_gemini_ingress_cli_reads_documented_raw_transcript_fixture() -> None:
    completed = _run_gemini_ingress_cli("--event-file", str(FIXTURE_PATH))

    assert completed.returncode == 0, completed.stderr
    records = _parse_jsonl_output(completed.stdout)

    assert len(records) == 3
    assert tuple(records[0]) == EXPECTED_RECORD_KEYS
    assert [record["raw_host_event_name"] for record in records] == [
        "content.delta",
        "content.delta",
        "interaction.complete",
    ]
    assert [record["dispatch_lane"] for record in records] == [
        "cheap",
        "candidate-bearing",
        "full-commitment",
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


def test_gemini_ingress_cli_load_save_works(tmp_path: Path) -> None:
    artifact_path = tmp_path / "gemini-ingress-session.json"

    first_completed = _run_gemini_ingress_cli(
        "--save-session",
        str(artifact_path),
        input_text='{"type":"content.delta","session_id":"gm-ingress-resume","interaction_id":"gm-int-1","delta":"hello"}\n',
    )
    second_completed = _run_gemini_ingress_cli(
        "--load-session",
        str(artifact_path),
        "--save-session",
        str(artifact_path),
        input_text='{"type":"interaction.complete","session_id":"gm-ingress-resume","interaction_id":"gm-int-1","commitment_id":"gm-ingress-commit","externally_consequential":true,"result_artifact_ref":"gm-ingress-artifact"}\n',
    )

    assert first_completed.returncode == 0, first_completed.stderr
    assert second_completed.returncode == 0, second_completed.stderr
    records = _parse_jsonl_output(second_completed.stdout)
    assert records[0]["event_index"] == 2
    assert records[0]["raw_host_event_name"] == "interaction.complete"


def test_gemini_ingress_cli_rejects_canonical_event_names_wrapper_shape_and_mixed_shape() -> None:
    canonical = _run_gemini_ingress_cli(
        input_text='{"type":"external/observation","session_id":"gm-bad","interaction_id":"gm-int-1"}\n'
    )
    wrapper = _run_gemini_ingress_cli(
        input_text='{"event_name":"interaction.complete","payload":{"session_id":"gm-bad","interaction_id":"gm-int-1"}}\n'
    )
    mixed = _run_gemini_ingress_cli(
        input_text='{"type":"interaction.complete","event_name":"interaction.complete","payload":{"session_id":"gm-bad","interaction_id":"gm-int-1"},"session_id":"gm-bad","interaction_id":"gm-int-1","commitment_id":"gm-bad-commit","externally_consequential":true,"result_artifact_ref":"gm-bad-artifact"}\n'
    )

    assert canonical.returncode == 1
    assert canonical.stdout == ""
    assert "raw Gemini host event name" in canonical.stderr

    assert wrapper.returncode == 1
    assert wrapper.stdout == ""
    assert "wrapper and mixed wrapper/transcript" in wrapper.stderr

    assert mixed.returncode == 1
    assert mixed.stdout == ""
    assert "wrapper and mixed wrapper/transcript" in mixed.stderr


def test_gemini_ingress_cli_undocumented_raw_host_event_still_warns_conservatively() -> None:
    completed = _run_gemini_ingress_cli(
        input_text='{"type":"content.tool_event","session_id":"gm-gap","interaction_id":"gm-int-gap","commitment_id":"gm-gap-commit","externally_consequential":true,"result_artifact_ref":"gm-gap-artifact"}\n'
    )

    assert completed.returncode == 0, completed.stderr
    records = _parse_jsonl_output(completed.stdout)
    assert records[0]["raw_host_event_name"] == "content.tool_event"
    assert records[0]["warnings"] == [
        "No documented Gemini lifecycle mapping for 'content.tool_event'; using conservative external/observation binding."
    ]


def _run_gemini_ingress_cli(
    *args: str,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "cortex.hosts.gemini.ingress_cli", *args],
        cwd=REPO_ROOT,
        input=input_text,
        capture_output=True,
        text=True,
        check=False,
    )


def _parse_jsonl_output(stdout: str) -> list[dict[str, object]]:
    lines = [line for line in stdout.splitlines() if line.strip()]
    return [json.loads(line) for line in lines]
