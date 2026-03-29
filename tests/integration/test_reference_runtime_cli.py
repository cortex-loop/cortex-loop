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
from cortex.sre.policy import neutral_dominance_decision
from cortex.sre.reference_scoring import build_reference_allocation_scorecard
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
FEEDBACK_WINDOW_FIXTURE_PATH = (
    REPO_ROOT
    / "tests"
    / "integration"
    / "fixtures"
    / "reference_runtime_feedback_window_session.jsonl"
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
    "feedback_window_summary",
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
    assert [record["feedback_window_summary"]["window_size"] for record in records] == [0, 1, 2]
    assert all(record["warnings"] == [] for record in records)
    assert records[-1]["session_summary"]["event_index"] == 3
    assert records[-1]["session_summary"]["budget_history"] == [
        "shell-low",
        "shell-medium",
        "shell-high",
    ]
    assert records[-1]["session_summary"]["feedback_window_size"] == 3
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
        "feedback_window_summary",
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
        "allocation_diagnostics",
    )
    assert tuple(records[-1]["control_ledger"]["allocation_diagnostics"]) == (
        "alpha_t",
        "activation_threshold",
        "selected_delta_over_neutral",
        "scores",
    )
    assert [record["control_ledger"]["allocation_diagnostics"]["alpha_t"] for record in records] == [
        1.0,
        0.85,
        0.85,
    ]
    assert records[1]["control_ledger"]["allocation_diagnostics"]["scores"][0]["allocated_score"] != records[1]["control_ledger"]["allocation_diagnostics"]["scores"][0]["online_score"]
    assert records[2]["control_ledger"]["allocation_diagnostics"]["scores"][0]["allocated_score"] != records[2]["control_ledger"]["allocation_diagnostics"]["scores"][0]["online_score"]


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
        "feedback_window_summary",
    )
    assert records[0]["selected_family"] == "branch"
    assert records[0]["warnings"] == ["latched-brake-enforced:branch:check"]
    assert records[0]["control_ledger"]["selected_family"] == "branch"
    assert records[0]["control_ledger"]["realized_family"] == "check"
    assert records[0]["control_ledger"]["primary_reason"] == (
        "latched-brake-enforced:branch:check"
    )
    assert records[0]["commitment_result_kind"] == "certified"
    assert records[0]["feedback_window_summary"]["window_size"] == 0


def test_reference_runtime_cli_emits_feedback_window_summary_for_real_session_mismatch_sequences() -> None:
    completed = _run_reference_cli("--event-file", str(FEEDBACK_WINDOW_FIXTURE_PATH))

    assert completed.returncode == 0, completed.stderr
    records = _parse_jsonl_output(completed.stdout)

    assert len(records) == 5
    assert [record["session_summary"]["feedback_window_size"] for record in records] == [
        1,
        2,
        3,
        3,
        3,
    ]
    assert records[2]["feedback_window_summary"] == {
        "window_size": 2,
        "rejection_count": 1,
        "override_count": 0,
        "latched_count": 0,
        "clean_success_streak": 0,
        "goal_progress_floor": 0.55,
        "degradation_pressure_bonus": 1,
        "sustained_spike_flags": ["prior-session-mismatch"],
    }
    assert records[4]["feedback_window_summary"] == {
        "window_size": 3,
        "rejection_count": 2,
        "override_count": 0,
        "latched_count": 0,
        "clean_success_streak": 0,
        "goal_progress_floor": 0.70,
        "degradation_pressure_bonus": 2,
        "sustained_spike_flags": [
            "prior-session-mismatch",
            "sustained-feedback-disruption",
        ],
    }
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
        "feedback_window_summary",
    )


def test_reference_runtime_cli_save_session_does_not_change_jsonl_output(tmp_path: Path) -> None:
    artifact_path = tmp_path / "session.json"

    without_save = _run_reference_cli("--event-file", str(FIXTURE_PATH))
    with_save = _run_reference_cli(
        "--event-file",
        str(FIXTURE_PATH),
        "--save-session",
        str(artifact_path),
    )

    assert without_save.returncode == 0, without_save.stderr
    assert with_save.returncode == 0, with_save.stderr
    assert with_save.stdout == without_save.stdout
    assert _parse_session_artifact(artifact_path) == {
        "artifact_kind": "reference-runtime-session",
        "artifact_version": 1,
        "continuity_truth": {
            "session_id": "cli-session-1",
            "event_index": 3,
            "branch_registry": ["main"],
            "active_track_ref": "main",
            "pending_goal_refs": [],
        },
        "control_residue": {
            "last_budget_band": "high",
            "last_commitment_result_summary": "certified",
            "last_realization_feedback": {
                "selected_family": "neutral",
                "realized_family": "neutral",
                "brake_state": "quiescent",
                "commitment_result_kind": "certified",
                "warning_codes": [],
                "host_friction_tags": ["approval-boundary-present"],
            },
            "feedback_window": [
                {
                    "selected_family": "neutral",
                    "realized_family": "neutral",
                    "brake_state": "quiescent",
                    "commitment_result_kind": None,
                    "warning_codes": [],
                    "host_friction_tags": [],
                },
                {
                    "selected_family": "neutral",
                    "realized_family": "neutral",
                    "brake_state": "quiescent",
                    "commitment_result_kind": None,
                    "warning_codes": [],
                    "host_friction_tags": ["approval-boundary-present"],
                },
                {
                    "selected_family": "neutral",
                    "realized_family": "neutral",
                    "brake_state": "quiescent",
                    "commitment_result_kind": "certified",
                    "warning_codes": [],
                    "host_friction_tags": ["approval-boundary-present"],
                },
            ],
        },
    }


def test_reference_runtime_cli_load_session_continues_event_index(tmp_path: Path) -> None:
    artifact_path = tmp_path / "session.json"
    final_path = tmp_path / "final.json"

    initial_completed = _run_reference_cli(
        "--save-session",
        str(artifact_path),
        input_text="\n".join(FIXTURE_PATH.read_text(encoding="utf-8").splitlines()[:2]) + "\n",
    )
    resumed_completed = _run_reference_cli(
        "--load-session",
        str(artifact_path),
        "--save-session",
        str(final_path),
        input_text=FIXTURE_PATH.read_text(encoding="utf-8").splitlines()[2] + "\n",
    )

    assert initial_completed.returncode == 0, initial_completed.stderr
    assert resumed_completed.returncode == 0, resumed_completed.stderr

    resumed_records = _parse_jsonl_output(resumed_completed.stdout)

    assert [record["event_index"] for record in resumed_records] == [3]
    assert resumed_records[0]["commitment_result_kind"] == "certified"
    assert _parse_session_artifact(final_path)["continuity_truth"]["event_index"] == 3


def test_reference_runtime_cli_same_path_load_and_save_replaces_artifact(tmp_path: Path) -> None:
    artifact_path = tmp_path / "session.json"

    first_completed = _run_reference_cli(
        "--save-session",
        str(artifact_path),
        input_text='{"event_name":"ContextLoad","payload":{"session_id":"same-path-session"}}\n',
    )
    second_completed = _run_reference_cli(
        "--load-session",
        str(artifact_path),
        "--save-session",
        str(artifact_path),
        input_text='{"event_name":"ApprovalRequest","payload":{"session_id":"same-path-session","candidate_id":"candidate-1"}}\n',
    )

    assert first_completed.returncode == 0, first_completed.stderr
    assert second_completed.returncode == 0, second_completed.stderr
    assert _parse_session_artifact(artifact_path)["continuity_truth"]["event_index"] == 2


def test_reference_runtime_cli_bad_load_artifact_exits_non_zero_and_emits_no_stdout(
    tmp_path: Path,
) -> None:
    artifact_path = tmp_path / "broken.json"
    artifact_path.write_text("{not-json\n", encoding="utf-8")

    completed = _run_reference_cli(
        "--load-session",
        str(artifact_path),
        input_text='{"event_name":"ContextLoad","payload":{"session_id":"broken"}}\n',
    )

    assert completed.returncode == 1
    assert completed.stdout == ""
    assert completed.stderr.startswith("reference_cli error:")


def test_reference_runtime_cli_save_failure_emits_no_stdout(tmp_path: Path) -> None:
    missing_parent = tmp_path / "missing-parent" / "session.json"

    completed = _run_reference_cli(
        "--save-session",
        str(missing_parent),
        input_text='{"event_name":"ContextLoad","payload":{"session_id":"save-failure"}}\n',
    )

    assert completed.returncode == 1
    assert completed.stdout == ""
    assert completed.stderr.startswith("reference_cli error:")


def test_reference_runtime_cli_zero_event_load_save_roundtrip_works(tmp_path: Path) -> None:
    artifact_path = tmp_path / "session.json"

    initial_completed = _run_reference_cli(
        "--save-session",
        str(artifact_path),
        input_text='{"event_name":"ContextLoad","payload":{"session_id":"zero-event"}}\n',
    )
    original_payload = _parse_session_artifact(artifact_path)
    roundtrip_completed = _run_reference_cli(
        "--load-session",
        str(artifact_path),
        "--save-session",
        str(artifact_path),
        input_text="",
    )

    assert initial_completed.returncode == 0, initial_completed.stderr
    assert roundtrip_completed.returncode == 0, roundtrip_completed.stderr
    assert roundtrip_completed.stdout == ""
    assert _parse_session_artifact(artifact_path) == original_payload


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


def _parse_session_artifact(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _selection(selected_family: SoftControlFamily) -> object:
    class _Selection:
        def __init__(self, family: SoftControlFamily) -> None:
            self.selected_family = family
            self.scorecard = build_reference_allocation_scorecard(
                _latched_state_with_evidence()
            )
            self.neutral_dominance = neutral_dominance_decision(self.scorecard)

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
