"""Tests for the OpenAI silent-control live-probe Gate-0 harness."""

from __future__ import annotations

import json

from lab.live_openai_silent_control_probe import run_gate0_audit


def test_gate0_blocks_live_trials_when_codex_operator_cannot_enact_debt_control(
    tmp_path,
) -> None:
    report = run_gate0_audit(output_root=tmp_path)

    assert report["runtime_control_delta_present"] is True
    assert report["model_bound_delta_present"] is False
    assert report["gate0_passed"] is False
    assert report["decision"] == {
        "live_trials_allowed": False,
        "verdict": "gate0_failed",
        "next_step": (
            "Do not run live trials. Open a remediation seam that connects "
            "OpenAI runtime debt-control outputs to the Codex operator invocation "
            "or continuation policy."
        ),
    }
    assert report["adapter_coupling"]["model_bound_debt_enactment_present"] is False
    assert report["adapter_coupling"]["accepts_runtime_control_argument"] is False
    assert report["adapter_coupling"]["directionality_harness_uses_debt_control"] is False
    assert report["adapter_coupling"]["codex_exec_command_accepts_control_payload"] is False

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
            "control_ledger_debt_control",
            "model_input_hash",
            "model_output_excerpt",
            "score",
        } <= set(row)
        assert row["control_ledger_debt_control"] == row["debt_control_payload"]

    shaped_rows = [row for row in rows if row["condition"] == "shaped_debt"]
    assert any(row["debt_control_payload"]["debt_pressure"] > 0.0 for row in shaped_rows)
