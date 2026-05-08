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
    EVALUATOR_LIVE_APPROVAL_ENV,
    EVALUATOR_LIVE_APPROVAL_VALUE,
    LAB_PROOF_MODEL_IO_PATH,
    LIVE_MATRIX_REPEAT_COUNT,
    MISSION_OBJECTIVE_REQUIRED_FIELDS,
    SCORE_FIELDS,
    SIMPLE_HOOK_LOC_LIMIT,
    SIMPLE_HOOK_SOURCE_PATH,
    TASK_FAMILIES,
    EvaluatorEpisodeRow,
    evaluate_cortex_effectiveness_rows,
    gate0_synthetic_scenarios,
    mission_contract_errors,
    mission_objective_for_row,
    run_cortex_effectiveness_evaluator_build,
    run_cortex_effectiveness_evaluator_gate0,
    run_cortex_effectiveness_evaluator_live_gate1,
    run_cortex_effectiveness_evaluator_live_matrix,
    run_cortex_simple_hook_baseline_gate0,
)
from lab.cortex_simple_hook_baseline import (
    assess_simple_hook_closure,
    capture_visible_task_standard,
    render_simple_hook_reminder,
)


def _fake_live_matrix_row(
    *,
    plan_row: dict[str, object],
    trial_root: Path,
    model: str,
    mode: str = "active_wins",
) -> EvaluatorEpisodeRow:
    arm = str(plan_row["arm"])
    task_family = str(plan_row["task_family"])
    policy_candidate = str(plan_row["policy_candidate"])
    score_by_arm = {
        "no_cortex_baseline": 0,
        "simple_hook_baseline": 1,
        "cortex_silent_perception": 0,
        "cortex_active_policy": 2,
    }
    if mode == "simple_parity" and arm == "cortex_active_policy":
        score_by_arm[arm] = 1
    if mode == "silent_contamination" and arm == "cortex_silent_perception":
        score_by_arm[arm] = 2
    metrics = {field: False for field in SCORE_FIELDS}
    for field in SCORE_FIELDS[: score_by_arm[arm]]:
        metrics[field] = True
    if mode == "boundary" and arm == "cortex_active_policy":
        metrics["overcontrol"] = True
    metrics.update(
        {
            "model": model,
            "workspace_seed": str(plan_row["workspace_seed"]),
            "model_visible_cortex_output_count": 1
            if arm in {"simple_hook_baseline", "cortex_active_policy"}
            else 0,
            "suppressed_cortex_output_count": 1
            if arm == "cortex_silent_perception"
            else 0,
            "subject_config_product_only": True,
            "runtime_snapshot_loaded": False,
        }
    )
    return EvaluatorEpisodeRow(
        task_family=task_family,
        case_id=str(plan_row["case_id"]),
        repeat_index=int(plan_row["repeat_index"]),
        arm=arm,
        policy_candidate=policy_candidate,
        metrics=metrics,
        source="live_matrix_fake",
        episode_id=str(plan_row["episode_id"]),
        expected_verdict="live_matrix_scored",
        notes=f"trial_root={trial_root}",
        mission_objective=evaluator._live_matrix_mission_objective_for_row(
            arm=arm,
            task_family=task_family,
            policy_candidate=policy_candidate,
        ),
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


def test_live_gate1_registers_approval_gated_dry_run_matrix(tmp_path: Path) -> None:
    report = run_cortex_effectiveness_evaluator_live_gate1(output_root=tmp_path)
    live_plan = json.loads((tmp_path / "live_plan.json").read_text())
    rows = [
        json.loads(line)
        for line in (tmp_path / "episode_table.jsonl").read_text().splitlines()
    ]

    assert report["passed"] is True
    assert report["verdict"] == "pass_cortex_executive_effectiveness_evaluator_live_gate1"
    assert report["live_trials_ran"] is False
    assert report["alphaevolve_mutation_loop_allowed"] is False
    assert report["next_train_if_pass"] == "cortex-simple-hook-baseline-challenger"
    assert live_plan["row_count"] == len(ARMS) * len(TASK_FAMILIES) * LIVE_MATRIX_REPEAT_COUNT
    assert len(rows) == live_plan["row_count"]
    assert set(live_plan["arms"]) == set(ARMS)
    assert set(live_plan["task_families"]) == set(TASK_FAMILIES)
    assert set(DOMINANCE_GATES).issubset(set(live_plan["dominance_gates"]))
    assert live_plan["registered_live_commands"][0]["env"] == {
        EVALUATOR_LIVE_APPROVAL_ENV: EVALUATOR_LIVE_APPROVAL_VALUE
    }
    assert all(
        set(MISSION_OBJECTIVE_REQUIRED_FIELDS).issubset(
            set(row["mission_objective"])
        )
        for row in rows
    )


def test_live_matrix_refuses_without_approval_and_runs_fake_matrix(tmp_path: Path) -> None:
    refused = run_cortex_effectiveness_evaluator_live_matrix(
        output_root=tmp_path / "refused",
        approval_env={},
    )
    approved = run_cortex_effectiveness_evaluator_live_matrix(
        output_root=tmp_path / "approved",
        approval_env={EVALUATOR_LIVE_APPROVAL_ENV: EVALUATOR_LIVE_APPROVAL_VALUE},
        run_id="run_fake",
        row_runner=_fake_live_matrix_row,
    )
    run_root = tmp_path / "approved" / "run_fake"
    rows = [
        json.loads(line)
        for line in (run_root / "episode_table.jsonl").read_text().splitlines()
    ]
    live_plan = json.loads((run_root / "live_plan.json").read_text())

    assert refused["verdict"] == "not_run_approval_required"
    assert refused["live_trials_ran"] is False
    assert refused["approval_env"] == EVALUATOR_LIVE_APPROVAL_ENV
    assert approved["verdict"] == "pass_scoped_cortex_value"
    assert approved["live_trials_ran"] is True
    assert approved["run_id"] == "run_fake"
    assert approved["row_count"] == len(ARMS) * len(TASK_FAMILIES) * LIVE_MATRIX_REPEAT_COUNT
    assert approved["completed_new_rows"] == approved["row_count"]
    assert approved["skipped_existing_rows"] == 0
    assert approved["positive_value_requires_user_review"] is True
    assert approved["next_train_if_recorded"] == "cortex-evolution-program-database"
    assert len(rows) == approved["row_count"]
    assert live_plan["row_count"] == approved["row_count"]
    assert (run_root / "leaderboard.json").exists()
    assert (run_root / "failure_analysis.json").exists()
    assert (run_root / "trials").exists()
    assert all(row["metrics"]["subject_config_product_only"] is True for row in rows)
    assert {
        row["mission_objective"]["model_io_path"]
        for row in rows
        if row["arm"] == "cortex_active_policy"
    } == {
        "codex_hooks_UserPromptSubmit_PostToolUse_Stop_hookSpecificOutput_or_block_stdout"
    }


def test_live_matrix_resume_skips_completed_fake_rows(tmp_path: Path) -> None:
    first = run_cortex_effectiveness_evaluator_live_matrix(
        output_root=tmp_path,
        approval_env={EVALUATOR_LIVE_APPROVAL_ENV: EVALUATOR_LIVE_APPROVAL_VALUE},
        run_id="run_resume",
        row_runner=_fake_live_matrix_row,
    )

    def forbidden_runner(**_: object) -> EvaluatorEpisodeRow:
        raise AssertionError("completed rows should be reused")

    second = run_cortex_effectiveness_evaluator_live_matrix(
        output_root=tmp_path,
        approval_env={EVALUATOR_LIVE_APPROVAL_ENV: EVALUATOR_LIVE_APPROVAL_VALUE},
        run_id="run_resume",
        row_runner=forbidden_runner,
    )

    assert first["row_count"] == second["row_count"]
    assert second["completed_new_rows"] == 0
    assert second["skipped_existing_rows"] == first["row_count"]


def test_live_matrix_plan_pairs_share_prompt_model_repeat_and_seed(tmp_path: Path) -> None:
    report = run_cortex_effectiveness_evaluator_live_matrix(
        output_root=tmp_path,
        approval_env={EVALUATOR_LIVE_APPROVAL_ENV: EVALUATOR_LIVE_APPROVAL_VALUE},
        run_id="run_pairing",
        row_runner=_fake_live_matrix_row,
    )
    plan = json.loads((tmp_path / "run_pairing" / "live_plan.json").read_text())
    groups: dict[tuple[str, int], list[dict[str, object]]] = {}
    for row in plan["rows"]:
        groups.setdefault((row["task_family"], row["repeat_index"]), []).append(row)

    assert report["model"] == "gpt-5.3-codex"
    for rows in groups.values():
        assert {row["arm"] for row in rows} == set(ARMS)
        assert len({row["prompt_hash"] for row in rows}) == 1
        assert len({row["workspace_seed"] for row in rows}) == 1


def test_live_matrix_boundary_and_no_value_verdicts_dominate(tmp_path: Path) -> None:
    simple_parity = run_cortex_effectiveness_evaluator_live_matrix(
        output_root=tmp_path / "simple",
        approval_env={EVALUATOR_LIVE_APPROVAL_ENV: EVALUATOR_LIVE_APPROVAL_VALUE},
        run_id="run_simple",
        row_runner=lambda **kwargs: _fake_live_matrix_row(
            **kwargs,
            mode="simple_parity",
        ),
    )
    silent = run_cortex_effectiveness_evaluator_live_matrix(
        output_root=tmp_path / "silent",
        approval_env={EVALUATOR_LIVE_APPROVAL_ENV: EVALUATOR_LIVE_APPROVAL_VALUE},
        run_id="run_silent",
        row_runner=lambda **kwargs: _fake_live_matrix_row(
            **kwargs,
            mode="silent_contamination",
        ),
    )
    boundary = run_cortex_effectiveness_evaluator_live_matrix(
        output_root=tmp_path / "boundary",
        approval_env={EVALUATOR_LIVE_APPROVAL_ENV: EVALUATOR_LIVE_APPROVAL_VALUE},
        run_id="run_boundary",
        row_runner=lambda **kwargs: _fake_live_matrix_row(
            **kwargs,
            mode="boundary",
        ),
    )

    assert simple_parity["verdict"] == "failure_no_value"
    assert simple_parity["exactness_value_lift_claim_allowed"] is False
    assert silent["verdict"] == "failure_silent_perception_contamination"
    assert boundary["verdict"] == "failure_boundary_dominance"


def test_simple_hook_baseline_module_is_small_independent_and_runnable() -> None:
    source = SIMPLE_HOOK_SOURCE_PATH.read_text(encoding="utf-8")
    loc = sum(
        1
        for line in source.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    )
    standard = capture_visible_task_standard(
        "Create exact_result.txt with alpha beta omega and verify bytes."
    )
    reminder = render_simple_hook_reminder(standard)
    evidence = assess_simple_hook_closure(
        standard,
        "PASS: checked exact_result.txt, content alpha beta omega, bytes=16.",
    )
    blocker = assess_simple_hook_closure(
        standard,
        "Blocked: exact_result.txt does not exist.",
    )
    unsupported = assess_simple_hook_closure(standard, "Done.")

    assert loc <= SIMPLE_HOOK_LOC_LIMIT
    assert "from cortex" not in source
    assert "import cortex" not in source
    assert standard.visible_task.startswith("Create exact_result.txt")
    assert "Before closing" in reminder
    assert "cortex" not in reminder.lower()
    assert evidence.satisfied is True
    assert evidence.evidence_reported is True
    assert blocker.satisfied is True
    assert blocker.blocker_reported is True
    assert unsupported.satisfied is False


def test_simple_hook_baseline_gate0_passes_and_writes_report(tmp_path: Path) -> None:
    report = run_cortex_simple_hook_baseline_gate0(output_root=tmp_path)

    assert report["passed"] is True
    assert report["verdict"] == "pass_cortex_simple_hook_baseline_challenger"
    assert report["model_io_path"] == LAB_PROOF_MODEL_IO_PATH
    assert report["live_trials_ran"] is False
    assert report["alphaevolve_mutation_loop_allowed"] is False
    assert report["next_train_if_pass"] == (
        "cortex-executive-effectiveness-evaluator-live-matrix-run"
    )
    assert report["checks"]["source_under_loc_limit"] is True
    assert report["checks"]["no_cortex_imports"] is True
    assert report["checks"]["simple_hook_arm_registered"] is True
    assert report["checks"]["scoring_logic_unchanged"] is True
    assert (tmp_path / "simple_hook_baseline.json").exists()
    assert (tmp_path / "gate0_report.json").exists()
    assert (tmp_path / "summary.json").exists()


def test_simple_hook_baseline_cli_passes(tmp_path: Path) -> None:
    output_root = tmp_path / "simple_hook"
    result = subprocess.run(
        [
            sys.executable,
            "lab/cortex_effectiveness_evaluator.py",
            "--simple-hook-baseline-gate0",
            "--require-pass",
            "--output-root",
            str(output_root),
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=True,
        text=True,
        capture_output=True,
    )

    assert "pass_cortex_simple_hook_baseline_challenger" in result.stdout
    assert (output_root / "summary.json").exists()


def test_live_gate1_cli_passes_and_live_matrix_cli_refuses(tmp_path: Path) -> None:
    gate_root = tmp_path / "live_gate1"
    gate = subprocess.run(
        [
            sys.executable,
            "lab/cortex_effectiveness_evaluator.py",
            "--live-gate1",
            "--require-pass",
            "--output-root",
            str(gate_root),
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=True,
        text=True,
        capture_output=True,
    )
    refusal = subprocess.run(
        [
            sys.executable,
            "lab/cortex_effectiveness_evaluator.py",
            "--live-matrix",
            "--output-root",
            str(tmp_path / "live_matrix_refusal"),
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=True,
        text=True,
        capture_output=True,
    )

    assert "pass_cortex_executive_effectiveness_evaluator_live_gate1" in gate.stdout
    assert (gate_root / "live_plan.json").exists()
    assert "not_run_approval_required" in refusal.stdout


def test_gate0_source_keeps_alphaevolve_loop_deferred() -> None:
    source = inspect.getsource(evaluator)

    assert "--gate0" in source
    assert "--live-gate1" in source
    assert "--live-matrix" in source
    assert "--simple-hook-baseline-gate0" in source
    assert "alphaevolve_loop_later" in source
    assert "program_database_fields" in source
    assert "candidate_representation" in source
    assert "forbidden_mutation_surfaces" in source
    assert "episode_table.jsonl" in source
    assert "leaderboard.json" in source
