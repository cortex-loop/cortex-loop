"""Integration tests for raw OpenAI transcript ingress CLI."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_PATH = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "openai_ingress_cli_session.jsonl"
)
EXPECTED_RECORD_KEYS = (
    "event_index",
    "raw_host_event_name",
    "native_event_name",
    "dispatch_lane",
    "decision",
    "warnings",
    "journal",
    "executive_state",
    "selected_family",
    "realized_family",
    "brake_state",
    "control_ledger",
    "feedback_window_summary",
    "commitment_result_kind",
)


def test_openai_ingress_cli_reads_documented_raw_transcript_fixture() -> None:
    completed = _run_openai_ingress_cli("--event-file", str(FIXTURE_PATH))

    assert completed.returncode == 0, completed.stderr
    records = _parse_jsonl_output(completed.stdout)

    assert len(records) == 3
    assert tuple(records[0]) == EXPECTED_RECORD_KEYS
    assert [record["raw_host_event_name"] for record in records] == [
        "response.output_text.delta",
        "response.output_text.delta",
        "response.completed",
    ]
    assert [record["dispatch_lane"] for record in records] == [
        "cheap",
        "candidate-bearing",
        "full-commitment",
    ]
    assert [record["decision"] for record in records] == ["check", "check", "check"]
    assert records[0]["selected_family"] == "seek-context"
    assert records[0]["realized_family"] == "seek-context"
    assert records[0]["brake_state"] == "guarded"
    assert records[-1]["journal"]["confirmed_artifact_refs"] == ["oa-ingress-artifact-1"]


def test_openai_ingress_cli_load_save_works(tmp_path: Path) -> None:
    artifact_path = tmp_path / "openai-ingress-session.json"

    first_completed = _run_openai_ingress_cli(
        "--save-session",
        str(artifact_path),
        input_text='{"type":"response.output_text.delta","session_id":"oa-ingress-resume","response_id":"resp-1","delta":"hello"}\n',
    )
    second_completed = _run_openai_ingress_cli(
        "--load-session",
        str(artifact_path),
        "--save-session",
        str(artifact_path),
        input_text='{"type":"response.completed","session_id":"oa-ingress-resume","response_id":"resp-1","commitment_id":"oa-ingress-commit","externally_consequential":true,"result_artifact_ref":"oa-ingress-artifact"}\n',
    )

    assert first_completed.returncode == 0, first_completed.stderr
    assert second_completed.returncode == 0, second_completed.stderr
    records = _parse_jsonl_output(second_completed.stdout)
    assert records[0]["event_index"] == 2
    assert records[0]["raw_host_event_name"] == "response.completed"


def test_openai_ingress_cli_rejects_canonical_event_names_wrapper_shape_and_mixed_shape() -> None:
    canonical = _run_openai_ingress_cli(
        input_text='{"type":"external/observation","session_id":"oa-bad","response_id":"resp-1"}\n'
    )
    wrapper = _run_openai_ingress_cli(
        input_text='{"event_name":"response.completed","payload":{"session_id":"oa-bad","response_id":"resp-1"}}\n'
    )
    mixed = _run_openai_ingress_cli(
        input_text='{"type":"response.completed","event_name":"response.completed","payload":{"session_id":"oa-bad","response_id":"resp-1"},"session_id":"oa-bad","response_id":"resp-1","commitment_id":"oa-bad-commit","externally_consequential":true,"result_artifact_ref":"oa-bad-artifact"}\n'
    )

    assert canonical.returncode == 1
    assert canonical.stdout == ""
    assert "raw OpenAI host event name" in canonical.stderr

    assert wrapper.returncode == 1
    assert wrapper.stdout == ""
    assert "wrapper and mixed wrapper/transcript" in wrapper.stderr

    assert mixed.returncode == 1
    assert mixed.stdout == ""
    assert "wrapper and mixed wrapper/transcript" in mixed.stderr


def test_openai_ingress_cli_undocumented_raw_host_event_still_warns_conservatively() -> None:
    completed = _run_openai_ingress_cli(
        input_text='{"type":"response.tool_event","session_id":"oa-gap","response_id":"resp-gap","commitment_id":"oa-gap-commit","externally_consequential":true,"result_artifact_ref":"oa-gap-artifact"}\n'
    )

    assert completed.returncode == 0, completed.stderr
    records = _parse_jsonl_output(completed.stdout)
    assert records[0]["raw_host_event_name"] == "response.tool_event"
    assert records[0]["warnings"] == [
        "No documented OpenAI lifecycle mapping for 'response.tool_event'; using conservative external/observation binding."
    ]


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


def _parse_jsonl_output(stdout: str) -> list[dict[str, object]]:
    lines = [line for line in stdout.splitlines() if line.strip()]
    return [json.loads(line) for line in lines]
