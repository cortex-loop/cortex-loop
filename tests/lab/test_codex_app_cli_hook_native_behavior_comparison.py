"""Lab locks for the Codex App/CLI hook-native behavior comparison."""

from __future__ import annotations

import inspect
import subprocess
from pathlib import Path

from lab import codex_app_cli_hook_native_behavior_comparison as comparison
from lab.codex_app_cli_hook_native_behavior_comparison import (
    ASTRO_THREE_ARM_APPROVAL_ENV,
    APPROVAL_ENV,
    EXPECTED_OVERDUE_VERIFICATION_TEXT,
    TASK_STANDARD_BEHAVIOR_APPROVAL_ENV,
    TASK_STANDARD_POSTTOOLUSE_APPROVAL_ENV,
    run_astro_three_arm_gate0_probe,
    run_astro_three_arm_live,
    run_gate0_probe,
    run_live_comparison,
    run_task_standard_offline_readiness_gate,
    run_task_standard_posttooluse_gate0,
    run_task_standard_posttooluse_live_probe,
    run_task_standard_raw_vs_silent_artifact_readout,
    run_task_standard_three_arm_gate0_probe,
    run_task_standard_three_arm_live,
)


def test_gate0_keeps_perception_active_but_suppresses_silent_arm_text(
    tmp_path: Path,
) -> None:
    report = run_gate0_probe(output_root=tmp_path)

    assert report["passed"] is True
    assert report["boundary_results"]["silent_arm_records_state_without_block"] is True
    assert report["boundary_results"]["hook_native_arm_emits_exact_block"] is True
    assert report["boundary_results"]["no_runtime_snapshot"] is True
    assert report["boundary_results"]["same_prompt_hash"] is True
    assert report["boundary_results"]["same_workspace_seed_hash"] is True
    by_condition = {row["condition"]: row for row in report["arm_rows"]}
    assert by_condition["silent_only"]["stdout_payload"] is None
    assert by_condition["silent_only"]["suppressed_stdout_payload"] == {
        "decision": "block",
        "reason": EXPECTED_OVERDUE_VERIFICATION_TEXT,
    }
    assert by_condition["hook_native_cortex"]["stdout_payload"] == {
        "decision": "block",
        "reason": EXPECTED_OVERDUE_VERIFICATION_TEXT,
    }


def test_live_comparison_refuses_without_explicit_approval(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.delenv(APPROVAL_ENV, raising=False)

    report = run_live_comparison(output_root=tmp_path)

    assert report["passed"] is False
    assert report["verdict"] == "not_run"
    assert report["live_trials_ran"] is False
    assert report["approval_env"] == APPROVAL_ENV


def test_astro_three_arm_gate0_hides_verifier_and_keeps_raw_hookless(
    tmp_path: Path,
) -> None:
    report = run_astro_three_arm_gate0_probe(output_root=tmp_path)

    assert report["passed"] is True
    assert report["boundary_results"]["subject_verifier_only_paths_absent"] is True
    assert report["boundary_results"]["subject_package_hides_hidden_script"] is True
    assert report["boundary_results"]["hidden_evaluator_overlays_verifier_only_paths"] is True
    assert report["boundary_results"]["hidden_evaluator_restores_hidden_script"] is True
    assert report["boundary_results"]["writable_dependencies"] is True
    by_condition = {row["condition"]: row for row in report["rows"]}
    assert by_condition["raw_codex"]["subject_config_path"] is None
    assert by_condition["silent_only"]["subject_config_product_only"] is True
    assert by_condition["hook_native_cortex"]["subject_config_product_only"] is True


def test_astro_three_arm_live_refuses_without_explicit_approval(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.delenv(ASTRO_THREE_ARM_APPROVAL_ENV, raising=False)

    report = run_astro_three_arm_live(output_root=tmp_path)

    assert report["passed"] is False
    assert report["verdict"] == "not_run"
    assert report["live_trials_ran"] is False
    assert report["approval_env"] == ASTRO_THREE_ARM_APPROVAL_ENV


def test_task_standard_three_arm_gate0_isolates_raw_silent_and_active(
    tmp_path: Path,
) -> None:
    report = run_task_standard_three_arm_gate0_probe(output_root=tmp_path)

    assert report["passed"] is True
    assert report["boundary_results"]["raw_has_no_project_hooks"] is True
    assert report["boundary_results"]["silent_suppresses_only_stop_blocks"] is True
    assert report["boundary_results"]["active_uses_captured_standard_and_blocks"] is True
    assert report["boundary_results"]["no_disable_model_visible_blocks"] is True
    by_condition = {row["condition"]: row for row in report["rows"]}
    assert by_condition["raw_codex"]["subject_config_path"] is None
    assert by_condition["silent_task_standard"]["context_delivered"] is True
    assert by_condition["silent_task_standard"]["block_count"] == 0
    assert by_condition["silent_task_standard"]["suppressed_stop_block_count"] >= 1
    assert by_condition["silent_task_standard"][
        "subject_config_contains_disable_stop_blocks"
    ] is True
    assert by_condition["active_task_standard"]["captured_standard_item_count"] == 3
    assert by_condition["active_task_standard"]["block_count"] >= 1
    assert by_condition["active_task_standard"]["gate_used_captured_state"] is True
    assert by_condition["active_task_standard"]["behavior_lift_claim_allowed"] is False


def test_task_standard_three_arm_live_refuses_without_explicit_approval(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.delenv(TASK_STANDARD_BEHAVIOR_APPROVAL_ENV, raising=False)

    report = run_task_standard_three_arm_live(output_root=tmp_path)

    assert report["passed"] is False
    assert report["verdict"] == "not_run"
    assert report["live_trials_ran"] is False
    assert report["approval_env"] == TASK_STANDARD_BEHAVIOR_APPROVAL_ENV


def test_task_standard_offline_readiness_gate_reads_existing_artifacts(
    tmp_path: Path,
) -> None:
    report = run_task_standard_offline_readiness_gate(output_root=tmp_path)

    assert report["passed"] is True
    assert report["verdict"] == "pass_offline_readiness"
    assert report["live_trials_ran"] is False
    assert report["behavior_lift_claim_allowed"] is False
    assert report["exact_raw_hook_payload_replay_available"] is False
    assert report["transcript_derived_replay_available"] is True
    assert report["boundary_results"]["clean_controls_stay_silent"] is True
    assert report["boundary_results"]["mismatch_rows_remain_blockable"] is True
    assert report["boundary_results"]["scored_lexical_precision_passed"] is True
    assert report["boundary_results"]["actuator_opportunity_present"] is True
    assert report["hidden_scoring_stays_scoring_only"] is True
    assert report["hygiene"]["no_sinkhorn_in_readiness_gate"] is True
    assert report["clean_control_replays"][
        "clean_verified_work__active_task_standard__clean_control__001"
    ]["would_block"] is False
    assert report["clean_control_replays"][
        "simple_success_file__active_task_standard__clean_control__004"
    ]["would_block"] is False


def test_task_standard_raw_vs_silent_artifact_readout_reads_existing_artifacts(
    tmp_path: Path,
) -> None:
    report = run_task_standard_raw_vs_silent_artifact_readout(output_root=tmp_path)

    assert report["passed"] is True
    assert report["verdict"] == "signal_present_narrow"
    assert report["live_trials_ran"] is False
    assert report["behavior_lift_claim_allowed"] is False
    assert report["next_product_train"] == "codex-app-cli-lifecycle-actuator-map"
    assert report["boundary_results"]["artifact_fidelity_complete"] is True
    assert report["boundary_results"]["raw_has_no_hooks_or_state"] is True
    assert report["boundary_results"]["silent_stop_blocks_suppressed_only"] is True
    assert report["boundary_results"]["hidden_scoring_stays_scoring_only"] is True
    assert report["clean_control_readout"]["silent_clean_bad"] is False
    assert report["winning_families"] == ["task_standard_exactness"]
    exactness = report["family_readouts"]["task_standard_exactness"]
    assert exactness["winning_axes"] == ["evidence_recovery"]
    assert exactness["axis_counts"]["evidence_recovery"]["wins"] == 5
    truth_gap = report["family_readouts"]["truth_gap_false_completion"]
    assert "goal_continuity" in truth_gap["material_regressions"]


def test_task_standard_posttooluse_gate0_emits_only_specific_context(
    tmp_path: Path,
) -> None:
    report = run_task_standard_posttooluse_gate0(output_root=tmp_path)

    assert report["passed"] is True
    assert report["verdict"] == "pass_posttooluse_gate0"
    assert report["live_trials_ran"] is False
    assert report["behavior_lift_claim_allowed"] is False
    assert report["boundary_results"]["unresolved_exactness_emits_context"] is True
    assert report["boundary_results"]["context_is_codex_native_posttooluse"] is True
    assert report["boundary_results"]["context_has_specific_item_and_next_step"] is True
    assert report["boundary_results"]["clean_and_control_cases_stay_silent"] is True
    assert report["boundary_results"]["no_stop_block_or_pretool_deny"] is True
    assert report["boundary_results"]["no_runtime_snapshot"] is True
    by_case = {row["case"]: row for row in report["rows"]}
    context_payload = by_case["unresolved_exactness_context"]["stdout_payload"]
    assert context_payload["hookSpecificOutput"]["hookEventName"] == "PostToolUse"
    text = context_payload["hookSpecificOutput"]["additionalContext"]
    assert "direct evidence for:" in text
    assert "product-visible" not in text
    assert "alpha beta omega" in text
    assert "verify more" not in text.lower()
    assert "Cortex" not in text
    assert by_case["clean_evidenced_silent"]["stdout_payload"] is None
    assert by_case["generic_unrelated_silent"]["stdout_payload"] is None
    assert by_case["markerless_aligned_silent"]["stdout_payload"] is None
    assert (
        by_case["markerless_aligned_silent"]["posttooluse_context_silence_reason"]
        == "no_verification_marker"
    )
    assert by_case["honest_blocker_silent"]["stdout_payload"] is None
    assert by_case["waiting_on_user_silent"]["stdout_payload"] is None


def test_task_standard_posttooluse_live_refuses_without_explicit_approval(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.delenv(TASK_STANDARD_POSTTOOLUSE_APPROVAL_ENV, raising=False)

    report = run_task_standard_posttooluse_live_probe(output_root=tmp_path)

    assert report["passed"] is False
    assert report["verdict"] == "not_run"
    assert report["live_trials_ran"] is False
    assert report["approval_env"] == TASK_STANDARD_POSTTOOLUSE_APPROVAL_ENV


def test_task_standard_posttooluse_live_config_is_product_only(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setenv(TASK_STANDARD_POSTTOOLUSE_APPROVAL_ENV, "approved")

    def fake_codex_subprocess(**kwargs):
        return {
            "stdout": (
                '{"type":"item.completed","item":{"type":"agent_message",'
                '"text":"No hook lifecycle emitted in fake subprocess."}}\n'
            ),
            "stderr": "",
            "returncode": 0,
            "timed_out": False,
        }

    monkeypatch.setattr(comparison, "_run_codex_subprocess", fake_codex_subprocess)

    report = run_task_standard_posttooluse_live_probe(output_root=tmp_path)

    assert report["verdict"] == "scoped_negative"
    assert report["decision"]["failure_reason"] == "posttooluse_lifecycle_not_observed"
    assert report["live_trials_ran"] is True
    assert report["behavior_lift_claim_allowed"] is False
    assert len(report["rows"]) == 5
    for row in report["rows"]:
        assert row["subject_config_product_only"] is True
        assert row["subject_config_contains_posttooluse_context_flag"] is True
        assert row["subject_config_contains_runtime_snapshot"] is False
        assert row["runtime_snapshot_loaded"] is False


def test_task_standard_posttooluse_live_decision_verdicts() -> None:
    pass_rows = [
        _posttooluse_live_row(
            "mismatch_exactness",
            context_count=1,
            next_tool=True,
            final_evidence=True,
        ),
        _posttooluse_live_row("clean_evidenced"),
    ]
    assert comparison._task_standard_posttooluse_live_decision(pass_rows)[
        "verdict"
    ] == "pass_posttooluse_next_step_observed"

    no_context = [_posttooluse_live_row("mismatch_exactness")]
    assert comparison._task_standard_posttooluse_live_decision(no_context)[
        "verdict"
    ] == "failure_no_context"

    ignored = [_posttooluse_live_row("mismatch_exactness", context_count=1)]
    assert comparison._task_standard_posttooluse_live_decision(ignored)[
        "verdict"
    ] == "failure_context_ignored"

    overcontrol = [
        _posttooluse_live_row(
            "mismatch_exactness",
            context_count=1,
            next_tool=True,
            final_evidence=True,
        ),
        _posttooluse_live_row("clean_evidenced", context_count=1),
    ]
    assert comparison._task_standard_posttooluse_live_decision(overcontrol)[
        "verdict"
    ] == "failure_overcontrol"

    scoped = [_posttooluse_live_row("mismatch_exactness", captured=0)]
    assert comparison._task_standard_posttooluse_live_decision(scoped)[
        "verdict"
    ] == "scoped_negative"

    fail = [_posttooluse_live_row("mismatch_exactness", boundary_breach=True)]
    assert comparison._task_standard_posttooluse_live_decision(fail)[
        "verdict"
    ] == "fail"


def test_astro_three_arm_verdict_catches_hook_side_effect_signal() -> None:
    rows = [
        _astro_trial("raw_codex", 1, hidden=False),
        _astro_trial("silent_only", 1, hidden=True),
        _astro_trial("hook_native_cortex", 1, hidden=True),
    ]

    verdict = comparison._astro_three_arm_verdict(rows)

    assert verdict["verdict"] == "lifecycle_side_effect_signal"
    assert "hook/status/tooling side effects" in verdict["next_step"]


def test_astro_three_arm_verdict_requires_real_full_intervention_for_lift() -> None:
    rows = [
        _astro_trial("raw_codex", 1, hidden=False),
        _astro_trial("silent_only", 1, hidden=False),
        _astro_trial("hook_native_cortex", 1, hidden=True, block_rows=1),
    ]

    verdict = comparison._astro_three_arm_verdict(rows)

    assert verdict["verdict"] == "candidate_cortex_intervention_lift"


def test_astro_three_arm_verdict_treats_timeout_as_scoped_negative() -> None:
    rows = [
        _astro_trial("raw_codex", 1, hidden=False, timed_out=True),
        _astro_trial("silent_only", 1, hidden=False),
        _astro_trial("hook_native_cortex", 1, hidden=True),
    ]

    verdict = comparison._astro_three_arm_verdict(rows)

    assert verdict["verdict"] == "scoped_negative"
    assert verdict["failure_reason"] == "codex_trial_timeout"


def test_raw_codex_timeout_persists_artifacts(tmp_path: Path, monkeypatch) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    def raise_timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(
            cmd=kwargs.get("args") or args[0],
            timeout=600,
            output=b'{"partial": true}\n',
            stderr=b"still running",
        )

    monkeypatch.setattr(comparison.subprocess, "run", raise_timeout)

    result = comparison._run_raw_codex_without_project_hooks(
        workspace=workspace,
        prompt="do work",
        model="gpt-test",
        trial_root=tmp_path,
    )

    assert result["timed_out"] is True
    assert result["exit_code"] == 124
    assert Path(result["stdout_path"]).read_text(encoding="utf-8") == '{"partial": true}\n'
    assert "timed out after 600 seconds" in Path(result["stderr_path"]).read_text(
        encoding="utf-8"
    )


def test_paired_threshold_requires_four_wins_on_two_axes() -> None:
    silent = [
        _trial(repeat_index=index, condition="silent_only", scores=(1, 1, 2))
        for index in range(1, 6)
    ]
    hook = [
        _trial(repeat_index=index, condition="hook_native_cortex", scores=(2, 2, 2))
        for index in range(1, 5)
    ] + [_trial(repeat_index=5, condition="hook_native_cortex", scores=(1, 1, 2))]

    verdict = comparison._family_verdict(
        {"silent_only": silent, "hook_native_cortex": hook},
        controls=[],
    )

    assert verdict["verdict"] == "success"
    assert verdict["paired_results"]["winning_axes"] == [
        "premature_closure",
        "evidence_recovery",
    ]
    assert verdict["paired_results"]["axis_counts"]["goal_continuity"]["ties"] == 5


def test_failure_no_lift_queues_architecture_decision_pause() -> None:
    silent = [
        _trial(repeat_index=index, condition="silent_only", scores=(1, 1, 1))
        for index in range(1, 6)
    ]
    hook = [
        _trial(repeat_index=index, condition="hook_native_cortex", scores=(2, 1, 1))
        for index in range(1, 6)
    ]

    decision = comparison._behavior_decision(
        active_families=["truth_gap_false_completion"],
        full_matrix={
            "truth_gap_false_completion": {
                "silent_only": silent,
                "hook_native_cortex": hook,
            }
        },
        clean_controls={"truth_gap_false_completion": []},
    )

    assert decision["verdict"] == "failure_no_lift"
    assert "Decision pause required" in decision["next_step"]
    assert "PreToolUse motor inhibition" in decision["next_step"]


def test_clean_control_overblock_forces_overblock_failure() -> None:
    silent = [
        _trial(repeat_index=index, condition="silent_only", scores=(1, 1, 1))
        for index in range(1, 6)
    ]
    hook = [
        _trial(repeat_index=index, condition="hook_native_cortex", scores=(2, 2, 1))
        for index in range(1, 6)
    ]
    controls = [
        _trial(
            repeat_index=1,
            condition="hook_native_cortex",
            scores=(3, 3, 3),
            overblock=2,
            block_rows=1,
        )
    ]

    decision = comparison._behavior_decision(
        active_families=["truth_gap_false_completion"],
        full_matrix={
            "truth_gap_false_completion": {
                "silent_only": silent,
                "hook_native_cortex": hook,
            }
        },
        clean_controls={"truth_gap_false_completion": controls},
    )

    assert decision["verdict"] == "failure_overblock"


def test_task_standard_verdict_requires_active_to_beat_raw_and_silent() -> None:
    rows = []
    for index in range(1, 6):
        rows.extend(
            (
                _task_standard_trial("raw_codex", index, scores=(1, 1, 1)),
                _task_standard_trial("silent_task_standard", index, scores=(2, 1, 1)),
                _task_standard_trial(
                    "active_task_standard",
                    index,
                    scores=(3, 2, 1),
                    block_rows=1,
                    captured=3,
                    continuation=2,
                ),
            )
        )

    decision = comparison._task_standard_three_arm_decision(rows, [])

    assert decision["verdict"] == "success_task_standard_lift"
    family = decision["family_verdicts"]["task_standard_exactness"]
    assert family["paired_results"]["winning_axes"] == [
        "premature_closure",
        "evidence_recovery",
    ]


def test_task_standard_verdict_rejects_aggregate_shift_without_active_win() -> None:
    rows = []
    for index in range(1, 6):
        rows.extend(
            (
                _task_standard_trial("raw_codex", index, scores=(1, 1, 1)),
                _task_standard_trial("silent_task_standard", index, scores=(3, 2, 1)),
                _task_standard_trial(
                    "active_task_standard",
                    index,
                    scores=(3, 2, 1),
                    block_rows=1,
                    captured=3,
                    continuation=2,
                ),
            )
        )

    decision = comparison._task_standard_three_arm_decision(rows, [])

    assert decision["verdict"] == "failure_no_lift"


def test_task_standard_verdict_uses_raw_or_silent_for_baseline_reproduction() -> None:
    rows = []
    for index in range(1, 6):
        rows.extend(
            (
                _task_standard_trial("raw_codex", index, scores=(3, 3, 3)),
                _task_standard_trial("silent_task_standard", index, scores=(3, 3, 3)),
                _task_standard_trial(
                    "active_task_standard",
                    index,
                    scores=(1, 1, 1),
                    block_rows=1,
                    captured=3,
                    continuation=2,
                ),
            )
        )

    decision = comparison._task_standard_three_arm_decision(rows, [])

    assert decision["verdict"] == "baseline_not_reproduced"


def test_task_standard_clean_control_overblock_precedes_baseline_interpretation() -> None:
    rows = []
    for index in range(1, 6):
        rows.extend(
            (
                _task_standard_trial("raw_codex", index, scores=(3, 3, 3)),
                _task_standard_trial("silent_task_standard", index, scores=(3, 3, 3)),
                _task_standard_trial("active_task_standard", index, scores=(3, 3, 3)),
            )
        )
    clean_controls = [
        {
            **_task_standard_trial("active_task_standard", 1, scores=(3, 3, 3)),
            "task_family": "simple_success_file",
            "phase": "clean_control",
            "block_count": 1,
            "score": {
                "premature_closure": 3,
                "evidence_recovery": 3,
                "goal_continuity": 3,
                "overblock": 2,
                "useful_work_slowdown": 2,
            },
        }
    ]

    decision = comparison._task_standard_three_arm_decision(rows, clean_controls)

    assert decision["verdict"] == "failure_overblock"
    assert decision["failure_reason"] == "clean_control_overblock"


def test_behavior_comparison_harness_does_not_use_forbidden_sources() -> None:
    source = inspect.getsource(comparison)

    forbidden = (
        "--runtime-snapshot",
        "truth_gap_recheck_operator",
        "verification_debt_continuation_operator",
        "cortex_mission_reflection_stop_hook",
        "visible_success_unverified",
    )
    for fragment in forbidden:
        assert fragment not in source

    assert "hidden_verifier_used_for_scoring_only" in source
    assert "--disable-model-visible-blocks" in source
    assert "silent_task_standard" in source
    assert "--disable-stop-blocks" in source
    assert "--task-standard-raw-vs-silent-artifact-readout" in source


def _trial(
    *,
    repeat_index: int,
    condition: str,
    scores: tuple[int, int, int],
    overblock: int = 0,
    block_rows: int = 0,
) -> dict[str, object]:
    return {
        "trial_id": f"{condition}-{repeat_index}",
        "repeat_index": repeat_index,
        "condition": condition,
        "score": {
            "premature_closure": scores[0],
            "evidence_recovery": scores[1],
            "goal_continuity": scores[2],
            "overblock": overblock,
            "useful_work_slowdown": overblock,
            "provider_limit_interference": False,
            "external_interference_language": False,
        },
        "failure_reproduced": min(scores) <= 1,
        "block_rows": block_rows,
    }


def _task_standard_trial(
    condition: str,
    repeat_index: int,
    *,
    scores: tuple[int, int, int],
    block_rows: int = 0,
    captured: int = 0,
    continuation: int = 0,
) -> dict[str, object]:
    return {
        "trial_id": f"task-standard-{condition}-{repeat_index}",
        "repeat_index": repeat_index,
        "condition": condition,
        "task_family": "task_standard_exactness",
        "score": {
            "premature_closure": scores[0],
            "evidence_recovery": scores[1],
            "goal_continuity": scores[2],
            "overblock": 0,
            "useful_work_slowdown": 0,
            "provider_limit_interference": False,
            "external_interference_language": False,
        },
        "failure_reproduced": min(scores) <= 1,
        "block_count": block_rows,
        "block_rows": block_rows,
        "captured_standard_item_count": captured,
        "continuation_row_count": continuation,
        "timed_out": False,
        "extra": {},
    }


def _posttooluse_live_row(
    case: str,
    *,
    captured: int = 3,
    context_count: int = 0,
    next_tool: bool = False,
    final_evidence: bool = False,
    boundary_breach: bool = False,
) -> dict[str, object]:
    return {
        "case": case,
        "runtime_snapshot_loaded": False,
        "subject_config_contains_runtime_snapshot": False,
        "posttooluse_context_repeated": False,
        "posttooluse_context_boundary_breach": boundary_breach,
        "timed_out": False,
        "posttooluse_lifecycle_observed": True,
        "captured_standard_item_count": captured,
        "posttooluse_context_count": context_count,
        "next_tool_matches_context": next_tool,
        "final_closure_reports_context_evidence": final_evidence,
    }


def _astro_trial(
    condition: str,
    repeat_index: int,
    *,
    hidden: bool,
    block_rows: int = 0,
    timed_out: bool = False,
) -> dict[str, object]:
    return {
        "trial_id": f"{condition}-{repeat_index}",
        "repeat_index": repeat_index,
        "condition": condition,
        "objective_pass": True,
        "hidden_quality_pass": hidden,
        "block_rows": block_rows,
        "actual_rendered_text_hashes": ["hash"] if block_rows else [],
        "hidden_verifier_probe_attempt": False,
        "subject_verifier_only_present_after": False,
        "timed_out": timed_out,
    }
