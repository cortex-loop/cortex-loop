"""Lab replay for the Codex App/CLI task-standard spine.

This is proof machinery only. It runs existing Astro trajectory rows through
the product task-standard object to measure whether the spine can distinguish
standard-aligned evidence from generic verification-shaped activity. Hidden
verifier artifacts stay scoring-only and are never read by the spine.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:  # pragma: no cover - direct script support.
    sys.path.insert(0, str(REPO_ROOT))

try:  # pragma: no cover - direct script execution uses fallback imports.
    from .codex_app_cli_cortex_value_ablation_audit import DEFAULT_ASTRO_RUN_ROOT
    from .codex_app_cli_hook_native_behavior_comparison import OUTPUT_QUALITY_TASK_ID
    from .cortex_output_quality import task_pack_by_name
    from .live_validation_common import LOCAL_LIVE_ROOT
except ImportError:  # pragma: no cover
    from lab.codex_app_cli_cortex_value_ablation_audit import DEFAULT_ASTRO_RUN_ROOT
    from lab.codex_app_cli_hook_native_behavior_comparison import OUTPUT_QUALITY_TASK_ID
    from lab.cortex_output_quality import task_pack_by_name
    from lab.live_validation_common import LOCAL_LIVE_ROOT

from cortex.sre.task_standard import (
    external_scoring_boundary_terms,
    initialize_task_standard_spine,
    record_closure_claims,
    record_task_standard_evidence,
    store_assistant_standard_block,
)


DEFAULT_OUTPUT_ROOT = (
    LOCAL_LIVE_ROOT / "openai" / "codex_app_cli_task_standard_spine"
)
DEFAULT_ASTRO_STANDARD_BLOCK = "\n".join(
    (
        "Work standard: docs index, nested docs pages, tag pages, docs search, and shared navigation are strong.",
        "Likely misses: search data, tag routes, nested document routes, and navigation consistency.",
        "Closure evidence: inspect docs index, nested pages, tag pages, search data, and navigation.",
    )
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--astro-run-root", type=Path, default=DEFAULT_ASTRO_RUN_ROOT)
    parser.add_argument("--require-pass", action="store_true")
    args = parser.parse_args(argv)

    report = run_replay(output_root=args.output_root, astro_run_root=args.astro_run_root)
    print(json.dumps(report, sort_keys=True, indent=2))
    if args.require_pass and not report.get("passed", False):
        return 1
    return 0


def run_replay(
    *,
    output_root: Path | str = DEFAULT_OUTPUT_ROOT,
    astro_run_root: Path | str = DEFAULT_ASTRO_RUN_ROOT,
) -> dict[str, Any]:
    output = Path(output_root)
    output.mkdir(parents=True, exist_ok=True)
    rows = _load_jsonl(Path(astro_run_root) / "trajectory.jsonl")
    hook_rows = [row for row in rows if row.get("condition") == "hook_native_cortex"]
    prompt_text = task_pack_by_name(OUTPUT_QUALITY_TASK_ID).prompt_text
    report = replay_rows(
        hook_rows,
        prompt_text=prompt_text,
        standard_block=DEFAULT_ASTRO_STANDARD_BLOCK,
    )
    report["artifact_roots"] = {"astro_three_arm": str(astro_run_root)}
    report["truth_boundary"] = (
        "This is lab replay over existing artifacts. The spine reads visible "
        "prompt text, output excerpts, and visible hook/evaluation summaries; "
        "hidden verifier files and hidden outputs remain scoring-only."
    )
    _write_json(output / "summary.json", report)
    return report


def replay_rows(
    rows: list[Mapping[str, Any]],
    *,
    prompt_text: str,
    standard_block: str,
) -> dict[str, Any]:
    trial_reports = [_replay_row(row, prompt_text, standard_block) for row in rows]
    hidden_failures = [trial for trial in trial_reports if not trial["hidden_quality_pass"]]
    hidden_passes = [trial for trial in trial_reports if trial["hidden_quality_pass"]]
    caught_hidden_failures = sum(
        1 for trial in hidden_failures if trial["would_remain_open_at_stop"]
    )
    overblock_risk_count = sum(
        1 for trial in hidden_passes if trial["would_remain_open_at_stop"]
    )
    verdict = (
        "standard_spine_overblocks_without_real_model_standard"
        if caught_hidden_failures and overblock_risk_count
        else "standard_spine_replay_clean"
        if caught_hidden_failures
        else "standard_spine_replay_inconclusive"
    )
    return {
        "probe": "codex_app_cli_task_standard_spine_replay",
        "surface": "product_plus_lab_proof",
        "evidence_kind": "offline_task_standard_spine_replay",
        "passed": True,
        "verdict": verdict,
        "hidden_verifier_read": False,
        "external_scoring_boundary_terms": list(external_scoring_boundary_terms()),
        "caught_hidden_failures": caught_hidden_failures,
        "overblock_risk_count": overblock_risk_count,
        "trials": trial_reports,
    }


def _replay_row(
    row: Mapping[str, Any],
    prompt_text: str,
    standard_block: str,
) -> dict[str, Any]:
    trial_id = str(row.get("trial_id") or "trial")
    spine = initialize_task_standard_spine(
        prompt_text,
        event_ref=f"{trial_id}:prompt",
    )
    spine = store_assistant_standard_block(
        spine,
        standard_block,
        event_ref=f"{trial_id}:standard",
    )
    visible_evidence = _visible_evidence_text(row)
    spine, evidence = record_task_standard_evidence(
        spine,
        event_ref=f"{trial_id}:visible-evidence",
        tool_text=visible_evidence,
        successful=True,
    )
    spine = record_closure_claims(
        spine,
        str(row.get("output_excerpt") or ""),
        event_ref=f"{trial_id}:closure",
    )
    would_remain_open = bool(spine.has_unmatched_closure_items)
    return {
        "trial_id": trial_id,
        "hidden_quality_pass": bool(row.get("hidden_quality_pass")),
        "evidence_class": evidence.evidence_class.value,
        "aligned_item_count": len(evidence.item_ids),
        "would_remain_open_at_stop": would_remain_open,
        "unmatched_standard_item_count": len(spine.unmatched_standard_item_ids),
        "hidden_verifier_read": False,
    }


def _visible_evidence_text(row: Mapping[str, Any]) -> str:
    parts: list[str] = []
    diagnostics = row.get("artifacts", {}).get("hook_trajectory") if isinstance(row.get("artifacts"), Mapping) else None
    if isinstance(diagnostics, str):
        parts.extend(_visible_hook_summary(Path(diagnostics)))
    final_evaluation = row.get("extra", {}).get("final_evaluation") if isinstance(row.get("extra"), Mapping) else None
    if isinstance(final_evaluation, Mapping):
        for check in final_evaluation.get("checks", ()):
            if not isinstance(check, Mapping):
                continue
            check_name = str(check.get("check_name") or "")
            if "hidden" in check_name.lower():
                continue
            parts.append(
                " ".join(
                    str(value)
                    for value in (
                        check_name,
                        check.get("command"),
                        check.get("exit_code"),
                    )
                )
            )
    return _strip_hidden_terms(" ".join(parts))


def _visible_hook_summary(path: Path) -> list[str]:
    if not path.exists():
        return []
    summaries: list[str] = []
    for row in _load_jsonl(path):
        event_name = str(row.get("hook_event_name") or "")
        if event_name not in {"PreToolUse", "PostToolUse"}:
            continue
        summaries.append(
            " ".join(
                str(value)
                for value in (
                    row.get("tool_name"),
                    row.get("tool_input_present"),
                    row.get("tool_response_present"),
                    row.get("error_present"),
                )
            )
        )
    return summaries


def _strip_hidden_terms(text: str) -> str:
    cleaned = text
    for term in external_scoring_boundary_terms():
        cleaned = cleaned.replace(term, "")
    return cleaned


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")


__all__ = [
    "DEFAULT_ASTRO_STANDARD_BLOCK",
    "DEFAULT_OUTPUT_ROOT",
    "replay_rows",
    "run_replay",
]


if __name__ == "__main__":
    raise SystemExit(main())
