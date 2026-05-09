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
    RETAINED_SPINE_LIVE_APPROVAL_ENV,
    EvaluatorEpisodeRow,
    build_retained_spine_executable_live_matrix_plan,
    build_retained_spine_live_gate1_plan,
    build_v2_executable_live_matrix_plan,
    build_v2_live_matrix_plan,
    build_live_matrix_plan,
    evaluate_cortex_effectiveness_rows,
    gate0_synthetic_scenarios,
    mission_contract_errors,
    mission_objective_for_row,
    run_cortex_effectiveness_v2_case_registry_gate0,
    run_cortex_effectiveness_v2_live_matrix,
    run_cortex_effectiveness_v2_live_matrix_gate1,
    run_cortex_effectiveness_measurement_stack_rebuild_gate0,
    run_cortex_effectiveness_evaluator_build,
    run_cortex_effectiveness_evaluator_gate0,
    run_cortex_effectiveness_evaluator_live_gate1,
    run_cortex_effectiveness_evaluator_live_matrix,
    run_cortex_retained_active_policy_spine_gate0,
    run_cortex_retained_active_policy_spine_live_gate1,
    run_cortex_retained_active_policy_spine_live_matrix,
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
    objective_factory = (
        evaluator._retained_spine_mission_objective_for_row
        if policy_candidate == "userpromptsubmit_stop_taskstandard_spine"
        else evaluator._live_matrix_mission_objective_for_row
    )
    expected_verdict = (
        "retained_spine_live_matrix_scored"
        if policy_candidate == "userpromptsubmit_stop_taskstandard_spine"
        else "live_matrix_scored"
    )
    source = (
        "retained_spine_live_matrix_fake"
        if policy_candidate == "userpromptsubmit_stop_taskstandard_spine"
        else "live_matrix_fake"
    )
    return EvaluatorEpisodeRow(
        task_family=task_family,
        case_id=str(plan_row["case_id"]),
        repeat_index=int(plan_row["repeat_index"]),
        arm=arm,
        policy_candidate=policy_candidate,
        metrics=metrics,
        source=source,
        episode_id=str(plan_row["episode_id"]),
        expected_verdict=expected_verdict,
        notes=f"trial_root={trial_root}",
        mission_objective=objective_factory(
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


def test_measurement_stack_rebuild_gate0_preserves_negative_matrix_diagnosis(
    tmp_path: Path,
) -> None:
    report = run_cortex_effectiveness_measurement_stack_rebuild_gate0(
        output_root=tmp_path,
    )
    diagnosis = json.loads((tmp_path / "measurement_diagnosis.json").read_text())
    discriminability = json.loads((tmp_path / "case_discriminability.json").read_text())

    assert report["passed"] is True
    assert (
        report["verdict"]
        == "pass_cortex_effectiveness_measurement_stack_rebuild_gate0"
    )
    assert report["historical_run_id"] == "run_20260508T221352Z"
    assert report["registered_verdict"] == "failure_silent_perception_contamination"
    assert report["preserved_verdict"] == "failure_silent_perception_contamination"
    assert report["live_trials_ran"] is False
    assert report["model_io_path"] == LAB_PROOF_MODEL_IO_PATH
    assert report["behavior_lift_claim_allowed"] is False
    assert report["exactness_value_lift_claim_allowed"] is False
    assert report["broad_cortex_lift_claim_allowed"] is False
    assert report["codex_app_parity_claim_allowed"] is False
    assert report["shipping_promotion_claim_allowed"] is False
    assert report["alphaevolve_mutation_loop_allowed"] is False
    assert report["next_train_if_pass"] == "cortex-effectiveness-v2-case-registry-gate0"
    assert set(diagnosis["loaded_artifacts"]) == {
        "summary.json",
        "leaderboard.json",
        "failure_analysis.json",
        "episode_table.jsonl",
    }
    assert diagnosis["historical_episode_table_row_count"] == 60
    assert diagnosis["claim_boundaries"]["candidate_evolution_allowed"] is False
    baseline_families = {
        row["task_family"] for row in diagnosis["baseline_parity_episodes"]
    }
    assert {
        "exactness_evidence_recovery",
        "truthful_closure",
        "blocker_surfacing",
        "clean_verified_work_control",
    }.issubset(baseline_families)
    assert any(
        row["task_family"] == "continuity_after_interruption"
        and row["repeat_index"] == 1
        for row in diagnosis["silent_contamination_episodes"]
    )
    family = discriminability["family_discriminability"]
    assert family["exactness_evidence_recovery"]["classification"] == "too_easy"
    assert family["truthful_closure"]["classification"] == "too_easy"
    assert family["blocker_surfacing"]["classification"] == "too_easy"
    assert family["clean_verified_work_control"]["classification"] == "control_valid"
    assert (
        family["continuity_after_interruption"]["classification"]
        == "silent_contaminated"
    )
    assert (
        discriminability["v2_measurement_design_proposal"][
            "no_current_v1_live_case_retroactively_rescored"
        ]
        is True
    )
    assert (tmp_path / "measurement_diagnosis.json").exists()
    assert (tmp_path / "case_discriminability.json").exists()
    assert (tmp_path / "gate0_report.json").exists()
    assert (tmp_path / "summary.json").exists()


def test_measurement_stack_rebuild_gate0_fails_missing_historical_artifacts(
    tmp_path: Path,
) -> None:
    report = run_cortex_effectiveness_measurement_stack_rebuild_gate0(
        output_root=tmp_path / "out",
        historical_run_root=tmp_path / "missing_run",
    )

    assert report["passed"] is False
    assert (
        report["verdict"]
        == "failure_cortex_effectiveness_measurement_stack_rebuild_gate0"
    )
    assert report["failure_reason"] == "missing_historical_artifacts"
    assert set(report["missing_historical_artifacts"]) == {
        "summary.json",
        "leaderboard.json",
        "failure_analysis.json",
        "episode_table.jsonl",
    }


def test_measurement_stack_rebuild_gate0_cli_passes(tmp_path: Path) -> None:
    output_root = tmp_path / "measurement_stack"
    result = subprocess.run(
        [
            sys.executable,
            "lab/cortex_effectiveness_evaluator.py",
            "--measurement-stack-rebuild-gate0",
            "--require-pass",
            "--output-root",
            str(output_root),
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=True,
        text=True,
        capture_output=True,
    )

    assert "pass_cortex_effectiveness_measurement_stack_rebuild_gate0" in result.stdout
    assert (output_root / "measurement_diagnosis.json").exists()
    assert (output_root / "case_discriminability.json").exists()
    assert (output_root / "summary.json").exists()


def test_v2_case_registry_gate0_writes_immutable_registry(tmp_path: Path) -> None:
    report = run_cortex_effectiveness_v2_case_registry_gate0(output_root=tmp_path)
    registry = json.loads((tmp_path / "v2_case_registry.json").read_text())

    assert report["passed"] is True
    assert report["verdict"] == "pass_cortex_effectiveness_v2_case_registry_gate0"
    assert report["live_trials_ran"] is False
    assert report["historical_run_id"] == "run_20260508T221352Z"
    assert report["preserved_v1_verdict"] == "failure_silent_perception_contamination"
    assert report["no_v1_live_case_retroactively_rescored"] is True
    assert report["model_io_path"] == LAB_PROOF_MODEL_IO_PATH
    assert report["behavior_lift_claim_allowed"] is False
    assert report["exactness_value_lift_claim_allowed"] is False
    assert report["broad_cortex_lift_claim_allowed"] is False
    assert report["codex_app_parity_claim_allowed"] is False
    assert report["shipping_promotion_claim_allowed"] is False
    assert report["product_progress_claim_allowed"] is False
    assert report["alphaevolve_mutation_loop_allowed"] is False
    assert report["next_train_if_pass"] == "cortex-effectiveness-v2-live-matrix-gate1"
    assert report["validation_errors"] == []
    assert set(report["task_families"]) == set(TASK_FAMILIES)
    assert (tmp_path / "gate0_report.json").exists()
    assert (tmp_path / "summary.json").exists()

    cases = registry["cases"]
    assert len(cases) == len(TASK_FAMILIES)
    assert {case["task_family"] for case in cases} == set(TASK_FAMILIES)
    assert len({case["case_id"] for case in cases}) == len(cases)
    assert all(case["case_id"].endswith("_v2") for case in cases)
    for case in cases:
        assert set(evaluator.V2_CASE_REGISTRY_REQUIRED_FIELDS).issubset(case)
        assert set(MISSION_OBJECTIVE_REQUIRED_FIELDS).issubset(case)
        assert case["model_io_path"] == LAB_PROOF_MODEL_IO_PATH
        assert case["product_spine"] == []
        assert "run_20260508T221352Z" in case["v1_failure_link"]
        assert set(DOMINANCE_GATES).issubset(set(case["dominance_gates"]))

    by_family = {case["task_family"]: case for case in cases}
    assert "post-observation" in by_family["exactness_evidence_recovery"][
        "measurement_rationale"
    ]
    assert "cannot condition" in by_family["exactness_evidence_recovery"][
        "simple_hook_challenge"
    ]
    assert "generic" in by_family["truthful_closure"]["measurement_rationale"]
    assert any(
        "concrete verification evidence" in criterion
        for criterion in by_family["truthful_closure"]["acceptance_criteria"]
    )
    assert "temptation" in by_family["blocker_surfacing"]["measurement_rationale"]
    assert "silent" in by_family["continuity_after_interruption"][
        "silent_contamination_guard"
    ].lower()
    assert "contamination" in by_family["continuity_after_interruption"][
        "silent_contamination_guard"
    ].lower()
    assert any(
        "zero active model-visible intervention" in criterion
        for criterion in by_family["clean_verified_work_control"][
            "acceptance_criteria"
        ]
    )


def test_v2_case_registry_validation_rejects_missing_mission_contract() -> None:
    registry = evaluator.cortex_effectiveness_v2_case_registry()
    del registry["cases"][0]["executive_function"]

    errors = evaluator.validate_cortex_effectiveness_v2_case_registry(registry)

    assert any("executive_function missing" in error for error in errors)


def test_v2_case_registry_cli_passes(tmp_path: Path) -> None:
    output_root = tmp_path / "v2_case_registry"
    result = subprocess.run(
        [
            sys.executable,
            "lab/cortex_effectiveness_evaluator.py",
            "--v2-case-registry-gate0",
            "--require-pass",
            "--output-root",
            str(output_root),
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=True,
        text=True,
        capture_output=True,
    )

    assert "pass_cortex_effectiveness_v2_case_registry_gate0" in result.stdout
    assert (output_root / "v2_case_registry.json").exists()
    assert (output_root / "gate0_report.json").exists()
    assert (output_root / "summary.json").exists()


def test_v2_live_matrix_gate1_writes_dry_run_plan(tmp_path: Path) -> None:
    v1_plan_before = build_live_matrix_plan()
    report = run_cortex_effectiveness_v2_live_matrix_gate1(output_root=tmp_path)
    live_plan = json.loads((tmp_path / "live_plan.json").read_text())
    rows = [
        json.loads(line)
        for line in (tmp_path / "episode_table.jsonl").read_text().splitlines()
    ]
    registry = json.loads((tmp_path / "v2_case_registry.json").read_text())

    assert report["passed"] is True
    assert report["verdict"] == "pass_cortex_effectiveness_v2_live_matrix_gate1"
    assert report["live_trials_ran"] is False
    assert report["model_io_path"] == LAB_PROOF_MODEL_IO_PATH
    assert report["behavior_lift_claim_allowed"] is False
    assert report["exactness_value_lift_claim_allowed"] is False
    assert report["broad_cortex_lift_claim_allowed"] is False
    assert report["codex_app_parity_claim_allowed"] is False
    assert report["shipping_promotion_claim_allowed"] is False
    assert report["product_progress_claim_allowed"] is False
    assert report["alphaevolve_mutation_loop_allowed"] is False
    assert report["next_train_if_pass"] == "cortex-effectiveness-v2-live-matrix-run"
    assert report["registry_validation_errors"] == []
    assert report["mission_contract_errors"] == []
    assert (tmp_path / "evaluator_design.json").exists()
    assert (tmp_path / "leaderboard.json").exists()
    assert (tmp_path / "failure_analysis.json").exists()
    assert (tmp_path / "summary.json").exists()

    assert live_plan["matrix_id"] == "cortex_effectiveness_v2_live_matrix"
    assert live_plan["live_trials_ran"] is False
    assert live_plan["registry_valid"] is True
    assert live_plan["row_count"] == len(ARMS) * len(TASK_FAMILIES) * LIVE_MATRIX_REPEAT_COUNT
    assert len(rows) == live_plan["row_count"]
    assert set(live_plan["arms"]) == set(ARMS)
    assert set(live_plan["task_families"]) == set(TASK_FAMILIES)
    assert set(DOMINANCE_GATES).issubset(set(live_plan["dominance_gates"]))
    assert live_plan["v2_case_registry"]["historical_run_id"] == "run_20260508T221352Z"
    assert (
        live_plan["v2_case_registry"]["preserved_v1_verdict"]
        == "failure_silent_perception_contamination"
    )
    assert live_plan["v2_case_registry"][
        "no_v1_live_case_retroactively_rescored"
    ] is True
    assert live_plan["registered_live_commands"][0]["env"] == {
        EVALUATOR_LIVE_APPROVAL_ENV: EVALUATOR_LIVE_APPROVAL_VALUE
    }
    assert live_plan["approval"]["without_approval_verdict"] == (
        "not_run_approval_required"
    )
    assert live_plan["approval"][
        "future_live_command_registered_not_implemented_here"
    ] is True

    expected_case_ids = {
        "exactness_evidence_recovery_v2",
        "truthful_closure_v2",
        "blocker_surfacing_v2",
        "continuity_after_interruption_v2",
        "clean_verified_work_control_v2",
    }
    assert set(live_plan["case_ids"]) == expected_case_ids
    assert all(row["case_id"] in expected_case_ids for row in rows)
    assert all(row["case_id"].endswith("_v2") for row in rows)
    assert all(row["source"] == "v2_live_gate1_dry_run_plan" for row in rows)
    assert all(row["metrics"]["live_trials_ran"] is False for row in rows)
    assert all(
        set(MISSION_OBJECTIVE_REQUIRED_FIELDS).issubset(
            set(row["mission_objective"])
        )
        for row in rows
    )
    assert not any(evaluator.row_claims_product_value(evaluator._episode_row_from_json(row)) for row in rows)

    plan_groups: dict[tuple[str, int], set[str]] = {}
    for row in live_plan["rows"]:
        key = (row["case_id"], int(row["repeat_index"]))
        plan_groups.setdefault(key, set()).add(row["workspace_seed"])
        assert "registry_hash" in row
        assert row["live_trials_ran"] is False
        assert row["case_materialization_status"] == (
            "not_materialized_gate1_dry_run"
        )
    assert all(len(seeds) == 1 for seeds in plan_groups.values())
    assert all(case["case_id"].endswith("_v2") for case in registry["cases"])
    assert build_live_matrix_plan() == v1_plan_before


def test_v2_live_matrix_plan_reports_invalid_registry_without_rows() -> None:
    registry = evaluator.cortex_effectiveness_v2_case_registry()
    del registry["cases"][0]["case_id"]

    plan = build_v2_live_matrix_plan(registry=registry)

    assert plan["registry_valid"] is False
    assert plan["row_count"] == 0
    assert plan["rows"] == []
    assert plan["v2_case_registry"]["validation_errors"]


def test_v2_live_matrix_gate1_cli_passes(tmp_path: Path) -> None:
    output_root = tmp_path / "v2_live_gate1"
    result = subprocess.run(
        [
            sys.executable,
            "lab/cortex_effectiveness_evaluator.py",
            "--v2-live-matrix-gate1",
            "--require-pass",
            "--output-root",
            str(output_root),
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=True,
        text=True,
        capture_output=True,
    )

    assert "pass_cortex_effectiveness_v2_live_matrix_gate1" in result.stdout
    assert (output_root / "v2_case_registry.json").exists()
    assert (output_root / "live_plan.json").exists()
    assert (output_root / "episode_table.jsonl").exists()
    assert (output_root / "summary.json").exists()


def test_v2_executable_live_matrix_plan_materializes_rows_without_changing_v1() -> None:
    v1_plan_before = build_live_matrix_plan()

    plan = build_v2_executable_live_matrix_plan()

    assert plan["matrix_id"] == "cortex_effectiveness_v2_live_matrix"
    assert plan["executable"] is True
    assert plan["materialization_errors"] == []
    assert plan["row_count"] == len(ARMS) * len(TASK_FAMILIES) * LIVE_MATRIX_REPEAT_COUNT
    assert plan["approval"][
        "future_live_command_registered_not_implemented_here"
    ] is False
    assert all(row["prompt"] for row in plan["rows"])
    assert all(row["prompt_hash"] for row in plan["rows"])
    assert all(row["case_materialization_status"] == "materialized_v2_live_runner" for row in plan["rows"])
    assert all(row["workspace_setup"] for row in plan["rows"])
    assert all(row["verifier"] for row in plan["rows"])
    assert {
        row["mission_objective"]["model_io_path"]
        for row in plan["rows"]
        if row["arm"] == "cortex_active_policy"
    } == {
        "codex_hooks_UserPromptSubmit_PostToolUse_Stop_hookSpecificOutput_or_block_stdout"
    }
    assert build_live_matrix_plan() == v1_plan_before


def test_v2_live_matrix_refuses_without_approval_and_runs_fake_matrix(tmp_path: Path) -> None:
    refused = run_cortex_effectiveness_v2_live_matrix(
        output_root=tmp_path / "refused",
        approval_env={},
    )
    approved = run_cortex_effectiveness_v2_live_matrix(
        output_root=tmp_path / "approved",
        approval_env={EVALUATOR_LIVE_APPROVAL_ENV: EVALUATOR_LIVE_APPROVAL_VALUE},
        run_id="run_v2_fake",
        row_runner=_fake_live_matrix_row,
    )
    run_root = tmp_path / "approved" / "run_v2_fake"
    rows = [
        json.loads(line)
        for line in (run_root / "episode_table.jsonl").read_text().splitlines()
    ]
    live_plan = json.loads((run_root / "live_plan.json").read_text())

    assert refused["verdict"] == "not_run_approval_required"
    assert refused["live_trials_ran"] is False
    assert refused["registered_live_commands"][0]["command"].endswith(
        "--v2-live-matrix"
    )
    assert approved["verdict"] == "pass_scoped_cortex_value"
    assert approved["live_trials_ran"] is True
    assert approved["run_id"] == "run_v2_fake"
    assert approved["row_count"] == len(ARMS) * len(TASK_FAMILIES) * LIVE_MATRIX_REPEAT_COUNT
    assert approved["completed_new_rows"] == approved["row_count"]
    assert approved["skipped_existing_rows"] == 0
    assert approved["positive_value_requires_user_review"] is True
    assert approved["next_train_if_recorded"] == (
        "cortex-effectiveness-v2-value-architecture-decision"
    )
    assert len(rows) == approved["row_count"]
    assert live_plan["executable"] is True
    assert live_plan["row_count"] == approved["row_count"]
    assert (run_root / "v2_case_registry.json").exists()
    assert (run_root / "leaderboard.json").exists()
    assert (run_root / "failure_analysis.json").exists()
    assert all(row["case_id"].endswith("_v2") for row in rows)


def test_v2_live_matrix_resume_skips_completed_fake_rows(tmp_path: Path) -> None:
    first = run_cortex_effectiveness_v2_live_matrix(
        output_root=tmp_path,
        approval_env={EVALUATOR_LIVE_APPROVAL_ENV: EVALUATOR_LIVE_APPROVAL_VALUE},
        run_id="run_v2_resume",
        row_runner=_fake_live_matrix_row,
    )

    def forbidden_runner(**_: object) -> EvaluatorEpisodeRow:
        raise AssertionError("completed rows should be reused")

    second = run_cortex_effectiveness_v2_live_matrix(
        output_root=tmp_path,
        approval_env={EVALUATOR_LIVE_APPROVAL_ENV: EVALUATOR_LIVE_APPROVAL_VALUE},
        run_id="run_v2_resume",
        row_runner=forbidden_runner,
    )

    assert first["row_count"] == second["row_count"]
    assert second["completed_new_rows"] == 0
    assert second["skipped_existing_rows"] == first["row_count"]


def test_v2_live_matrix_cli_refusal_passes(tmp_path: Path) -> None:
    output_root = tmp_path / "v2_live_refusal"
    result = subprocess.run(
        [
            sys.executable,
            "lab/cortex_effectiveness_evaluator.py",
            "--v2-live-matrix",
            "--output-root",
            str(output_root),
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=True,
        text=True,
        capture_output=True,
    )

    assert "not_run_approval_required" in result.stdout
    summary = json.loads((output_root / "summary.json").read_text())
    assert summary["registered_live_commands"][0]["env"] == {
        EVALUATOR_LIVE_APPROVAL_ENV: EVALUATOR_LIVE_APPROVAL_VALUE
    }


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


def test_retained_active_policy_spine_gate0_writes_contract(tmp_path: Path) -> None:
    report = run_cortex_retained_active_policy_spine_gate0(output_root=tmp_path)
    contract = json.loads((tmp_path / "retained_spine_contract.json").read_text())

    assert report["passed"] is True
    assert report["verdict"] == "pass_cortex_retained_active_policy_spine_gate0"
    assert report["model_io_path"] == LAB_PROOF_MODEL_IO_PATH
    assert report["live_trials_ran"] is False
    assert report["retained_spine_id"] == "userpromptsubmit_stop_taskstandard_spine"
    assert set(report["retained_component_ids"]) == {
        "userpromptsubmit_task_standard_formation",
        "stop_closure_continuation_gate",
        "taskstandardspine_state_law",
        "sre_tool_evidence_classifier",
    }
    assert report["checks"]["model_io_paths_named"] is True
    assert report["checks"]["simple_hook_parity_blocks_value"] is True
    assert report["checks"]["posttooluse_role_demoted"] is True
    assert report["checks"]["candidate_evolution_not_allowed"] is True
    assert report["posttooluse_reactivated_as_earned_policy"] is False
    assert report["behavior_lift_claim_allowed"] is False
    assert report["alphaevolve_candidate_evolution_allowed"] is False
    assert report["next_train_if_pass"] == (
        "cortex-retained-active-policy-spine-live-gate1"
    )
    assert contract["seam_model_io_path"] == LAB_PROOF_MODEL_IO_PATH
    assert contract["retained_policy_candidate_for_next_gate"][
        "simple_hook_parity_blocks_value"
    ] is True
    assert contract["retained_policy_candidate_for_next_gate"][
        "candidate_evolution_allowed"
    ] is False
    assert "PostToolUse task-standard context" in str(contract["excluded_surfaces"])
    assert (tmp_path / "gate0_report.json").exists()
    assert (tmp_path / "summary.json").exists()


def test_retained_active_policy_spine_cli_passes(tmp_path: Path) -> None:
    output_root = tmp_path / "retained_spine"
    result = subprocess.run(
        [
            sys.executable,
            "lab/cortex_effectiveness_evaluator.py",
            "--retained-active-policy-spine-gate0",
            "--require-pass",
            "--output-root",
            str(output_root),
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=True,
        text=True,
        capture_output=True,
    )

    assert "pass_cortex_retained_active_policy_spine_gate0" in result.stdout
    assert (output_root / "retained_spine_contract.json").exists()
    assert (output_root / "summary.json").exists()


def test_retained_spine_live_gate1_builds_no_live_dry_run_matrix(
    tmp_path: Path,
) -> None:
    report = run_cortex_retained_active_policy_spine_live_gate1(output_root=tmp_path)
    live_plan = json.loads((tmp_path / "live_plan.json").read_text())
    rows = [
        json.loads(line)
        for line in (tmp_path / "episode_table.jsonl").read_text().splitlines()
    ]

    assert report["passed"] is True
    assert report["verdict"] == "pass_cortex_retained_active_policy_spine_live_gate1"
    assert report["live_trials_ran"] is False
    assert report["model_io_path"] == LAB_PROOF_MODEL_IO_PATH
    assert report["policy_candidate"] == "userpromptsubmit_stop_taskstandard_spine"
    assert report["behavior_lift_claim_allowed"] is False
    assert report["alphaevolve_candidate_evolution_allowed"] is False
    assert report["posttooluse_reactivated_as_earned_policy"] is False
    assert report["next_train_if_pass"] == "cortex-retained-active-policy-spine-live-run"
    assert report["checks"]["active_rows_use_retained_spine_only"] is True
    assert report["checks"]["posttooluse_not_reactivated"] is True
    assert report["checks"]["workspace_seeds_matched_across_arms"] is True
    assert report["checks"]["simple_hook_parity_blocks_value"] is True
    assert report["checks"]["silent_success_blocks_value"] is True
    assert live_plan["row_count"] == len(ARMS) * len(TASK_FAMILIES) * LIVE_MATRIX_REPEAT_COUNT
    assert live_plan["approval"]["env"] == RETAINED_SPINE_LIVE_APPROVAL_ENV
    assert live_plan["approval"]["without_approval_verdict"] == "not_run_approval_required"
    assert live_plan["approval"]["future_live_command_registered_not_implemented_here"] is True
    assert set(live_plan["arms"]) == set(ARMS)
    assert set(live_plan["task_families"]) == set(TASK_FAMILIES)
    assert all(str(case_id).endswith("_v2") for case_id in live_plan["case_ids"])
    assert len(rows) == len(ARMS) * len(TASK_FAMILIES) * LIVE_MATRIX_REPEAT_COUNT
    assert all(
        row["policy_candidate"] == "userpromptsubmit_stop_taskstandard_spine"
        for row in live_plan["rows"]
        if row["arm"] == "cortex_active_policy"
    )
    assert all(
        row["arm_settings"]["enable_posttooluse_task_standard_context"] is False
        for row in live_plan["rows"]
    )
    assert (tmp_path / "retained_spine_contract.json").exists()
    assert (tmp_path / "evaluator_design.json").exists()
    assert (tmp_path / "leaderboard.json").exists()
    assert (tmp_path / "failure_analysis.json").exists()


def test_retained_spine_live_gate1_plan_keeps_pair_seeds_matched() -> None:
    plan = build_retained_spine_live_gate1_plan()

    assert plan["row_count"] == len(ARMS) * len(TASK_FAMILIES) * LIVE_MATRIX_REPEAT_COUNT
    for task_family in TASK_FAMILIES:
        for repeat_index in range(1, LIVE_MATRIX_REPEAT_COUNT + 1):
            seeds = {
                row["workspace_seed"]
                for row in plan["rows"]
                if row["task_family"] == task_family
                and int(row["repeat_index"]) == repeat_index
            }
            assert len(seeds) == 1
    assert all(
        row["policy_candidate"] != "userpromptsubmit_stop_taskstandard_spine"
        for row in plan["rows"]
        if row["arm"] != "cortex_active_policy"
    )


def test_retained_spine_executable_live_matrix_plan_materializes_without_posttooluse() -> None:
    plan = build_retained_spine_executable_live_matrix_plan()

    assert plan["matrix_id"] == "cortex_retained_active_policy_spine_live_matrix"
    assert plan["executable"] is True
    assert plan["materialization_errors"] == []
    assert plan["row_count"] == len(ARMS) * len(TASK_FAMILIES) * LIVE_MATRIX_REPEAT_COUNT
    assert plan["approval"][
        "future_live_command_registered_not_implemented_here"
    ] is False
    assert all(row["prompt"] for row in plan["rows"])
    assert all(row["prompt_hash"] for row in plan["rows"])
    assert all(
        row["case_materialization_status"]
        == "materialized_retained_spine_live_runner"
        for row in plan["rows"]
    )
    assert all(row["workspace_setup"] for row in plan["rows"])
    assert all(row["verifier"] for row in plan["rows"])
    assert all(
        row["arm_settings"]["enable_posttooluse_task_standard_context"] is False
        for row in plan["rows"]
    )
    assert {
        row["mission_objective"]["model_io_path"]
        for row in plan["rows"]
        if row["arm"] == "cortex_active_policy"
    } == {"codex_hooks_UserPromptSubmit_Stop_hookSpecificOutput_or_block_stdout"}
    assert all(
        "posttooluse" not in " ".join(
            row["mission_objective"]["product_spine"]
        ).lower()
        for row in plan["rows"]
        if row["arm"] == "cortex_active_policy"
    )


def test_retained_spine_live_matrix_refuses_without_approval_and_runs_fake_matrix(
    tmp_path: Path,
) -> None:
    refused = run_cortex_retained_active_policy_spine_live_matrix(
        output_root=tmp_path / "refused",
        approval_env={},
    )
    approved = run_cortex_retained_active_policy_spine_live_matrix(
        output_root=tmp_path / "approved",
        approval_env={RETAINED_SPINE_LIVE_APPROVAL_ENV: "approved"},
        run_id="run_retained_fake",
        row_runner=_fake_live_matrix_row,
    )
    run_root = tmp_path / "approved" / "run_retained_fake"
    rows = [
        json.loads(line)
        for line in (run_root / "episode_table.jsonl").read_text().splitlines()
    ]
    live_plan = json.loads((run_root / "live_plan.json").read_text())

    assert refused["verdict"] == "not_run_approval_required"
    assert refused["approval_env"] == RETAINED_SPINE_LIVE_APPROVAL_ENV
    assert refused["live_trials_ran"] is False
    assert approved["verdict"] == "pass_scoped_cortex_value"
    assert approved["live_trials_ran"] is True
    assert approved["run_id"] == "run_retained_fake"
    assert approved["row_count"] == len(ARMS) * len(TASK_FAMILIES) * LIVE_MATRIX_REPEAT_COUNT
    assert approved["completed_new_rows"] == approved["row_count"]
    assert approved["skipped_existing_rows"] == 0
    assert approved["retained_spine_id"] == "userpromptsubmit_stop_taskstandard_spine"
    assert approved["posttooluse_reactivated_as_earned_policy"] is False
    assert approved["positive_value_requires_user_review"] is True
    assert approved["next_train_if_recorded"] == (
        "cortex-retained-active-policy-value-architecture-decision"
    )
    assert len(rows) == approved["row_count"]
    assert live_plan["executable"] is True
    assert live_plan["row_count"] == approved["row_count"]
    assert all(row["case_id"].endswith("_v2") for row in rows)
    assert all(
        row["policy_candidate"] == "userpromptsubmit_stop_taskstandard_spine"
        for row in rows
        if row["arm"] == "cortex_active_policy"
    )
    assert all(
        row["metrics"].get("subject_config_contains_posttooluse_context_flag")
        is not True
        for row in rows
    )
    assert (run_root / "retained_spine_contract.json").exists()
    assert (run_root / "v2_case_registry.json").exists()
    assert (run_root / "leaderboard.json").exists()
    assert (run_root / "failure_analysis.json").exists()


def test_retained_spine_live_matrix_resume_skips_completed_fake_rows(
    tmp_path: Path,
) -> None:
    first = run_cortex_retained_active_policy_spine_live_matrix(
        output_root=tmp_path,
        approval_env={RETAINED_SPINE_LIVE_APPROVAL_ENV: "approved"},
        run_id="run_retained_resume",
        row_runner=_fake_live_matrix_row,
    )

    def forbidden_runner(**_: object) -> EvaluatorEpisodeRow:
        raise AssertionError("completed retained-spine rows should be reused")

    second = run_cortex_retained_active_policy_spine_live_matrix(
        output_root=tmp_path,
        approval_env={RETAINED_SPINE_LIVE_APPROVAL_ENV: "approved"},
        run_id="run_retained_resume",
        row_runner=forbidden_runner,
    )

    assert first["row_count"] == second["row_count"]
    assert second["completed_new_rows"] == 0
    assert second["skipped_existing_rows"] == first["row_count"]


def test_retained_spine_live_gate1_cli_passes_and_live_matrix_cli_refuses(
    tmp_path: Path,
) -> None:
    gate_root = tmp_path / "retained_spine_live_gate1"
    gate = subprocess.run(
        [
            sys.executable,
            "lab/cortex_effectiveness_evaluator.py",
            "--retained-spine-live-gate1",
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
            "--retained-spine-live-matrix",
            "--output-root",
            str(tmp_path / "retained_spine_live_matrix_refusal"),
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=True,
        text=True,
        capture_output=True,
    )

    assert "pass_cortex_retained_active_policy_spine_live_gate1" in gate.stdout
    assert (gate_root / "live_plan.json").exists()
    assert "not_run_approval_required" in refusal.stdout


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
    assert "--measurement-stack-rebuild-gate0" in source
    assert "--v2-case-registry-gate0" in source
    assert "--v2-live-matrix-gate1" in source
    assert "--retained-active-policy-spine-gate0" in source
    assert "--retained-spine-live-gate1" in source
    assert "--retained-spine-live-matrix" in source
    assert "alphaevolve_loop_later" in source
    assert "program_database_fields" in source
    assert "candidate_representation" in source
    assert "forbidden_mutation_surfaces" in source
    assert "episode_table.jsonl" in source
    assert "leaderboard.json" in source
