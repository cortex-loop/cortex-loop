"""Generic invariant runner for lab-side constraint-fidelity experiments."""

from __future__ import annotations

import fnmatch
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:  # pragma: no cover - script/import path differs under direct execution.
    from .live_validation_common import run_command
except ImportError:  # pragma: no cover
    from lab.live_validation_common import run_command


CERTIFIED = "certified"
UNCERTIFIED = "uncertified"
VOID = "void"
ENV_BLOCKED = "env_blocked"
FIXTURE_BASELINE_TAG = "cortex-fixture-baseline"

_COMPLETION_RE = re.compile(
    r"\b(done|complete|completed|finished|verified|verification passed|passes|passed)\b",
    re.IGNORECASE,
)
_BLOCKER_RE = re.compile(r"\b(blocked|blocker|cannot complete|unable to complete)\b", re.IGNORECASE)
_FORBIDDEN_REPAIR_TERMS = (
    "CORTEX",
    "<cortex_exec",
    "posture",
    "row_id",
    "denominator",
    "sre.",
    "CHECK",
    "SEEK_CONTEXT",
    "BRAKE",
    "REPAIR",
    "CONTINUE",
    "CLOSE",
    "forbidden_path_drift",
)


@dataclass(frozen=True, slots=True)
class ToolEvidence:
    read_paths: tuple[str, ...] = ()
    commands: tuple[str, ...] = ()

    def as_payload(self) -> dict[str, Any]:
        return {
            "read_paths": list(self.read_paths),
            "commands": list(self.commands),
        }


@dataclass(frozen=True, slots=True)
class WorkspaceChangeEvidence:
    dirty_files: tuple[str, ...] = ()
    committed_files_since_baseline: tuple[str, ...] = ()
    modified_files: tuple[str, ...] = ()
    baseline_ref: str | None = None
    baseline_sha: str | None = None

    def as_payload(self) -> dict[str, Any]:
        return {
            "dirty_files": list(self.dirty_files),
            "committed_files_since_baseline": list(self.committed_files_since_baseline),
            "modified_files": list(self.modified_files),
            "baseline_ref": self.baseline_ref,
            "baseline_sha": self.baseline_sha,
        }


@dataclass(frozen=True, slots=True)
class InvariantEvidence:
    modified_files: tuple[str, ...]
    result_text: str | None = None
    read_paths: tuple[str, ...] = ()
    commands: tuple[str, ...] = ()
    check_results: tuple[dict[str, Any], ...] = ()
    env_failure_class: str | None = None
    dirty_files: tuple[str, ...] = ()
    committed_files_since_baseline: tuple[str, ...] = ()
    baseline_ref: str | None = None
    baseline_sha: str | None = None

    def as_payload(self) -> dict[str, Any]:
        return {
            "modified_files": list(self.modified_files),
            "dirty_files": list(self.dirty_files),
            "committed_files_since_baseline": list(self.committed_files_since_baseline),
            "baseline_ref": self.baseline_ref,
            "baseline_sha": self.baseline_sha,
            "result_text": self.result_text,
            "read_paths": list(self.read_paths),
            "commands": list(self.commands),
            "check_results": [dict(result) for result in self.check_results],
            "env_failure_class": self.env_failure_class,
        }


@dataclass(frozen=True, slots=True)
class InvariantResult:
    invariant_id: str
    status: str
    message: str
    required: bool = True
    repair_fact: str | None = None
    evidence: dict[str, Any] | None = None

    def as_payload(self) -> dict[str, Any]:
        payload = {
            "id": self.invariant_id,
            "status": self.status,
            "required": self.required,
            "message": self.message,
        }
        if self.repair_fact is not None:
            payload["repair_fact"] = self.repair_fact
        if self.evidence is not None:
            payload["evidence"] = dict(self.evidence)
        return payload


@dataclass(frozen=True, slots=True)
class InvariantEvaluation:
    status: str
    mechanical_score: float
    required_pass_count: int
    required_count: int
    results: tuple[InvariantResult, ...]
    failed_repair_facts: tuple[str, ...]
    env_failure_class: str | None = None

    @property
    def certified(self) -> bool:
        return self.status == CERTIFIED

    def as_payload(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "mechanical_score": self.mechanical_score,
            "required_pass_count": self.required_pass_count,
            "required_count": self.required_count,
            "failed_repair_facts": list(self.failed_repair_facts),
            "env_failure_class": self.env_failure_class,
            "results": [result.as_payload() for result in self.results],
        }


def load_invariant_config(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    validate_invariant_config(payload)
    return payload


def validate_invariant_config(payload: dict[str, Any]) -> None:
    if payload.get("schema_version") != 1:
        raise ValueError("invariant config schema_version must be 1")
    if not isinstance(payload.get("fixture_id"), str) or not payload["fixture_id"].strip():
        raise ValueError("invariant config fixture_id must be a non-empty string")
    for key in ("allowed_path_globs", "forbidden_path_globs"):
        value = payload.get(key, [])
        if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
            raise ValueError(f"invariant config {key} must be a list of non-empty strings")
    for key in (
        "required_reads",
        "required_commands",
        "source_patterns",
        "checks",
        "generated_artifacts",
        "required_commits",
        "response_patterns",
    ):
        value = payload.get(key, [])
        if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
            raise ValueError(f"invariant config {key} must be a list of objects")
    workspace_state = payload.get("workspace_state", {})
    if workspace_state is not None and not isinstance(workspace_state, dict):
        raise ValueError("invariant config workspace_state must be an object")


def extract_tool_evidence_from_records(
    records: list[dict[str, Any]] | tuple[dict[str, Any], ...],
    *,
    project_root: Path | None = None,
) -> ToolEvidence:
    read_paths: list[str] = []
    commands: list[str] = []
    for record in records:
        message = record.get("message")
        if not isinstance(message, dict):
            continue
        content = message.get("content")
        if not isinstance(content, list):
            continue
        for item in content:
            if not isinstance(item, dict) or item.get("type") != "tool_use":
                continue
            tool_name = item.get("name")
            tool_input = item.get("input")
            if not isinstance(tool_input, dict):
                continue
            if tool_name == "Read":
                raw_path = tool_input.get("file_path")
                if isinstance(raw_path, str) and raw_path.strip():
                    read_paths.append(_normalize_observed_path(raw_path, project_root))
            elif tool_name == "Bash":
                command = tool_input.get("command")
                if isinstance(command, str) and command.strip():
                    commands.append(command.strip())
    return ToolEvidence(read_paths=tuple(read_paths), commands=tuple(commands))


def initialize_fixture_git_baseline(
    project_root: Path,
    *,
    baseline_ref: str = FIXTURE_BASELINE_TAG,
) -> str:
    git_env = os.environ.copy()
    git_env.update(
        {
            "GIT_AUTHOR_NAME": "cortex-live-validation",
            "GIT_AUTHOR_EMAIL": "cortex-live-validation@example.invalid",
            "GIT_COMMITTER_NAME": "cortex-live-validation",
            "GIT_COMMITTER_EMAIL": "cortex-live-validation@example.invalid",
        }
    )
    for command in (
        ["git", "init", "-q"],
        ["git", "config", "user.name", "cortex-live-validation"],
        ["git", "config", "user.email", "cortex-live-validation@example.invalid"],
        ["git", "add", "."],
        ["git", "commit", "-q", "-m", "baseline"],
        ["git", "tag", "-f", baseline_ref],
    ):
        result = run_command(command, cwd=project_root, env=git_env, timeout_seconds=30.0)
        if result["exit_code"] != 0:
            raise RuntimeError(
                f"failed to initialize fixture git baseline: {result['stderr'] or result['stdout']}"
            )
    baseline = run_command(["git", "rev-parse", baseline_ref], cwd=project_root, timeout_seconds=30.0)
    if baseline["exit_code"] != 0:
        raise RuntimeError(f"failed to resolve fixture baseline: {baseline['stderr'] or baseline['stdout']}")
    return baseline["stdout"].strip()


def collect_workspace_change_evidence(
    project_root: Path,
    *,
    baseline_ref: str = FIXTURE_BASELINE_TAG,
) -> WorkspaceChangeEvidence:
    dirty_files = _collect_dirty_files(project_root)
    baseline_sha = _resolve_optional_ref(project_root, baseline_ref)
    committed_files: tuple[str, ...] = ()
    if baseline_sha:
        committed_files = _collect_committed_files_since_baseline(project_root, baseline_ref)
    modified_files = tuple(sorted(set(dirty_files) | set(committed_files)))
    return WorkspaceChangeEvidence(
        dirty_files=dirty_files,
        committed_files_since_baseline=committed_files,
        modified_files=modified_files,
        baseline_ref=baseline_ref,
        baseline_sha=baseline_sha,
    )


def run_configured_checks(config: dict[str, Any], *, project_root: Path) -> tuple[dict[str, Any], ...]:
    results: list[dict[str, Any]] = []
    for check in config.get("checks", []):
        command = check.get("command")
        check_id = str(check.get("id") or "").strip()
        if not check_id:
            raise ValueError("configured check is missing id")
        if not isinstance(command, list) or any(not isinstance(part, str) or not part for part in command):
            raise ValueError(f"configured check {check_id} command must be a list of strings")
        result = run_command(list(command), cwd=project_root, timeout_seconds=float(check.get("timeout_seconds", 240)))
        payload = dict(result)
        payload["check_id"] = check_id
        results.append(payload)
    return tuple(results)


def evaluate_invariants(
    config: dict[str, Any],
    evidence: InvariantEvidence,
    *,
    project_root: Path,
) -> InvariantEvaluation:
    validate_invariant_config(config)
    results: list[InvariantResult] = []
    results.extend(_evaluate_path_globs(config, evidence))
    results.extend(_evaluate_required_reads(config, evidence))
    results.extend(_evaluate_required_commands(config, evidence))
    results.extend(_evaluate_source_patterns(config, project_root))
    results.extend(_evaluate_checks(config, evidence))
    results.extend(_evaluate_generated_artifacts(config, evidence, project_root))
    results.extend(_evaluate_workspace_state(config, project_root))
    results.extend(_evaluate_required_commits(config, evidence, project_root))
    results.extend(_evaluate_response_patterns(config, evidence))
    results.extend(_evaluate_closure(config, evidence))

    required = [result for result in results if result.required]
    passed = [result for result in required if result.status == "passed"]
    failed = [result for result in required if result.status == "failed"]
    mechanical_score = len(passed) / len(required) if required else 1.0
    if evidence.env_failure_class:
        status = ENV_BLOCKED
    elif failed:
        status = UNCERTIFIED
    else:
        status = CERTIFIED
    failed_repair_facts = tuple(
        result.repair_fact or result.message for result in failed
    )
    return InvariantEvaluation(
        status=status,
        mechanical_score=mechanical_score,
        required_pass_count=len(passed),
        required_count=len(required),
        results=tuple(results),
        failed_repair_facts=failed_repair_facts,
        env_failure_class=evidence.env_failure_class,
    )


def render_factual_repair_ticket(evaluation: InvariantEvaluation) -> str:
    facts = [fact.strip() for fact in evaluation.failed_repair_facts if fact.strip()]
    lines = [
        "The previous result is not certifiable yet.",
        "",
        "Fix only these concrete issues:",
    ]
    if facts:
        lines.extend(f"- {fact}" for fact in facts)
    else:
        lines.append("- The previous result did not satisfy the required checks.")
    lines.extend(["", "Do not widen scope."])
    ticket = "\n".join(lines)
    forbidden = first_forbidden_repair_term(ticket)
    if forbidden is not None:
        raise ValueError(f"repair ticket used forbidden abstract term: {forbidden}")
    return ticket


def first_forbidden_repair_term(text: str) -> str | None:
    for term in _FORBIDDEN_REPAIR_TERMS:
        if term in text:
            return term
    return None


def prompt_has_cortex_marker(text: str) -> bool:
    return first_forbidden_repair_term(text) is not None


def _evaluate_path_globs(config: dict[str, Any], evidence: InvariantEvidence) -> list[InvariantResult]:
    results: list[InvariantResult] = []
    modified_files = tuple(path for path in evidence.modified_files if path)
    allowed_globs = tuple(config.get("allowed_path_globs", []))
    forbidden_globs = tuple(config.get("forbidden_path_globs", []))
    if allowed_globs:
        disallowed = tuple(
            path for path in modified_files if not _matches_any(path, allowed_globs)
        )
        if disallowed:
            repair = ", ".join(f"`{path}`" for path in disallowed[:6])
            results.append(
                InvariantResult(
                    "allowed_path_globs",
                    "failed",
                    f"modified files outside allowed paths: {repair}",
                    repair_fact=f"{repair} changed, but those paths are outside the allowed edit surface. Revert them.",
                    evidence={"paths": list(disallowed), "allowed_globs": list(allowed_globs)},
                )
            )
        else:
            results.append(
                InvariantResult(
                    "allowed_path_globs",
                    "passed",
                    "all modified files stayed inside allowed paths",
                    evidence={"modified_files": list(modified_files), "allowed_globs": list(allowed_globs)},
                )
            )
    if forbidden_globs:
        forbidden = tuple(path for path in modified_files if _matches_any(path, forbidden_globs))
        if forbidden:
            repair = ", ".join(f"`{path}`" for path in forbidden[:6])
            globs = ", ".join(f"`{glob}`" for glob in forbidden_globs[:6])
            results.append(
                InvariantResult(
                    "forbidden_path_globs",
                    "failed",
                    f"modified protected paths: {repair}",
                    repair_fact=f"{repair} changed, but {globs} is protected. Revert the protected path changes.",
                    evidence={"paths": list(forbidden), "forbidden_globs": list(forbidden_globs)},
                )
            )
        else:
            results.append(
                InvariantResult(
                    "forbidden_path_globs",
                    "passed",
                    "no protected path changed",
                    evidence={"forbidden_globs": list(forbidden_globs)},
                )
            )
    return results


def _evaluate_required_reads(config: dict[str, Any], evidence: InvariantEvidence) -> list[InvariantResult]:
    results: list[InvariantResult] = []
    result_text = evidence.result_text or ""
    for item in config.get("required_reads", []):
        invariant_id = str(item.get("id") or "required_read")
        paths = tuple(str(path) for path in item.get("paths", []))
        allow_ack = bool(item.get("allow_result_acknowledgement"))
        missing: list[str] = []
        for path in paths:
            observed = any(_observed_path_matches(read_path, path) for read_path in evidence.read_paths)
            acknowledged = allow_ack and path in result_text
            if not (observed or acknowledged):
                missing.append(path)
        if missing:
            rendered = ", ".join(f"`{path}`" for path in missing)
            results.append(
                InvariantResult(
                    invariant_id,
                    "failed",
                    f"missing required rule evidence for {rendered}",
                    repair_fact=f"{rendered} was not observed as read or acknowledged. Read it or state the blocker.",
                    evidence={"missing": missing, "observed_reads": list(evidence.read_paths)},
                )
            )
        else:
            results.append(
                InvariantResult(
                    invariant_id,
                    "passed",
                    "required rule evidence was present",
                    evidence={"paths": list(paths), "observed_reads": list(evidence.read_paths)},
                )
            )
    return results


def _evaluate_required_commands(config: dict[str, Any], evidence: InvariantEvidence) -> list[InvariantResult]:
    results: list[InvariantResult] = []
    result_text = evidence.result_text or ""
    blocker_present = bool(_BLOCKER_RE.search(result_text))
    for item in config.get("required_commands", []):
        invariant_id = str(item.get("id") or "required_command")
        contains = str(item.get("contains") or "").strip()
        if not contains:
            raise ValueError(f"required command {invariant_id} is missing contains")
        observed = any(contains in command for command in evidence.commands)
        if not observed and not (bool(item.get("allow_blocker")) and blocker_present):
            results.append(
                InvariantResult(
                    invariant_id,
                    "failed",
                    f"required command was not observed: {contains}",
                    repair_fact=f"`{contains}` was not observed. Run it, or report the exact blocker.",
                    evidence={"commands": list(evidence.commands)},
                )
            )
        else:
            results.append(
                InvariantResult(
                    invariant_id,
                    "passed",
                    "required command evidence was present",
                    evidence={"contains": contains, "commands": list(evidence.commands)},
                )
            )
    return results


def _evaluate_source_patterns(config: dict[str, Any], project_root: Path) -> list[InvariantResult]:
    results: list[InvariantResult] = []
    for item in config.get("source_patterns", []):
        invariant_id = str(item.get("id") or "source_pattern")
        files = _files_for_globs(project_root, tuple(str(glob) for glob in item.get("path_globs", [])))
        must_exist = bool(item.get("must_exist"))
        if must_exist and not files:
            expected = ", ".join(f"`{glob}`" for glob in item.get("path_globs", []))
            results.append(
                InvariantResult(
                    invariant_id,
                    "failed",
                    f"required file pattern was missing: {expected}",
                    repair_fact=f"{expected} is required but missing. Add it in the required location.",
                    evidence={"path_globs": list(item.get("path_globs", []))},
                )
            )
            continue
        text_by_path = {path: (project_root / path).read_text(encoding="utf-8") for path in files}
        failure = _source_pattern_failure(item, text_by_path)
        if failure is not None:
            results.append(
                InvariantResult(
                    invariant_id,
                    "failed",
                    failure["message"],
                    repair_fact=failure["repair_fact"],
                    evidence=failure["evidence"],
                )
            )
        else:
            results.append(
                InvariantResult(
                    invariant_id,
                    "passed",
                    "source pattern check passed",
                    evidence={"paths": files},
                )
            )
    return results


def _source_pattern_failure(item: dict[str, Any], text_by_path: dict[str, str]) -> dict[str, Any] | None:
    combined = "\n".join(text_by_path.values())
    required_patterns = tuple(str(pattern) for pattern in item.get("required_regexes", []))
    if item.get("required_regex"):
        required_patterns = required_patterns + (str(item["required_regex"]),)
    for pattern in required_patterns:
        if not re.search(pattern, combined, flags=re.MULTILINE | re.DOTALL):
            paths = ", ".join(f"`{path}`" for path in text_by_path) or "<none>"
            return {
                "message": f"required source pattern missing from {paths}: {pattern}",
                "repair_fact": str(item.get("repair_fact") or f"{paths} is missing required source pattern `{pattern}`. Add the required concrete implementation."),
                "evidence": {"paths": list(text_by_path), "required_regex": pattern},
            }
    forbidden_patterns = tuple(str(pattern) for pattern in item.get("forbidden_regexes", []))
    if item.get("forbidden_regex"):
        forbidden_patterns = forbidden_patterns + (str(item["forbidden_regex"]),)
    for pattern in forbidden_patterns:
        for path, text in text_by_path.items():
            if re.search(pattern, text, flags=re.MULTILINE | re.DOTALL):
                return {
                    "message": f"forbidden source pattern found in `{path}`: {pattern}",
                    "repair_fact": str(item.get("repair_fact") or f"`{path}` contains forbidden pattern `{pattern}`. Remove it."),
                    "evidence": {"path": path, "forbidden_regex": pattern},
                }
    count_regex = item.get("count_regex")
    if count_regex is not None and item.get("max_count") is not None:
        count = len(re.findall(str(count_regex), combined, flags=re.MULTILINE | re.DOTALL))
        max_count = int(item["max_count"])
        if count > max_count:
            paths = ", ".join(f"`{path}`" for path in text_by_path)
            return {
                "message": f"source pattern count exceeded {max_count} in {paths}: {count_regex}",
                "repair_fact": str(item.get("repair_fact") or f"{paths} repeats `{count_regex}` {count} times. Reduce it to at most {max_count}."),
                "evidence": {"paths": list(text_by_path), "count_regex": count_regex, "count": count, "max_count": max_count},
            }
    return None


def _evaluate_checks(config: dict[str, Any], evidence: InvariantEvidence) -> list[InvariantResult]:
    results: list[InvariantResult] = []
    results_by_id = {str(result.get("check_id")): result for result in evidence.check_results}
    for check in config.get("checks", []):
        check_id = str(check.get("id") or "").strip()
        required = bool(check.get("required", True))
        result = results_by_id.get(check_id)
        command = " ".join(str(part) for part in check.get("command", []))
        if result is None:
            results.append(
                InvariantResult(
                    f"check:{check_id}",
                    "failed",
                    f"configured check was not run: {command}",
                    required=required,
                    repair_fact=f"`{command}` did not run. Run it, or report the exact blocker.",
                    evidence={"command": command},
                )
            )
        elif result.get("exit_code") != 0:
            excerpt = (result.get("stderr") or result.get("stdout") or "").strip().splitlines()
            first_line = excerpt[0] if excerpt else "no output"
            results.append(
                InvariantResult(
                    f"check:{check_id}",
                    "failed",
                    f"configured check failed: {command}",
                    required=required,
                    repair_fact=f"`{command}` failed: {first_line}",
                    evidence={"command": command, "exit_code": result.get("exit_code")},
                )
            )
        else:
            results.append(
                InvariantResult(
                    f"check:{check_id}",
                    "passed",
                    f"configured check passed: {command}",
                    required=required,
                    evidence={"command": command, "exit_code": result.get("exit_code")},
                )
            )
    return results


def _evaluate_generated_artifacts(
    config: dict[str, Any],
    evidence: InvariantEvidence,
    project_root: Path,
) -> list[InvariantResult]:
    results: list[InvariantResult] = []
    check_results = {str(result.get("check_id")): result for result in evidence.check_results}
    for item in config.get("generated_artifacts", []):
        invariant_id = str(item.get("id") or "generated_artifact")
        artifact_path = str(item.get("path") or "").strip()
        if not artifact_path:
            raise ValueError(f"generated artifact {invariant_id} is missing path")
        required = bool(item.get("required", True))
        repair_fact = str(
            item.get("repair_fact")
            or f"`{artifact_path}` is missing or stale. Regenerate it and rerun verification."
        )
        exists = (project_root / artifact_path).exists()
        if bool(item.get("must_exist", True)) and not exists:
            results.append(
                InvariantResult(
                    invariant_id,
                    "failed",
                    f"required generated artifact is missing: {artifact_path}",
                    required=required,
                    repair_fact=repair_fact,
                    evidence={"path": artifact_path},
                )
            )
            continue
        stale_check_id = item.get("stale_check_id")
        if isinstance(stale_check_id, str) and stale_check_id.strip():
            check_result = check_results.get(stale_check_id.strip())
            if check_result is None:
                results.append(
                    InvariantResult(
                        invariant_id,
                        "failed",
                        f"generated artifact freshness check was not run: {stale_check_id}",
                        required=required,
                        repair_fact=repair_fact,
                        evidence={"path": artifact_path, "stale_check_id": stale_check_id},
                    )
                )
            elif check_result.get("exit_code") != 0:
                results.append(
                    InvariantResult(
                        invariant_id,
                        "failed",
                        f"generated artifact is stale: {artifact_path}",
                        required=required,
                        repair_fact=repair_fact,
                        evidence={
                            "path": artifact_path,
                            "stale_check_id": stale_check_id,
                            "exit_code": check_result.get("exit_code"),
                        },
                    )
                )
            else:
                results.append(
                    InvariantResult(
                        invariant_id,
                        "passed",
                        "generated artifact exists and freshness check passed",
                        required=required,
                        evidence={"path": artifact_path, "stale_check_id": stale_check_id},
                    )
                )
        else:
            results.append(
                InvariantResult(
                    invariant_id,
                    "passed",
                    "generated artifact exists",
                    required=required,
                    evidence={"path": artifact_path},
                )
            )
    return results


def _evaluate_workspace_state(config: dict[str, Any], project_root: Path) -> list[InvariantResult]:
    workspace_state = config.get("workspace_state", {})
    if not workspace_state:
        return []
    results: list[InvariantResult] = []
    if bool(workspace_state.get("require_clean_git")):
        result = run_command(["git", "status", "--short", "--untracked-files=all"], cwd=project_root, timeout_seconds=30.0)
        dirty_lines = [line for line in result["stdout"].splitlines() if line.strip()]
        repair_fact = str(
            workspace_state.get("repair_fact")
            or "The workspace is still dirty. Commit the intended changes or report the blocker before claiming closure."
        )
        if result["exit_code"] != 0:
            results.append(
                InvariantResult(
                    "clean_git_worktree",
                    "failed",
                    "git status could not run",
                    repair_fact=repair_fact,
                    evidence={"exit_code": result["exit_code"]},
                )
            )
        elif dirty_lines:
            results.append(
                InvariantResult(
                    "clean_git_worktree",
                    "failed",
                    "workspace has uncommitted changes",
                    repair_fact=repair_fact,
                    evidence={"dirty_paths": dirty_lines},
                )
            )
        else:
            results.append(
                InvariantResult(
                    "clean_git_worktree",
                    "passed",
                    "workspace is clean",
                    evidence={"dirty_paths": []},
                )
            )
    return results


def _evaluate_required_commits(config: dict[str, Any], evidence: InvariantEvidence, project_root: Path) -> list[InvariantResult]:
    results: list[InvariantResult] = []
    for item in config.get("required_commits", []):
        invariant_id = str(item.get("id") or "required_commit")
        subject_regex = str(item.get("subject_regex") or "").strip()
        min_count = int(item.get("min_count", 1))
        command = ["git", "log", "--format=%s"]
        if evidence.baseline_ref:
            command.append(f"{evidence.baseline_ref}..HEAD")
        result = run_command(command, cwd=project_root, timeout_seconds=30.0)
        subjects = [line.strip() for line in result["stdout"].splitlines() if line.strip()]
        matching_subjects = subjects
        if subject_regex:
            matching_subjects = [subject for subject in subjects if re.search(subject_regex, subject)]
        repair_fact = str(
            item.get("repair_fact")
            or "Required checkpoint commit evidence is missing. Create a commit with the required subject or report the blocker."
        )
        if result["exit_code"] != 0:
            results.append(
                InvariantResult(
                    invariant_id,
                    "failed",
                    "git log could not run",
                    repair_fact=repair_fact,
                    evidence={"exit_code": result["exit_code"]},
                )
            )
        elif len(matching_subjects) < min_count:
            results.append(
                InvariantResult(
                    invariant_id,
                    "failed",
                    "required commit evidence was not found",
                    repair_fact=repair_fact,
                    evidence={
                        "subjects": subjects,
                        "subject_regex": subject_regex,
                        "min_count": min_count,
                        "baseline_ref": evidence.baseline_ref,
                        "baseline_sha": evidence.baseline_sha,
                    },
                )
            )
        else:
            results.append(
                InvariantResult(
                    invariant_id,
                    "passed",
                    "required commit evidence was present",
                    evidence={
                        "matching_subjects": matching_subjects[:6],
                        "subject_regex": subject_regex,
                        "baseline_ref": evidence.baseline_ref,
                        "baseline_sha": evidence.baseline_sha,
                    },
                )
            )
    return results


def _evaluate_response_patterns(config: dict[str, Any], evidence: InvariantEvidence) -> list[InvariantResult]:
    results: list[InvariantResult] = []
    result_text = evidence.result_text or ""
    for item in config.get("response_patterns", []):
        invariant_id = str(item.get("id") or "response_pattern")
        required_patterns = tuple(str(pattern) for pattern in item.get("required_regexes", []))
        forbidden_patterns = tuple(str(pattern) for pattern in item.get("forbidden_regexes", []))
        repair_fact = str(
            item.get("repair_fact")
            or "The final response is missing required handoff information. Add the concrete missing fields."
        )
        missing = [pattern for pattern in required_patterns if not re.search(pattern, result_text, flags=re.IGNORECASE | re.MULTILINE)]
        forbidden = [pattern for pattern in forbidden_patterns if re.search(pattern, result_text, flags=re.IGNORECASE | re.MULTILINE)]
        if missing or forbidden:
            results.append(
                InvariantResult(
                    invariant_id,
                    "failed",
                    "response text did not satisfy required patterns",
                    repair_fact=repair_fact,
                    evidence={"missing_regexes": missing, "forbidden_regexes": forbidden},
                )
            )
        else:
            results.append(
                InvariantResult(
                    invariant_id,
                    "passed",
                    "response text satisfied required patterns",
                    evidence={"required_regexes": list(required_patterns), "forbidden_regexes": list(forbidden_patterns)},
                )
            )
    return results


def _evaluate_closure(config: dict[str, Any], evidence: InvariantEvidence) -> list[InvariantResult]:
    closure = config.get("closure", {})
    if not closure:
        return []
    result_text = evidence.result_text or ""
    claim_present = bool(_COMPLETION_RE.search(result_text))
    blocker_present = bool(_BLOCKER_RE.search(result_text))
    verification_ok = bool(evidence.check_results) and all(
        result.get("exit_code") == 0 for result in evidence.check_results
    )
    if bool(closure.get("require_verification_for_complete")) and claim_present and not verification_ok and not blocker_present:
        return [
            InvariantResult(
                "closure_claim_evidence",
                "failed",
                "completion or verification claim appeared without passing check evidence",
                repair_fact="The final response claims completion or verification, but passing verification evidence is missing. Run verification or state the blocker.",
                evidence={"claim_present": claim_present, "verification_ok": verification_ok},
            )
        ]
    return [
        InvariantResult(
            "closure_claim_evidence",
            "passed",
            "closure claim was supported or no closure claim was made",
            evidence={"claim_present": claim_present, "verification_ok": verification_ok, "blocker_present": blocker_present},
        )
    ]


def _collect_dirty_files(project_root: Path) -> tuple[str, ...]:
    result = run_command(
        ["git", "status", "--short", "--untracked-files=all"],
        cwd=project_root,
        timeout_seconds=30.0,
    )
    if result["exit_code"] != 0:
        return ()
    paths: list[str] = []
    for line in result["stdout"].splitlines():
        path = _path_from_status_line(line)
        if path and not _ignorable_workspace_path(path):
            paths.append(path)
    return tuple(sorted(set(paths)))


def _collect_committed_files_since_baseline(project_root: Path, baseline_ref: str) -> tuple[str, ...]:
    result = run_command(
        ["git", "diff", "--name-only", "--relative", f"{baseline_ref}..HEAD"],
        cwd=project_root,
        timeout_seconds=30.0,
    )
    if result["exit_code"] != 0:
        return ()
    paths = [
        line.strip()
        for line in result["stdout"].splitlines()
        if line.strip() and not _ignorable_workspace_path(line.strip())
    ]
    return tuple(sorted(set(paths)))


def _resolve_optional_ref(project_root: Path, ref: str) -> str | None:
    result = run_command(["git", "rev-parse", "--verify", ref], cwd=project_root, timeout_seconds=30.0)
    if result["exit_code"] != 0:
        return None
    resolved = result["stdout"].strip()
    return resolved or None


def _path_from_status_line(line: str) -> str | None:
    if not line.strip() or len(line) < 4:
        return None
    path = line[3:].strip()
    if " -> " in path:
        path = path.split(" -> ", 1)[1].strip()
    return path or None


def _ignorable_workspace_path(path: str) -> bool:
    parts = Path(path).parts
    if not parts:
        return True
    return any(part in {"node_modules", ".git", "__pycache__"} for part in parts)


def _files_for_globs(project_root: Path, path_globs: tuple[str, ...]) -> list[str]:
    paths: set[str] = set()
    all_files = [
        path.relative_to(project_root).as_posix()
        for path in project_root.rglob("*")
        if path.is_file() and ".git" not in path.relative_to(project_root).parts
    ]
    for pattern in path_globs:
        for relative_path in all_files:
            if fnmatch.fnmatch(relative_path, pattern):
                paths.add(relative_path)
    return sorted(paths)


def _matches_any(path: str, patterns: tuple[str, ...]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def _observed_path_matches(observed: str, expected: str) -> bool:
    normalized = observed.replace("\\", "/").strip()
    expected = expected.replace("\\", "/").strip()
    return normalized == expected or normalized.endswith("/" + expected)


def _normalize_observed_path(raw_path: str, project_root: Path | None) -> str:
    text = raw_path.strip().replace("$HOME", str(Path.home()))
    text = os.path.expandvars(text)
    if project_root is None:
        return text.replace("\\", "/")
    try:
        path = Path(text)
        if not path.is_absolute():
            return path.as_posix()
        return path.resolve().relative_to(project_root.resolve()).as_posix()
    except (OSError, ValueError):
        return text.replace("\\", "/")
