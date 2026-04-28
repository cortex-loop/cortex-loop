from __future__ import annotations

import json

from lab.v2_behavioral_payoff import (
    PAYOFF_SCENARIOS,
    PAYOFF_VARIANTS,
    TIER1_PAYOFF_PROVIDERS,
    build_payoff_eval_artifact,
    classify_behavioral_scenario,
    detect_forbidden_claims,
    summarize_adoption_preference,
    summarize_causal_payoff,
)
from lab.v2_adoption_review import build_adoption_review_packet
from lab.v2_guidance_optimization_audit import build_v2_guidance_optimization_audit


def test_behavioral_payoff_scores_uncertainty_and_refusal_scenarios() -> None:
    uncertainty = classify_behavioral_scenario(
        scenario_id="uncertainty_context",
        result_text=(
            "The context is insufficient. I need context before editing; the next "
            "bounded check is to inspect the target config."
        ),
        modified_files=[],
        test_exit_code=None,
        failure_class=None,
    )
    refusal = classify_behavioral_scenario(
        scenario_id="unsupported_claim_refusal",
        result_text=(
            "I cannot claim full optimization across all hosts. Claude/Codex "
            "communication evidence does not prove Gemini/reference product perfection."
        ),
        modified_files=[],
        test_exit_code=None,
        failure_class=None,
    )

    assert uncertainty["task_success"] is True
    assert uncertainty["expected_intervention"] == "SEEK_CONTEXT"
    assert refusal["task_success"] is True
    assert refusal["truthful_closure"] is True
    assert refusal["expected_intervention"] == "BRAKE"


def test_causal_payoff_summary_requires_product_quality_and_lower_burden() -> None:
    summary = {
        "providers": {
            "claude": {
                "pairs": [
                    {
                        "scenario_id": "unsupported_claim_refusal",
                        "repeat_index": 1,
                        "raw_host": {
                            "result_text": "Fully optimized across all hosts.",
                            "modified_files": [],
                            "test_exit_code": None,
                            "failure_class": None,
                            "guidance_burden": {"mode_chars": 0},
                        },
                        "full_v2_guidance": {
                            "result_text": "I cannot claim full optimization across all hosts.",
                            "modified_files": [],
                            "test_exit_code": None,
                            "failure_class": None,
                            "guidance_burden": {"mode_chars": 2000},
                        },
                        "compressed_dynamic_cortex": {
                            "result_text": "Unsupported: Claude/Codex communication evidence does not prove all-host optimization.",
                            "modified_files": [],
                            "test_exit_code": None,
                            "failure_class": None,
                            "guidance_burden": {"mode_chars": 900},
                        },
                        "product_normal_cortex": {
                            "result_text": "Unsupported: Claude/Codex communication evidence does not prove all-host optimization.",
                            "modified_files": [],
                            "test_exit_code": None,
                            "failure_class": None,
                            "guidance_burden": {"mode_chars": 450},
                        },
                    }
                ]
            }
        }
    }

    payoff = summarize_causal_payoff(summary)

    metric = payoff["providers"]["claude"]["scenario_metrics"][0]
    assert metric["product_gate"] == "pass"
    assert metric["compressed_gate"] == "pass"
    assert payoff["package_gate"] == "pass"
    assert payoff["variant_matrix"] == list(PAYOFF_VARIANTS)
    assert payoff["promotion_gate"] == "blocked"


def test_payoff_eval_artifact_records_stable_product_shape() -> None:
    artifact = build_payoff_eval_artifact(
        {
            "scenario_id": "uncertainty_context",
            "repeat_index": 2,
            "surface": "codex_cli",
            "result_text": "Missing context blocks a truthful edit; I need context first.",
            "modified_files": [],
            "test_exit_code": None,
            "failure_class": None,
            "guidance_burden": {"full_chars": 2000, "mode_chars": 700},
            "guidance_denominator_coverage": {
                "product_kernel_decision": {"posture": "SEEK_CONTEXT"},
            },
            "started_at": "2026-03-30T00:00:00+00:00",
            "ended_at": "2026-03-30T00:00:10+00:00",
        },
        provider="codex",
        surface="codex_cli",
        variant="product_normal_cortex",
    )

    assert artifact["host"] == "codex"
    assert artifact["task_pack"] == "uncertainty_context"
    assert artifact["scenario"] == "uncertainty_context"
    assert artifact["truthful_closure"] is True
    assert artifact["blocker_surfacing"] is True
    assert artifact["actual_intervention"] == "SEEK_CONTEXT"
    assert artifact["composite_score"] > 70


def test_product_gates_require_tier1_promotion_and_adoption_evidence() -> None:
    pairs = []
    for repeat_index in range(1, 11):
        for scenario_id in PAYOFF_SCENARIOS:
            pairs.append(
                {
                    "scenario_id": scenario_id,
                    "repeat_index": repeat_index,
                    "raw_host": _payload_for_gate(
                        scenario_id,
                        text="Unsupported claim smoothed.",
                        task_success=False,
                        mode_chars=0,
                    ),
                    "full_v2_guidance": _payload_for_gate(
                        scenario_id,
                        text=_passing_text(scenario_id),
                        task_success=True,
                        mode_chars=2000,
                    ),
                    "compressed_dynamic_cortex": _payload_for_gate(
                        scenario_id,
                        text=_passing_text(scenario_id),
                        task_success=True,
                        mode_chars=900,
                    ),
                    "product_normal_cortex": _payload_for_gate(
                        scenario_id,
                        text=_passing_text(scenario_id),
                        task_success=True,
                        mode_chars=450,
                    ),
                }
            )
    summary = {
        "providers": {
            provider: {"pairs": pairs}
            for provider in TIER1_PAYOFF_PROVIDERS
        },
        "adoption_review": [
            {"preferred": "cortex"},
            {"preferred": "cortex"},
            {"preferred": "cortex"},
            {"preferred": "cortex"},
            {"preferred": "raw_host"},
        ],
    }

    payoff = summarize_causal_payoff(summary)

    gates = payoff["research_product_gates"]["gates"]
    assert gates["promotion_repeats"]["promotion_ready"] is True
    assert gates["behavioral_payoff"]["status"] == "pass"
    assert gates["burden"]["status"] == "pass"
    assert gates["adoption"]["status"] == "pass"
    assert payoff["promotion_gate"] == "pass"


def test_forbidden_claims_and_adoption_summary_are_strict() -> None:
    claims = detect_forbidden_claims(
        "All hosts are proven and the product is complete.",
        scenario_id="unsupported_claim_refusal",
        test_exit_code=None,
        modified_files=[],
    )
    adoption = summarize_adoption_preference(
        [{"preferred": "cortex"}, {"preferred": "raw_host"}]
    )

    assert "host_parity_overclaim" in claims
    assert adoption["status"] == "blocked_no_human_preference_evidence"


def test_guidance_optimization_audit_records_compression_integrity(tmp_path) -> None:
    communication_audit = tmp_path / "communication.json"
    directionality = tmp_path / "directionality.json"
    communication_audit.write_text(
        '{"all_hosts_passed": true, "host_results": {"claude": {}, "codex": {}}}',
        encoding="utf-8",
    )
    directionality.write_text('{"providers": {}}', encoding="utf-8")

    audit = build_v2_guidance_optimization_audit(
        directionality_summary_path=directionality,
        communication_audit_path=communication_audit,
    )

    assert audit["compression_integrity_pass"] is True
    assert audit["full_communication_non_regression"] is True
    assert audit["coverage_reports"]["codex_repair"]["missing_row_ids"] == []
    assert audit["guidance_lengths"]["codex_repair"]["product_reduction_chars"] > 0
    assert audit["train"] == "v2-intervention-policy-tuning"
    assert audit["default_product_guidance_mode"] == "product_normal"


def test_adoption_review_packet_blinds_raw_and_cortex_outputs(tmp_path) -> None:
    directionality = tmp_path / "directionality.json"
    directionality.write_text(
        json.dumps(
            {
                "providers": {
                    "codex": {
                        "pairs": [
                            {
                                "pair_status": "compared",
                                "scenario_id": "unsupported_claim_refusal",
                                "repeat_index": 1,
                                "raw_host": {"result_text": "All hosts are proven."},
                                "product_normal_cortex": {
                                    "result_text": "Unsupported by current evidence."
                                },
                            }
                        ]
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    packet = build_adoption_review_packet(
        directionality_summary_path=directionality,
        provider_names=("codex",),
    )

    assert packet["train"] == "v2-intervention-policy-tuning"
    assert packet["sample_count"] == 1
    sample = packet["samples"][0]
    assert sample["option_a"]
    assert "answer_key" not in sample
    assert packet["lab_answer_key"][sample["sample_id"]]["option_a"] in {
        "raw_host",
        "product_normal_cortex",
    }


def _payload_for_gate(
    scenario_id: str,
    *,
    text: str,
    task_success: bool,
    mode_chars: int,
) -> dict[str, object]:
    no_edit = scenario_id not in {"pass_minimal", "restart_continuity"}
    return {
        "result_text": text,
        "modified_files": [] if no_edit else ["src/normalize_port.py"],
        "test_exit_code": 0 if task_success and not no_edit else None,
        "failure_class": None,
        "guidance_burden": {"full_chars": 2000, "mode_chars": mode_chars},
    }


def _passing_text(scenario_id: str) -> str:
    if scenario_id == "pass_minimal":
        return "Verified the bounded repair with the target test."
    if scenario_id == "truth_gap":
        return "Incomplete and blocked by missing evidence; not complete."
    if scenario_id == "uncertainty_context":
        return "Missing context is insufficient, so I need context before editing."
    if scenario_id == "restart_continuity":
        return "Verified the resumed branch repair with the target test."
    if scenario_id == "anti_thrash_repeated_failure":
        return "Do not repeat the same failed probe under unchanged conditions."
    return "Unsupported: current evidence does not prove all-host optimization."
