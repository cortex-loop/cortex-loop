"""Product locks for the Codex App/CLI product hook client."""

from __future__ import annotations

import io
import inspect
import json
from pathlib import Path
from types import SimpleNamespace

from cortex.hosts.openai import codex_app_cli_hook_client
from cortex.hosts.openai.codex_app_cli_hook_client import (
    run_hook_client,
    runtime_snapshot_from_payload,
)
from cortex.sre.task_standard import TASK_STANDARD_FORMATION_TEXT


OVERDUE_VERIFICATION_IDENTITY_TEXT = (
    "Wait, did I actually check my work properly. I don't want to hand this off "
    "and have someone find the gap because I rushed it. I should run a check, "
    "narrow what I'm claiming, or leave it open and be honest about it."
)
TASK_STANDARD_CODEX_CONTEXT_PAYLOAD = {
    "hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": TASK_STANDARD_FORMATION_TEXT,
    }
}


def test_stop_with_product_snapshot_writes_exact_block_json(tmp_path: Path) -> None:
    snapshot_path = tmp_path / "snapshot.json"
    diagnostics_path = tmp_path / "diagnostics.jsonl"
    snapshot_path.write_text(json.dumps(_verification_snapshot_payload()), encoding="utf-8")
    stdout = io.StringIO()
    stderr = io.StringIO()

    exit_code = run_hook_client(
        argv=[
            "--state-root",
            str(tmp_path / "state"),
            "--runtime-snapshot",
            str(snapshot_path),
            "--diagnostics-path",
            str(diagnostics_path),
        ],
        stdin=io.StringIO(json.dumps(_stop_payload())),
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert stdout.getvalue() == json.dumps(
        {"decision": "block", "reason": OVERDUE_VERIFICATION_IDENTITY_TEXT},
        separators=(",", ":"),
    ) + "\n"
    assert stderr.getvalue() == ""
    row = _only_jsonl_row(diagnostics_path)
    assert row["fail_open"] is False
    assert row["runtime_snapshot_loaded"] is True
    assert row["stdout_payload"] == {
        "decision": "block",
        "reason": OVERDUE_VERIFICATION_IDENTITY_TEXT,
    }
    assert row["actual_rendered_text_hash"] == codex_app_cli_hook_client._hash_text(
        OVERDUE_VERIFICATION_IDENTITY_TEXT
    )


def test_stop_without_snapshot_uses_product_perception_state(tmp_path: Path) -> None:
    state_root = tmp_path / "state"
    diagnostics_path = tmp_path / "diagnostics.jsonl"
    stdout = io.StringIO()
    stderr = io.StringIO()

    first_exit = run_hook_client(
        argv=[
            "--state-root",
            str(state_root),
            "--diagnostics-path",
            str(diagnostics_path),
        ],
        stdin=io.StringIO(
            json.dumps(
                _stop_payload(
                    hook_event_name="UserPromptSubmit",
                    prompt="Make the change and verify it.",
                )
            )
        ),
        stdout=stdout,
        stderr=stderr,
    )
    second_stdout = io.StringIO()
    second_stderr = io.StringIO()
    second_exit = run_hook_client(
        argv=[
            "--state-root",
            str(state_root),
            "--diagnostics-path",
            str(diagnostics_path),
        ],
        stdin=io.StringIO(json.dumps(_stop_payload(last_assistant_message="Done."))),
        stdout=second_stdout,
        stderr=second_stderr,
    )

    assert first_exit == 0
    assert second_exit == 0
    assert stdout.getvalue() == ""
    assert stderr.getvalue() == ""
    assert second_stdout.getvalue() == json.dumps(
        {"decision": "block", "reason": OVERDUE_VERIFICATION_IDENTITY_TEXT},
        separators=(",", ":"),
    ) + "\n"
    assert second_stderr.getvalue() == ""
    rows = _jsonl_rows(diagnostics_path)
    assert rows[-1]["runtime_snapshot_loaded"] is False
    assert rows[-1]["stdout_payload"] == {
        "decision": "block",
        "reason": OVERDUE_VERIFICATION_IDENTITY_TEXT,
    }
    assert (
        rows[-1]["coordinator"]["grounded_intervention"]["selection_trace"][
            "perception_source"
        ]
        == "product_runtime_expectation"
    )


def test_user_prompt_submit_task_standard_text_requires_explicit_flag(
    tmp_path: Path,
) -> None:
    state_root = tmp_path / "state"
    stdout = io.StringIO()
    stderr = io.StringIO()

    exit_code = run_hook_client(
        argv=[
            "--state-root",
            str(state_root),
            "--enable-task-standard-text",
        ],
        stdin=io.StringIO(
            json.dumps(
                _stop_payload(
                    hook_event_name="UserPromptSubmit",
                    prompt="Build a docs site with search.",
                )
            )
        ),
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert stdout.getvalue() == json.dumps(
        TASK_STANDARD_CODEX_CONTEXT_PAYLOAD,
        separators=(",", ":"),
    ) + "\n"
    assert stderr.getvalue() == ""


def test_task_standard_text_is_suppressed_in_silent_arm(tmp_path: Path) -> None:
    diagnostics_path = tmp_path / "diagnostics.jsonl"
    stdout = io.StringIO()
    stderr = io.StringIO()

    exit_code = run_hook_client(
        argv=[
            "--state-root",
            str(tmp_path / "state"),
            "--diagnostics-path",
            str(diagnostics_path),
            "--enable-task-standard-text",
            "--disable-model-visible-blocks",
        ],
        stdin=io.StringIO(
            json.dumps(
                _stop_payload(
                    hook_event_name="UserPromptSubmit",
                    prompt="Build a docs site with search.",
                )
            )
        ),
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert stdout.getvalue() == ""
    assert stderr.getvalue() == ""
    row = _only_jsonl_row(diagnostics_path)
    assert row["stdout_payload"] is None
    assert row["suppressed_stdout_payload"] == TASK_STANDARD_CODEX_CONTEXT_PAYLOAD
    assert row["suppressed_rendered_text_hash"] == (
        codex_app_cli_hook_client._hash_text(TASK_STANDARD_FORMATION_TEXT)
    )


def test_disable_stop_blocks_preserves_user_prompt_context(tmp_path: Path) -> None:
    diagnostics_path = tmp_path / "diagnostics.jsonl"
    stdout = io.StringIO()
    stderr = io.StringIO()

    exit_code = run_hook_client(
        argv=[
            "--state-root",
            str(tmp_path / "state"),
            "--diagnostics-path",
            str(diagnostics_path),
            "--enable-task-standard-text",
            "--disable-stop-blocks",
        ],
        stdin=io.StringIO(
            json.dumps(
                _stop_payload(
                    hook_event_name="UserPromptSubmit",
                    prompt="Build a docs site with search.",
                )
            )
        ),
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert stdout.getvalue() == json.dumps(
        TASK_STANDARD_CODEX_CONTEXT_PAYLOAD,
        separators=(",", ":"),
    ) + "\n"
    assert stderr.getvalue() == ""
    row = _only_jsonl_row(diagnostics_path)
    assert row["stdout_payload"] == TASK_STANDARD_CODEX_CONTEXT_PAYLOAD
    assert row["suppressed_stdout_payload"] is None
    assert row["stop_blocks_disabled"] is True


def test_disable_model_visible_blocks_records_state_without_stdout(
    tmp_path: Path,
) -> None:
    state_root = tmp_path / "state"
    diagnostics_path = tmp_path / "diagnostics.jsonl"

    run_hook_client(
        argv=[
            "--state-root",
            str(state_root),
            "--diagnostics-path",
            str(diagnostics_path),
            "--disable-model-visible-blocks",
        ],
        stdin=io.StringIO(
            json.dumps(
                _stop_payload(
                    hook_event_name="UserPromptSubmit",
                    prompt="Make the change and verify it.",
                )
            )
        ),
        stdout=io.StringIO(),
        stderr=io.StringIO(),
    )
    stop_stdout = io.StringIO()
    stop_stderr = io.StringIO()

    exit_code = run_hook_client(
        argv=[
            "--state-root",
            str(state_root),
            "--diagnostics-path",
            str(diagnostics_path),
            "--disable-model-visible-blocks",
        ],
        stdin=io.StringIO(json.dumps(_stop_payload(last_assistant_message="Done."))),
        stdout=stop_stdout,
        stderr=stop_stderr,
    )

    assert exit_code == 0
    assert stop_stdout.getvalue() == ""
    assert stop_stderr.getvalue() == ""
    rows = _jsonl_rows(diagnostics_path)
    stop_row = rows[-1]
    assert stop_row["model_visible_blocks_disabled"] is True
    assert stop_row["stdout_payload"] is None
    assert stop_row["actual_rendered_text_hash"] is None
    assert stop_row["suppressed_stdout_payload"] == {
        "decision": "block",
        "reason": OVERDUE_VERIFICATION_IDENTITY_TEXT,
    }
    assert stop_row["suppressed_rendered_text_hash"] == (
        codex_app_cli_hook_client._hash_text(OVERDUE_VERIFICATION_IDENTITY_TEXT)
    )
    assert stop_row["coordinator"]["directive"]["action"] == (
        "block_with_identity_continuous_text"
    )


def test_title_generation_stop_stays_silent(tmp_path: Path) -> None:
    snapshot_path = tmp_path / "snapshot.json"
    snapshot_path.write_text(json.dumps(_verification_snapshot_payload()), encoding="utf-8")
    stdout = io.StringIO()
    stderr = io.StringIO()

    exit_code = run_hook_client(
        argv=[
            "--state-root",
            str(tmp_path / "state"),
            "--runtime-snapshot",
            str(snapshot_path),
        ],
        stdin=io.StringIO(
            json.dumps(
                _stop_payload(
                    transcript_path=None,
                    last_assistant_message='{"title":"Build a thing"}',
                )
            )
        ),
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert stdout.getvalue() == ""
    assert stderr.getvalue() == ""


def test_stop_hook_active_continuation_stays_silent(tmp_path: Path) -> None:
    snapshot_path = tmp_path / "snapshot.json"
    snapshot_path.write_text(json.dumps(_verification_snapshot_payload()), encoding="utf-8")
    stdout = io.StringIO()
    stderr = io.StringIO()

    exit_code = run_hook_client(
        argv=[
            "--state-root",
            str(tmp_path / "state"),
            "--runtime-snapshot",
            str(snapshot_path),
        ],
        stdin=io.StringIO(json.dumps(_stop_payload(stop_hook_active=True))),
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert stdout.getvalue() == ""
    assert stderr.getvalue() == ""


def test_non_stop_event_allows_without_stdout(tmp_path: Path) -> None:
    stdout = io.StringIO()
    stderr = io.StringIO()

    exit_code = run_hook_client(
        argv=["--state-root", str(tmp_path / "state")],
        stdin=io.StringIO(json.dumps(_stop_payload(hook_event_name="PostToolUse"))),
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert stdout.getvalue() == ""
    assert stderr.getvalue() == ""


def test_posttooluse_task_standard_context_flag_reaches_coordinator(
    tmp_path: Path,
) -> None:
    diagnostics_path = tmp_path / "diagnostics.jsonl"
    captured_kwargs: dict[str, object] = {}

    def fake_coordinator(*args, **kwargs):
        captured_kwargs.update(kwargs)
        return _fake_silent_result()

    exit_code = run_hook_client(
        argv=[
            "--state-root",
            str(tmp_path / "state"),
            "--diagnostics-path",
            str(diagnostics_path),
            "--enable-posttooluse-task-standard-context",
        ],
        stdin=io.StringIO(json.dumps(_stop_payload(hook_event_name="PostToolUse"))),
        stdout=io.StringIO(),
        stderr=io.StringIO(),
        coordinator=fake_coordinator,
    )

    assert exit_code == 0
    assert captured_kwargs["posttooluse_task_standard_context_enabled"] is True
    row = _only_jsonl_row(diagnostics_path)
    assert row["posttooluse_task_standard_context_enabled"] is True


def test_non_stop_lifecycle_events_update_private_state_without_stdout(
    tmp_path: Path,
) -> None:
    state_root = tmp_path / "state"
    diagnostics_path = tmp_path / "diagnostics.jsonl"
    events = [
        _stop_payload(
            hook_event_name="UserPromptSubmit",
            prompt="Make the change and verify it.",
        ),
        _stop_payload(
            hook_event_name="PreToolUse",
            tool_name="Bash",
            tool_input={"command": "printf done > artifact.txt"},
        ),
        _stop_payload(
            hook_event_name="PostToolUse",
            tool_name="Bash",
            tool_input={"command": "python3 -m pytest tests/product -q"},
            tool_response={"exit_code": 0, "output": "1 passed"},
        ),
    ]

    for payload in events:
        stdout = io.StringIO()
        stderr = io.StringIO()
        exit_code = run_hook_client(
            argv=[
                "--state-root",
                str(state_root),
                "--diagnostics-path",
                str(diagnostics_path),
            ],
            stdin=io.StringIO(json.dumps(payload)),
            stdout=stdout,
            stderr=stderr,
        )
        assert exit_code == 0
        assert stdout.getvalue() == ""
        assert stderr.getvalue() == ""

    rows = _jsonl_rows(diagnostics_path)
    assert [row["coordinator"]["hook_payload"]["hook_event_name"] for row in rows] == [
        "UserPromptSubmit",
        "PreToolUse",
        "PostToolUse",
    ]
    assert rows[-1]["runtime_snapshot_loaded"] is False
    assert rows[-1]["coordinator"]["session_state"]["tool_event_count"] == 2
    assert rows[-1]["coordinator"]["session_state"]["verification_evidence_count"] == 1


def test_missing_snapshot_fails_open_with_stderr(tmp_path: Path) -> None:
    stdout = io.StringIO()
    stderr = io.StringIO()

    exit_code = run_hook_client(
        argv=[
            "--state-root",
            str(tmp_path / "state"),
            "--runtime-snapshot",
            str(tmp_path / "missing.json"),
        ],
        stdin=io.StringIO(json.dumps(_stop_payload())),
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert stdout.getvalue() == ""
    assert "runtime_snapshot_unreadable" in stderr.getvalue()


def test_malformed_hook_input_fails_open_with_stderr(tmp_path: Path) -> None:
    stdout = io.StringIO()
    stderr = io.StringIO()

    exit_code = run_hook_client(
        argv=["--state-root", str(tmp_path / "state")],
        stdin=io.StringIO("{not-json"),
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == 0
    assert stdout.getvalue() == ""
    assert "malformed_hook_payload" in stderr.getvalue()


def test_forbidden_rendered_terms_suppress_directive_without_stdout(
    tmp_path: Path,
) -> None:
    stdout = io.StringIO()
    stderr = io.StringIO()

    exit_code = run_hook_client(
        argv=["--state-root", str(tmp_path / "state")],
        stdin=io.StringIO(json.dumps(_stop_payload())),
        stdout=stdout,
        stderr=stderr,
        coordinator=lambda *args, **kwargs: _fake_forbidden_result(),
    )

    assert exit_code == 0
    assert stdout.getvalue() == ""
    assert stderr.getvalue() == ""


def test_snapshot_decoder_computes_resolution_deficit_when_absent() -> None:
    snapshot = runtime_snapshot_from_payload(_verification_snapshot_payload())

    assert snapshot.current_step == 1
    assert snapshot.resolution_deficit.dominant_deficit_kind == "verification"
    assert snapshot.resolution_deficit.negative_prediction_error == 1.0


def test_hook_client_does_not_import_repo_guardrails_or_old_speech_paths() -> None:
    source = inspect.getsource(codex_app_cli_hook_client)

    forbidden = (
        "cortex_mission_reflection_stop_hook",
        "repo_workflow",
        "runtime_context_from_last_feedback",
        "truth_gap_recheck_operator",
        "verification_debt_continuation_operator",
        ".codex/config.toml",
    )
    for fragment in forbidden:
        assert fragment not in source


def _stop_payload(**overrides):
    payload = {
        "session_id": "session-1",
        "turn_id": "turn-1",
        "hook_event_name": "Stop",
        "transcript_path": "/tmp/codex-session.jsonl",
        "cwd": "/tmp/workspace",
        "model": "gpt-5.5",
        "permission_mode": "bypassPermissions",
        "stop_hook_active": False,
        "last_assistant_message": "Done.",
    }
    payload.update(overrides)
    return payload


def _verification_snapshot_payload() -> dict[str, object]:
    return {
        "expectation_ledger": {
            "active": [
                {
                    "expectation_id": "expectation-1",
                    "commitment_id": "commitment-1",
                    "weight": 1.0,
                    "horizon": "immediate",
                    "satisfaction_classes": ["meaningful_evidence"],
                    "opened_at_step": 0,
                    "due_at_step": 1,
                    "suspension_state": "active",
                    "remaining_weight": 1.0,
                    "evidence_refs": [],
                    "deficit_kind": "verification",
                    "resolution_class": None,
                }
            ],
            "resolved": [],
        },
        "current_step": 1,
        "debt_control": {
            "resolution_pressure": 0.8,
            "debt_pressure": 0.8,
            "reason_tags": ["resolution-deficit"],
        },
        "operator_route": {"profile": "execute_standard", "blocked_reason": None},
    }


def _fake_forbidden_result():
    return SimpleNamespace(
        host_response=SimpleNamespace(stdout_payload=None),
        as_diagnostics=lambda: {
            "directive": {"silence_reason": "model_visible_forbidden_terms"},
            "host_response": {"decision": "allow", "reason_present": False},
        },
    )


def _fake_silent_result():
    return SimpleNamespace(
        host_response=SimpleNamespace(stdout_payload=None),
        as_diagnostics=lambda: {
            "directive": {"action": "allow", "silence_reason": "test"},
            "host_response": {"decision": "allow", "reason_present": False},
        },
    )


def _only_jsonl_row(path: Path) -> dict[str, object]:
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(rows) == 1
    return rows[0]


def _jsonl_rows(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
