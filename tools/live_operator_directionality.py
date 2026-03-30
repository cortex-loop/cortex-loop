"""Paired raw-vs-Cortex operator directionality audit harness."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
import time
from contextlib import contextmanager, nullcontext
from pathlib import Path
from typing import Any, Iterator

from cortex.sre.operator_routing import (
    build_operator_route_diagnostics,
    build_operator_task_state,
    select_operator_route,
)

try:  # pragma: no cover
    from . import live_host_native_product_paths as host_paths
    from . import live_openai_app_server_operator as openai_operator
    from .live_validation_common import (
        MODEL_MATRIX,
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
        operator_directionality_root,
        prepare_harness_workspace,
        read_prompt_template,
        recent_operator_probe_failure,
        resolve_auth_mode,
        run_command,
        run_target_test,
        summarize_operator_runs,
        write_json,
    )
except ImportError:  # pragma: no cover
    import live_host_native_product_paths as host_paths
    import live_openai_app_server_operator as openai_operator
    from live_validation_common import (
        MODEL_MATRIX,
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
        operator_directionality_root,
        prepare_harness_workspace,
        read_prompt_template,
        recent_operator_probe_failure,
        resolve_auth_mode,
        run_command,
        run_target_test,
        summarize_operator_runs,
        write_json,
    )


_SCENARIOS: dict[str, dict[str, Any]] = {
    "pass_minimal": {
        "prompt_file": "pass_minimal_operator.md",
        "run_test": True,
    },
    "truth_gap": {
        "prompt_file": "truth_gap_operator.md",
        "run_test": False,
    },
    "restart_continuity": {
        "turn1_prompt_file": "restart_continuity_turn1_operator.md",
        "turn2_prompt_file": "restart_continuity_turn2_operator.md",
        "run_test": True,
    },
}
_VARIANTS = ("raw_host", "cortex_operator")
_REPEAT_COUNT = 3
_RAW_BASELINE_FAILURE = "blocked_raw_baseline_contaminated"
_SURFACE_LABEL = {
    "claude": "claude_cli",
    "gemini": "gemini_cli",
    "openai": "codex_app_server",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 tools/live_operator_directionality.py",
        description="Run paired raw-vs-Cortex operator directionality comparisons.",
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
        "--repeat-count",
        type=int,
        default=_REPEAT_COUNT,
    )
    args = parser.parse_args(argv)

    ensure_live_validation_dirs()
    providers = ("claude", "gemini", "openai") if args.provider == "all" else (args.provider,)
    scenarios = tuple(_SCENARIOS) if args.scenario == "all" else (args.scenario,)

    summary = _read_json(comparator_path("operator_directionality_summary.json"))
    if not summary:
        summary = {
            "generated_at": now_utc_iso(),
            "surface": "operator_directionality",
            "lane": "operator",
            "providers": {},
        }
    summary["generated_at"] = now_utc_iso()
    summary["surface"] = "operator_directionality"
    summary["lane"] = "operator"
    if args.provider == "all":
        summary["providers"] = {}
    for provider in providers:
        summary["providers"][provider] = _run_provider(
            provider,
            scenarios=scenarios,
            repeat_count=max(1, args.repeat_count),
        )
        write_json(comparator_path("operator_directionality_summary.json"), summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def _run_provider(
    provider: str,
    *,
    scenarios: tuple[str, ...],
    repeat_count: int,
) -> dict[str, Any]:
    precheck = _raw_host_precheck(provider)
    baseline_summary = _read_json(comparator_path("operator_provider_baseline_summary.json"))
    baseline_runs = baseline_summary.get("providers", {}).get(provider, {}).get("runs", [])
    prior_variant_runs: dict[str, list[dict[str, Any]]] = {variant: [] for variant in _VARIANTS}
    pairs: list[dict[str, Any]] = []
    for scenario_id in scenarios:
        for repeat_index in range(1, repeat_count + 1):
            pair = _run_pair(
                provider,
                scenario_id=scenario_id,
                repeat_index=repeat_index,
                precheck=precheck,
                baseline_runs=baseline_runs,
                prior_variant_runs={
                    variant: tuple(runs)
                    for variant, runs in prior_variant_runs.items()
                },
            )
            pairs.append(pair)
            if pair.get("pair_status") == "compared":
                raw_host = pair.get("raw_host")
                cortex_operator = pair.get("cortex_operator")
                if isinstance(raw_host, dict):
                    prior_variant_runs["raw_host"].append(raw_host)
                if isinstance(cortex_operator, dict):
                    prior_variant_runs["cortex_operator"].append(cortex_operator)
    summary = {
        "generated_at": now_utc_iso(),
        "provider": provider,
        "lane": "operator",
        "raw_host_precheck": precheck,
        "pairs": pairs,
    }
    write_json(operator_directionality_root(provider, "summary") / "summary.json", summary)
    return summary


def _run_pair(
    provider: str,
    *,
    scenario_id: str,
    repeat_index: int,
    precheck: dict[str, Any],
    baseline_runs: list[dict[str, Any]],
    prior_variant_runs: dict[str, tuple[dict[str, Any], ...]],
) -> dict[str, Any]:
    if precheck["status"] != "ready":
        raw_payload = _blocked_raw_payload(
            provider,
            scenario_id=scenario_id,
            repeat_index=repeat_index,
            reason=precheck["reason"],
        )
        return {
            "provider": provider,
            "scenario_id": scenario_id,
            "repeat_index": repeat_index,
            "pair_status": "blocked",
            "blocked_reason": precheck["reason"],
            "raw_host": raw_payload,
            "cortex_operator": None,
        }

    raw_payload = _run_variant(
        provider,
        variant="raw_host",
        scenario_id=scenario_id,
        repeat_index=repeat_index,
        precheck=precheck,
        baseline_runs=baseline_runs,
        prior_runs=prior_variant_runs["raw_host"],
    )
    cortex_payload = _run_variant(
        provider,
        variant="cortex_operator",
        scenario_id=scenario_id,
        repeat_index=repeat_index,
        precheck=precheck,
        baseline_runs=baseline_runs,
        prior_runs=prior_variant_runs["cortex_operator"],
    )
    return {
        "provider": provider,
        "scenario_id": scenario_id,
        "repeat_index": repeat_index,
        "pair_status": "compared",
        "blocked_reason": None,
        "raw_host": raw_payload,
        "cortex_operator": cortex_payload,
    }


def _run_variant(
    provider: str,
    *,
    variant: str,
    scenario_id: str,
    repeat_index: int,
    precheck: dict[str, Any],
    baseline_runs: list[dict[str, Any]],
    prior_runs: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    if provider == "openai":
        return _run_openai_variant(
            variant=variant,
            scenario_id=scenario_id,
            repeat_index=repeat_index,
            precheck=precheck,
        )
    return _run_cli_variant(
        provider,
        variant=variant,
        scenario_id=scenario_id,
        repeat_index=repeat_index,
        precheck=precheck,
        baseline_runs=baseline_runs,
        prior_runs=prior_runs,
    )


def _run_cli_variant(
    provider: str,
    variant: str,
    *,
    scenario_id: str,
    repeat_index: int,
    precheck: dict[str, Any],
    baseline_runs: list[dict[str, Any]],
    prior_runs: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    root = operator_directionality_root(provider, variant)
    project_root = prepare_harness_workspace(
        provider=provider,
        lane=f"operator_directionality/{variant}",
        scenario_id=scenario_id,
        repeat_index=repeat_index,
    )
    hook_log_path = (
        host_paths._configure_hook_capture(
            provider=provider,
            project_root=project_root,
            scenario_id=scenario_id,
            repeat_index=repeat_index,
            log_root=root,
        )
        if variant == "cortex_operator"
        else None
    )
    if scenario_id == "restart_continuity":
        return _run_cli_restart_continuity_variant(
            provider,
            variant=variant,
            scenario_id=scenario_id,
            repeat_index=repeat_index,
            project_root=project_root,
            root=root,
            hook_log_path=hook_log_path,
            precheck=precheck,
        )

    prompt = read_prompt_template(_SCENARIOS[scenario_id]["prompt_file"])
    auth_mode = resolve_auth_mode(provider, "operator")
    route_state = build_operator_task_state(
        scenario_id,
        previous_same_host_run_failed_before_completion=summarize_operator_runs(
            prior_runs,
            scenario_id=scenario_id,
        )["previous_failed_before_completion"],
        recent_probe_failure_class=recent_operator_probe_failure(provider),
        recent_baseline_clean_count=summarize_operator_runs(baseline_runs)["clean_success_count"],
        recent_warning_bearing_success_present=summarize_operator_runs(baseline_runs)["warning_bearing_success_present"],
        recent_product_failure_class=summarize_operator_runs(
            prior_runs,
            scenario_id=scenario_id,
        )["latest_failure_class"],
    )
    route_decision = select_operator_route(route_state)
    route_diagnostics = build_operator_route_diagnostics(route_state, route_decision)
    if route_decision.blocked_reason is not None:
        return host_paths._blocked_operator_route_payload(
            provider=provider,
            scenario_id=scenario_id,
            repeat_index=repeat_index,
            route_diagnostics=route_diagnostics,
            failure_class=host_paths._blocked_route_failure_class(
                route_state,
                recent_probe_failure_class=recent_operator_probe_failure(provider),
                recent_product_failure_class=summarize_operator_runs(
                    prior_runs,
                    scenario_id=scenario_id,
                )["latest_failure_class"],
            ),
            notes="Route selector blocked paired execution before host work started.",
        )
    if variant == "cortex_operator":
        run_result, failure_class, chosen_model, preferred_model, auto_supported, attempted_models = host_paths._run_operator_attempts(
            provider=provider,
            prompt=prompt,
            project_root=project_root,
            auth_mode=auth_mode,
            approval_mode=None,
            hook_log_path=hook_log_path,
            max_attempts=1 + route_decision.budget.max_retries,
            cooldown_seconds=30,
            preferred_model_override=None,
            fallback_model_override=None,
            disable_auto_probe=False,
        )
    else:
        run_result, failure_class, chosen_model, preferred_model, auto_supported, attempted_models = _run_raw_operator_attempts(
            provider=provider,
            prompt=prompt,
            project_root=project_root,
            auth_mode=auth_mode,
            approval_mode=None,
            precheck=precheck,
            max_attempts=1 + route_decision.budget.max_retries,
        )
    payload = host_paths._materialize_operator_run(
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
        run_verification=route_decision.budget.require_verification,
        route_diagnostics=route_diagnostics,
    )
    payload["variant"] = variant
    payload["surface"] = _SURFACE_LABEL[provider]
    return payload


def _run_cli_restart_continuity_variant(
    provider: str,
    *,
    variant: str,
    scenario_id: str,
    repeat_index: int,
    project_root: Path,
    root: Path,
    hook_log_path: Path | None,
    precheck: dict[str, Any],
    baseline_runs: list[dict[str, Any]],
    prior_runs: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    auth_mode = resolve_auth_mode(provider, "operator")
    first_prompt = read_prompt_template(_SCENARIOS[scenario_id]["turn1_prompt_file"])
    second_prompt = read_prompt_template(_SCENARIOS[scenario_id]["turn2_prompt_file"])
    route_state = build_operator_task_state(
        scenario_id,
        previous_same_host_run_failed_before_completion=summarize_operator_runs(
            prior_runs,
            scenario_id=scenario_id,
        )["previous_failed_before_completion"],
        recent_probe_failure_class=recent_operator_probe_failure(provider),
        recent_baseline_clean_count=summarize_operator_runs(baseline_runs)["clean_success_count"],
        recent_warning_bearing_success_present=summarize_operator_runs(baseline_runs)["warning_bearing_success_present"],
        recent_product_failure_class=summarize_operator_runs(
            prior_runs,
            scenario_id=scenario_id,
        )["latest_failure_class"],
    )
    route_decision = select_operator_route(route_state)
    route_diagnostics = build_operator_route_diagnostics(route_state, route_decision)
    if route_decision.blocked_reason is not None:
        return host_paths._blocked_operator_route_payload(
            provider=provider,
            scenario_id=scenario_id,
            repeat_index=repeat_index,
            route_diagnostics=route_diagnostics,
            failure_class=host_paths._blocked_route_failure_class(
                route_state,
                recent_probe_failure_class=recent_operator_probe_failure(provider),
                recent_product_failure_class=summarize_operator_runs(
                    prior_runs,
                    scenario_id=scenario_id,
                )["latest_failure_class"],
            ),
            notes="Route selector blocked continuity before the first operator turn.",
        )

    if variant == "cortex_operator":
        first_result, first_failure, chosen_model, preferred_model, auto_supported, attempted_models = host_paths._run_operator_attempts(
            provider=provider,
            prompt=first_prompt,
            project_root=project_root,
            auth_mode=auth_mode,
            approval_mode=None,
            hook_log_path=hook_log_path,
            max_attempts=1 + route_decision.budget.max_retries,
            cooldown_seconds=30,
            preferred_model_override=None,
            fallback_model_override=None,
            disable_auto_probe=False,
        )
    else:
        first_result, first_failure, chosen_model, preferred_model, auto_supported, attempted_models = _run_raw_operator_attempts(
            provider=provider,
            prompt=first_prompt,
            project_root=project_root,
            auth_mode=auth_mode,
            approval_mode=None,
            precheck=precheck,
            max_attempts=1 + route_decision.budget.max_retries,
        )

    if first_failure in host_paths.BLOCKING_FAILURE_CLASSES:
        payload = {
            "provider": provider,
            "variant": variant,
            "surface": _SURFACE_LABEL[provider],
            "scenario_id": scenario_id,
            "repeat_index": repeat_index,
            "success": False,
            "failure_class": first_failure,
            "attempted_models": attempted_models,
            "model": chosen_model,
            "preferred_model": preferred_model,
            "notes": "Continuity stopped at the first operator turn.",
            "artifact_path": None,
            **route_diagnostics,
        }
        return payload

    first_records = host_paths.parse_json_lines(first_result["stdout"])
    session_id = extract_session_id(provider, first_records)
    if variant == "cortex_operator":
        second_result = host_paths._resume_provider_task(
            provider,
            prompt=second_prompt,
            project_root=project_root,
            model=chosen_model,
            auth_mode=auth_mode,
            session_id=session_id,
            approval_mode="yolo" if provider == "gemini" else None,
            hook_log_path=hook_log_path,
        )
    else:
        second_result = _resume_raw_provider_task(
            provider,
            prompt=second_prompt,
            project_root=project_root,
            model=chosen_model,
            auth_mode=auth_mode,
            session_id=session_id,
            approval_mode="yolo" if provider == "gemini" else None,
            precheck=precheck,
        )

    second_failure = classify_failure(f"{second_result['stdout']}\n{second_result['stderr']}")
    if second_failure is None and second_result["exit_code"] == 124:
        second_failure = "operator_timeout"

    payload = host_paths._materialize_operator_run(
        provider=provider,
        scenario_id=scenario_id,
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
        run_verification=route_decision.budget.require_verification,
        route_diagnostics=route_diagnostics,
    )
    payload["variant"] = variant
    payload["surface"] = _SURFACE_LABEL[provider]
    payload["session_id"] = session_id
    return payload


def _run_raw_operator_attempts(
    *,
    provider: str,
    prompt: str,
    project_root: Path,
    auth_mode: str,
    approval_mode: str | None,
    precheck: dict[str, Any],
    max_attempts: int,
) -> tuple[dict[str, Any], str | None, str, str, bool | None, list[str]]:
    auto_supported: bool | None = None
    ladder = host_paths._requested_model_ladder(
        provider=provider,
        preferred_model_override=None,
        fallback_model_override=None,
        disable_auto_probe=False,
    )
    preferred_model = ladder[0]
    current_model = preferred_model
    attempted_models: list[str] = []
    run_result: dict[str, Any] | None = None
    failure_class: str | None = None

    for attempt_index in range(1, max_attempts + 1):
        run_result = _run_raw_provider_task(
            provider,
            prompt=prompt,
            project_root=project_root,
            model=current_model,
            auth_mode=auth_mode,
            approval_mode=approval_mode,
            precheck=precheck,
        )
        failure_class = classify_failure(f"{run_result['stdout']}\n{run_result['stderr']}")
        if failure_class is None and run_result["exit_code"] == 124:
            failure_class = "operator_timeout"
        attempted_models.append(current_model)

        if provider == "gemini" and current_model == MODEL_MATRIX["gemini"]["operator"].preferred:
            auto_supported = run_result["exit_code"] == 0 and failure_class != "model_unavailable"

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
        if attempt_index < max_attempts:
            time.sleep(30)

    if run_result is None:
        raise RuntimeError("raw operator attempt loop produced no run result")

    return (
        run_result,
        failure_class,
        current_model,
        preferred_model,
        auto_supported,
        attempted_models,
    )


def _run_raw_provider_task(
    provider: str,
    *,
    prompt: str,
    project_root: Path,
    model: str,
    auth_mode: str,
    approval_mode: str | None,
    precheck: dict[str, Any],
) -> dict[str, Any]:
    if provider == "claude":
        return _run_raw_claude_task(prompt, project_root=project_root, model=model, auth_mode=auth_mode)
    if provider == "gemini":
        return _run_raw_gemini_task(
            prompt,
            project_root=project_root,
            model=model,
            auth_mode=auth_mode,
            approval_mode=approval_mode,
        )
    raise ValueError(f"unsupported raw operator provider: {provider}")


def _resume_raw_provider_task(
    provider: str,
    *,
    prompt: str,
    project_root: Path,
    model: str,
    auth_mode: str,
    session_id: str | None,
    approval_mode: str | None,
    precheck: dict[str, Any],
) -> dict[str, Any]:
    if provider == "claude":
        return _run_raw_claude_task(
            prompt,
            project_root=project_root,
            model=model,
            auth_mode=auth_mode,
            resume_session=session_id,
        )
    if provider == "gemini":
        return _run_raw_gemini_task(
            prompt,
            project_root=project_root,
            model=model,
            auth_mode=auth_mode,
            resume_session=session_id,
            approval_mode=approval_mode,
        )
    raise ValueError(f"unsupported raw operator provider: {provider}")


def _run_raw_claude_task(
    prompt: str,
    *,
    project_root: Path,
    model: str,
    auth_mode: str,
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
        "8",
        "--permission-mode",
        "bypassPermissions",
        "--setting-sources",
        "local",
    ]
    if auth_mode != "claude_code":
        return host_paths._unsupported_operator_mode("claude", auth_mode, command)
    if resume_session:
        command.extend(["--resume", resume_session])
    return host_paths._run_timed_command(
        command,
        cwd=project_root,
        timeout_seconds=180.0,
    )


def _run_raw_gemini_task(
    prompt: str,
    *,
    project_root: Path,
    model: str,
    auth_mode: str,
    resume_session: str | None = None,
    approval_mode: str | None = None,
) -> dict[str, Any]:
    if auth_mode not in {"google_login", "api_key"}:
        return host_paths._unsupported_operator_mode("gemini", auth_mode, ["gemini"])
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
    return host_paths._run_timed_command(
        command,
        cwd=project_root,
        timeout_seconds=180.0,
    )


def _run_openai_variant(
    *,
    variant: str,
    scenario_id: str,
    repeat_index: int,
    precheck: dict[str, Any],
) -> dict[str, Any]:
    root = operator_directionality_root("openai", variant)
    project_root = prepare_harness_workspace(
        provider="openai",
        lane=f"operator_directionality/{variant}",
        scenario_id=scenario_id,
        repeat_index=repeat_index,
    )
    auth_mode = resolve_auth_mode("openai", "operator")
    if scenario_id == "restart_continuity":
        return _run_openai_restart_continuity_variant(
            variant=variant,
            scenario_id=scenario_id,
            repeat_index=repeat_index,
            project_root=project_root,
            root=root,
            auth_mode=auth_mode,
        )

    prompt = read_prompt_template(_SCENARIOS[scenario_id]["prompt_file"])
    with _openai_variant_env(variant, precheck) as env:
        run_state, failure_class, model, attempted_models = _run_openai_single_turn_attempts(
            project_root=project_root,
            prompt=prompt,
            auth_mode=auth_mode,
            scenario_id=scenario_id,
            env=env,
            stderr_path=root / f"{scenario_id}__run_{repeat_index:03d}.live.stderr.log",
        )
    payload = openai_operator._materialize_run(
        root=root,
        project_root=project_root,
        scenario_id=scenario_id,
        repeat_index=repeat_index,
        auth_mode=auth_mode,
        model=model,
        run_state=run_state,
        failure_class=failure_class,
        run_test=_SCENARIOS[scenario_id]["run_test"],
    )
    payload["variant"] = variant
    payload["surface"] = _SURFACE_LABEL["openai"]
    payload["attempted_models"] = attempted_models
    return payload


def _run_openai_restart_continuity_variant(
    *,
    variant: str,
    scenario_id: str,
    repeat_index: int,
    project_root: Path,
    root: Path,
    auth_mode: str,
) -> dict[str, Any]:
    first_prompt = read_prompt_template(_SCENARIOS[scenario_id]["turn1_prompt_file"])
    second_prompt = read_prompt_template(_SCENARIOS[scenario_id]["turn2_prompt_file"])
    with _openai_variant_env(variant, {"status": "ready"}) as env:
        first_state, first_failure, model, attempted_models = _run_openai_single_turn_attempts(
            project_root=project_root,
            prompt=first_prompt,
            auth_mode=auth_mode,
            scenario_id=f"{scenario_id}_turn_1",
            env=env,
            stderr_path=root / f"{scenario_id}__run_{repeat_index:03d}.turn1.live.stderr.log",
        )
        if first_failure is not None:
            payload = openai_operator._materialize_run(
                root=root,
                project_root=project_root,
                scenario_id=scenario_id,
                repeat_index=repeat_index,
                auth_mode=auth_mode,
                model=model,
                run_state=first_state,
                failure_class=first_failure,
                run_test=False,
                notes="Continuity stopped at the first App Server turn.",
            )
            payload["variant"] = variant
            payload["surface"] = _SURFACE_LABEL["openai"]
            payload["attempted_models"] = attempted_models
            return payload

        thread_id = openai_operator._extract_thread_id(first_state["thread_read"])
        second_state, second_failure = openai_operator._run_resumed_turn(
            project_root=project_root,
            prompt=second_prompt,
            auth_mode=auth_mode,
            model=model,
            thread_id=thread_id,
            env=env,
            stderr_path=root / f"{scenario_id}__run_{repeat_index:03d}.turn2.live.stderr.log",
        )
        combined_state = {
            "started_at": first_state["started_at"],
            "ended_at": second_state["ended_at"],
            "timeline": first_state["timeline"] + second_state["timeline"],
            "stderr_text": "\n".join(
                text for text in (first_state["stderr_text"], second_state["stderr_text"]) if text
            ),
            "thread_read": second_state["thread_read"],
            "thread_id": thread_id,
            "lifecycle_summary": openai_operator.summarize_app_server_timeline(
                first_state["timeline"] + second_state["timeline"],
                thread_read=second_state["thread_read"],
            ),
        }
    payload = openai_operator._materialize_run(
        root=root,
        project_root=project_root,
        scenario_id=scenario_id,
        repeat_index=repeat_index,
        auth_mode=auth_mode,
        model=model,
        run_state=combined_state,
        failure_class=second_failure,
        run_test=True,
    )
    payload["variant"] = variant
    payload["surface"] = _SURFACE_LABEL["openai"]
    payload["attempted_models"] = attempted_models
    payload["thread_id"] = combined_state["lifecycle_summary"].get("thread_id")
    return payload


def _run_openai_single_turn_attempts(
    *,
    project_root: Path,
    prompt: str,
    auth_mode: str,
    scenario_id: str,
    env: dict[str, str] | None,
    stderr_path: Path,
) -> tuple[dict[str, Any], str | None, str, list[str]]:
    preferred_model = MODEL_MATRIX["openai"]["operator"].preferred
    attempted_models = [preferred_model]
    state, failure_class = openai_operator._run_single_turn(
        project_root=project_root,
        prompt=prompt,
        auth_mode=auth_mode,
        model=preferred_model,
        scenario_id=scenario_id,
        ephemeral=True,
        env=env,
        stderr_path=stderr_path,
    )
    chosen_model = choose_model("openai", "operator", first_failure=failure_class)
    if chosen_model != preferred_model:
        state, failure_class = openai_operator._run_single_turn(
            project_root=project_root,
            prompt=prompt,
            auth_mode=auth_mode,
            model=chosen_model,
            scenario_id=scenario_id,
            ephemeral=True,
            env=env,
            stderr_path=stderr_path,
        )
        attempted_models.append(chosen_model)
    return state, failure_class, chosen_model, attempted_models


@contextmanager
def _openai_variant_env(
    variant: str,
    precheck: dict[str, Any],
) -> Iterator[dict[str, str] | None]:
    if variant != "raw_host":
        yield None
        return
    codex_auth_path = Path.home() / ".codex" / "auth.json"
    if not codex_auth_path.exists():
        raise RuntimeError("raw OpenAI directionality run requires ~/.codex/auth.json")
    tmp_root = Path(tempfile.mkdtemp(prefix="cortex-directionality-codex-"))
    try:
        shutil.copy2(codex_auth_path, tmp_root / "auth.json")
        env = dict(os.environ)
        env["CODEX_HOME"] = str(tmp_root)
        yield env
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)


def _raw_host_precheck(provider: str) -> dict[str, Any]:
    if provider == "claude":
        help_result = run_command(["claude", "--help"], timeout_seconds=30.0)
        text = f"{help_result['stdout']}\n{help_result['stderr']}"
        if "--setting-sources" not in text:
            return {
                "status": "blocked",
                "reason": _RAW_BASELINE_FAILURE,
                "note": "Claude raw baseline cannot be isolated because the current CLI has no supported settings-source override.",
                "isolation_mode": None,
            }
        return {
            "status": "ready",
            "reason": None,
            "note": "Claude raw baseline uses --setting-sources local to avoid user-level hook/config injection.",
            "isolation_mode": "setting_sources_local",
        }

    if provider == "gemini":
        settings_path = Path.home() / ".gemini" / "settings.json"
        if settings_path.exists():
            try:
                payload = json.loads(settings_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                payload = {}
            if isinstance(payload, dict) and "hooks" in payload:
                return {
                    "status": "blocked",
                    "reason": _RAW_BASELINE_FAILURE,
                    "note": "Gemini raw baseline is contaminated by user-level hook configuration.",
                    "isolation_mode": None,
                }
        return {
            "status": "ready",
            "reason": None,
            "note": "Gemini raw baseline uses the same CLI surface without project-level hook injection.",
            "isolation_mode": "no_project_hook_injection",
        }

    codex_auth_path = Path.home() / ".codex" / "auth.json"
    if not codex_auth_path.exists():
        return {
            "status": "blocked",
            "reason": _RAW_BASELINE_FAILURE,
            "note": "OpenAI raw baseline requires auth.json so CODEX_HOME can be isolated from user config.",
            "isolation_mode": None,
        }
    return {
        "status": "ready",
        "reason": None,
        "note": "OpenAI raw baseline uses codex app-server with an isolated CODEX_HOME that carries only auth.json.",
        "isolation_mode": "isolated_codex_home_auth_only",
    }


def _blocked_raw_payload(
    provider: str,
    *,
    scenario_id: str,
    repeat_index: int,
    reason: str | None,
) -> dict[str, Any]:
    root = operator_directionality_root(provider, "raw_host")
    artifact_path = root / f"{scenario_id}__run_{repeat_index:03d}.blocked.json"
    payload = {
        "provider": provider,
        "variant": "raw_host",
        "scenario_id": scenario_id,
        "repeat_index": repeat_index,
        "surface": _SURFACE_LABEL[provider],
        "success": False,
        "failure_class": reason or _RAW_BASELINE_FAILURE,
        "notes": "Skipped raw-host paired run because the baseline could not be isolated safely on this machine.",
    }
    write_json(artifact_path, payload)
    payload["artifact_path"] = str(artifact_path.relative_to(root.parents[4]))
    return payload


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
