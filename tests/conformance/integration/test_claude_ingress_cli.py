"""Integration tests for raw Claude transcript ingress CLI."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_PATH = (
    REPO_ROOT / "tests" / "conformance" / "fixtures" / "claude_ingress_cli_session.jsonl"
)
EXPECTED_RECORD_KEYS = (
    "event_index",
    "raw_host_event_name",
    "message_id",
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
    "executive_signal_summary",
    "executive_modulator_state",
    "executive_policy_view",
    "operator_route",
    "closure_required",
    "closure_reason_tags",
)


def test_claude_ingress_cli_reads_documented_raw_transcript_fixture() -> None:
    completed = _run_claude_ingress_cli("--event-file", str(FIXTURE_PATH))

    assert completed.returncode == 0, completed.stderr
    records = _parse_jsonl_output(completed.stdout)

    assert len(records) == 3
    assert tuple(records[0]) == EXPECTED_RECORD_KEYS
    assert [record["raw_host_event_name"] for record in records] == [
        "content_block_delta",
        "content_block_delta",
        "message_stop",
    ]
    assert [record["message_id"] for record in records] == [
        "cl-msg-ingress-1",
        "cl-msg-ingress-1",
        "cl-msg-ingress-1",
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
        "audit_projection",
    )
    assert records[-1]["control_ledger"]["audit_projection"]["selected_family"] == (
        records[-1]["control_ledger"]["selected_family"]
    )
    assert tuple(records[-1]["control_ledger"]["allocation_diagnostics"]) == (
        "alpha_t",
        "activation_threshold",
        "selected_delta_over_neutral",
        "chi_t",
        "risk_weight",
        "brake_tonic",
        "rejected_cheaper_families",
        "probe_path_state",
        "probe_unavailable_reason",
        "probe_result_class",
        "verification_state",
        "explainability_profile",
        "anti_thrash",
        "scores",
    )
    assert [record["executive_state_summary"]["probe_path_state"] for record in records] == [
        "unavailable",
        "unavailable",
        "unavailable",
    ]
    assert [record["executive_state_summary"]["posture"] for record in records] == [
        "inspect",
        "execute",
        "execute",
    ]
    assert records[0]["operator_route"]["route_profile"] == "inspect_light"
    assert [
        record["operator_route"]["route_profile"].startswith("execute_")
        for record in records[1:]
    ] == [True, True]
    assert [record["operator_route"]["route_budget"]["allow_extra_read_pass"] for record in records] == [
        True,
        False,
        False,
    ]


def test_claude_ingress_cli_load_save_works(tmp_path: Path) -> None:
    artifact_path = tmp_path / "claude-ingress-session.json"

    first_completed = _run_claude_ingress_cli(
        "--save-session",
        str(artifact_path),
        input_text='{"type":"content_block_delta","session_id":"cl-ingress-resume","message_id":"cl-msg-1","delta":"hello"}\n',
    )
    second_completed = _run_claude_ingress_cli(
        "--load-session",
        str(artifact_path),
        "--save-session",
        str(artifact_path),
        input_text='{"type":"message_stop","session_id":"cl-ingress-resume","message_id":"cl-msg-1","commitment_id":"cl-ingress-commit","externally_consequential":true,"result_artifact_ref":"cl-ingress-artifact"}\n',
    )

    assert first_completed.returncode == 0, first_completed.stderr
    assert second_completed.returncode == 0, second_completed.stderr
    records = _parse_jsonl_output(second_completed.stdout)
    assert records[0]["event_index"] == 2
    assert records[0]["raw_host_event_name"] == "message_stop"


def test_claude_ingress_cli_rejects_canonical_event_names_wrapper_shape_and_mixed_shape() -> None:
    canonical = _run_claude_ingress_cli(
        input_text='{"type":"external/observation","session_id":"cl-bad","message_id":"cl-msg-1"}\n'
    )
    wrapper = _run_claude_ingress_cli(
        input_text='{"event_name":"message_stop","payload":{"session_id":"cl-bad","message_id":"cl-msg-1"}}\n'
    )
    mixed = _run_claude_ingress_cli(
        input_text='{"type":"message_stop","event_name":"message_stop","payload":{"session_id":"cl-bad","message_id":"cl-msg-1"},"session_id":"cl-bad","message_id":"cl-msg-1","commitment_id":"cl-bad-commit","externally_consequential":true,"result_artifact_ref":"cl-bad-artifact"}\n'
    )

    assert canonical.returncode == 1
    assert canonical.stdout == ""
    assert "raw Claude host event name" in canonical.stderr

    assert wrapper.returncode == 1
    assert wrapper.stdout == ""
    assert "wrapper and mixed wrapper/transcript" in wrapper.stderr

    assert mixed.returncode == 1
    assert mixed.stdout == ""
    assert "wrapper and mixed wrapper/transcript" in mixed.stderr


def test_claude_ingress_cli_undocumented_raw_host_event_still_warns_conservatively() -> None:
    completed = _run_claude_ingress_cli(
        input_text='{"type":"content_block_magic","session_id":"cl-gap","message_id":"cl-msg-gap","commitment_id":"cl-gap-commit","externally_consequential":true,"result_artifact_ref":"cl-gap-artifact"}\n'
    )

    assert completed.returncode == 0, completed.stderr
    records = _parse_jsonl_output(completed.stdout)
    assert records[0]["raw_host_event_name"] == "content_block_magic"
    assert records[0]["warnings"] == [
        "No documented Claude lifecycle mapping for 'content_block_magic'; using conservative external/observation binding."
    ]


def _run_claude_ingress_cli(
    *args: str,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "cortex.hosts.claude.ingress_cli", *args],
        cwd=REPO_ROOT,
        input=input_text,
        capture_output=True,
        text=True,
        check=False,
    )


def _parse_jsonl_output(stdout: str) -> list[dict[str, object]]:
    lines = [line for line in stdout.splitlines() if line.strip()]
    return [json.loads(line) for line in lines]
