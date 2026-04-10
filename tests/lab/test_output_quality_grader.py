"""Focused tests for the E12 hidden output-quality grader."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

from lab import output_quality_grader as grader
from lab.output_quality_common import OutputQualityTaskPack


def _task_pack(tmp_path: Path) -> OutputQualityTaskPack:
    template_root = tmp_path / "template"
    template_root.mkdir()
    return OutputQualityTaskPack(
        task_id="sample",
        prompt_text="Implement this in a clean, maintainable way.",
        template_root=template_root,
        allowed_write_paths=("src/app.ts",),
        visible_context_paths=(),
        verifier_only_paths=(),
        install_command=("npm", "ci"),
        lint_command=("npm", "run", "lint"),
        typecheck_command=("npm", "run", "typecheck"),
        build_command=("npm", "run", "build"),
        visible_test_command=("npm", "run", "test:visible"),
        hidden_test_command=("npm", "run", "test:hidden"),
    )


def test_evaluate_workspace_hidden_failure_keeps_objective_pass_true(
    tmp_path: Path,
    monkeypatch,
) -> None:
    task_pack = _task_pack(tmp_path)

    def _fake_run_command(command, *, cwd, timeout_seconds):
        _ = cwd, timeout_seconds
        check = command[-1]
        if check == "lint":
            return {"command": command, "exit_code": 0, "stdout": "", "stderr": ""}
        if check == "typecheck":
            return {"command": command, "exit_code": 0, "stdout": "", "stderr": ""}
        if check == "build":
            return {"command": command, "exit_code": 0, "stdout": "", "stderr": ""}
        if check == "test:visible":
            return {"command": command, "exit_code": 0, "stdout": "", "stderr": ""}
        if check == "test:hidden":
            return {
                "command": command,
                "exit_code": 1,
                "stdout": "expected nav integration",
                "stderr": "",
            }
        raise AssertionError(f"unexpected command: {command}")

    monkeypatch.setattr(grader, "run_command", _fake_run_command)

    evaluation = grader.evaluate_workspace(
        task_pack=task_pack,
        project_root=tmp_path,
        shared_install_result={"command": ["npm", "ci"], "exit_code": 0, "stdout": "", "stderr": ""},
    )

    assert evaluation.status == "failed"
    assert evaluation.failure_class == "hidden_test_failed"
    assert evaluation.objective_pass is True
    assert evaluation.hidden_quality_pass is False
    assert evaluation.failing_checks == ("hidden_test",)


def test_build_output_quality_repair_ticket_includes_paths_and_failures() -> None:
    evaluation = grader.OutputQualityEvaluation(
        status="failed",
        failure_class="hidden_test_failed",
        objective_pass=True,
        hidden_quality_pass=False,
        failing_checks=("hidden_test",),
        first_failure_excerpt="missing nav integration",
        checks=(),
    )

    ticket = grader.build_output_quality_repair_ticket(
        evaluation=evaluation,
        allowed_write_paths=("src/app.ts", "src/nav.tsx"),
    )

    assert "failure_class: hidden_test_failed" in ticket
    assert "failing_checks: hidden_test" in ticket
    assert "allowed_write_paths: src/app.ts, src/nav.tsx" in ticket


def test_build_output_quality_repair_ticket_supports_minimal_style() -> None:
    evaluation = grader.OutputQualityEvaluation(
        status="failed",
        failure_class="build_failed",
        objective_pass=False,
        hidden_quality_pass=False,
        failing_checks=("build",),
        first_failure_excerpt="build failed",
        checks=(),
    )

    ticket = grader.build_output_quality_repair_ticket(
        evaluation=evaluation,
        allowed_write_paths=("src/app.ts",),
        style="minimal",
        repair_surface=("src/app.ts",),
    )

    assert "failure_class: build_failed" in ticket
    assert "failing_checks: build" in ticket
    assert "repair_surface: src/app.ts" in ticket
    assert "allowed_write_paths:" not in ticket


def test_judge_pairwise_merge_worthiness_uses_objective_override() -> None:
    judgment = grader.judge_pairwise_merge_worthiness(
        prompt_text="Build the feature cleanly.",
        output_a={
            "evaluation": {
                "objective_pass": True,
                "hidden_quality_pass": False,
                "failure_class": None,
                "failing_checks": [],
                "first_failure_excerpt": None,
            },
            "changed_files": {},
        },
        output_b={
            "evaluation": {
                "objective_pass": False,
                "hidden_quality_pass": False,
                "failure_class": "build_failed",
                "failing_checks": ["build"],
                "first_failure_excerpt": "build failed",
            },
            "changed_files": {},
        },
    )

    assert judgment.winner == "a"
    assert judgment.objective_override is True
    assert judgment.reason_tags == ("objective-gate",)


def test_parse_judge_payload_normalizes_invalid_payload() -> None:
    parsed = grader._parse_judge_payload("winner: a")

    assert parsed["winner"] is None
    assert parsed["confidence"] == "low"
    assert parsed["reason_tags"] == ["judge-unparseable"]


def test_judge_pairwise_merge_worthiness_operator_cli_uses_cli_helper(
    monkeypatch,
) -> None:
    @contextmanager
    def _fake_env():
        yield {}

    monkeypatch.setattr(grader, "isolated_codex_home_env", _fake_env)
    monkeypatch.setattr(
        grader,
        "run_openai_operator_single_turn",
        lambda **_kwargs: {
            "failure_class": None,
            "output_text": '{"winner":"b","confidence":"medium","reason_tags":["quality"]}',
        },
    )

    judgment = grader.judge_pairwise_merge_worthiness(
        prompt_text="Build the feature cleanly.",
        output_a={
            "evaluation": {
                "objective_pass": True,
                "hidden_quality_pass": True,
                "failure_class": None,
                "failing_checks": [],
                "first_failure_excerpt": None,
            },
            "changed_files": {},
        },
        output_b={
            "evaluation": {
                "objective_pass": True,
                "hidden_quality_pass": True,
                "failure_class": None,
                "failing_checks": [],
                "first_failure_excerpt": None,
            },
            "changed_files": {},
        },
        surface="operator_cli",
    )

    assert judgment.winner == "b"
    assert judgment.reason_tags == ("quality",)
