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

from cortex.sre.executive_summary import build_executive_signal_summary
from cortex.sre.modulators import ExecutiveModulatorMemory, update_executive_modulators
from cortex.sre.operator_routing import (
    build_operator_route_diagnostics,
    select_operator_route_with_policy,
)
from cortex.sre.policy_view import build_executive_policy_view
from lab.live_operator_route_state import (
    build_operator_summary_inputs,
    build_operator_task_state,
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
        live_evidence_fields,
        now_utc_iso,
        operator_directionality_root,
        prepare_harness_workspace,
        read_prompt_template,
        recent_operator_probe_failure,
        resolve_auth_mode,
        rewrite_artifact_payload,
        run_command,
        run_target_test,
        summarize_operator_runs,
        write_json,
    )
except ImportError:  # pragma: no cover
    import live_host_native_product_paths as host_paths
    import live_openai_app_server_operator as openai_operator
    from lab.live_validation_common import (
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
        live_evidence_fields,
        now_utc_iso,
        operator_directionality_root,
        prepare_harness_workspace,
        read_prompt_template,
        recent_operator_probe_failure,
        resolve_auth_mode,
        rewrite_artifact_payload,
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
        prog="python3 lab/live_operator_directionality.py",
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
    parser.add_argument(
        "--cortex-execution-flavor",
        choices=("auto", "minimal", "wrapped"),
        default="auto",
    )
    args = parser.parse_args(argv)

    ensure_live_validation_dirs()
    providers = ("claude", "gemini", "openai") if args.provider == "all" else (args.provider,)
    scenarios = tuple(_SCENARIOS) if args.scenario == "all" else (args.scenario,)

    provider_updates: dict[str, Any] = {}
    for provider in providers:
        provider_updates[provider] = _run_provider(
            provider,
            scenarios=scenarios,
            repeat_count=max(1, args.repeat_count),
            cortex_execution_flavor_override=args.cortex_execution_flavor,
        )
        summary = _merged_provider_summaries(provider_updates)
        write_json(comparator_path("operator_directionality_summary.json"), summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def _run_provider(
    provider: str,
    *,
    scenarios: tuple[str, ...],
    repeat_count: int,
    cortex_execution_flavor_override: str,
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
                cortex_execution_flavor_override=cortex_execution_flavor_override,
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
        **live_evidence_fields(lane="operator"),
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
    cortex_execution_flavor_override: str,
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

    provider_window_caution = _provider_window_caution(provider, prior_variant_runs)
    if provider_window_caution is not None:
        raw_payload = _blocked_raw_payload(
            provider,
            scenario_id=scenario_id,
            repeat_index=repeat_index,
            reason="blocked_by_provider_window_caution",
        )
        raw_payload["provider_window_caution"] = True
        raw_payload["provider_window_note"] = provider_window_caution
        raw_payload["comparison_contaminated"] = True
        return {
            "provider": provider,
            "scenario_id": scenario_id,
            "repeat_index": repeat_index,
            "pair_status": "blocked",
            "blocked_reason": "blocked_by_provider_window_caution",
            "raw_host": raw_payload,
            "cortex_operator": None,
            "variant_order": list(_variant_order(repeat_index)),
        }

    pair_payloads: dict[str, dict[str, Any]] = {}
    variant_order = _variant_order(repeat_index)
    for variant in variant_order:
        pair_payloads[variant] = _run_variant(
            provider,
            variant=variant,
            scenario_id=scenario_id,
            repeat_index=repeat_index,
            precheck=precheck,
            baseline_runs=baseline_runs,
            prior_runs=prior_variant_runs[variant],
            cortex_execution_flavor_override=cortex_execution_flavor_override,
        )
    return {
        "provider": provider,
        "scenario_id": scenario_id,
        "repeat_index": repeat_index,
        "pair_status": "compared",
        "blocked_reason": None,
        "variant_order": list(variant_order),
        "raw_host": pair_payloads["raw_host"],
        "cortex_operator": pair_payloads["cortex_operator"],
    }


def _variant_order(repeat_index: int) -> tuple[str, str]:
    return ("raw_host", "cortex_operator") if repeat_index % 2 == 1 else ("cortex_operator", "raw_host")


def _merged_provider_summaries(provider_updates: dict[str, Any] | None = None) -> dict[str, Any]:
    updates = {} if provider_updates is None else dict(provider_updates)
    summary = {
        "generated_at": now_utc_iso(),
        "surface": "operator_directionality",
        "lane": "operator",
        **live_evidence_fields(lane="operator"),
        "providers": {},
    }
    for provider in ("claude", "gemini", "openai"):
        payload = updates.get(provider)
        if payload is None:
            payload = _read_json(operator_directionality_root(provider, "summary") / "summary.json")
        if payload:
            summary["providers"][provider] = payload
    return summary


def _run_variant(
    provider: str,
    *,
    variant: str,
    scenario_id: str,
    repeat_index: int,
    precheck: dict[str, Any],
    baseline_runs: list[dict[str, Any]],
    prior_runs: tuple[dict[str, Any], ...],
    cortex_execution_flavor_override: str = "auto",
) -> dict[str, Any]:
    if provider == "openai":
        return _run_openai_variant(
            variant=variant,
            scenario_id=scenario_id,
            repeat_index=repeat_index,
            precheck=precheck,
            baseline_runs=baseline_runs,
            prior_runs=prior_runs,
            cortex_execution_flavor_override=cortex_execution_flavor_override,
        )
    return _run_cli_variant(
        provider,
        variant=variant,
        scenario_id=scenario_id,
        repeat_index=repeat_index,
        precheck=precheck,
        baseline_runs=baseline_runs,
        prior_runs=prior_runs,
        cortex_execution_flavor_override=cortex_execution_flavor_override,
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
    cortex_execution_flavor_override: str = "auto",
) -> dict[str, Any]:
    root = operator_directionality_root(provider, variant)
    project_root = prepare_harness_workspace(
        provider=provider,
        lane=f"operator_directionality/{variant}",
        scenario_id=scenario_id,
        repeat_index=repeat_index,
    )
    if scenario_id == "restart_continuity":
        return _run_cli_restart_continuity_variant(
            provider,
            variant=variant,
            scenario_id=scenario_id,
            repeat_index=repeat_index,
            project_root=project_root,
            root=root,
            hook_log_path=None,
            precheck=precheck,
            baseline_runs=baseline_runs,
            prior_runs=prior_runs,
            cortex_execution_flavor_override=cortex_execution_flavor_override,
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
    summary = build_executive_signal_summary(
        build_operator_summary_inputs(
            route_state,
            previous_same_host_run_failed_before_completion=summarize_operator_runs(
                prior_runs,
                scenario_id=scenario_id,
            )["previous_failed_before_completion"],
            recent_probe_failure_class=recent_operator_probe_failure(provider),
            recent_product_failure_class=summarize_operator_runs(
                prior_runs,
                scenario_id=scenario_id,
            )["latest_failure_class"],
            recent_warning_bearing_success_present=summarize_operator_runs(baseline_runs)["warning_bearing_success_present"],
            verification_required=bool(_SCENARIOS[scenario_id]["run_test"]),
        )
    )
    previous_memory = _latest_modulator_memory(prior_runs)
    modulator_update = update_executive_modulators(summary, previous_memory)
    policy_view = build_executive_policy_view(summary, modulator_update.state)
    route_decision = select_operator_route_with_policy(route_state, modulator_update, policy_view)
    route_diagnostics = build_operator_route_diagnostics(route_state, route_decision)
    execution_flavor = "wrapped"
    hook_log_path = None
    if variant == "cortex_operator":
        execution_flavor, execution_updates = host_paths._resolve_cortex_execution_flavor(
            provider=provider,
            scenario_id=scenario_id,
            override=cortex_execution_flavor_override,
        )
        route_diagnostics.update(execution_updates)
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
        hook_log_path = host_paths._configure_hook_capture(
            provider=provider,
            project_root=project_root,
            scenario_id=scenario_id,
            repeat_index=repeat_index,
            execution_flavor=execution_flavor,
            log_root=root,
        )
    if variant == "cortex_operator":
        run_result, failure_class, chosen_model, preferred_model, auto_supported, attempted_models = host_paths._run_operator_attempts(
            provider=provider,
            prompt=prompt,
            project_root=project_root,
            auth_mode=auth_mode,
            approval_mode=None,
            hook_log_path=hook_log_path,
            scenario_id=scenario_id,
            max_attempts=1 + route_decision.budget.max_retries,
            cooldown_seconds=30,
            preferred_model_override=None,
            fallback_model_override=None,
            disable_auto_probe=False,
            execution_flavor=execution_flavor,
        )
    else:
        run_result, failure_class, chosen_model, preferred_model, auto_supported, attempted_models = _run_raw_operator_attempts(
            provider=provider,
            prompt=prompt,
            project_root=project_root,
            auth_mode=auth_mode,
            approval_mode=None,
            precheck=precheck,
            scenario_id=scenario_id,
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
    _attach_extra_read_defaults(payload)
    if (
        scenario_id == "truth_gap"
        and route_decision.budget.allow_extra_read_pass
        and (variant != "cortex_operator" or execution_flavor != "minimal")
        and payload.get("truth_gap_kind") == "truthful_incomplete"
        and not payload.get("provider_limit_interference")
    ):
        payload = _maybe_run_cli_extra_read_pass(
            provider=provider,
            variant=variant,
            project_root=project_root,
            prompt=read_prompt_template("truth_gap_recheck_operator.md"),
            auth_mode=auth_mode,
            chosen_model=chosen_model,
            session_id=extract_session_id(provider, host_paths.parse_json_records(run_result["stdout"])[0]),
            root=root,
            hook_log_path=hook_log_path,
            repeat_index=repeat_index,
            first_payload=payload,
            route_diagnostics=route_diagnostics,
        )
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
    cortex_execution_flavor_override: str = "auto",
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
    summary = build_executive_signal_summary(
        build_operator_summary_inputs(
            route_state,
            previous_same_host_run_failed_before_completion=summarize_operator_runs(
                prior_runs,
                scenario_id=scenario_id,
            )["previous_failed_before_completion"],
            recent_probe_failure_class=recent_operator_probe_failure(provider),
            recent_product_failure_class=summarize_operator_runs(
                prior_runs,
                scenario_id=scenario_id,
            )["latest_failure_class"],
            recent_warning_bearing_success_present=summarize_operator_runs(baseline_runs)["warning_bearing_success_present"],
            verification_required=True,
        )
    )
    previous_memory = _latest_modulator_memory(prior_runs)
    modulator_update = update_executive_modulators(summary, previous_memory)
    policy_view = build_executive_policy_view(summary, modulator_update.state)
    route_decision = select_operator_route_with_policy(route_state, modulator_update, policy_view)
    route_diagnostics = build_operator_route_diagnostics(route_state, route_decision)
    execution_flavor = "wrapped"
    if variant == "cortex_operator":
        execution_flavor, execution_updates = host_paths._resolve_cortex_execution_flavor(
            provider=provider,
            scenario_id=scenario_id,
            override=cortex_execution_flavor_override,
        )
        route_diagnostics.update(execution_updates)
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
        hook_log_path = host_paths._configure_hook_capture(
            provider=provider,
            project_root=project_root,
            scenario_id=scenario_id,
            repeat_index=repeat_index,
            execution_flavor=execution_flavor,
            log_root=root,
        )

    if variant == "cortex_operator":
        first_result, first_failure, chosen_model, preferred_model, auto_supported, attempted_models = host_paths._run_operator_attempts(
            provider=provider,
            prompt=first_prompt,
            project_root=project_root,
            auth_mode=auth_mode,
            approval_mode=None,
            hook_log_path=hook_log_path,
            scenario_id="restart_continuity",
            max_attempts=1 + route_decision.budget.max_retries,
            cooldown_seconds=30,
            preferred_model_override=None,
            fallback_model_override=None,
            disable_auto_probe=False,
            execution_flavor=execution_flavor,
        )
    else:
        first_result, first_failure, chosen_model, preferred_model, auto_supported, attempted_models = _run_raw_operator_attempts(
            provider=provider,
            prompt=first_prompt,
            project_root=project_root,
            auth_mode=auth_mode,
            approval_mode=None,
            precheck=precheck,
            scenario_id="restart_continuity",
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

    first_records, _first_extraction_mode = host_paths.parse_json_records(first_result["stdout"])
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
            scenario_id="restart_continuity",
            execution_flavor=execution_flavor,
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
            scenario_id="restart_continuity",
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
    scenario_id: str,
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
            scenario_id=scenario_id,
        )
        failure_class = classify_failure(f"{run_result['stdout']}\n{run_result['stderr']}")
        if failure_class is None and run_result["exit_code"] == 124:
            failure_class = "operator_timeout"
        attempted_models.append(current_model)

        if provider == "gemini" and current_model == MODEL_MATRIX["gemini"]["operator"].preferred:
            auto_supported = failure_class != "model_unavailable"

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
    scenario_id: str | None = None,
) -> dict[str, Any]:
    if provider == "claude":
        return _run_raw_claude_task(
            prompt,
            project_root=project_root,
            model=model,
            auth_mode=auth_mode,
            scenario_id=scenario_id,
        )
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
    scenario_id: str | None = None,
) -> dict[str, Any]:
    if provider == "claude":
        return _run_raw_claude_task(
            prompt,
            project_root=project_root,
            model=model,
            auth_mode=auth_mode,
            resume_session=session_id,
            scenario_id=scenario_id,
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
    scenario_id: str | None = None,
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
        str(host_paths._claude_max_turns(scenario_id, resume_session=resume_session)),
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
    baseline_runs: list[dict[str, Any]],
    prior_runs: tuple[dict[str, Any], ...],
    cortex_execution_flavor_override: str = "auto",
) -> dict[str, Any]:
    root = operator_directionality_root("openai", variant)
    project_root = prepare_harness_workspace(
        provider="openai",
        lane=f"operator_directionality/{variant}",
        scenario_id=scenario_id,
        repeat_index=repeat_index,
    )
    auth_mode = resolve_auth_mode("openai", "operator")
    route_state = build_operator_task_state(
        scenario_id,
        previous_same_host_run_failed_before_completion=summarize_operator_runs(
            prior_runs,
            scenario_id=scenario_id,
        )["previous_failed_before_completion"],
        recent_probe_failure_class=recent_operator_probe_failure("openai"),
        recent_baseline_clean_count=summarize_operator_runs(baseline_runs)["clean_success_count"],
        recent_warning_bearing_success_present=summarize_operator_runs(baseline_runs)["warning_bearing_success_present"],
        recent_product_failure_class=summarize_operator_runs(
            prior_runs,
            scenario_id=scenario_id,
        )["latest_failure_class"],
    )
    summary = build_executive_signal_summary(
        build_operator_summary_inputs(
            route_state,
            previous_same_host_run_failed_before_completion=summarize_operator_runs(
                prior_runs,
                scenario_id=scenario_id,
            )["previous_failed_before_completion"],
            recent_probe_failure_class=recent_operator_probe_failure("openai"),
            recent_product_failure_class=summarize_operator_runs(
                prior_runs,
                scenario_id=scenario_id,
            )["latest_failure_class"],
            recent_warning_bearing_success_present=summarize_operator_runs(baseline_runs)["warning_bearing_success_present"],
            verification_required=bool(_SCENARIOS[scenario_id]["run_test"]),
        )
    )
    previous_memory = _latest_modulator_memory(prior_runs)
    modulator_update = update_executive_modulators(summary, previous_memory)
    policy_view = build_executive_policy_view(summary, modulator_update.state)
    route_decision = select_operator_route_with_policy(route_state, modulator_update, policy_view)
    route_diagnostics = build_operator_route_diagnostics(route_state, route_decision)
    if route_decision.blocked_reason is not None:
        payload = host_paths._blocked_operator_route_payload(
            provider="openai",
            scenario_id=scenario_id,
            repeat_index=repeat_index,
            route_diagnostics=route_diagnostics,
            failure_class=host_paths._blocked_route_failure_class(
                route_state,
                recent_probe_failure_class=recent_operator_probe_failure("openai"),
                recent_product_failure_class=summarize_operator_runs(
                    prior_runs,
                    scenario_id=scenario_id,
                )["latest_failure_class"],
            ),
            notes="Route selector blocked paired execution before host work started.",
        )
        payload["variant"] = variant
        payload["surface"] = _SURFACE_LABEL["openai"]
        payload["attempted_models"] = []
        return payload
    if scenario_id == "restart_continuity":
        return _run_openai_restart_continuity_variant(
            variant=variant,
            scenario_id=scenario_id,
            repeat_index=repeat_index,
            project_root=project_root,
            root=root,
            auth_mode=auth_mode,
            route_diagnostics=route_diagnostics,
            require_verification=route_decision.budget.require_verification,
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
            ephemeral=not route_decision.budget.allow_extra_read_pass,
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
            run_test=route_decision.budget.require_verification and _SCENARIOS[scenario_id]["run_test"],
            route_diagnostics=route_diagnostics,
        )
        payload["variant"] = variant
        payload["surface"] = _SURFACE_LABEL["openai"]
        payload["attempted_models"] = attempted_models
        _attach_extra_read_defaults(payload)
        if (
            scenario_id == "truth_gap"
            and route_decision.budget.allow_extra_read_pass
            and payload.get("truth_gap_kind") == "truthful_incomplete"
            and not payload.get("provider_limit_interference")
        ):
            payload = _maybe_run_openai_extra_read_pass(
                project_root=project_root,
                prompt=read_prompt_template("truth_gap_recheck_operator.md"),
                auth_mode=auth_mode,
                model=model,
                thread_id=run_state.get("thread_id"),
                env=env,
                root=root,
                repeat_index=repeat_index,
                first_payload=payload,
                route_diagnostics=route_diagnostics,
            )
    return payload


def _run_openai_restart_continuity_variant(
    *,
    variant: str,
    scenario_id: str,
    repeat_index: int,
    project_root: Path,
    root: Path,
    auth_mode: str,
    route_diagnostics: dict[str, Any],
    require_verification: bool,
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
            ephemeral=False,
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
                route_diagnostics=route_diagnostics,
                continuity_diagnostics=openai_operator._continuity_diagnostics(
                    thread_ephemeral=False,
                    failure_class=first_failure,
                ),
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
        run_test=require_verification,
        route_diagnostics=route_diagnostics,
        continuity_diagnostics=openai_operator._continuity_diagnostics(
            thread_ephemeral=False,
            failure_class=second_failure,
        ),
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
    ephemeral: bool = True,
) -> tuple[dict[str, Any], str | None, str, list[str]]:
    preferred_model = MODEL_MATRIX["openai"]["operator"].preferred
    attempted_models = [preferred_model]
    state, failure_class = openai_operator._run_single_turn(
        project_root=project_root,
        prompt=prompt,
        auth_mode=auth_mode,
        model=preferred_model,
        scenario_id=scenario_id,
        ephemeral=ephemeral,
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
            ephemeral=ephemeral,
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
        "lane": "operator",
        **live_evidence_fields(lane="operator"),
        "variant": "raw_host",
        "scenario_id": scenario_id,
        "repeat_index": repeat_index,
        "surface": _SURFACE_LABEL[provider],
        "success": False,
        "failure_class": reason or _RAW_BASELINE_FAILURE,
        "notes": "Skipped raw-host paired run because the baseline could not be isolated safely on this machine.",
        "token_usage_visible": False,
        "input_tokens": None,
        "output_tokens": None,
        "cache_tokens": None,
        "provider_limit_interference": False,
        "provider_limit_kind": None,
        "comparison_contaminated": True,
        "provider_window_caution": False,
        "provider_window_note": None,
    }
    write_json(artifact_path, payload)
    payload["artifact_path"] = str(artifact_path.relative_to(root.parents[4]))
    return payload


def _attach_extra_read_defaults(payload: dict[str, Any]) -> None:
    payload.setdefault("extra_read_pass_attempted", False)
    payload.setdefault("extra_read_pass_completed", False)
    payload.setdefault("extra_read_pass_mode", None)
    payload.setdefault("extra_read_pass_failure_class", None)


def _maybe_run_cli_extra_read_pass(
    *,
    provider: str,
    variant: str,
    project_root: Path,
    prompt: str,
    auth_mode: str,
    chosen_model: str,
    session_id: str | None,
    root: Path,
    hook_log_path: Path | None,
    repeat_index: int,
    first_payload: dict[str, Any],
    route_diagnostics: dict[str, Any],
) -> dict[str, Any]:
    if not session_id:
        first_payload.update(
            {
                "extra_read_pass_attempted": True,
                "extra_read_pass_completed": False,
                "extra_read_pass_mode": "resume",
                "extra_read_pass_failure_class": "operator_surface_missing",
                "comparison_contaminated": True,
            }
        )
        rewrite_artifact_payload(first_payload)
        return first_payload

    if variant == "cortex_operator":
        second_result = host_paths._resume_provider_task(
            provider,
            prompt=prompt,
            project_root=project_root,
            model=chosen_model,
            auth_mode=auth_mode,
            session_id=session_id,
            approval_mode="yolo" if provider == "gemini" else None,
            hook_log_path=hook_log_path,
            scenario_id="truth_gap",
        )
    else:
        second_result = _resume_raw_provider_task(
            provider,
            prompt=prompt,
            project_root=project_root,
            model=chosen_model,
            auth_mode=auth_mode,
            session_id=session_id,
            approval_mode="yolo" if provider == "gemini" else None,
            precheck={"status": "ready"},
            scenario_id="truth_gap",
        )
    second_failure = classify_failure(f"{second_result['stdout']}\n{second_result['stderr']}")
    if second_failure is None and second_result["exit_code"] == 124:
        second_failure = "operator_timeout"

    second_payload = host_paths._materialize_operator_run(
        provider=provider,
        scenario_id="truth_gap",
        repeat_index=repeat_index,
        project_root=project_root,
        root=root,
        run_result=second_result,
        model=chosen_model,
        preferred_model=first_payload["preferred_model"],
        auto_supported=first_payload.get("auto_supported"),
        attempted_models=list(first_payload.get("attempted_models", [])) + [chosen_model],
        auth_mode=auth_mode,
        failure_class=second_failure,
        hook_log_path=hook_log_path,
        run_verification=False,
        route_diagnostics=route_diagnostics,
    )
    second_payload["variant"] = variant
    second_payload["surface"] = _SURFACE_LABEL[provider]
    second_payload["attempted_models"] = list(first_payload.get("attempted_models", [])) + [chosen_model]
    _attach_extra_read_defaults(second_payload)

    if second_payload.get("truth_gap_kind") == "truthful_incomplete" and not second_payload.get(
        "provider_limit_interference"
    ):
        second_payload.update(
            {
                "extra_read_pass_attempted": True,
                "extra_read_pass_completed": True,
                "extra_read_pass_mode": "resume",
                "extra_read_pass_failure_class": None,
            }
        )
        rewrite_artifact_payload(second_payload)
        return second_payload

    first_payload.update(
        {
            "extra_read_pass_attempted": True,
            "extra_read_pass_completed": False,
            "extra_read_pass_mode": "resume",
            "extra_read_pass_failure_class": second_failure or "truth_gap_not_reaffirmed",
            "comparison_contaminated": True,
        }
    )
    rewrite_artifact_payload(first_payload)
    return first_payload


def _maybe_run_openai_extra_read_pass(
    *,
    project_root: Path,
    prompt: str,
    auth_mode: str,
    model: str,
    thread_id: str | None,
    env: dict[str, str] | None,
    root: Path,
    repeat_index: int,
    first_payload: dict[str, Any],
    route_diagnostics: dict[str, Any],
) -> dict[str, Any]:
    second_state, second_failure = openai_operator._run_resumed_turn(
        project_root=project_root,
        prompt=prompt,
        auth_mode=auth_mode,
        model=model,
        thread_id=thread_id,
        env=env,
        stderr_path=root / f"truth_gap__run_{repeat_index:03d}.recheck.live.stderr.log",
    )
    second_payload = openai_operator._materialize_run(
        root=root,
        project_root=project_root,
        scenario_id="truth_gap",
        repeat_index=repeat_index,
        auth_mode=auth_mode,
        model=model,
        run_state=second_state,
        failure_class=second_failure,
        run_test=False,
        route_diagnostics=route_diagnostics,
        continuity_diagnostics={
            "continuity_transport": "thread_resume",
            "thread_ephemeral": False,
            "continuity_failure_kind": None,
        },
    )
    second_payload["variant"] = first_payload["variant"]
    second_payload["surface"] = first_payload["surface"]
    second_payload["attempted_models"] = list(first_payload.get("attempted_models", []))
    _attach_extra_read_defaults(second_payload)
    if second_payload.get("truth_gap_kind") == "truthful_incomplete" and not second_payload.get(
        "provider_limit_interference"
    ):
        second_payload.update(
            {
                "extra_read_pass_attempted": True,
                "extra_read_pass_completed": True,
                "extra_read_pass_mode": "resume",
                "extra_read_pass_failure_class": None,
            }
        )
        rewrite_artifact_payload(second_payload)
        return second_payload
    first_payload.update(
        {
            "extra_read_pass_attempted": True,
            "extra_read_pass_completed": False,
            "extra_read_pass_mode": "resume",
            "extra_read_pass_failure_class": second_failure or "truth_gap_not_reaffirmed",
            "comparison_contaminated": True,
        }
    )
    rewrite_artifact_payload(first_payload)
    return first_payload


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _provider_window_caution(
    provider: str,
    prior_variant_runs: dict[str, tuple[dict[str, Any], ...]],
) -> str | None:
    if provider != "claude":
        return None
    recent_runs = [
        payload
        for runs in prior_variant_runs.values()
        for payload in runs
        if isinstance(payload, dict)
    ]
    if not recent_runs:
        return None
    latest = max(recent_runs, key=lambda payload: str(payload.get("ended_at", "")))
    if latest.get("provider_window_caution") or latest.get("provider_limit_interference"):
        return "Recent Claude provider-window interference suggests the current usage window is contaminated; skip this pair rather than spending another immediate attempt."
    return None


def _latest_modulator_memory(
    runs: tuple[dict[str, Any], ...],
) -> ExecutiveModulatorMemory | None:
    recent = [
        payload
        for payload in runs
        if isinstance(payload, dict) and isinstance(payload.get("modulator_memory"), dict)
    ]
    if not recent:
        return None
    latest = max(recent, key=lambda payload: str(payload.get("ended_at", "")))
    memory = latest["modulator_memory"]
    return ExecutiveModulatorMemory(
        focus_tonic=float(memory["focus_tonic"]),
        explore_tonic=float(memory["explore_tonic"]),
        stop_tonic=float(memory["stop_tonic"]),
        update_tonic=float(memory["update_tonic"]),
    )


if __name__ == "__main__":
    raise SystemExit(main())
