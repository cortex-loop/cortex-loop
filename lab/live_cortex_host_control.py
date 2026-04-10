"""Current loopback-service automation-lane probe for L2."""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from lab.live_validation_common import (
    MODEL_MATRIX,
    REPO_ROOT,
    apply_unified_diff,
    automation_auth_readiness,
    classify_failure,
    classify_truth_gap,
    collect_modified_files,
    comparator_path,
    ensure_live_validation_dirs,
    extract_result_text,
    extract_unified_diff,
    live_evidence_fields,
    load_local_env_file,
    now_utc_iso,
    prepare_harness_workspace,
    provider_root,
    read_prompt_template,
    run_target_test,
    write_json,
    write_text,
)


PROVIDER_CONFIG = {
    "claude": {
        "module": "cortex.hosts.claude.service",
        "runtime_label": "claude-service",
        "action_path": "/v1/actions/message-stream",
        "action_tag": "claude-message-stream",
    },
    "gemini": {
        "module": "cortex.hosts.gemini.service",
        "runtime_label": "gemini-service",
        "action_path": "/v1/actions/interaction-stream",
        "action_tag": "gemini-interaction-stream",
    },
    "openai": {
        "module": "cortex.hosts.openai.service",
        "runtime_label": "openai-service",
        "action_path": "/v1/actions/response-stream",
        "action_tag": "openai-response-stream",
    },
}

SERVICE_SUITES = {
    "current": {
        "suite_role": "readiness_probe",
        "scenario_ids": ("service_smoke", "service_restart_continuity"),
    },
    "canonical_anchor": {
        "suite_role": "canonical_truth_anchor",
        "scenario_ids": ("pass_minimal", "truth_gap", "restart_continuity"),
    },
}

_CANONICAL_ANCHOR_PROVIDERS = frozenset({"claude", "openai"})

SMOKE_PROMPT = "Respond exactly with OK."
_PATCH_TARGET = "src/normalize_port.py"
_WORKSPACE_CONTEXT_FILES = (
    "README_TASK.md",
    "src/normalize_port.py",
    "tests/test_normalize_port.py",
)
_INFRA_BLOCKERS = frozenset(
    {
        "auth_missing",
        "blocked_by_spend_policy",
        "mis_scoped",
        "capacity_exhausted",
        "quota_exhausted",
        "provider_internal_error",
        "operator_timeout",
    }
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 lab/live_cortex_host_control.py",
        description="Probe the current loopback-service automation lane.",
    )
    parser.add_argument(
        "--provider",
        choices=("claude", "gemini", "openai", "all"),
        default="all",
    )
    parser.add_argument(
        "--lane",
        choices=("automation",),
        default="automation",
    )
    parser.add_argument(
        "--suite",
        choices=tuple(SERVICE_SUITES),
        default="current",
    )
    args = parser.parse_args(argv)

    load_local_env_file()
    ensure_live_validation_dirs()
    providers = ("claude", "gemini", "openai") if args.provider == "all" else (args.provider,)
    summary = _build_summary(
        lane=args.lane,
        suite_id=args.suite,
        provider_payloads={provider: _capture_provider(provider, suite_id=args.suite) for provider in providers},
    )
    if args.provider == "all":
        write_json(comparator_path("cortex_live_summary.json"), summary)
    else:
        write_json(comparator_path(f"cortex_live_summary_{args.provider}.json"), summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def _build_summary(
    *,
    lane: str,
    suite_id: str,
    provider_payloads: dict[str, Any],
) -> dict[str, Any]:
    return {
        "generated_at": now_utc_iso(),
        "surface": "cortex_live_host_control",
        "lane": lane,
        "suite_id": suite_id,
        "suite_role": SERVICE_SUITES[suite_id]["suite_role"],
        **live_evidence_fields(lane=lane),
        "providers": provider_payloads,
    }


def _capture_provider(provider: str, *, suite_id: str) -> dict[str, Any]:
    root = provider_root(provider, "automation", "service")
    readiness = automation_auth_readiness(provider)
    auth_mode = readiness["auth_mode"]
    cycle_index = _next_service_cycle_index(root, suite_id)

    if suite_id == "current":
        cycle = _capture_current_suite_cycle(
            provider=provider,
            auth_mode=auth_mode,
            readiness=readiness,
            root=root,
            cycle_index=cycle_index,
        )
    else:
        cycle = _capture_canonical_anchor_cycle(
            provider=provider,
            auth_mode=auth_mode,
            readiness=readiness,
            root=root,
            cycle_index=cycle_index,
        )

    summary = _update_service_summary(root=root, provider=provider, cycle=cycle)
    return summary["suites"][suite_id]


def _capture_current_suite_cycle(
    *,
    provider: str,
    auth_mode: str,
    readiness: dict[str, Any],
    root: Path,
    cycle_index: int,
) -> dict[str, Any]:
    suite_id = "current"
    suite_role = SERVICE_SUITES[suite_id]["suite_role"]
    smoke_model = _service_model_for_scenario(provider, "service_smoke")
    continuity_model = _service_model_for_scenario(provider, "service_restart_continuity")
    if readiness["status"] != "ready":
        runs = [
            _blocked_service_run(
                provider,
                auth_mode=auth_mode,
                model=smoke_model,
                root=root,
                scenario_id="service_smoke",
                readiness=readiness,
                suite_id=suite_id,
                suite_role=suite_role,
                cycle_index=cycle_index,
            ),
            _blocked_service_run(
                provider,
                auth_mode=auth_mode,
                model=continuity_model,
                root=root,
                scenario_id="service_restart_continuity",
                readiness=readiness,
                suite_id=suite_id,
                suite_role=suite_role,
                cycle_index=cycle_index,
            ),
        ]
    else:
        runs = [
            _run_single_live_call(
                provider,
                auth_mode=auth_mode,
                model=smoke_model,
                root=root,
                suite_id=suite_id,
                suite_role=suite_role,
                cycle_index=cycle_index,
            ),
            _run_continuity_capture(
                provider,
                auth_mode=auth_mode,
                model=continuity_model,
                root=root,
                suite_id=suite_id,
                suite_role=suite_role,
                cycle_index=cycle_index,
            ),
        ]
    return _build_cycle_payload(
        provider=provider,
        auth_mode=auth_mode,
        readiness=readiness,
        suite_id=suite_id,
        suite_role=suite_role,
        cycle_index=cycle_index,
        runs=runs,
    )


def _capture_canonical_anchor_cycle(
    *,
    provider: str,
    auth_mode: str,
    readiness: dict[str, Any],
    root: Path,
    cycle_index: int,
) -> dict[str, Any]:
    suite_id = "canonical_anchor"
    suite_role = SERVICE_SUITES[suite_id]["suite_role"]
    scenario_ids = SERVICE_SUITES[suite_id]["scenario_ids"]

    if provider not in _CANONICAL_ANCHOR_PROVIDERS:
        runs = [
            _blocked_service_run(
                provider,
                auth_mode=auth_mode,
                model=_service_model_for_scenario(provider, scenario_id),
                root=root,
                scenario_id=scenario_id,
                readiness={"status": "mis_scoped", "auth_mode": auth_mode},
                suite_id=suite_id,
                suite_role=suite_role,
                cycle_index=cycle_index,
                notes="`canonical_anchor` is implemented for OpenAI current product scope and retained for Claude future host-expansion plumbing.",
            )
            for scenario_id in scenario_ids
        ]
        return _build_cycle_payload(
            provider=provider,
            auth_mode=auth_mode,
            readiness=readiness,
            suite_id=suite_id,
            suite_role=suite_role,
            cycle_index=cycle_index,
            runs=runs,
        )

    if readiness["status"] != "ready":
        runs = [
            _blocked_service_run(
                provider,
                auth_mode=auth_mode,
                model=_service_model_for_scenario(provider, scenario_id),
                root=root,
                scenario_id=scenario_id,
                readiness=readiness,
                suite_id=suite_id,
                suite_role=suite_role,
                cycle_index=cycle_index,
            )
            for scenario_id in scenario_ids
        ]
        return _build_cycle_payload(
            provider=provider,
            auth_mode=auth_mode,
            readiness=readiness,
            suite_id=suite_id,
            suite_role=suite_role,
            cycle_index=cycle_index,
            runs=runs,
        )

    runs: list[dict[str, Any]] = []
    run_map = {
        "pass_minimal": _run_pass_minimal_capture,
        "truth_gap": _run_truth_gap_capture,
        "restart_continuity": _run_canonical_restart_continuity_capture,
    }
    failed = False
    for scenario_id in scenario_ids:
        model = _service_model_for_scenario(provider, scenario_id)
        if failed:
            runs.append(
                _skipped_service_run(
                    provider,
                    auth_mode=auth_mode,
                    model=model,
                    scenario_id=scenario_id,
                    suite_id=suite_id,
                    suite_role=suite_role,
                    cycle_index=cycle_index,
                    notes="Skipped after an earlier canonical-anchor failure in the same cycle.",
                )
            )
            continue
        run = run_map[scenario_id](
            provider=provider,
            auth_mode=auth_mode,
            model=model,
            root=root,
            suite_id=suite_id,
            suite_role=suite_role,
            cycle_index=cycle_index,
        )
        runs.append(run)
        failed = not run.get("success", False)

    return _build_cycle_payload(
        provider=provider,
        auth_mode=auth_mode,
        readiness=readiness,
        suite_id=suite_id,
        suite_role=suite_role,
        cycle_index=cycle_index,
        runs=runs,
    )


def _build_cycle_payload(
    *,
    provider: str,
    auth_mode: str,
    readiness: dict[str, Any],
    suite_id: str,
    suite_role: str,
    cycle_index: int,
    runs: list[dict[str, Any]],
) -> dict[str, Any]:
    failure_classes = sorted(
        {
            str(run.get("failure_class"))
            for run in runs
            if isinstance(run.get("failure_class"), str) and run.get("failure_class")
        }
    )
    warning_classes = sorted(
        {
            warning
            for run in runs
            for warning in run.get("warning_classes", [])
            if isinstance(warning, str) and warning
        }
    )
    success = bool(runs) and all(run.get("success") for run in runs) and not any(run.get("skipped") for run in runs)
    cycle_status = "positive" if success else "partial"
    if not success and any(failure in _INFRA_BLOCKERS for failure in failure_classes):
        cycle_status = "blocked"
    return {
        "generated_at": now_utc_iso(),
        "provider": provider,
        "lane": "automation",
        **live_evidence_fields(lane="automation"),
        "suite_id": suite_id,
        "suite_role": suite_role,
        "cycle_index": cycle_index,
        "auth_mode": auth_mode,
        "auth_readiness": readiness,
        "runs": runs,
        "success": success,
        "cycle_status": cycle_status,
        "failure_classes": failure_classes,
        "warning_classes": warning_classes,
    }


def _next_service_cycle_index(root: Path, suite_id: str) -> int:
    summary = _read_json(root / "service_runs.json")
    suites = summary.get("suites", {}) if isinstance(summary.get("suites"), dict) else {}
    suite_summary = suites.get(suite_id, {})
    cycles = suite_summary.get("cycles", []) if isinstance(suite_summary, dict) else []
    return len(cycles) + 1


def _update_service_summary(*, root: Path, provider: str, cycle: dict[str, Any]) -> dict[str, Any]:
    summary_path = root / "service_runs.json"
    existing = _read_json(summary_path)
    suites = existing.get("suites", {}) if isinstance(existing.get("suites"), dict) else {}
    prior_suite = suites.get(cycle["suite_id"], {})
    prior_cycles = prior_suite.get("cycles", []) if isinstance(prior_suite, dict) else []
    cycles = [*prior_cycles, cycle]
    suites[cycle["suite_id"]] = _suite_summary_from_cycles(
        provider=provider,
        suite_id=cycle["suite_id"],
        suite_role=cycle["suite_role"],
        auth_readiness=cycle["auth_readiness"],
        cycles=cycles,
    )
    summary = {
        "generated_at": now_utc_iso(),
        "provider": provider,
        "lane": "automation",
        **live_evidence_fields(lane="automation"),
        "suite_id": cycle["suite_id"],
        "suite_role": cycle["suite_role"],
        "runs": cycle["runs"],
        "suites": suites,
    }
    write_json(summary_path, summary)
    write_json(root / f"service_runs__{cycle['suite_id']}.json", suites[cycle["suite_id"]])
    return summary


def _suite_summary_from_cycles(
    *,
    provider: str,
    suite_id: str,
    suite_role: str,
    auth_readiness: dict[str, Any],
    cycles: list[dict[str, Any]],
) -> dict[str, Any]:
    successful_cycle_count = sum(1 for cycle in cycles if cycle.get("success"))
    latest_cycle = cycles[-1]
    return {
        "provider": provider,
        "lane": "automation",
        **live_evidence_fields(lane="automation"),
        "suite_id": suite_id,
        "suite_role": suite_role,
        "auth_readiness": auth_readiness,
        "cycle_count": len(cycles),
        "successful_cycle_count": successful_cycle_count,
        "repeat_stable_success": successful_cycle_count >= 2 if suite_id == "canonical_anchor" else False,
        "latest_cycle_index": latest_cycle["cycle_index"],
        "latest_cycle_status": latest_cycle["cycle_status"],
        "latest_cycle_success": bool(latest_cycle.get("success")),
        "latest_failure_classes": latest_cycle["failure_classes"],
        "latest_warning_classes": latest_cycle["warning_classes"],
        "cycles": cycles,
    }


def _service_model_for_scenario(provider: str, scenario_id: str) -> str:
    if provider == "openai" and scenario_id == "service_smoke":
        return "gpt-5.4-mini"
    return MODEL_MATRIX[provider]["automation"].preferred


def _blocked_service_run(
    provider: str,
    *,
    auth_mode: str,
    model: str,
    root: Path,
    scenario_id: str,
    readiness: dict[str, Any],
    suite_id: str,
    suite_role: str,
    cycle_index: int,
    notes: str | None = None,
) -> dict[str, Any]:
    artifact_path = root / f"{_artifact_stem(suite_id, cycle_index, scenario_id)}.blocked.json"
    failure_class = _service_failure_class_for_readiness(str(readiness.get("status")))
    payload = {
        "provider": provider,
        "lane": "automation",
        **live_evidence_fields(lane="automation"),
        "auth_mode": auth_mode,
        "model": model,
        "scenario_id": scenario_id,
        "suite_id": suite_id,
        "suite_role": suite_role,
        "cycle_index": cycle_index,
        "success": False,
        "failure_class": failure_class,
        "warning_classes": [],
        "notes": notes
        or f"Skipped live service proof because automation auth is `{readiness['status']}`.",
        "auth_readiness": readiness,
    }
    write_json(artifact_path, payload)
    payload["artifact_path"] = _relative_repo_path(artifact_path)
    return payload


def _skipped_service_run(
    provider: str,
    *,
    auth_mode: str,
    model: str,
    scenario_id: str,
    suite_id: str,
    suite_role: str,
    cycle_index: int,
    notes: str,
) -> dict[str, Any]:
    return {
        "provider": provider,
        "lane": "automation",
        **live_evidence_fields(lane="automation"),
        "auth_mode": auth_mode,
        "model": model,
        "scenario_id": scenario_id,
        "suite_id": suite_id,
        "suite_role": suite_role,
        "cycle_index": cycle_index,
        "success": False,
        "skipped": True,
        "failure_class": None,
        "warning_classes": [],
        "notes": notes,
    }


def _run_single_live_call(
    provider: str,
    *,
    auth_mode: str,
    model: str,
    root: Path,
    suite_id: str = "current",
    suite_role: str = "readiness_probe",
    cycle_index: int = 1,
) -> dict[str, Any]:
    scenario_id = "service_smoke"
    interaction = _invoke_action_roundtrip(
        provider=provider,
        auth_mode=auth_mode,
        root=root,
        stem=_artifact_stem(suite_id, cycle_index, scenario_id),
        prompt=SMOKE_PROMPT,
        model=model,
        max_output_tokens=24,
        export_session=True,
    )
    warning_classes: list[str] = []
    effective_failure_class = interaction["failure_class"]
    if (
        interaction["status_code"] == 200
        and interaction["export_status"] == 200
        and effective_failure_class in {"capacity_exhausted", "quota_exhausted"}
    ):
        warning_classes = [effective_failure_class]
        effective_failure_class = None
    records = interaction["records"]
    return {
        "provider": provider,
        "lane": "automation",
        **live_evidence_fields(lane="automation"),
        "auth_mode": auth_mode,
        "model": model,
        "scenario_id": scenario_id,
        "suite_id": suite_id,
        "suite_role": suite_role,
        "cycle_index": cycle_index,
        "request_started_at": interaction["request_started_at"],
        "first_record_at": interaction["response_received_at"] if records else None,
        "final_record_at": interaction["response_received_at"] if records else None,
        "export_received_at": interaction["export_received_at"],
        "success": (
            interaction["status_code"] == 200
            and interaction["export_status"] == 200
            and effective_failure_class is None
            and isinstance(records, list)
        ),
        "failure_class": effective_failure_class,
        "warning_classes": warning_classes,
        "http_statuses": {
            "action_status": interaction["status_code"],
            "export_status": interaction["export_status"],
        },
        "request_path": interaction["request_path"],
        "response_path": interaction["response_path"],
        "export_path": interaction["export_path"],
        "service_log_path": interaction["service_log_path"],
        "record_count": len(records) if isinstance(records, list) else 0,
    }


def _run_continuity_capture(
    provider: str,
    *,
    auth_mode: str,
    model: str,
    root: Path,
    suite_id: str = "current",
    suite_role: str = "readiness_probe",
    cycle_index: int = 1,
) -> dict[str, Any]:
    scenario_id = "service_restart_continuity"
    exchange = _invoke_continuity_roundtrip(
        provider=provider,
        auth_mode=auth_mode,
        root=root,
        stem=_artifact_stem(suite_id, cycle_index, scenario_id),
        first_prompt="first step",
        second_prompt="second step",
        model=model,
        first_max_output_tokens=96,
        second_max_output_tokens=96,
    )
    warning_classes: list[str] = []
    effective_failure_class = exchange["failure_class"]
    if (
        exchange["import_status"] == 200
        and exchange["second_status"] == 200
        and exchange["final_export_status"] == 200
        and effective_failure_class in {"capacity_exhausted", "quota_exhausted"}
    ):
        warning_classes = [effective_failure_class]
        effective_failure_class = None
    second_records = exchange["second_records"]
    payload = {
        "provider": provider,
        "lane": "automation",
        **live_evidence_fields(lane="automation"),
        "auth_mode": auth_mode,
        "model": model,
        "scenario_id": scenario_id,
        "suite_id": suite_id,
        "suite_role": suite_role,
        "cycle_index": cycle_index,
        "success": (
            exchange["first_status"] == 200
            and exchange["export_status"] == 200
            and exchange["import_status"] == 200
            and exchange["second_status"] == 200
            and exchange["final_export_status"] == 200
            and isinstance(second_records, list)
            and effective_failure_class is None
        ),
        "failure_class": effective_failure_class,
        "warning_classes": warning_classes,
        "http_statuses": {
            "first_status": exchange["first_status"],
            "export_status": exchange["export_status"],
            "import_status": exchange["import_status"],
            "second_status": exchange["second_status"],
            "final_export_status": exchange["final_export_status"],
        },
        "request_started_at": exchange["first_request_started_at"],
        "first_record_at": exchange["first_response_received_at"] if exchange["first_records"] else None,
        "final_record_at": exchange["second_response_received_at"] if second_records else None,
        "import_received_at": exchange["import_received_at"],
        "final_export_received_at": exchange["final_export_received_at"],
        "record_count": len(exchange["first_records"]) + len(second_records),
        "first_request_path": exchange["first_request_path"],
        "second_request_path": exchange["second_request_path"],
        "first_response_path": exchange["first_response_path"],
        "first_export_path": exchange["first_export_path"],
        "import_response_path": exchange["import_response_path"],
        "second_response_path": exchange["second_response_path"],
        "final_export_path": exchange["final_export_path"],
    }
    artifact_path = root / f"{_artifact_stem(suite_id, cycle_index, scenario_id)}.json"
    write_json(artifact_path, payload)
    payload["artifact_path"] = _relative_repo_path(artifact_path)
    return payload


def _run_pass_minimal_capture(
    *,
    provider: str,
    auth_mode: str,
    model: str,
    root: Path,
    suite_id: str,
    suite_role: str,
    cycle_index: int,
) -> dict[str, Any]:
    scenario_id = "pass_minimal"
    workspace_path = prepare_harness_workspace(
        provider=provider,
        lane="automation",
        scenario_id=scenario_id,
        repeat_index=cycle_index,
    )
    interaction = _invoke_action_roundtrip(
        provider=provider,
        auth_mode=auth_mode,
        root=root,
        stem=_artifact_stem(suite_id, cycle_index, scenario_id),
        prompt=_prompt_with_workspace_context(
            read_prompt_template("pass_minimal_automation.md"),
            workspace_path,
        ),
        model=model,
        max_output_tokens=384,
        export_session=False,
    )
    return _score_patch_scenario(
        provider=provider,
        auth_mode=auth_mode,
        model=model,
        root=root,
        scenario_id=scenario_id,
        suite_id=suite_id,
        suite_role=suite_role,
        cycle_index=cycle_index,
        interaction=interaction,
        workspace_path=workspace_path,
    )


def _run_truth_gap_capture(
    *,
    provider: str,
    auth_mode: str,
    model: str,
    root: Path,
    suite_id: str,
    suite_role: str,
    cycle_index: int,
) -> dict[str, Any]:
    scenario_id = "truth_gap"
    workspace_path = prepare_harness_workspace(
        provider=provider,
        lane="automation",
        scenario_id=scenario_id,
        repeat_index=cycle_index,
    )
    interaction = _invoke_action_roundtrip(
        provider=provider,
        auth_mode=auth_mode,
        root=root,
        stem=_artifact_stem(suite_id, cycle_index, scenario_id),
        prompt=_prompt_with_workspace_context(
            read_prompt_template("truth_gap_automation.md"),
            workspace_path,
        ),
        model=model,
        max_output_tokens=160,
        export_session=False,
    )
    result_text = extract_result_text(interaction["records"], interaction.get("result_text") or "")
    result_text_path = root / f"{_artifact_stem(suite_id, cycle_index, scenario_id)}.result.txt"
    if result_text is not None:
        write_text(result_text_path, result_text)
    failure_class = _interaction_failure_class(interaction)
    truth_gap_kind = None
    success = False
    if failure_class is None and interaction["status_code"] == 200:
        truth_gap_kind = classify_truth_gap(
            result_text,
            test_passed=False,
            modified_files=[],
        )
        success = truth_gap_kind == "truthful_incomplete"
        if not success:
            failure_class = "truth_gap_smoothing"
    payload = {
        "provider": provider,
        "lane": "automation",
        **live_evidence_fields(lane="automation"),
        "auth_mode": auth_mode,
        "model": model,
        "scenario_id": scenario_id,
        "suite_id": suite_id,
        "suite_role": suite_role,
        "cycle_index": cycle_index,
        "success": success,
        "failure_class": failure_class,
        "warning_classes": [],
        "truth_gap_kind": truth_gap_kind,
        "request_started_at": interaction["request_started_at"],
        "first_record_at": interaction["response_received_at"] if interaction["records"] else None,
        "final_record_at": interaction["response_received_at"] if interaction["records"] else None,
        "http_statuses": {"action_status": interaction["status_code"]},
        "request_path": interaction["request_path"],
        "response_path": interaction["response_path"],
        "service_log_path": interaction["service_log_path"],
        "record_count": len(interaction["records"]),
        "result_text_path": _relative_repo_path(result_text_path) if result_text is not None else None,
    }
    artifact_path = root / f"{_artifact_stem(suite_id, cycle_index, scenario_id)}.json"
    write_json(artifact_path, payload)
    payload["artifact_path"] = _relative_repo_path(artifact_path)
    return payload


def _run_canonical_restart_continuity_capture(
    *,
    provider: str,
    auth_mode: str,
    model: str,
    root: Path,
    suite_id: str,
    suite_role: str,
    cycle_index: int,
) -> dict[str, Any]:
    scenario_id = "restart_continuity"
    stem = _artifact_stem(suite_id, cycle_index, scenario_id)
    workspace_path = prepare_harness_workspace(
        provider=provider,
        lane="automation",
        scenario_id=scenario_id,
        repeat_index=cycle_index,
    )
    exchange = _invoke_continuity_roundtrip(
        provider=provider,
        auth_mode=auth_mode,
        root=root,
        stem=stem,
        first_prompt=_prompt_with_workspace_context(
            read_prompt_template("restart_continuity_turn1_automation.md"),
            workspace_path,
        ),
        second_prompt=_prompt_with_workspace_context(
            read_prompt_template("restart_continuity_turn2_automation.md"),
            workspace_path,
        ),
        model=model,
        first_max_output_tokens=128,
        second_max_output_tokens=384,
    )
    plan_text = extract_result_text(exchange["first_records"], exchange.get("first_result_text") or "")
    plan_path = root / f"{stem}.plan.txt"
    if plan_text is not None:
        write_text(plan_path, plan_text)

    interaction = {
        "status_code": exchange["second_status"],
        "response_payload": exchange["second_response"],
        "records": exchange["second_records"],
        "result_text": exchange.get("second_result_text"),
        "failure_class": exchange["failure_class"],
        "request_started_at": exchange["first_request_started_at"],
        "response_received_at": exchange["second_response_received_at"],
        "request_path": exchange["second_request_path"],
        "response_path": exchange["second_response_path"],
        "service_log_path": exchange["second_service_log_path"],
    }
    payload = _score_patch_scenario(
        provider=provider,
        auth_mode=auth_mode,
        model=model,
        root=root,
        scenario_id=scenario_id,
        suite_id=suite_id,
        suite_role=suite_role,
        cycle_index=cycle_index,
        interaction=interaction,
        workspace_path=workspace_path,
    )
    if plan_text is None or not plan_text.strip():
        payload["success"] = False
        payload["failure_class"] = payload.get("failure_class") or "continuity_plan_missing"
    payload["http_statuses"] = {
        "first_status": exchange["first_status"],
        "export_status": exchange["export_status"],
        "import_status": exchange["import_status"],
        "second_status": exchange["second_status"],
        "final_export_status": exchange["final_export_status"],
    }
    payload["first_request_path"] = exchange["first_request_path"]
    payload["first_response_path"] = exchange["first_response_path"]
    payload["first_export_path"] = exchange["first_export_path"]
    payload["import_response_path"] = exchange["import_response_path"]
    payload["second_request_path"] = exchange["second_request_path"]
    payload["second_response_path"] = exchange["second_response_path"]
    payload["final_export_path"] = exchange["final_export_path"]
    payload["plan_text_path"] = _relative_repo_path(plan_path) if plan_text is not None else None
    payload["import_received_at"] = exchange["import_received_at"]
    payload["final_export_received_at"] = exchange["final_export_received_at"]
    payload["artifact_path"] = _relative_repo_path(root / f"{stem}.json")
    write_json(root / f"{stem}.json", {key: value for key, value in payload.items() if key != "artifact_path"})
    return payload


def _score_patch_scenario(
    *,
    provider: str,
    auth_mode: str,
    model: str,
    root: Path,
    scenario_id: str,
    suite_id: str,
    suite_role: str,
    cycle_index: int,
    interaction: dict[str, Any],
    workspace_path: Path | None = None,
) -> dict[str, Any]:
    stem = _artifact_stem(suite_id, cycle_index, scenario_id)
    result_text = extract_result_text(interaction["records"], interaction.get("result_text") or "")
    result_text_path = root / f"{stem}.result.txt"
    if result_text is not None:
        write_text(result_text_path, result_text)
    diff_text = extract_unified_diff(result_text or "")
    diff_path = root / f"{stem}.patch.diff"
    if diff_text is not None:
        write_text(diff_path, diff_text)
    failure_class = _interaction_failure_class(interaction)
    modified_files: list[str] = []
    apply_result: dict[str, Any] | None = None
    test_result: dict[str, Any] | None = None
    prepared_workspace = workspace_path

    if failure_class is None and interaction["status_code"] == 200:
        if diff_text is None:
            failure_class = "patch_missing"
        else:
            if prepared_workspace is None:
                prepared_workspace = prepare_harness_workspace(
                    provider=provider,
                    lane="automation",
                    scenario_id=scenario_id,
                    repeat_index=cycle_index,
                )
            apply_result = apply_unified_diff(prepared_workspace, diff_text)
            write_json(root / f"{stem}.apply.json", apply_result)
            if apply_result["exit_code"] != 0:
                failure_class = "patch_apply_failed"
            else:
                modified_files = collect_modified_files(prepared_workspace)
                if modified_files != [_PATCH_TARGET]:
                    failure_class = "scope_broadened"
                else:
                    test_result = run_target_test(prepared_workspace)
                    write_json(root / f"{stem}.test.json", test_result)
                    if test_result["exit_code"] != 0:
                        failure_class = "test_failure"

    artifact_path = root / f"{stem}.json"
    payload = {
        "provider": provider,
        "lane": "automation",
        **live_evidence_fields(lane="automation"),
        "auth_mode": auth_mode,
        "model": model,
        "scenario_id": scenario_id,
        "suite_id": suite_id,
        "suite_role": suite_role,
        "cycle_index": cycle_index,
        "success": failure_class is None,
        "failure_class": failure_class,
        "warning_classes": [],
        "modified_files": modified_files,
        "request_started_at": interaction["request_started_at"],
        "first_record_at": interaction["response_received_at"] if interaction["records"] else None,
        "final_record_at": interaction["response_received_at"] if interaction["records"] else None,
        "http_statuses": {"action_status": interaction["status_code"]},
        "request_path": interaction["request_path"],
        "response_path": interaction["response_path"],
        "service_log_path": interaction["service_log_path"],
        "record_count": len(interaction["records"]),
        "result_text_path": _relative_repo_path(result_text_path) if result_text is not None else None,
        "patch_path": _relative_repo_path(diff_path) if diff_text is not None else None,
        "apply_result_path": _relative_repo_path(root / f"{stem}.apply.json") if apply_result is not None else None,
        "test_result_path": _relative_repo_path(root / f"{stem}.test.json") if test_result is not None else None,
        "workspace_path": sanitize_path(prepared_workspace) if prepared_workspace is not None else None,
    }
    write_json(artifact_path, payload)
    payload["artifact_path"] = _relative_repo_path(artifact_path)
    return payload


def _prompt_with_workspace_context(base_prompt: str, workspace_path: Path) -> str:
    sections = [base_prompt.rstrip(), "", "Workspace context:"]
    for relative_path in _WORKSPACE_CONTEXT_FILES:
        file_path = workspace_path / relative_path
        content = file_path.read_text(encoding="utf-8").rstrip()
        sections.extend(
            [
                "",
                f"File: {relative_path}",
                "```",
                content,
                "```",
            ]
        )
    return "\n".join(sections).rstrip() + "\n"


def _invoke_action_roundtrip(
    *,
    provider: str,
    auth_mode: str,
    root: Path,
    stem: str,
    prompt: str,
    model: str,
    max_output_tokens: int,
    export_session: bool,
) -> dict[str, Any]:
    request_path = root / f"{stem}.request.json"
    response_path = root / f"{stem}.response.json"
    export_path = root / f"{stem}.export.json"
    service_log_path = root / f"{stem}.service.stderr.log"
    payload = _action_payload(provider, prompt, model=model, max_output_tokens=max_output_tokens)
    write_json(request_path, payload)

    with _running_service(provider, service_log_path, auth_mode=auth_mode) as base_url:
        status_code, response_payload, request_started_at, response_received_at = _request_json(
            "POST",
            f"{base_url}{PROVIDER_CONFIG[provider]['action_path']}",
            payload,
        )
        export_status = None
        export_payload: dict[str, Any] = {}
        export_received_at = None
        if export_session:
            export_status, export_payload, _export_started_at, export_received_at = _request_json(
                "GET",
                f"{base_url}/v1/session/export",
                None,
            )
    write_json(response_path, response_payload)
    if export_session:
        write_json(export_path, export_payload)
    serialized = json.dumps(response_payload, sort_keys=True)
    if export_session:
        serialized += json.dumps(export_payload, sort_keys=True)
    failure_class = classify_failure(serialized)
    records = response_payload.get("records")
    return {
        "status_code": status_code,
        "response_payload": response_payload,
        "records": records if isinstance(records, list) else [],
        "export_status": export_status,
        "export_payload": export_payload,
        "failure_class": failure_class,
        "result_text": response_payload.get("result_text")
        if isinstance(response_payload.get("result_text"), str)
        else None,
        "request_started_at": request_started_at,
        "response_received_at": response_received_at,
        "export_received_at": export_received_at,
        "request_path": _relative_repo_path(request_path),
        "response_path": _relative_repo_path(response_path),
        "export_path": _relative_repo_path(export_path) if export_session else None,
        "service_log_path": _relative_repo_path(service_log_path),
    }


def _invoke_continuity_roundtrip(
    *,
    provider: str,
    auth_mode: str,
    root: Path,
    stem: str,
    first_prompt: str,
    second_prompt: str,
    model: str,
    first_max_output_tokens: int,
    second_max_output_tokens: int,
) -> dict[str, Any]:
    first_request_path = root / f"{stem}.first.request.json"
    second_request_path = root / f"{stem}.second.request.json"
    first_response_path = root / f"{stem}.first.response.json"
    first_export_path = root / f"{stem}.first.export.json"
    import_response_path = root / f"{stem}.import.response.json"
    second_response_path = root / f"{stem}.second.response.json"
    final_export_path = root / f"{stem}.final.export.json"
    first_service_log_path = root / f"{stem}.first.service.stderr.log"
    second_service_log_path = root / f"{stem}.second.service.stderr.log"
    first_payload = _action_payload(provider, first_prompt, model=model, max_output_tokens=first_max_output_tokens)
    second_payload = _action_payload(provider, second_prompt, model=model, max_output_tokens=second_max_output_tokens)
    write_json(first_request_path, first_payload)
    write_json(second_request_path, second_payload)

    with _running_service(provider, first_service_log_path, auth_mode=auth_mode) as first_url:
        first_status, first_response, first_request_started_at, first_response_received_at = _request_json(
            "POST",
            f"{first_url}{PROVIDER_CONFIG[provider]['action_path']}",
            first_payload,
        )
        export_status, exported_seed, _first_export_started_at, first_export_received_at = _request_json(
            "GET",
            f"{first_url}/v1/session/export",
            None,
        )
    write_json(first_response_path, first_response)
    write_json(first_export_path, exported_seed)

    if first_status != 200 or export_status != 200:
        serialized = json.dumps(first_response, sort_keys=True) + json.dumps(exported_seed, sort_keys=True)
        return {
            "first_status": first_status,
            "export_status": export_status,
            "import_status": None,
            "second_status": None,
            "final_export_status": None,
            "failure_class": classify_failure(serialized) or "continuity_first_turn_failed",
            "first_records": first_response.get("records", []) if isinstance(first_response.get("records"), list) else [],
            "second_records": [],
            "first_response": first_response,
            "second_response": {},
            "first_request_started_at": first_request_started_at,
            "first_response_received_at": first_response_received_at,
            "second_response_received_at": None,
            "import_received_at": None,
            "final_export_received_at": None,
            "first_request_path": _relative_repo_path(first_request_path),
            "second_request_path": _relative_repo_path(second_request_path),
            "first_response_path": _relative_repo_path(first_response_path),
            "first_export_path": _relative_repo_path(first_export_path),
            "import_response_path": _relative_repo_path(import_response_path),
            "second_response_path": _relative_repo_path(second_response_path),
            "final_export_path": _relative_repo_path(final_export_path),
            "second_service_log_path": _relative_repo_path(second_service_log_path),
            "first_result_text": first_response.get("result_text")
            if isinstance(first_response.get("result_text"), str)
            else None,
            "second_result_text": None,
        }

    with _running_service(provider, second_service_log_path, auth_mode=auth_mode) as second_url:
        import_status, import_response, _import_started_at, import_received_at = _request_json(
            "POST",
            f"{second_url}/v1/session/import",
            exported_seed,
        )
        second_status, second_response, _second_request_started_at, second_response_received_at = _request_json(
            "POST",
            f"{second_url}{PROVIDER_CONFIG[provider]['action_path']}",
            second_payload,
        )
        final_export_status, final_export, _final_export_started_at, final_export_received_at = _request_json(
            "GET",
            f"{second_url}/v1/session/export",
            None,
        )
    write_json(import_response_path, import_response)
    write_json(second_response_path, second_response)
    write_json(final_export_path, final_export)
    serialized = (
        json.dumps(import_response, sort_keys=True)
        + json.dumps(second_response, sort_keys=True)
        + json.dumps(final_export, sort_keys=True)
    )
    return {
        "first_status": first_status,
        "export_status": export_status,
        "import_status": import_status,
        "second_status": second_status,
        "final_export_status": final_export_status,
        "failure_class": classify_failure(serialized),
        "first_records": first_response.get("records", []) if isinstance(first_response.get("records"), list) else [],
        "second_records": second_response.get("records", []) if isinstance(second_response.get("records"), list) else [],
        "first_response": first_response,
        "second_response": second_response,
        "first_request_started_at": first_request_started_at,
        "first_response_received_at": first_response_received_at,
        "second_response_received_at": second_response_received_at,
        "import_received_at": import_received_at,
        "final_export_received_at": final_export_received_at,
        "first_request_path": _relative_repo_path(first_request_path),
        "second_request_path": _relative_repo_path(second_request_path),
        "first_response_path": _relative_repo_path(first_response_path),
        "first_export_path": _relative_repo_path(first_export_path),
        "import_response_path": _relative_repo_path(import_response_path),
        "second_response_path": _relative_repo_path(second_response_path),
        "final_export_path": _relative_repo_path(final_export_path),
        "second_service_log_path": _relative_repo_path(second_service_log_path),
        "first_result_text": first_response.get("result_text")
        if isinstance(first_response.get("result_text"), str)
        else None,
        "second_result_text": second_response.get("result_text")
        if isinstance(second_response.get("result_text"), str)
        else None,
    }


def _interaction_failure_class(interaction: dict[str, Any]) -> str | None:
    if interaction["status_code"] != 200:
        return interaction["failure_class"] or "service_http_error"
    return interaction["failure_class"]

def _artifact_stem(suite_id: str, cycle_index: int, scenario_id: str) -> str:
    return f"{suite_id}__cycle_{cycle_index:03d}__{scenario_id}"


def _relative_repo_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return sanitize_path(path)


def sanitize_path(path: Path) -> str:
    return str(path).replace(str(REPO_ROOT), "$REPO_ROOT")


def _action_payload(provider: str, prompt: str, *, model: str, max_output_tokens: int) -> dict[str, Any]:
    return {
        "action_tag": PROVIDER_CONFIG[provider]["action_tag"],
        "request": {
            "model": model,
            "input": prompt,
            "max_output_tokens": max_output_tokens,
        },
    }


@contextmanager
def _running_service(provider: str, log_path: Path, *, auth_mode: str) -> Iterator[str]:
    port = _free_port()
    module = PROVIDER_CONFIG[provider]["module"]
    env = os.environ.copy()
    if provider == "claude":
        env["CORTEX_CLAUDE_LIVE_AUTH_MODE"] = auth_mode
    elif provider == "gemini":
        env["CORTEX_GEMINI_LIVE_AUTH_MODE"] = auth_mode
    else:
        env["CORTEX_OPENAI_LIVE_AUTH_MODE"] = auth_mode
    command = [sys.executable, "-m", module, "--port", str(port)]
    with log_path.open("w", encoding="utf-8") as log_file:
        process = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=log_file,
            cwd=str(REPO_ROOT),
            env=env,
            text=True,
        )
        try:
            base_url = f"http://127.0.0.1:{port}"
            _wait_for_health(base_url, expected_runtime=PROVIDER_CONFIG[provider]["runtime_label"])
            yield base_url
        finally:
            process.terminate()
            try:
                process.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5.0)


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        sock.listen(1)
        return int(sock.getsockname()[1])


def _wait_for_health(base_url: str, *, expected_runtime: str) -> None:
    deadline = time.time() + 10.0
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            status_code, payload, _started_at, _ended_at = _request_json("GET", f"{base_url}/health", None)
            if status_code == 200 and payload.get("runtime") == expected_runtime:
                return
        except Exception as exc:  # pragma: no cover
            last_error = exc
        time.sleep(0.1)
    raise RuntimeError(f"service at {base_url} did not become healthy: {last_error}")


def _request_json(method: str, url: str, payload: dict[str, Any] | None) -> tuple[int, dict[str, Any], str, str]:
    started_at = now_utc_iso()
    body = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=60.0) as response:
            data = response.read().decode("utf-8")
            return response.getcode(), json.loads(data), started_at, now_utc_iso()
    except urllib.error.HTTPError as exc:
        data = exc.read().decode("utf-8")
        try:
            response_payload = json.loads(data)
        except json.JSONDecodeError:
            response_payload = {"error": data or exc.reason}
        return exc.code, response_payload, started_at, now_utc_iso()


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _service_failure_class_for_readiness(status: str) -> str:
    if status == "blocked_by_spend_policy":
        return "blocked_by_spend_policy"
    if status == "mis_scoped":
        return "mis_scoped"
    return "auth_missing"


if __name__ == "__main__":
    raise SystemExit(main())
