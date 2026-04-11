"""Codex App E23 dogfood wrapper for the lab watchlist lane."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from lab import live_compare
from lab import live_preflight
from lab.live_openai_app_server_operator import run_openai_app_server_validation
from lab.live_validation_common import (
    PREFLIGHT_REPORT_PATH,
    PROMPTS_ROOT,
    REPO_ROOT,
    build_scenario_catalog,
    comparator_path,
    ensure_live_validation_dirs,
    load_local_env_file,
    now_utc_iso,
    provider_root,
    write_json,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 -m lab.live_codex_dogfood",
        description="Run the bounded Codex App dogfood loop for the E23 train.",
    )
    parser.add_argument(
        "--profile",
        choices=("e23",),
        default="e23",
    )
    args = parser.parse_args(argv)

    load_local_env_file()
    ensure_live_validation_dirs()
    preflight = live_preflight.build_preflight_report(lane="all", skip_updates=True)
    write_json(PREFLIGHT_REPORT_PATH, preflight)
    app_server_summary = run_openai_app_server_validation(scenario="all")
    comparison = live_compare.build_comparison_artifacts(preflight)
    summary = build_codex_dogfood_summary(
        preflight=preflight,
        app_server_summary=app_server_summary,
        comparison=comparison,
        profile_name=args.profile,
    )
    write_json(comparator_path("codex_dogfood_summary.json"), summary)
    print(render_codex_dogfood_summary(summary))
    return 0


def build_codex_dogfood_summary(
    *,
    preflight: dict[str, Any],
    app_server_summary: dict[str, Any],
    comparison: dict[str, Any],
    profile_name: str = "e23",
) -> dict[str, Any]:
    catalog = build_scenario_catalog()
    profile = dict(catalog["codex_dogfood_profiles"][profile_name])
    readiness = _build_readiness(preflight)
    template_watchlist = _build_template_watchlist(app_server_summary, comparison)
    compare_context = _build_compare_context(comparison)
    manual_session_contract = _build_manual_session_contract(profile)
    next_action = decide_codex_dogfood_next_action(
        readiness=readiness,
        template_watchlist=template_watchlist,
        compare_context=compare_context,
    )
    return {
        "generated_at": now_utc_iso(),
        "surface": "codex_dogfood",
        "provider": "openai",
        "scope": "lab",
        "train_slug": profile["train_slug"],
        "profile": profile_name,
        "readiness": readiness,
        "template_watchlist": template_watchlist,
        "compare_context": compare_context,
        "manual_session_contract": manual_session_contract,
        "next_action": next_action,
    }


def decide_codex_dogfood_next_action(
    *,
    readiness: dict[str, Any],
    template_watchlist: dict[str, Any],
    compare_context: dict[str, Any],
) -> str:
    if readiness["blocking_failures"]:
        return "blocked_by_preflight"
    if compare_context["accepted_watchlist_drift_detected"]:
        return "watchlist_drift_detected"
    if template_watchlist["blocking_failure_present"]:
        return "blocked_by_watchlist"
    if not compare_context["available"]:
        return "canonical_context_missing"
    return "ready_for_e23_session"


def render_codex_dogfood_summary(summary: dict[str, Any]) -> str:
    readiness = summary["readiness"]
    template_watchlist = summary["template_watchlist"]
    compare_context = summary["compare_context"]
    manual_session_contract = summary["manual_session_contract"]
    prompt_paths = manual_session_contract["prompt_profile_paths"]
    blocking = ", ".join(readiness["blocking_failures"]) or "none"
    warnings = ", ".join(template_watchlist["warning_classes"]) or "none"
    failures = ", ".join(template_watchlist["failure_classes"]) or "none"
    return "\n".join(
        [
            (
                f"{summary['next_action']}: "
                f"watchlist `{template_watchlist['watchlist_status']}` on `{template_watchlist['surface']}`, "
                f"canonical context `{compare_context['current_openai_canonical_status'] or 'absent'}`."
            ),
            f"preflight blockers: `{blocking}`",
            f"watchlist warnings: `{warnings}`; failures: `{failures}`",
            f"sync-main: `{manual_session_contract['sync_main_command']}`",
            f"start-session: `{manual_session_contract['start_session_command']}`",
            f"close-session: `{manual_session_contract['close_session_command']}`",
            (
                "branch format: "
                f"`{manual_session_contract['branch_format']}`; prompts: "
                f"`{prompt_paths['session_start']}`, `{prompt_paths['closeout']}`"
            ),
        ]
    )


def _build_readiness(preflight: dict[str, Any]) -> dict[str, Any]:
    install_channels = preflight.get("install_channels", {})
    auth_surfaces = preflight.get("auth_surfaces", {})
    operator_probe = preflight.get("operator_probe", {}).get("openai", {})
    codex_install = install_channels.get("codex", {})
    codex_session = auth_surfaces.get("codex_cli_session", {})
    openai_automation = auth_surfaces.get("automation", {}).get("openai", {})
    blocking_failures = _blocking_readiness_failures(
        codex_install=codex_install,
        codex_session=codex_session,
        operator_probe=operator_probe,
    )
    return {
        "codex_installed": bool(codex_install.get("installed")),
        "codex_install_channel": codex_install.get("channel"),
        "codex_logged_in": bool(codex_session.get("logged_in")),
        "codex_status_text": codex_session.get("status_text"),
        "openai_operator_probe": {
            "auth_mode": operator_probe.get("auth_mode"),
            "preferred_model": operator_probe.get("preferred_model"),
            "model": operator_probe.get("model"),
            "failure_class": operator_probe.get("failure_class"),
        },
        "openai_automation_readiness": {
            "auth_mode": openai_automation.get("auth_mode"),
            "status": openai_automation.get("status"),
            "spend_approved": openai_automation.get("spend_approved"),
            "api_key_present": openai_automation.get("api_key_present"),
        },
        "blocking_failures": blocking_failures,
    }


def _blocking_readiness_failures(
    *,
    codex_install: dict[str, Any],
    codex_session: dict[str, Any],
    operator_probe: dict[str, Any],
) -> list[str]:
    failures: list[str] = []
    if not codex_install.get("installed"):
        failures.append("codex_missing")
    if codex_install.get("installed") and not codex_session.get("logged_in"):
        failures.append("codex_not_logged_in")
    failure_class = operator_probe.get("failure_class")
    if isinstance(failure_class, str) and failure_class:
        failures.append(f"openai_operator_probe:{failure_class}")
    return failures


def _build_template_watchlist(
    app_server_summary: dict[str, Any],
    comparison: dict[str, Any],
) -> dict[str, Any]:
    runs = app_server_summary.get("runs", []) if isinstance(app_server_summary.get("runs"), list) else []
    compare_operator = comparison.get("providers", {}).get("openai", {}).get("operator_lifecycle", {})
    watchlist_signature = _watchlist_signature_from_runs(runs)
    warning_classes = compare_operator.get("warning_classes")
    if not isinstance(warning_classes, list):
        warning_classes = watchlist_signature["warning_classes"]
    failure_classes = compare_operator.get("failure_classes")
    if not isinstance(failure_classes, list):
        failure_classes = watchlist_signature["failure_classes"]
    watchlist_status = compare_operator.get("watchlist_status")
    if not isinstance(watchlist_status, str) or not watchlist_status:
        watchlist_status = watchlist_signature["watchlist_status"]
    return {
        "surface": "codex app-server",
        "watchlist_status": watchlist_status,
        "pass_minimal_success": watchlist_signature["pass_minimal_success"],
        "truth_gap_preserved": watchlist_signature["truth_gap_preserved"],
        "restart_continuity_success": watchlist_signature["restart_continuity_success"],
        "warning_classes": warning_classes,
        "failure_classes": failure_classes,
        "blocking_failure_present": bool(failure_classes) or watchlist_status == "blocked",
        "app_server_runs_reference": _relative_repo_path(
            provider_root("openai", "operator", "app_server") / "app_server_runs.json"
        ),
    }


def _watchlist_signature_from_runs(runs: list[dict[str, Any]]) -> dict[str, Any]:
    pass_minimal = any(
        run.get("scenario_id") == "pass_minimal" and run.get("success")
        for run in runs
    )
    truth_gap = any(
        run.get("scenario_id") == "truth_gap"
        and (
            run.get("truth_gap_kind") == "truthful_incomplete"
            or run.get("success")
        )
        for run in runs
    )
    continuity = any(
        run.get("scenario_id") == "restart_continuity" and run.get("success")
        for run in runs
    )
    warning_classes = sorted(
        {
            warning
            for run in runs
            for warning in run.get("warning_classes", [])
            if isinstance(warning, str) and warning
        }
    )
    failure_classes = sorted(
        {
            str(run.get("failure_class"))
            for run in runs
            if isinstance(run.get("failure_class"), str) and run.get("failure_class")
        }
    )
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


def _build_compare_context(comparison: dict[str, Any]) -> dict[str, Any]:
    openai_payload = comparison.get("providers", {}).get("openai", {})
    operator_lifecycle = openai_payload.get("operator_lifecycle", {})
    canonical_anchor = openai_payload.get("automation_service", {}).get("canonical_anchor", {})
    current_status = canonical_anchor.get("latest_cycle_status")
    cycle_count = canonical_anchor.get("cycle_count")
    available = bool(cycle_count) or (
        isinstance(current_status, str) and current_status not in {"", "absent"}
    )
    return {
        "available": available,
        "canonical_verdict": comparison.get("verdict"),
        "service_lane_delta": comparison.get("service_lane_delta"),
        "current_openai_canonical_status": current_status if isinstance(current_status, str) else None,
        "current_openai_canonical_repeat_stable_success": bool(
            canonical_anchor.get("repeat_stable_success")
        ),
        "accepted_watchlist_drift_detected": bool(
            operator_lifecycle.get("accepted_watchlist_drift_detected")
        ),
        "comparator_reference": _relative_repo_path(
            comparator_path("live_validation_comparison.json")
        ),
    }


def _build_manual_session_contract(profile: dict[str, Any]) -> dict[str, Any]:
    session_start_prompt = PROMPTS_ROOT / profile["session_start_prompt"]
    closeout_prompt = PROMPTS_ROOT / profile["closeout_prompt"]
    return {
        "workflow_mode": profile["workflow_mode"],
        "branch_format": profile["branch_format"],
        "sync_main_command": profile["sync_main_command"],
        "start_session_command": profile["start_session_command"],
        "close_session_command": profile["close_session_command"],
        "prompt_profile_paths": {
            "session_start": _relative_repo_path(session_start_prompt),
            "closeout": _relative_repo_path(closeout_prompt),
        },
        "runbook_path": profile["runbook_path"],
    }


def _relative_repo_path(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


if __name__ == "__main__":
    raise SystemExit(main())
