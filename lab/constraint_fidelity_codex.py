"""Codex CLI observation helpers for constraint-fidelity lab harnesses.

Surface: lab
Executive Benefit: let existing invariant fixtures observe Codex CLI work without
changing invariant law, repair tickets, fixture configs, or scoring.
Why this beats direct product work now: this isolates host-parity plumbing needed
to test whether the bounded check-repair loop generalizes beyond Claude.
"""

from __future__ import annotations

import shlex
from contextlib import nullcontext
from pathlib import Path
from typing import Any

try:  # pragma: no cover - import path differs under direct execution.
    from .invariant_runner import ToolEvidence, extract_tool_evidence_from_records
    from .live_validation_common import now_utc_iso, run_command
    from .openai_operator_cli import isolated_codex_home_env
except ImportError:  # pragma: no cover
    from lab.invariant_runner import ToolEvidence, extract_tool_evidence_from_records
    from lab.live_validation_common import now_utc_iso, run_command
    from lab.openai_operator_cli import isolated_codex_home_env


def auth_mode_supported(*, provider: str, auth_mode: str) -> bool:
    return (provider == "claude" and auth_mode == "claude_code") or (
        provider == "codex" and auth_mode == "codex_cli"
    )


def operator_env(provider: str):
    if provider == "codex":
        return isolated_codex_home_env()
    return nullcontext(None)


def run_codex_turn(
    prompt: str,
    *,
    project_root: Path,
    model: str,
    auth_mode: str,
    resume_session: str | None = None,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    if resume_session:
        command = [
            "codex",
            "exec",
            "resume",
            "--json",
            "--full-auto",
            "--skip-git-repo-check",
            resume_session,
            prompt,
        ]
    else:
        command = [
            "codex",
            "exec",
            "--json",
            "--full-auto",
            "--skip-git-repo-check",
            "-m",
            model,
            prompt,
        ]
    if auth_mode != "codex_cli":
        return {
            "command": command,
            "exit_code": 1,
            "stdout": "",
            "stderr": f"unsupported auth mode for Codex operator lane: {auth_mode}",
            "started_at": now_utc_iso(),
            "ended_at": now_utc_iso(),
        }
    return run_command(command, cwd=project_root, env=env, timeout_seconds=240.0)


def extract_operator_tool_evidence(
    provider: str,
    records: list[dict[str, Any]] | tuple[dict[str, Any], ...],
    *,
    project_root: Path,
) -> ToolEvidence:
    base = extract_tool_evidence_from_records(records, project_root=project_root)
    if provider != "codex":
        return base
    commands: list[str] = list(base.commands)
    read_paths: list[str] = list(base.read_paths)
    for record in records:
        item = record.get("item") if record.get("type") == "item.completed" else None
        if not isinstance(item, dict) or item.get("type") != "command_execution":
            continue
        command = _codex_command_text(item.get("command"))
        if not command:
            continue
        commands.append(command)
        read_paths.extend(_read_paths_from_command(command, project_root=project_root))
    return ToolEvidence(
        read_paths=tuple(dict.fromkeys(read_paths)),
        commands=tuple(dict.fromkeys(commands)),
    )


def _codex_command_text(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    if isinstance(value, list) and all(isinstance(part, str) and part for part in value):
        return " ".join(value)
    return None


_READ_COMMANDS = {"cat", "sed", "rg", "grep", "head", "tail", "nl", "less", "more"}


def _read_paths_from_command(command: str, *, project_root: Path) -> list[str]:
    try:
        tokens = shlex.split(command)
    except ValueError:
        return []
    if len(tokens) >= 3 and Path(tokens[0]).name in {"bash", "sh", "zsh"} and tokens[1] in {"-c", "-lc"}:
        return _read_paths_from_command(tokens[2], project_root=project_root)
    if not tokens or Path(tokens[0]).name not in _READ_COMMANDS:
        return []
    paths: list[str] = []
    for token in tokens[1:]:
        if not token or token.startswith("-") or token in {"|", "||", "&&", ";"}:
            continue
        normalized = _normalize_observed_command_path(token, project_root=project_root)
        if normalized is not None:
            paths.append(normalized)
    return paths


def _normalize_observed_command_path(token: str, *, project_root: Path) -> str | None:
    candidate = Path(token)
    if candidate.is_absolute():
        try:
            relative = candidate.resolve().relative_to(project_root.resolve())
        except ValueError:
            return None
        return relative.as_posix()
    if (project_root / candidate).exists():
        return candidate.as_posix()
    return None
