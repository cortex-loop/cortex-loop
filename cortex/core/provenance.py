"""Repo-visible provenance helpers for later commitment-time evidence use."""

from __future__ import annotations

import re
import shlex
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

    def __post_init__(self) -> None:
        if any(not changed_file.strip() for changed_file in self.changed_files):
            raise ValueError(
                "RepositorySnapshot.changed_files must contain only non-empty repo-relative paths after trimming.",
            )
        if self.error_reason is not None and not self.error_reason.strip():
            raise ValueError(
                "RepositorySnapshot.error_reason must be non-empty after trimming when provided.",
            )
        if self.repository_root is not None and not isinstance(self.repository_root, Path):
            actual_type = type(self.repository_root).__name__
            raise TypeError(
                "RepositorySnapshot.repository_root must be Path | None, "
                f"got {actual_type}.",
            )


@dataclass(frozen=True, slots=True)
class ChangedFilesDelta:
    changed_files: tuple[str, ...] | None
    reason: str | None = None

    def __post_init__(self) -> None:
        if self.changed_files is not None and any(
            not changed_file.strip() for changed_file in self.changed_files
        ):
            raise ValueError(
                "ChangedFilesDelta.changed_files must contain only non-empty repo-relative paths after trimming.",
            )
        if self.reason is not None and not self.reason.strip():
            raise ValueError(
                "ChangedFilesDelta.reason must be non-empty after trimming when provided.",
            )


@dataclass(frozen=True, slots=True)
class EvidenceReferenceEvaluation:
    reference_kind: str
    check_status: str
    reason: str
    normalized_reference: str | None = None

    def __post_init__(self) -> None:
        if not self.reference_kind.strip():
            raise ValueError(
                "EvidenceReferenceEvaluation.reference_kind must be non-empty after trimming.",
            )
        if not self.check_status.strip():
            raise ValueError(
                "EvidenceReferenceEvaluation.check_status must be non-empty after trimming.",
            )


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
    if baseline_snapshot.repository_root is None:
        return ChangedFilesDelta(None, "baseline repository root unavailable for comparison")
    if current_snapshot.repository_root is None:
        return ChangedFilesDelta(None, "current repository root unavailable for comparison")
    if baseline_snapshot.repository_root != current_snapshot.repository_root:
        return ChangedFilesDelta(
            None,
            "repository root mismatch between baseline and current snapshots",
        )

    baseline_files = set(baseline_snapshot.changed_files)
    current_files = set(current_snapshot.changed_files)
    return ChangedFilesDelta(tuple(sorted(current_files - baseline_files)), None)


def evaluate_evidence_reference(
    reference: str,
    *,
    root: Path,
    observed_commands: Sequence[str] = (),
    observed_tools: Sequence[str] = (),
) -> EvidenceReferenceEvaluation:
    reference_kind, normalized_reference = _classify_evidence_reference(reference, root=root)
    normalized_commands = tuple(
        normalized
        for value in observed_commands
        if (normalized := normalize_command_claim(value))
    )
    normalized_tools = {
        str(value).strip().lower()
        for value in observed_tools
        if str(value).strip()
    }

    if reference_kind == "path":
        path = _evidence_reference_path(reference, root=root)
        if path is not None and path.exists():
            return EvidenceReferenceEvaluation(
                reference_kind="path",
                check_status="verified",
                reason="path exists",
                normalized_reference=normalized_reference,
            )
        return EvidenceReferenceEvaluation(
            reference_kind="path",
            check_status="unverified",
            reason=f"path does not exist: {normalized_reference}",
            normalized_reference=normalized_reference,
        )

    if reference_kind == "tool":
        if not normalized_tools:
            return EvidenceReferenceEvaluation(
                reference_kind="tool",
                check_status="uncheckable",
                reason="no observed tool evidence",
                normalized_reference=normalized_reference,
            )
        if normalized_reference in normalized_tools:
            return EvidenceReferenceEvaluation(
                reference_kind="tool",
                check_status="verified",
                reason=f"tool observed: {normalized_reference}",
                normalized_reference=normalized_reference,
            )
        return EvidenceReferenceEvaluation(
            reference_kind="tool",
            check_status="unverified",
            reason=f"tool not observed: {normalized_reference}",
            normalized_reference=normalized_reference,
        )

    if reference_kind == "command":
        if not normalized_commands:
            return EvidenceReferenceEvaluation(
                reference_kind="command",
                check_status="uncheckable",
                reason="no observed command evidence",
                normalized_reference=normalized_reference,
            )
        if normalized_reference and any(
            command_claim_matches(normalized_reference, observed)
            for observed in normalized_commands
        ):
            return EvidenceReferenceEvaluation(
                reference_kind="command",
                check_status="verified",
                reason="command matched observed evidence",
                normalized_reference=normalized_reference,
            )
        return EvidenceReferenceEvaluation(
            reference_kind="command",
            check_status="unverified",
            reason="command not witnessed in observed evidence",
            normalized_reference=normalized_reference,
        )

    return EvidenceReferenceEvaluation(
        reference_kind="note",
        check_status="uncheckable",
        reason="reference is non-verifiable note text",
        normalized_reference=None,
    )


def normalize_command_claim(text: str) -> str:
    raw_value = str(text).strip()
    wrapped_command_match = re.fullmatch(
        r"`(?P<command>[^`]+)`(?:\s*[:\-]?\s*(?:ok|pass|passed|success|succeeded))?[.,;:!?]*",
        raw_value,
        flags=re.IGNORECASE,
    )
    if wrapped_command_match is not None:
        raw_value = wrapped_command_match.group("command")

    value = raw_value.strip().strip("`").lower()
    value = re.sub(r"[.,;:!?]+$", "", value).strip()
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"[:\-]\s*(ok|pass|passed|success|succeeded)$", "", value).strip()
    return value


def command_claim_matches(claim: str, observed: str) -> bool:
    claim_tokens = _command_tokens(claim)
    observed_tokens = _command_tokens(observed)
    if not claim_tokens or not observed_tokens:
        return False
    return claim_tokens == observed_tokens or (
        len(claim_tokens) <= len(observed_tokens)
        and observed_tokens[: len(claim_tokens)] == claim_tokens
    )


def normalize_repo_relative_file_claims(value: Any, *, root: Path) -> tuple[str, ...]:
    root_resolved = root.resolve()
    normalized: list[str] = []
    seen: set[str] = set()
    for raw in _as_string_tuple(value):
        claim = _normalize_repo_relative_file_claim(raw, root=root_resolved)
        if claim is None or claim in seen:
            continue
        seen.add(claim)
        normalized.append(claim)
    return tuple(normalized)


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


def _classify_evidence_reference(reference: str, *, root: Path) -> tuple[str, str | None]:
    text = str(reference).strip()
    lower = text.lower()
    if lower.startswith("tool:"):
        return "tool", lower.split(":", 1)[1].strip()
    if lower.startswith("cmd:"):
        return "command", normalize_command_claim(text.split(":", 1)[1].strip())
    if _looks_like_command_claim(text):
        return "command", normalize_command_claim(text)
    normalized_path = _normalize_repo_relative_file_claim(text, root=root.resolve())
    if normalized_path is not None:
        return "path", normalized_path
    return "note", None


def _evidence_reference_path(reference: str, *, root: Path) -> Path | None:
    normalized_path = _normalize_repo_relative_file_claim(reference, root=root.resolve())
    if normalized_path is None:
        return None
    return (root.resolve() / normalized_path).resolve()


def _normalize_repo_relative_file_claim(reference: str, *, root: Path) -> str | None:
    text = str(reference).strip()
    if not text or text.startswith(("http://", "https://")):
        return None

    path_text = text.split("#", 1)[0].strip()
    if " " in path_text:
        first_token = path_text.split(None, 1)[0].strip()
        if first_token and (
            any(sep in first_token for sep in ("/", "\\"))
            or first_token.startswith((".", "~"))
        ):
            path_text = first_token
    path_text = re.sub(r":\d+(?::\d+|-\d+)?$", "", path_text).strip()
    path_text = path_text.rstrip(".,;:")
    if not path_text:
        return None
    if not any(sep in path_text for sep in ("/", "\\")) and not path_text.startswith((".", "~")):
        return None

    path = Path(path_text).expanduser()
    if not path.is_absolute():
        path = root / path
    resolved = path.resolve()
    try:
        return resolved.relative_to(root).as_posix()
    except ValueError:
        return None


def _looks_like_command_claim(text: str) -> bool:
    return bool(
        re.search(
            r"\b(pytest|npm|pnpm|yarn|npx|ruff|mypy|go test|cargo test|python\s+-m)\b",
            text.lower(),
        )
    )


def _command_tokens(command: str) -> tuple[str, ...]:
    normalized = normalize_command_claim(command)
    if not normalized:
        return ()
    try:
        raw_tokens = shlex.split(normalized)
    except ValueError:
        raw_tokens = normalized.split()

    tokens = [token.strip().lower() for token in raw_tokens if token.strip()]
    if not tokens:
        return ()

    while True:
        if len(tokens) >= 3 and tokens[0] in {"bash", "sh"} and tokens[1] == "-lc":
            return _command_tokens(" ".join(tokens[2:]))
        if len(tokens) >= 2 and tuple(tokens[:2]) in {("uv", "run"), ("poetry", "run"), ("pipenv", "run")}:
            tokens = tokens[2:]
            continue
        if len(tokens) >= 3 and tokens[0] in {"python", "python3", "py"} and tokens[1:3] == ["-m", "pytest"]:
            tokens = ["pytest", *tokens[3:]]
            continue
        break

    return tuple(tokens)


def _has_enclosing_git_marker(root: Path) -> bool:
    return any((candidate / ".git").exists() for candidate in (root, *root.parents))


__all__ = [
    "ChangedFilesDelta",
    "EvidenceReferenceEvaluation",
    "RepositorySnapshot",
    "command_claim_matches",
    "changed_files_since_baseline",
    "evaluate_evidence_reference",
    "extract_requirement_ids",
    "normalize_command_claim",
    "normalize_repo_relative_file_claims",
    "repository_snapshot",
]
