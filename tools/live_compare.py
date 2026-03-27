"""Comparator and verdict builder for L1 live-validation artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from live_validation_common import (
    PREFLIGHT_REPORT_PATH,
    PROVIDER_ROOTS,
    decide_verdict,
    ensure_live_validation_dirs,
    now_utc_iso,
    write_json,
    write_text,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 tools/live_compare.py",
        description="Build the L1 comparison summary and verdict from captured artifacts.",
    )
    parser.parse_args(argv)

    ensure_live_validation_dirs()
    preflight = _read_json(PREFLIGHT_REPORT_PATH)
    provider_baselines = _read_json(
        PROVIDER_ROOTS["comparators"] / "provider_baseline_summary.json"
    )
    cortex_live = _read_json(PROVIDER_ROOTS["comparators"] / "cortex_live_summary.json")

    comparison = _build_comparison(preflight, provider_baselines, cortex_live)
    write_json(PROVIDER_ROOTS["comparators"] / "live_validation_comparison.json", comparison)
    write_text(
        PROVIDER_ROOTS["comparators"] / "live_validation_comparison.md",
        _comparison_markdown(comparison),
    )
    print(json.dumps(comparison, indent=2, sort_keys=True))
    return 0


def _build_comparison(
    preflight: dict[str, Any],
    provider_baselines: dict[str, Any],
    cortex_live: dict[str, Any],
) -> dict[str, Any]:
    providers: dict[str, Any] = {}
    blocker_classes: set[str] = set()
    provider_success_count = 0
    cortex_success_count = 0

    for provider in ("claude", "gemini", "openai"):
        baseline_runs = provider_baselines.get("providers", {}).get(provider, {}).get("runs", [])
        cortex_runs = cortex_live.get("providers", {}).get(provider, {}).get("runs", [])
        successful_baseline = [run for run in baseline_runs if run.get("success")]
        successful_cortex = [run for run in cortex_runs if run.get("success")]
        baseline_failures = sorted(
            {run["failure_class"] for run in baseline_runs if run.get("failure_class")}
        )
        cortex_failures = sorted(
            {run["failure_class"] for run in cortex_runs if run.get("failure_class")}
        )
        blocker_classes.update(baseline_failures)
        blocker_classes.update(cortex_failures)
        if successful_baseline:
            provider_success_count += 1
        if successful_cortex:
            cortex_success_count += 1

        providers[provider] = {
            "provider_baseline": {
                "successful_run_count": len(successful_baseline),
                "failure_classes": baseline_failures,
                "first_success_labels": successful_baseline[0].get("structured_event_labels", [])
                if successful_baseline
                else [],
            },
            "cortex_live": {
                "successful_run_count": len(successful_cortex),
                "failure_classes": cortex_failures,
                "record_count_total": sum(
                    int(run.get("record_count", 0)) for run in successful_cortex
                ),
            },
            "environment_api_key_present": preflight["auth_surfaces"]["environment_api_keys"].get(
                f"{provider.upper()}_API_KEY".replace("CLAUDE", "ANTHROPIC")
            ),
        }

    verdict, verdict_reason = decide_verdict(
        provider_success_count=provider_success_count,
        cortex_success_count=cortex_success_count,
        blocker_classes=blocker_classes,
    )
    return {
        "generated_at": now_utc_iso(),
        "provider_success_count": provider_success_count,
        "cortex_success_count": cortex_success_count,
        "providers": providers,
        "verdict": verdict,
        "verdict_reason": verdict_reason,
        "next_corrective_seam": _next_corrective_seam(blocker_classes, cortex_success_count),
    }


def _next_corrective_seam(blocker_classes: set[str], cortex_success_count: int) -> str:
    if "auth_missing" in blocker_classes or "auth_expired" in blocker_classes:
        return (
            "open one bounded live-auth alignment seam so the provider CLI sessions and the "
            "current A4/G4/O4 live transports can both prove fresh credentials without private-account drift"
        )
    if "capacity_exhausted" in blocker_classes or "quota_exhausted" in blocker_classes:
        return (
            "open one bounded live-model availability seam to choose subscription-runnable models without silently rewriting accepted product pins"
        )
    if cortex_success_count == 0:
        return (
            "open one bounded live-capture proof seam that gets at least one successful Cortex host-control run per provider before judging payoff"
        )
    return (
        "open one bounded richer host-event capture seam only if repeated live evidence shows provider-native structure that the current shells drop materially"
    )


def _comparison_markdown(comparison: dict[str, Any]) -> str:
    lines = [
        "# L1 Live Validation Comparison",
        "",
        f"- Generated at: `{comparison['generated_at']}`",
        f"- Provider baseline successes: `{comparison['provider_success_count']}`",
        f"- Cortex live-path successes: `{comparison['cortex_success_count']}`",
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
                f"- provider baseline successful runs: `{payload['provider_baseline']['successful_run_count']}`",
                f"- provider baseline failure classes: `{', '.join(payload['provider_baseline']['failure_classes']) or 'none'}`",
                f"- Cortex live successful runs: `{payload['cortex_live']['successful_run_count']}`",
                f"- Cortex live failure classes: `{', '.join(payload['cortex_live']['failure_classes']) or 'none'}`",
                f"- Cortex live total record count: `{payload['cortex_live']['record_count_total']}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Next corrective seam",
            "",
            comparison["next_corrective_seam"],
            "",
        ]
    )
    return "\n".join(lines)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
