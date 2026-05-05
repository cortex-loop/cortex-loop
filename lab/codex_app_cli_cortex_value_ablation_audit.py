"""Decision audit for Codex App/CLI Cortex value evidence.

The audit is intentionally read-only against existing live artifacts by
default. It separates threshold, paydown, Stop text, family scope, and
claim/evidence perception questions without changing product Cortex policy.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:  # pragma: no cover - direct script support.
    sys.path.insert(0, str(REPO_ROOT))

try:  # pragma: no cover - direct script execution uses fallback imports.
    from .codex_app_cli_hook_native_behavior_comparison import OUTPUT_QUALITY_TASK_ID
    from .codex_app_cli_stop_activation_probe import _hash_text, _jsonl_rows, _stable_hash
    from .cortex_output_quality import task_pack_by_name
    from .live_validation_common import LOCAL_LIVE_ROOT
except ImportError:  # pragma: no cover
    from lab.codex_app_cli_hook_native_behavior_comparison import OUTPUT_QUALITY_TASK_ID
    from lab.codex_app_cli_stop_activation_probe import _hash_text, _jsonl_rows, _stable_hash
    from lab.cortex_output_quality import task_pack_by_name
    from lab.live_validation_common import LOCAL_LIVE_ROOT


DEFAULT_OUTPUT_ROOT = LOCAL_LIVE_ROOT / "openai" / "codex_app_cli_cortex_value_ablation_audit"
DEFAULT_ASTRO_RUN_ROOT = (
    LOCAL_LIVE_ROOT
    / "openai"
    / "codex_app_cli_hook_native_behavior_comparison"
    / "astro_three_arm_live_20260505T033207Z"
)
DEFAULT_CONTINUATION_ROOT = (
    LOCAL_LIVE_ROOT
    / "openai"
    / "codex_app_cli_stop_continuation_resolution_loop"
)
DEFAULT_BEHAVIOR_COMPARISON_ROOT = (
    LOCAL_LIVE_ROOT / "openai" / "codex_app_cli_hook_native_behavior_comparison"
)
DEFAULT_VISIBLE_RERUN_ROOT = (
    LOCAL_LIVE_ROOT / "openai" / "visible_intervention_live_probe" / "live_trials"
)
APPROVAL_ENV = "CORTEX_CODEX_APP_CLI_VALUE_ABLATION_AUDIT_APPROVED"
THRESHOLDS = (0.55, 0.35, 0.15, 0.0)
PRIMARY_OBLIGATIONS = (
    "docs index page",
    "nested docs pages",
    "tag pages",
    "docs search experience",
    "shared navigation",
)
VISIBLE_CHECK_MARKERS = ("test:visible", "npm run build", "npm run lint", "npm run typecheck")
GENERIC_CHECK_MARKERS = ("build", "lint", "typecheck", "test", "cat ", "grep", "stat")
CLAIM_WORDS = ("done", "complete", "completed", "implemented", "created", "fixed", "ready")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--astro-run-root", type=Path, default=DEFAULT_ASTRO_RUN_ROOT)
    parser.add_argument("--require-pass", action="store_true")
    parser.add_argument("--forced-intervention-live", action="store_true")
    args = parser.parse_args(argv)

    if args.forced_intervention_live:
        report = run_forced_intervention_live(output_root=args.output_root)
    else:
        report = run_audit(output_root=args.output_root, astro_run_root=args.astro_run_root)
    print(json.dumps(report, sort_keys=True, indent=2))
    if args.require_pass and not report.get("passed", False):
        return 1
    return 0


def run_audit(
    *,
    output_root: Path | str = DEFAULT_OUTPUT_ROOT,
    astro_run_root: Path | str = DEFAULT_ASTRO_RUN_ROOT,
) -> dict[str, Any]:
    output = Path(output_root)
    output.mkdir(parents=True, exist_ok=True)
    astro_root = Path(astro_run_root)
    astro_summary = _load_json(astro_root / "summary.json")
    astro_rows = _load_jsonl(astro_root / "trajectory.jsonl")
    hook_native_rows = [row for row in astro_rows if row.get("condition") == "hook_native_cortex"]

    threshold = threshold_replay(hook_native_rows)
    paydown = paydown_ablation(hook_native_rows)
    alignment = claim_evidence_alignment(hook_native_rows)
    family = family_separation(
        astro_summary=astro_summary,
        continuation_summary=_latest_matching(DEFAULT_CONTINUATION_ROOT, "run_*/report.json"),
        behavior_summary=_load_json(DEFAULT_BEHAVIOR_COMPARISON_ROOT / "live_trials_20260504T203012Z" / "summary.json"),
        visible_rerun_summary=_load_json(DEFAULT_VISIBLE_RERUN_ROOT / "2026-05-03T115354Z0000" / "summary.json"),
    )
    forced = forced_intervention_probe_status()
    decision = audit_decision(
        threshold=threshold,
        paydown=paydown,
        alignment=alignment,
        family=family,
        forced=forced,
    )
    report = {
        "probe": "codex_app_cli_cortex_value_ablation_audit",
        "surface": "product_plus_lab_proof",
        "evidence_kind": "offline_value_ablation_audit",
        "passed": True,
        "verdict": decision["verdict"],
        "decision": decision,
        "artifact_roots": {
            "astro_three_arm": str(astro_root),
            "continuation_resolution": str(DEFAULT_CONTINUATION_ROOT),
            "behavior_comparison": str(DEFAULT_BEHAVIOR_COMPARISON_ROOT),
            "visible_hardened_rerun": str(DEFAULT_VISIBLE_RERUN_ROOT),
        },
        "threshold_replay": threshold,
        "paydown_ablation": paydown,
        "claim_evidence_alignment": alignment,
        "family_separation": family,
        "forced_intervention_probe": forced,
        "truth_boundary": (
            "This audit replays existing product/lab evidence and may choose the "
            "next research direction. It does not change Cortex thresholds, "
            "paydown policy, speech, hooks, or shipping truth."
        ),
    }
    _write_json(output / "summary.json", report)
    return report


def threshold_replay(rows: list[Mapping[str, Any]], thresholds: Iterable[float] = THRESHOLDS) -> dict[str, Any]:
    trials = []
    for row in rows:
        final_stop = _final_stop_diagnostics(row)
        pressure = _strongest_pressure(final_stop)
        session_state = _session_state(final_stop)
        active = _expectations(session_state, "active")
        resolved = _expectations(session_state, "resolved")
        trials.append(
            {
                "trial_id": row.get("trial_id"),
                "hidden_quality_pass": bool(row.get("hidden_quality_pass")),
                "pressure": pressure,
                "active_expectation_count": len(active),
                "resolved_expectation_count": len(resolved),
                "silence_reason": _directive(final_stop).get("silence_reason"),
                "would_block_by_threshold": {
                    f"{threshold:.2f}": bool(active and pressure >= threshold)
                    for threshold in thresholds
                },
            }
        )
    hidden_failures = [trial for trial in trials if not trial["hidden_quality_pass"]]
    threshold_changed = any(
        any(trial["would_block_by_threshold"].values()) for trial in hidden_failures
    )
    verdict = "threshold_could_change_outcome" if threshold_changed else "threshold_not_causal"
    return {
        "verdict": verdict,
        "thresholds": [round(float(threshold), 2) for threshold in thresholds],
        "hidden_failure_count": len(hidden_failures),
        "trials": trials,
    }


def paydown_ablation(rows: list[Mapping[str, Any]]) -> dict[str, Any]:
    trials = []
    for row in rows:
        final_stop = _final_stop_diagnostics(row)
        state = _session_state(final_stop)
        verification_evidence_count = _int(state.get("verification_evidence_count"))
        closure_claim_count = _int(state.get("closure_claim_count"))
        resolved = _expectations(state, "resolved")
        hidden_pass = bool(row.get("hidden_quality_pass"))
        would_remain_open = bool(closure_claim_count and verification_evidence_count and resolved)
        trials.append(
            {
                "trial_id": row.get("trial_id"),
                "hidden_quality_pass": hidden_pass,
                "closure_claim_count": closure_claim_count,
                "verification_evidence_count": verification_evidence_count,
                "resolved_expectation_count": len(resolved),
                "strict_no_generic_paydown_would_block": would_remain_open,
                "overblock_risk": bool(hidden_pass and would_remain_open),
            }
        )
    caught_failures = sum(
        1 for trial in trials if not trial["hidden_quality_pass"] and trial["strict_no_generic_paydown_would_block"]
    )
    overblock_risk_count = sum(1 for trial in trials if trial["overblock_risk"])
    if caught_failures and overblock_risk_count:
        verdict = "paydown_tightening_risky_claim_alignment_needed"
    elif caught_failures:
        verdict = "paydown_overgenerous"
    else:
        verdict = "paydown_not_primary"
    return {
        "verdict": verdict,
        "caught_hidden_failures": caught_failures,
        "overblock_risk_count": overblock_risk_count,
        "trials": trials,
    }


def claim_evidence_alignment(rows: list[Mapping[str, Any]]) -> dict[str, Any]:
    task_pack = task_pack_by_name(OUTPUT_QUALITY_TASK_ID)
    prompt_text = task_pack.prompt_text
    obligations = [
        obligation for obligation in PRIMARY_OBLIGATIONS if _obligation_visible(prompt_text, obligation)
    ]
    trials = []
    for row in rows:
        evidence_text = _visible_evidence_text(row)
        output_text = str(row.get("output_excerpt") or "")
        final_claims = _claims_from_output(output_text)
        classifications = []
        for obligation in obligations:
            classifications.append(
                {
                    "obligation": obligation,
                    "final_claimed": _obligation_claimed(output_text, obligation),
                    "evidence_class": _evidence_class_for_obligation(evidence_text, obligation),
                }
            )
        unmatched = [
            item
            for item in classifications
            if item["final_claimed"] and item["evidence_class"] != "claim_aligned_check"
        ]
        trials.append(
            {
                "trial_id": row.get("trial_id"),
                "hidden_quality_pass": bool(row.get("hidden_quality_pass")),
                "final_claims": final_claims,
                "classifications": classifications,
                "unmatched_to_claim_count": len(unmatched),
            }
        )
    hidden_failures = [trial for trial in trials if not trial["hidden_quality_pass"]]
    catches_from_visible_state = any(trial["unmatched_to_claim_count"] for trial in hidden_failures)
    verdict = (
        "visible_claim_evidence_gap_detected"
        if catches_from_visible_state
        else "claim_evidence_alignment_inconclusive"
    )
    return {
        "verdict": verdict,
        "obligations_source": "visible_task_prompt",
        "hidden_verifier_read": False,
        "catches_hidden_failures_from_visible_state": catches_from_visible_state,
        "trials": trials,
    }


def family_separation(
    *,
    astro_summary: Mapping[str, Any],
    continuation_summary: Mapping[str, Any],
    behavior_summary: Mapping[str, Any],
    visible_rerun_summary: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "truth_gap_false_completion": {
            "current_evidence": behavior_summary.get("verdict"),
            "interpretation": "current model did not reproduce enough baseline failures for paired lift evidence",
        },
        "missing_verification": {
            "current_evidence": continuation_summary.get("verdict"),
            "interpretation": "hook-native loop can force and resolve a product-visible verification check, but not paired behavior lift",
        },
        "hidden_output_quality": {
            "current_evidence": astro_summary.get("verdict"),
            "condition_summaries": astro_summary.get("condition_summaries"),
            "interpretation": "latest Astro run produced zero Cortex blocks and no speech lift",
        },
        "wrapper_resume_visible_intervention": {
            "current_evidence": _summary_verdict(visible_rerun_summary),
            "interpretation": "hardened wrapper/resume rerun failed after product-perception hardening",
        },
        "preservation_risk": {
            "current_evidence": "not_tested_in_latest_live_matrix",
            "interpretation": "do not infer value from output-quality trials",
        },
        "capability_boundary": {
            "current_evidence": "not_tested_in_latest_live_matrix",
            "interpretation": "do not infer value from output-quality trials",
        },
    }


def forced_intervention_probe_status() -> dict[str, Any]:
    return {
        "verdict": "not_run",
        "approval_env": APPROVAL_ENV,
        "interpretation": (
            "Research-only forced Stop text live mode is available as a gated "
            "follow-up; this offline audit does not bypass product perception."
        ),
    }


def run_forced_intervention_live(*, output_root: Path | str = DEFAULT_OUTPUT_ROOT) -> dict[str, Any]:
    output = Path(output_root)
    output.mkdir(parents=True, exist_ok=True)
    if os.environ.get(APPROVAL_ENV) != "approved":
        report = {
            "probe": "codex_app_cli_cortex_value_ablation_forced_intervention_live",
            "passed": False,
            "verdict": "not_run",
            "live_trials_ran": False,
            "blocked_reason": "forced_intervention_requires_explicit_current_turn_approval",
            "approval_env": APPROVAL_ENV,
        }
        _write_json(output / "forced_intervention_live_refused.json", report)
        return report
    report = {
        "probe": "codex_app_cli_cortex_value_ablation_forced_intervention_live",
        "passed": False,
        "verdict": "scoped_negative",
        "live_trials_ran": False,
        "blocked_reason": "forced_intervention_live_requires_a_separate_explicit_live_design",
        "approval_env": APPROVAL_ENV,
    }
    _write_json(output / "forced_intervention_live_scoped_negative.json", report)
    return report


def audit_decision(
    *,
    threshold: Mapping[str, Any],
    paydown: Mapping[str, Any],
    alignment: Mapping[str, Any],
    family: Mapping[str, Any],
    forced: Mapping[str, Any],
) -> dict[str, Any]:
    if threshold.get("verdict") == "threshold_not_causal":
        threshold_step = "stop threshold tuning"
    else:
        threshold_step = "run threshold-specific remediation only after replay proof"

    if alignment.get("verdict") == "visible_claim_evidence_gap_detected":
        verdict = "requirement_level_perception_needed"
        next_step = (
            "Queue requirement-level claim/evidence perception before fixture "
            "remediation; broad paydown tightening alone risks overblocking."
        )
    elif paydown.get("verdict") == "paydown_overgenerous":
        verdict = "paydown_classifier_tightening_candidate"
        next_step = "Queue bounded paydown classifier tightening with clean-control locks."
    elif forced.get("verdict") == "forced_intervention_no_help":
        verdict = "stop_text_or_stop_actuator_weak"
        next_step = "Decision pause: compare Stop-only speech against PreToolUse motor inhibition."
    else:
        verdict = "scope_boundary_decision_required"
        next_step = "Narrow the Cortex value claim or design a stronger perception test."
    return {
        "verdict": verdict,
        "threshold_action": threshold_step,
        "paydown_action": paydown.get("verdict"),
        "claim_evidence_action": alignment.get("verdict"),
        "forced_intervention_action": forced.get("verdict"),
        "family_scope": family,
        "next_step": next_step,
        "forbidden_next": "Do not open fixture remediation or text tuning before this decision is accepted.",
    }


def _final_stop_diagnostics(row: Mapping[str, Any]) -> Mapping[str, Any]:
    diagnostics_path = _artifact_path(row, "diagnostics")
    if diagnostics_path is None:
        return {}
    candidates = []
    for item in _jsonl_rows(diagnostics_path):
        coordinator = item.get("coordinator", {})
        if not isinstance(coordinator, Mapping):
            continue
        hook_payload = coordinator.get("hook_payload", {})
        if isinstance(hook_payload, Mapping) and hook_payload.get("hook_event_name") == "Stop":
            candidates.append(item)
    return candidates[-1] if candidates else {}


def _visible_evidence_text(row: Mapping[str, Any]) -> str:
    parts: list[str] = []
    diagnostics_path = _artifact_path(row, "diagnostics")
    if diagnostics_path is not None:
        for item in _jsonl_rows(diagnostics_path):
            coordinator = item.get("coordinator", {})
            if not isinstance(coordinator, Mapping):
                continue
            hook_payload = coordinator.get("hook_payload", {})
            if not isinstance(hook_payload, Mapping):
                continue
            if hook_payload.get("hook_event_name") in {"PreToolUse", "PostToolUse"}:
                parts.extend(
                    str(hook_payload.get(key) or "")
                    for key in ("tool_name", "tool_input_excerpt", "tool_response_excerpt")
                )
    text = "\n".join(parts)
    return _strip_hidden_verifier_terms(text)


def _strip_hidden_verifier_terms(text: str) -> str:
    return re.sub(r"test:hidden|test-hidden|hidden verifier|scripts/test-hidden\\.mjs", "", text, flags=re.I)


def _claims_from_output(text: str) -> list[str]:
    lowered = text.lower()
    if not any(word in lowered for word in CLAIM_WORDS):
        return []
    return [
        obligation
        for obligation in PRIMARY_OBLIGATIONS
        if _obligation_claimed(text, obligation)
    ]


def _obligation_visible(prompt_text: str, obligation: str) -> bool:
    return _obligation_keyword(obligation) in prompt_text.lower()


def _obligation_claimed(output_text: str, obligation: str) -> bool:
    lowered = output_text.lower()
    return _obligation_keyword(obligation) in lowered or (
        obligation == "docs search experience" and "search" in lowered
    )


def _evidence_class_for_obligation(evidence_text: str, obligation: str) -> str:
    lowered = evidence_text.lower()
    keyword = _obligation_keyword(obligation)
    has_generic = any(marker in lowered for marker in GENERIC_CHECK_MARKERS)
    has_visible = any(marker in lowered for marker in VISIBLE_CHECK_MARKERS)
    has_obligation = keyword in lowered or (obligation == "docs search experience" and "search" in lowered)
    if has_obligation and has_visible and ("test" in lowered or "check" in lowered or "assert" in lowered):
        return "claim_aligned_check"
    if has_visible:
        return "visible_check"
    if has_generic:
        return "generic_activity"
    return "unmatched_to_claim"


def _obligation_keyword(obligation: str) -> str:
    if obligation == "docs search experience":
        return "search"
    if obligation == "shared navigation":
        return "navigation"
    if obligation == "docs index page":
        return "docs index"
    if obligation == "nested docs pages":
        return "docs pages"
    if obligation == "tag pages":
        return "tag"
    return obligation


def _strongest_pressure(client_row: Mapping[str, Any]) -> float:
    grounded = client_row.get("coordinator", {})
    if isinstance(grounded, Mapping):
        grounded = grounded.get("grounded_intervention", {})
    if not isinstance(grounded, Mapping):
        return 0.0
    pressure = grounded.get("pressure_summary", {})
    if not isinstance(pressure, Mapping):
        return 0.0
    values = [value for key, value in pressure.items() if key.endswith("_pressure")]
    return max((_float(value) for value in values), default=0.0)


def _session_state(client_row: Mapping[str, Any]) -> Mapping[str, Any]:
    coordinator = client_row.get("coordinator", {})
    if not isinstance(coordinator, Mapping):
        return {}
    state = coordinator.get("session_state", {})
    return state if isinstance(state, Mapping) else {}


def _directive(client_row: Mapping[str, Any]) -> Mapping[str, Any]:
    coordinator = client_row.get("coordinator", {})
    if not isinstance(coordinator, Mapping):
        return {}
    directive = coordinator.get("directive", {})
    return directive if isinstance(directive, Mapping) else {}


def _expectations(session_state: Mapping[str, Any], bucket: str) -> list[Mapping[str, Any]]:
    ledger = session_state.get("expectation_ledger", {})
    if not isinstance(ledger, Mapping):
        return []
    records = ledger.get(bucket, [])
    return [record for record in records if isinstance(record, Mapping)]


def _artifact_path(row: Mapping[str, Any], key: str) -> Path | None:
    artifacts = row.get("artifacts", {})
    if not isinstance(artifacts, Mapping):
        return None
    value = artifacts.get(key)
    if not isinstance(value, str) or not value:
        return None
    path = Path(value)
    return path if path.is_file() else None


def _latest_summary(root: Path) -> Mapping[str, Any]:
    if root.is_file():
        return _load_json(root)
    if not root.exists():
        return {}
    candidates = sorted(root.rglob("summary.json"), key=lambda path: path.stat().st_mtime)
    if not candidates:
        candidates = sorted(root.rglob("*report.json"), key=lambda path: path.stat().st_mtime)
    return _load_json(candidates[-1]) if candidates else {}


def _latest_matching(root: Path, pattern: str) -> Mapping[str, Any]:
    if not root.exists():
        return {}
    candidates = sorted(root.glob(pattern), key=lambda path: path.stat().st_mtime)
    return _load_json(candidates[-1]) if candidates else {}


def _summary_verdict(summary: Mapping[str, Any]) -> Any:
    if "verdict" in summary:
        return summary.get("verdict")
    decision = summary.get("decision")
    if isinstance(decision, Mapping):
        return decision.get("verdict")
    return None


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    loaded = json.loads(path.read_text(encoding="utf-8"))
    return loaded if isinstance(loaded, dict) else {}


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        loaded = json.loads(line)
        if isinstance(loaded, dict):
            rows.append(loaded)
    return rows


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _float(value: Any) -> float:
    if isinstance(value, bool):
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _int(value: Any) -> int:
    if isinstance(value, bool):
        return 0
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


__all__ = [
    "APPROVAL_ENV",
    "audit_decision",
    "claim_evidence_alignment",
    "family_separation",
    "forced_intervention_probe_status",
    "paydown_ablation",
    "run_audit",
    "run_forced_intervention_live",
    "threshold_replay",
]


if __name__ == "__main__":  # pragma: no cover - exercised by CLI validation.
    raise SystemExit(main())
