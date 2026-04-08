"""Shared helpers for the E12 comparative output-quality benchmark."""

from __future__ import annotations

import hashlib
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal


ArmName = Literal["raw", "tooling_only", "cortex"]
_FILE_HEADER_RE = re.compile(r"^=== FILE: (?P<path>.+?) ===$")
_BLOCKED_HEADER_RE = re.compile(
    r"^=== BLOCKED: (?P<reason>needs_user_input|unsafe_request) ===$"
)
_END_FILE_MARKER = "=== END FILE ==="
_END_BLOCKED_MARKER = "=== END BLOCKED ==="
_BLOCKED_TO_FAILURE_CLASS = {
    "needs_user_input": "blocked_missing_info",
    "unsafe_request": "blocked_unsafe",
}


@dataclass(frozen=True, slots=True)
class OutputQualityTaskPack:
    task_id: str
    prompt_text: str
    template_root: Path
    allowed_write_paths: tuple[str, ...]
    visible_context_paths: tuple[str, ...]
    verifier_only_paths: tuple[str, ...]
    install_command: tuple[str, ...]
    lint_command: tuple[str, ...]
    typecheck_command: tuple[str, ...]
    build_command: tuple[str, ...]
    visible_test_command: tuple[str, ...]
    hidden_test_command: tuple[str, ...]
    max_output_tokens: int = 6000


@dataclass(frozen=True, slots=True)
class OutputParseResult:
    file_map: dict[str, str] | None
    parse_error: str | None
    blocked_reason: str | None
    blocked_message: str | None

    @property
    def failure_class(self) -> str | None:
        if self.blocked_reason is not None:
            return _BLOCKED_TO_FAILURE_CLASS[self.blocked_reason]
        if self.parse_error is not None:
            return "output_invalid"
        return None


def build_file_block_protocol(allowed_write_paths: tuple[str, ...]) -> str:
    allowed_paths = "\n".join(f"- {path}" for path in allowed_write_paths)
    return (
        "Return only full-file blocks for the requested changes.\n"
        "Use this exact format for each edited file:\n"
        "=== FILE: relative/path ===\n"
        "<full file contents>\n"
        "=== END FILE ===\n\n"
        "If you cannot complete the task because essential information is missing, use:\n"
        "=== BLOCKED: needs_user_input ===\n"
        "<message>\n"
        "=== END BLOCKED ===\n\n"
        "If the request is unsafe, use:\n"
        "=== BLOCKED: unsafe_request ===\n"
        "<message>\n"
        "=== END BLOCKED ===\n\n"
        "Keep any changes within these paths:\n"
        f"{allowed_paths}\n"
        "Do not include explanations, prose, or code fences."
    )


def build_output_quality_input_text(
    task_pack: OutputQualityTaskPack,
    *,
    arm: ArmName,
) -> str:
    protocol = build_file_block_protocol(task_pack.allowed_write_paths)
    if arm == "raw":
        return f"{task_pack.prompt_text.strip()}\n\n{protocol}"
    context_intro = (
        "Visible contract files follow. Additional verifier-only checks may run.\n"
        "Use the existing files below as the visible task contract.\n"
    )
    return (
        f"{task_pack.prompt_text.strip()}\n\n"
        f"{context_intro}"
        f"{render_context_bundle(task_pack)}\n\n"
        f"{protocol}"
    )


def render_context_bundle(task_pack: OutputQualityTaskPack) -> str:
    blocks: list[str] = []
    seen: set[str] = set()
    for relative_path in (*task_pack.allowed_write_paths, *task_pack.visible_context_paths):
        if relative_path in seen:
            continue
        seen.add(relative_path)
        source_path = task_pack.template_root / relative_path
        if not source_path.is_file():
            raise RuntimeError(
                "output-quality context file is missing from the template: "
                f"{relative_path}"
            )
        text = source_path.read_text(encoding="utf-8").rstrip()
        blocks.append(
            "\n".join(
                (
                    f"=== CONTEXT FILE: {relative_path} ===",
                    text,
                    "=== END CONTEXT FILE ===",
                )
            )
        )
    return "\n\n".join(blocks)


def parse_output_quality_result(
    result_text: str | None,
    *,
    allowed_write_paths: tuple[str, ...],
) -> OutputParseResult:
    if result_text is None or not result_text.strip():
        return OutputParseResult(
            file_map=None,
            parse_error="result_text was empty.",
            blocked_reason=None,
            blocked_message=None,
        )

    lines = result_text.splitlines()
    index = 0
    file_map: dict[str, str] = {}
    blocked_reason: str | None = None
    blocked_message: str | None = None
    allowed_path_set = set(allowed_write_paths)

    while index < len(lines):
        line = lines[index].rstrip("\n")
        stripped = line.strip()
        if not stripped:
            index += 1
            continue

        blocked_match = _BLOCKED_HEADER_RE.match(stripped)
        if blocked_match is not None:
            if file_map:
                return OutputParseResult(
                    file_map=None,
                    parse_error="blocked marker appeared after file blocks.",
                    blocked_reason=None,
                    blocked_message=None,
                )
            blocked_reason = blocked_match.group("reason")
            body_lines: list[str] = []
            index += 1
            while index < len(lines):
                candidate = lines[index].rstrip("\n")
                if candidate.strip() == _END_BLOCKED_MARKER:
                    blocked_message = "\n".join(body_lines).strip() or None
                    return OutputParseResult(
                        file_map=None,
                        parse_error=None,
                        blocked_reason=blocked_reason,
                        blocked_message=blocked_message,
                    )
                body_lines.append(candidate)
                index += 1
            return OutputParseResult(
                file_map=None,
                parse_error="blocked marker was not terminated.",
                blocked_reason=None,
                blocked_message=None,
            )

        header_match = _FILE_HEADER_RE.match(stripped)
        if header_match is None:
            return OutputParseResult(
                file_map=None,
                parse_error=f"unexpected line outside file block: {stripped}",
                blocked_reason=None,
                blocked_message=None,
            )
        relative_path = header_match.group("path").strip()
        if relative_path not in allowed_path_set:
            return OutputParseResult(
                file_map=None,
                parse_error=f"output modified unapproved path: {relative_path}",
                blocked_reason=None,
                blocked_message=None,
            )
        if relative_path in file_map:
            return OutputParseResult(
                file_map=None,
                parse_error=f"duplicate file block for path: {relative_path}",
                blocked_reason=None,
                blocked_message=None,
            )
        index += 1
        body_lines = []
        while index < len(lines):
            candidate = lines[index].rstrip("\n")
            if candidate.strip() == _END_FILE_MARKER:
                file_map[relative_path] = "\n".join(body_lines).rstrip("\n") + "\n"
                index += 1
                break
            body_lines.append(candidate)
            index += 1
        else:
            return OutputParseResult(
                file_map=None,
                parse_error=f"file block for {relative_path} was not terminated.",
                blocked_reason=None,
                blocked_message=None,
            )

    if not file_map:
        return OutputParseResult(
            file_map=None,
            parse_error="result_text did not contain any file blocks.",
            blocked_reason=None,
            blocked_message=None,
        )
    return OutputParseResult(
        file_map=file_map,
        parse_error=None,
        blocked_reason=None,
        blocked_message=None,
    )


def prepare_output_quality_workspace(*, template_root: Path, run_root: Path) -> Path:
    if run_root.exists():
        shutil.rmtree(run_root)
    project_root = run_root / "project_a"
    shutil.copytree(template_root, project_root)
    return project_root


def prepare_seeded_workspace(
    *,
    template_root: Path,
    seed_workspace_root: Path,
    run_root: Path,
) -> Path:
    if run_root.exists():
        shutil.rmtree(run_root)
    project_root = run_root / "project_a"
    shutil.copytree(
        template_root,
        project_root,
        ignore=shutil.ignore_patterns("node_modules", "dist", ".astro"),
    )
    seed_node_modules = seed_workspace_root / "node_modules"
    if seed_node_modules.exists():
        (project_root / "node_modules").symlink_to(seed_node_modules)
    return project_root


def apply_output_files(*, project_root: Path, file_map: dict[str, str]) -> None:
    for relative_path, contents in file_map.items():
        target_path = project_root / relative_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(contents, encoding="utf-8")


def snapshot_files(
    *,
    root: Path,
    relative_paths: tuple[str, ...],
) -> dict[str, str]:
    snapshot: dict[str, str] = {}
    for relative_path in relative_paths:
        target = root / relative_path
        if target.is_file():
            snapshot[relative_path] = target.read_text(encoding="utf-8")
    return snapshot


def stable_pair_order(seed: str) -> tuple[str, str]:
    digest = hashlib.sha256(seed.encode("utf-8")).digest()
    return ("a", "b") if digest[0] % 2 == 0 else ("b", "a")
