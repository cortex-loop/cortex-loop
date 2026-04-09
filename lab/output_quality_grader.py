"""Hidden grading layer for the E12 comparative output-quality benchmark."""

from __future__ import annotations

import json
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cortex.runtime.openai_host_control import OpenAIHostControlRequest, run_openai_host_control

from lab.live_validation_common import classify_failure, run_command, sanitize_text
from lab.openai_operator_cli import isolated_codex_home_env, run_openai_operator_single_turn
from lab.output_quality_common import OutputQualityTaskPack


OutcomeStatus = Literal["passed", "failed", "env_blocked"]
JudgeSurface = Literal["service_api", "operator_cli"]


@dataclass(frozen=True, slots=True)
class OutputQualityEvaluation:
    status: OutcomeStatus
    failure_class: str | None
    objective_pass: bool
    hidden_quality_pass: bool
    failing_checks: tuple[str, ...]
    first_failure_excerpt: str | None
    checks: tuple[dict[str, Any], ...]

    def as_payload(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "failure_class": self.failure_class,
            "objective_pass": self.objective_pass,
            "hidden_quality_pass": self.hidden_quality_pass,
            "failing_checks": list(self.failing_checks),
            "first_failure_excerpt": self.first_failure_excerpt,
            "checks": [dict(check) for check in self.checks],
        }


@dataclass(frozen=True, slots=True)
class PairwiseJudgment:
    winner: str | None
    confidence: str
    reason_tags: tuple[str, ...]
    objective_override: bool
    raw_response: str | None = None

    def as_payload(self) -> dict[str, Any]:
        payload = {
            "winner": self.winner,
            "confidence": self.confidence,
            "reason_tags": list(self.reason_tags),
            "objective_override": self.objective_override,
        }
        if self.raw_response is not None:
            payload["raw_response"] = self.raw_response
        return payload


def evaluate_workspace(
    *,
    task_pack: OutputQualityTaskPack,
    project_root: Path,
    shared_install_result: dict[str, Any],
) -> OutputQualityEvaluation:
    if shared_install_result["exit_code"] != 0:
        failure_class = classify_failure(
            f"{shared_install_result['stderr']}\n{shared_install_result['stdout']}"
        )
        status: OutcomeStatus = "env_blocked" if failure_class is not None else "failed"
        return OutputQualityEvaluation(
            status=status,
            failure_class=failure_class or "install_failed",
            objective_pass=False,
            hidden_quality_pass=False,
            failing_checks=("install",),
            first_failure_excerpt=_failure_excerpt(shared_install_result),
            checks=(dict(shared_install_result, check_name="install"),),
        )

    checks = [dict(shared_install_result, check_name="install")]
    for check_name, command, timeout_seconds in (
        ("lint", task_pack.lint_command, 120.0),
        ("typecheck", task_pack.typecheck_command, 240.0),
        ("build", task_pack.build_command, 300.0),
        ("visible_test", task_pack.visible_test_command, 240.0),
        ("hidden_test", task_pack.hidden_test_command, 240.0),
    ):
        result = run_command(
            list(command),
            cwd=project_root,
            timeout_seconds=timeout_seconds,
        )
        checks.append(dict(result, check_name=check_name))
        if result["exit_code"] != 0:
            failure_class = _failure_class_for_check(check_name, result)
            objective_pass = check_name not in {"lint", "typecheck", "build", "visible_test"}
            return OutputQualityEvaluation(
                status="env_blocked"
                if failure_class in {"auth_missing", "quota_exhausted", "capacity_exhausted", "provider_internal_error"}
                else "failed",
                failure_class=failure_class,
                objective_pass=False if check_name != "hidden_test" else True,
                hidden_quality_pass=False,
                failing_checks=(check_name,),
                first_failure_excerpt=_failure_excerpt(result),
                checks=tuple(checks),
            )
    return OutputQualityEvaluation(
        status="passed",
        failure_class=None,
        objective_pass=True,
        hidden_quality_pass=True,
        failing_checks=(),
        first_failure_excerpt=None,
        checks=tuple(checks),
    )


def build_output_quality_repair_ticket(
    *,
    evaluation: OutputQualityEvaluation,
    allowed_write_paths: tuple[str, ...],
    style: Literal["factual", "minimal"] = "factual",
    repair_surface: tuple[str, ...] | None = None,
) -> str:
    if style not in {"factual", "minimal"}:
        raise ValueError("build_output_quality_repair_ticket.style must be accepted.")
    if repair_surface is None:
        repair_surface = allowed_write_paths
    if any(not (isinstance(path, str) and path.strip()) for path in repair_surface):
        raise ValueError(
            "build_output_quality_repair_ticket.repair_surface must contain only non-empty paths."
        )
    allowed_paths = ", ".join(allowed_write_paths) or "<none>"
    failing_checks = ", ".join(evaluation.failing_checks) or "<none>"
    if style == "minimal":
        repair_surface_text = ", ".join(repair_surface) or "<none>"
        return (
            "Repair the previous submission without widening scope.\n\n"
            f"failure_class: {evaluation.failure_class}\n"
            f"failing_checks: {failing_checks}\n"
            f"repair_surface: {repair_surface_text}"
        )
    return (
        "Repair the previous submission without widening scope.\n\n"
        f"failure_class: {evaluation.failure_class}\n"
        f"failing_checks: {failing_checks}\n"
        f"first_failure_excerpt: {evaluation.first_failure_excerpt or '<none>'}\n"
        f"allowed_write_paths: {allowed_paths}\n"
        "Fix only the reported failures and keep the change minimal."
    )


def judge_pairwise_merge_worthiness(
    *,
    prompt_text: str,
    output_a: dict[str, Any],
    output_b: dict[str, Any],
    model: str | None = None,
    surface: JudgeSurface = "service_api",
) -> PairwiseJudgment:
    evaluation_a = output_a["evaluation"]
    evaluation_b = output_b["evaluation"]
    if evaluation_a["objective_pass"] != evaluation_b["objective_pass"]:
        winner = "a" if evaluation_a["objective_pass"] else "b"
        return PairwiseJudgment(
            winner=winner,
            confidence="high",
            reason_tags=("objective-gate",),
            objective_override=True,
        )
    if not evaluation_a["objective_pass"] and not evaluation_b["objective_pass"]:
        return PairwiseJudgment(
            winner=None,
            confidence="low",
            reason_tags=("both-failed-objective",),
            objective_override=True,
        )
    if surface == "operator_cli":
        return _judge_pairwise_merge_worthiness_operator(
            prompt_text=prompt_text,
            output_a=output_a,
            output_b=output_b,
            model=model,
        )

    judge_prompt = _build_judge_prompt(
        prompt_text=prompt_text,
        output_a=output_a,
        output_b=output_b,
    )
    request = OpenAIHostControlRequest(
        action_tag="openai-response-stream",
        model=model or "gpt-5.4-mini",
        input_text=judge_prompt,
        max_output_tokens=600,
    )
    result, _ = run_openai_host_control(request)
    parsed = _parse_judge_payload(result.result_text)
    return PairwiseJudgment(
        winner=parsed["winner"],
        confidence=parsed["confidence"],
        reason_tags=tuple(parsed["reason_tags"]),
        objective_override=False,
        raw_response=result.result_text,
    )


def _judge_pairwise_merge_worthiness_operator(
    *,
    prompt_text: str,
    output_a: dict[str, Any],
    output_b: dict[str, Any],
    model: str | None,
) -> PairwiseJudgment:
    judge_prompt = _build_judge_prompt(
        prompt_text=prompt_text,
        output_a=output_a,
        output_b=output_b,
    )
    with tempfile.TemporaryDirectory(prefix="cortex-output-quality-judge-") as tmp_dir:
        judge_root = Path(tmp_dir)
        try:
            with isolated_codex_home_env() as env:
                turn = run_openai_operator_single_turn(
                    project_root=judge_root,
                    prompt=judge_prompt,
                    scenario_id="output_quality_pairwise_judge",
                    stderr_path=judge_root / "judge.stderr.log",
                    ephemeral=True,
                    env=env,
                    model=model,
                )
        except RuntimeError:
            return PairwiseJudgment(
                winner=None,
                confidence="low",
                reason_tags=("judge-env-blocked",),
                objective_override=False,
                raw_response=None,
            )
    failure_class = turn.get("failure_class")
    if isinstance(failure_class, str) and failure_class:
        return PairwiseJudgment(
            winner=None,
            confidence="low",
            reason_tags=("judge-env-blocked",),
            objective_override=False,
            raw_response=turn.get("output_text"),
        )
    parsed = _parse_judge_payload(turn.get("output_text"))
    return PairwiseJudgment(
        winner=parsed["winner"],
        confidence=parsed["confidence"],
        reason_tags=tuple(parsed["reason_tags"]),
        objective_override=False,
        raw_response=turn.get("output_text"),
    )


def _failure_class_for_check(check_name: str, result: dict[str, Any]) -> str:
    classified = classify_failure(f"{result['stderr']}\n{result['stdout']}")
    if classified is not None:
        return classified
    return {
        "lint": "lint_failed",
        "typecheck": "typecheck_failed",
        "build": "build_failed",
        "visible_test": "visible_test_failed",
        "hidden_test": "hidden_test_failed",
    }[check_name]


def _failure_excerpt(result: dict[str, Any]) -> str | None:
    combined = sanitize_text(f"{result['stderr']}\n{result['stdout']}")
    lines = [line.strip() for line in combined.splitlines() if line.strip()]
    if not lines:
        return None
    return "\n".join(lines[:6])


def _build_judge_prompt(
    *,
    prompt_text: str,
    output_a: dict[str, Any],
    output_b: dict[str, Any],
) -> str:
    return (
        "You are comparing two code submissions for the same engineering task.\n"
        "Choose the one a strong engineer would merge.\n"
        "Use only the task request, objective check summaries, hidden-quality summaries, and changed files.\n"
        "Do not infer which system produced either submission.\n"
        "Return JSON only with keys winner, confidence, reason_tags.\n"
        'winner must be "a", "b", or null.\n'
        'confidence must be "low", "medium", or "high".\n'
        "reason_tags must be a short list of stable kebab-case tags.\n\n"
        f"TASK REQUEST\n{prompt_text.strip()}\n\n"
        f"OUTPUT A\n{_render_output_for_judge(output_a)}\n\n"
        f"OUTPUT B\n{_render_output_for_judge(output_b)}"
    )


def _render_output_for_judge(output: dict[str, Any]) -> str:
    evaluation = output["evaluation"]
    changed_files = output["changed_files"]
    rendered_files = []
    for relative_path, contents in sorted(changed_files.items()):
        rendered_files.append(
            "\n".join(
                (
                    f"=== FILE: {relative_path} ===",
                    contents.rstrip(),
                    "=== END FILE ===",
                )
            )
        )
    return (
        f"objective_pass: {evaluation['objective_pass']}\n"
        f"hidden_quality_pass: {evaluation['hidden_quality_pass']}\n"
        f"failure_class: {evaluation['failure_class']}\n"
        f"failing_checks: {', '.join(evaluation['failing_checks']) or '<none>'}\n"
        f"first_failure_excerpt: {evaluation['first_failure_excerpt'] or '<none>'}\n\n"
        f"{chr(10).join(rendered_files) if rendered_files else '<no changed files>'}"
    )


def _parse_judge_payload(result_text: str | None) -> dict[str, Any]:
    if result_text is None or not result_text.strip():
        return {"winner": None, "confidence": "low", "reason_tags": ["judge-empty"]}
    stripped = result_text.strip()
    candidate = stripped
    if not candidate.startswith("{"):
        match = re.search(r"\{.*\}", stripped, re.DOTALL)
        if match is None:
            return {"winner": None, "confidence": "low", "reason_tags": ["judge-unparseable"]}
        candidate = match.group(0)
    try:
        payload = json.loads(candidate)
    except json.JSONDecodeError:
        return {"winner": None, "confidence": "low", "reason_tags": ["judge-unparseable"]}
    winner = payload.get("winner")
    if winner not in {"a", "b", None}:
        winner = None
    confidence = payload.get("confidence")
    if confidence not in {"low", "medium", "high"}:
        confidence = "low"
    reason_tags = payload.get("reason_tags")
    if not isinstance(reason_tags, list):
        reason_tags = ["judge-unparseable"]
    cleaned_tags = [
        str(tag).strip().lower().replace(" ", "-")
        for tag in reason_tags
        if isinstance(tag, str) and tag.strip()
    ][:4]
    if not cleaned_tags:
        cleaned_tags = ["judge-unparseable"]
    return {
        "winner": winner,
        "confidence": confidence,
        "reason_tags": cleaned_tags,
    }
