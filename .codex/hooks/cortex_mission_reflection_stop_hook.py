#!/usr/bin/env python3
"""Codex App Stop hook that enforces Cortex Mission Reflection.

Codex App Stop hooks receive the latest assistant message directly in
``last_assistant_message``. This hook validates that message with the
same shared graph contract used by ``grid``, ``grid-validate``, and the
Claude Code Stop hook. Missing/underfit graph output returns
``{"decision": "block"}``, which asks Codex to continue the turn with
the hook's reason as corrective context.

Lifecycle scope: repo-local Codex hooks require ``[features].codex_hooks
= true`` and a trusted project ``.codex/`` layer. Hook health proves this
configuration and simulated Stop-payload behavior; it does not prove live
model-output lift from Cortex product code.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def _repo_root(hook_input: dict[str, object]) -> Path:
    cwd = hook_input.get("cwd")
    if isinstance(cwd, str) and cwd.strip():
        candidate = Path(cwd).resolve()
        try:
            proc = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=str(candidate),
                check=False,
                capture_output=True,
                text=True,
                timeout=10,
            )
        except (OSError, subprocess.TimeoutExpired):
            return candidate
        if proc.returncode == 0 and proc.stdout.strip():
            return Path(proc.stdout.strip()).resolve()
        return candidate
    return Path(__file__).resolve().parents[2]


def _ensure_repo_import(repo_root: Path) -> None:
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))


def _allow_stop() -> None:
    sys.exit(0)


def _block(reason: str) -> None:
    sys.stdout.write(json.dumps({"decision": "block", "reason": reason}))
    sys.stdout.flush()
    sys.exit(0)


def _diagnostic_exit(message: str) -> None:
    # Fail open only when hook infrastructure cannot supply the data or
    # commands required for validation. Agent non-compliance blocks.
    sys.stderr.write(f"cortex_codex_stop_hook: {message}\n")
    _allow_stop()


def _run_grid(repo_root: Path, mode: str) -> str | None:
    try:
        proc = subprocess.run(
            [
                sys.executable,
                "internal/workflow/repo_workflow.py",
                "grid",
                "--mode",
                mode,
            ],
            cwd=str(repo_root),
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout


def _run_reflection_check(repo_root: Path) -> dict[str, object] | None:
    if os.environ.get("CORTEX_CODEX_APP_HOOK_STRUCTURAL_ONLY") == "1":
        return None
    try:
        proc = subprocess.run(
            [
                sys.executable,
                "internal/workflow/repo_workflow.py",
                "reflection-check",
                "--json",
            ],
            cwd=str(repo_root),
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode not in (0, 1):
        return None
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def main() -> None:
    raw_input = sys.stdin.read()
    if not raw_input.strip():
        _diagnostic_exit("empty hook input on stdin; allowing stop")
        return
    try:
        hook_input = json.loads(raw_input)
    except json.JSONDecodeError as exc:
        _diagnostic_exit(f"hook input is not valid JSON: {exc}; allowing stop")
        return
    if not isinstance(hook_input, dict):
        _diagnostic_exit("hook input is not a JSON object; allowing stop")
        return

    repo_root = _repo_root(hook_input)
    _ensure_repo_import(repo_root)
    try:
        from internal.workflow import mission_reflection
    except Exception as exc:  # pragma: no cover - defensive fail-open path
        _diagnostic_exit(f"could not import mission_reflection: {exc}; allowing stop")
        return

    last_message = hook_input.get("last_assistant_message")
    if not isinstance(last_message, str) or not last_message.strip():
        _diagnostic_exit("missing last_assistant_message; allowing stop")
        return

    validation_mode = mission_reflection.infer_graph_mode(last_message)
    grid_output = _run_grid(repo_root, validation_mode)
    check_payload = _run_reflection_check(repo_root)
    structural_only = os.environ.get("CORTEX_CODEX_APP_HOOK_STRUCTURAL_ONLY") == "1"
    if grid_output is None or (check_payload is None and not structural_only):
        _diagnostic_exit(
            "grid or reflection-check command failed to produce output; allowing stop"
        )
        return

    result = mission_reflection.validate_graph_text(
        last_message,
        check_payload=check_payload,
        require_filled=True,
        mode=validation_mode,
    )
    if result.ok:
        _allow_stop()

    reason_parts = [
        "Cortex Mission Reflection did not pass the shared graph validator.",
        "Per the mission-reflection contract, every Codex App chat must end with the"
        " graph produced by `python3 internal/workflow/repo_workflow.py grid"
        f" --mode {validation_mode}`,"
        " filled in place, as exactly one markdown table under"
        f" `{mission_reflection.GRAPH_HEADER_MARKER}`.",
        "",
        "Validation errors:",
        result.reason(),
        "",
        "Canonical graph skeleton for this turn:",
        "",
        grid_output,
    ]
    _block("\n".join(reason_parts))


if __name__ == "__main__":
    main()
