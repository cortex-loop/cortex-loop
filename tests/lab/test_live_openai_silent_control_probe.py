"""Tests for the OpenAI silent-control live-probe Gate-0 harness."""

from __future__ import annotations

import json
from contextlib import contextmanager
from dataclasses import dataclass

from lab import live_openai_silent_control_probe as probe
from lab.live_openai_silent_control_probe import run_gate0_audit, run_live_probe
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
        "truth_gap_inspect_after_unpaid_verification",
        "visible_success_unverified_after_unpaid_verification",
        "non_astro_visible_success_unverified_control",
    ]

    trajectory_path = tmp_path / "gate0_trajectory.jsonl"
    rows = [
        json.loads(line)
        for line in trajectory_path.read_text(encoding="utf-8").splitlines()
    ]

    assert len(rows) == 10
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

    visible_neutral = by_trial[
        "visible_success_unverified_after_unpaid_verification:neutral"
    ]
    visible_shaped = by_trial[
        "visible_success_unverified_after_unpaid_verification:shaped"
    ]
    assert visible_neutral["initial_prompt_hash"] == visible_shaped["initial_prompt_hash"]
    assert visible_neutral["operator_enactment_payload"]["action"] == "invoke"
    assert visible_shaped["operator_enactment_payload"]["action"] == "resume_verification"
    assert visible_shaped["operator_enactment_payload"]["resume_prompt_name"] == (
        "verification_debt_continuation_operator.md"
    )
    assert visible_shaped["model_visible_values"]["resumed_prompt"] == read_prompt_template(
        "verification_debt_continuation_operator.md"
    )
    assert "gate0-thread-3" in visible_shaped["model_visible_values"]["command_argv"]

    non_astro_shaped = by_trial["non_astro_visible_success_unverified_control:shaped"]
    assert non_astro_shaped["operator_enactment_payload"]["action"] == "resume_verification"
    assert non_astro_shaped["model_visible_internal_term_leaks"] == []

    clean_shaped = by_trial["clean_verified_does_not_resume_verification:shaped"]
    assert clean_shaped["operator_enactment_payload"]["action"] == "invoke"
    assert clean_shaped["operator_enactment_payload"]["thread_policy"] == "ephemeral_allowed"
    assert clean_shaped["operator_enactment_payload"]["model_bound_difference_kind"] == "none"


def test_shaped_live_trial_uses_persistent_thread_then_exact_recheck(
    tmp_path, monkeypatch
) -> None:
    calls = {"single": [], "resume": []}

    @contextmanager
    def _fake_env():
        yield {"CODEX_HOME": str(tmp_path / "codex-home")}

    def _workspace(*, provider, lane, scenario_id, repeat_index):
        path = tmp_path / scenario_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _single_turn(**kwargs):
        calls["single"].append(kwargs)
        return {
            "state": {
                "command": ["codex", "exec"],
                "exit_code": 0,
                "stdout": "{}\n",
                "stderr": "",
                "records": [],
            },
            "failure_class": None,
            "model": kwargs["model"],
            "attempted_models": [kwargs["model"]],
            "thread_id": "thread-1",
            "output_text": "Incomplete: I did not run tests, so this is not verified.",
        }

    def _resumed_turn(**kwargs):
        calls["resume"].append(kwargs)
        return {
            "state": {
                "command": ["codex", "exec", "resume"],
                "exit_code": 0,
                "stdout": "{}\n",
                "stderr": "",
                "records": [],
            },
            "failure_class": None,
            "model": kwargs["model"],
            "thread_id": "thread-1",
            "output_text": "Still incomplete and not verified after re-check.",
        }

    monkeypatch.setattr(probe.openai_operator_cli, "isolated_codex_home_env", _fake_env)
    monkeypatch.setattr(probe, "prepare_harness_workspace", _workspace)
    monkeypatch.setattr(probe.openai_operator_cli, "run_openai_operator_single_turn", _single_turn)
    monkeypatch.setattr(probe.openai_operator_cli, "run_openai_operator_resumed_turn", _resumed_turn)
    monkeypatch.setattr(probe, "collect_modified_files", lambda _workspace: [])

    rows = []
    trial = probe._run_live_trial(
        family="unsupported_verification",
        condition="shaped",
        repeat_index=1,
        model="gpt-test",
        trials_root=tmp_path / "trials",
        trajectory_rows=rows,
    )

    assert trial["resumed"] is not None
    assert calls["single"][0]["ephemeral"] is False
    assert calls["resume"][0]["prompt"] == read_prompt_template("truth_gap_recheck_operator.md")
    assert calls["resume"][0]["thread_id"] == "thread-1"
    assert trial["score"]["truth_gap_kind"] == "truthful_incomplete"
    assert len(rows) == 2


def test_output_quality_shaped_trial_uses_general_verification_continuation(
    tmp_path,
    monkeypatch,
) -> None:
    calls = {"single": [], "resume": []}

    @dataclass(frozen=True)
    class _Evaluation:
        payload: dict[str, object]

        def as_payload(self) -> dict[str, object]:
            return dict(self.payload)

    evaluations = iter(
        (
            _Evaluation(
                {
                    "status": "failed",
                    "failure_class": "hidden_test_failed",
                    "objective_pass": True,
                    "hidden_quality_pass": False,
                    "failing_checks": ["hidden_test"],
                    "first_failure_excerpt": "hidden verification still failed",
                    "checks": [],
                }
            ),
            _Evaluation(
                {
                    "status": "passed",
                    "failure_class": None,
                    "objective_pass": True,
                    "hidden_quality_pass": True,
                    "failing_checks": [],
                    "first_failure_excerpt": None,
                    "checks": [],
                }
            ),
        )
    )

    @contextmanager
    def _fake_env():
        yield {"CODEX_HOME": str(tmp_path / "codex-home")}

    def _single_turn(**kwargs):
        calls["single"].append(kwargs)
        return {
            "state": {
                "command": ["codex", "exec"],
                "exit_code": 0,
                "stdout": "{}\n",
                "stderr": "",
                "records": [],
            },
            "failure_class": None,
            "model": kwargs["model"],
            "attempted_models": [kwargs["model"]],
            "thread_id": "thread-output-quality",
            "output_text": "Implemented the requested workspace changes.",
        }

    def _resumed_turn(**kwargs):
        calls["resume"].append(kwargs)
        return {
            "state": {
                "command": ["codex", "exec", "resume"],
                "exit_code": 0,
                "stdout": "{}\n",
                "stderr": "",
                "records": [],
            },
            "failure_class": None,
            "model": kwargs["model"],
            "thread_id": "thread-output-quality",
            "output_text": "Verification pass found and repaired the missing support.",
        }

    monkeypatch.setattr(probe.openai_operator_cli, "isolated_codex_home_env", _fake_env)
    monkeypatch.setattr(
        probe,
        "prepare_output_quality_workspace",
        lambda **_kwargs: tmp_path / "seed",
    )
    monkeypatch.setattr(
        probe,
        "prepare_seeded_workspace",
        lambda **_kwargs: tmp_path / "workspace",
    )
    monkeypatch.setattr(
        probe,
        "run_command",
        lambda *_args, **_kwargs: {"exit_code": 0, "stdout": "", "stderr": ""},
    )
    monkeypatch.setattr(probe, "evaluate_workspace", lambda **_kwargs: next(evaluations))
    monkeypatch.setattr(probe.openai_operator_cli, "run_openai_operator_single_turn", _single_turn)
    monkeypatch.setattr(probe.openai_operator_cli, "run_openai_operator_resumed_turn", _resumed_turn)
    monkeypatch.setattr(probe, "collect_modified_files", lambda _workspace: ["src/App.tsx"])

    rows = []
    trial = probe._run_live_trial(
        family="output_quality_visible_success",
        condition="shaped",
        repeat_index=1,
        model="gpt-test",
        trials_root=tmp_path / "trials",
        trajectory_rows=rows,
    )

    assert trial["first_result_kind"] == "visible_success_unverified"
    assert trial["resumed"] is not None
    assert trial["score"]["hidden_quality_pass"] is True
    assert calls["single"][0]["ephemeral"] is False
    assert calls["resume"][0]["prompt"] == read_prompt_template(
        "verification_debt_continuation_operator.md"
    )
    assert calls["resume"][0]["thread_id"] == "thread-output-quality"
    assert len(rows) == 2
    assert rows[1]["operator_enactment_payload"]["action"] == "resume_verification"


def test_live_probe_stops_before_full_matrix_when_baseline_does_not_reproduce(
    tmp_path, monkeypatch
) -> None:
    @contextmanager
    def _fake_env():
        yield {"CODEX_HOME": str(tmp_path / "codex-home")}

    def _workspace(*, provider, lane, scenario_id, repeat_index):
        path = tmp_path / scenario_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _single_turn(**kwargs):
        return {
            "state": {
                "command": ["codex", "exec"],
                "exit_code": 0,
                "stdout": "{}\n",
                "stderr": "",
                "records": [],
            },
            "failure_class": None,
            "model": kwargs["model"],
            "attempted_models": [kwargs["model"]],
            "thread_id": "thread-safe",
            "output_text": "Incomplete: I did not run tests, so this is not verified.",
        }

    monkeypatch.setattr(probe.openai_operator_cli, "isolated_codex_home_env", _fake_env)
    monkeypatch.setattr(probe, "PRIMARY_TASK_FAMILIES", ("unsupported_verification",))
    monkeypatch.setattr(probe, "prepare_harness_workspace", _workspace)
    monkeypatch.setattr(probe.openai_operator_cli, "run_openai_operator_single_turn", _single_turn)
    monkeypatch.setattr(probe, "collect_modified_files", lambda _workspace: [])

    report = run_live_probe(
        output_root=tmp_path / "out",
        model="gpt-test",
        baseline_gate_trials=2,
        full_trials=1,
        clean_control_trials=1,
    )

    assert report["active_families"] == []
    assert report["decision"]["verdict"] == "baseline_not_reproduced"
    assert report["full_matrix"] == {}
    assert (tmp_path / "out").exists()
