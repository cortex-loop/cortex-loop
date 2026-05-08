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
    TASK_FAMILIES,
    evaluate_cortex_effectiveness_rows,
    gate0_synthetic_scenarios,
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


def test_gate0_source_keeps_alphaevolve_loop_deferred() -> None:
    source = inspect.getsource(evaluator)

    assert "--gate0" in source
    assert "alphaevolve_loop_later" in source
    assert "program_database_fields" in source
    assert "candidate_representation" in source
    assert "forbidden_mutation_surfaces" in source
    assert "episode_table.jsonl" in source
    assert "leaderboard.json" in source
