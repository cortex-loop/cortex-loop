"""Focused tests for the maintainer-only Cortex train loop recorder."""

from __future__ import annotations

import json
import sys
from pathlib import Path


TOOLS_ROOT = Path(__file__).resolve().parents[2] / "tools"
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

import cortex_train_loop as train_loop


def test_decide_loop_decision_promotes_on_metric_lift() -> None:
    decision, reason = train_loop.decide_loop_decision(
        primary_metric_before=0,
        primary_metric_after=1,
        guardrail_ok=True,
        localized_failure=True,
        better_classification=True,
        budget_remaining=1,
    )

    assert decision == "promote"
    assert "improved" in reason


def test_decide_loop_decision_revises_localized_failure_with_budget() -> None:
    decision, reason = train_loop.decide_loop_decision(
        primary_metric_before=0,
        primary_metric_after=0,
        guardrail_ok=True,
        localized_failure=True,
        better_classification=False,
        budget_remaining=1,
    )

    assert decision == "revise"
    assert "localized" in reason


def test_decide_loop_decision_cuts_on_guardrail_regression() -> None:
    decision, reason = train_loop.decide_loop_decision(
        primary_metric_before=0,
        primary_metric_after=1,
        guardrail_ok=False,
        localized_failure=True,
        better_classification=True,
        budget_remaining=1,
    )

    assert decision == "cut"
    assert "guardrail" in reason


def test_decide_loop_decision_escalates_after_second_no_lift_cut() -> None:
    decision, reason = train_loop.decide_loop_decision(
        primary_metric_before=0,
        primary_metric_after=0,
        guardrail_ok=True,
        localized_failure=False,
        better_classification=False,
        budget_remaining=0,
        previous_no_lift_cuts=1,
    )

    assert decision == "escalate"
    assert "two no-lift revisions" in reason


def test_evaluate_conformance_summary_truth_detects_missing_artifacts(
    tmp_path: Path,
) -> None:
    phase_gates_path = tmp_path / "phase_gates.md"
    phase_gates_path.write_text(
        "| `CT2` active verified-work tri-brain conformance | evidence | owner | partial | current shipping-default decision is `promote` |\n",
        encoding="utf-8",
    )
    summary_path = tmp_path / "summary.latest.json"
    summary_path.write_text(
        json.dumps(
            {
                "next_decision": "fix_wiring_only",
                "shipping_truth": {"default": "openai:service_api"},
                "results": [
                    {"brain": "openai", "artifact_relpath": "missing/openai"},
                    {"brain": "claude", "artifact_relpath": "missing/claude"},
                    {"brain": "gemini", "artifact_relpath": "missing/gemini"},
                ],
            }
        ),
        encoding="utf-8",
    )

    result = train_loop.evaluate_conformance_summary_truth(
        repo_root=tmp_path,
        summary_path=summary_path,
        phase_gates_path=phase_gates_path,
    )

    assert result["primary_metric_value"] == 0
    assert "references missing artifacts" in " ".join(result["reasons"])
    assert result["accepted_next_decision"] == "promote"


def test_run_conformance_summary_truth_pilot_records_iteration(
    tmp_path: Path,
    monkeypatch,
) -> None:
    baseline_iter = iter(
        (
            {
                "primary_metric_value": 0,
                "guardrail_ok": True,
                "accepted_next_decision": "promote",
                "summary_next_decision": "fix_wiring_only",
                "is_full_run": False,
                "artifacts_exist": False,
                "reasons": ["stale"],
            },
            {
                "primary_metric_value": 1,
                "guardrail_ok": True,
                "accepted_next_decision": "promote",
                "summary_next_decision": "promote",
                "is_full_run": True,
                "artifacts_exist": True,
                "reasons": [],
            },
        )
    )

    monkeypatch.setattr(
        train_loop,
        "evaluate_conformance_summary_truth",
        lambda **_kwargs: next(baseline_iter),
    )
    monkeypatch.setattr(
        train_loop,
        "_run_shell_command",
        lambda command, *, cwd: {
            "command": command,
            "cwd": str(cwd),
            "exit_code": 0,
            "stdout": "",
            "stderr": "",
        },
    )

    record = train_loop.run_conformance_summary_truth_pilot(loop_root=tmp_path)

    assert record.final_decision == "promote"
    assert record.iterations[0].primary_metric_before == 0
    assert record.iterations[0].primary_metric_after == 1
    assert (tmp_path / "conformance-summary-truth" / "summary.json").exists()


def test_run_conformance_summary_truth_pilot_promotes_when_alignment_is_preserved(
    tmp_path: Path,
    monkeypatch,
) -> None:
    aligned = {
        "primary_metric_value": 1,
        "guardrail_ok": True,
        "accepted_next_decision": "promote",
        "summary_next_decision": "promote",
        "is_full_run": True,
        "artifacts_exist": True,
        "reasons": [],
    }
    baseline_iter = iter((aligned, aligned))

    monkeypatch.setattr(
        train_loop,
        "evaluate_conformance_summary_truth",
        lambda **_kwargs: next(baseline_iter),
    )
    monkeypatch.setattr(
        train_loop,
        "_run_shell_command",
        lambda command, *, cwd: {
            "command": command,
            "cwd": str(cwd),
            "exit_code": 0,
            "stdout": "",
            "stderr": "",
        },
    )

    record = train_loop.run_conformance_summary_truth_pilot(loop_root=tmp_path)

    assert record.final_decision == "promote"
    assert "preserved" in record.iterations[0].reason
