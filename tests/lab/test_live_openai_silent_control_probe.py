"""Tests for the OpenAI silent-control live-probe Gate-0 harness."""

from __future__ import annotations

import json

from lab.live_openai_silent_control_probe import run_gate0_audit
from lab.live_validation_common import read_prompt_template


def test_gate0_passes_when_openai_host_adapter_enacts_debt_control(
    tmp_path,
) -> None:
    report = run_gate0_audit(output_root=tmp_path)

    assert report["runtime_control_delta_present"] is True
    assert report["model_bound_delta_present"] is True
    assert report["gate0_passed"] is True
    assert report["decision"] == {
        "live_trials_allowed": True,
        "verdict": "gate0_passed",
        "next_step": (
            "Retry the paired baseline/shaped/clean OpenAI operator trial "
            "matrix with host-adapter enactment enabled."
        ),
    }
    assert report["adapter_coupling"]["host_adapter_enactment_present"] is True
    assert report["adapter_coupling"]["low_level_cli_runner_stays_thin"] is True
    assert report["adapter_coupling"]["model_bound_debt_enactment_present"] is True
    assert report["adapter_coupling"]["model_bound_enactment_scenarios"] == [
        "truth_gap_inspect_after_unpaid_verification"
    ]

    trajectory_path = tmp_path / "gate0_trajectory.jsonl"
    rows = [
        json.loads(line)
        for line in trajectory_path.read_text(encoding="utf-8").splitlines()
    ]

    assert len(rows) == 4
    for row in rows:
        assert {
            "trial_id",
            "condition",
            "task_family",
            "event_index",
            "input_event",
            "expectation_ledger",
            "resolution_deficit_payload",
            "debt_control_payload",
            "executive_policy_view_payload",
            "operator_route_payload",
            "operator_enactment_payload",
            "control_ledger_debt_control",
            "initial_prompt_hash",
            "model_input_hash",
            "model_output_excerpt",
            "model_visible_internal_term_leaks",
            "model_visible_values",
            "score",
        } <= set(row)
        assert row["control_ledger_debt_control"] == row["debt_control_payload"]
        assert row["model_visible_internal_term_leaks"] == []

    shaped_rows = [row for row in rows if row["condition"] == "shaped_debt"]
    assert any(row["debt_control_payload"]["debt_pressure"] > 0.0 for row in shaped_rows)
    by_trial = {row["trial_id"]: row for row in rows}
    neutral = by_trial["truth_gap_inspect_after_unpaid_verification:neutral"]
    shaped = by_trial["truth_gap_inspect_after_unpaid_verification:shaped"]
    assert neutral["initial_prompt_hash"] == shaped["initial_prompt_hash"]
    assert neutral["operator_enactment_payload"]["action"] == "invoke"
    assert neutral["operator_enactment_payload"]["thread_policy"] == "ephemeral_allowed"
    assert shaped["operator_enactment_payload"]["action"] == "resume_recheck"
    assert shaped["operator_enactment_payload"]["resume_prompt_name"] == (
        "truth_gap_recheck_operator.md"
    )
    assert shaped["operator_enactment_payload"]["thread_policy"] == (
        "resume_existing_thread"
    )
    assert shaped["model_visible_values"]["resumed_prompt"] == read_prompt_template(
        "truth_gap_recheck_operator.md"
    )
    assert shaped["model_visible_values"]["command_argv"][:5] == [
        "codex",
        "exec",
        "resume",
        "--json",
        "--full-auto",
    ]
    assert "gate0-thread-1" in shaped["model_visible_values"]["command_argv"]
