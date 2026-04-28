"""Live website-fixture constraint-fidelity harness.

Surface: lab
Executive Benefit: falsify or prove kernel-side constraint certification without
prompt-side Cortex doctrine.
Why this beats direct product work now: the live Claude smoke showed prompt
guidance was not enough, so this isolates external invariant gating.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:  # pragma: no cover - direct script entrypoint support.
    sys.path.insert(0, str(ROOT))

try:  # pragma: no cover - import path differs under direct execution.
    from .invariant_runner import (
        CERTIFIED,
        ENV_BLOCKED,
        UNCERTIFIED,
        InvariantEvaluation,
        InvariantEvidence,
        evaluate_invariants,
        extract_tool_evidence_from_records,
        first_forbidden_repair_term,
        load_invariant_config,
        prompt_has_cortex_marker,
        render_factual_repair_ticket,
        run_configured_checks,
    )
    from .live_validation_common import (
        MODEL_MATRIX,
        choose_model,
        classify_failure,
        ensure_live_validation_dirs,
        extract_result_text,
        extract_session_id,
        live_evidence_fields,
        now_utc_iso,
        parse_json_records,
        resolve_auth_mode,
        run_command,
        write_json,
        write_text,
    )
except ImportError:  # pragma: no cover
    from lab.invariant_runner import (
        CERTIFIED,
        ENV_BLOCKED,
        UNCERTIFIED,
        InvariantEvaluation,
        InvariantEvidence,
        evaluate_invariants,
        extract_tool_evidence_from_records,
        first_forbidden_repair_term,
        load_invariant_config,
        prompt_has_cortex_marker,
        render_factual_repair_ticket,
        run_configured_checks,
    )
    from lab.live_validation_common import (
        MODEL_MATRIX,
        choose_model,
        classify_failure,
        ensure_live_validation_dirs,
        extract_result_text,
        extract_session_id,
        live_evidence_fields,
        now_utc_iso,
        parse_json_records,
        resolve_auth_mode,
        run_command,
        write_json,
        write_text,
    )


FIXTURE_ROOT = ROOT / "tests" / "lab" / "fixtures" / "live_validation" / "website_fixture_template"
INVARIANT_CONFIG_PATH = FIXTURE_ROOT / "cortex-invariants.json"
ARTIFACT_ROOT = ROOT / ".cortex" / "live_validation" / "website_constraint_fidelity"
WORKSPACE_ROOT = ROOT / ".cortex" / "live_validation" / "workspaces" / "website_constraint_fidelity"
SCENARIO_ID = "website_fixture"
VARIANTS = ("raw_host", "kernel_only_cortex")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 -m lab.website_constraint_fidelity",
        description="Run the website-fixture constraint-fidelity experiment.",
    )
    parser.add_argument("--provider", choices=("claude",), default="claude")
    parser.add_argument("--repeat-count", type=int, default=3)
    parser.add_argument("--stage", choices=("reproduce", "kernel", "all"), default="all")
    args = parser.parse_args(argv)

    ensure_live_validation_dirs()
    summary = run_suite(
        provider=args.provider,
        repeat_count=max(1, args.repeat_count),
        stage=args.stage,
    )
    write_json(ARTIFACT_ROOT / args.provider / "summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def run_suite(*, provider: str, repeat_count: int = 3, stage: str = "all") -> dict[str, Any]:
    if provider != "claude":
        raise ValueError("website constraint fidelity currently supports Claude first")
    variants = _variants_for_stage(stage)
    runs: list[dict[str, Any]] = []
    for repeat_index in range(1, repeat_count + 1):
        for variant in variants:
            runs.append(
                run_variant(
                    provider=provider,
                    variant=variant,
                    repeat_index=repeat_index,
                )
            )
    return build_summary(
        provider=provider,
        stage=stage,
        repeat_count=repeat_count,
        runs=runs,
    )


def build_initial_prompt(*, fixture_root: Path = FIXTURE_ROOT) -> str:
    return (fixture_root / "README_TASK.md").read_text(encoding="utf-8").strip()


def run_variant(*, provider: str, variant: str, repeat_index: int) -> dict[str, Any]:
    if variant not in VARIANTS:
        raise ValueError(f"unsupported website constraint variant: {variant}")
    config = load_invariant_config(INVARIANT_CONFIG_PATH)
    project_root = prepare_workspace(provider=provider, variant=variant, repeat_index=repeat_index)
    root = ARTIFACT_ROOT / provider / variant
    prompt = build_initial_prompt()
    prompt_marker_absent = not prompt_has_cortex_marker(prompt)
    model = choose_model(provider, "operator")
    auth_mode = resolve_auth_mode(provider, "operator")
    if auth_mode != "claude_code":
        payload = _blocked_payload(
            provider=provider,
            variant=variant,
            repeat_index=repeat_index,
            model=model,
            auth_mode=auth_mode,
            prompt=prompt,
            project_root=project_root,
            reason="operator_surface_missing",
        )
        write_json(root / f"{SCENARIO_ID}__run_{repeat_index:03d}.json", payload)
        return payload

    first_turn = _run_claude_turn(
        prompt,
        project_root=project_root,
        model=model,
        auth_mode=auth_mode,
        scenario_id=SCENARIO_ID,
    )
    first_payload = _materialize_attempt(
        provider=provider,
        variant=variant,
        repeat_index=repeat_index,
        attempt_index=1,
        project_root=project_root,
        root=root,
        run_result=first_turn,
        model=model,
        auth_mode=auth_mode,
        prompt=prompt,
        config=config,
        prior_records=(),
    )

    final_payload = first_payload
    repair_turn_payload = None
    if variant == "kernel_only_cortex" and first_payload["certification"]["status"] == UNCERTIFIED:
        session_id = extract_session_id("claude", first_payload["records"])
        repair_ticket = render_factual_repair_ticket(
            _evaluation_from_payload(first_payload["certification"])
        )
        repair_forbidden_term = first_forbidden_repair_term(repair_ticket)
        if session_id and repair_forbidden_term is None:
            repair_turn = _run_claude_turn(
                repair_ticket,
                project_root=project_root,
                model=model,
                auth_mode=auth_mode,
                scenario_id=SCENARIO_ID,
                resume_session=session_id,
            )
            repair_turn_payload = _materialize_attempt(
                provider=provider,
                variant=variant,
                repeat_index=repeat_index,
                attempt_index=2,
                project_root=project_root,
                root=root,
                run_result=repair_turn,
                model=model,
                auth_mode=auth_mode,
                prompt=repair_ticket,
                config=config,
                prior_records=tuple(first_payload["records"]),
            )
            final_payload = repair_turn_payload
        else:
            repair_turn_payload = {
                "attempted": True,
                "completed": False,
                "failure_class": "operator_surface_missing" if not session_id else "repair_ticket_invalid",
                "repair_ticket": repair_ticket,
                "forbidden_term": repair_forbidden_term,
            }

    payload = {
        "provider": provider,
        "lane": "operator",
        **live_evidence_fields(lane="operator"),
        "surface": "website_constraint_fidelity",
        "scenario_id": SCENARIO_ID,
        "variant": variant,
        "repeat_index": repeat_index,
        "model": model,
        "auth_mode": auth_mode,
        "prompt_marker_absent": prompt_marker_absent,
        "first_prompt_sha": _stable_text_digest(prompt),
        "first_turn": _attempt_summary(first_payload),
        "repair_turn_attempted": repair_turn_payload is not None,
        "repair_turn": _attempt_summary(repair_turn_payload) if isinstance(repair_turn_payload, dict) else None,
        "final": _attempt_summary(final_payload),
        "certification_status": final_payload["certification"]["status"],
        "mechanical_score": final_payload["certification"]["mechanical_score"],
        "modified_files": final_payload["modified_files"],
        "workspace_label": _display_path(project_root),
        "artifact_path": str((root / f"{SCENARIO_ID}__run_{repeat_index:03d}.json").relative_to(ROOT)),
    }
    write_json(root / f"{SCENARIO_ID}__run_{repeat_index:03d}.json", payload)
    return payload


def build_summary(
    *,
    provider: str,
    stage: str,
    repeat_count: int,
    runs: list[dict[str, Any]],
) -> dict[str, Any]:
    raw_runs = [run for run in runs if run.get("variant") == "raw_host"]
    kernel_runs = [run for run in runs if run.get("variant") == "kernel_only_cortex"]
    raw_uncertified = sum(1 for run in raw_runs if run.get("certification_status") == UNCERTIFIED)
    kernel_certified = sum(1 for run in kernel_runs if run.get("certification_status") == CERTIFIED)
    threshold = 2 if repeat_count >= 3 else repeat_count
    raw_mean = _mean_score(raw_runs)
    kernel_mean = _mean_score(kernel_runs)
    score_lift = None if raw_mean is None or kernel_mean is None else kernel_mean - raw_mean

    if raw_runs and raw_uncertified < threshold:
        experiment_status = "void_fixture_not_discriminative"
    elif kernel_runs and (
        kernel_certified >= threshold or (score_lift is not None and score_lift >= 0.30)
    ):
        experiment_status = "kernel_lift_smoke_passed"
    elif any(run.get("certification_status") == ENV_BLOCKED for run in runs):
        experiment_status = ENV_BLOCKED
    else:
        experiment_status = "kernel_lift_not_earned"

    return {
        "generated_at": now_utc_iso(),
        "provider": provider,
        "lane": "operator",
        **live_evidence_fields(lane="operator"),
        "surface": "website_constraint_fidelity",
        "stage": stage,
        "repeat_count": repeat_count,
        "raw_failure_threshold": threshold,
        "experiment_status": experiment_status,
        "raw_uncertified_count": raw_uncertified,
        "kernel_certified_count": kernel_certified,
        "raw_mean_mechanical_score": raw_mean,
        "kernel_mean_mechanical_score": kernel_mean,
        "kernel_score_lift": score_lift,
        "runs": runs,
    }


def prepare_workspace(*, provider: str, variant: str, repeat_index: int) -> Path:
    run_root = WORKSPACE_ROOT / variant / provider / f"{SCENARIO_ID}__run_{repeat_index:03d}"
    if run_root.exists():
        shutil.rmtree(run_root)
    project_root = run_root / "project_a"
    shutil.copytree(FIXTURE_ROOT, project_root)
    _initialize_workspace_git(project_root)
    return project_root


def collect_workspace_changes(project_root: Path) -> tuple[str, ...]:
    result = run_command(
        ["git", "status", "--short", "--untracked-files=all"],
        cwd=project_root,
        timeout_seconds=30.0,
    )
    if result["exit_code"] != 0:
        return ()
    changed: list[str] = []
    for line in result["stdout"].splitlines():
        if not line.strip():
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip()
        if path and not _ignorable_generated_path(path):
            changed.append(path)
    return tuple(sorted(set(changed)))


def _materialize_attempt(
    *,
    provider: str,
    variant: str,
    repeat_index: int,
    attempt_index: int,
    project_root: Path,
    root: Path,
    run_result: dict[str, Any],
    model: str,
    auth_mode: str,
    prompt: str,
    config: dict[str, Any],
    prior_records: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    stem = f"{SCENARIO_ID}__run_{repeat_index:03d}__attempt_{attempt_index}"
    write_text(root / f"{stem}.stdout.log", run_result["stdout"])
    write_text(root / f"{stem}.stderr.log", run_result["stderr"])
    records, extraction_mode = parse_json_records(run_result["stdout"])
    all_records = list(prior_records) + records
    result_text = extract_result_text(records, run_result["stdout"])
    failure_class = classify_failure(f"{run_result['stdout']}\n{run_result['stderr']}")
    if run_result["exit_code"] == 124 and failure_class is None:
        failure_class = "operator_timeout"
    tool_evidence = extract_tool_evidence_from_records(all_records, project_root=project_root)
    check_results = run_configured_checks(config, project_root=project_root)
    modified_files = collect_workspace_changes(project_root)
    evidence = InvariantEvidence(
        modified_files=modified_files,
        result_text=result_text,
        read_paths=tool_evidence.read_paths,
        commands=tool_evidence.commands,
        check_results=check_results,
        env_failure_class=failure_class if failure_class in {"auth_missing", "not_logged_in", "capacity_exhausted", "quota_exhausted", "operator_timeout"} else None,
    )
    certification = evaluate_invariants(config, evidence, project_root=project_root)
    return {
        "provider": provider,
        "variant": variant,
        "repeat_index": repeat_index,
        "attempt_index": attempt_index,
        "model": model,
        "auth_mode": auth_mode,
        "command": run_result["command"],
        "exit_code": run_result["exit_code"],
        "failure_class": failure_class,
        "started_at": run_result["started_at"],
        "ended_at": run_result["ended_at"],
        "prompt": prompt,
        "prompt_marker_absent": not prompt_has_cortex_marker(prompt),
        "records": all_records,
        "record_count": len(all_records),
        "extraction_mode": extraction_mode,
        "result_text": result_text,
        "modified_files": list(modified_files),
        "tool_evidence": tool_evidence.as_payload(),
        "check_results": [dict(result) for result in check_results],
        "certification": certification.as_payload(),
    }


def _run_claude_turn(
    prompt: str,
    *,
    project_root: Path,
    model: str,
    auth_mode: str,
    scenario_id: str,
    resume_session: str | None = None,
) -> dict[str, Any]:
    command = [
        "claude",
        "-p",
        prompt,
        "--model",
        model,
        "--output-format",
        "stream-json",
        "--verbose",
        "--max-turns",
        "6" if resume_session is None else "4",
        "--permission-mode",
        "bypassPermissions",
        "--setting-sources",
        "local",
    ]
    if resume_session:
        command.extend(["--resume", resume_session])
    if auth_mode != "claude_code":
        return {
            "command": command,
            "exit_code": 1,
            "stdout": "",
            "stderr": f"unsupported auth mode for Claude operator lane: {auth_mode}",
            "started_at": now_utc_iso(),
            "ended_at": now_utc_iso(),
        }
    return run_command(command, cwd=project_root, timeout_seconds=240.0)


def _blocked_payload(
    *,
    provider: str,
    variant: str,
    repeat_index: int,
    model: str,
    auth_mode: str,
    prompt: str,
    project_root: Path,
    reason: str,
) -> dict[str, Any]:
    return {
        "provider": provider,
        "lane": "operator",
        **live_evidence_fields(lane="operator"),
        "surface": "website_constraint_fidelity",
        "scenario_id": SCENARIO_ID,
        "variant": variant,
        "repeat_index": repeat_index,
        "model": model,
        "auth_mode": auth_mode,
        "prompt_marker_absent": not prompt_has_cortex_marker(prompt),
        "first_prompt_sha": _stable_text_digest(prompt),
        "certification_status": ENV_BLOCKED,
        "mechanical_score": 0.0,
        "modified_files": [],
        "workspace_label": _display_path(project_root),
        "blocked_reason": reason,
    }


def _attempt_summary(payload: dict[str, Any] | None) -> dict[str, Any] | None:
    if payload is None:
        return None
    if "certification" not in payload:
        return dict(payload)
    return {
        "attempt_index": payload["attempt_index"],
        "exit_code": payload["exit_code"],
        "failure_class": payload["failure_class"],
        "prompt_marker_absent": payload["prompt_marker_absent"],
        "result_text": payload["result_text"],
        "modified_files": payload["modified_files"],
        "tool_evidence": payload["tool_evidence"],
        "certification": payload["certification"],
    }


def _evaluation_from_payload(payload: dict[str, Any]) -> InvariantEvaluation:
    from lab.invariant_runner import InvariantResult

    results = tuple(
        InvariantResult(
            invariant_id=str(result["id"]),
            status=str(result["status"]),
            required=bool(result.get("required", True)),
            message=str(result["message"]),
            repair_fact=result.get("repair_fact") if isinstance(result.get("repair_fact"), str) else None,
            evidence=result.get("evidence") if isinstance(result.get("evidence"), dict) else None,
        )
        for result in payload.get("results", [])
    )
    return InvariantEvaluation(
        status=str(payload["status"]),
        mechanical_score=float(payload["mechanical_score"]),
        required_pass_count=int(payload["required_pass_count"]),
        required_count=int(payload["required_count"]),
        failed_repair_facts=tuple(str(fact) for fact in payload.get("failed_repair_facts", [])),
        results=results,
        env_failure_class=payload.get("env_failure_class") if isinstance(payload.get("env_failure_class"), str) else None,
    )


def _initialize_workspace_git(project_root: Path) -> None:
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
        ["git", "add", "."],
        ["git", "commit", "-q", "-m", "baseline"],
    ):
        result = run_command(command, cwd=project_root, env=git_env, timeout_seconds=30.0)
        if result["exit_code"] != 0:
            raise RuntimeError(
                f"failed to initialize website fixture workspace: {result['stderr'] or result['stdout']}"
            )


def _variants_for_stage(stage: str) -> tuple[str, ...]:
    if stage == "reproduce":
        return ("raw_host",)
    if stage == "kernel":
        return ("kernel_only_cortex",)
    if stage == "all":
        return VARIANTS
    raise ValueError(f"unsupported stage: {stage}")


def _mean_score(runs: list[dict[str, Any]]) -> float | None:
    scores = [float(run["mechanical_score"]) for run in runs if isinstance(run.get("mechanical_score"), (int, float))]
    if not scores:
        return None
    return sum(scores) / len(scores)


def _stable_text_digest(text: str) -> str:
    import hashlib

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _ignorable_generated_path(path: str) -> bool:
    parts = Path(path).parts
    return any(part in {"node_modules", ".git"} for part in parts)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
