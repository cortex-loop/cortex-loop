"""Integration tests for one-process reference runtime continuity."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_PATH = (
    REPO_ROOT
    / "tests"
    / "conformance"
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
        "seek-context",
        "check",
        "seek-context",
        "seek-context",
    ]
    assert [record["brake_state"] for record in records] == [
        "guarded",
        "guarded",
        "guarded",
        "guarded",
    ]
    assert [record["control_ledger"]["allocation_diagnostics"]["alpha_t"] for record in records] == [
        0.75,
        0.75,
        0.75,
        0.75,
    ]
    assert [
        record["control_ledger"]["allocation_diagnostics"]["activation_threshold"]
        for record in records
    ] == pytest.approx([0.37, 0.281, 0.333, 0.193])
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
    assert [record["executive_state_summary"]["posture"] for record in records] == [
        "resume",
        "resume",
        "resume",
        "execute",
    ]
    assert [record["operator_route"]["route_profile"] for record in records] == [
        "continuity_standard",
        "continuity_standard",
        "continuity_standard",
        "execute_standard",
    ]
    assert [record["operator_route"]["route_budget"]["allow_resume"] for record in records] == [
        True,
        True,
        True,
        False,
    ]
    assert [record["executive_state_summary"]["pending_goal_refs"] for record in records] == [
        [],
        ["branch-alpha"],
        [],
        [],
    ]
    assert [record["closure_required"] for record in records] == [
        False,
        True,
        False,
        False,
    ]
    assert [record["closure_reason_tags"] for record in records] == [
        [],
        ["continuity_reminder", "pending_goal_debt"],
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


def test_reference_runtime_cli_rejects_illegal_continuity_transitions_without_mutating_session_truth() -> None:
    missing_resume_anchor_completed = _run_reference_cli(
        input_text="\n".join(
            [
                '{"event_name":"ContextLoad","payload":{"session_id":"reject-1","branch_operation":"open","branch_track_ref":"branch-alpha"}}',
                '{"event_name":"ContextLoad","payload":{"session_id":"reject-1","branch_operation":"resume","branch_track_ref":"branch-alpha"}}',
            ]
        )
    )
    missing_active_branch_completed = _run_reference_cli(
        input_text='{"event_name":"ContextLoad","payload":{"session_id":"reject-2","branch_operation":"suspend","branch_track_ref":"branch-alpha"}}\n'
    )
    illegal_merge_target_completed = _run_reference_cli(
        input_text="\n".join(
            [
                '{"event_name":"ContextLoad","payload":{"session_id":"reject-3","branch_operation":"open","branch_track_ref":"branch-alpha"}}',
                '{"event_name":"ApprovalResult","payload":{"session_id":"reject-3","branch_operation":"merge","branch_track_ref":"branch-alpha","merge_target_ref":"branch-ghost","commitment_id":"commit-reject","externally_consequential":true,"result_artifact_ref":"artifact-reject"}}',
            ]
        )
    )
    suspended_merge_completed = _run_reference_cli(
        input_text="\n".join(
            [
                '{"event_name":"ContextLoad","payload":{"session_id":"reject-4","branch_operation":"open","branch_track_ref":"branch-alpha"}}',
                '{"event_name":"ApprovalRequest","payload":{"session_id":"reject-4","branch_operation":"suspend","branch_track_ref":"branch-alpha","candidate_id":"candidate-reject"}}',
                '{"event_name":"ApprovalResult","payload":{"session_id":"reject-4","branch_operation":"merge","branch_track_ref":"branch-alpha","merge_target_ref":"main","commitment_id":"commit-reject","externally_consequential":true,"result_artifact_ref":"artifact-reject"}}',
            ]
        )
    )
    malformed_open_completed = _run_reference_cli(
        input_text="\n".join(
            [
                '{"event_name":"ContextLoad","payload":{"session_id":"reject-5","branch_operation":"open","branch_track_ref":"branch-alpha"}}',
                '{"event_name":"ApprovalRequest","payload":{"session_id":"reject-5","branch_operation":"suspend","branch_track_ref":"branch-alpha","candidate_id":"candidate-reject"}}',
                '{"event_name":"ContextLoad","payload":{"session_id":"reject-5","branch_operation":"open"}}',
            ]
        )
    )
    pending_goal_merge_completed = _run_reference_cli(
        input_text="\n".join(
            [
                '{"event_name":"ContextLoad","payload":{"session_id":"reject-6","branch_operation":"open","branch_track_ref":"branch-alpha"}}',
                '{"event_name":"ApprovalRequest","payload":{"session_id":"reject-6","branch_operation":"suspend","branch_track_ref":"branch-alpha","candidate_id":"candidate-reject"}}',
                '{"event_name":"ContextLoad","payload":{"session_id":"reject-6","pending_goal_refs":["goal-extra"]}}',
                '{"event_name":"ContextLoad","payload":{"session_id":"reject-6","branch_operation":"resume","branch_track_ref":"branch-alpha"}}',
            ]
        )
    )
    mismatched_session_completed = _run_reference_cli(
        input_text="\n".join(
            [
                '{"event_name":"ContextLoad","payload":{"session_id":"reject-7-a"}}',
                '{"event_name":"ContextLoad","payload":{"session_id":"reject-7-b"}}',
            ]
        )
    )
    duplicate_open_completed = _run_reference_cli(
        input_text="\n".join(
            [
                '{"event_name":"ContextLoad","payload":{"session_id":"reject-8","branch_operation":"open","branch_track_ref":"branch-alpha"}}',
                '{"event_name":"ContextLoad","payload":{"session_id":"reject-8","branch_operation":"open","branch_track_ref":"branch-alpha"}}',
            ]
        )
    )

    assert missing_resume_anchor_completed.returncode == 0, missing_resume_anchor_completed.stderr
    assert missing_active_branch_completed.returncode == 0, missing_active_branch_completed.stderr
    assert illegal_merge_target_completed.returncode == 0, illegal_merge_target_completed.stderr
    assert suspended_merge_completed.returncode == 0, suspended_merge_completed.stderr
    assert malformed_open_completed.returncode == 0, malformed_open_completed.stderr
    assert pending_goal_merge_completed.returncode == 0, pending_goal_merge_completed.stderr
    assert mismatched_session_completed.returncode == 0, mismatched_session_completed.stderr
    assert duplicate_open_completed.returncode == 0, duplicate_open_completed.stderr

    missing_resume_anchor = _parse_jsonl_output(missing_resume_anchor_completed.stdout)
    missing_active_branch = _parse_jsonl_output(missing_active_branch_completed.stdout)
    illegal_merge_target = _parse_jsonl_output(illegal_merge_target_completed.stdout)
    suspended_merge = _parse_jsonl_output(suspended_merge_completed.stdout)
    malformed_open = _parse_jsonl_output(malformed_open_completed.stdout)
    pending_goal_merge = _parse_jsonl_output(pending_goal_merge_completed.stdout)
    mismatched_session = _parse_jsonl_output(mismatched_session_completed.stdout)
    duplicate_open = _parse_jsonl_output(duplicate_open_completed.stdout)

    assert missing_resume_anchor[-1]["warnings"] == [
        "continuity-rejected:missing-resume-anchor:branch-alpha"
    ]
    assert missing_resume_anchor[-1]["session_summary"]["branch_registry"] == ["main", "branch-alpha"]
    assert missing_resume_anchor[-1]["session_summary"]["active_track_ref"] == "branch-alpha"
    assert missing_resume_anchor[-1]["brake_state"] == "guarded"

    assert missing_active_branch[-1]["warnings"] == [
        "continuity-rejected:missing-active-branch:branch-alpha"
    ]
    assert missing_active_branch[-1]["session_summary"]["branch_registry"] == ["main"]
    assert missing_active_branch[-1]["session_summary"]["active_track_ref"] == "main"
    assert missing_active_branch[-1]["session_summary"]["pending_goal_refs"] == []
    assert missing_active_branch[-1]["brake_state"] == "guarded"

    assert illegal_merge_target[-1]["warnings"] == [
        "continuity-rejected:illegal-merge-target:branch-ghost"
    ]
    assert illegal_merge_target[-1]["session_summary"]["branch_registry"] == ["main", "branch-alpha"]
    assert illegal_merge_target[-1]["session_summary"]["active_track_ref"] == "branch-alpha"
    assert illegal_merge_target[-1]["commitment_result_kind"] == "certified"

    assert suspended_merge[-1]["warnings"] == [
        "continuity-rejected:continuity-mismatch-after-suspension:branch-alpha"
    ]
    assert suspended_merge[-1]["session_summary"]["branch_registry"] == ["main", "branch-alpha"]
    assert suspended_merge[-1]["session_summary"]["active_track_ref"] == "main"
    assert suspended_merge[-1]["session_summary"]["pending_goal_refs"] == ["branch-alpha"]
    assert suspended_merge[-1]["brake_state"] == "guarded"
    assert suspended_merge[-1]["commitment_result_kind"] == "certified"

    assert malformed_open[-1]["warnings"] == [
        "continuity-rejected:missing-open-track-ref"
    ]
    assert malformed_open[-1]["session_summary"]["branch_registry"] == ["main", "branch-alpha"]
    assert malformed_open[-1]["session_summary"]["active_track_ref"] == "main"
    assert malformed_open[-1]["session_summary"]["pending_goal_refs"] == ["branch-alpha"]

    assert pending_goal_merge[-1]["warnings"] == []
    assert pending_goal_merge[-1]["session_summary"]["active_track_ref"] == "branch-alpha"
    assert pending_goal_merge[-1]["session_summary"]["pending_goal_refs"] == ["goal-extra"]
    assert pending_goal_merge[-1]["executive_state_summary"]["pending_goal_refs"] == ["goal-extra"]

    assert mismatched_session[-1]["warnings"] == [
        "session-rejected:mismatched-session-id:reject-7-b"
    ]
    assert mismatched_session[-1]["session_summary"]["session_id"] == "reject-7-a"

    assert duplicate_open[-1]["warnings"] == []
    assert duplicate_open[-1]["session_summary"]["branch_registry"] == ["main", "branch-alpha"]
    assert duplicate_open[-1]["session_summary"]["active_track_ref"] == "branch-alpha"
    assert duplicate_open[-1]["session_summary"]["pending_goal_refs"] == []


def test_reference_runtime_cli_split_session_is_c1_equivalent_to_one_process_baseline(
    tmp_path: Path,
) -> None:
    one_process_artifact = tmp_path / "one-process.json"
    split_seed_artifact = tmp_path / "split-seed.json"
    split_final_artifact = tmp_path / "split-final.json"
    fixture_lines = FIXTURE_PATH.read_text(encoding="utf-8").splitlines()

    one_process_completed = _run_reference_cli(
        "--event-file",
        str(FIXTURE_PATH),
        "--save-session",
        str(one_process_artifact),
    )
    split_first_completed = _run_reference_cli(
        "--save-session",
        str(split_seed_artifact),
        input_text="\n".join(fixture_lines[:2]) + "\n",
    )
    split_second_completed = _run_reference_cli(
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

    _assert_c1_equivalent(
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


def test_reference_runtime_cli_preserves_malformed_open_rejection_across_restart(
    tmp_path: Path,
) -> None:
    artifact_path = tmp_path / "session.json"

    first_completed = _run_reference_cli(
        "--save-session",
        str(artifact_path),
        input_text="\n".join(
            [
                '{"event_name":"ContextLoad","payload":{"session_id":"restart-open","branch_operation":"open","branch_track_ref":"branch-alpha"}}',
                '{"event_name":"ApprovalRequest","payload":{"session_id":"restart-open","branch_operation":"suspend","branch_track_ref":"branch-alpha","candidate_id":"candidate-1"}}',
            ]
        )
        + "\n",
    )
    second_completed = _run_reference_cli(
        "--load-session",
        str(artifact_path),
        input_text='{"event_name":"ContextLoad","payload":{"session_id":"restart-open","branch_operation":"open"}}\n',
    )

    assert first_completed.returncode == 0, first_completed.stderr
    assert second_completed.returncode == 0, second_completed.stderr

    records = _parse_jsonl_output(second_completed.stdout)

    assert records[-1]["warnings"] == ["continuity-rejected:missing-open-track-ref"]
    assert records[-1]["session_summary"]["branch_registry"] == ["main", "branch-alpha"]
    assert records[-1]["session_summary"]["active_track_ref"] == "main"
    assert records[-1]["session_summary"]["pending_goal_refs"] == ["branch-alpha"]


def test_reference_runtime_cli_preserves_mismatched_session_rejection_across_restart(
    tmp_path: Path,
) -> None:
    artifact_path = tmp_path / "session.json"

    first_completed = _run_reference_cli(
        "--save-session",
        str(artifact_path),
        input_text='{"event_name":"ContextLoad","payload":{"session_id":"restart-stable-a"}}\n',
    )
    second_completed = _run_reference_cli(
        "--load-session",
        str(artifact_path),
        input_text='{"event_name":"ContextLoad","payload":{"session_id":"restart-stable-b"}}\n',
    )

    assert first_completed.returncode == 0, first_completed.stderr
    assert second_completed.returncode == 0, second_completed.stderr

    records = _parse_jsonl_output(second_completed.stdout)

    assert records[-1]["warnings"] == [
        "session-rejected:mismatched-session-id:restart-stable-b"
    ]
    assert records[-1]["session_summary"]["session_id"] == "restart-stable-a"


def test_reference_runtime_cli_preserves_certified_commitment_plus_illegal_merge_target_across_restart(
    tmp_path: Path,
) -> None:
    artifact_path = tmp_path / "session.json"

    first_completed = _run_reference_cli(
        "--save-session",
        str(artifact_path),
        input_text='{"event_name":"ContextLoad","payload":{"session_id":"restart-merge","branch_operation":"open","branch_track_ref":"branch-alpha"}}\n',
    )
    second_completed = _run_reference_cli(
        "--load-session",
        str(artifact_path),
        input_text='{"event_name":"ApprovalResult","payload":{"session_id":"restart-merge","branch_operation":"merge","branch_track_ref":"branch-alpha","merge_target_ref":"branch-ghost","commitment_id":"commit-restart","externally_consequential":true,"result_artifact_ref":"artifact-restart"}}\n',
    )

    assert first_completed.returncode == 0, first_completed.stderr
    assert second_completed.returncode == 0, second_completed.stderr

    records = _parse_jsonl_output(second_completed.stdout)

    assert records[-1]["warnings"] == [
        "continuity-rejected:illegal-merge-target:branch-ghost"
    ]
    assert records[-1]["commitment_result_kind"] == "certified"
    assert records[-1]["session_summary"]["branch_registry"] == ["main", "branch-alpha"]
    assert records[-1]["session_summary"]["active_track_ref"] == "branch-alpha"


def _run_reference_cli(
    *args: str,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "cortex.hosts.reference.cli", *args],
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


def _assert_c1_equivalent(
    expected_records: list[dict[str, object]],
    actual_records: list[dict[str, object]],
    expected_artifact: dict[str, object],
    actual_artifact: dict[str, object],
) -> None:
    assert len(expected_records) == len(actual_records)
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
    assert actual_artifact["continuity_truth"] == expected_artifact["continuity_truth"]
    assert actual_artifact["control_residue"] == expected_artifact["control_residue"]
