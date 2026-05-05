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
    run_astro_three_arm_gate0_probe,
    run_astro_three_arm_live,
    run_gate0_probe,
    run_live_comparison,
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
