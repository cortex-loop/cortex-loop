"""No-API-spend preflight for Claude/Codex subscription CLI lanes."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Callable, Mapping

from lab.agent_loop_guard import LOOP_GUARD_ROOT
from lab.live_validation_common import (
    REPO_ROOT,
    api_key_presence,
    now_utc_iso,
    redact_claude_auth_payload,
    run_command,
    write_json,
)


DEFAULT_PREFLIGHT_PATH = LOOP_GUARD_ROOT / "v2_subscription_cli_preflight.latest.json"
SMOKE_MARKER = "CORTEX_CLI_SMOKE_OK"
CommandRunner = Callable[..., dict[str, Any]]


def build_subscription_cli_preflight(
    *,
    run_smoke: bool = False,
    command_runner: CommandRunner | None = None,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    command_runner = command_runner or run_command
    env_source = os.environ if env is None else env
    api_keys = api_key_presence(env)
    claude = _claude_subscription_status(command_runner)
    codex = _codex_subscription_status(command_runner)
    payload: dict[str, Any] = {
        "surface": "lab",
        "evidence_role": "watchlist",
        "generated_at": now_utc_iso(),
        "spend_state": "subscription_cli_no_api_spend",
        "api_key_env_present": api_keys,
        "service_spend_opt_in_present": bool(
            env_source.get("CORTEX_LIVE_SERVICE_SPEND_APPROVED")
        ),
        "claude_cli": claude,
        "codex_cli": codex,
        "ready_for_live_watchlist": _ready_for_live_watchlist(
            claude=claude,
            codex=codex,
            api_keys=api_keys,
            service_spend_opt_in_present=bool(
                env_source.get("CORTEX_LIVE_SERVICE_SPEND_APPROVED")
            ),
        ),
        "smoke": None,
    }
    if run_smoke:
        smoke = {
            "claude_cli": _run_claude_smoke(command_runner),
            "codex_cli": _run_codex_smoke(command_runner),
        }
        payload["smoke"] = smoke
        payload["ready_for_live_watchlist"] = payload[
            "ready_for_live_watchlist"
        ] and all(result["success"] for result in smoke.values())
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 -m lab.v2_subscription_cli_preflight",
        description="Record Claude/Codex subscription CLI readiness without API spend.",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_PREFLIGHT_PATH)
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Run minimal non-editing Claude and Codex subscription CLI prompts.",
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    payload = build_subscription_cli_preflight(run_smoke=args.smoke)
    if args.check:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    write_json(args.output, payload)
    print(str(args.output))
    return 0


def _claude_subscription_status(command_runner: CommandRunner) -> dict[str, Any]:
    result = command_runner(["claude", "auth", "status"], timeout_seconds=30.0)
    payload: dict[str, Any] = {
        "command": result["command"],
        "exit_code": result["exit_code"],
        "available": result["exit_code"] == 0,
    }
    if result["exit_code"] != 0:
        payload["error"] = (result.get("stderr") or result.get("stdout") or "").strip()
        payload["subscription_no_api_spend"] = False
        return payload
    try:
        auth_payload = json.loads(result.get("stdout") or "{}")
    except json.JSONDecodeError:
        payload["error"] = "claude auth status did not emit JSON"
        payload["subscription_no_api_spend"] = False
        return payload
    redacted = redact_claude_auth_payload(auth_payload)
    payload.update(redacted)
    payload["subscription_no_api_spend"] = (
        redacted.get("logged_in") is True
        and redacted.get("auth_method") == "claude.ai"
        and redacted.get("api_provider") == "firstParty"
        and bool(redacted.get("subscription_type"))
    )
    return payload


def _codex_subscription_status(command_runner: CommandRunner) -> dict[str, Any]:
    result = command_runner(["codex", "login", "status"], timeout_seconds=30.0)
    text = (result.get("stdout") or result.get("stderr") or "").strip()
    logged_in_chatgpt = result["exit_code"] == 0 and "Logged in using ChatGPT" in text
    return {
        "command": result["command"],
        "exit_code": result["exit_code"],
        "available": result["exit_code"] == 0,
        "status_text": text,
        "logged_in_chatgpt": logged_in_chatgpt,
        "subscription_no_api_spend": logged_in_chatgpt,
    }


def _ready_for_live_watchlist(
    *,
    claude: dict[str, Any],
    codex: dict[str, Any],
    api_keys: dict[str, bool],
    service_spend_opt_in_present: bool,
) -> bool:
    return (
        claude.get("subscription_no_api_spend") is True
        and codex.get("subscription_no_api_spend") is True
        and not service_spend_opt_in_present
        and not api_keys.get("ANTHROPIC_API_KEY", False)
        and not api_keys.get("OPENAI_API_KEY", False)
    )


def _run_claude_smoke(command_runner: CommandRunner) -> dict[str, Any]:
    result = command_runner(
        [
            "claude",
            "-p",
            f"Reply with exactly {SMOKE_MARKER} and nothing else.",
            "--output-format",
            "json",
            "--max-turns",
            "1",
            "--permission-mode",
            "default",
        ],
        cwd=REPO_ROOT,
        timeout_seconds=60.0,
    )
    text = (result.get("stdout") or "").strip()
    parsed_result = ""
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            parsed_result = str(parsed.get("result", ""))
    except json.JSONDecodeError:
        parsed_result = text
    return {
        "command": result["command"],
        "exit_code": result["exit_code"],
        "success": result["exit_code"] == 0 and parsed_result.strip() == SMOKE_MARKER,
        "marker_seen": SMOKE_MARKER in text,
        "stderr": result.get("stderr", "").strip(),
    }


def _run_codex_smoke(command_runner: CommandRunner) -> dict[str, Any]:
    result = command_runner(
        [
            "codex",
            "-a",
            "never",
            "exec",
            "--json",
            "--skip-git-repo-check",
            "--sandbox",
            "read-only",
            "-m",
            "gpt-5.3-codex",
            f"Reply with exactly {SMOKE_MARKER} and nothing else.",
        ],
        cwd=REPO_ROOT,
        timeout_seconds=60.0,
    )
    stdout = result.get("stdout") or ""
    return {
        "command": result["command"],
        "exit_code": result["exit_code"],
        "success": result["exit_code"] == 0 and SMOKE_MARKER in stdout,
        "marker_seen": SMOKE_MARKER in stdout,
        "stderr": result.get("stderr", "").strip(),
    }


if __name__ == "__main__":
    raise SystemExit(main())
