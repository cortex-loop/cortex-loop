"""Audit reducer for raw-vs-Cortex operator directionality runs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:  # pragma: no cover
    from .live_validation_common import (
        BLOCKING_FAILURE_CLASSES,
        comparator_path,
        ensure_live_validation_dirs,
        now_utc_iso,
        operator_directionality_root,
        write_json,
        write_text,
    )
except ImportError:  # pragma: no cover
    from live_validation_common import (
        BLOCKING_FAILURE_CLASSES,
        comparator_path,
        ensure_live_validation_dirs,
        now_utc_iso,
        operator_directionality_root,
        write_json,
        write_text,
    )


_SCENARIOS = ("pass_minimal", "truth_gap", "restart_continuity")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 tools/live_operator_directionality_audit.py",
        description="Build the operator raw-vs-Cortex directionality audit from paired live artifacts.",
    )
    parser.parse_args(argv)

    ensure_live_validation_dirs()
    summary = _read_json(comparator_path("operator_directionality_summary.json"))
    audit = _build_audit(summary)
    write_json(comparator_path("operator_directionality_audit.json"), audit)
    write_text(comparator_path("operator_directionality_audit.md"), _audit_markdown(audit))
    print(json.dumps(audit, indent=2, sort_keys=True))
    return 0


def _build_audit(summary: dict[str, Any]) -> dict[str, Any]:
    providers: dict[str, Any] = {}
    host_verdicts: list[str] = []
    for provider in ("claude", "gemini", "openai"):
        payload = _read_provider_summary(provider, summary)
        provider_audit = _audit_provider(provider, payload)
        providers[provider] = provider_audit
        host_verdicts.append(provider_audit["host_verdict"])

    package_verdict, verdict_reason = _package_verdict(host_verdicts)
    return {
        "generated_at": now_utc_iso(),
        "surface": "operator_directionality_audit",
        "providers": providers,
        "package_verdict": package_verdict,
        "verdict_reason": verdict_reason,
    }


def _audit_provider(provider: str, payload: dict[str, Any]) -> dict[str, Any]:
    pairs = payload.get("pairs", [])
    scenario_summaries: dict[str, Any] = {}
    scenario_verdicts: list[str] = []
    for scenario_id in _SCENARIOS:
        scenario_pairs = [pair for pair in pairs if pair.get("scenario_id") == scenario_id]
        audited_pairs = [_audit_pair(pair) for pair in scenario_pairs]
        scenario_verdict = _scenario_verdict(audited_pairs)
        scenario_summaries[scenario_id] = {
            "pair_count": len(audited_pairs),
            "pair_verdicts": [pair["pair_verdict"] for pair in audited_pairs],
            "scenario_verdict": scenario_verdict,
            "pairs": audited_pairs,
        }
        scenario_verdicts.append(scenario_verdict)

    host_verdict = _host_verdict(scenario_verdicts)
    return {
        "raw_host_precheck": payload.get("raw_host_precheck", {}),
        "scenario_summaries": scenario_summaries,
        "host_verdict": host_verdict,
    }


def _audit_pair(pair: dict[str, Any]) -> dict[str, Any]:
    if pair.get("pair_status") != "compared":
        return {
            "scenario_id": pair.get("scenario_id"),
            "repeat_index": pair.get("repeat_index"),
            "pair_verdict": "blocked",
            "notes": [pair.get("blocked_reason") or "blocked"],
        }

    raw = pair["raw_host"]
    cortex = pair["cortex_operator"]
    notes: list[str] = []
    raw_failure = raw.get("failure_class")
    cortex_failure = cortex.get("failure_class")

    if raw_failure in BLOCKING_FAILURE_CLASSES and cortex_failure in BLOCKING_FAILURE_CLASSES:
        return {
            "scenario_id": pair.get("scenario_id"),
            "repeat_index": pair.get("repeat_index"),
            "pair_verdict": "blocked",
            "notes": [
                "both raw_host and cortex_operator were blocked before a meaningful comparison was possible"
            ],
        }

    if pair.get("scenario_id") == "truth_gap":
        raw_truth = raw.get("truth_gap_kind") == "truthful_incomplete"
        cortex_truth = cortex.get("truth_gap_kind") == "truthful_incomplete"
        if raw_truth and not cortex_truth:
            verdict = "negative"
            notes.append("raw_host preserved truth_gap while cortex_operator did not")
        elif cortex_truth and not raw_truth:
            verdict = "positive"
            notes.append("cortex_operator preserved truth_gap while raw_host did not")
        else:
            burden_cmp = _compare_burden(raw, cortex)
            if burden_cmp == "worse":
                verdict = "mixed"
                notes.append("cortex_operator matched truth_gap discipline but carried higher burden")
            else:
                verdict = "positive"
                notes.append("cortex_operator matched truth_gap discipline without worse burden")
        return {
            "scenario_id": pair.get("scenario_id"),
            "repeat_index": pair.get("repeat_index"),
            "pair_verdict": verdict,
            "notes": notes,
        }

    raw_success = bool(raw.get("success")) and raw.get("test_exit_code") == 0
    cortex_success = bool(cortex.get("success")) and cortex.get("test_exit_code") == 0
    if raw_success and not cortex_success:
        verdict = "negative"
        notes.append("raw_host succeeded while cortex_operator failed")
    elif cortex_success and not raw_success:
        verdict = "positive"
        notes.append("cortex_operator succeeded while raw_host failed")
    else:
        burden_cmp = _compare_burden(raw, cortex)
        scope_cmp = _compare_scope(raw, cortex)
        visibility_cmp = _compare_visibility(raw, cortex)
        if burden_cmp == "worse":
            verdict = "mixed"
            notes.append("cortex_operator matched task value but carried higher burden")
        elif scope_cmp == "worse":
            verdict = "mixed"
            notes.append("cortex_operator matched task value but widened file scope")
        elif visibility_cmp == "better":
            verdict = "positive"
            notes.append("cortex_operator matched task value and preserved stronger lifecycle visibility")
        else:
            verdict = "positive"
            notes.append("cortex_operator matched raw_host on task value without worse burden")
    return {
        "scenario_id": pair.get("scenario_id"),
        "repeat_index": pair.get("repeat_index"),
        "pair_verdict": verdict,
        "notes": notes,
    }


def _compare_burden(raw: dict[str, Any], cortex: dict[str, Any]) -> str:
    raw_score = len(raw.get("warning_classes", [])) + max(0, len(raw.get("attempted_models", [])) - 1)
    cortex_score = len(cortex.get("warning_classes", [])) + max(0, len(cortex.get("attempted_models", [])) - 1)
    if cortex_score > raw_score:
        return "worse"
    if cortex_score < raw_score:
        return "better"
    return "same"


def _compare_scope(raw: dict[str, Any], cortex: dict[str, Any]) -> str:
    raw_count = len(raw.get("modified_files", []) or [])
    cortex_count = len(cortex.get("modified_files", []) or [])
    if cortex_count > raw_count:
        return "worse"
    if cortex_count < raw_count:
        return "better"
    return "same"


def _compare_visibility(raw: dict[str, Any], cortex: dict[str, Any]) -> str:
    raw_score = len(raw.get("hook_event_labels", []) or []) + len(raw.get("lifecycle_event_labels", []) or [])
    cortex_score = len(cortex.get("hook_event_labels", []) or []) + len(cortex.get("lifecycle_event_labels", []) or [])
    if cortex_score > raw_score:
        return "better"
    if cortex_score < raw_score:
        return "worse"
    return "same"


def _scenario_verdict(audited_pairs: list[dict[str, Any]]) -> str:
    verdicts = [pair["pair_verdict"] for pair in audited_pairs]
    if not verdicts:
        return "blocked"
    if any(verdict == "negative" for verdict in verdicts):
        return "negative"
    if any(verdict == "mixed" for verdict in verdicts):
        return "mixed"
    if all(verdict == "blocked" for verdict in verdicts):
        return "blocked"
    if any(verdict == "blocked" for verdict in verdicts):
        return "mixed"
    return "positive"


def _host_verdict(scenario_verdicts: list[str]) -> str:
    non_empty = [verdict for verdict in scenario_verdicts if verdict]
    if not non_empty or all(verdict == "blocked" for verdict in non_empty):
        return "blocked"
    if any(verdict == "negative" for verdict in non_empty):
        return "negative"
    if any(verdict == "mixed" for verdict in non_empty):
        return "mixed"
    if any(verdict == "blocked" for verdict in non_empty):
        return "mixed"
    return "positive"


def _package_verdict(host_verdicts: list[str]) -> tuple[str, str]:
    if all(verdict == "blocked" for verdict in host_verdicts):
        return (
            "blocked",
            "Every host is blocked or contaminated, so the current machine cannot answer raw-vs-Cortex directionality honestly.",
        )
    if any(verdict == "negative" for verdict in host_verdicts):
        return (
            "not_yet_positive",
            "At least one host is directionally negative, so further widening should pause until that is explained.",
        )
    if any(verdict in {"mixed", "blocked"} for verdict in host_verdicts):
        return (
            "mixed_direction",
            "Some hosts are positive, but at least one host remains mixed or blocked, so package-level direction is not yet clean.",
        )
    return (
        "promising_positive",
        "All compared hosts are directionally positive or matching without hidden burden inflation on the current paired audit.",
    )


def _audit_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# Operator Directionality Audit",
        "",
        f"- Generated at: `{audit['generated_at']}`",
        f"- Package verdict: **{audit['package_verdict']}**",
        "",
        audit["verdict_reason"],
        "",
        "## Host summary",
        "",
    ]
    for provider, payload in audit["providers"].items():
        lines.extend(
            [
                f"### {provider}",
                "",
                f"- host verdict: `{payload['host_verdict']}`",
                f"- raw precheck: `{payload['raw_host_precheck'].get('status', 'unknown')}`",
            ]
        )
        note = payload["raw_host_precheck"].get("note")
        if isinstance(note, str) and note.strip():
            lines.append(f"- raw precheck note: {note}")
        lines.append("")
        for scenario_id, scenario_payload in payload["scenario_summaries"].items():
            lines.append(f"- {scenario_id}: `{scenario_payload['scenario_verdict']}`")
        lines.append("")
    return "\n".join(lines)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _read_provider_summary(provider: str, summary: dict[str, Any]) -> dict[str, Any]:
    provider_summary_path = operator_directionality_root(provider, "summary") / "summary.json"
    provider_summary = _read_json(provider_summary_path)
    if provider_summary.get("pairs"):
        return provider_summary
    return summary.get("providers", {}).get(provider, {})


if __name__ == "__main__":
    raise SystemExit(main())
