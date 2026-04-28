"""Live website-fixture constraint-fidelity harness.

Surface: lab
Executive Benefit: falsify or prove kernel-side constraint certification without
prompt-side Cortex doctrine.
Why this beats direct product work now: the live Claude smoke showed prompt
guidance was not enough, so this isolates external invariant gating.
"""

from __future__ import annotations

import argparse
import hashlib
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
RAW_HOST = "raw_host"
KERNEL_ONLY_CORTEX = "kernel_only_cortex"
KERNEL_LOOP_CORTEX = "kernel_loop_cortex"
BASE_VARIANTS = (RAW_HOST, KERNEL_ONLY_CORTEX)
VARIANTS = (RAW_HOST, KERNEL_ONLY_CORTEX, KERNEL_LOOP_CORTEX)
SINGLE_REPAIR_TURNS = 1
LOOP_REPAIR_TURNS = 3
BASELINE_PROMPT_SHA = "630a9a9afef1cc804aa91a4111d60379d0cf13e29b2b579b4e21f72eb2d264fd"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 -m lab.website_constraint_fidelity",
        description="Run the website-fixture constraint-fidelity experiment.",
    )
    parser.add_argument("--provider", choices=("claude",), default="claude")
    parser.add_argument("--repeat-count", type=int, default=3)
    parser.add_argument("--stage", choices=("reproduce", "kernel", "kernel-loop", "all"), default="all")
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
    fixture_fingerprint = compute_fixture_fingerprint(prompt=prompt)
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
            fixture_fingerprint=fixture_fingerprint,
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
    repair_attempts: list[dict[str, Any]] = []
    repair_policy = _repair_policy_for_variant(variant)
    max_repair_turns = _max_repair_turns_for_variant(variant)
    if max_repair_turns and first_payload["certification"]["status"] == UNCERTIFIED:
        repair_attempts, final_payload = _run_repair_policy(
            provider=provider,
            variant=variant,
            repeat_index=repeat_index,
            project_root=project_root,
            root=root,
            model=model,
            auth_mode=auth_mode,
            first_payload=first_payload,
            config=config,
            max_repair_turns=max_repair_turns,
        )
        repair_turn_payload = repair_attempts[0] if repair_attempts else None

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
        "repair_policy": repair_policy,
        "max_repair_turns": max_repair_turns,
        "fixture_fingerprint": fixture_fingerprint,
        "prompt_marker_absent": prompt_marker_absent,
        "first_prompt_sha": _stable_text_digest(prompt),
        "first_turn": _attempt_summary(first_payload),
        "repair_turn_attempted": repair_turn_payload is not None,
        "repair_turn": _attempt_summary(repair_turn_payload) if isinstance(repair_turn_payload, dict) else None,
        "repair_attempts": [_attempt_summary(attempt) for attempt in repair_attempts],
        "converted_failure_classes": _converted_failure_classes(
            first_payload=first_payload,
            repair_attempts=repair_attempts,
            final_payload=final_payload,
        ),
        "final": _attempt_summary(final_payload),
        "certification_status": final_payload["certification"]["status"],
        "mechanical_score": final_payload["certification"]["mechanical_score"],
        "modified_files": final_payload["modified_files"],
        "workspace_label": _display_path(project_root),
        "artifact_path": str((root / f"{SCENARIO_ID}__run_{repeat_index:03d}.json").relative_to(ROOT)),
    }
    write_json(root / f"{SCENARIO_ID}__run_{repeat_index:03d}.json", payload)
    return payload


def _run_repair_policy(
    *,
    provider: str,
    variant: str,
    repeat_index: int,
    project_root: Path,
    root: Path,
    model: str,
    auth_mode: str,
    first_payload: dict[str, Any],
    config: dict[str, Any],
    max_repair_turns: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    final_payload = first_payload
    attempts: list[dict[str, Any]] = []
    session_id = extract_session_id("claude", first_payload["records"])
    for repair_index in range(1, max_repair_turns + 1):
        if final_payload["certification"]["status"] != UNCERTIFIED:
            break
        repair_ticket = render_factual_repair_ticket(
            _evaluation_from_payload(final_payload["certification"])
        )
        repair_forbidden_term = first_forbidden_repair_term(repair_ticket)
        if not session_id or repair_forbidden_term is not None:
            attempts.append(
                {
                    "attempted": True,
                    "completed": False,
                    "failure_class": "operator_surface_missing" if not session_id else "repair_ticket_invalid",
                    "repair_ticket": repair_ticket,
                    "forbidden_term": repair_forbidden_term,
                }
            )
            break
        repair_turn = _run_claude_turn(
            repair_ticket,
            project_root=project_root,
            model=model,
            auth_mode=auth_mode,
            scenario_id=SCENARIO_ID,
            resume_session=session_id,
        )
        repair_payload = _materialize_attempt(
            provider=provider,
            variant=variant,
            repeat_index=repeat_index,
            attempt_index=repair_index + 1,
            project_root=project_root,
            root=root,
            run_result=repair_turn,
            model=model,
            auth_mode=auth_mode,
            prompt=repair_ticket,
            config=config,
            prior_records=tuple(final_payload["records"]),
        )
        attempts.append(repair_payload)
        final_payload = repair_payload
        session_id = extract_session_id("claude", final_payload["records"]) or session_id
    return attempts, final_payload


def build_summary(
    *,
    provider: str,
    stage: str,
    repeat_count: int,
    runs: list[dict[str, Any]],
) -> dict[str, Any]:
    raw_runs = [run for run in runs if run.get("variant") == RAW_HOST]
    kernel_runs = [run for run in runs if run.get("variant") == KERNEL_ONLY_CORTEX]
    loop_runs = [run for run in runs if run.get("variant") == KERNEL_LOOP_CORTEX]
    raw_uncertified = sum(1 for run in raw_runs if run.get("certification_status") == UNCERTIFIED)
    kernel_certified = sum(1 for run in kernel_runs if run.get("certification_status") == CERTIFIED)
    loop_certified = sum(1 for run in loop_runs if run.get("certification_status") == CERTIFIED)
    threshold = 2 if repeat_count >= 3 else repeat_count
    raw_mean = _mean_score(raw_runs)
    kernel_mean = _mean_score(kernel_runs)
    loop_mean = _mean_score(loop_runs)
    score_lift = None if raw_mean is None or kernel_mean is None else kernel_mean - raw_mean
    loop_baseline = _historical_single_repair_baseline(
        provider=provider,
        fixture_fingerprint=_common_fixture_fingerprint(runs),
        first_prompt_sha=_common_first_prompt_sha(runs),
    )

    if loop_runs:
        if any(run.get("certification_status") == ENV_BLOCKED for run in loop_runs):
            experiment_status = ENV_BLOCKED
        elif repeat_count >= 10 and loop_certified >= 9:
            experiment_status = "kernel_loop_promotion_passed"
        elif loop_certified > _baseline_certified_count(loop_baseline):
            experiment_status = "kernel_loop_lift_smoke_passed"
        else:
            experiment_status = "kernel_loop_lift_not_earned"
    elif raw_runs and raw_uncertified < threshold:
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
        "kernel_loop_certified_count": loop_certified,
        "raw_mean_mechanical_score": raw_mean,
        "kernel_mean_mechanical_score": kernel_mean,
        "kernel_loop_mean_mechanical_score": loop_mean,
        "kernel_score_lift": score_lift,
        "historical_single_repair_baseline": loop_baseline,
        "fixture_fingerprint": _common_fixture_fingerprint(runs),
        "first_prompt_hashes": sorted({run.get("first_prompt_sha") for run in runs if run.get("first_prompt_sha")}),
        "prompt_marker_absent_all": all(bool(run.get("prompt_marker_absent")) for run in runs),
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
    if failure_class is None and _records_show_max_turns(records):
        failure_class = "turn_budget_cutoff"
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
    fixture_fingerprint: str | None = None,
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
        "repair_policy": _repair_policy_for_variant(variant),
        "max_repair_turns": _max_repair_turns_for_variant(variant),
        "fixture_fingerprint": fixture_fingerprint,
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
        return (RAW_HOST,)
    if stage == "kernel":
        return (KERNEL_ONLY_CORTEX,)
    if stage == "kernel-loop":
        return (KERNEL_LOOP_CORTEX,)
    if stage == "all":
        return BASE_VARIANTS
    raise ValueError(f"unsupported stage: {stage}")


def _mean_score(runs: list[dict[str, Any]]) -> float | None:
    scores = [float(run["mechanical_score"]) for run in runs if isinstance(run.get("mechanical_score"), (int, float))]
    if not scores:
        return None
    return sum(scores) / len(scores)


def _stable_text_digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def compute_fixture_fingerprint(*, prompt: str | None = None, fixture_root: Path = FIXTURE_ROOT) -> str:
    prompt = build_initial_prompt(fixture_root=fixture_root) if prompt is None else prompt
    digest = hashlib.sha256()
    digest.update(b"prompt\0")
    digest.update(prompt.encode("utf-8"))
    for path in sorted(p for p in fixture_root.rglob("*") if p.is_file()):
        relative = path.relative_to(fixture_root).as_posix()
        digest.update(b"\0file\0")
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _repair_policy_for_variant(variant: str) -> str:
    if variant == KERNEL_ONLY_CORTEX:
        return "single"
    if variant == KERNEL_LOOP_CORTEX:
        return "loop"
    return "none"


def _max_repair_turns_for_variant(variant: str) -> int:
    if variant == KERNEL_ONLY_CORTEX:
        return SINGLE_REPAIR_TURNS
    if variant == KERNEL_LOOP_CORTEX:
        return LOOP_REPAIR_TURNS
    return 0


def _records_show_max_turns(records: list[dict[str, Any]]) -> bool:
    return any(record.get("type") == "result" and record.get("subtype") == "error_max_turns" for record in records)


def _converted_failure_classes(
    *,
    first_payload: dict[str, Any],
    repair_attempts: list[dict[str, Any]],
    final_payload: dict[str, Any],
) -> list[str]:
    if not repair_attempts:
        return []
    if final_payload.get("certification", {}).get("status") != CERTIFIED:
        return []
    classes: set[str] = set()
    previous_payloads = [first_payload, *repair_attempts[:-1]]
    for payload in previous_payloads:
        if payload.get("certification", {}).get("status") == CERTIFIED:
            continue
        failure_class = payload.get("failure_class")
        if isinstance(failure_class, str) and failure_class:
            classes.add(failure_class)
    return sorted(classes)


def _common_fixture_fingerprint(runs: list[dict[str, Any]]) -> str | None:
    fingerprints = {run.get("fixture_fingerprint") for run in runs if run.get("fixture_fingerprint")}
    if len(fingerprints) == 1:
        return str(next(iter(fingerprints)))
    return None


def _common_first_prompt_sha(runs: list[dict[str, Any]]) -> str | None:
    hashes = {run.get("first_prompt_sha") for run in runs if run.get("first_prompt_sha")}
    if len(hashes) == 1:
        return str(next(iter(hashes)))
    return None


def _historical_single_repair_baseline(
    *,
    provider: str,
    fixture_fingerprint: str | None,
    first_prompt_sha: str | None,
    baseline_path: Path | None = None,
) -> dict[str, Any]:
    baseline_path = baseline_path or ARTIFACT_ROOT / provider / "n10_failure_classification.json"
    try:
        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"usable": False, "reason": "missing_baseline", "source_path": str(baseline_path)}
    baseline_fingerprint = baseline.get("fixture_fingerprint")
    if isinstance(baseline_fingerprint, str):
        if baseline_fingerprint != fixture_fingerprint:
            return {
                "usable": False,
                "reason": "fixture_fingerprint_mismatch",
                "source_path": str(baseline_path),
                "baseline_fixture_fingerprint": baseline_fingerprint,
                "current_fixture_fingerprint": fixture_fingerprint,
            }
    elif first_prompt_sha != BASELINE_PROMPT_SHA:
        return {
            "usable": False,
            "reason": "legacy_baseline_prompt_hash_mismatch",
            "source_path": str(baseline_path),
            "baseline_first_prompt_sha": BASELINE_PROMPT_SHA,
            "current_first_prompt_sha": first_prompt_sha,
        }
    return {
        "usable": True,
        "source_path": str(baseline_path),
        "kernel_certified_count": baseline.get("kernel_certified_count"),
        "kernel_uncertified_count": baseline.get("kernel_uncertified_count"),
        "repeat_count": baseline.get("repeat_count"),
        "fixture_fingerprint": baseline_fingerprint,
        "legacy_without_fingerprint": not isinstance(baseline_fingerprint, str),
    }


def _baseline_certified_count(baseline: dict[str, Any]) -> int:
    value = baseline.get("kernel_certified_count")
    if isinstance(value, int):
        return value
    return 8


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
