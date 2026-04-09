"""Shared verified-work runtime helpers over the landed verified-work law."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from cortex.sre.preservation import PreservationState
from cortex.sre.verified_work import VerificationOutcome, WorkContract


REPO_ROOT = Path(__file__).resolve().parents[2]
BLOCKED_REASON_MAP = {
    "needs_user_input": "blocked_missing_info",
    "unsafe_request": "blocked_unsafe",
}
_PYTHON_BIN = shutil.which("python3") or sys.executable
_VENV_DIR_NAME = ".verified-work-venv"
_FILE_HEADER_RE = re.compile(r"^=== FILE: (?P<path>.+?) ===$")
_BLOCKED_HEADER_RE = re.compile(
    r"^=== BLOCKED: (?P<reason>needs_user_input|unsafe_request) ===$"
)
_END_FILE_MARKER = "=== END FILE ==="
_END_BLOCKED_MARKER = "=== END BLOCKED ==="
_PASSED_RE = re.compile(r"(?P<count>\d+)\s+passed")
_FAILED_RE = re.compile(r"(?P<count>\d+)\s+failed")
_FAILING_TEST_RE = re.compile(r"^(?:FAILED|ERROR) (?P<name>tests/[^\s]+)", re.MULTILINE)

VerifiedWorkContextMode = Literal[
    "default",
    "off",
    "writable_files_only",
    "writable_files_plus_visible_tests",
]
VerifiedWorkRepairTicketStyle = Literal["factual", "minimal"]


@dataclass(frozen=True, slots=True)
class VerifiedWorkProfileSpec:
    template_root: Path
    read_only_context_paths: tuple[str, ...]
    import_target: str | None
    pytest_command: tuple[str, ...]


_VERIFIED_WORK_PROFILE_REGISTRY = {
    "python_workspace_pytest_v1": VerifiedWorkProfileSpec(
        template_root=(
            REPO_ROOT
            / "tests"
            / "fixtures"
            / "live_validation"
            / "bookmarks_app_template"
        ),
        read_only_context_paths=("tests/test_bookmarks_api.py",),
        import_target="bookmarks_api.main",
        pytest_command=("-m", "pytest", "-q", "tests/test_bookmarks_api.py"),
    ),
    "python_workspace_pytest_port_fix_v1": VerifiedWorkProfileSpec(
        template_root=(
            REPO_ROOT
            / "tests"
            / "fixtures"
            / "live_validation"
            / "project_template"
        ),
        read_only_context_paths=("tests/test_normalize_port.py",),
        import_target="normalize_port",
        pytest_command=("-m", "pytest", "-q", "tests/test_normalize_port.py"),
    ),
    "python_workspace_pytest_feature_flags_v1": VerifiedWorkProfileSpec(
        template_root=(
            REPO_ROOT
            / "tests"
            / "fixtures"
            / "live_validation"
            / "feature_flags_template"
        ),
        read_only_context_paths=("tests/test_feature_flags.py",),
        import_target="feature_flags.evaluator",
        pytest_command=("-m", "pytest", "-q", "tests/test_feature_flags.py"),
    ),
}


def build_verified_work_instructions(work_contract: WorkContract) -> str:
    allowed_paths = "\n".join(f"- {path}" for path in work_contract.allowed_write_paths)
    return (
        "Return only full-file blocks for the allowed paths.\n"
        "Allowed paths:\n"
        f"{allowed_paths}\n\n"
        "For each file, use:\n"
        "=== FILE: relative/path ===\n"
        "<full file contents>\n"
        "=== END FILE ===\n\n"
        "If blocked because you need missing user information, use:\n"
        "=== BLOCKED: needs_user_input ===\n"
        "<message>\n"
        "=== END BLOCKED ===\n\n"
        "If blocked because the request is unsafe, use:\n"
        "=== BLOCKED: unsafe_request ===\n"
        "<message>\n"
        "=== END BLOCKED ===\n\n"
        "Do not return prose, explanations, or code fences. Do not run tests."
    )


def build_verified_work_input_text(
    task_prompt: str,
    work_contract: WorkContract,
    *,
    context_mode: VerifiedWorkContextMode = "default",
) -> str:
    if not (isinstance(task_prompt, str) and task_prompt.strip()):
        raise ValueError(
            "build_verified_work_input_text.task_prompt must be non-empty after trimming."
        )
    if context_mode not in {
        "default",
        "off",
        "writable_files_only",
        "writable_files_plus_visible_tests",
    }:
        raise ValueError("build_verified_work_input_text.context_mode must be accepted.")
    if context_mode == "off":
        return task_prompt.strip()
    return (
        f"{task_prompt.strip()}\n\n"
        "Read-only workspace context follows. Use the existing writable-file contents and tests below as the task contract.\n"
        "Modify only the allowed paths named in the work contract.\n\n"
        f"{_build_verified_work_context_bundle(work_contract, context_mode=context_mode)}"
    )


def build_verified_work_repair_ticket(
    preservation_state: PreservationState,
    *,
    style: VerifiedWorkRepairTicketStyle = "factual",
) -> str:
    if style not in {"factual", "minimal"}:
        raise ValueError("build_verified_work_repair_ticket.style must be accepted.")
    if not isinstance(preservation_state, PreservationState):
        actual_type = type(preservation_state).__name__
        raise TypeError(
            "build_verified_work_repair_ticket.preservation_state must be PreservationState, "
            f"got {actual_type}."
        )
    trusted_checks = ", ".join(sorted(preservation_state.trusted_structure.checks)) or "<none>"
    trusted_paths = ", ".join(sorted(preservation_state.trusted_structure.paths)) or "<none>"
    falsified_checks = ", ".join(sorted(preservation_state.falsified_structure.checks)) or "<none>"
    failing_tests = ", ".join(sorted(preservation_state.falsified_structure.failing_tests)) or "<none>"
    repair_surface = ", ".join(sorted(preservation_state.lawful_repair_surface)) or "<none>"
    allowed_moves = ", ".join(sorted(preservation_state.intervention_budget.allowed_moves))
    if style == "minimal":
        return (
            f"task_anchor: {preservation_state.task_anchor}\n"
            f"failure_class: {preservation_state.falsified_structure.failure_class or '<none>'}\n"
            f"falsified_checks: {falsified_checks}\n"
            f"lawful_repair_surface: {repair_surface}\n"
            f"remaining_repairs: {preservation_state.intervention_budget.remaining_repairs}\n"
            f"allowed_moves: {allowed_moves}"
        )
    return (
        f"task_anchor: {preservation_state.task_anchor}\n"
        f"trusted_checks: {trusted_checks}\n"
        f"trusted_paths: {trusted_paths}\n"
        f"failure_class: {preservation_state.falsified_structure.failure_class or '<none>'}\n"
        f"falsified_checks: {falsified_checks}\n"
        f"failing_tests: {failing_tests}\n"
        f"lawful_repair_surface: {repair_surface}\n"
        f"remaining_repairs: {preservation_state.intervention_budget.remaining_repairs}\n"
        f"allowed_moves: {allowed_moves}"
    )


def verify_verified_work_result(
    result_text: str | None,
    work_contract: WorkContract,
    *,
    preserved_file_map: dict[str, str] | None = None,
    verifier_contract: WorkContract | None = None,
) -> tuple[dict[str, str] | None, VerificationOutcome]:
    file_map, blocked_outcome = _parse_verified_work_result(result_text, work_contract)
    if blocked_outcome is not None:
        return file_map, blocked_outcome
    assert file_map is not None
    effective_file_map = _overlay_verified_work_file_map(
        preserved_file_map,
        file_map,
    )
    return effective_file_map, _run_verified_work_verifier(
        effective_file_map,
        verifier_contract or work_contract,
    )


def _overlay_verified_work_file_map(
    preserved_file_map: dict[str, str] | None,
    repair_file_map: dict[str, str],
) -> dict[str, str]:
    if preserved_file_map is None:
        return dict(repair_file_map)
    combined = dict(preserved_file_map)
    combined.update(repair_file_map)
    return combined


def _build_verified_work_context_bundle(
    work_contract: WorkContract,
    *,
    context_mode: VerifiedWorkContextMode = "default",
) -> str:
    profile = _verified_work_profile_spec(work_contract)
    if context_mode == "writable_files_only":
        context_paths = tuple(work_contract.allowed_write_paths)
    else:
        context_paths = tuple(work_contract.allowed_write_paths) + profile.read_only_context_paths
    rendered_blocks: list[str] = []
    for relative_path in context_paths:
        source_path = profile.template_root / relative_path
        if not source_path.is_file():
            raise RuntimeError(
                "verified-work context file is missing from the selected template: "
                f"{relative_path}"
            )
        file_text = source_path.read_text(encoding="utf-8").rstrip()
        rendered_blocks.append(
            "\n".join(
                (
                    f"=== CONTEXT FILE: {relative_path} ===",
                    file_text,
                    "=== END CONTEXT FILE ===",
                )
            )
        )
    return "\n\n".join(rendered_blocks)


def _parse_verified_work_result(
    result_text: str | None,
    work_contract: WorkContract,
) -> tuple[dict[str, str] | None, VerificationOutcome | None]:
    if result_text is None or not result_text.strip():
        return None, VerificationOutcome(
            status="failed",
            failure_class="output_invalid",
            parse_error="result_text was empty.",
        )
    lines = result_text.strip().splitlines()
    file_map: dict[str, str] = {}
    blocked_reason: str | None = None
    blocked_message: str | None = None
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        file_match = _FILE_HEADER_RE.match(line)
        blocked_match = _BLOCKED_HEADER_RE.match(line)
        if file_match is not None:
            if blocked_reason is not None:
                return None, VerificationOutcome(
                    status="failed",
                    failure_class="output_invalid",
                    parse_error="blocked markers may not be mixed with file blocks.",
                )
            path = file_match.group("path").strip()
            if path not in work_contract.allowed_write_paths:
                return None, VerificationOutcome(
                    status="failed",
                    failure_class="output_invalid",
                    parse_error=f"unapproved write path: {path}",
                )
            if path in file_map:
                return None, VerificationOutcome(
                    status="failed",
                    failure_class="output_invalid",
                    parse_error=f"duplicate file block for {path}",
                )
            index += 1
            content_lines: list[str] = []
            while index < len(lines) and lines[index] != _END_FILE_MARKER:
                content_lines.append(lines[index])
                index += 1
            if index >= len(lines):
                return None, VerificationOutcome(
                    status="failed",
                    failure_class="output_invalid",
                    parse_error=f"missing end marker for {path}",
                )
            file_map[path] = "\n".join(content_lines)
            index += 1
            continue
        if blocked_match is not None:
            if file_map:
                return None, VerificationOutcome(
                    status="failed",
                    failure_class="output_invalid",
                    parse_error="file blocks may not be mixed with blocked markers.",
                )
            if blocked_reason is not None:
                return None, VerificationOutcome(
                    status="failed",
                    failure_class="output_invalid",
                    parse_error="only one blocked marker is allowed.",
                )
            blocked_reason = BLOCKED_REASON_MAP[blocked_match.group("reason")]
            index += 1
            message_lines: list[str] = []
            while index < len(lines) and lines[index] != _END_BLOCKED_MARKER:
                message_lines.append(lines[index])
                index += 1
            if index >= len(lines):
                return None, VerificationOutcome(
                    status="failed",
                    failure_class="output_invalid",
                    parse_error="missing blocked end marker.",
                )
            blocked_message = "\n".join(message_lines).strip()
            if not blocked_message:
                return None, VerificationOutcome(
                    status="failed",
                    failure_class="output_invalid",
                    parse_error="blocked marker requires a message.",
                )
            index += 1
            continue
        return None, VerificationOutcome(
            status="failed",
            failure_class="output_invalid",
            parse_error=f"unexpected text outside protocol blocks: {line}",
        )
    if blocked_reason is not None:
        return None, VerificationOutcome(
            status="blocked",
            failure_class=blocked_reason,
            blocked_message=blocked_message,
        )
    if not file_map:
        return None, VerificationOutcome(
            status="failed",
            failure_class="output_invalid",
            parse_error="no file blocks were produced.",
        )
    return file_map, None


def _run_verified_work_verifier(
    file_map: dict[str, str],
    work_contract: WorkContract,
) -> VerificationOutcome:
    profile = _verified_work_profile_spec(work_contract)
    with tempfile.TemporaryDirectory(prefix="cortex-openai-verified-work-") as tmpdir:
        project_root = Path(tmpdir) / "workspace"
        shutil.copytree(profile.template_root, project_root)
        for relative_path, content in file_map.items():
            destination = project_root / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content, encoding="utf-8")

        parsed_paths = tuple(file_map)
        python_bin = _prepare_verified_work_python(project_root)
        if profile.import_target is not None:
            import_command = [
                str(python_bin),
                "-c",
                (
                    "import importlib; "
                    f"importlib.import_module('{profile.import_target}')"
                ),
            ]
            import_result = _run_command(import_command, cwd=project_root)
            if import_result.returncode != 0:
                return VerificationOutcome(
                    status="failed",
                    failure_class="import_smoke_failed",
                    parsed_paths=parsed_paths,
                    import_smoke_ok=False,
                    import_smoke_excerpt=_first_relevant_excerpt(_command_output(import_result)),
                    first_failure_excerpt=_first_relevant_excerpt(_command_output(import_result)),
                )

        pytest_result = _run_command(
            [str(python_bin), *profile.pytest_command],
            cwd=project_root,
        )
        pytest_output = _command_output(pytest_result)
        passed_count = _extract_pytest_count(_PASSED_RE, pytest_output)
        failed_count = _extract_pytest_count(_FAILED_RE, pytest_output)
        failing_tests = tuple(dict.fromkeys(_FAILING_TEST_RE.findall(pytest_output)))
        if pytest_result.returncode != 0:
            return VerificationOutcome(
                status="failed",
                failure_class="test_failed",
                parsed_paths=parsed_paths,
                import_smoke_ok=True,
                pytest_ok=False,
                pytest_exit_code=pytest_result.returncode,
                pytest_passed=passed_count,
                pytest_failed=failed_count,
                failing_tests=failing_tests,
                first_failure_excerpt=_first_relevant_excerpt(pytest_output),
            )
        return VerificationOutcome(
            status="passed",
            failure_class=None,
            parsed_paths=parsed_paths,
            import_smoke_ok=True,
            pytest_ok=True,
            pytest_exit_code=pytest_result.returncode,
            pytest_passed=passed_count,
            pytest_failed=failed_count,
        )


def _run_command(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    pythonpath_parts = [str(cwd / "src")]
    existing_pythonpath = env.get("PYTHONPATH")
    if existing_pythonpath:
        pythonpath_parts.append(existing_pythonpath)
    env["PYTHONPATH"] = os.pathsep.join(pythonpath_parts)
    return subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=120,
        env=env,
    )


def _prepare_verified_work_python(project_root: Path) -> Path:
    venv_root = project_root / _VENV_DIR_NAME
    python_bin = _venv_python_path(venv_root)
    if python_bin.exists():
        return python_bin
    venv_result = subprocess.run(
        [_PYTHON_BIN, "-m", "venv", str(venv_root)],
        cwd=project_root,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if venv_result.returncode != 0:
        raise RuntimeError(
            "failed to create verified-work venv: "
            f"{_command_output(venv_result) or '<no output>'}"
        )
    install_result = subprocess.run(
        [
            str(python_bin),
            "-m",
            "pip",
            "install",
            "--quiet",
            "-e",
            ".[test]",
            "pytest",
        ],
        cwd=project_root,
        capture_output=True,
        text=True,
        timeout=300,
        env={
            **os.environ,
            "PIP_DISABLE_PIP_VERSION_CHECK": "1",
        },
    )
    if install_result.returncode != 0:
        raise RuntimeError(
            "failed to install verified-work dependencies: "
            f"{_command_output(install_result) or '<no output>'}"
        )
    return python_bin


def _venv_python_path(venv_root: Path) -> Path:
    if os.name == "nt":
        return venv_root / "Scripts" / "python.exe"
    return venv_root / "bin" / "python"


def _extract_pytest_count(pattern: re.Pattern[str], output: str) -> int | None:
    match = pattern.search(output)
    if match is None:
        return 0 if "no tests ran" in output else None
    return int(match.group("count"))


def _command_output(result: subprocess.CompletedProcess[str]) -> str:
    return "\n".join(part for part in (result.stdout, result.stderr) if part).strip()


def _first_relevant_excerpt(output: str) -> str | None:
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("E   ") or line.startswith("FAILED ") or line.startswith("ERROR "):
            return line
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if line:
            return line
    return None


def _verified_work_profile_spec(work_contract: WorkContract) -> VerifiedWorkProfileSpec:
    try:
        return _VERIFIED_WORK_PROFILE_REGISTRY[work_contract.verification_profile]
    except KeyError as exc:  # pragma: no cover - WorkContract validation owns legality.
        raise RuntimeError(
            "verified-work profile registry is missing the active profile: "
            f"{work_contract.verification_profile}"
        ) from exc


__all__ = [
    "BLOCKED_REASON_MAP",
    "build_verified_work_input_text",
    "build_verified_work_instructions",
    "build_verified_work_repair_ticket",
    "verify_verified_work_result",
]
