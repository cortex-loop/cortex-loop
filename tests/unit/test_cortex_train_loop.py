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


def test_run_verified_work_breadth_openai_train_records_promote_on_third_pack_lift(
    tmp_path: Path,
    monkeypatch,
) -> None:
    def _fake_run_shell_command(command, *, cwd):
        _ = cwd
        if "pytest -q" in command:
            return {
                "command": command,
                "cwd": str(cwd),
                "exit_code": 0,
                "stdout": "",
                "stderr": "",
            }
        if "verified_work_bookmarks_v1" in command:
            payload = {
                "results": [
                    {"brain": "openai", "status": "conformant"},
                ],
                "next_decision": "promote",
            }
        elif "--brain openai" in command:
            payload = {
                "results": [
                    {"brain": "openai", "status": "conformant"},
                ],
                "next_decision": "promote",
            }
        else:
            payload = {
                "results": [
                    {"brain": "openai", "status": "conformant"},
                    {"brain": "claude", "status": "conformant"},
                    {"brain": "gemini", "status": "conformant"},
                ],
                "next_decision": "promote",
            }
        return {
            "command": command,
            "cwd": str(cwd),
            "exit_code": 0,
            "stdout": json.dumps(payload),
            "stderr": "",
        }

    monkeypatch.setattr(train_loop, "_run_shell_command", _fake_run_shell_command)

    record = train_loop.run_verified_work_breadth_openai_train(loop_root=tmp_path)

    assert record.final_decision == "promote"
    assert record.iterations[0].primary_metric_before == 2
    assert record.iterations[0].primary_metric_after == 3
    assert (tmp_path / "verified-work-breadth-openai" / "summary.json").exists()


def test_run_verified_work_breadth_openai_train_escalates_on_repeated_env_block(
    tmp_path: Path,
    monkeypatch,
) -> None:
    def _fake_run_shell_command(command, *, cwd):
        _ = cwd
        if "pytest -q" in command:
            return {
                "command": command,
                "cwd": str(cwd),
                "exit_code": 0,
                "stdout": "",
                "stderr": "",
            }
        if "verified_work_bookmarks_v1" in command:
            payload = {
                "results": [
                    {"brain": "openai", "status": "conformant"},
                ],
                "next_decision": "promote",
            }
            return {
                "command": command,
                "cwd": str(cwd),
                "exit_code": 0,
                "stdout": json.dumps(payload),
                "stderr": "",
            }
        if "--brain openai" in command:
            payload = {
                "results": [
                    {"brain": "openai", "status": "env_blocked"},
                ],
                "next_decision": "clear_env_blocks",
            }
            return {
                "command": command,
                "cwd": str(cwd),
                "exit_code": 0,
                "stdout": json.dumps(payload),
                "stderr": "",
            }
        payload = {
            "results": [
                {"brain": "openai", "status": "env_blocked"},
                {"brain": "claude", "status": "conformant"},
                {"brain": "gemini", "status": "conformant"},
            ],
            "next_decision": "clear_env_blocks",
        }
        return {
            "command": command,
            "cwd": str(cwd),
            "exit_code": 0,
            "stdout": json.dumps(payload),
            "stderr": "",
        }

    monkeypatch.setattr(train_loop, "_run_shell_command", _fake_run_shell_command)

    record = train_loop.run_verified_work_breadth_openai_train(loop_root=tmp_path)

    assert record.final_decision == "escalate"
    assert "provider/env block" in record.iterations[0].reason


def test_run_verified_work_breadth_openai_train_retries_once_on_non_shipping_guardrail_env_block(
    tmp_path: Path,
    monkeypatch,
) -> None:
    state = {"tri_brain_calls": 0}

    def _fake_run_shell_command(command, *, cwd):
        _ = cwd
        if "pytest -q" in command:
            return {
                "command": command,
                "cwd": str(cwd),
                "exit_code": 0,
                "stdout": "",
                "stderr": "",
            }
        if "--brain openai" in command:
            payload = {
                "results": [
                    {"brain": "openai", "status": "conformant"},
                ],
                "next_decision": "promote",
            }
            return {
                "command": command,
                "cwd": str(cwd),
                "exit_code": 0,
                "stdout": json.dumps(payload),
                "stderr": "",
            }
        state["tri_brain_calls"] += 1
        if state["tri_brain_calls"] == 1:
            payload = {
                "results": [
                    {"brain": "openai", "status": "conformant"},
                    {"brain": "claude", "status": "env_blocked"},
                    {"brain": "gemini", "status": "conformant"},
                ],
                "next_decision": "promote",
            }
        else:
            payload = {
                "results": [
                    {"brain": "openai", "status": "conformant"},
                    {"brain": "claude", "status": "conformant"},
                    {"brain": "gemini", "status": "conformant"},
                ],
                "next_decision": "promote",
            }
        return {
            "command": command,
            "cwd": str(cwd),
            "exit_code": 0,
            "stdout": json.dumps(payload),
            "stderr": "",
        }

    monkeypatch.setattr(train_loop, "_run_shell_command", _fake_run_shell_command)

    record = train_loop.run_verified_work_breadth_openai_train(loop_root=tmp_path)

    assert record.final_decision == "promote"
    assert state["tri_brain_calls"] == 2
    assert record.iterations[0].primary_metric_after == 3
    assert len(record.iterations[0].proof_commands) == 9


def test_run_verified_work_repair_yield_openai_train_promotes_on_recovered_repair(
    tmp_path: Path,
    monkeypatch,
) -> None:
    def _fake_run_shell_command(command, *, cwd):
        _ = cwd
        if "pytest -q" in command:
            payload = {}
        elif "--contract-pack verified_work_normalize_port_v1 --max-repair-turns 1" in command:
            payload = {
                "results": [
                    {
                        "brain": "openai",
                        "status": "conformant",
                        "repair_conversion": "recovered_after_repair",
                    }
                ]
            }
        elif "--max-repair-turns 1" in command:
            payload = {
                "results": [
                    {
                        "brain": "openai",
                        "status": "conformant",
                        "repair_conversion": "passed_without_repair",
                    }
                ]
            }
        elif "--max-repair-turns 0" in command:
            payload = {
                "results": [
                    {
                        "brain": "openai",
                        "status": "conformant",
                        "repair_conversion": "passed_without_repair",
                    }
                ]
            }
        else:
            payload = {
                "results": [
                    {"brain": "openai", "status": "conformant"},
                    {"brain": "claude", "status": "conformant"},
                    {"brain": "gemini", "status": "conformant"},
                ]
            }
        return {
            "command": command,
            "cwd": str(cwd),
            "exit_code": 0,
            "stdout": json.dumps(payload),
            "stderr": "",
        }

    monkeypatch.setattr(train_loop, "_run_shell_command", _fake_run_shell_command)

    record = train_loop.run_verified_work_repair_yield_openai_train(loop_root=tmp_path)

    assert record.final_decision == "promote"
    assert record.iterations[0].primary_metric_before == 0
    assert record.iterations[0].primary_metric_after == 2
    assert record.baseline_result["repair_opportunities"] == 2
    assert "make revalidate-openai-host-control" in record.iterations[0].proof_commands


def test_run_verified_work_repair_yield_openai_train_escalates_when_no_repair_opportunities_appear(
    tmp_path: Path,
    monkeypatch,
) -> None:
    def _fake_run_shell_command(command, *, cwd):
        _ = cwd
        payload = {}
        if "pytest -q" not in command:
            payload = {
                "results": [
                    {
                        "brain": "openai",
                        "status": "conformant",
                        "repair_conversion": "passed_without_repair",
                    }
                ]
            }
        return {
            "command": command,
            "cwd": str(cwd),
            "exit_code": 0,
            "stdout": json.dumps(payload),
            "stderr": "",
        }

    monkeypatch.setattr(train_loop, "_run_shell_command", _fake_run_shell_command)

    record = train_loop.run_verified_work_repair_yield_openai_train(loop_root=tmp_path)

    assert record.final_decision == "escalate"
    assert "insufficient natural failures" in record.iterations[0].reason
    assert record.baseline_result["rounds_executed"] == 2
    assert "make revalidate-openai-host-control" in record.iterations[0].proof_commands


def test_run_output_quality_comparison_openai_train_promotes_on_repeat_stable_advantage(
    tmp_path: Path,
    monkeypatch,
) -> None:
    def _fake_short_command(command, *, cwd):
        _ = cwd
        return {
            "command": command,
            "cwd": str(cwd),
            "exit_code": 0,
            "stdout": "",
            "stderr": "",
        }

    summaries = iter(
        (
            {
                "env_blocked": False,
                "aggregate_objective_pass_count": {"raw": 2, "tooling_only": 4, "cortex": 4},
                "aggregate_hidden_quality_pass_count": {"raw": 1, "tooling_only": 3, "cortex": 4},
                "pairwise_summary": {
                    "cortex_vs_raw": {"wins": 4, "losses": 1, "ties": 0, "win_rate": 0.8},
                    "cortex_vs_tooling_only": {
                        "wins": 2,
                        "losses": 2,
                        "ties": 1,
                        "win_rate": 0.4,
                    },
                },
            },
            {
                "env_blocked": False,
                "aggregate_objective_pass_count": {"raw": 2, "tooling_only": 4, "cortex": 4},
                "aggregate_hidden_quality_pass_count": {"raw": 1, "tooling_only": 3, "cortex": 4},
                "pairwise_summary": {
                    "cortex_vs_raw": {"wins": 3, "losses": 1, "ties": 1, "win_rate": 0.6},
                    "cortex_vs_tooling_only": {
                        "wins": 2,
                        "losses": 2,
                        "ties": 1,
                        "win_rate": 0.4,
                    },
                },
            },
        )
    )

    def _fake_long_command(command, *, cwd):
        _ = cwd
        return {
            "command": command,
            "cwd": str(cwd),
            "exit_code": 0,
            "stdout": json.dumps(next(summaries)),
            "stderr": "",
        }

    monkeypatch.setattr(train_loop, "_run_shell_command", _fake_short_command)
    monkeypatch.setattr(train_loop, "_run_long_shell_command", _fake_long_command)

    record = train_loop.run_output_quality_comparison_openai_train(loop_root=tmp_path)

    assert record.final_decision == "promote"
    assert record.iterations[0].primary_metric_after == 70
    assert record.baseline_result["total_pairwise_wins"] == 7
    assert (tmp_path / "output-quality-comparison-openai" / "summary.json").exists()


def test_run_output_quality_comparison_openai_train_escalates_on_env_block(
    tmp_path: Path,
    monkeypatch,
) -> None:
    def _fake_short_command(command, *, cwd):
        _ = cwd
        return {
            "command": command,
            "cwd": str(cwd),
            "exit_code": 0,
            "stdout": "",
            "stderr": "",
        }

    def _fake_long_command(command, *, cwd):
        _ = cwd
        return {
            "command": command,
            "cwd": str(cwd),
            "exit_code": 0,
            "stdout": json.dumps(
                {
                    "env_blocked": True,
                    "aggregate_objective_pass_count": {"raw": 0, "tooling_only": 0, "cortex": 0},
                    "aggregate_hidden_quality_pass_count": {"raw": 0, "tooling_only": 0, "cortex": 0},
                    "pairwise_summary": {
                        "cortex_vs_raw": {"wins": 0, "losses": 0, "ties": 0, "win_rate": 0.0},
                    },
                }
            ),
            "stderr": "",
        }

    monkeypatch.setattr(train_loop, "_run_shell_command", _fake_short_command)
    monkeypatch.setattr(train_loop, "_run_long_shell_command", _fake_long_command)

    record = train_loop.run_output_quality_comparison_openai_train(loop_root=tmp_path)

    assert record.final_decision == "escalate"
    assert "env/auth blocked" in record.iterations[0].reason


def test_run_causal_contribution_map_openai_train_promotes_on_repeat_stable_classification(
    tmp_path: Path,
    monkeypatch,
) -> None:
    def _fake_short_command(command, *, cwd):
        _ = cwd
        if "pytest -q" in command or "make revalidate-openai-host-control" in command:
            return {
                "command": command,
                "cwd": str(cwd),
                "exit_code": 0,
                "stdout": "",
                "stderr": "",
            }
        payload = {
            "openai_ablation_config": None,
            "results": [
                {
                    "brain": "openai",
                    "status": "conformant",
                    "attempt_count": 1,
                    "repair_conversion": "passed_without_repair",
                }
            ],
        }
        if "--verification-binding off --repair-turn off" in command:
            payload = {
                "openai_ablation_config": {
                    "verification_binding": "off",
                    "repair_turn": "off",
                },
                "results": [
                    {
                        "brain": "openai",
                        "status": "partial",
                        "attempt_count": 1,
                        "repair_conversion": "failed_without_repair",
                    }
                ],
            }
        return {
            "command": command,
            "cwd": str(cwd),
            "exit_code": 0,
            "stdout": json.dumps(payload),
            "stderr": "",
        }

    def _fake_long_command(command, *, cwd):
        _ = cwd
        payload = {
            "env_blocked": False,
            "pairwise_summary": {
                "cortex_vs_raw": {"wins": 2, "losses": 1, "ties": 2, "win_rate": 0.4},
                "cortex_vs_tooling_only": {
                    "wins": 2,
                    "losses": 1,
                    "ties": 2,
                    "win_rate": 0.4,
                },
            },
            "aggregate_objective_pass_count": {"cortex": 3},
            "aggregate_hidden_quality_pass_count": {"cortex": 2},
        }
        if "--verification-binding off --repair-turn off" in command:
            payload = {
                "env_blocked": False,
                "pairwise_summary": {
                    "cortex_vs_raw": {"wins": 0, "losses": 3, "ties": 2, "win_rate": 0.0},
                    "cortex_vs_tooling_only": {
                        "wins": 0,
                        "losses": 3,
                        "ties": 2,
                        "win_rate": 0.0,
                    },
                },
                "aggregate_objective_pass_count": {"cortex": 1},
                "aggregate_hidden_quality_pass_count": {"cortex": 1},
            }
        return {
            "command": command,
            "cwd": str(cwd),
            "exit_code": 0,
            "stdout": json.dumps(payload),
            "stderr": "",
        }

    monkeypatch.setattr(train_loop, "_run_shell_command", _fake_short_command)
    monkeypatch.setattr(train_loop, "_run_long_shell_command", _fake_long_command)

    note_path = tmp_path / "CORTEX_V2_CAUSAL_MAP_NOTE_0.md"
    record = train_loop.run_causal_contribution_map_openai_train(
        loop_root=tmp_path,
        note_path=note_path,
    )

    assert record.final_decision == "promote"
    assert (
        record.analysis["component_classifications"]["revision_loop_off"]["classification"]
        == "positive"
    )
    assert (tmp_path / "causal-contribution-map-openai" / "summary.json").exists()
    assert note_path.exists()
