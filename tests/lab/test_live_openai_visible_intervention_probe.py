"""Tests for the OpenAI grounded visible-intervention live probe."""

from __future__ import annotations

import json
from contextlib import contextmanager
from dataclasses import dataclass

from lab import live_openai_visible_intervention_probe as probe
from lab.live_openai_visible_intervention_probe import run_gate0_audit


def test_gate0_passes_only_with_product_rendered_visible_text(tmp_path) -> None:
    report = run_gate0_audit(output_root=tmp_path)

    assert report["gate0_passed"] is True
    assert report["product_rendered_visible_delta_present"] is True
    assert report["decision"]["live_trials_allowed"] is True

    by_id = {case["scenario_id"]: case for case in report["cases"]}
    visible = by_id["overdue_verification_visible_intervention"]
    general = by_id["non_astro_generalization_control"]
    clean = by_id["clean_no_debt_stays_silent"]
    no_anchor = by_id["missing_prior_anchor_stays_silent"]

    assert visible["visible_delta_present"] is True
    assert visible["visible_text_source"] == "product_renderer"
    assert visible["fixture_prompt_used_for_visible_arm"] is False
    assert visible["visible_forbidden_terms"] == []
    assert visible["visible_enactment_payload"]["action"] == (
        "resume_visible_intervention"
    )
    assert visible["visible_enactment_payload"]["rendered_text"] == (
        "I have not verified the verification opened by this task yet. Need "
        "evidence, a check, or a narrower claim before calling it complete."
    )

    assert general["visible_delta_present"] is True
    assert general["task_id"] == "react_dashboard_v1"
    assert clean["visible_enactment_payload"]["action"] == "stay_silent"
    assert no_anchor["visible_enactment_payload"]["blocked_reason"] == (
        "missing_prior_act_anchor"
    )

    rows = [
        json.loads(line)
        for line in (tmp_path / "gate0_trajectory.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert len(rows) == 8
    for row in rows:
        assert {
            "trial_id",
            "condition",
            "task_family",
            "task_id",
            "input_event",
            "expectation_ledger",
            "resolution_deficit_payload",
            "debt_control_payload",
            "operator_route_payload",
            "grounded_intervention_payload",
            "visible_intervention_enactment_payload",
            "rendered_intervention_text_hash",
            "rendered_intervention_text_excerpt",
            "forbidden_term_scan",
            "initial_prompt_hash",
            "workspace_hash",
            "model_input_hash",
            "model_output_excerpt",
            "artifact_paths",
            "score",
        } <= set(row)
        assert row["forbidden_term_scan"] == []

    visible_rows = [row for row in rows if row["condition"] == "visible_intervention"]
    assert any(
        row["visible_intervention_enactment_payload"]["action"]
        == "resume_visible_intervention"
        for row in visible_rows
    )
    assert "verification_debt_continuation_operator.md" not in str(rows)
    assert "truth_gap_recheck_operator.md" not in str(rows)


def test_visible_trial_uses_rendered_intervention_text_not_prompt_fixture(
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
            "thread_id": "thread-visible",
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
            "thread_id": "thread-visible",
            "output_text": "Verified and repaired the remaining support.",
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
    monkeypatch.setattr(
        probe.openai_operator_cli,
        "run_openai_operator_single_turn",
        _single_turn,
    )
    monkeypatch.setattr(
        probe.openai_operator_cli,
        "run_openai_operator_resumed_turn",
        _resumed_turn,
    )
    monkeypatch.setattr(probe, "collect_modified_files", lambda _workspace: ["src/App.tsx"])

    rows = []
    trial = probe._run_output_quality_trial(
        family="output_quality_visible_success",
        condition="visible_intervention",
        repeat_index=1,
        model="gpt-test",
        trials_root=tmp_path / "trials",
        trajectory_rows=rows,
    )

    assert trial["first_result_kind"] == "visible_success_unverified"
    assert trial["resumed"] is not None
    assert trial["score"]["hidden_quality_pass"] is True
    assert calls["single"][0]["ephemeral"] is False
    assert calls["resume"][0]["thread_id"] == "thread-visible"
    assert calls["resume"][0]["prompt"] == (
        "I have not verified the verification opened by this task yet. Need "
        "evidence, a check, or a narrower claim before calling it complete."
    )
    assert "verification_debt_continuation_operator.md" not in calls["resume"][0]["prompt"]
    assert len(rows) == 2
    assert rows[1]["visible_intervention_enactment_payload"]["action"] == (
        "resume_visible_intervention"
    )
    assert rows[1]["forbidden_term_scan"] == []


def test_silent_only_trial_does_not_resume_with_visible_or_fixture_text(
    tmp_path,
    monkeypatch,
) -> None:
    calls = {"single": [], "resume": []}

    @dataclass(frozen=True)
    class _Evaluation:
        payload: dict[str, object]

        def as_payload(self) -> dict[str, object]:
            return dict(self.payload)

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
            "thread_id": "thread-silent",
            "output_text": "Implemented the requested workspace changes.",
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
    monkeypatch.setattr(
        probe,
        "evaluate_workspace",
        lambda **_kwargs: _Evaluation(
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
    )
    monkeypatch.setattr(
        probe.openai_operator_cli,
        "run_openai_operator_single_turn",
        _single_turn,
    )
    monkeypatch.setattr(
        probe.openai_operator_cli,
        "run_openai_operator_resumed_turn",
        lambda **kwargs: calls["resume"].append(kwargs),
    )
    monkeypatch.setattr(probe, "collect_modified_files", lambda _workspace: ["src/App.tsx"])

    rows = []
    trial = probe._run_output_quality_trial(
        family="output_quality_visible_success",
        condition="silent_only",
        repeat_index=1,
        model="gpt-test",
        trials_root=tmp_path / "trials",
        trajectory_rows=rows,
    )

    assert trial["resumed"] is None
    assert calls["resume"] == []
    assert rows[1]["visible_intervention_enactment_payload"]["action"] == "stay_silent"
    assert rows[1]["visible_intervention_enactment_payload"]["rendered_text"] is None
