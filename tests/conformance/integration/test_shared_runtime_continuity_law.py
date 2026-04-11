"""Cross-host continuity-law projection locks over the existing runtime fixtures."""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_DIR = REPO_ROOT / "tests" / "conformance" / "fixtures"


@dataclass(frozen=True, slots=True)
class _RuntimeHostSpec:
    cli_module: str
    fixture_path: Path
    rejection_input: str
    continuity_projection: tuple[dict[str, object], ...]
    rejection_projection: tuple[dict[str, object], ...]


_ZERO_FEEDBACK_WINDOW = {
    "window_size": 0,
    "rejection_count": 0,
    "override_count": 0,
    "latched_count": 0,
    "clean_success_streak": 0,
    "goal_progress_floor": 0.0,
    "degradation_pressure_bonus": 0,
    "sustained_spike_flags": [],
}
_FIRST_FEEDBACK_WINDOW = {
    "window_size": 1,
    "rejection_count": 0,
    "override_count": 0,
    "latched_count": 0,
    "clean_success_streak": 0,
    "goal_progress_floor": 0.0,
    "degradation_pressure_bonus": 0,
    "sustained_spike_flags": [],
}
_SECOND_FEEDBACK_WINDOW = {
    "window_size": 2,
    "rejection_count": 0,
    "override_count": 0,
    "latched_count": 0,
    "clean_success_streak": 0,
    "goal_progress_floor": 0.0,
    "degradation_pressure_bonus": 0,
    "sustained_spike_flags": [],
}
_THIRD_FEEDBACK_WINDOW = {
    "window_size": 3,
    "rejection_count": 0,
    "override_count": 0,
    "latched_count": 0,
    "clean_success_streak": 0,
    "goal_progress_floor": 0.0,
    "degradation_pressure_bonus": 0,
    "sustained_spike_flags": [],
}


_HOSTS: dict[str, _RuntimeHostSpec] = {
    "openai": _RuntimeHostSpec(
        cli_module="cortex.hosts.openai.cli",
        fixture_path=FIXTURE_DIR / "openai_runtime_continuity_session.jsonl",
        rejection_input="\n".join(
            (
                '{"event_name":"response.output_text.delta","payload":{"session_id":"oa-shared-law","response_id":"oa-shared-law-1","branch_operation":"open","branch_track_ref":"branch-alpha","delta":"open"}}',
                '{"event_name":"response.output_text.delta","payload":{"session_id":"oa-shared-law","response_id":"oa-shared-law-1","branch_operation":"resume","branch_track_ref":"branch-alpha","delta":"resume"}}',
            )
        )
        + "\n",
        continuity_projection=(
            {
                "selected_family": "seek-context",
                "realized_family": "seek-context",
                "brake_state": "guarded",
                "continuity_warnings": [],
                "active_track_ref": "branch-alpha",
                "pending_goal_refs": [],
                "feedback_window_summary": _ZERO_FEEDBACK_WINDOW,
                "closure_required": False,
                "closure_reason_tags": [],
            },
            {
                "selected_family": "seek-context",
                "realized_family": "seek-context",
                "brake_state": "guarded",
                "continuity_warnings": ["continuity-debt:pending-goals"],
                "active_track_ref": "main",
                "pending_goal_refs": ["branch-alpha"],
                "feedback_window_summary": _FIRST_FEEDBACK_WINDOW,
                "closure_required": True,
                "closure_reason_tags": ["pending_goal_debt"],
            },
            {
                "selected_family": "seek-context",
                "realized_family": "seek-context",
                "brake_state": "guarded",
                "continuity_warnings": [],
                "active_track_ref": "branch-alpha",
                "pending_goal_refs": [],
                "feedback_window_summary": _SECOND_FEEDBACK_WINDOW,
                "closure_required": False,
                "closure_reason_tags": [],
            },
            {
                "selected_family": "seek-context",
                "realized_family": "seek-context",
                "brake_state": "guarded",
                "continuity_warnings": [],
                "active_track_ref": "main",
                "pending_goal_refs": [],
                "feedback_window_summary": _THIRD_FEEDBACK_WINDOW,
                "closure_required": False,
                "closure_reason_tags": [],
            },
        ),
        rejection_projection=(
            {
                "selected_family": "seek-context",
                "realized_family": "seek-context",
                "brake_state": "guarded",
                "continuity_warnings": [],
                "active_track_ref": "branch-alpha",
                "pending_goal_refs": [],
                "feedback_window_summary": _ZERO_FEEDBACK_WINDOW,
                "closure_required": False,
                "closure_reason_tags": [],
            },
            {
                "selected_family": "seek-context",
                "realized_family": "seek-context",
                "brake_state": "guarded",
                "continuity_warnings": [
                    "continuity-rejected:missing-resume-anchor:branch-alpha"
                ],
                "active_track_ref": "branch-alpha",
                "pending_goal_refs": [],
                "feedback_window_summary": _FIRST_FEEDBACK_WINDOW,
                "closure_required": True,
                "closure_reason_tags": [
                    "continuity_rejection",
                    "continuity_reminder",
                ],
            },
        ),
    ),
    "claude": _RuntimeHostSpec(
        cli_module="cortex.hosts.claude.cli",
        fixture_path=FIXTURE_DIR / "claude_runtime_continuity_session.jsonl",
        rejection_input="\n".join(
            (
                '{"event_name":"content_block_delta","payload":{"session_id":"cl-shared-law","message_id":"cl-shared-law-1","branch_operation":"open","branch_track_ref":"branch-alpha","delta":"open"}}',
                '{"event_name":"content_block_delta","payload":{"session_id":"cl-shared-law","message_id":"cl-shared-law-1","branch_operation":"resume","branch_track_ref":"branch-alpha","delta":"resume"}}',
            )
        )
        + "\n",
        continuity_projection=(
            {
                "selected_family": "seek-context",
                "realized_family": "seek-context",
                "brake_state": "guarded",
                "continuity_warnings": [],
                "active_track_ref": "branch-alpha",
                "pending_goal_refs": [],
                "feedback_window_summary": _ZERO_FEEDBACK_WINDOW,
                "closure_required": False,
                "closure_reason_tags": [],
            },
            {
                "selected_family": "seek-context",
                "realized_family": "seek-context",
                "brake_state": "guarded",
                "continuity_warnings": [],
                "active_track_ref": "main",
                "pending_goal_refs": ["branch-alpha"],
                "feedback_window_summary": _FIRST_FEEDBACK_WINDOW,
                "closure_required": True,
                "closure_reason_tags": ["pending_goal_debt"],
            },
            {
                "selected_family": "seek-context",
                "realized_family": "seek-context",
                "brake_state": "guarded",
                "continuity_warnings": [],
                "active_track_ref": "branch-alpha",
                "pending_goal_refs": [],
                "feedback_window_summary": _SECOND_FEEDBACK_WINDOW,
                "closure_required": False,
                "closure_reason_tags": [],
            },
            {
                "selected_family": "seek-context",
                "realized_family": "seek-context",
                "brake_state": "guarded",
                "continuity_warnings": [],
                "active_track_ref": "main",
                "pending_goal_refs": [],
                "feedback_window_summary": _THIRD_FEEDBACK_WINDOW,
                "closure_required": False,
                "closure_reason_tags": [],
            },
        ),
        rejection_projection=(
            {
                "selected_family": "seek-context",
                "realized_family": "seek-context",
                "brake_state": "guarded",
                "continuity_warnings": [],
                "active_track_ref": "branch-alpha",
                "pending_goal_refs": [],
                "feedback_window_summary": _ZERO_FEEDBACK_WINDOW,
                "closure_required": False,
                "closure_reason_tags": [],
            },
            {
                "selected_family": "seek-context",
                "realized_family": "seek-context",
                "brake_state": "guarded",
                "continuity_warnings": [
                    "continuity-rejected:missing-resume-anchor:branch-alpha"
                ],
                "active_track_ref": "branch-alpha",
                "pending_goal_refs": [],
                "feedback_window_summary": _FIRST_FEEDBACK_WINDOW,
                "closure_required": True,
                "closure_reason_tags": [
                    "continuity_rejection",
                    "continuity_reminder",
                ],
            },
        ),
    ),
    "gemini": _RuntimeHostSpec(
        cli_module="cortex.hosts.gemini.cli",
        fixture_path=FIXTURE_DIR / "gemini_runtime_continuity_session.jsonl",
        rejection_input="\n".join(
            (
                '{"event_name":"content.delta","payload":{"session_id":"gm-shared-law","interaction_id":"gm-shared-law-1","branch_operation":"open","branch_track_ref":"branch-alpha","delta":"open"}}',
                '{"event_name":"content.delta","payload":{"session_id":"gm-shared-law","interaction_id":"gm-shared-law-1","branch_operation":"resume","branch_track_ref":"branch-alpha","delta":"resume"}}',
            )
        )
        + "\n",
        continuity_projection=(
            {
                "selected_family": "seek-context",
                "realized_family": "seek-context",
                "brake_state": "guarded",
                "continuity_warnings": [],
                "active_track_ref": "branch-alpha",
                "pending_goal_refs": [],
                "feedback_window_summary": _ZERO_FEEDBACK_WINDOW,
                "closure_required": False,
                "closure_reason_tags": [],
            },
            {
                "selected_family": "seek-context",
                "realized_family": "seek-context",
                "brake_state": "guarded",
                "continuity_warnings": [],
                "active_track_ref": "main",
                "pending_goal_refs": ["branch-alpha"],
                "feedback_window_summary": _FIRST_FEEDBACK_WINDOW,
                "closure_required": True,
                "closure_reason_tags": ["pending_goal_debt"],
            },
            {
                "selected_family": "seek-context",
                "realized_family": "seek-context",
                "brake_state": "guarded",
                "continuity_warnings": [],
                "active_track_ref": "branch-alpha",
                "pending_goal_refs": [],
                "feedback_window_summary": _SECOND_FEEDBACK_WINDOW,
                "closure_required": False,
                "closure_reason_tags": [],
            },
            {
                "selected_family": "seek-context",
                "realized_family": "seek-context",
                "brake_state": "guarded",
                "continuity_warnings": [],
                "active_track_ref": "main",
                "pending_goal_refs": [],
                "feedback_window_summary": _THIRD_FEEDBACK_WINDOW,
                "closure_required": False,
                "closure_reason_tags": [],
            },
        ),
        rejection_projection=(
            {
                "selected_family": "seek-context",
                "realized_family": "seek-context",
                "brake_state": "guarded",
                "continuity_warnings": [],
                "active_track_ref": "branch-alpha",
                "pending_goal_refs": [],
                "feedback_window_summary": _ZERO_FEEDBACK_WINDOW,
                "closure_required": False,
                "closure_reason_tags": [],
            },
            {
                "selected_family": "seek-context",
                "realized_family": "seek-context",
                "brake_state": "guarded",
                "continuity_warnings": [
                    "continuity-rejected:missing-resume-anchor:branch-alpha"
                ],
                "active_track_ref": "branch-alpha",
                "pending_goal_refs": [],
                "feedback_window_summary": _FIRST_FEEDBACK_WINDOW,
                "closure_required": True,
                "closure_reason_tags": [
                    "continuity_rejection",
                    "continuity_reminder",
                ],
            },
        ),
    ),
    "reference": _RuntimeHostSpec(
        cli_module="cortex.hosts.reference.cli",
        fixture_path=FIXTURE_DIR / "reference_runtime_continuity_session.jsonl",
        rejection_input="\n".join(
            (
                '{"event_name":"ContextLoad","payload":{"session_id":"ref-shared-law","branch_operation":"open","branch_track_ref":"branch-alpha"}}',
                '{"event_name":"ContextLoad","payload":{"session_id":"ref-shared-law","branch_operation":"resume","branch_track_ref":"branch-alpha"}}',
            )
        )
        + "\n",
        continuity_projection=(
            {
                "selected_family": "seek-context",
                "realized_family": "seek-context",
                "brake_state": "guarded",
                "continuity_warnings": [],
                "active_track_ref": "branch-alpha",
                "pending_goal_refs": [],
                "feedback_window_summary": _ZERO_FEEDBACK_WINDOW,
                "closure_required": False,
                "closure_reason_tags": [],
            },
            {
                "selected_family": "seek-context",
                "realized_family": "seek-context",
                "brake_state": "guarded",
                "continuity_warnings": [],
                "active_track_ref": "main",
                "pending_goal_refs": ["branch-alpha"],
                "feedback_window_summary": _FIRST_FEEDBACK_WINDOW,
                "closure_required": True,
                "closure_reason_tags": ["pending_goal_debt"],
            },
            {
                "selected_family": "seek-context",
                "realized_family": "seek-context",
                "brake_state": "guarded",
                "continuity_warnings": [],
                "active_track_ref": "branch-alpha",
                "pending_goal_refs": [],
                "feedback_window_summary": _SECOND_FEEDBACK_WINDOW,
                "closure_required": False,
                "closure_reason_tags": [],
            },
            {
                "selected_family": "seek-context",
                "realized_family": "seek-context",
                "brake_state": "guarded",
                "continuity_warnings": [],
                "active_track_ref": "main",
                "pending_goal_refs": [],
                "feedback_window_summary": _THIRD_FEEDBACK_WINDOW,
                "closure_required": False,
                "closure_reason_tags": [],
            },
        ),
        rejection_projection=(
            {
                "selected_family": "seek-context",
                "realized_family": "seek-context",
                "brake_state": "guarded",
                "continuity_warnings": [],
                "active_track_ref": "branch-alpha",
                "pending_goal_refs": [],
                "feedback_window_summary": _ZERO_FEEDBACK_WINDOW,
                "closure_required": False,
                "closure_reason_tags": [],
            },
            {
                "selected_family": "seek-context",
                "realized_family": "seek-context",
                "brake_state": "guarded",
                "continuity_warnings": [
                    "continuity-rejected:missing-resume-anchor:branch-alpha"
                ],
                "active_track_ref": "branch-alpha",
                "pending_goal_refs": [],
                "feedback_window_summary": _FIRST_FEEDBACK_WINDOW,
                "closure_required": True,
                "closure_reason_tags": [
                    "continuity_rejection",
                    "continuity_reminder",
                ],
            },
        ),
    ),
}


def test_runtime_continuity_fixtures_lock_shared_session_truth_and_host_control_projection() -> None:
    projected = {
        host_name: _project_records(
            _run_cli(
                spec.cli_module,
                "--event-file",
                str(spec.fixture_path),
            )
        )
        for host_name, spec in _HOSTS.items()
    }

    reference_truth = [
        {
                "active_track_ref": record["active_track_ref"],
                "pending_goal_refs": record["pending_goal_refs"],
                "feedback_window_summary": record["feedback_window_summary"],
                "closure_required": record["closure_required"],
                "closure_reason_tags": record["closure_reason_tags"],
            }
            for record in _HOSTS["reference"].continuity_projection
        ]
    for host_name, records in projected.items():
        assert records == list(_HOSTS[host_name].continuity_projection)
        assert [
            {
                "active_track_ref": record["active_track_ref"],
                "pending_goal_refs": record["pending_goal_refs"],
                "feedback_window_summary": record["feedback_window_summary"],
                "closure_required": record["closure_required"],
                "closure_reason_tags": record["closure_reason_tags"],
            }
            for record in records
        ] == reference_truth


def test_runtime_continuity_missing_resume_anchor_lock_preserves_cross_host_rejection_law() -> None:
    projected = {
        host_name: _project_records(
            _run_cli(spec.cli_module, input_text=spec.rejection_input)
        )
        for host_name, spec in _HOSTS.items()
    }

    reference_rejections = [
        record["continuity_warnings"]
        for record in _HOSTS["reference"].rejection_projection
    ]
    reference_truth = [
        {
                "active_track_ref": record["active_track_ref"],
                "pending_goal_refs": record["pending_goal_refs"],
                "feedback_window_summary": record["feedback_window_summary"],
                "closure_required": record["closure_required"],
                "closure_reason_tags": record["closure_reason_tags"],
            }
            for record in _HOSTS["reference"].rejection_projection
        ]
    for host_name, records in projected.items():
        assert records == list(_HOSTS[host_name].rejection_projection)
        assert [record["continuity_warnings"] for record in records] == reference_rejections
        assert [
            {
                "active_track_ref": record["active_track_ref"],
                "pending_goal_refs": record["pending_goal_refs"],
                "feedback_window_summary": record["feedback_window_summary"],
                "closure_required": record["closure_required"],
                "closure_reason_tags": record["closure_reason_tags"],
            }
            for record in records
        ] == reference_truth


def _run_cli(
    cli_module: str,
    *args: str,
    input_text: str | None = None,
) -> list[dict[str, object]]:
    completed = subprocess.run(
        [sys.executable, "-m", cli_module, *args],
        cwd=REPO_ROOT,
        input=input_text,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    return [json.loads(line) for line in completed.stdout.splitlines() if line.strip()]


def _project_records(records: list[dict[str, object]]) -> list[dict[str, object]]:
    return [_project_record(record) for record in records]


def _project_record(record: dict[str, object]) -> dict[str, object]:
    session_summary = record.get("journal") or record.get("session_summary")
    assert isinstance(session_summary, dict)
    warnings = record["warnings"]
    assert isinstance(warnings, list)
    continuity_warnings = [
        warning for warning in warnings if isinstance(warning, str) and warning.startswith("continuity-")
    ]
    control_ledger = record["control_ledger"]
    assert isinstance(control_ledger, dict)
    return {
        "selected_family": record["selected_family"],
        "realized_family": control_ledger["realized_family"],
        "brake_state": record["brake_state"],
        "continuity_warnings": continuity_warnings,
        "active_track_ref": session_summary["active_track_ref"],
        "pending_goal_refs": session_summary["pending_goal_refs"],
        "feedback_window_summary": record["feedback_window_summary"],
        "closure_required": record["closure_required"],
        "closure_reason_tags": record["closure_reason_tags"],
    }
