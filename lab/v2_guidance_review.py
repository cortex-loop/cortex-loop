"""Strict review evidence for Cortex v2 model-visible guidance."""

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
    GUIDANCE_MARKER,
    assert_status_bio_to_code_coverage,
    v2_guidance_inventory_payload,
)
from internal.truth.status import STATUS_SOURCE
from lab.agent_loop_guard import LOOP_GUARD_ROOT
from lab.live_validation_common import now_utc_iso, write_json

DEFAULT_REVIEW_PATH = LOOP_GUARD_ROOT / "v2_guidance_review.latest.json"


def build_v2_guidance_review() -> dict[str, Any]:
    status_payload = json.loads(STATUS_SOURCE.read_text(encoding="utf-8"))
    assert_status_bio_to_code_coverage(status_payload)
    inventory_rows = v2_guidance_inventory_payload()
    row_ids = {row["row_id"] for row in inventory_rows}
    _assert_required_rows(row_ids)
    return {
        "surface": "lab",
        "evidence_role": "watchlist",
        "generated_at": now_utc_iso(),
        "guidance_marker": GUIDANCE_MARKER,
        "packet_sources": [
            "docs/CORTEX_V2_CORE_2.md",
            "docs/CORTEX_V2_SRE_2.md",
            "docs/CORTEX_V2_AUX_2.md",
            "internal/truth/cortex_status.json",
        ],
        "inventory_rows": inventory_rows,
        "coverage": {
            "core": _row_ids_with_prefix(row_ids, "core."),
            "shared_runtime": _row_ids_with_prefix(row_ids, "runtime."),
            "sre": _row_ids_with_prefix(row_ids, "sre."),
            "host": _row_ids_with_prefix(row_ids, "host."),
            "aux": _row_ids_with_prefix(row_ids, "aux."),
            "operational": _row_ids_with_prefix(row_ids, "operational."),
            "negative": _row_ids_with_prefix(row_ids, "negative."),
        },
        "model_visible_evidence": {
            "claude_system_channel": {
                "code": "cortex/hosts/claude/host_control.py::_request_with_model_visible_guidance",
                "tests": [
                    "tests/conformance/test_claude_host_control.py::test_claude_host_control_injects_v2_guidance_into_model_visible_system_channel",
                    "tests/lab/test_live_validation_tools.py::test_claude_live_task_prompt_carries_v2_guidance",
                ],
            },
            "codex_prompt_or_instructions": {
                "code": [
                    "cortex/hosts/openai/host_control.py::_request_with_model_visible_guidance",
                    "lab/live_host_native_product_paths.py::_run_codex_task",
                ],
                "tests": [
                    "tests/product/test_openai_host_control.py::test_openai_host_control_injects_v2_guidance_into_model_visible_instructions_channel",
                    "tests/lab/test_live_validation_tools.py::test_codex_live_task_prompt_carries_v2_guidance",
                ],
            },
        },
        "hostile_reviewer_critiques": [
            {
                "critique": "calculated-but-not-communicated",
                "answer": (
                    "The guidance is appended before outbound transport through Claude "
                    "system text, OpenAI/Codex instructions, and Claude/Codex CLI prompts."
                ),
                "status": "answered-by-fixture",
            },
            {
                "critique": "one-file-only",
                "answer": (
                    "The proof crosses typed SRE contract, Claude host control, OpenAI/Codex "
                    "host control, lab CLI prompt wrapping, product tests, conformance tests, "
                    "and lab fixture tests."
                ),
                "status": "answered-by-code-refs",
            },
            {
                "critique": "diagnostics-only",
                "answer": (
                    "The captured request/prompt tests assert the guidance is present in "
                    "model-facing system, instructions, or prompt text before the model turn."
                ),
                "status": "answered-by-fixture",
            },
            {
                "critique": "raw-aux-or-hidden-memory",
                "answer": (
                    "AUX rows tell the model that AUX is default-zero and publication-only; "
                    "the contract does not read raw support memory."
                ),
                "status": "answered-by-negative-row",
            },
            {
                "critique": "v3-successor-overclaim",
                "answer": (
                    "The negative row forbids treating v3 successor work as V2 communication "
                    "proof; this report is generated from active V2 code and status truth."
                ),
                "status": "answered-by-negative-row",
            },
            {
                "critique": "live-proof-overclaim",
                "answer": (
                    "Live Claude/Codex service-lane proof is not marked pass here; it remains "
                    "blocked unless no-spend evidence or explicit spend approval exists."
                ),
                "status": "blocked-not-overclaimed",
            },
        ],
        "live_watchlist_status": {
            "claude_live_watchlist_evidence": "blocked_without_explicit_spend_or_no_spend_transcript",
            "codex_live_watchlist_evidence": "blocked_without_explicit_spend_or_no_spend_transcript",
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python3 -m lab.v2_guidance_review",
        description="Render strict Cortex v2 guidance inventory/review evidence.",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_REVIEW_PATH)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    report = build_v2_guidance_review()
    if args.check:
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    write_json(args.output, report)
    print(str(args.output))
    return 0


def _assert_required_rows(row_ids: set[str]) -> None:
    required = {
        "core.lifecycle_dispatch",
        "core.commitment_certification",
        "core.environment_degradation",
        "runtime.verified_work_repair",
        "sre.family_policy",
        "sre.uncertainty_brake",
        "sre.branch_continuity",
        "sre.intervention_pricing",
        "sre.blocker_goal_debt",
        "sre.anti_thrash_probe",
        "host.claude_cli",
        "host.codex_cli",
        "host.gemini_reference_conformance",
        "aux.default_zero_removable",
        "aux.publication_only",
        "operational.truth_distinctions",
        "negative.forbidden_shortcuts",
    }
    missing = sorted(required - row_ids)
    if missing:
        raise RuntimeError("missing V2 guidance rows: " + ", ".join(missing))


def _row_ids_with_prefix(row_ids: set[str], prefix: str) -> list[str]:
    return sorted(row_id for row_id in row_ids if row_id.startswith(prefix))


if __name__ == "__main__":
    raise SystemExit(main())
