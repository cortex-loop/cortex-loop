"""Audit reducer for raw-vs-Cortex operator directionality runs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:  # pragma: no cover - direct script entrypoint support.
    sys.path.insert(0, str(ROOT))

try:  # pragma: no cover
    from .live_validation_common import (
        BLOCKING_FAILURE_CLASSES,
        classify_failure,
        comparator_path,
        ensure_live_validation_dirs,
        live_evidence_fields,
        now_utc_iso,
        operator_directionality_root,
        write_json,
        write_text,
    )
    from .v2_behavioral_payoff import (
        PAYOFF_SCENARIOS,
        TIER1_PAYOFF_PROVIDERS,
        classify_behavioral_scenario,
        summarize_causal_payoff,
    )
except ImportError:  # pragma: no cover
    from lab.live_validation_common import (
        BLOCKING_FAILURE_CLASSES,
        classify_failure,
        comparator_path,
        ensure_live_validation_dirs,
        live_evidence_fields,
        now_utc_iso,
        operator_directionality_root,
        write_json,
        write_text,
    )
    from lab.v2_behavioral_payoff import (
        PAYOFF_SCENARIOS,
        TIER1_PAYOFF_PROVIDERS,
        classify_behavioral_scenario,
        summarize_causal_payoff,
    )


_SCENARIOS = PAYOFF_SCENARIOS
_ALL_PROVIDERS = ("claude", "codex", "gemini", "openai")
_PRIMARY_CORTEX_VARIANTS = ("full_v2_guidance", "compressed_dynamic_cortex")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 lab/live_operator_directionality_audit.py",
        description="Build the operator raw-vs-Cortex directionality audit from paired live artifacts.",
    )
    parser.add_argument(
        "--provider",
        choices=("claude", "codex", "gemini", "openai", "tier1", "all"),
        action="append",
        default=None,
    )
    args = parser.parse_args(argv)

    ensure_live_validation_dirs()
    summary = _read_json(comparator_path("operator_directionality_summary.json"))
    requested_providers = args.provider or ["all"]
    if "all" in requested_providers:
        providers = _ALL_PROVIDERS
    elif "tier1" in requested_providers:
        providers = TIER1_PAYOFF_PROVIDERS
    else:
        providers = tuple(dict.fromkeys(requested_providers))
    audit = _build_audit(summary, provider_names=providers)
    write_json(comparator_path("operator_directionality_audit.json"), audit)
    write_text(comparator_path("operator_directionality_audit.md"), _audit_markdown(audit))
    print(json.dumps(audit, indent=2, sort_keys=True))
    return 0


def _build_audit(
    summary: dict[str, Any],
    *,
    provider_names: tuple[str, ...] = TIER1_PAYOFF_PROVIDERS,
) -> dict[str, Any]:
    providers: dict[str, Any] = {}
    host_verdicts: list[str] = []
    efficiency_readings: list[str] = []
    for provider in provider_names:
        payload = _read_provider_summary(provider, summary)
        provider_audit = _audit_provider(provider, payload)
        providers[provider] = provider_audit
        host_verdicts.append(provider_audit["host_verdict"])
        efficiency_readings.append(provider_audit["efficiency_reading"])

    package_verdict, verdict_reason = _package_verdict(host_verdicts)
    causal_payoff = summarize_causal_payoff(
        {"providers": {
            provider: _read_provider_summary(provider, summary)
            for provider in provider_names
        }}
    )
    return {
        "generated_at": now_utc_iso(),
        "surface": "operator_directionality_audit",
        "lane": "operator",
        **live_evidence_fields(lane="operator"),
        "providers": providers,
        "package_verdict": package_verdict,
        "verdict_reason": verdict_reason,
        "efficiency_note": _package_efficiency_note(efficiency_readings),
        "causal_payoff": causal_payoff,
        "promotion_gate": causal_payoff["promotion_gate"],
        "tier1_providers": list(TIER1_PAYOFF_PROVIDERS),
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
        "quality_axis": host_verdict,
        "efficiency_reading": _efficiency_reading(pairs),
        "provider_limit_interference": any(
            bool(payload.get("provider_limit_interference"))
            for pair in pairs
            for payload in _pair_payloads(pair)
            if isinstance(payload, dict)
        ),
    }


def _audit_pair(pair: dict[str, Any]) -> dict[str, Any]:
    if pair.get("pair_status") != "compared":
        return {
            "scenario_id": pair.get("scenario_id"),
            "repeat_index": pair.get("repeat_index"),
            "pair_verdict": "blocked",
            "notes": [pair.get("blocked_reason") or "blocked"],
            "quality_axis": "no_meaningful_comparison",
            "burden_axis": "provider_limited",
            "provider_limit_interference": True,
            "comparison_contaminated": True,
        }

    raw = pair["raw_host"]
    cortex_label, cortex = _primary_cortex_payload(pair)
    compressed = pair.get("compressed_dynamic_cortex")
    notes: list[str] = []
    raw_failure = _effective_failure_class(raw)
    cortex_failures = [
        (label, _effective_failure_class(payload))
        for label, payload in _named_cortex_payloads(pair)
    ]
    cortex_failure = _effective_failure_class(cortex)

    if raw_failure in BLOCKING_FAILURE_CLASSES or any(
        failure in BLOCKING_FAILURE_CLASSES for _, failure in cortex_failures
    ):
        blocked_variants: list[str] = []
        if raw_failure in BLOCKING_FAILURE_CLASSES:
            blocked_variants.append("raw_host")
        blocked_variants.extend(
            label
            for label, failure in cortex_failures
            if failure in BLOCKING_FAILURE_CLASSES
        )
        return {
            "scenario_id": pair.get("scenario_id"),
            "repeat_index": pair.get("repeat_index"),
            "pair_verdict": "blocked",
            "notes": [
                f"{', '.join(blocked_variants)} hit a blocking host/provider limit before a meaningful comparison was possible"
            ],
            "quality_axis": "no_meaningful_comparison",
            "burden_axis": "provider_limited",
            "provider_limit_interference": True,
            "comparison_contaminated": True,
        }

    if pair.get("scenario_id") == "truth_gap":
        raw_truth = raw.get("truth_gap_kind") == "truthful_incomplete"
        cortex_truth = cortex.get("truth_gap_kind") == "truthful_incomplete"
        compressed_truth = (
            compressed.get("truth_gap_kind") == "truthful_incomplete"
            if isinstance(compressed, dict)
            else None
        )
        if compressed_truth is not None:
            verdict, note = _compressed_truth_gap_verdict(
                raw,
                cortex,
                compressed,
                raw_truth=raw_truth,
                full_truth=cortex_truth,
                compressed_truth=compressed_truth,
            )
            notes.append(note)
            return {
                "scenario_id": pair.get("scenario_id"),
                "repeat_index": pair.get("repeat_index"),
                "pair_verdict": verdict,
                "notes": notes,
                "quality_axis": _three_way_quality_axis(
                    raw_truth,
                    cortex_truth,
                    compressed_truth,
                ),
                "burden_axis": _three_way_burden_axis(raw, cortex, compressed),
                "provider_limit_interference": False,
                "comparison_contaminated": _comparison_contaminated(raw, cortex, compressed),
            }
        if raw_truth and not cortex_truth:
            verdict = "negative"
            notes.append(f"raw_host preserved truth_gap while {cortex_label} did not")
        elif cortex_truth and not raw_truth:
            verdict = "positive"
            notes.append(f"{cortex_label} preserved truth_gap while raw_host did not")
        elif not raw_truth and not cortex_truth:
            verdict = "mixed"
            notes.append(f"both raw_host and {cortex_label} failed truth_gap discipline, so no directional win is earned")
        else:
            burden_cmp = _compare_burden(raw, cortex)
            if burden_cmp == "worse":
                verdict = "mixed"
                notes.append(f"{cortex_label} matched truth_gap discipline but carried higher burden")
            else:
                verdict = "positive"
                notes.append(f"{cortex_label} matched truth_gap discipline without worse burden")
        return {
            "scenario_id": pair.get("scenario_id"),
            "repeat_index": pair.get("repeat_index"),
            "pair_verdict": verdict,
            "notes": notes,
            "quality_axis": _truth_gap_quality_axis(raw_truth, cortex_truth),
            "burden_axis": _burden_axis(raw, cortex),
            "provider_limit_interference": False,
            "comparison_contaminated": _comparison_contaminated(raw, cortex),
        }

    raw_success = _payload_task_success(raw, str(pair.get("scenario_id")))
    cortex_success = _payload_task_success(cortex, str(pair.get("scenario_id")))
    compressed_success = (
        _payload_task_success(compressed, str(pair.get("scenario_id")))
        if isinstance(compressed, dict)
        else None
    )
    if isinstance(compressed, dict):
        verdict, note = _compressed_task_verdict(
            raw,
            cortex,
            compressed,
            raw_success=raw_success,
            full_success=cortex_success,
            compressed_success=bool(compressed_success),
        )
        notes.append(note)
        return {
            "scenario_id": pair.get("scenario_id"),
            "repeat_index": pair.get("repeat_index"),
            "pair_verdict": verdict,
            "notes": notes,
            "quality_axis": _three_way_quality_axis(
                raw_success,
                cortex_success,
                bool(compressed_success),
            ),
            "burden_axis": _three_way_burden_axis(raw, cortex, compressed),
            "provider_limit_interference": False,
            "comparison_contaminated": _comparison_contaminated(raw, cortex, compressed),
        }
    if raw_success and not cortex_success:
        verdict = "negative"
        notes.append(f"raw_host succeeded while {cortex_label} failed")
    elif cortex_success and not raw_success:
        verdict = "positive"
        notes.append(f"{cortex_label} succeeded while raw_host failed")
    elif not raw_success and not cortex_success:
        verdict = "mixed"
        notes.append(f"both raw_host and {cortex_label} failed task value, so no directional win is earned")
    else:
        burden_cmp = _compare_burden(raw, cortex)
        scope_cmp = _compare_scope(raw, cortex)
        visibility_cmp = _compare_visibility(raw, cortex)
        if burden_cmp == "worse":
            verdict = "mixed"
            notes.append(f"{cortex_label} matched task value but carried higher burden")
        elif scope_cmp == "worse":
            verdict = "mixed"
            notes.append(f"{cortex_label} matched task value but widened file scope")
        elif visibility_cmp == "better":
            verdict = "positive"
            notes.append(f"{cortex_label} matched task value and preserved stronger lifecycle visibility")
        else:
            verdict = "positive"
            notes.append(f"{cortex_label} matched raw_host on task value without worse burden")
    return {
        "scenario_id": pair.get("scenario_id"),
        "repeat_index": pair.get("repeat_index"),
        "pair_verdict": verdict,
        "notes": notes,
        "quality_axis": _task_quality_axis(raw_success, cortex_success),
        "burden_axis": _burden_axis(raw, cortex),
        "provider_limit_interference": False,
        "comparison_contaminated": _comparison_contaminated(raw, cortex),
    }


def _pair_payloads(pair: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    payloads = [pair.get("raw_host")]
    payloads.extend(payload for _, payload in _named_cortex_payloads(pair))
    return tuple(payload for payload in payloads if isinstance(payload, dict))


def _named_cortex_payloads(pair: dict[str, Any]) -> tuple[tuple[str, dict[str, Any]], ...]:
    named: list[tuple[str, dict[str, Any]]] = []
    for variant in _PRIMARY_CORTEX_VARIANTS:
        payload = pair.get(variant)
        if isinstance(payload, dict):
            named.append((variant, payload))
    if not named and isinstance(pair.get("cortex_operator"), dict):
        named.append(("cortex_operator", pair["cortex_operator"]))
    return tuple(named)


def _primary_cortex_payload(pair: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    named = _named_cortex_payloads(pair)
    if not named:
        raise KeyError("pair does not include a Cortex comparison payload")
    return named[0]


def _compressed_truth_gap_verdict(
    raw: dict[str, Any],
    full: dict[str, Any],
    compressed: dict[str, Any],
    *,
    raw_truth: bool,
    full_truth: bool,
    compressed_truth: bool,
) -> tuple[str, str]:
    if full_truth and not compressed_truth:
        return "negative", "compressed_dynamic_cortex lost truth-gap discipline that full_v2_guidance preserved"
    if compressed_truth and not raw_truth:
        return "positive", "compressed_dynamic_cortex preserved truth-gap discipline beyond raw_host"
    if compressed_truth and full_truth:
        burden_cmp = _compare_burden(full, compressed)
        if burden_cmp == "worse":
            return "mixed", "compressed_dynamic_cortex matched full_v2_guidance but carried higher burden"
        return "positive", "compressed_dynamic_cortex matched full_v2_guidance without worse burden"
    return "mixed", "compressed_dynamic_cortex did not earn a truth-gap payoff"


def _compressed_task_verdict(
    raw: dict[str, Any],
    full: dict[str, Any],
    compressed: dict[str, Any],
    *,
    raw_success: bool,
    full_success: bool,
    compressed_success: bool,
) -> tuple[str, str]:
    if full_success and not compressed_success:
        return "negative", "compressed_dynamic_cortex regressed task success versus full_v2_guidance"
    if compressed_success and not raw_success:
        return "positive", "compressed_dynamic_cortex succeeded where raw_host did not"
    if compressed_success and full_success:
        burden_cmp = _compare_burden(full, compressed)
        scope_cmp = _compare_scope(full, compressed)
        if burden_cmp == "worse":
            return "mixed", "compressed_dynamic_cortex matched full_v2_guidance but carried higher burden"
        if scope_cmp == "worse":
            return "mixed", "compressed_dynamic_cortex matched full_v2_guidance but widened file scope"
        return "positive", "compressed_dynamic_cortex matched full_v2_guidance without worse burden or scope"
    if raw_success and not compressed_success:
        return "negative", "raw_host succeeded while compressed_dynamic_cortex failed"
    return "mixed", "no variant earned task value, so no compressed payoff is earned"


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


def _truth_gap_quality_axis(raw_truth: bool, cortex_truth: bool) -> str:
    if raw_truth and not cortex_truth:
        return "raw_better"
    if cortex_truth and not raw_truth:
        return "cortex_better"
    if raw_truth and cortex_truth:
        return "matched"
    return "both_failed"


def _task_quality_axis(raw_success: bool, cortex_success: bool) -> str:
    if raw_success and not cortex_success:
        return "raw_better"
    if cortex_success and not raw_success:
        return "cortex_better"
    if raw_success and cortex_success:
        return "matched"
    return "both_failed"


def _payload_task_success(payload: dict[str, Any], scenario_id: str) -> bool:
    if scenario_id in PAYOFF_SCENARIOS:
        return bool(
            classify_behavioral_scenario(
                scenario_id=scenario_id,
                result_text=payload.get("result_text"),
                modified_files=payload.get("modified_files"),
                test_exit_code=payload.get("test_exit_code"),
                failure_class=payload.get("failure_class"),
            )["task_success"]
        )
    return bool(payload.get("success")) and payload.get("test_exit_code") == 0


def _burden_axis(raw: dict[str, Any], cortex: dict[str, Any]) -> str:
    burden_cmp = _compare_burden(raw, cortex)
    if burden_cmp == "worse":
        return "cortex_higher"
    if burden_cmp == "better":
        return "raw_higher"
    return "matched"


def _three_way_quality_axis(raw: bool, full: bool, compressed: bool) -> str:
    if compressed and not raw:
        return "compressed_better_than_raw"
    if full and not compressed:
        return "compressed_regressed_from_full"
    if compressed and full and raw:
        return "matched"
    if not raw and not full and not compressed:
        return "all_failed"
    return "mixed"


def _three_way_burden_axis(
    raw: dict[str, Any],
    full: dict[str, Any],
    compressed: dict[str, Any],
) -> str:
    full_vs_compressed = _compare_burden(full, compressed)
    raw_vs_compressed = _compare_burden(raw, compressed)
    if full_vs_compressed == "worse":
        return "compressed_higher_than_full"
    if full_vs_compressed == "better":
        return "compressed_lower_than_full"
    if raw_vs_compressed == "worse":
        return "compressed_higher_than_raw"
    return "matched"


def _comparison_contaminated(*payloads: dict[str, Any]) -> bool:
    return any(bool(payload.get("comparison_contaminated")) for payload in payloads)


def _effective_failure_class(payload: dict[str, Any]) -> str | None:
    failure_class = payload.get("failure_class")
    if isinstance(failure_class, str) and failure_class.strip():
        return failure_class
    result_text = payload.get("result_text")
    if isinstance(result_text, str):
        return classify_failure(result_text)
    return None


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


def _efficiency_reading(pairs: list[dict[str, Any]]) -> str:
    if any(
        any(bool(payload.get("provider_limit_interference")) for payload in _pair_payloads(pair))
        for pair in pairs
    ):
        return "provider_limited"
    visible_payloads = [
        payload
        for pair in pairs
        for payload in _pair_payloads(pair)
        if isinstance(payload, dict) and payload.get("token_usage_visible") is True
    ]
    if not visible_payloads:
        return "insufficient_visibility"
    if any(_token_burden_delta(pair) == "cortex_higher" for pair in pairs if pair.get("pair_status") == "compared"):
        return "elevated_burden"
    return "clean"


def _token_burden_delta(pair: dict[str, Any]) -> str | None:
    raw = pair.get("raw_host") or {}
    _, cortex = _primary_cortex_payload(pair)
    compressed = pair.get("compressed_dynamic_cortex")
    if isinstance(compressed, dict):
        cortex = compressed
    if not raw.get("token_usage_visible") or not cortex.get("token_usage_visible"):
        return None
    raw_total = sum(int(raw.get(field, 0) or 0) for field in ("input_tokens", "output_tokens", "cache_tokens"))
    cortex_total = sum(int(cortex.get(field, 0) or 0) for field in ("input_tokens", "output_tokens", "cache_tokens"))
    if cortex_total >= raw_total + 1000 and cortex_total >= int(raw_total * 1.5):
        return "cortex_higher"
    if raw_total >= cortex_total + 1000 and raw_total >= int(cortex_total * 1.5):
        return "raw_higher"
    return "matched"


def _package_efficiency_note(efficiency_readings: list[str]) -> str:
    if any(reading == "provider_limited" for reading in efficiency_readings):
        return "At least one host is currently provider-limited, so efficiency evidence remains contaminated by host quota/rate ceilings."
    if any(reading == "elevated_burden" for reading in efficiency_readings):
        return "At least one host shows elevated Cortex burden, so package-level efficiency is not yet clean."
    if all(reading == "clean" for reading in efficiency_readings):
        return "Current host-visible efficiency looks clean on the compared operator surfaces."
    return "Token usage visibility remains incomplete on at least one host surface, so package-level efficiency is still only partially observable."


def _audit_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# Operator Directionality Audit",
        "",
        f"- Generated at: `{audit['generated_at']}`",
        f"- Package verdict: **{audit['package_verdict']}**",
        f"- Promotion gate: `{audit['promotion_gate']}`",
        "- Pair order: alternated by repeat index to reduce shared-budget bias.",
        "",
        audit["verdict_reason"],
        "",
        audit["efficiency_note"],
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
                f"- quality axis: `{payload['quality_axis']}`",
                f"- efficiency reading: `{payload['efficiency_reading']}`",
                f"- provider-limit interference: `{payload['provider_limit_interference']}`",
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
