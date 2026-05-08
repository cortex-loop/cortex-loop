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
    TASK_STANDARD_POSTTOOLUSE_VALUE_APPROVAL_ENV,
    run_astro_three_arm_gate0_probe,
    run_astro_three_arm_live,
    run_gate0_probe,
    run_live_comparison,
    run_task_standard_offline_readiness_gate,
    run_task_standard_posttooluse_context_loop_trace_gate0,
    run_task_standard_posttooluse_exactness_only_paired_value_gate0,
    run_task_standard_posttooluse_final_closure_readout_gate0,
    run_task_standard_posttooluse_firing_boundary_gate0,
    run_task_standard_posttooluse_actuator_trace_gate0,
    run_task_standard_posttooluse_phase_aware_gate0,
    run_task_standard_posttooluse_gate0,
    run_task_standard_posttooluse_live_probe,
    run_task_standard_posttooluse_measurement_stack_gate0,
    run_task_standard_posttooluse_overcontrol_gate0,
    run_task_standard_posttooluse_shared_tool_evidence_gate0,
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


def test_task_standard_posttooluse_phase_aware_gate0_waits_for_candidate(
    tmp_path: Path,
) -> None:
    report = run_task_standard_posttooluse_phase_aware_gate0(output_root=tmp_path)

    assert report["passed"] is True
    assert report["verdict"] == "pass_posttooluse_phase_aware_gate0"
    assert report["live_trials_ran"] is False
    assert report["behavior_lift_claim_allowed"] is False
    assert report["boundary_results"]["pre_artifact_check_stays_silent"] is True
    assert report["boundary_results"]["candidate_artifact_emits_context"] is True
    assert (
        report["boundary_results"]["candidate_context_targets_unresolved_evidence"]
        is True
    )
    assert report["boundary_results"]["clean_and_control_cases_stay_silent"] is True
    assert report["boundary_results"]["markerless_literal_is_not_candidate_artifact"] is True
    assert report["boundary_results"]["no_stop_block_or_pretool_deny"] is True
    by_case = {row["case"]: row for row in report["rows"]}
    assert by_case["pre_artifact_missing_silent"]["stdout_payload"] is None
    assert (
        by_case["pre_artifact_missing_silent"][
            "posttooluse_context_silence_reason"
        ]
        == "pre_artifact_candidate_missing"
    )
    context_payload = by_case["candidate_artifact_context"]["stdout_payload"]
    assert context_payload["hookSpecificOutput"]["hookEventName"] == "PostToolUse"
    text = context_payload["hookSpecificOutput"]["additionalContext"]
    assert "wc -l exact_result.txt" in text
    assert "cat -A exact_result.txt" in text
    assert "product-visible" not in text
    assert "verify more" not in text.lower()
    assert "Cortex" not in text


def test_task_standard_posttooluse_firing_boundary_gate0_accepts_live_equivalent_payloads(
    tmp_path: Path,
) -> None:
    report = run_task_standard_posttooluse_firing_boundary_gate0(output_root=tmp_path)

    assert report["passed"] is True
    assert report["verdict"] == "pass_posttooluse_firing_boundary_gate0"
    assert report["live_trials_ran"] is False
    assert report["behavior_lift_claim_allowed"] is False
    assert report["next_product_train"] == (
        "codex-app-cli-posttooluse-task-standard-phase-aware-narrow-live-rerun"
    )
    assert report["boundary_results"]["pre_artifact_check_stays_silent"] is True
    assert (
        report["boundary_results"][
            "live_equivalent_candidate_artifact_emits_context"
        ]
        is True
    )
    assert (
        report["boundary_results"][
            "live_equivalent_readback_emits_context_without_status_marker"
        ]
        is True
    )
    assert report["boundary_results"]["successful_contexts_target_unresolved_evidence"]
    assert report["boundary_results"]["clean_and_control_cases_stay_silent"] is True
    assert report["boundary_results"]["marker_miss_is_private"] is True
    assert report["boundary_results"]["failed_candidate_stays_silent"] is True
    assert report["boundary_results"]["no_stop_block_or_pretool_deny"] is True
    by_case = {row["case"]: row for row in report["rows"]}
    assert (
        by_case["live_equivalent_pre_artifact_missing_silent"][
            "posttooluse_context_silence_reason"
        ]
        == "pre_artifact_candidate_missing"
    )
    assert (
        by_case["markerless_aligned_silent"][
            "posttooluse_context_silence_reason"
        ]
        == "no_verification_marker"
    )
    context_payload = by_case["live_equivalent_candidate_artifact_context"][
        "stdout_payload"
    ]
    text = context_payload["hookSpecificOutput"]["additionalContext"]
    assert "direct evidence for:" in text
    assert "product-visible" not in text
    assert "verify more" not in text.lower()


def test_task_standard_posttooluse_overcontrol_gate0_keeps_failed_clean_check_silent(
    tmp_path: Path,
) -> None:
    report = run_task_standard_posttooluse_overcontrol_gate0(output_root=tmp_path)

    assert report["passed"] is True
    assert report["verdict"] == "pass_posttooluse_overcontrol_gate0"
    assert report["live_trials_ran"] is False
    assert report["behavior_lift_claim_allowed"] is False
    assert report["next_product_train"] == (
        "codex-app-cli-posttooluse-task-standard-phase-aware-narrow-live-rerun"
    )
    assert (
        report["boundary_results"]["live_equivalent_failed_check_stays_silent"]
        is True
    )
    assert report["boundary_results"]["mismatch_candidate_still_emits_context"] is True
    assert report["boundary_results"]["mismatch_readback_still_emits_context"] is True
    assert report["boundary_results"]["clean_and_control_cases_stay_silent"] is True
    assert report["boundary_results"]["pre_artifact_check_stays_silent"] is True
    assert report["boundary_results"]["marker_miss_is_private"] is True
    assert report["boundary_results"]["failed_candidate_stays_silent"] is True
    assert report["boundary_results"]["no_stop_block_or_pretool_deny"] is True
    by_case = {row["case"]: row for row in report["rows"]}
    failed_check = by_case["live_equivalent_clean_failed_check_silent"]
    assert failed_check["stdout_payload"] is None
    assert failed_check["posttooluse_context_silence_reason"] == "phase_check_failed"
    candidate_payload = by_case["live_equivalent_candidate_artifact_context"][
        "stdout_payload"
    ]
    assert candidate_payload["hookSpecificOutput"]["hookEventName"] == "PostToolUse"
    assert "direct evidence for:" in candidate_payload["hookSpecificOutput"][
        "additionalContext"
    ]


def test_task_standard_posttooluse_actuator_trace_gate0_uses_hook_chronology(
    tmp_path: Path,
) -> None:
    report = run_task_standard_posttooluse_actuator_trace_gate0(output_root=tmp_path)

    assert report["passed"] is True
    assert report["verdict"] == "pass_posttooluse_actuator_trace_gate0"
    assert report["live_trials_ran"] is False
    assert report["behavior_lift_claim_allowed"] is False
    assert report["next_product_train"] == (
        "codex-app-cli-posttooluse-task-standard-phase-aware-narrow-live-rerun"
    )
    boundary_results = report["boundary_results"]
    assert boundary_results["live_equivalent_failed_check_stays_silent"] is True
    assert boundary_results["mismatch_candidate_still_emits_context"] is True
    assert boundary_results["event_ref_trace_non_ambiguous"] is True
    assert boundary_results["event_ref_join_source"] is True
    assert boundary_results["trace_uses_context_row_chronology"] is True
    assert boundary_results["preceding_tool_is_context_source"] is True
    assert boundary_results["next_tool_is_strictly_after_context"] is True
    assert boundary_results["historical_trace_marked_ambiguous_without_event_ref"] is True
    assert boundary_results["historical_trace_does_not_infer_by_position"] is True
    trace = report["event_ref_trace"]["trace"]
    assert "printf 'alpha beta omega' > exact_result.txt" in trace["preceding_tool"][
        "command"
    ]
    assert "printf 'alpha beta omega' > exact_result.txt" not in trace[
        "next_tool_after_context"
    ]["command"]
    historical_trace = report["trace_replay"]["trace"]
    assert historical_trace["ambiguous"] is True
    assert historical_trace["preceding_tool"] is None
    assert historical_trace["next_tool_after_context"] is None


def test_task_standard_posttooluse_shared_tool_evidence_gate0(
    tmp_path: Path,
) -> None:
    report = run_task_standard_posttooluse_shared_tool_evidence_gate0(
        output_root=tmp_path,
    )

    assert report["passed"] is True
    assert report["verdict"] == "pass_posttooluse_shared_tool_evidence_gate0"
    assert report["live_trials_ran"] is False
    assert report["behavior_lift_claim_allowed"] is False
    assert report["next_product_train"] == (
        "codex-app-cli-posttooluse-task-standard-phase-aware-narrow-live-rerun"
    )
    boundary_results = report["boundary_results"]
    assert boundary_results["shared_classifier_detects_pre_artifact_missing"] is True
    assert boundary_results["shared_classifier_detects_failed_check"] is True
    assert boundary_results["shared_classifier_detects_candidate_artifact"] is True
    assert boundary_results["shared_classifier_detects_readback"] is True
    assert boundary_results["shared_classifier_detects_markerless"] is True
    assert boundary_results["sre_task_standard_generic_check_preserved"] is True
    assert boundary_results["sre_task_standard_aligned_readback_preserved"] is True
    assert boundary_results["status_completion_marker_is_not_host_phase_marker"] is True
    assert boundary_results["prior_causal_trace_gate0_preserved"] is True


def test_task_standard_posttooluse_context_loop_trace_gate0(
    tmp_path: Path,
) -> None:
    report = run_task_standard_posttooluse_context_loop_trace_gate0(
        output_root=tmp_path,
    )

    assert report["passed"] is True
    assert report["verdict"] == "pass_posttooluse_context_loop_trace_gate0"
    assert report["live_trials_ran"] is False
    assert report["behavior_lift_claim_allowed"] is False
    assert report["next_product_train"] == (
        "codex-app-cli-posttooluse-task-standard-phase-aware-narrow-live-rerun"
    )
    boundary_results = report["boundary_results"]
    assert boundary_results["context_loop_first_context_emitted"] is True
    assert boundary_results["context_loop_second_context_silent"] is True
    assert boundary_results["context_loop_single_context_item"] is True
    assert boundary_results["context_loop_active_pending_reason"] is True
    assert boundary_results["exact_ref_trace_still_non_ambiguous"] is True
    assert boundary_results["exact_ref_trace_uses_ref_join"] is True
    assert boundary_results["fingerprint_trace_non_ambiguous"] is True
    assert boundary_results["fingerprint_trace_uses_fingerprint_join"] is True
    assert boundary_results["duplicate_fingerprint_marked_ambiguous"] is True
    assert boundary_results["missing_fingerprint_marked_ambiguous"] is True
    assert boundary_results["legacy_trace_not_interpreted_without_join"] is True
    assert boundary_results["no_ordinal_trace_join"] is True


def test_task_standard_posttooluse_measurement_stack_gate0(
    tmp_path: Path,
) -> None:
    report = run_task_standard_posttooluse_measurement_stack_gate0(
        output_root=tmp_path,
    )

    assert report["passed"] is True
    assert report["verdict"] == "pass_posttooluse_measurement_stack_gate0"
    assert report["live_trials_ran"] is False
    assert report["behavior_lift_claim_allowed"] is False
    assert report["next_product_train"] == (
        "codex-app-cli-posttooluse-task-standard-final-closure-readout-remediation-gate0"
    )
    boundary_results = report["boundary_results"]
    assert boundary_results["all_historical_artifacts_loaded"] is True
    assert boundary_results["five_artifacts_replayed"] is True
    assert boundary_results["preserves_true_next_action_ignore"] is True
    assert boundary_results["preserves_no_context"] is True
    assert boundary_results["preserves_overcontrol"] is True
    assert boundary_results["preserves_repeated_context_and_trace_blocker"] is True
    assert boundary_results["recognizes_final_closure_metric_underfit"] is True
    assert boundary_results["registered_verdicts_preserved"] is True
    assert boundary_results["semantic_evidence_does_not_mask_boundary_failures"] is True
    assert boundary_results["final_closure_helper_scoped_to_measurement_table"] is True
    episodes = {
        episode["artifact_id"]: episode for episode in report["episode_table"]
    }
    assert episodes["task_standard_posttooluse_live_20260507T100836Z"][
        "episode_classification"
    ] == "true_next_action_ignore"
    assert episodes["task_standard_posttooluse_live_20260507T142129Z"][
        "episode_classification"
    ] == "failure_no_context"
    assert episodes["task_standard_posttooluse_live_20260507T153242Z"][
        "episode_classification"
    ] == "failure_overcontrol"
    assert episodes["task_standard_posttooluse_live_20260507T213732Z"][
        "episode_classification"
    ] == "repeated_context_trace_not_interpretable"
    latest = episodes["task_standard_posttooluse_live_20260507T225019Z"]
    assert latest["registered_verdict"] == "failure_context_ignored"
    assert latest["old_final_closure_reports_context_evidence"] is False
    assert latest["semantic_final_closure_evidence"] is True
    assert latest["episode_classification"] == "final_closure_metric_underfit"


def test_task_standard_posttooluse_final_closure_readout_gate0(
    tmp_path: Path,
) -> None:
    report = run_task_standard_posttooluse_final_closure_readout_gate0(
        output_root=tmp_path,
    )

    assert report["passed"] is True
    assert report["verdict"] == "pass_posttooluse_final_closure_readout_gate0"
    assert report["live_trials_ran"] is False
    assert report["behavior_lift_claim_allowed"] is False
    assert report["next_product_train"] == (
        "codex-app-cli-posttooluse-task-standard-exactness-only-paired-value-probe-gate0"
    )
    boundary_results = report["boundary_results"]
    assert boundary_results["all_historical_artifacts_loaded"] is True
    assert boundary_results["five_artifacts_replayed"] is True
    assert boundary_results["old_cat_a_shape_still_recognized"] is True
    assert boundary_results["old_line_count_shape_still_recognized"] is True
    assert boundary_results["semantic_pass_bytes_hex_content_recognized"] is True
    assert boundary_results["semantic_cmp_exact_match_recognized"] is True
    assert boundary_results["incomplete_semantic_shapes_rejected"] is True
    assert boundary_results["registered_verdicts_preserved"] is True
    assert boundary_results["preserves_true_next_action_ignore"] is True
    assert boundary_results["preserves_no_context"] is True
    assert boundary_results["preserves_overcontrol"] is True
    assert boundary_results["preserves_repeated_context_and_trace_blocker"] is True
    assert boundary_results["corrects_latest_final_closure_readout_to_pass"] is True
    assert boundary_results["only_latest_artifact_passes_after_correction"] is True
    assert boundary_results["boundary_dominance_preserved"] is True

    replays = {
        replay["artifact_id"]: replay for replay in report["corrected_replay_table"]
    }
    assert replays["task_standard_posttooluse_live_20260507T100836Z"][
        "corrected_failure_reason"
    ] == "next_model_tool_did_not_run_named_direct_check"
    assert replays["task_standard_posttooluse_live_20260507T142129Z"][
        "corrected_verdict"
    ] == "failure_no_context"
    assert replays["task_standard_posttooluse_live_20260507T153242Z"][
        "corrected_verdict"
    ] == "failure_overcontrol"
    assert replays["task_standard_posttooluse_live_20260507T213732Z"][
        "corrected_failure_reason"
    ] == "repeated_posttooluse_context_loop"
    latest = replays["task_standard_posttooluse_live_20260507T225019Z"]
    assert latest["registered_verdict"] == "failure_context_ignored"
    assert latest["old_final_closure_reports_context_evidence"] is False
    assert latest["corrected_final_closure_reports_context_evidence"] is True
    assert latest["corrected_verdict"] == "pass_posttooluse_next_step_observed"


def test_task_standard_posttooluse_final_closure_predicate_shapes() -> None:
    assert comparison._final_reports_posttooluse_evidence(
        "cat -A exact_result.txt showed alpha beta omega; one line; "
        "1 exact_result.txt."
    )
    assert comparison._final_reports_posttooluse_evidence(
        "Result: PASS bytes=16 hex=616c7068612062657461206f6d656761; "
        "content is exactly alpha beta omega."
    )
    assert comparison._final_reports_posttooluse_evidence(
        "cmp_exit=0; exact byte match; exact_result.txt contains "
        "alpha beta omega."
    )
    assert not comparison._final_reports_posttooluse_evidence(
        "PASS bytes=16 but the content was not printed."
    )
    assert not comparison._final_reports_posttooluse_evidence(
        "alpha beta omega with no verification evidence."
    )


def test_task_standard_posttooluse_exactness_only_paired_value_gate0(
    tmp_path: Path,
) -> None:
    report = run_task_standard_posttooluse_exactness_only_paired_value_gate0(
        output_root=tmp_path,
    )

    assert report["passed"] is True
    assert report["verdict"] == "pass_posttooluse_exactness_only_paired_value_gate0"
    assert report["live_trials_ran"] is False
    assert report["behavior_lift_claim_allowed"] is False
    assert report["exactness_value_lift_claim_allowed"] is False
    assert report["next_product_train"] == (
        "codex-app-cli-posttooluse-task-standard-exactness-only-paired-value-live-probe"
    )
    design = report["probe_design"]
    assert design["conditions"] == [
        "active_posttooluse_context",
        "silent_posttooluse_control",
    ]
    assert design["cases"] == [
        "mismatch_exactness",
        "clean_evidenced",
        "honest_blocker",
        "waiting_on_user",
        "unrelated_tool",
    ]
    assert design["future_live_approval_env"] == (
        TASK_STANDARD_POSTTOOLUSE_VALUE_APPROVAL_ENV
    )
    assert design["arm_delta"] == ["enable_posttooluse_task_standard_context"]
    assert design["pass_threshold"] == {"active_wins": 4, "pairs": 5}
    assert design["historical_feasibility_counts_as_value_lift"] is False

    boundary_results = report["boundary_results"]
    for key in (
        "design_conditions_registered",
        "design_cases_registered",
        "approval_env_registered",
        "active_silent_arm_delta_only_context_flag",
        "threshold_registered",
        "passing_design_row_passes",
        "passing_design_has_5_active_wins",
        "no_value_row_fails_no_value",
        "silent_success_is_tie_not_active_win",
        "active_ignore_row_fails_context_ignored",
        "overcontrol_dominates_value",
        "repeated_context_dominates_value",
        "trace_ambiguity_dominates_value",
        "boundary_breach_dominates_value",
        "root_config_mutation_dominates_value",
        "runtime_snapshot_dominates_value",
        "latest_corrected_replay_is_feasibility_only",
        "no_live_trials",
        "behavior_lift_claim_forbidden",
        "exactness_value_lift_claim_forbidden",
    ):
        assert boundary_results[key] is True


def test_task_standard_posttooluse_paired_value_decision_boundaries() -> None:
    passing = comparison._task_standard_posttooluse_paired_value_decision(
        comparison._posttooluse_paired_value_synthetic_rows(
            silent_mismatch_success=False,
        )
    )
    assert passing["verdict"] == "pass_exactness_only_paired_value"
    assert passing["active_wins"] == 5

    no_value = comparison._task_standard_posttooluse_paired_value_decision(
        comparison._posttooluse_paired_value_synthetic_rows(
            silent_mismatch_success=True,
        )
    )
    assert no_value["verdict"] == "failure_no_value"
    assert no_value["active_wins"] == 0

    active_ignore = comparison._task_standard_posttooluse_paired_value_decision(
        comparison._posttooluse_paired_value_synthetic_rows(
            active_next_tool_matches_context=False,
            silent_mismatch_success=False,
        )
    )
    assert active_ignore["verdict"] == "failure_context_ignored"

    overcontrol = comparison._task_standard_posttooluse_paired_value_decision(
        comparison._posttooluse_paired_value_synthetic_rows(
            active_control_context_count=1,
            silent_mismatch_success=False,
        )
    )
    assert overcontrol["verdict"] == "failure_overcontrol"

    repeated = comparison._task_standard_posttooluse_paired_value_decision(
        comparison._posttooluse_paired_value_synthetic_rows(
            active_context_count=2,
            active_repeated_context=True,
            silent_mismatch_success=False,
        )
    )
    assert repeated["failure_reason"] == "repeated_posttooluse_context_loop"

    trace = comparison._task_standard_posttooluse_paired_value_decision(
        comparison._posttooluse_paired_value_synthetic_rows(
            active_trace_ambiguous=True,
            silent_mismatch_success=False,
        )
    )
    assert trace["verdict"] == "scoped_negative"
    assert trace["failure_reason"] == "posttooluse_context_trace_ambiguous"

    boundary = comparison._task_standard_posttooluse_paired_value_decision(
        comparison._posttooluse_paired_value_synthetic_rows(
            active_boundary_breach=True,
            silent_mismatch_success=False,
        )
    )
    assert boundary["failure_reason"] == "model_visible_context_boundary_breached"

    root_mutation = comparison._task_standard_posttooluse_paired_value_decision(
        comparison._posttooluse_paired_value_synthetic_rows(
            silent_mismatch_success=False,
        ),
        root_config_changed=True,
    )
    assert root_mutation["failure_reason"] == "root_config_changed"

    runtime_snapshot = comparison._task_standard_posttooluse_paired_value_decision(
        comparison._posttooluse_paired_value_synthetic_rows(
            active_runtime_snapshot_loaded=True,
            silent_mismatch_success=False,
        )
    )
    assert runtime_snapshot["failure_reason"] == "runtime_snapshot_loaded"


def test_task_standard_posttooluse_measurement_episode_accepts_synthetic_pass() -> None:
    row = comparison._posttooluse_measurement_synthetic_row(
        final_closure_reports_context_evidence=True,
        next_tool_matches_context=True,
    )
    row["output_excerpt"] = (
        "Result: PASS bytes=16 hex=616c7068612062657461206f6d656761 "
        "content alpha beta omega"
    )
    report = {
        "verdict": "pass_posttooluse_next_step_observed",
        "decision": {"verdict": "pass_posttooluse_next_step_observed"},
        "rows": [row],
    }

    episode = comparison.build_posttooluse_evidence_recovery_episode(
        artifact_id="synthetic_pass",
        report=report,
    )

    assert episode.episode_classification == "candidate_pass"
    assert episode.semantic_final_closure_evidence is True
    assert episode.old_final_closure_reports_context_evidence is True


def test_task_standard_posttooluse_measurement_episode_keeps_boundary_dominance() -> None:
    mismatch = comparison._posttooluse_measurement_synthetic_row(
        final_closure_reports_context_evidence=True,
        next_tool_matches_context=True,
    )
    mismatch["output_excerpt"] = (
        "Result: PASS bytes=16 hex=616c7068612062657461206f6d656761 "
        "content alpha beta omega"
    )
    clean_control = {
        "case": "clean_evidenced",
        "posttooluse_context_count": 1,
    }
    report = {
        "verdict": "failure_overcontrol",
        "decision": {
            "verdict": "failure_overcontrol",
            "failure_reason": "clean_or_control_case_received_context",
        },
        "rows": [mismatch, clean_control],
    }

    episode = comparison.build_posttooluse_evidence_recovery_episode(
        artifact_id="synthetic_overcontrol",
        report=report,
    )

    assert episode.semantic_final_closure_evidence is True
    assert episode.episode_classification == "failure_overcontrol"


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

    no_context_after_candidate = [
        _posttooluse_live_row("mismatch_exactness", artifact_prerequisite=True)
    ]
    no_context_decision = comparison._task_standard_posttooluse_live_decision(
        no_context_after_candidate
    )
    assert no_context_decision["verdict"] == "failure_no_context"
    assert (
        no_context_decision["failure_reason"]
        == "candidate_artifact_without_posttooluse_context"
    )

    preartifact_spend = [
        _posttooluse_live_row(
            "mismatch_exactness",
            context_count=1,
            preartifact_context=True,
        )
    ]
    preartifact_decision = comparison._task_standard_posttooluse_live_decision(
        preartifact_spend
    )
    assert preartifact_decision["verdict"] == "fail"
    assert preartifact_decision["failure_reason"] == "pre_artifact_context_spend"

    ignored = [_posttooluse_live_row("mismatch_exactness", context_count=1)]
    assert comparison._task_standard_posttooluse_live_decision(ignored)[
        "verdict"
    ] == "failure_context_ignored"

    repeated = [
        _posttooluse_live_row(
            "mismatch_exactness",
            context_count=2,
            repeated_context=True,
        )
    ]
    repeated_decision = comparison._task_standard_posttooluse_live_decision(
        repeated
    )
    assert repeated_decision["verdict"] == "fail"
    assert repeated_decision["failure_reason"] == "repeated_posttooluse_context_loop"

    trace_ambiguous = [
        _posttooluse_live_row(
            "mismatch_exactness",
            context_count=1,
            trace_ambiguous=True,
        )
    ]
    trace_decision = comparison._task_standard_posttooluse_live_decision(
        trace_ambiguous
    )
    assert trace_decision["verdict"] == "scoped_negative"
    assert trace_decision["failure_reason"] == "posttooluse_context_trace_ambiguous"

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
    assert "--task-standard-posttooluse-phase-aware-gate0" in source
    assert "--task-standard-posttooluse-overcontrol-gate0" in source
    assert "--task-standard-posttooluse-actuator-trace-gate0" in source
    assert "--task-standard-posttooluse-shared-tool-evidence-gate0" in source
    assert "--task-standard-posttooluse-context-loop-trace-gate0" in source
    assert "--task-standard-posttooluse-final-closure-readout-gate0" in source
    assert (
        "--task-standard-posttooluse-exactness-only-paired-value-gate0" in source
    )


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
    artifact_prerequisite: bool = False,
    preartifact_context: bool = False,
    boundary_breach: bool = False,
    trace_ambiguous: bool = False,
    repeated_context: bool = False,
) -> dict[str, object]:
    return {
        "case": case,
        "runtime_snapshot_loaded": False,
        "subject_config_contains_runtime_snapshot": False,
        "posttooluse_context_repeated": repeated_context,
        "posttooluse_context_boundary_breach": boundary_breach,
        "timed_out": False,
        "posttooluse_lifecycle_observed": True,
        "captured_standard_item_count": captured,
        "posttooluse_context_count": context_count,
        "artifact_prerequisite_observed": artifact_prerequisite,
        "posttooluse_context_after_preartifact_check": preartifact_context,
        "posttooluse_context_trace_ambiguous": trace_ambiguous,
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
