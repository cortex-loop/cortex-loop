"""Deterministic V2 guidance optimization audit artifact."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:  # pragma: no cover - direct script entrypoint support.
    sys.path.insert(0, str(ROOT))

from cortex.sre.guidance import (
    ExecutiveGuidanceContext,
    GuidanceMode,
    render_executive_guidance,
    v2_guidance_denominator_coverage_payload,
)
from lab.live_validation_common import (
    comparator_path,
    ensure_live_validation_dirs,
    now_utc_iso,
    write_json,
)
from lab.v2_behavioral_payoff import (
    PAYOFF_TASK_PACKS,
    PAYOFF_VARIANTS,
    TIER1_PAYOFF_PROVIDERS,
    summarize_causal_payoff,
)
from lab.v2_live_communication_audit import DEFAULT_AUDIT_PATH


DEFAULT_OPTIMIZATION_AUDIT_PATH = comparator_path(
    "v2_guidance_optimization_audit.latest.json"
)


def build_v2_guidance_optimization_audit(
    *,
    directionality_summary_path: Path | None = None,
    communication_audit_path: Path = DEFAULT_AUDIT_PATH,
    provider_names: tuple[str, ...] = TIER1_PAYOFF_PROVIDERS,
) -> dict[str, Any]:
    contexts = _sample_contexts()
    coverage_reports = {
        name: v2_guidance_denominator_coverage_payload(
            context,
            mode=GuidanceMode.COMPRESSED_DYNAMIC,
        )
        for name, context in contexts.items()
    }
    full_lengths = {
        name: len(render_executive_guidance(context, mode=GuidanceMode.FULL))
        for name, context in contexts.items()
    }
    compressed_lengths = {
        name: len(render_executive_guidance(context, mode=GuidanceMode.COMPRESSED_DYNAMIC))
        for name, context in contexts.items()
    }
    communication_audit = _read_json(communication_audit_path)
    directionality_summary = _read_json(
        directionality_summary_path or comparator_path("operator_directionality_summary.json")
    )
    causal_payoff = summarize_causal_payoff(
        {
            "providers": {
                provider: payload
                for provider, payload in (directionality_summary.get("providers") or {}).items()
                if provider in provider_names
            }
        }
    )
    compression_integrity_pass = all(
        not report["missing_row_ids"]
        and report["guidance_burden"]["mode_is_smaller_than_full"] is True
        for report in coverage_reports.values()
    )
    full_communication_non_regression = (
        communication_audit.get("all_hosts_passed") is True
        and set((communication_audit.get("host_results") or {}).keys()) >= {"claude", "codex"}
    )
    return {
        "generated_at": now_utc_iso(),
        "surface": "lab",
        "evidence_role": "watchlist",
        "train": "v2-intervention-policy-tuning",
        "guidance_modes": ["raw", "full", "compressed_dynamic"],
        "default_product_profile": "normal",
        "default_product_guidance_mode": "compressed_dynamic",
        "variant_matrix": list(PAYOFF_VARIANTS),
        "task_packs": list(PAYOFF_TASK_PACKS),
        "provider_scope": list(provider_names),
        "tier1_provider_scope": list(TIER1_PAYOFF_PROVIDERS),
        "support_provider_scope": ["openai"],
        "compression_integrity_pass": compression_integrity_pass,
        "full_communication_non_regression": full_communication_non_regression,
        "causal_payoff_gate": causal_payoff["package_gate"],
        "promotion_gate": causal_payoff["promotion_gate"],
        "research_product_gates": causal_payoff["research_product_gates"],
        "coverage_reports": coverage_reports,
        "guidance_lengths": {
            name: {
                "full_chars": full_lengths[name],
                "compressed_dynamic_chars": compressed_lengths[name],
                "reduction_chars": full_lengths[name] - compressed_lengths[name],
            }
            for name in contexts
        },
        "causal_payoff": causal_payoff,
        "hostile_review": {
            "row_dropped": "failed if any compressed coverage report has missing_row_ids",
            "raw_aux_hidden_memory": "AUX default-zero remains always-on and publication-only is dynamic",
            "single_host_overclaim": "full communication non-regression requires Claude and Codex only and does not claim all-host optimization",
            "codex_cli_gap": "OpenAI app-server evidence remains support evidence unless a separate codex provider run passes on codex exec",
            "audit_transcript_bloat": "compressed_dynamic omits contract_rows and records denominator detail in artifact coverage",
            "adoption_overclaim": "broad product usefulness remains forbidden until human or dogfood-equivalent preference evidence reaches the 2:1 adoption gate",
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 -m lab.v2_guidance_optimization_audit",
        description="Write the deterministic V2 guidance optimization audit artifact.",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OPTIMIZATION_AUDIT_PATH)
    parser.add_argument("--directionality-summary", type=Path, default=None)
    parser.add_argument("--communication-audit", type=Path, default=DEFAULT_AUDIT_PATH)
    parser.add_argument(
        "--provider",
        choices=("claude", "codex", "openai"),
        action="append",
        default=None,
    )
    args = parser.parse_args(argv)

    ensure_live_validation_dirs()
    payload = build_v2_guidance_optimization_audit(
        directionality_summary_path=args.directionality_summary,
        communication_audit_path=args.communication_audit,
        provider_names=tuple(args.provider or TIER1_PAYOFF_PROVIDERS),
    )
    write_json(args.output, payload)
    print(str(args.output))
    return 0 if payload["compression_integrity_pass"] else 1


def _sample_contexts() -> dict[str, ExecutiveGuidanceContext]:
    return {
        "codex_repair": ExecutiveGuidanceContext(
            host_name="codex",
            surface="codex-cli",
            transport_channel="prompt",
            active_track_ref="verified-work:1-paths",
            pending_goal_refs=("repair-target", "verify-test"),
            last_selected_family="check",
            last_brake_state="guarded",
            next_recommended_move="repair",
            last_commitment_result_summary="verification failed on target test",
        ),
        "claude_truth_gap": ExecutiveGuidanceContext(
            host_name="claude",
            surface="claude-cli",
            transport_channel="prompt",
            pending_goal_refs=("preserve-truth-gap",),
            last_selected_family="seek-context",
            next_recommended_move="close truthfully with blockers explicit",
            last_commitment_result_summary="evidence incomplete",
        ),
    }


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
