"""Integration tests for the OpenAI documented host-event runtime CLI shell."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from cortex.aux.publication import (
    OfflineSupportPublication,
    offline_support_publication_as_payload,
)
from cortex.core.envelopes import MetadataField
from cortex.hosts.openai.runtime import run_openai_runtime_step
from tests.experimental._aux_test_support import make_support_ref

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_PATH = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "openai_runtime_cli_session.jsonl"
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
    "executive_signal_summary",
    "executive_modulator_state",
    "executive_policy_view",
    "operator_route",
    "closure_required",
    "closure_reason_tags",
    "commitment_result_kind",
)


def test_openai_runtime_cli_reads_documented_raw_events_and_preserves_host_name() -> None:
    completed = _run_openai_cli("--event-file", str(FIXTURE_PATH))

    assert completed.returncode == 0, completed.stderr
    records = _parse_jsonl_output(completed.stdout)

    assert len(records) == 3
    assert tuple(records[0]) == EXPECTED_RECORD_KEYS
    assert [record["event_index"] for record in records] == [1, 2, 3]
    assert [record["raw_host_event_name"] for record in records] == [
        "response.output_text.delta",
        "response.output_text.delta",
        "response.completed",
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
    assert [record["decision"] for record in records] == [
        "check",
        "check",
        "check",
    ]
    assert [record["commitment_result_kind"] for record in records] == [
        None,
        None,
        "certified",
    ]
    assert records[0]["executive_state"]["active_track_ref"] == "main"
    assert records[0]["selected_family"] == "seek-context"
    assert records[0]["realized_family"] == "seek-context"
    assert records[0]["brake_state"] == "guarded"
    assert records[0]["control_ledger"]["budget_band"] == "low"
    assert records[0]["feedback_window_summary"]["window_size"] == 1
    assert records[0]["feedback_window_summary"]["recent_evidence_progress_class"] == (
        "token-stream"
    )
    assert records[0]["feedback_window_summary"]["recent_continuity_progress_class"] == (
        "none"
    )
    assert records[0]["executive_signal_summary"]["quota_pressure"] == 0.25
    assert records[0]["executive_modulator_state"]["explore_gain"] == 0.4375
    assert records[0]["executive_policy_view"]["switch_margin"] == 0.045
    assert records[0]["executive_state"]["posture"] == "inspect"
    assert records[0]["operator_route"]["route_profile"] == "inspect_light"
    assert records[0]["closure_required"] is False
    assert records[0]["closure_reason_tags"] == []
    assert records[-1]["journal"]["confirmed_artifact_refs"] == ["oa-artifact-1"]
    assert records[-1]["journal"]["executive_modulator_memory"] is not None
    assert records[-1]["journal"]["next_recommended_move"] == "check"


def test_openai_runtime_cli_explicit_load_save_works(tmp_path: Path) -> None:
    artifact_path = tmp_path / "openai-session.json"

    first_completed = _run_openai_cli(
        "--save-session",
        str(artifact_path),
        input_text='{"event_name":"response.output_text.delta","payload":{"session_id":"oa-resume","response_id":"resp-1","delta":"hello"}}\n',
    )
    second_completed = _run_openai_cli(
        "--load-session",
        str(artifact_path),
        "--save-session",
        str(artifact_path),
        input_text='{"event_name":"response.completed","payload":{"session_id":"oa-resume","response_id":"resp-1","commitment_id":"oa-commit","externally_consequential":true,"result_artifact_ref":"oa-artifact"}}\n',
    )

    assert first_completed.returncode == 0, first_completed.stderr
    assert second_completed.returncode == 0, second_completed.stderr

    records = _parse_jsonl_output(second_completed.stdout)
    assert records[0]["event_index"] == 2
    assert records[0]["raw_host_event_name"] == "response.completed"
    assert _parse_session_artifact(artifact_path)["journal"]["event_index"] == 2


def test_openai_runtime_cli_rejects_canonical_cortex_event_names() -> None:
    completed = _run_openai_cli(
        input_text='{"event_name":"external/observation","payload":{"session_id":"oa-bad","response_id":"resp"}}\n'
    )

    assert completed.returncode == 1
    assert completed.stdout == ""
    assert (
        completed.stderr
        == "openai_cli error: line 1: event_name must be a raw OpenAI host event name, not a canonical Cortex event name.\n"
    )


def test_openai_runtime_cli_offline_publication_file_matches_direct_runtime_projection(
    tmp_path: Path,
) -> None:
    publication_path = tmp_path / "offline-publication.json"
    publication_path.write_text(
        json.dumps(offline_support_publication_as_payload(_offline_publication())),
        encoding="utf-8",
    )
    input_text = (
        '{"event_name":"response.output_text.delta","payload":{"session_id":"oa-memory-cli","response_id":"resp-memory-cli","delta":"hello"}}\n'
    )

    completed = _run_openai_cli(
        "--offline-publication-file",
        str(publication_path),
        input_text=input_text,
    )

    assert completed.returncode == 0, completed.stderr
    records = _parse_jsonl_output(completed.stdout)
    direct = run_openai_runtime_step(
        "response.output_text.delta",
        {
            "session_id": "oa-memory-cli",
            "response_id": "resp-memory-cli",
            "delta": "hello",
        },
        offline_publication=_offline_publication(),
    )

    assert records[0]["control_ledger"]["allocation_diagnostics"]["memory_reentry"] == direct.control_ledger_summary["allocation_diagnostics"]["memory_reentry"]


def test_openai_runtime_cli_rejects_malformed_offline_publication_file(tmp_path: Path) -> None:
    publication_path = tmp_path / "broken-publication.json"
    publication_path.write_text("{not-json\n", encoding="utf-8")

    completed = _run_openai_cli(
        "--offline-publication-file",
        str(publication_path),
        input_text='{"event_name":"response.output_text.delta","payload":{"session_id":"oa-broken-publication","response_id":"resp-broken-publication","delta":"hello"}}\n',
    )

    assert completed.returncode == 1
    assert completed.stdout == ""
    assert completed.stderr.startswith("openai_cli error: offline publication file")


def test_openai_runtime_cli_rejects_missing_offline_publication_file(tmp_path: Path) -> None:
    publication_path = tmp_path / "missing-publication.json"

    completed = _run_openai_cli(
        "--offline-publication-file",
        str(publication_path),
        input_text='{"event_name":"response.output_text.delta","payload":{"session_id":"oa-missing-publication","response_id":"resp-missing-publication","delta":"hello"}}\n',
    )

    assert completed.returncode == 1
    assert completed.stdout == ""
    assert (
        completed.stderr
        == f"openai_cli error: offline publication file {publication_path} does not exist.\n"
    )


def test_openai_runtime_cli_load_save_failure_emits_no_stdout(tmp_path: Path) -> None:
    broken_path = tmp_path / "broken.json"
    broken_path.write_text("{not-json\n", encoding="utf-8")

    load_failed = _run_openai_cli(
        "--load-session",
        str(broken_path),
        input_text='{"event_name":"response.output_text.delta","payload":{"session_id":"oa-broken","response_id":"resp"}}\n',
    )
    save_failed = _run_openai_cli(
        "--save-session",
        str(tmp_path / "missing" / "session.json"),
        input_text='{"event_name":"response.output_text.delta","payload":{"session_id":"oa-save","response_id":"resp"}}\n',
    )

    assert load_failed.returncode == 1
    assert load_failed.stdout == ""
    assert load_failed.stderr.startswith("openai_cli error:")

    assert save_failed.returncode == 1
    assert save_failed.stdout == ""
    assert save_failed.stderr.startswith("openai_cli error:")


def test_openai_runtime_cli_undocumented_raw_host_event_warns_without_fabricating_parity() -> None:
    completed = _run_openai_cli(
        input_text='{"event_name":"response.tool_event","payload":{"session_id":"oa-gap","response_id":"resp-gap","commitment_id":"oa-gap-commit","externally_consequential":true,"result_artifact_ref":"oa-gap-artifact"}}\n'
    )

    assert completed.returncode == 0, completed.stderr
    records = _parse_jsonl_output(completed.stdout)

    assert records[0]["raw_host_event_name"] == "response.tool_event"
    assert records[0]["native_event_name"] == "external/observation"
    assert records[0]["commitment_result_kind"] == "certified"
    assert records[0]["warnings"] == [
        "No documented OpenAI lifecycle mapping for 'response.tool_event'; using conservative external/observation binding."
    ]


def _run_openai_cli(*args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "cortex.hosts.openai.cli", *args],
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


def _offline_publication() -> OfflineSupportPublication:
    return OfflineSupportPublication(
        contradiction_summary_refs=(make_support_ref("contradiction", "host-degraded"),),
        publication_tags=frozenset({"aux/offline-publication"}),
        notes=("support-side only",),
        metadata=(
            MetadataField("source", "aux/distillation"),
            MetadataField("host_name", "openai"),
        ),
    )
