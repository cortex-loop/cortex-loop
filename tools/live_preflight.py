"""Preflight/update harness for L1 live validation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from live_validation_common import (
    PREFLIGHT_REPORT_PATH,
    PROVIDER_MODELS,
    api_key_presence,
    ensure_live_validation_dirs,
    now_utc_iso,
    read_workstream_baseline,
    redact_claude_auth_payload,
    run_command,
    write_json,
)


def build_preflight_report(*, skip_updates: bool) -> dict[str, Any]:
    ensure_live_validation_dirs()
    accepted_branch, accepted_commit = read_workstream_baseline()

    update_results = {}
    if not skip_updates:
        update_results = {
            "claude": _trimmed(run_command(["claude", "update"])),
            "gemini": _trimmed(run_command(["brew", "upgrade", "gemini-cli"])),
            "openai": _trimmed(run_command(["pipx", "upgrade", "openai"])),
        }

    claude_version = _trimmed(run_command(["claude", "--version"]))
    gemini_version = _trimmed(run_command(["gemini", "--version"]))
    openai_version = _trimmed(run_command(["openai", "--version"]))
    openai_help = _trimmed(run_command(["openai", "--help"]))

    claude_auth_command = run_command(["claude", "auth", "status"])
    claude_auth = _parse_claude_auth_status(claude_auth_command)
    gemini_help = _trimmed(run_command(["gemini", "auth", "--help"]))

    return {
        "generated_at": now_utc_iso(),
        "accepted_baseline": {
            "branch": accepted_branch,
            "commit": accepted_commit,
        },
        "models_under_test": dict(PROVIDER_MODELS),
        "tool_updates": update_results,
        "tool_versions": {
            "claude": claude_version,
            "gemini": gemini_version,
            "openai": openai_version,
        },
        "auth_surfaces": {
            "claude_cli_session": claude_auth,
            "gemini_cli_status_probe": {
                "available": gemini_help["exit_code"] == 0,
                "note": (
                    "Gemini CLI exposes no separate non-invasive auth-status command in the current tool surface; "
                    "live prompt execution is the practical auth/capacity probe."
                ),
            },
            "openai_cli_capability": {
                "installed": openai_help["exit_code"] == 0,
                "note": "The installed OpenAI CLI is an API utility and still expects an API key for live calls.",
            },
            "environment_api_keys": api_key_presence(),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 tools/live_preflight.py",
        description="Update provider CLIs and emit the L1 machine-readable preflight report.",
    )
    parser.add_argument(
        "--skip-updates",
        action="store_true",
        help="Skip mutating provider tool updates and only record the current state.",
    )
    args = parser.parse_args(argv)

    report = build_preflight_report(skip_updates=args.skip_updates)
    write_json(PREFLIGHT_REPORT_PATH, report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


def _parse_claude_auth_status(command_result: dict[str, Any]) -> dict[str, Any]:
    if command_result["exit_code"] != 0:
        return {
            "available": False,
            "error": (command_result["stderr"] or command_result["stdout"]).strip(),
        }
    try:
        payload = json.loads(command_result["stdout"])
    except json.JSONDecodeError:
        return {
            "available": False,
            "error": "claude auth status did not emit JSON.",
        }
    if not isinstance(payload, dict):
        return {
            "available": False,
            "error": "claude auth status emitted a non-object payload.",
        }
    redacted = redact_claude_auth_payload(payload)
    redacted["available"] = True
    redacted["note"] = (
        "CLI session presence does not prove token freshness; live baseline runs still act as the real auth probe."
    )
    return redacted


def _trimmed(command_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "command": command_result["command"],
        "exit_code": command_result["exit_code"],
        "stdout": command_result["stdout"].strip(),
        "stderr": command_result["stderr"].strip(),
        "started_at": command_result["started_at"],
        "ended_at": command_result["ended_at"],
    }


if __name__ == "__main__":
    raise SystemExit(main())
