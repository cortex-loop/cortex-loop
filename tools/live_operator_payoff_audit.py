"""Cross-host operator payoff audit for the live-validation train."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from live_validation_common import comparator_path, ensure_live_validation_dirs, now_utc_iso, write_json, write_text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 tools/live_operator_payoff_audit.py",
        description="Build the operator-only payoff audit from local live-validation artifacts.",
    )
    parser.parse_args(argv)

    ensure_live_validation_dirs()
    compare = _read_json(comparator_path("live_validation_comparison.json"))
    audit = _build_audit(compare)
    write_json(comparator_path("operator_payoff_audit.json"), audit)
    write_text(comparator_path("operator_payoff_audit.md"), _audit_markdown(audit))
    print(json.dumps(audit, indent=2, sort_keys=True))
    return 0


def _build_audit(compare: dict[str, Any]) -> dict[str, Any]:
    providers: dict[str, Any] = {}
    strong_count = 0
    partial_count = 0

    for provider in ("claude", "gemini", "openai"):
        payload = compare.get("providers", {}).get(provider, {})
        operator = payload.get("operator_lifecycle", {})
        warnings = operator.get("warning_classes", [])
        failures = operator.get("failure_classes", [])
        pass_minimal = bool(operator.get("pass_minimal_success"))
        truth_gap = bool(operator.get("truth_gap_preserved"))
        continuity = bool(operator.get("restart_continuity_success"))
        hook_labels = operator.get("hook_event_labels", [])
        chosen_models = operator.get("chosen_models", [])

        lifecycle_visibility = "strong" if (provider == "openai" or hook_labels) else "partial"
        truth_discipline = "strong" if truth_gap else "partial"
        continuity_value = "strong" if continuity else "partial"
        task_value = "strong" if pass_minimal else "partial"
        host_burden = "partial" if warnings or failures else "strong"

        if pass_minimal and truth_gap and continuity:
            classification = "strong"
            strong_count += 1
        elif pass_minimal or truth_gap or continuity:
            classification = "partial"
            partial_count += 1
        else:
            classification = "blocked"

        providers[provider] = {
            "classification": classification,
            "lifecycle_visibility": lifecycle_visibility,
            "truth_discipline": truth_discipline,
            "continuity_value": continuity_value,
            "task_value": task_value,
            "host_burden": host_burden,
            "chosen_models": chosen_models,
            "warning_classes": warnings,
            "failure_classes": failures,
            "hook_event_labels": hook_labels,
        }

    verdict, verdict_reason = _operator_payoff_verdict(providers, strong_count, partial_count)
    return {
        "generated_at": now_utc_iso(),
        "providers": providers,
        "verdict": verdict,
        "verdict_reason": verdict_reason,
        "qualifier": "Gemini remains an explicit partial host line and automation/service remains blocked on missing machine auth.",
    }


def _operator_payoff_verdict(
    providers: dict[str, Any],
    strong_count: int,
    partial_count: int,
) -> tuple[str, str]:
    if strong_count >= 2 and providers.get("gemini", {}).get("classification") == "partial":
        return (
            "operator lifecycle-first is already paying off clearly",
            "Claude and OpenAI are strong on real host-native operator lanes, while Gemini remains explicit partial truth rather than hidden failure.",
        )
    if strong_count >= 1 or partial_count >= 2:
        return (
            "operator lifecycle-first is promising but still host-fragile",
            "Some hosts now show clear operator-lifecycle value, but the cross-host picture is still too uneven to treat the lane as fully robust.",
        )
    return (
        "operator lifecycle-first is not yet paying off enough",
        "Too little host-native operator truth is earned to claim clear lifecycle payoff.",
    )


def _audit_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# L3 Operator Payoff Audit",
        "",
        f"- Generated at: `{audit['generated_at']}`",
        f"- Verdict: **{audit['verdict']}**",
        "",
        audit["verdict_reason"],
        "",
        audit["qualifier"],
        "",
        "## Provider audit",
        "",
    ]
    for provider, payload in audit["providers"].items():
        lines.extend(
            [
                f"### {provider}",
                "",
                f"- classification: `{payload['classification']}`",
                f"- lifecycle visibility: `{payload['lifecycle_visibility']}`",
                f"- truth discipline: `{payload['truth_discipline']}`",
                f"- continuity value: `{payload['continuity_value']}`",
                f"- task value: `{payload['task_value']}`",
                f"- host burden: `{payload['host_burden']}`",
                f"- chosen models: `{', '.join(payload['chosen_models']) or 'none'}`",
                f"- warning classes: `{', '.join(payload['warning_classes']) or 'none'}`",
                f"- failure classes: `{', '.join(payload['failure_classes']) or 'none'}`",
                f"- hook/event labels: `{', '.join(payload['hook_event_labels']) or 'none'}`",
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
