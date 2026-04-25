from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from lab import v2_subscription_cli_preflight


def test_subscription_cli_preflight_classifies_no_api_spend_lanes() -> None:
    payload = v2_subscription_cli_preflight.build_subscription_cli_preflight(
        command_runner=_fake_runner,
        env={},
    )

    assert payload["spend_state"] == "subscription_cli_no_api_spend"
    assert payload["ready_for_live_watchlist"] is True
    assert payload["claude_cli"]["subscription_no_api_spend"] is True
    assert payload["claude_cli"]["auth_method"] == "claude.ai"
    assert payload["codex_cli"]["subscription_no_api_spend"] is True
    assert payload["codex_cli"]["logged_in_chatgpt"] is True
    assert payload["api_key_env_present"]["ANTHROPIC_API_KEY"] is False
    assert payload["api_key_env_present"]["OPENAI_API_KEY"] is False


def test_subscription_cli_preflight_blocks_api_key_env() -> None:
    payload = v2_subscription_cli_preflight.build_subscription_cli_preflight(
        command_runner=_fake_runner,
        env={"OPENAI_API_KEY": "present"},
    )

    assert payload["ready_for_live_watchlist"] is False
    assert payload["api_key_env_present"]["OPENAI_API_KEY"] is True


def test_subscription_cli_preflight_smoke_uses_non_api_cli_commands() -> None:
    payload = v2_subscription_cli_preflight.build_subscription_cli_preflight(
        run_smoke=True,
        command_runner=_fake_runner,
        env={},
    )

    assert payload["ready_for_live_watchlist"] is True
    assert payload["smoke"]["claude_cli"]["success"] is True
    assert payload["smoke"]["codex_cli"]["success"] is True
    assert payload["smoke"]["codex_cli"]["command"][:4] == [
        "codex",
        "-a",
        "never",
        "exec",
    ]


def test_subscription_cli_preflight_cli_writes_report(tmp_path: Path, monkeypatch) -> None:
    output = tmp_path / "preflight.json"
    monkeypatch.setattr(v2_subscription_cli_preflight, "run_command", _fake_runner)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("CORTEX_LIVE_SERVICE_SPEND_APPROVED", raising=False)

    assert v2_subscription_cli_preflight.main(["--output", str(output), "--smoke"]) == 0

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["ready_for_live_watchlist"] is True
    assert payload["smoke"]["codex_cli"]["marker_seen"] is True


def _fake_runner(command: list[str], **_: Any) -> dict[str, Any]:
    if command == ["claude", "auth", "status"]:
        stdout = json.dumps(
            {
                "loggedIn": True,
                "authMethod": "claude.ai",
                "apiProvider": "firstParty",
                "email": "private@example.com",
                "subscriptionType": "pro",
            }
        )
        return _result(command, stdout=stdout)
    if command == ["codex", "login", "status"]:
        return _result(command, stdout="Logged in using ChatGPT\n")
    if command and command[0] == "claude":
        return _result(
            command,
            stdout=json.dumps(
                {"result": v2_subscription_cli_preflight.SMOKE_MARKER}
            ),
        )
    if command and command[0] == "codex":
        return _result(
            command,
            stdout=(
                '{"type":"item.completed","item":{"text":"'
                + v2_subscription_cli_preflight.SMOKE_MARKER
                + '"}}\n'
            ),
        )
    raise AssertionError(f"unexpected command: {command!r}")


def _result(command: list[str], *, stdout: str = "", stderr: str = "") -> dict[str, Any]:
    return {
        "command": command,
        "exit_code": 0,
        "stdout": stdout,
        "stderr": stderr,
        "started_at": "2026-04-25T00:00:00+00:00",
        "ended_at": "2026-04-25T00:00:00+00:00",
    }
