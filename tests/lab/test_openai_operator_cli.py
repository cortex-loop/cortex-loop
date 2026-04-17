from __future__ import annotations

from pathlib import Path

from lab import openai_operator_cli


def test_run_openai_operator_single_turn_uses_codex_exec_and_extracts_result(monkeypatch, tmp_path: Path) -> None:
    recorded: dict[str, object] = {}

    def _fake_run_command(command, *, cwd=None, env=None, timeout_seconds=0.0):
        recorded["command"] = command
        recorded["cwd"] = cwd
        recorded["env"] = env
        recorded["timeout_seconds"] = timeout_seconds
        return {
            "command": command,
            "exit_code": 0,
            "stdout": (
                '{"type":"result","session_id":"sess-123","result":"=== FILE: src/app.py ===\\npass\\n=== END FILE ==="}\n'
            ),
            "stderr": "",
            "started_at": "2026-04-17T00:00:00+00:00",
            "ended_at": "2026-04-17T00:00:01+00:00",
        }

    monkeypatch.setattr(openai_operator_cli, "run_command", _fake_run_command)

    result = openai_operator_cli.run_openai_operator_single_turn(
        project_root=tmp_path,
        prompt="Fix the file",
        scenario_id="smoke",
        stderr_path=tmp_path / "operator.stderr.log",
        env={"CODEX_HOME": "/tmp/codex-home"},
        model="gpt-5.3-codex-spark",
    )

    assert recorded["command"] == [
        "codex",
        "exec",
        "--json",
        "--full-auto",
        "--skip-git-repo-check",
        "-m",
        "gpt-5.3-codex-spark",
        "Fix the file",
    ]
    assert recorded["cwd"] == tmp_path
    assert recorded["env"] == {"CODEX_HOME": "/tmp/codex-home"}
    assert result["failure_class"] is None
    assert result["thread_id"] == "sess-123"
    assert result["output_text"] == "=== FILE: src/app.py ===\npass\n=== END FILE ==="


def test_run_openai_operator_resumed_turn_uses_codex_resume(monkeypatch, tmp_path: Path) -> None:
    recorded: dict[str, object] = {}

    def _fake_run_command(command, *, cwd=None, env=None, timeout_seconds=0.0):
        recorded["command"] = command
        return {
            "command": command,
            "exit_code": 0,
            "stdout": '{"type":"result","session_id":"sess-123","result":"done"}\n',
            "stderr": "",
            "started_at": "2026-04-17T00:00:00+00:00",
            "ended_at": "2026-04-17T00:00:01+00:00",
        }

    monkeypatch.setattr(openai_operator_cli, "run_command", _fake_run_command)

    result = openai_operator_cli.run_openai_operator_resumed_turn(
        project_root=tmp_path,
        prompt="Repair it",
        model="gpt-5.3-codex-spark",
        thread_id="sess-123",
        stderr_path=tmp_path / "operator.stderr.log",
    )

    assert recorded["command"] == [
        "codex",
        "exec",
        "resume",
        "--json",
        "--full-auto",
        "sess-123",
        "Repair it",
    ]
    assert result["failure_class"] is None
    assert result["thread_id"] == "sess-123"
    assert result["output_text"] == "done"
