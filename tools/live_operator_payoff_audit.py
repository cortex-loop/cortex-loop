"""Cross-host operator payoff audit for the live-validation train."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from live_validation_common import (
    comparator_path,
    ensure_live_validation_dirs,
    live_evidence_fields,
    now_utc_iso,
    write_json,
    write_text,
)


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

    for provider in ("claude", "gemini", "openai"):
        payload = compare.get("providers", {}).get(provider, {})
        operator = payload.get("operator_lifecycle", {})

        providers[provider] = {
            "watchlist_status": operator.get("watchlist_status", "unknown"),
            "source": operator.get("source", "unknown"),
            "accepted_watchlist_status": operator.get("accepted_watchlist_status"),
            "accepted_watchlist_drift_detected": operator.get(
                "accepted_watchlist_drift_detected",
                False,
            ),
            "chosen_models": operator.get("chosen_models", []),
            "warning_classes": operator.get("warning_classes", []),
            "failure_classes": operator.get("failure_classes", []),
            "hook_event_labels": operator.get("hook_event_labels", []),
        }

    verdict, verdict_reason = _operator_watchlist_verdict(compare)
    return {
        "generated_at": now_utc_iso(),
        "lane": "operator",
        **live_evidence_fields(lane="operator"),
        "canonical_verdict": compare.get("verdict"),
        "providers": providers,
        "verdict": verdict,
        "verdict_reason": verdict_reason,
        "qualifier": "This audit is watchlist-only. It may summarize headless-CLI behavior, but it does not establish product/runtime payoff.",
    }


def _operator_watchlist_verdict(compare: dict[str, Any]) -> tuple[str, str]:
    canonical_verdict = compare.get("verdict")
    if canonical_verdict == "canonical runtime truth is blocked on this machine":
        return (
            "operator watchlist snapshot recorded under blocked canonical truth",
            "The direct-API lane is still blocked on this machine, so this audit is diagnostic only and cannot establish runtime payoff.",
        )
    if canonical_verdict == "canonical runtime truth is still partial":
        return (
            "operator watchlist snapshot recorded under partial canonical truth",
            "The direct-API lane has some evidence but is not yet stable enough for runtime closure, so this audit remains secondary.",
        )
    return (
        "operator watchlist snapshot recorded alongside canonical truth",
        "Direct-API truth is carrying the runtime claim for current scope; this audit remains a secondary watchlist for host-boundary drift.",
    )


def _audit_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# Operator Watchlist Diagnostic",
        "",
        f"- Generated at: `{audit['generated_at']}`",
        f"- Evidence lane: `{audit['execution_surface']} / {audit['evidence_role']}`",
        f"- Canonical verdict: `{audit.get('canonical_verdict')}`",
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
                f"- watchlist status: `{payload['watchlist_status']}`",
                f"- source: `{payload['source']}`",
                f"- accepted watchlist status: `{payload.get('accepted_watchlist_status') or 'none'}`",
                f"- accepted watchlist drift detected: `{payload['accepted_watchlist_drift_detected']}`",
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
