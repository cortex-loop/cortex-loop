"""Comparator and verdict builder for the L2 live testing environment."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from live_validation_common import (
    PREFLIGHT_REPORT_PATH,
    comparator_path,
    decide_verdict,
    ensure_live_validation_dirs,
    now_utc_iso,
    provider_root,
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
    providers: dict[str, Any] = {}
    blocker_classes: set[str] = set()
    operator_pass_count = 0
    operator_truthful_gap_count = 0
    automation_pass_count = 0
    service_success_count = 0

    for provider in ("claude", "gemini", "openai"):
        baseline_runs = _read_json(
            provider_root(provider, "operator", "baselines") / "provider_baseline_runs.json"
        ).get("runs", [])
        operator_runs = _read_operator_lifecycle_runs(provider)
        exploratory_baseline_runs = _read_exploratory_baseline_runs(provider)
        exploratory_operator_runs = _read_exploratory_operator_runs(provider)
        service_runs = _read_json(
            provider_root(provider, "automation", "service") / "service_runs.json"
        ).get("runs", [])

        successful_operator = [run for run in operator_runs if run.get("success")]
        truthful_gaps = [
            run
            for run in operator_runs
            if run.get("scenario_id") == "truth_gap" and run.get("truth_gap_kind") == "truthful_incomplete"
        ]
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
        successful_service = [run for run in service_runs if run.get("success")]
        baseline_failures = sorted(
            {run["failure_class"] for run in baseline_runs if run.get("failure_class")}
        )
        operator_failures = sorted(
            {run["failure_class"] for run in operator_runs if run.get("failure_class")}
        )
        service_failures = sorted(
            {run["failure_class"] for run in service_runs if run.get("failure_class")}
        )

        blocker_classes.update(baseline_failures)
        blocker_classes.update(operator_failures)
        blocker_classes.update(service_failures)
        if any(run.get("scenario_id") == "pass_minimal" and run.get("success") for run in operator_runs):
            operator_pass_count += 1
        if truthful_gaps:
            operator_truthful_gap_count += 1
        if successful_service:
            service_success_count += 1

        providers[provider] = {
            "operator_baseline": {
                "failure_classes": baseline_failures,
                "successful_run_count": len([run for run in baseline_runs if run.get("success")]),
            },
            "operator_lifecycle": {
                "successful_run_count": len(successful_operator),
                "pass_minimal_success": any(
                    run.get("scenario_id") == "pass_minimal" and run.get("success")
                    for run in operator_runs
                ),
                "restart_continuity_success": any(
                    run.get("scenario_id") == "restart_continuity" and run.get("success")
                    for run in operator_runs
                ),
                "truth_gap_preserved": bool(truthful_gaps),
                "failure_classes": operator_failures,
                "warning_classes": operator_warning_classes,
                "preferred_models": preferred_models,
                "chosen_models": chosen_models,
                "hook_event_labels": hook_event_labels,
            },
            "automation_service": {
                "successful_run_count": len(successful_service),
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
        "operator_pass_count": operator_pass_count,
        "operator_truthful_gap_count": operator_truthful_gap_count,
        "automation_pass_count": automation_pass_count,
        "service_success_count": service_success_count,
        "providers": providers,
        "verdict": verdict,
        "verdict_reason": verdict_reason,
        "service_lane_delta": _service_lane_delta(providers),
        "next_corrective_seam": _next_corrective_seam(blocker_classes, operator_pass_count, service_success_count),
    }


def _next_corrective_seam(
    blocker_classes: set[str],
    operator_pass_count: int,
    service_success_count: int,
) -> str:
    if "auth_expired" in blocker_classes or "not_logged_in" in blocker_classes:
        return (
            "refresh or re-prove the signed-in operator credentials first, because signed-in host-native truth is the primary acceptance lane"
        )
    if "capacity_exhausted" in blocker_classes or "model_unavailable" in blocker_classes:
        return (
            "rerun the affected host on its documented fallback model and keep the preferred model pin visible in the verdict"
        )
    if operator_pass_count == 0:
        return (
            "finish the signed-in host-native product-path harness until at least one provider completes pass_minimal cleanly"
        )
    if service_success_count == 0:
        return (
            "re-open the automation auth-alignment seam for the current service endpoints without demoting the signed-in operator lane"
        )
    return (
        "add a raw-response extraction seam for the automation service lane only if shared coding-harness parity is still too thin after auth alignment"
    )


def _comparison_markdown(comparison: dict[str, Any]) -> str:
    lines = [
        "# L2 Live Testing Comparison",
        "",
        f"- Generated at: `{comparison['generated_at']}`",
        f"- Operator pass_minimal host count: `{comparison['operator_pass_count']}`",
        f"- Operator truthful-gap host count: `{comparison['operator_truthful_gap_count']}`",
        f"- Automation service success host count: `{comparison['service_success_count']}`",
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
                f"- operator baseline failures: `{', '.join(payload['operator_baseline']['failure_classes']) or 'none'}`",
                f"- operator lifecycle surface: `{payload['operator_lifecycle']['surface']}`",
                f"- operator pass_minimal success: `{payload['operator_lifecycle']['pass_minimal_success']}`",
                f"- operator restart_continuity success: `{payload['operator_lifecycle']['restart_continuity_success']}`",
                f"- operator truthful gap preserved: `{payload['operator_lifecycle']['truth_gap_preserved']}`",
                f"- operator chosen models: `{', '.join(payload['operator_lifecycle']['chosen_models']) or 'none'}`",
                f"- operator warning classes: `{', '.join(payload['operator_lifecycle']['warning_classes']) or 'none'}`",
                f"- operator hook labels: `{', '.join(payload['operator_lifecycle']['hook_event_labels']) or 'none'}`",
                f"- operator lifecycle failures: `{', '.join(payload['operator_lifecycle']['failure_classes']) or 'none'}`",
                f"- operator warning-preserving: `{payload['operator_lifecycle'].get('warning_preserving', False)}`",
                f"- operator scenario-split: `{payload['operator_lifecycle'].get('scenario_split', False)}`",
                f"- automation service failures: `{', '.join(payload['automation_service']['failure_classes']) or 'none'}`",
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
            "## Service lane delta",
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


def _service_lane_delta(providers: dict[str, Any]) -> str:
    ready = []
    blocked = []
    for provider, payload in providers.items():
        automation_auth = payload.get("automation_auth", {})
        automation_service = payload.get("automation_service", {})
        if automation_service.get("successful_run_count", 0) > 0:
            ready.append(provider)
            continue
        status = automation_auth.get("status")
        if status:
            blocked.append(f"{provider}:{status}")
        else:
            blocked.append(f"{provider}:unknown")
    return (
        f"operator strong/partial truth is earned on `{', '.join(providers.keys())}`; "
        f"automation live proof is ready on `{', '.join(ready) or 'none'}` and blocked on `{', '.join(blocked)}`."
    )


if __name__ == "__main__":
    raise SystemExit(main())
