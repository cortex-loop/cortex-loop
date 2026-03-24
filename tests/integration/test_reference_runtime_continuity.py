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


def _run_reference_cli(
    *args: str,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
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
