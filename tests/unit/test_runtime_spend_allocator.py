"""Deterministic tests for the runtime spend allocator."""

from __future__ import annotations

import json
import sys
from pathlib import Path


TOOLS_ROOT = Path(__file__).resolve().parents[2] / "tools"
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

import runtime_spend_allocator as allocator


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_runtime_spend_repo(
    repo_root: Path,
    *,
    zero_lift_env_block: bool = True,
    include_repair_yield_gap: bool = True,
    e23_local_keep: bool = True,
    service_spend_deferred: bool = True,
    publication_blocked: bool = True,
    repeated_plumbing_crash: bool = False,
) -> None:
    conformance_artifact = (
        repo_root
        / ".cortex"
        / "live_validation"
        / "conformance"
        / "run_20260410T000000+0000"
        / "openai_operator_cli"
    )
    conformance_artifact.mkdir(parents=True, exist_ok=True)
    _write_json(
        repo_root / ".cortex" / "live_validation" / "conformance" / "summary.latest.json",
        {
            "product_truth": {"runtime_claim": "openai:service_api"},
            "proving_truth": {"active_default": "openai:operator_cli"},
            "results": [
                {
                    "brain": "openai",
                    "status": "conformant",
                    "artifact_relpath": str(
                        conformance_artifact.relative_to(repo_root)
                    ),
                }
            ],
        },
    )

    output_quality_artifact = (
        repo_root
        / ".cortex"
        / "live_validation"
        / "output_quality"
        / "openai_operator_cli"
        / "run_20260410T000000+0000"
    )
    output_quality_artifact.mkdir(parents=True, exist_ok=True)
    _write_json(
        repo_root / ".cortex" / "live_validation" / "output_quality" / "summary.latest.json",
        {
            "artifact_root": str(output_quality_artifact.relative_to(repo_root)),
            "env_blocked": zero_lift_env_block,
            "provider": "openai",
            "surface": "operator_cli",
            "aggregate_objective_pass_count": {
                "raw": 0,
                "tooling_only": 0,
                "cortex": 0,
            }
            if zero_lift_env_block
            else {"raw": 1, "tooling_only": 1, "cortex": 1},
            "aggregate_hidden_quality_pass_count": {
                "raw": 0,
                "tooling_only": 0,
                "cortex": 0,
            }
            if zero_lift_env_block
            else {"raw": 1, "tooling_only": 1, "cortex": 1},
            "pairwise_summary": {
                "cortex_vs_raw": {
                    "wins": 0 if zero_lift_env_block else 1,
                    "losses": 0,
                    "ties": 5 if zero_lift_env_block else 0,
                },
                "cortex_vs_tooling_only": {
                    "wins": 0 if zero_lift_env_block else 1,
                    "losses": 0,
                    "ties": 5 if zero_lift_env_block else 0,
                },
            },
        },
    )

    if include_repair_yield_gap:
        _write_json(
            repo_root
            / ".cortex"
            / "train_loops"
            / "verified-work-repair-yield-openai"
            / "summary.json",
            {
                "train_name": "verified-work-repair-yield-openai",
                "primary_metric": "successful_failure_to_pass_repairs",
                "final_decision": "escalate",
                "baseline_result": {"repair_opportunities": 0},
            },
        )

    workstream_lines = ["# Cortex v2 Active Workstream", ""]
    if e23_local_keep:
        workstream_lines.append(
            "- treat E23 as a local `keep` on the OpenAI `operator_cli` proving lane while leaving shipping truth unchanged"
        )
    if service_spend_deferred:
        workstream_lines.append(
            "- keep new OpenAI `service_api` spend deferred under the current policy"
        )
    if publication_blocked:
        workstream_lines.append(
            "- publication and reconciliation remain blocked on the local accepted-history line until the accepted history is published"
        )
    if repeated_plumbing_crash:
        workstream_lines.append(
            "- the earlier operator-resume payload-sanitization crash is now repeating and remains an unresolved shared proof-plumbing risk"
        )
    else:
        workstream_lines.append(
            "- the earlier operator-resume payload-sanitization crash did not recur on two fresh direct reruns and currently reads as unreproduced shared proof-plumbing noise"
        )
    workstream_path = (
        repo_root / "docs" / "internal" / "CORTEX_V2_ACTIVE_WORKSTREAM.md"
    )
    workstream_path.parent.mkdir(parents=True, exist_ok=True)
    workstream_path.write_text("\n".join(workstream_lines) + "\n", encoding="utf-8")


def test_recommend_runtime_spend_prefers_real_work_replay_pack_on_current_repo_shape(
    tmp_path: Path,
) -> None:
    _write_runtime_spend_repo(tmp_path)

    recommendation = allocator.recommend_runtime_spend(repo_root=tmp_path)

    assert recommendation.recommended_candidate.spec.slug == "real-work-replay-pack-openai"
    assert recommendation.as_payload()["recommended_train_slug"] == "real-work-replay-pack-openai"
    assert recommendation.as_payload()["runtime_budget"] == 2
    assert "docs/internal/CORTEX_V2_ACTIVE_WORKSTREAM.md" in recommendation.artifact_refs_used


def test_e23_local_keep_blocks_broad_watch_reopen(tmp_path: Path) -> None:
    _write_runtime_spend_repo(tmp_path, e23_local_keep=True)

    recommendation = allocator.recommend_runtime_spend(repo_root=tmp_path)
    blocked = {candidate.spec.slug: candidate for candidate in recommendation.blocked_candidates}

    assert "e23-broad-watch-reopen" in blocked
    assert "do not reopen E23 broad watch surfaces by habit" in blocked[
        "e23-broad-watch-reopen"
    ].blocked_reasons


def test_unreproduced_plumbing_crash_does_not_prefer_plumbing(tmp_path: Path) -> None:
    _write_runtime_spend_repo(
        tmp_path,
        zero_lift_env_block=True,
        include_repair_yield_gap=True,
        repeated_plumbing_crash=False,
    )

    recommendation = allocator.recommend_runtime_spend(repo_root=tmp_path)

    assert recommendation.recommended_candidate.spec.slug != "shared-openai-operator-proof-plumbing"


def test_repeated_plumbing_crash_prefers_shared_operator_proof_plumbing(
    tmp_path: Path,
) -> None:
    _write_runtime_spend_repo(
        tmp_path,
        zero_lift_env_block=False,
        include_repair_yield_gap=False,
        repeated_plumbing_crash=True,
    )

    recommendation = allocator.recommend_runtime_spend(repo_root=tmp_path)

    assert recommendation.recommended_candidate.spec.slug == "shared-openai-operator-proof-plumbing"


def test_service_api_spend_deferral_blocks_service_lane_candidate(tmp_path: Path) -> None:
    _write_runtime_spend_repo(tmp_path, service_spend_deferred=True)

    recommendation = allocator.recommend_runtime_spend(repo_root=tmp_path)
    blocked = {candidate.spec.slug: candidate for candidate in recommendation.blocked_candidates}

    assert blocked["openai-service-api-runtime-train"].consequence == "block"
    assert "service_api spend remains deferred" in blocked[
        "openai-service-api-runtime-train"
    ].blocked_reasons[0]


def test_host_expansion_candidate_stays_blocked_under_current_scope(
    tmp_path: Path,
) -> None:
    _write_runtime_spend_repo(tmp_path)

    recommendation = allocator.recommend_runtime_spend(repo_root=tmp_path)
    blocked = {candidate.spec.slug: candidate for candidate in recommendation.blocked_candidates}

    assert blocked["host-expansion-train"].consequence == "block"
    assert "current product scope remains OpenAI-only" in blocked[
        "host-expansion-train"
    ].reason
