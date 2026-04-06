"""Comparator and verdict builder for the L2 live testing environment."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from live_validation_common import (
    PREFLIGHT_REPORT_PATH,
    canonical_service_provider_scope,
    comparator_path,
    decide_verdict,
    ensure_live_validation_dirs,
    live_evidence_fields,
    now_utc_iso,
    provider_root,
    WORKSTREAM_PATH,
    write_json,
    write_text,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 tools/live_compare.py",
        description="Build the L2 comparison summary and verdict from local artifacts.",
    )
    parser.parse_args(argv)

    ensure_live_validation_dirs()
    preflight = _read_json(PREFLIGHT_REPORT_PATH)
    comparison = _build_comparison(preflight)
    write_json(comparator_path("live_validation_comparison.json"), comparison)
    write_text(comparator_path("live_validation_comparison.md"), _comparison_markdown(comparison))
    print(json.dumps(comparison, indent=2, sort_keys=True))
    return 0


def _build_comparison(preflight: dict[str, Any]) -> dict[str, Any]:
    accepted_watchlist = _accepted_watchlist_fallbacks()
    canonical_scope = set(canonical_service_provider_scope())
    providers: dict[str, Any] = {}
    blocker_classes: set[str] = set()
    operator_pass_count = 0
    operator_truthful_gap_count = 0
    automation_pass_count = 0
    service_success_count = 0
    watchlist_drift_hosts: list[str] = []

    for provider in ("claude", "gemini", "openai"):
        baseline_runs = _read_json(
            provider_root(provider, "operator", "baselines") / "provider_baseline_runs.json"
        ).get("runs", [])
        operator_runs = _read_operator_lifecycle_runs(provider)
        exploratory_baseline_runs = _read_exploratory_baseline_runs(provider)
        exploratory_operator_runs = _read_exploratory_operator_runs(provider)
        service_summary = _read_service_summary(provider)
        accepted_watchlist_payload = accepted_watchlist.get(provider)
        operator_runs, operator_source = _effective_operator_runs(
            provider=provider,
            operator_runs=operator_runs,
            accepted_watchlist_payload=accepted_watchlist_payload,
        )

        successful_operator = [run for run in operator_runs if run.get("success")]
        truthful_gaps = [
            run
            for run in operator_runs
            if run.get("scenario_id") == "truth_gap" and run.get("truth_gap_kind") == "truthful_incomplete"
        ]
        continuity_success = _continuity_success(provider=provider, operator_runs=operator_runs)
        operator_warning_classes = sorted(
            {
                warning
                for run in operator_runs
                for warning in run.get("warning_classes", [])
                if isinstance(warning, str) and warning
            }
        )
        chosen_models = sorted(
            {
                run["model"]
                for run in operator_runs
                if isinstance(run.get("model"), str) and run.get("model")
            }
        )
        preferred_models = sorted(
            {
                run["preferred_model"]
                for run in operator_runs
                if isinstance(run.get("preferred_model"), str) and run.get("preferred_model")
            }
        )
        hook_event_labels = sorted(
            {
                label
                for run in operator_runs
                for label in run.get("hook_event_labels", [])
                if isinstance(label, str) and label
            }
        )
        baseline_failures = sorted(
            {run["failure_class"] for run in baseline_runs if run.get("failure_class")}
        )
        operator_failures = sorted(
            {run["failure_class"] for run in operator_runs if run.get("failure_class")}
        )
        service_failures = service_summary["failure_classes"]
        in_canonical_scope = provider in canonical_scope

        if in_canonical_scope:
            blocker_classes.update(service_failures)
        if (
            in_canonical_scope
            and preflight.get("auth_surfaces", {}).get("automation", {}).get(provider, {}).get("status")
            == "ready"
        ):
            automation_pass_count += 1
        if any(run.get("scenario_id") == "pass_minimal" and run.get("success") for run in operator_runs):
            operator_pass_count += 1
        if truthful_gaps:
            operator_truthful_gap_count += 1
        if in_canonical_scope and service_summary["canonical_anchor"]["repeat_stable_success"]:
            service_success_count += 1

        current_watchlist_signature = _watchlist_signature_from_runs(provider, operator_runs)
        current_watchlist_status = current_watchlist_signature["watchlist_status"]
        accepted_watchlist_status = (
            _watchlist_status_from_runs(provider, accepted_watchlist_payload["synthetic_runs"])
            if accepted_watchlist_payload is not None
            else None
        )
        accepted_watchlist_signature = (
            _watchlist_signature_from_runs(provider, accepted_watchlist_payload["synthetic_runs"])
            if accepted_watchlist_payload is not None
            else None
        )
        accepted_watchlist_drift_detected = (
            accepted_watchlist_signature is not None
            and operator_source == "local_artifacts"
            and current_watchlist_signature != accepted_watchlist_signature
        )
        if accepted_watchlist_drift_detected:
            watchlist_drift_hosts.append(provider)

        providers[provider] = {
            "operator_baseline": {
                **live_evidence_fields(lane="operator"),
                "failure_classes": baseline_failures,
                "successful_run_count": len([run for run in baseline_runs if run.get("success")]),
            },
            "operator_lifecycle": {
                **live_evidence_fields(lane="operator"),
                "successful_run_count": len(successful_operator),
                "pass_minimal_success": any(
                    run.get("scenario_id") == "pass_minimal" and run.get("success")
                    for run in operator_runs
                ),
                "restart_continuity_success": continuity_success,
                "truth_gap_preserved": bool(truthful_gaps),
                "failure_classes": operator_failures,
                "warning_classes": operator_warning_classes,
                "preferred_models": preferred_models,
                "chosen_models": chosen_models,
                "hook_event_labels": hook_event_labels,
                "source": operator_source,
                "watchlist_status": current_watchlist_status,
                "accepted_watchlist_status": accepted_watchlist_status,
                "accepted_watchlist_source": (
                    accepted_watchlist_payload["source"]
                    if accepted_watchlist_payload is not None
                    else None
                ),
                "accepted_watchlist_signature": accepted_watchlist_signature,
                "accepted_watchlist_drift_detected": accepted_watchlist_drift_detected,
            },
            "automation_service": {
                **live_evidence_fields(lane="automation"),
                "in_canonical_scope": in_canonical_scope,
                "current": service_summary["current"],
                "canonical_anchor": service_summary["canonical_anchor"],
                "successful_run_count": service_summary["canonical_anchor"]["successful_cycle_count"],
                "failure_classes": service_failures,
            },
            "operator_probe": preflight.get("operator_probe", {}).get(provider, {}),
            "automation_auth": preflight.get("auth_surfaces", {}).get("automation", {}).get(provider, {}),
        }
        if provider == "openai":
            providers[provider]["operator_lifecycle"]["surface"] = "codex app-server"
        else:
            providers[provider]["operator_lifecycle"]["surface"] = "host-native CLI task lane"
        if provider == "gemini":
            providers[provider]["operator_lifecycle"]["warning_preserving"] = bool(operator_warning_classes)
            providers[provider]["operator_lifecycle"]["scenario_split"] = len(chosen_models) > 1
            providers[provider]["exploratory_probe"] = _build_exploratory_probe_summary(
                exploratory_baseline_runs,
                exploratory_operator_runs,
            )
            providers[provider]["operator_lifecycle"]["explicit_partial"] = True
        else:
            providers[provider]["operator_lifecycle"]["explicit_partial"] = False

    verdict, verdict_reason = decide_verdict(
        operator_pass_count=operator_pass_count,
        operator_truthful_gap_count=operator_truthful_gap_count,
        automation_pass_count=automation_pass_count,
        service_success_count=service_success_count,
        blocker_classes=blocker_classes,
    )
    return {
        "generated_at": now_utc_iso(),
        "operator_evidence": live_evidence_fields(lane="operator"),
        "automation_evidence": live_evidence_fields(lane="automation"),
        "canonical_provider_scope": sorted(canonical_scope),
        "operator_pass_count": operator_pass_count,
        "operator_truthful_gap_count": operator_truthful_gap_count,
        "automation_pass_count": automation_pass_count,
        "service_success_count": service_success_count,
        "providers": providers,
        "watchlist_drift_hosts": watchlist_drift_hosts,
        "verdict": verdict,
        "verdict_reason": verdict_reason,
        "service_lane_delta": _service_lane_delta(providers, canonical_scope=canonical_scope),
        "next_corrective_seam": _next_corrective_seam(providers, canonical_scope=canonical_scope),
    }


def _next_corrective_seam(
    providers: dict[str, Any],
    *,
    canonical_scope: set[str] | frozenset[str] | None = None,
) -> str:
    scoped_providers = canonical_scope if canonical_scope is not None else set(providers)
    ready_hosts = [
        provider
        for provider, payload in providers.items()
        if provider in scoped_providers and payload.get("automation_auth", {}).get("status") == "ready"
    ]
    canonical_hosts = [
        provider
        for provider, payload in providers.items()
        if provider in scoped_providers
        and payload.get("automation_service", {}).get("canonical_anchor", {}).get("repeat_stable_success")
    ]
    blocked_statuses = {
        provider: payload.get("automation_auth", {}).get("status")
        for provider, payload in providers.items()
        if provider in scoped_providers
        and payload.get("automation_auth", {}).get("status") not in {None, "ready"}
    }
    watchlist_drift_hosts = [
        provider
        for provider, payload in providers.items()
        if provider in scoped_providers
        if payload.get("operator_lifecycle", {}).get("accepted_watchlist_drift_detected")
    ]

    if not canonical_hosts and blocked_statuses and not ready_hosts:
        return (
            "treat the current machine as out of scope for actual service proof, move the repo to a capable machine with machine auth and spend approval, and rerun the bounded service-proof train there"
        )
    if not canonical_hosts and ready_hosts:
        return (
            "rerun the bounded direct-API confirmation suite only on the currently ready hosts until canonical truth either re-earns cleanly or blocks truthfully"
        )
    if watchlist_drift_hosts:
        return (
            "treat the headless-CLI lane as watchlist drift detection only, keep canonical claims on the direct-API lane, and investigate local-vs-accepted watchlist differences without promoting them into runtime truth"
        )
    if blocked_statuses:
        return (
            "keep blocked providers watchlist-only until direct auth exists, and do not let CLI evidence promote or overturn canonical runtime truth"
        )
    return (
        "current product scope is already re-earned on the canonical direct-API lane; keep out-of-scope hosts on watchlist or future host-expansion seams, and open the bounded OpenAI-only support/eval compression train next"
    )


def _comparison_markdown(comparison: dict[str, Any]) -> str:
    lines = [
        "# L2 Live Testing Comparison",
        "",
        f"- Generated at: `{comparison['generated_at']}`",
        f"- Canonical direct-API scope: `{', '.join(comparison['canonical_provider_scope']) or 'none'}`",
        f"- Watchlist pass_minimal host count: `{comparison['operator_pass_count']}`",
        f"- Watchlist truthful-gap host count: `{comparison['operator_truthful_gap_count']}`",
        f"- Canonical direct-API re-earned host count: `{comparison['service_success_count']}`",
        f"- Verdict: **{comparison['verdict']}**",
        "",
        comparison["verdict_reason"],
        "",
        "## Provider summary",
        "",
    ]
    for provider, payload in comparison["providers"].items():
        lines.extend(
            [
                f"### {provider}",
                "",
                f"- headless-CLI watchlist surface: `{payload['operator_lifecycle']['surface']}`",
                f"- headless-CLI watchlist status: `{payload['operator_lifecycle']['watchlist_status']}`",
                f"- headless-CLI watchlist source: `{payload['operator_lifecycle']['source']}`",
                f"- accepted watchlist status: `{payload['operator_lifecycle'].get('accepted_watchlist_status') or 'none'}`",
                f"- accepted watchlist drift detected: `{payload['operator_lifecycle'].get('accepted_watchlist_drift_detected', False)}`",
                f"- watchlist pass_minimal success: `{payload['operator_lifecycle']['pass_minimal_success']}`",
                f"- watchlist restart_continuity success: `{payload['operator_lifecycle']['restart_continuity_success']}`",
                f"- watchlist truthful gap preserved: `{payload['operator_lifecycle']['truth_gap_preserved']}`",
                f"- watchlist chosen models: `{', '.join(payload['operator_lifecycle']['chosen_models']) or 'none'}`",
                f"- watchlist warning classes: `{', '.join(payload['operator_lifecycle']['warning_classes']) or 'none'}`",
                f"- watchlist hook labels: `{', '.join(payload['operator_lifecycle']['hook_event_labels']) or 'none'}`",
                f"- watchlist lifecycle failures: `{', '.join(payload['operator_lifecycle']['failure_classes']) or 'none'}`",
                f"- direct-API readiness status: `{payload['automation_service']['current']['latest_cycle_status']}`",
                f"- direct-API canonical scope: `{payload['automation_service']['in_canonical_scope']}`",
                f"- direct-API canonical status: `{payload['automation_service']['canonical_anchor']['latest_cycle_status']}`",
                f"- direct-API canonical repeat-stable: `{payload['automation_service']['canonical_anchor']['repeat_stable_success']}`",
                f"- direct-API canonical failures: `{', '.join(payload['automation_service']['failure_classes']) or 'none'}`",
                "",
            ]
        )
        if provider == "gemini":
            exploratory = payload.get("exploratory_probe", {})
            lines.extend(
                [
                    f"- exploratory pro smoke success: `{exploratory.get('smoke_success', False)}`",
                    f"- exploratory pro truth_gap preserved: `{exploratory.get('truth_gap_preserved', False)}`",
                    f"- exploratory pro chosen models: `{', '.join(exploratory.get('chosen_models', [])) or 'none'}`",
                    f"- exploratory pro failures: `{', '.join(exploratory.get('failure_classes', [])) or 'none'}`",
                    "",
                ]
            )
    lines.extend(
        [
            "## Next corrective seam",
            "",
            comparison["next_corrective_seam"],
            "",
            "## Lane relationship",
            "",
            comparison["service_lane_delta"],
            "",
        ]
    )
    return "\n".join(lines)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _effective_operator_runs(
    *,
    provider: str,
    operator_runs: list[dict[str, Any]],
    accepted_watchlist_payload: dict[str, Any] | None,
) -> tuple[list[dict[str, Any]], str]:
    filtered_runs = [
        run for run in operator_runs if run.get("scenario_id") != "operator_product_gate"
    ]
    if accepted_watchlist_payload is None:
        return filtered_runs, "local_artifacts"
    if not filtered_runs:
        return list(accepted_watchlist_payload["synthetic_runs"]), accepted_watchlist_payload["source"]
    return filtered_runs, "local_artifacts"


def _continuity_success(*, provider: str, operator_runs: list[dict[str, Any]]) -> bool:
    continuity_runs = [
        run for run in operator_runs if run.get("scenario_id") == "restart_continuity"
    ]
    if provider != "gemini":
        return any(run.get("success") for run in continuity_runs)

    local_continuity_runs = [
        run for run in continuity_runs
        if str(run.get("artifact_path", "")).startswith(".cortex/live_validation/operator/gemini/product_paths/")
    ]
    if len(local_continuity_runs) >= 2:
        ordered = sorted(
            local_continuity_runs,
            key=lambda run: int(run.get("repeat_index", 0)),
        )
        latest_two = ordered[-2:]
        return all(run.get("success") for run in latest_two)
    return any(run.get("success") for run in continuity_runs)


def _accepted_watchlist_fallbacks() -> dict[str, dict[str, Any]]:
    text = WORKSTREAM_PATH.read_text(encoding="utf-8")
    claude_positive = (
        "the Claude operator lane is now hook-backed and completes:" in text
        or "Claude: positive watchlist signal" in text
    )
    gemini_truthful_gap = (
        "`truth_gap` is truthful on the latest reruns on `auto`" in text
        or "Gemini: unresolved watchlist signal" in text
    )
    openai_positive = (
        "the OpenAI App Server operator lane now completes:" in text
        or "OpenAI: positive watchlist signal" in text
    )
    return {
        "claude": {
            "source": "accepted_watchlist_fallback",
            "synthetic_runs": [
                {
                    "scenario_id": "pass_minimal",
                    "success": claude_positive,
                    "truth_gap_kind": None,
                    "failure_class": None,
                    "warning_classes": [],
                    **live_evidence_fields(lane="operator"),
                    "model": "claude-sonnet-4-6",
                    "preferred_model": "claude-sonnet-4-6",
                    "hook_event_labels": ["SessionStart", "PreToolUse", "PostToolUse", "Stop", "SessionEnd"],
                },
                {
                    "scenario_id": "truth_gap",
                    "success": False,
                    "truth_gap_kind": "truthful_incomplete" if ("    - `truth_gap` truthfully" in text or claude_positive) else None,
                    "failure_class": None,
                    "warning_classes": [],
                    **live_evidence_fields(lane="operator"),
                    "model": "claude-sonnet-4-6",
                    "preferred_model": "claude-sonnet-4-6",
                    "hook_event_labels": ["SessionStart", "PreToolUse", "PostToolUse", "Stop", "SessionEnd"],
                },
                {
                    "scenario_id": "restart_continuity",
                    "success": claude_positive,
                    "truth_gap_kind": None,
                    "failure_class": None,
                    "warning_classes": [],
                    **live_evidence_fields(lane="operator"),
                    "model": "claude-sonnet-4-6",
                    "preferred_model": "claude-sonnet-4-6",
                    "hook_event_labels": ["SessionStart", "PreToolUse", "PostToolUse", "Stop", "SessionEnd"],
                },
            ],
        },
        "gemini": {
            "source": "accepted_watchlist_fallback",
            "synthetic_runs": [
                {
                    "scenario_id": "pass_minimal",
                    "success": "`pass_minimal` succeeds twice on `auto` with explicit `capacity_exhausted` warnings" in text,
                    "truth_gap_kind": None,
                    "failure_class": None,
                    "warning_classes": ["capacity_exhausted"],
                    **live_evidence_fields(lane="operator"),
                    "model": "auto",
                    "preferred_model": "auto",
                    "hook_event_labels": ["SessionStart", "BeforeTool", "AfterTool", "SessionEnd"],
                },
                {
                    "scenario_id": "truth_gap",
                    "success": False,
                    "truth_gap_kind": "truthful_incomplete" if gemini_truthful_gap else None,
                    "failure_class": None,
                    "warning_classes": [],
                    **live_evidence_fields(lane="operator"),
                    "model": "auto",
                    "preferred_model": "auto",
                    "hook_event_labels": ["SessionStart", "BeforeTool", "AfterTool", "SessionEnd"],
                },
                {
                    "scenario_id": "restart_continuity",
                    "success": False,
                    "truth_gap_kind": None,
                    "failure_class": "capacity_exhausted",
                    "warning_classes": ["capacity_exhausted"],
                    **live_evidence_fields(lane="operator"),
                    "model": "auto",
                    "preferred_model": "auto",
                    "hook_event_labels": ["SessionStart", "BeforeTool", "AfterTool", "SessionEnd"],
                },
            ],
        },
        "openai": {
            "source": "accepted_watchlist_fallback",
            "synthetic_runs": [
                {
                    "scenario_id": "pass_minimal",
                    "success": openai_positive,
                    "truth_gap_kind": None,
                    "failure_class": None,
                    "warning_classes": [],
                    **live_evidence_fields(lane="operator"),
                    "model": "gpt-5.3-codex",
                    "preferred_model": "gpt-5.3-codex",
                    "hook_event_labels": [],
                },
                {
                    "scenario_id": "truth_gap",
                    "success": False,
                    "truth_gap_kind": "truthful_incomplete" if ("    - `truth_gap` truthfully" in text or openai_positive) else None,
                    "failure_class": None,
                    "warning_classes": [],
                    **live_evidence_fields(lane="operator"),
                    "model": "gpt-5.3-codex",
                    "preferred_model": "gpt-5.3-codex",
                    "hook_event_labels": [],
                },
                {
                    "scenario_id": "restart_continuity",
                    "success": openai_positive,
                    "truth_gap_kind": None,
                    "failure_class": None,
                    "warning_classes": [],
                    **live_evidence_fields(lane="operator"),
                    "model": "gpt-5.3-codex",
                    "preferred_model": "gpt-5.3-codex",
                    "hook_event_labels": [],
                },
            ],
        },
    }


def _watchlist_status_from_runs(provider: str, runs: list[dict[str, Any]]) -> str:
    return _watchlist_signature_from_runs(provider, runs)["watchlist_status"]


def _watchlist_signature_from_runs(provider: str, runs: list[dict[str, Any]]) -> dict[str, Any]:
    return _watchlist_signature(
        pass_minimal=any(
            run.get("scenario_id") == "pass_minimal" and run.get("success")
            for run in runs
        ),
        truth_gap=any(
            run.get("scenario_id") == "truth_gap"
            and run.get("truth_gap_kind") == "truthful_incomplete"
            for run in runs
        ),
        continuity=_continuity_success(provider=provider, operator_runs=runs),
        warning_classes=sorted(
            {
                warning
                for run in runs
                for warning in run.get("warning_classes", [])
                if isinstance(warning, str) and warning
            }
        ),
        failure_classes=sorted(
            {
                str(run.get("failure_class"))
                for run in runs
                if isinstance(run.get("failure_class"), str) and run.get("failure_class")
            }
        ),
    )


def _watchlist_signature(
    *,
    pass_minimal: bool,
    truth_gap: bool,
    continuity: bool,
    warning_classes: list[str],
    failure_classes: list[str],
) -> dict[str, Any]:
    watchlist_status = "blocked"
    if pass_minimal and truth_gap and continuity and not warning_classes and not failure_classes:
        watchlist_status = "positive"
    elif pass_minimal or truth_gap or continuity or warning_classes or failure_classes:
        watchlist_status = "unresolved"
    return {
        "watchlist_status": watchlist_status,
        "pass_minimal_success": pass_minimal,
        "truth_gap_preserved": truth_gap,
        "restart_continuity_success": continuity,
        "warning_classes": warning_classes,
        "failure_classes": failure_classes,
    }


def _read_operator_lifecycle_runs(provider: str) -> list[dict[str, Any]]:
    if provider == "openai":
        return _read_json(provider_root(provider, "operator", "app_server") / "app_server_runs.json").get("runs", [])
    return _read_json(
        provider_root(provider, "operator", "product_paths") / "host_native_product_runs.json"
    ).get("runs", [])


def _read_exploratory_baseline_runs(provider: str) -> list[dict[str, Any]]:
    return _read_json(
        provider_root(provider, "operator", "baselines_exploratory") / "provider_baseline_runs.json"
    ).get("runs", [])


def _read_exploratory_operator_runs(provider: str) -> list[dict[str, Any]]:
    return _read_json(
        provider_root(provider, "operator", "product_paths_exploratory") / "host_native_product_runs.json"
    ).get("runs", [])


def _read_service_summary(provider: str) -> dict[str, Any]:
    payload = _read_json(provider_root(provider, "automation", "service") / "service_runs.json")
    suites = payload.get("suites", {}) if isinstance(payload.get("suites"), dict) else {}
    if not suites and isinstance(payload.get("runs"), list):
        suites = {
            "current": {
                "suite_id": "current",
                "suite_role": "readiness_probe",
                "cycle_count": 1,
                "successful_cycle_count": int(bool(payload.get("runs")) and all(run.get("success") for run in payload["runs"])),
                "latest_cycle_status": "positive"
                if payload.get("runs") and all(run.get("success") for run in payload["runs"])
                else "partial",
                "latest_cycle_success": bool(payload.get("runs")) and all(run.get("success") for run in payload["runs"]),
                "latest_failure_classes": sorted(
                    {
                        str(run.get("failure_class"))
                        for run in payload["runs"]
                        if isinstance(run.get("failure_class"), str) and run.get("failure_class")
                    }
                ),
                "latest_warning_classes": sorted(
                    {
                        warning
                        for run in payload["runs"]
                        for warning in run.get("warning_classes", [])
                        if isinstance(warning, str) and warning
                    }
                ),
                "cycles": [
                    {
                        "cycle_index": 1,
                        "success": bool(payload.get("runs")) and all(run.get("success") for run in payload["runs"]),
                        "cycle_status": "positive"
                        if payload.get("runs") and all(run.get("success") for run in payload["runs"])
                        else "partial",
                        "runs": payload["runs"],
                    }
                ],
            }
        }
    current = _normalize_service_suite(
        suites.get("current"),
        suite_id="current",
        suite_role="readiness_probe",
    )
    canonical_anchor = _normalize_service_suite(
        suites.get("canonical_anchor"),
        suite_id="canonical_anchor",
        suite_role="canonical_truth_anchor",
    )
    return {
        "current": current,
        "canonical_anchor": canonical_anchor,
        "failure_classes": sorted(
            {
                *current["failure_classes"],
                *canonical_anchor["failure_classes"],
            }
        ),
    }


def _normalize_service_suite(
    payload: dict[str, Any] | None,
    *,
    suite_id: str,
    suite_role: str,
) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return _empty_service_suite(suite_id=suite_id, suite_role=suite_role)
    cycles = payload.get("cycles", []) if isinstance(payload.get("cycles"), list) else []
    latest_cycle = cycles[-1] if cycles else {}
    latest_runs = latest_cycle.get("runs", []) if isinstance(latest_cycle.get("runs"), list) else []
    failure_classes = payload.get("latest_failure_classes")
    if not isinstance(failure_classes, list):
        failure_classes = sorted(
            {
                str(run.get("failure_class"))
                for run in latest_runs
                if isinstance(run.get("failure_class"), str) and run.get("failure_class")
            }
        )
    warning_classes = payload.get("latest_warning_classes")
    if not isinstance(warning_classes, list):
        warning_classes = sorted(
            {
                warning
                for run in latest_runs
                for warning in run.get("warning_classes", [])
                if isinstance(warning, str) and warning
            }
        )
    successful_cycle_count = payload.get("successful_cycle_count")
    if not isinstance(successful_cycle_count, int):
        successful_cycle_count = sum(1 for cycle in cycles if cycle.get("success"))
    cycle_count = payload.get("cycle_count")
    if not isinstance(cycle_count, int):
        cycle_count = len(cycles)
    latest_cycle_status = payload.get("latest_cycle_status")
    if not isinstance(latest_cycle_status, str):
        latest_cycle_status = str(latest_cycle.get("cycle_status", "absent"))
    latest_cycle_success = payload.get("latest_cycle_success")
    if not isinstance(latest_cycle_success, bool):
        latest_cycle_success = bool(latest_cycle.get("success"))
    return {
        "suite_id": suite_id,
        "suite_role": suite_role,
        "cycle_count": cycle_count,
        "successful_cycle_count": successful_cycle_count,
        "repeat_stable_success": bool(payload.get("repeat_stable_success"))
        or (suite_id == "canonical_anchor" and successful_cycle_count >= 2),
        "latest_cycle_status": latest_cycle_status,
        "latest_cycle_success": latest_cycle_success,
        "failure_classes": failure_classes,
        "warning_classes": warning_classes,
    }


def _empty_service_suite(*, suite_id: str, suite_role: str) -> dict[str, Any]:
    return {
        "suite_id": suite_id,
        "suite_role": suite_role,
        "cycle_count": 0,
        "successful_cycle_count": 0,
        "repeat_stable_success": False,
        "latest_cycle_status": "absent",
        "latest_cycle_success": False,
        "failure_classes": [],
        "warning_classes": [],
    }


def _build_exploratory_probe_summary(
    baseline_runs: list[dict[str, Any]],
    operator_runs: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "smoke_success": any(run.get("success") for run in baseline_runs),
        "truth_gap_preserved": any(
            run.get("scenario_id") == "truth_gap" and run.get("truth_gap_kind") == "truthful_incomplete"
            for run in operator_runs
        ),
        "chosen_models": sorted(
            {
                run["model"]
                for run in baseline_runs + operator_runs
                if isinstance(run.get("model"), str) and run.get("model")
            }
        ),
        "failure_classes": sorted(
            {
                run["failure_class"]
                for run in baseline_runs + operator_runs
                if run.get("failure_class")
            }
        ),
    }


def _service_lane_delta(
    providers: dict[str, Any],
    *,
    canonical_scope: set[str] | frozenset[str] | None = None,
) -> str:
    scoped_providers = canonical_scope if canonical_scope is not None else set(providers)
    ready_in_scope = []
    blocked_in_scope = []
    probe_clean_in_scope = []
    canonical_success = []
    canonical_partial = []
    watchlist = []
    drift = []
    for provider, payload in providers.items():
        automation_auth = payload.get("automation_auth", {})
        automation_service = payload.get("automation_service", {})
        readiness_suite = automation_service.get("current", {})
        canonical_suite = automation_service.get("canonical_anchor", {})
        operator_lifecycle = payload.get("operator_lifecycle", {})
        if provider in scoped_providers:
            if readiness_suite.get("latest_cycle_success"):
                probe_clean_in_scope.append(provider)
            if canonical_suite.get("repeat_stable_success"):
                canonical_success.append(provider)
            elif canonical_suite.get("cycle_count", 0) > 0:
                canonical_partial.append(provider)
            status = automation_auth.get("status")
            if status == "ready":
                ready_in_scope.append(provider)
            elif status:
                blocked_in_scope.append(f"{provider}:{status}")
            else:
                blocked_in_scope.append(f"{provider}:unknown")
        watchlist_status = operator_lifecycle.get("watchlist_status", "unknown")
        accepted_status = operator_lifecycle.get("accepted_watchlist_status")
        if operator_lifecycle.get("accepted_watchlist_drift_detected"):
            drift.append(provider)
            watchlist.append(f"{provider}:{watchlist_status}->accepted:{accepted_status}")
        else:
            watchlist.append(f"{provider}:{watchlist_status}")
    if canonical_success:
        canonical_clause = (
            f"direct_api canonical truth is re-earned for current scope on `{', '.join(canonical_success)}`"
        )
    elif canonical_partial:
        canonical_clause = (
            f"direct_api canonical truth is still partial on `{', '.join(canonical_partial)}`"
        )
    elif probe_clean_in_scope:
        canonical_clause = (
            f"direct_api readiness is clean in current scope on `{', '.join(probe_clean_in_scope)}`, but the canonical anchor is not yet re-earned"
        )
    else:
        canonical_clause = "direct_api canonical truth is not yet re-earned in current scope on this machine"
    drift_clause = (
        f"; drift against the accepted watchlist is explicit on `{', '.join(drift)}`"
        if drift
        else ""
    )
    out_of_scope = sorted(provider for provider in providers if provider not in scoped_providers)
    out_of_scope_clause = (
        f"; out-of-scope direct_api providers remain watchlist-only for runtime truth: `{', '.join(out_of_scope)}`"
        if out_of_scope
        else ""
    )
    return (
        f"{canonical_clause}; "
        f"current-scope automation auth readiness is `{', '.join(ready_in_scope) or 'none'}` ready and `{', '.join(blocked_in_scope) or 'none'}` unavailable; "
        f"headless_cli watchlist currently reads `{', '.join(watchlist) or 'none'}`{drift_clause}{out_of_scope_clause}."
    )


if __name__ == "__main__":
    raise SystemExit(main())
