"""Signed-in host-native product-path harness for the L2 live testing environment."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any

try:  # pragma: no cover - import path differs between script execution and pytest import.
    from .live_validation_common import (
        BLOCKING_FAILURE_CLASSES,
        MODEL_MATRIX,
        SCENARIOS,
        choose_model,
        classify_failure,
        classify_truth_gap,
        collect_modified_files,
        comparator_path,
        ensure_live_validation_dirs,
        extract_event_labels,
        extract_result_text,
        extract_session_id,
        now_utc_iso,
        parse_json_lines,
        prepare_harness_workspace,
        provider_root,
        REPO_ROOT,
        read_prompt_template,
        resolve_auth_mode,
        run_target_test,
        sanitize_text,
        should_collapse_after_failure,
        write_json,
        write_text,
    )
    from .live_openai_app_server_operator import run_openai_app_server_validation
except ImportError:  # pragma: no cover
    from live_validation_common import (
        BLOCKING_FAILURE_CLASSES,
        MODEL_MATRIX,
        SCENARIOS,
        choose_model,
        classify_failure,
        classify_truth_gap,
        collect_modified_files,
        comparator_path,
        ensure_live_validation_dirs,
        extract_event_labels,
        extract_result_text,
        extract_session_id,
        now_utc_iso,
        parse_json_lines,
        prepare_harness_workspace,
        provider_root,
        REPO_ROOT,
        read_prompt_template,
        resolve_auth_mode,
        run_target_test,
        sanitize_text,
        should_collapse_after_failure,
        write_json,
        write_text,
    )
    from live_openai_app_server_operator import run_openai_app_server_validation


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 tools/live_host_native_product_paths.py",
        description="Run signed-in host-native product-path validations on the shared coding harness.",
    )
    parser.add_argument(
        "--provider",
        choices=("claude", "gemini", "openai", "all"),
        default="all",
    )
    parser.add_argument(
        "--scenario",
        choices=("pass_minimal", "truth_gap", "restart_continuity", "all"),
        default="all",
    )
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=3,
    )
    parser.add_argument(
        "--cooldown-seconds",
        type=int,
        default=30,
    )
    parser.add_argument(
        "--preferred-model",
        default=None,
    )
    parser.add_argument(
        "--fallback-model",
        default=None,
    )
    parser.add_argument(
        "--disable-auto-probe",
        action="store_true",
    )
    parser.add_argument(
        "--exploratory-probe",
        action="store_true",
    )
    args = parser.parse_args(argv)

    ensure_live_validation_dirs()
    providers = ("claude", "gemini", "openai") if args.provider == "all" else (args.provider,)
    summary_name = (
        "host_native_product_paths_summary__exploratory.json"
        if args.exploratory_probe
        else "host_native_product_paths_summary.json"
    )
    summary_path = comparator_path(summary_name)
    summary = _read_json(summary_path)
    if not summary:
        summary = {
            "generated_at": now_utc_iso(),
            "surface": "host_native_product_paths",
            "lane": "operator",
            "providers": {},
        }
    summary["generated_at"] = now_utc_iso()
    summary["surface"] = "host_native_product_paths"
    summary["lane"] = "operator"
    for provider in providers:
        summary["providers"][provider] = _run_provider(
            provider,
            scenario=args.scenario,
            max_attempts=max(1, args.max_attempts),
            cooldown_seconds=max(0, args.cooldown_seconds),
            preferred_model_override=args.preferred_model,
            fallback_model_override=args.fallback_model,
            disable_auto_probe=args.disable_auto_probe,
            exploratory_probe=args.exploratory_probe,
        )
    write_json(summary_path, summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def _run_provider(
    provider: str,
    *,
    scenario: str,
    max_attempts: int,
    cooldown_seconds: int,
    preferred_model_override: str | None,
    fallback_model_override: str | None,
    disable_auto_probe: bool,
    exploratory_probe: bool,
) -> dict[str, Any]:
    if provider == "openai":
        return run_openai_app_server_validation(scenario=scenario)
    surface = "product_paths_exploratory" if exploratory_probe else "product_paths"
    root = provider_root(provider, "operator", surface)
    existing_summary = _read_json(root / "host_native_product_runs.json")
    existing_runs = existing_summary.get("runs", []) if scenario != "all" else []
    baseline_summary = _read_json(comparator_path("operator_provider_baseline_summary.json"))
    baseline_runs = baseline_summary.get("providers", {}).get(provider, {}).get("runs", [])
    blocking_baseline_failures = sorted(
        {
            run["failure_class"]
            for run in baseline_runs
            if run.get("failure_class") in BLOCKING_FAILURE_CLASSES
        }
    )
    successful_baseline_runs = [run for run in baseline_runs if run.get("success")]
    if blocking_baseline_failures or not successful_baseline_runs:
        summary = {
            "generated_at": now_utc_iso(),
            "provider": provider,
            "lane": "operator",
            "runs": [
                {
                    "provider": provider,
                    "scenario_id": "operator_product_gate",
                    "repeat_index": 1,
                    "success": False,
                    "failure_class": blocking_baseline_failures[0] if blocking_baseline_failures else "operator_surface_missing",
                    "notes": "Skipped heavy operator product-path execution because the signed-in baseline lane is not yet stable.",
                }
            ],
        }
        write_json(root / "host_native_product_runs.json", summary)
        return summary

    if existing_runs:
        existing_runs = [
            run
            for run in existing_runs
            if run.get("scenario_id") != "operator_product_gate"
        ]

    runs: list[dict[str, Any]] = []
    blocked_failure: str | None = None

    for scenario_spec in SCENARIOS:
        if scenario not in {"all", scenario_spec.scenario_id}:
            continue
        for repeat_index in range(1, scenario_spec.repeat_count + 1):
            if blocked_failure is not None:
                runs.append(
                    {
                        "provider": provider,
                        "scenario_id": scenario_spec.scenario_id,
                        "repeat_index": repeat_index,
                        "success": False,
                        "skipped": True,
                        "failure_class": blocked_failure,
                        "notes": "Skipped after an earlier blocking operator-lane failure.",
                    }
                )
                continue
            result = _run_single_scenario(
                provider,
                scenario_spec.scenario_id,
                repeat_index,
                root,
                max_attempts=max_attempts,
                cooldown_seconds=cooldown_seconds,
                preferred_model_override=preferred_model_override,
                fallback_model_override=fallback_model_override,
                disable_auto_probe=disable_auto_probe,
            )
            runs.append(result)
            if should_collapse_after_failure(result.get("failure_class")):
                blocked_failure = result["failure_class"]

    if scenario in {"all", "restart_continuity"}:
        continuity = _run_restart_continuity(
            provider,
            root,
            existing_runs=existing_runs,
            max_attempts=max_attempts,
            cooldown_seconds=cooldown_seconds,
            preferred_model_override=preferred_model_override,
            fallback_model_override=fallback_model_override,
            disable_auto_probe=disable_auto_probe,
        )
        runs.append(continuity)
    summary = {
        "generated_at": now_utc_iso(),
        "provider": provider,
        "lane": "operator",
        "runs": _merge_runs(existing_runs, runs) if scenario != "all" else runs,
    }
    write_json(root / "host_native_product_runs.json", summary)
    return summary


def _run_single_scenario(
    provider: str,
    scenario_id: str,
    repeat_index: int,
    root: Path,
    *,
    max_attempts: int,
    cooldown_seconds: int,
    preferred_model_override: str | None,
    fallback_model_override: str | None,
    disable_auto_probe: bool,
) -> dict[str, Any]:
    project_root = prepare_harness_workspace(
        provider=provider,
        lane="operator",
        scenario_id=scenario_id,
        repeat_index=repeat_index,
    )
    hook_log_path = _configure_hook_capture(
        provider=provider,
        project_root=project_root,
        scenario_id=scenario_id,
        repeat_index=repeat_index,
    )
    prompt_file = next(spec.operator_prompt for spec in SCENARIOS if spec.scenario_id == scenario_id)
    prompt = read_prompt_template(prompt_file)
    auth_mode = resolve_auth_mode(provider, "operator")
    run_result, failure_class, chosen_model, preferred_model, auto_supported, attempted_models = _run_operator_attempts(
        provider=provider,
        prompt=prompt,
        project_root=project_root,
        auth_mode=auth_mode,
        approval_mode=None,
        hook_log_path=hook_log_path,
        max_attempts=max_attempts,
        cooldown_seconds=cooldown_seconds,
        preferred_model_override=preferred_model_override,
        fallback_model_override=fallback_model_override,
        disable_auto_probe=disable_auto_probe,
    )
    return _materialize_operator_run(
        provider=provider,
        scenario_id=scenario_id,
        repeat_index=repeat_index,
        project_root=project_root,
        root=root,
        run_result=run_result,
        model=chosen_model,
        preferred_model=preferred_model,
        auto_supported=auto_supported,
        attempted_models=attempted_models,
        auth_mode=auth_mode,
        failure_class=failure_class,
        hook_log_path=hook_log_path,
    )


def _run_operator_attempts(
    *,
    provider: str,
    prompt: str,
    project_root: Path,
    auth_mode: str,
    approval_mode: str | None,
    hook_log_path: Path | None,
    max_attempts: int,
    cooldown_seconds: int,
    preferred_model_override: str | None,
    fallback_model_override: str | None,
    disable_auto_probe: bool,
) -> tuple[dict[str, Any], str | None, str, str, bool | None, list[str]]:
    auto_supported: bool | None = None
    ladder = _requested_model_ladder(
        provider=provider,
        preferred_model_override=preferred_model_override,
        fallback_model_override=fallback_model_override,
        disable_auto_probe=disable_auto_probe,
    )
    preferred_model = ladder[0]
    current_model = preferred_model
    attempted_models: list[str] = []
    run_result: dict[str, Any] | None = None
    failure_class: str | None = None

    for attempt_index in range(1, max_attempts + 1):
        run_result = _run_provider_task(
            provider,
            prompt=prompt,
            project_root=project_root,
            model=current_model,
            auth_mode=auth_mode,
            approval_mode=approval_mode,
            hook_log_path=hook_log_path,
        )
        failure_class = classify_failure(f"{run_result['stdout']}\n{run_result['stderr']}")
        if failure_class is None and run_result["exit_code"] == 124:
            failure_class = "operator_timeout"
        attempted_models.append(current_model)

        if provider == "gemini" and current_model == MODEL_MATRIX["gemini"]["operator"].preferred:
            auto_supported = run_result["exit_code"] == 0 and failure_class != "model_unavailable"
            if auto_supported is False and run_result["exit_code"] != 0:
                ladder = _requested_model_ladder(
                    provider=provider,
                    preferred_model_override=preferred_model_override,
                    fallback_model_override=fallback_model_override,
                    disable_auto_probe=True,
                )
                preferred_model = ladder[0]

        if run_result["exit_code"] == 0:
            break

        next_model = choose_model(
            provider,
            "operator",
            first_failure=failure_class,
            current_model=current_model,
            auto_supported=auto_supported,
            ladder=ladder,
        )
        if next_model != current_model:
            current_model = next_model
            continue
        if failure_class not in {"capacity_exhausted", "quota_exhausted", "operator_timeout"}:
            break
        if attempt_index < max_attempts and cooldown_seconds > 0:
            time.sleep(cooldown_seconds)

    if run_result is None:
        raise RuntimeError("operator attempt loop produced no run result")

    return (
        run_result,
        failure_class,
        current_model,
        preferred_model,
        auto_supported,
        attempted_models,
    )


def _run_restart_continuity(
    provider: str,
    root: Path,
    *,
    existing_runs: list[dict[str, Any]],
    max_attempts: int,
    cooldown_seconds: int,
    preferred_model_override: str | None,
    fallback_model_override: str | None,
    disable_auto_probe: bool,
) -> dict[str, Any]:
    repeat_index = _next_repeat_index(existing_runs, "restart_continuity")
    project_root = prepare_harness_workspace(
        provider=provider,
        lane="operator",
        scenario_id="restart_continuity",
        repeat_index=repeat_index,
    )
    hook_log_path = _configure_hook_capture(
        provider=provider,
        project_root=project_root,
        scenario_id="restart_continuity",
        repeat_index=repeat_index,
    )
    auth_mode = resolve_auth_mode(provider, "operator")
    first_result, first_failure, chosen_model, preferred_model, auto_supported, attempted_models = _run_operator_attempts(
        provider=provider,
        prompt=read_prompt_template("restart_continuity_turn1_operator.md"),
        project_root=project_root,
        auth_mode=auth_mode,
        approval_mode=None,
        hook_log_path=hook_log_path,
        max_attempts=max_attempts,
        cooldown_seconds=cooldown_seconds,
        preferred_model_override=preferred_model_override,
        fallback_model_override=fallback_model_override,
        disable_auto_probe=disable_auto_probe,
    )

    if first_failure in BLOCKING_FAILURE_CLASSES:
        first_metadata = _materialize_operator_run(
            provider=provider,
            scenario_id="restart_continuity_turn_1",
            repeat_index=repeat_index,
            project_root=project_root,
            root=root,
            run_result=first_result,
            model=chosen_model,
            preferred_model=preferred_model,
            auto_supported=auto_supported,
            attempted_models=attempted_models,
            auth_mode=auth_mode,
            failure_class=first_failure,
            hook_log_path=hook_log_path,
        )
        return {
            "provider": provider,
            "scenario_id": "restart_continuity",
            "repeat_index": repeat_index,
            "success": False,
            "failure_class": first_failure,
            "artifact_path": first_metadata["artifact_path"],
            "notes": "Continuity stopped at the first signed-in operator turn.",
        }

    first_records = parse_json_lines(first_result["stdout"])
    session_id = extract_session_id(provider, first_records)
    second_result = _resume_provider_task(
        provider,
        prompt=read_prompt_template("restart_continuity_turn2_operator.md"),
        project_root=project_root,
        model=chosen_model,
        auth_mode=auth_mode,
        session_id=session_id,
        approval_mode="yolo" if provider == "gemini" else None,
        hook_log_path=hook_log_path,
    )
    second_failure = classify_failure(f"{second_result['stdout']}\n{second_result['stderr']}")
    if second_failure is None and second_result["exit_code"] == 124:
        second_failure = "operator_timeout"
    payload = _materialize_operator_run(
        provider=provider,
        scenario_id="restart_continuity",
        repeat_index=repeat_index,
        project_root=project_root,
        root=root,
        run_result=second_result,
        model=chosen_model,
        preferred_model=preferred_model,
        auto_supported=auto_supported,
        attempted_models=attempted_models + [chosen_model],
        auth_mode=auth_mode,
        failure_class=second_failure,
        hook_log_path=hook_log_path,
    )
    payload["session_id"] = session_id
    write_json(root / "restart_continuity.latest.json", payload)
    return payload


def _materialize_operator_run(
    *,
    provider: str,
    scenario_id: str,
    repeat_index: int,
    project_root: Path,
    root: Path,
    run_result: dict[str, Any],
    model: str,
    preferred_model: str,
    auto_supported: bool | None,
    attempted_models: list[str],
    auth_mode: str,
    failure_class: str | None,
    hook_log_path: Path | None,
) -> dict[str, Any]:
    stem = f"{scenario_id}__run_{repeat_index:03d}"
    stdout_path = root / f"{stem}.stdout.log"
    stderr_path = root / f"{stem}.stderr.log"
    metadata_path = root / f"{stem}.json"
    write_text(stdout_path, run_result["stdout"])
    write_text(stderr_path, run_result["stderr"])

    test_result = run_target_test(project_root)
    records = parse_json_lines(run_result["stdout"])
    modified_files = collect_modified_files(project_root)
    result_text = extract_result_text(records, run_result["stdout"])
    hook_records = _read_hook_records(hook_log_path)
    warning_classes = _warning_classes_for_success(
        provider=provider,
        failure_class=failure_class,
        exit_code=run_result["exit_code"],
        test_exit_code=test_result["exit_code"],
    )
    effective_failure_class = None if warning_classes else failure_class
    success = run_result["exit_code"] == 0 and effective_failure_class is None and test_result["exit_code"] == 0
    truth_gap_kind = None
    if scenario_id == "truth_gap":
        truth_gap_kind = classify_truth_gap(
            result_text,
            test_passed=test_result["exit_code"] == 0,
            modified_files=modified_files,
        )
        success = truth_gap_kind == "truthful_incomplete" and effective_failure_class is None

    payload = {
        "provider": provider,
        "lane": "operator",
        "scenario_id": scenario_id,
        "repeat_index": repeat_index,
        "auth_mode": auth_mode,
        "preferred_model": preferred_model,
        "model": model,
        "auto_supported": auto_supported,
        "attempted_models": attempted_models,
        "success": success,
        "failure_class": effective_failure_class,
        "warning_classes": warning_classes,
        "command": run_result["command"],
        "structured_event_count": len(records),
        "structured_event_labels": extract_event_labels(records),
        "hook_event_count": len(hook_records),
        "hook_event_labels": _hook_event_labels(hook_records),
        "result_text": result_text,
        "modified_files": modified_files,
        "test_exit_code": test_result["exit_code"],
        "test_stdout": test_result["stdout"].strip(),
        "test_stderr": test_result["stderr"].strip(),
        "workspace_label": str(project_root.relative_to(project_root.parents[4])),
        "stdout_path": str(stdout_path.relative_to(root.parents[4])),
        "stderr_path": str(stderr_path.relative_to(root.parents[4])),
        "hook_log_path": (
            str(hook_log_path.relative_to(root.parents[4])) if hook_log_path is not None else None
        ),
        "truth_gap_kind": truth_gap_kind,
        "started_at": run_result["started_at"],
        "ended_at": run_result["ended_at"],
    }
    write_json(metadata_path, payload)
    payload["artifact_path"] = str(metadata_path.relative_to(root.parents[4]))
    return payload


def _run_provider_task(
    provider: str,
    *,
    prompt: str,
    project_root: Path,
    model: str,
    auth_mode: str,
    approval_mode: str | None = None,
    hook_log_path: Path | None = None,
) -> dict[str, Any]:
    if provider == "claude":
        return _run_claude_task(
            prompt,
            project_root=project_root,
            model=model,
            auth_mode=auth_mode,
            hook_log_path=hook_log_path,
        )
    if provider == "gemini":
        return _run_gemini_task(
            prompt,
            project_root=project_root,
            model=model,
            auth_mode=auth_mode,
            approval_mode=approval_mode,
            hook_log_path=hook_log_path,
        )
    return _run_codex_task(prompt, project_root=project_root, model=model, auth_mode=auth_mode)


def _resume_provider_task(
    provider: str,
    *,
    prompt: str,
    project_root: Path,
    model: str,
    auth_mode: str,
    session_id: str | None,
    approval_mode: str | None = None,
    hook_log_path: Path | None = None,
) -> dict[str, Any]:
    if provider == "claude":
        return _run_claude_task(
            prompt,
            project_root=project_root,
            model=model,
            auth_mode=auth_mode,
            resume_session=session_id,
            hook_log_path=hook_log_path,
        )
    if provider == "gemini":
        return _run_gemini_task(
            prompt,
            project_root=project_root,
            model=model,
            auth_mode=auth_mode,
            resume_session=session_id,
            approval_mode=approval_mode,
            hook_log_path=hook_log_path,
        )
    return _run_codex_task(
        prompt,
        project_root=project_root,
        model=model,
        auth_mode=auth_mode,
        resume_session=session_id,
    )


def _run_claude_task(
    prompt: str,
    *,
    project_root: Path,
    model: str,
    auth_mode: str,
    resume_session: str | None = None,
    hook_log_path: Path | None = None,
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
        "8",
        "--permission-mode",
        "bypassPermissions",
    ]
    if auth_mode != "claude_code":
        return _unsupported_operator_mode("claude", auth_mode, command)
    if resume_session:
        command.extend(["--resume", resume_session])
    return _run_timed_command(
        command,
        cwd=project_root,
        timeout_seconds=180.0,
        env=_hook_env("claude", hook_log_path),
    )


def _run_gemini_task(
    prompt: str,
    *,
    project_root: Path,
    model: str,
    auth_mode: str,
    resume_session: str | None = None,
    approval_mode: str | None = None,
    hook_log_path: Path | None = None,
) -> dict[str, Any]:
    if auth_mode not in {"google_login", "api_key"}:
        return _unsupported_operator_mode("gemini", auth_mode, ["gemini"])
    effective_approval_mode = approval_mode or "yolo"
    command = [
        "gemini",
        "-p",
        prompt,
        "-o",
        "stream-json",
        "--approval-mode",
        effective_approval_mode,
    ]
    if model != "auto":
        command[5:5] = ["-m", model]
    if resume_session:
        command.extend(["-r", resume_session])
    return _run_timed_command(
        command,
        cwd=project_root,
        timeout_seconds=180.0,
        env=_hook_env("gemini", hook_log_path),
    )


def _run_codex_task(
    prompt: str,
    *,
    project_root: Path,
    model: str,
    auth_mode: str,
    resume_session: str | None = None,
) -> dict[str, Any]:
    if auth_mode != "codex_cli":
        return _unsupported_operator_mode("openai", auth_mode, ["codex"])
    if resume_session:
        command = [
            "codex",
            "exec",
            "resume",
            "--json",
            "--full-auto",
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
    return _run_timed_command(command, cwd=project_root, timeout_seconds=120.0)


def _run_timed_command(
    command: list[str],
    *,
    cwd: Path,
    timeout_seconds: float,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    started_at = now_utc_iso()
    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd),
            env=env,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
        return {
            "command": command,
            "exit_code": completed.returncode,
            "stdout": sanitize_text(completed.stdout),
            "stderr": sanitize_text(completed.stderr),
            "started_at": started_at,
            "ended_at": now_utc_iso(),
        }
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else (exc.stdout or b"").decode("utf-8", errors="replace")
        stderr = exc.stderr if isinstance(exc.stderr, str) else (exc.stderr or b"").decode("utf-8", errors="replace")
        return {
            "command": command,
            "exit_code": 124,
            "stdout": sanitize_text(stdout),
            "stderr": sanitize_text(stderr),
            "started_at": started_at,
            "ended_at": now_utc_iso(),
        }


def _unsupported_operator_mode(provider: str, auth_mode: str, command: list[str]) -> dict[str, Any]:
    return {
        "command": command,
        "exit_code": 1,
        "stdout": "",
        "stderr": f"{provider} operator auth mode `{auth_mode}` is not supported by the host-native product-path harness.",
        "started_at": now_utc_iso(),
        "ended_at": now_utc_iso(),
    }


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _requested_model_ladder(
    *,
    provider: str,
    preferred_model_override: str | None,
    fallback_model_override: str | None,
    disable_auto_probe: bool,
) -> tuple[str, ...]:
    if preferred_model_override:
        ladder = [preferred_model_override]
        if fallback_model_override and fallback_model_override.lower() != "none" and fallback_model_override != preferred_model_override:
            ladder.append(fallback_model_override)
        return tuple(ladder)
    if provider == "gemini" and disable_auto_probe:
        ladder = ["gemini-2.5-flash"]
        if fallback_model_override and fallback_model_override.lower() != "none" and fallback_model_override not in ladder:
            ladder.append(fallback_model_override)
        elif "gemini-2.5-flash-lite" not in ladder:
            ladder.append("gemini-2.5-flash-lite")
        return tuple(ladder)
    return (MODEL_MATRIX[provider]["operator"].preferred,) if MODEL_MATRIX[provider]["operator"].fallback is None else (
        MODEL_MATRIX[provider]["operator"].preferred,
        MODEL_MATRIX[provider]["operator"].fallback,
    )


def _merge_runs(existing_runs: list[dict[str, Any]], new_runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[tuple[str | None, int | None], dict[str, Any]] = {}
    order: list[tuple[str | None, int | None]] = []
    for run in existing_runs + new_runs:
        key = (run.get("scenario_id"), run.get("repeat_index"))
        if key not in merged:
            order.append(key)
        merged[key] = run
    return [merged[key] for key in order]


def _next_repeat_index(existing_runs: list[dict[str, Any]], scenario_id: str) -> int:
    existing_indexes = [
        int(run["repeat_index"])
        for run in existing_runs
        if run.get("scenario_id") == scenario_id and isinstance(run.get("repeat_index"), int)
    ]
    return (max(existing_indexes) + 1) if existing_indexes else 1


def _configure_hook_capture(
    *,
    provider: str,
    project_root: Path,
    scenario_id: str,
    repeat_index: int,
    log_root: Path | None = None,
) -> Path | None:
    if provider not in {"claude", "gemini"}:
        return None
    recorder_path = REPO_ROOT / "tools" / "live_hook_recorder.py"
    effective_log_root = (
        provider_root(provider, "operator", "product_paths")
        if log_root is None
        else log_root
    )
    hook_log_path = effective_log_root / f"{scenario_id}__run_{repeat_index:03d}.hooks.jsonl"
    command_literal = json.dumps(f'python3 "{recorder_path}"')
    if provider == "claude":
        settings_path = project_root / ".claude" / "settings.json"
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        settings = {
            "hooks": {
                "SessionStart": [{"hooks": [{"type": "command", "command": json.loads(command_literal)}]}],
                "PreToolUse": [{"matcher": ".*", "hooks": [{"type": "command", "command": json.loads(command_literal)}]}],
                "PostToolUse": [{"matcher": ".*", "hooks": [{"type": "command", "command": json.loads(command_literal)}]}],
                "Stop": [{"hooks": [{"type": "command", "command": json.loads(command_literal)}]}],
                "SessionEnd": [{"hooks": [{"type": "command", "command": json.loads(command_literal)}]}],
            }
        }
    else:
        settings_path = project_root / ".gemini" / "settings.json"
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        settings = {
            "hooks": {
                "SessionStart": [{"matcher": "*", "hooks": [{"name": "cortex-start", "type": "command", "command": json.loads(command_literal)}]}],
                "BeforeTool": [{"matcher": ".*", "hooks": [{"name": "cortex-before-tool", "type": "command", "command": json.loads(command_literal)}]}],
                "AfterTool": [{"matcher": ".*", "hooks": [{"name": "cortex-after-tool", "type": "command", "command": json.loads(command_literal)}]}],
                "SessionEnd": [{"matcher": "*", "hooks": [{"name": "cortex-end", "type": "command", "command": json.loads(command_literal)}]}],
            }
        }
    settings_path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
    return hook_log_path


def _hook_env(provider: str, hook_log_path: Path | None) -> dict[str, str]:
    env = dict(os.environ)
    env["CORTEX_LIVE_HOOK_PROVIDER"] = provider
    if hook_log_path is not None:
        env["CORTEX_LIVE_HOOK_SCENARIO_ID"] = hook_log_path.name.split("__run_")[0]
        env["CORTEX_LIVE_HOOK_LOG_PATH"] = str(hook_log_path)
    return env


def _read_hook_records(path: Path | None) -> list[dict[str, Any]]:
    if path is None or not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            records.append(payload)
    return records


def _hook_event_labels(records: list[dict[str, Any]]) -> list[str]:
    labels: list[str] = []
    for record in records:
        name = record.get("hook_event_name")
        if isinstance(name, str) and name.strip():
            labels.append(name.strip())
    return labels


def _warning_classes_for_success(
    *,
    provider: str,
    failure_class: str | None,
    exit_code: int,
    test_exit_code: int,
) -> list[str]:
    _ = test_exit_code
    if provider == "gemini" and failure_class in {"capacity_exhausted", "quota_exhausted"} and exit_code == 0:
        return [failure_class]
    return []


if __name__ == "__main__":
    raise SystemExit(main())
