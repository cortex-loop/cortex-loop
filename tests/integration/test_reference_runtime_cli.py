"""Integration tests for the reference-host runtime CLI shell."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

import cortex.runtime.reference as reference_runtime
import cortex.runtime.reference_cli as reference_cli
from cortex.sre.brake import BrakeState
from cortex.sre.families import SoftControlFamily
from cortex.sre.state import (
    ReferenceBrakeView,
    ReferenceControlAllocationView,
    ReferenceExecutiveState,
    ReferenceGoalContinuityView,
    ReferenceModeAndGatingView,
    ReferenceUncertaintyMonitoringView,
)
from cortex.sre.uncertainty import UncertaintyEstimate


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = (
    REPO_ROOT / "tests" / "integration" / "fixtures" / "reference_runtime_cli_session.jsonl"
)
EXPECTED_RECORD_KEYS = {
    "event_index",
    "native_event_name",
    "dispatch_lane",
    "selected_family",
    "brake_state",
    "executive_state_summary",
    "control_ledger",
    "warnings",
    "session_summary",
    "commitment_result_kind",
}


def test_reference_runtime_cli_reads_event_file_and_emits_one_record_per_event() -> None:
    completed = _run_reference_cli("--event-file", str(FIXTURE_PATH))

    assert completed.returncode == 0, completed.stderr
    assert completed.stderr == ""

    records = _parse_jsonl_output(completed.stdout)

    assert len(records) == 3
    assert all(set(record) == EXPECTED_RECORD_KEYS for record in records)
    assert [record["event_index"] for record in records] == [1, 2, 3]
    assert [record["native_event_name"] for record in records] == [
        "context/load",
        "approval/request",
        "approval/result",
    ]
    assert [record["dispatch_lane"] for record in records] == [
        "cheap",
        "candidate-bearing",
        "full-commitment",
    ]
    assert [record["selected_family"] for record in records] == [
        "neutral",
        "neutral",
        "neutral",
    ]
    assert [record["brake_state"] for record in records] == [
        "quiescent",
        "quiescent",
        "quiescent",
    ]
    assert [record["executive_state_summary"]["mode_tag"] for record in records] == [
        "pass_through",
        "review_pending",
        "commitment_path",
    ]
    assert [record["executive_state_summary"]["budget_band"] for record in records] == [
        "low",
        "medium",
        "high",
    ]
    assert [record["control_ledger"]["event_class"] for record in records] == [
        "cheap",
        "candidate-bearing",
        "full-commitment",
    ]
    assert [record["control_ledger"]["selected_family"] for record in records] == [
        "neutral",
        "neutral",
        "neutral",
    ]
    assert [record["control_ledger"]["realized_family"] for record in records] == [
        "neutral",
        "neutral",
        "neutral",
    ]
    assert [record["control_ledger"]["brake_state"] for record in records] == [
        "quiescent",
        "quiescent",
        "quiescent",
    ]
    assert [record["commitment_result_kind"] for record in records] == [
        None,
        None,
        "certified",
    ]
    assert all(record["warnings"] == [] for record in records)
    assert records[-1]["session_summary"]["event_index"] == 3
    assert records[-1]["session_summary"]["budget_history"] == [
        "shell-low",
        "shell-medium",
        "shell-high",
    ]
    assert records[-1]["executive_state_summary"]["top_family_set"] == ["neutral"]
    assert tuple(records[-1]) == (
        "event_index",
        "native_event_name",
        "dispatch_lane",
        "selected_family",
        "brake_state",
        "executive_state_summary",
        "control_ledger",
        "warnings",
        "session_summary",
        "commitment_result_kind",
    )
    assert tuple(records[-1]["control_ledger"]) == (
        "event_class",
        "admissible_families",
        "selected_family",
        "realized_family",
        "dominant_uncertainty_sources",
        "brake_state",
        "budget_band",
        "primary_reason",
    )


def test_reference_runtime_cli_reads_stdin_and_preserves_locked_output_contract() -> None:
    fixture_text = FIXTURE_PATH.read_text(encoding="utf-8")

    from_file = _parse_jsonl_output(
        _run_reference_cli("--event-file", str(FIXTURE_PATH)).stdout
    )
    from_stdin = _parse_jsonl_output(
        _run_reference_cli(input_text=fixture_text).stdout
    )

    assert from_stdin == from_file


def test_reference_runtime_cli_in_process_surfaces_selected_vs_realized_divergence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        reference_runtime,
        "build_reference_executive_state",
        _latched_state_with_evidence,
    )
    monkeypatch.setattr(
        reference_runtime,
        "select_reference_soft_control",
        lambda executive_state: _selection(SoftControlFamily.BRANCH),
    )

    records = reference_cli._run_reference_cli_lines(
        [
            json.dumps(
                {
                    "event_name": "ApprovalResult",
                    "payload": {
                        "session_id": "session-cli-enforced",
                        "commitment_id": "commit-cli-enforced",
                        "externally_consequential": True,
                        "result_artifact_ref": "artifact-cli-enforced",
                    },
                }
            )
        ]
    )

    assert len(records) == 1
    assert tuple(records[0]) == (
        "event_index",
        "native_event_name",
        "dispatch_lane",
        "selected_family",
        "brake_state",
        "executive_state_summary",
        "control_ledger",
        "warnings",
        "session_summary",
        "commitment_result_kind",
    )
    assert records[0]["selected_family"] == "branch"
    assert records[0]["warnings"] == ["latched-brake-enforced:branch:check"]
    assert records[0]["control_ledger"]["selected_family"] == "branch"
    assert records[0]["control_ledger"]["realized_family"] == "check"
    assert records[0]["control_ledger"]["primary_reason"] == (
        "latched-brake-enforced:branch:check"
    )
    assert records[0]["commitment_result_kind"] == "certified"


def _run_reference_cli(*args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "cortex.runtime.reference_cli", *args],
        cwd=REPO_ROOT,
        input=input_text,
        capture_output=True,
        text=True,
        check=False,
    )


def _parse_jsonl_output(stdout: str) -> list[dict[str, object]]:
    lines = [line for line in stdout.splitlines() if line.strip()]
    return [json.loads(line) for line in lines]


def _selection(selected_family: SoftControlFamily) -> object:
    class _Selection:
        def __init__(self, family: SoftControlFamily) -> None:
            self.selected_family = family

    return _Selection(selected_family)


def _latched_state_with_evidence(*args: object, **kwargs: object) -> ReferenceExecutiveState:
    return ReferenceExecutiveState(
        goal_continuity=ReferenceGoalContinuityView(active_track_ref="review-track"),
        uncertainty_monitoring=ReferenceUncertaintyMonitoringView(
            classwise_uncertainty=(
                UncertaintyEstimate(class_tag="evidence", level=0.95),
                UncertaintyEstimate(class_tag="environment", level=0.75),
                UncertaintyEstimate(class_tag="host-capability", level=0.2),
                UncertaintyEstimate(class_tag="goal-progress", level=0.4),
            )
        ),
        mode_and_gating=ReferenceModeAndGatingView(
            mode_tag="latched_review",
            family_mask=frozenset(
                {
                    SoftControlFamily.NEUTRAL,
                    SoftControlFamily.CHECK,
                    SoftControlFamily.BRANCH,
                    SoftControlFamily.BRAKE,
                }
            ),
        ),
        control_allocation=ReferenceControlAllocationView(
            budget_band="high",
            top_family_set=frozenset(
                {
                    SoftControlFamily.NEUTRAL,
                    SoftControlFamily.BRANCH,
                    SoftControlFamily.BRAKE,
                }
            ),
        ),
        brake=ReferenceBrakeView(brake_state=BrakeState.LATCHED),
    )
