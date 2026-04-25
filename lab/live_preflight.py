"""Preflight/update harness for the L2 live testing environment."""

from __future__ import annotations

import argparse
import json
from typing import Any

from lab.live_validation_common import (
    AUTH_MODE_ENV,
    GEMINI_OPERATOR_FULL_LADDER,
    MODEL_MATRIX,
    PREFLIGHT_REPORT_PATH,
    api_key_presence,
    automation_auth_readiness,
    build_scenario_catalog,
    choose_model,
    classify_failure,
    command_exists,
    detect_install_channel,
    ensure_live_validation_dirs,
    load_local_env_file,
    now_utc_iso,
    read_workstream_baseline,
    recommended_update_command,
    redact_claude_auth_payload,
    resolve_auth_mode,
    run_command,
    vertex_adc_available,
    write_json,
)


def build_preflight_report(*, lane: str, skip_updates: bool) -> dict[str, Any]:
    ensure_live_validation_dirs()
    accepted_branch, accepted_commit = read_workstream_baseline()

    install_channels = {
        "claude": detect_install_channel("claude"),
        "gemini": detect_install_channel("gemini"),
        "codex": detect_install_channel("codex"),
        "openai": detect_install_channel("openai"),
    }

    update_results = {}
    if not skip_updates:
        update_results = _run_updates(install_channels)

    claude_version = _trimmed(run_command(["claude", "--version"])) if install_channels["claude"]["installed"] else None
    gemini_version = _trimmed(run_command(["gemini", "--version"])) if install_channels["gemini"]["installed"] else None
    codex_version = _trimmed(run_command(["codex", "--version"])) if install_channels["codex"]["installed"] else None
    openai_version = _trimmed(run_command(["openai", "--version"])) if install_channels["openai"]["installed"] else None

    claude_auth = _claude_auth_status() if install_channels["claude"]["installed"] else {"available": False}
    codex_auth = _codex_auth_status() if install_channels["codex"]["installed"] else {"available": False}
    gemini_auth = {
        "available": install_channels["gemini"]["installed"],
        "note": (
            "Gemini CLI exposes no separate non-invasive auth-status command in the current tool surface; "
            "the operator probe below is the real auth and capacity check."
        ),
    }

    operator_probe = _operator_probe_summary()
    automation_probe = {
        "claude": automation_auth_readiness("claude"),
        "gemini": automation_auth_readiness("gemini"),
        "openai": automation_auth_readiness("openai"),
    }

    return {
        "generated_at": now_utc_iso(),
        "accepted_baseline": {"branch": accepted_branch, "commit": accepted_commit},
        "lane": lane,
        "scenario_catalog": build_scenario_catalog(),
        "install_channels": install_channels,
        "tool_updates": update_results,
        "tool_versions": {
            "claude": claude_version,
            "gemini": gemini_version,
            "codex": codex_version,
            "openai": openai_version,
        },
        "auth_surfaces": {
            "claude_cli_session": claude_auth,
            "gemini_cli_status_probe": gemini_auth,
            "codex_cli_session": codex_auth,
            "automation": automation_probe,
        },
        "operator_probe": operator_probe,
        "model_preferences": {
            provider: {
                lane_name: {
                    "preferred": pref.preferred,
                    "fallback": pref.fallback,
                    "fallback_chain": list(GEMINI_OPERATOR_FULL_LADDER[1:]) if provider == "gemini" and lane_name == "operator" else ([pref.fallback] if pref.fallback else []),
                }
                for lane_name, pref in lane_map.items()
            }
            for provider, lane_map in MODEL_MATRIX.items()
        },
        "auth_mode_env": dict(AUTH_MODE_ENV),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 lab/live_preflight.py",
        description="Update live-testing CLIs and emit the L2 preflight report.",
    )
    parser.add_argument(
        "--lane",
        choices=("operator", "automation", "all"),
        default="all",
    )
    parser.add_argument(
        "--skip-updates",
        action="store_true",
        help="Skip mutating tool updates and only record the current state.",
    )
    args = parser.parse_args(argv)

    load_local_env_file()
    report = build_preflight_report(lane=args.lane, skip_updates=args.skip_updates)
    write_json(PREFLIGHT_REPORT_PATH, report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


def _run_updates(install_channels: dict[str, dict[str, Any]]) -> dict[str, Any]:
    results: dict[str, Any] = {}
    for binary in ("claude", "gemini", "codex", "openai"):
        channel = install_channels[binary]["channel"]
        command = recommended_update_command(binary, channel)
        if command is None:
            results[binary] = {
                "skipped": True,
                "reason": f"no safe updater for channel `{channel}`",
            }
            continue
        results[binary] = _trimmed(run_command(command))
    return results


def _claude_auth_status() -> dict[str, Any]:
    result = run_command(["claude", "auth", "status"])
    if result["exit_code"] != 0:
        return {
            "available": False,
            "error": (result["stderr"] or result["stdout"]).strip(),
        }
    try:
        payload = json.loads(result["stdout"])
    except json.JSONDecodeError:
        return {"available": False, "error": "claude auth status did not emit JSON"}
    if not isinstance(payload, dict):
        return {"available": False, "error": "claude auth status emitted a non-object payload"}
    redacted = redact_claude_auth_payload(payload)
    redacted["available"] = True
    return redacted


def _codex_auth_status() -> dict[str, Any]:
    result = run_command(["codex", "login", "status"])
    text = (result["stdout"] or result["stderr"]).strip()
    return {
        "available": result["exit_code"] == 0,
        "status_text": text,
        "logged_in": "Logged in" in text,
    }


def _operator_probe_summary() -> dict[str, Any]:
    return {
        "claude": _probe_claude_operator(),
        "gemini": _probe_gemini_operator(),
        "openai": _probe_openai_operator(),
        "codex": _probe_codex_operator(),
    }


def _probe_claude_operator() -> dict[str, Any]:
    preferred = MODEL_MATRIX["claude"]["operator"].preferred
    probe = _run_claude_probe(preferred)
    failure_class = classify_failure(f"{probe['stdout']}\n{probe['stderr']}")
    chosen_model = choose_model("claude", "operator", first_failure=failure_class)
    if chosen_model != preferred:
        probe = _run_claude_probe(chosen_model)
        failure_class = classify_failure(f"{probe['stdout']}\n{probe['stderr']}")
    return {
        "auth_mode": resolve_auth_mode("claude", "operator"),
        "preferred_model": preferred,
        "model": chosen_model,
        "failure_class": failure_class,
        "command": probe["command"],
    }


def _probe_gemini_operator() -> dict[str, Any]:
    preferred = MODEL_MATRIX["gemini"]["operator"].preferred
    attempted_models: list[str] = []
    probe = _run_gemini_probe(preferred)
    failure_class = classify_failure(f"{probe['stdout']}\n{probe['stderr']}")
    attempted_models.append(preferred)
    auto_supported = failure_class != "model_unavailable"
    chosen_model = choose_model(
        "gemini",
        "operator",
        first_failure=failure_class,
        current_model=preferred,
        auto_supported=auto_supported,
    )
    while chosen_model != attempted_models[-1]:
        probe = _run_gemini_probe(chosen_model)
        failure_class = classify_failure(f"{probe['stdout']}\n{probe['stderr']}")
        attempted_models.append(chosen_model)
        chosen_model = choose_model(
            "gemini",
            "operator",
            first_failure=failure_class,
            current_model=chosen_model,
            auto_supported=auto_supported,
        )
    final_model = attempted_models[-1]
    return {
        "auth_mode": resolve_auth_mode("gemini", "operator"),
        "preferred_model": preferred,
        "model": final_model,
        "auto_supported": auto_supported,
        "attempted_models": attempted_models,
        "failure_class": failure_class,
        "command": probe["command"],
    }


def _probe_openai_operator() -> dict[str, Any]:
    preferred = MODEL_MATRIX["openai"]["operator"].preferred
    probe = _run_codex_probe(preferred)
    failure_class = classify_failure(f"{probe['stdout']}\n{probe['stderr']}")
    chosen_model = choose_model("openai", "operator", first_failure=failure_class)
    if chosen_model != preferred:
        probe = _run_codex_probe(chosen_model)
        failure_class = classify_failure(f"{probe['stdout']}\n{probe['stderr']}")
    return {
        "auth_mode": resolve_auth_mode("openai", "operator"),
        "preferred_model": preferred,
        "model": chosen_model,
        "failure_class": failure_class,
        "command": probe["command"],
    }


def _probe_codex_operator() -> dict[str, Any]:
    preferred = MODEL_MATRIX["codex"]["operator"].preferred
    probe = _run_codex_probe(preferred)
    failure_class = classify_failure(f"{probe['stdout']}\n{probe['stderr']}")
    chosen_model = choose_model("codex", "operator", first_failure=failure_class)
    if chosen_model != preferred:
        probe = _run_codex_probe(chosen_model)
        failure_class = classify_failure(f"{probe['stdout']}\n{probe['stderr']}")
    return {
        "auth_mode": resolve_auth_mode("codex", "operator"),
        "preferred_model": preferred,
        "model": chosen_model,
        "failure_class": failure_class,
        "command": probe["command"],
    }


def _run_claude_probe(model: str) -> dict[str, Any]:
    with tempfile_workspace() as cwd:
        return run_command(
            [
                "claude",
                "-p",
                "Respond exactly with OK.",
                "--model",
                model,
                "--output-format",
                "stream-json",
                "--verbose",
                "--max-turns",
                "1",
                "--permission-mode",
                "plan",
            ],
            cwd=cwd,
            timeout_seconds=30.0,
        )


def _run_gemini_probe(model: str) -> dict[str, Any]:
    with tempfile_workspace() as cwd:
        command = [
            "gemini",
            "-p",
            "Respond exactly with OK.",
            "-o",
            "stream-json",
            "--approval-mode",
            "yolo",
        ]
        if model != "auto":
            command[5:5] = ["-m", model]
        return run_command(
            command,
            cwd=cwd,
            timeout_seconds=30.0,
        )


def _run_codex_probe(model: str) -> dict[str, Any]:
    with tempfile_workspace() as cwd:
        return run_command(
            [
                "codex",
                "exec",
                "--json",
                "--skip-git-repo-check",
                "--sandbox",
                "read-only",
                "-m",
                model,
                "Respond exactly with OK.",
            ],
            cwd=cwd,
            timeout_seconds=30.0,
        )


def tempfile_workspace():
    from contextlib import contextmanager
    import tempfile
    from pathlib import Path

    @contextmanager
    def _ctx():
        with tempfile.TemporaryDirectory(prefix="cortex-live-preflight-") as tmpdir:
            yield Path(tmpdir)

    return _ctx()


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
