"""Repo-visible provenance helpers for later commitment-time evidence use."""

from __future__ import annotations

import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class RepositorySnapshot:
    available: bool
    changed_files: tuple[str, ...]
    error_reason: str | None = None
    repository_root: Path | None = None


@dataclass(frozen=True, slots=True)
class ChangedFilesDelta:
    changed_files: tuple[str, ...] | None
    reason: str | None = None


def extract_requirement_ids(payload: Mapping[str, Any]) -> tuple[str, ...]:
    direct_ids = _extract_ids_from_mapping(payload)
    if direct_ids:
        return direct_ids

    task_contract = payload.get("task_contract")
    if isinstance(task_contract, Mapping):
        contract_ids = _extract_ids_from_mapping(task_contract)
        if contract_ids:
            return contract_ids

    task = payload.get("task")
    if isinstance(task, Mapping):
        contract = task.get("contract")
        if isinstance(contract, Mapping):
            contract_ids = _extract_ids_from_mapping(contract)
            if contract_ids:
                return contract_ids

    return ()


def repository_snapshot(root: Path) -> RepositorySnapshot:
    probe_root = root.resolve()
    if not _has_enclosing_git_marker(probe_root):
        return RepositorySnapshot(
            available=False,
            changed_files=(),
            error_reason="git repository marker not found",
            repository_root=None,
        )

    try:
        root_proc = subprocess.run(
            ["git", "-C", str(probe_root), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False,
            timeout=2,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return RepositorySnapshot(
            available=False,
            changed_files=(),
            error_reason=f"git root probe failed: {exc}",
            repository_root=None,
        )
    if root_proc.returncode != 0:
        reason = root_proc.stderr.strip() or root_proc.stdout.strip() or f"exit code {root_proc.returncode}"
        return RepositorySnapshot(
            available=False,
            changed_files=(),
            error_reason=reason,
            repository_root=None,
        )

    repository_root = Path(root_proc.stdout.strip())
    try:
        status_proc = subprocess.run(
            [
                "git",
                "-C",
                str(probe_root),
                "-c",
                "status.relativePaths=false",
                "status",
                "--porcelain",
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=2,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return RepositorySnapshot(
            available=False,
            changed_files=(),
            error_reason=f"git status failed: {exc}",
            repository_root=repository_root,
        )
    if status_proc.returncode != 0:
        reason = (
            status_proc.stderr.strip()
            or status_proc.stdout.strip()
            or f"exit code {status_proc.returncode}"
        )
        return RepositorySnapshot(
            available=False,
            changed_files=(),
            error_reason=reason,
            repository_root=repository_root,
        )

    changed_files: list[str] = []
    for line in status_proc.stdout.splitlines():
        if not line:
            continue
        path_field = line[3:].strip() if len(line) > 3 else ""
        if " -> " in path_field:
            path_field = path_field.split(" -> ", 1)[1].strip()
        normalized = _normalize_repo_relative_path(path_field)
        if normalized:
            changed_files.append(normalized)

    return RepositorySnapshot(
        available=True,
        changed_files=tuple(sorted(set(changed_files))),
        error_reason=None,
        repository_root=repository_root,
    )


def changed_files_since_baseline(
    *,
    baseline_snapshot: RepositorySnapshot | None,
    current_snapshot: RepositorySnapshot | None,
) -> ChangedFilesDelta:
    if baseline_snapshot is None:
        return ChangedFilesDelta(None, "baseline repository snapshot unavailable")
    if current_snapshot is None:
        return ChangedFilesDelta(None, "current repository snapshot unavailable")
    if not baseline_snapshot.available:
        return ChangedFilesDelta(
            None,
            baseline_snapshot.error_reason or "baseline repository snapshot unavailable",
        )
    if not current_snapshot.available:
        return ChangedFilesDelta(
            None,
            current_snapshot.error_reason or "current repository snapshot unavailable",
        )

    baseline_files = set(baseline_snapshot.changed_files)
    current_files = set(current_snapshot.changed_files)
    return ChangedFilesDelta(tuple(sorted(current_files - baseline_files)), None)


def _extract_ids_from_mapping(value: Mapping[str, Any]) -> tuple[str, ...]:
    direct = _as_string_tuple(value.get("required_requirement_ids"))
    if direct:
        return _unique_strings(direct)
    fallback = _as_string_tuple(value.get("required_ids"))
    return _unique_strings(fallback)


def _as_string_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        text = value.strip()
        return (text,) if text else ()
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        values: list[str] = []
        for item in value:
            text = str(item).strip()
            if text:
                values.append(text)
        return tuple(values)
    return ()


def _unique_strings(values: Sequence[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        unique.append(value)
    return tuple(unique)


def _normalize_repo_relative_path(path_field: str) -> str | None:
    candidate = path_field.strip().strip('"')
    if not candidate:
        return None
    return candidate.replace("\\", "/")


def _has_enclosing_git_marker(root: Path) -> bool:
    return any((candidate / ".git").exists() for candidate in (root, *root.parents))


__all__ = [
    "ChangedFilesDelta",
    "RepositorySnapshot",
    "changed_files_since_baseline",
    "extract_requirement_ids",
    "repository_snapshot",
]
