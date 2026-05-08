"""Lab locks for the Cortex executive effectiveness evaluator Gate 0."""

from __future__ import annotations

import inspect
import json
import subprocess
import sys
from pathlib import Path

from lab import cortex_effectiveness_evaluator as evaluator
from lab.cortex_effectiveness_evaluator import (
    ARMS,
    DOMINANCE_GATES,
    LAB_PROOF_MODEL_IO_PATH,
    MISSION_OBJECTIVE_REQUIRED_FIELDS,
    TASK_FAMILIES,
    EvaluatorEpisodeRow,
    evaluate_cortex_effectiveness_rows,
    gate0_synthetic_scenarios,
    mission_contract_errors,
    mission_objective_for_row,
    run_cortex_effectiveness_evaluator_build,
    run_cortex_effectiveness_evaluator_gate0,
)


def test_gate0_design_registers_hard_objective_and_arms(tmp_path: Path) -> None:
    report = run_cortex_effectiveness_evaluator_gate0(output_root=tmp_path)
    design = json.loads((tmp_path / "evaluator_design.json").read_text())

    assert report["passed"] is True
    assert report["verdict"] == "pass_cortex_executive_effectiveness_evaluator_gate0"
    assert report["live_trials_ran"] is False
    assert report["behavior_lift_claim_allowed"] is False
    assert report["exactness_value_lift_claim_allowed"] is False
    assert report["broad_cortex_lift_claim_allowed"] is False
    assert set(design["arms"]) == set(ARMS)
    assert design["simple_hook_challenger"]["mandatory"] is True
    assert design["simple_hook_challenger"]["target_implementation_loc_max"] <= 500
    assert "cortex/core" in design["simple_hook_challenger"]["independent_of"]
    assert "cortex/sre" in design["simple_hook_challenger"]["independent_of"]
    assert "cortex/aux" in design["simple_hook_challenger"]["independent_of"]
    assert set(TASK_FAMILIES).issubset(set(design["task_families"]))
    assert set(DOMINANCE_GATES).issubset(set(design["dominance_gates"]))
    assert set(MISSION_OBJECTIVE_REQUIRED_FIELDS).issubset(
        set(design["mission_objective_contract"]["required_fields"])
    )
    assert (
        design["mission_objective_contract"]["lab_proof_model_io_path"]
        == LAB_PROOF_MODEL_IO_PATH
    )
    assert design["contraction_obligations"]
    assert (
        design["end_of_part_decision"]["if_pass"]
        == "queue_cortex_executive_effectiveness_evaluator_build"
    )


def test_gate0_decision_refuses_simple_or_silent_parity() -> None:
    scenarios = gate0_synthetic_scenarios()

    simple_parity = evaluate_cortex_effectiveness_rows(
        scenarios["simple_hook_parity_blocks_value"]
    )
    silent_success = evaluate_cortex_effectiveness_rows(
        scenarios["silent_success_is_no_value"]
    )

    assert simple_parity["passed"] is False
    assert simple_parity["verdict"] == "failure_simple_baseline_parity"
    assert silent_success["passed"] is False
    assert silent_success["verdict"] == "failure_silent_perception_contamination"


def test_gate0_dominance_gates_block_value_scoring() -> None:
    scenarios = gate0_synthetic_scenarios()

    for name in (
        "overcontrol_dominates",
        "trace_ambiguity_dominates",
        "root_mutation_dominates",
        "runtime_snapshot_dominates",
        "hidden_verifier_leakage_dominates",
    ):
        result = evaluate_cortex_effectiveness_rows(scenarios[name])
        assert result["passed"] is False
        assert result["verdict"] == "failure_boundary_dominance"


def test_gate0_writes_summary_and_cli_passes(tmp_path: Path) -> None:
    output_root = tmp_path / "cli_gate0"
    result = subprocess.run(
        [
            sys.executable,
            "lab/cortex_effectiveness_evaluator.py",
            "--gate0",
            "--require-pass",
            "--output-root",
            str(output_root),
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=True,
        text=True,
        capture_output=True,
    )

    assert "pass_cortex_executive_effectiveness_evaluator_gate0" in result.stdout
    assert (output_root / "evaluator_design.json").exists()
    assert (output_root / "gate0_report.json").exists()
    assert (output_root / "summary.json").exists()
    summary = json.loads((output_root / "summary.json").read_text())
    assert summary["passed"] is True
    assert summary["next_train_if_pass"] == "cortex-executive-effectiveness-evaluator-build"


def test_build_writes_episode_table_summary_and_leaderboard(tmp_path: Path) -> None:
    report = run_cortex_effectiveness_evaluator_build(output_root=tmp_path)
    rows = [
        json.loads(line)
        for line in (tmp_path / "episode_table.jsonl").read_text().splitlines()
    ]
    leaderboard = json.loads((tmp_path / "leaderboard.json").read_text())

    assert report["passed"] is True
    assert report["verdict"] == "pass_cortex_executive_effectiveness_evaluator_build"
    assert report["live_trials_ran"] is False
    assert report["alphaevolve_mutation_loop_allowed"] is False
    assert report["behavior_lift_claim_allowed"] is False
    assert report["exactness_value_lift_claim_allowed"] is False
    assert (tmp_path / "evaluator_design.json").exists()
    assert (tmp_path / "episode_table.jsonl").exists()
    assert (tmp_path / "summary.json").exists()
    assert (tmp_path / "leaderboard.json").exists()
    assert {row["arm"] for row in rows}.issuperset(set(ARMS))
    assert leaderboard["claim_allowed"]["behavior_lift"] is False
    assert leaderboard["claim_allowed"]["exactness_value_lift"] is False


def test_build_preserves_historical_posttooluse_failure_no_value(tmp_path: Path) -> None:
    report = run_cortex_effectiveness_evaluator_build(output_root=tmp_path)
    rows = [
        json.loads(line)
        for line in (tmp_path / "episode_table.jsonl").read_text().splitlines()
    ]

    assert report["historical_replay"]["artifact"] == (
        "task_standard_posttooluse_paired_value_live_20260508T120907Z"
    )
    assert report["historical_replay"]["registered_verdict"] == "failure_no_value"
    assert report["historical_replay"]["preserved_verdict"] == "failure_no_value"
    assert report["historical_replay"]["preserved"] is True
    assert report["historical_replay"]["counts_as_new_live_run"] is False
    assert any(
        row["source"] == "historical_posttooluse_failure_no_value"
        and row["expected_verdict"] == "failure_no_value"
        for row in rows
    )


def test_build_checks_refuse_value_without_simple_and_silent_controls(tmp_path: Path) -> None:
    report = run_cortex_effectiveness_evaluator_build(output_root=tmp_path)
    checks = report["build_checks"]

    assert checks["all_scoreable_episodes_have_required_arms"] is True
    assert checks["simple_hook_baseline_present"] is True
    assert checks["simple_hook_parity_blocks_value"] is True
    assert checks["silent_success_blocks_value"] is True
    assert checks["dominance_gates_block_value"] is True
    assert checks["mission_objective_contract_registered"] is True
    assert checks["episode_rows_carry_valid_mission_contract"] is True
    assert checks["lab_only_rows_do_not_claim_product_value"] is True


def test_build_rows_carry_lab_proof_mission_contract(tmp_path: Path) -> None:
    report = run_cortex_effectiveness_evaluator_build(output_root=tmp_path)
    rows = [
        json.loads(line)
        for line in (tmp_path / "episode_table.jsonl").read_text().splitlines()
    ]

    assert report["mission_contract_errors"] == []
    for row in rows:
        objective = row["mission_objective"]
        assert set(MISSION_OBJECTIVE_REQUIRED_FIELDS).issubset(set(objective))
        assert objective["model_io_path"] == LAB_PROOF_MODEL_IO_PATH
        assert objective["product_spine"] == []


def test_mission_contract_rejects_missing_fields_and_lab_only_value_claim() -> None:
    valid = mission_objective_for_row(
        arm="cortex_active_policy",
        task_family="exactness_evidence_recovery",
        policy_candidate="posttooluse_stop",
    )
    missing = EvaluatorEpisodeRow(
        task_family="exactness_evidence_recovery",
        case_id="missing_contract",
        repeat_index=1,
        arm="cortex_active_policy",
        policy_candidate="posttooluse_stop",
        metrics={},
        mission_objective={},
    )
    lab_value = EvaluatorEpisodeRow(
        task_family="exactness_evidence_recovery",
        case_id="lab_value",
        repeat_index=1,
        arm="cortex_active_policy",
        policy_candidate="posttooluse_stop",
        metrics={"behavior_lift_claim_allowed": True},
        mission_objective=valid,
    )

    assert any("executive_function missing" in error for error in mission_contract_errors(missing))
    assert any("lab-only row cannot claim" in error for error in mission_contract_errors(lab_value))


def test_product_claim_requires_model_io_path_and_product_spine() -> None:
    base = mission_objective_for_row(
        arm="cortex_active_policy",
        task_family="exactness_evidence_recovery",
        policy_candidate="posttooluse_stop",
    )
    bad_objective = dict(base)
    bad_objective["model_io_path"] = "Codex PostToolUse additionalContext"
    bad_objective["product_spine"] = []
    good_objective = dict(bad_objective)
    good_objective["product_spine"] = [
        "truthful_closure",
        "task_standard_state_law",
        "posttooluse_context_decision",
        "Codex PostToolUse",
        "hookSpecificOutput.additionalContext",
    ]
    bad = EvaluatorEpisodeRow(
        task_family="exactness_evidence_recovery",
        case_id="bad_product",
        repeat_index=1,
        arm="cortex_active_policy",
        policy_candidate="posttooluse_stop",
        metrics={"exactness_value_lift_claim_allowed": True},
        mission_objective=bad_objective,
    )
    good = EvaluatorEpisodeRow(
        task_family="exactness_evidence_recovery",
        case_id="good_product",
        repeat_index=1,
        arm="cortex_active_policy",
        policy_candidate="posttooluse_stop",
        metrics={"exactness_value_lift_claim_allowed": True},
        mission_objective=good_objective,
    )

    assert any("product_spine" in error for error in mission_contract_errors(bad))
    assert mission_contract_errors(good) == ()


def test_build_cli_passes_and_emits_required_artifacts(tmp_path: Path) -> None:
    output_root = tmp_path / "cli_build"
    result = subprocess.run(
        [
            sys.executable,
            "lab/cortex_effectiveness_evaluator.py",
            "--build",
            "--require-pass",
            "--output-root",
            str(output_root),
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=True,
        text=True,
        capture_output=True,
    )

    assert "pass_cortex_executive_effectiveness_evaluator_build" in result.stdout
    assert (output_root / "evaluator_design.json").exists()
    assert (output_root / "episode_table.jsonl").exists()
    assert (output_root / "summary.json").exists()
    assert (output_root / "leaderboard.json").exists()


def test_gate0_source_keeps_alphaevolve_loop_deferred() -> None:
    source = inspect.getsource(evaluator)

    assert "--gate0" in source
    assert "alphaevolve_loop_later" in source
    assert "program_database_fields" in source
    assert "candidate_representation" in source
    assert "forbidden_mutation_surfaces" in source
    assert "episode_table.jsonl" in source
    assert "leaderboard.json" in source
