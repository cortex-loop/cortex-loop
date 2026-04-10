"""Focused tests for the E12 comparative output-quality runner."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

import pytest

from lab import cortex_output_quality as output_quality
from lab.live_validation_common import collect_modified_files
from lab.output_quality_ablation import OutputQualityAblationConfig
from lab.output_quality_grader import OutputQualityEvaluation, PairwiseJudgment


def test_supported_task_ids_cover_all_five_output_quality_tasks() -> None:
    assert output_quality.supported_task_ids() == (
        "astro_docs_site_v1",
        "astro_marketing_forms_v1",
        "react_dashboard_v1",
        "react_existing_feature_extension_v1",
        "frontend_bugfix_cleanup_v1",
    )


def test_task_prompts_use_human_language_without_hidden_rubric_leaks() -> None:
    banned_terms = (
        "waterfall",
        "back/forward",
        "server/client",
        "gratutious",
        "client-side fetch",
    )

    for task_id in output_quality.supported_task_ids():
        prompt = output_quality.task_pack_by_name(task_id).prompt_text
        normalized = prompt.lower()
        assert "maintainable" in normalized
        assert any(
            phrase in normalized
            for phrase in (
                "best practices",
                "keep the structure stable",
            )
        )
        assert "additional verifier-only checks may run" in prompt
        for banned_term in banned_terms:
            assert banned_term not in normalized


def test_build_pairwise_results_maps_blind_labels_back_to_arms(monkeypatch) -> None:
    task_pack = output_quality.task_pack_by_name("astro_docs_site_v1")
    monkeypatch.setattr(output_quality, "stable_pair_order", lambda _seed: ("b", "a"))
    monkeypatch.setattr(
        output_quality,
        "judge_pairwise_merge_worthiness",
        lambda **_kwargs: PairwiseJudgment(
            winner="a",
            confidence="high",
            reason_tags=("maintainability",),
            objective_override=False,
        ),
    )

    pairwise = output_quality._build_pairwise_results(
        task_pack=task_pack,
        arms=("raw", "tooling_only", "cortex"),
        arm_results={
            "raw": {"evaluation": {"objective_pass": True, "hidden_quality_pass": True}, "changed_files": {}},
            "tooling_only": {"evaluation": {"objective_pass": True, "hidden_quality_pass": True}, "changed_files": {}},
            "cortex": {"evaluation": {"objective_pass": True, "hidden_quality_pass": True}, "changed_files": {}},
        },
    )

    assert pairwise[0]["left_arm"] == "cortex"
    assert pairwise[0]["right_arm"] == "raw"
    assert pairwise[0]["winner_arm"] == "raw"
    assert pairwise[1]["winner_arm"] == "tooling_only"


def test_build_suite_summary_counts_pairwise_wins() -> None:
    summary = output_quality._build_suite_summary(
        run_root=Path("/tmp/output-quality"),
        task_ids=("astro_docs_site_v1",),
        arms=("raw", "tooling_only", "cortex"),
        model="gpt-5.4",
        task_results={},
        aggregate_objective={"raw": 0, "tooling_only": 1, "cortex": 1},
        aggregate_hidden={"raw": 0, "tooling_only": 1, "cortex": 1},
        pairwise_results=[
            {
                "task_id": "astro_docs_site_v1",
                "left_arm": "cortex",
                "right_arm": "raw",
                "winner_arm": "cortex",
                "confidence": "high",
                "reason_tags": ["quality"],
                "objective_override": False,
            },
            {
                "task_id": "astro_docs_site_v1",
                "left_arm": "cortex",
                "right_arm": "tooling_only",
                "winner_arm": None,
                "confidence": "low",
                "reason_tags": ["tie"],
                "objective_override": False,
            },
        ],
        env_blocked=False,
        ablation_config=OutputQualityAblationConfig(verification_binding="off"),
    )

    assert summary["pairwise_summary"]["cortex_vs_raw"]["wins"] == 1
    assert summary["pairwise_summary"]["cortex_vs_raw"]["win_rate"] == 1.0
    assert summary["pairwise_summary"]["cortex_vs_tooling_only"]["ties"] == 1
    assert summary["ablation_config"]["verification_binding"] == "off"
    assert summary["surface"] == "operator_cli"


def test_build_output_quality_operator_prompt_uses_workspace_editing_not_file_blocks() -> None:
    task_pack = output_quality.task_pack_by_name("astro_docs_site_v1")

    prompt = output_quality.build_output_quality_operator_prompt(task_pack, arm="tooling_only")

    assert "Edit the workspace directly" in prompt
    assert "=== FILE:" not in prompt
    assert "Visible contract files follow." in prompt


def test_run_arm_skips_repair_when_verification_binding_is_off(
    tmp_path: Path,
    monkeypatch,
) -> None:
    task_pack = output_quality.task_pack_by_name("astro_docs_site_v1")
    execute_calls: list[dict[str, object]] = []

    monkeypatch.setattr(
        output_quality,
        "_execute_openai_turn",
        lambda **kwargs: execute_calls.append(kwargs) or {
            "response_id": "resp-1",
            "output_text": "=== FILE: src/App.tsx ===\nexport default function App() { return null }\n=== END FILE ===\n",
            "raw_events": [],
        },
    )
    monkeypatch.setattr(
        output_quality,
        "prepare_seeded_workspace",
        lambda **_kwargs: tmp_path,
    )
    monkeypatch.setattr(
        output_quality,
        "_evaluate_turn_output",
        lambda **_kwargs: {
            "evaluation": {
                "status": "failed",
                "failure_class": "hidden_test_failed",
                "objective_pass": True,
                "hidden_quality_pass": False,
                "failing_checks": ["hidden_test"],
                "first_failure_excerpt": "missing hidden integration",
                "checks": [],
            },
            "changed_files": {},
            "repairable": True,
            "parse": {
                "parse_error": None,
                "blocked_reason": None,
                "blocked_message": None,
                "parsed_paths": [],
            },
        },
    )
    monkeypatch.setattr(output_quality, "write_json", lambda *_args, **_kwargs: None)

    result = output_quality._run_arm(
        task_pack=task_pack,
        arm="cortex",
        model="gpt-5.4",
        surface="service_api",
        task_root=tmp_path,
        seed_workspace=tmp_path,
        shared_install_result={"exit_code": 0, "stdout": "", "stderr": ""},
        ablation_config=OutputQualityAblationConfig(
            verification_binding="off",
            repair_turn="on",
        ),
    )

    assert result["attempt_count"] == 1
    assert len(execute_calls) == 1


def test_main_requires_service_spend_approval_for_service_api(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CORTEX_LIVE_SERVICE_SPEND_APPROVED", raising=False)
    monkeypatch.setattr(
        output_quality,
        "run_output_quality_suite",
        lambda **_kwargs: pytest.fail("run_output_quality_suite should not be called"),
    )

    with pytest.raises(SystemExit, match="service-lane spend is blocked"):
        output_quality.main(["--surface", "service_api"])


def test_main_defaults_to_operator_cli_without_service_spend_approval(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CORTEX_LIVE_SERVICE_SPEND_APPROVED", raising=False)
    monkeypatch.setattr(
        output_quality,
        "run_output_quality_suite",
        lambda **_kwargs: {"surface": "operator_cli", "arms": [], "pairwise_summary": {}},
    )

    assert output_quality.main([]) == 0


def test_main_allows_operator_cli_without_service_spend_approval(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CORTEX_LIVE_SERVICE_SPEND_APPROVED", raising=False)
    monkeypatch.setattr(
        output_quality,
        "run_output_quality_suite",
        lambda **_kwargs: {"surface": "operator_cli", "arms": [], "pairwise_summary": {}},
    )

    assert output_quality.main(["--surface", "operator_cli"]) == 0


def test_main_passes_private_artifact_root_and_skip_latest_update(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def _fake_run_output_quality_suite(**kwargs):
        captured.update(kwargs)
        return {"surface": "operator_cli", "arms": [], "pairwise_summary": {}}

    monkeypatch.delenv("CORTEX_LIVE_SERVICE_SPEND_APPROVED", raising=False)
    monkeypatch.setattr(output_quality, "run_output_quality_suite", _fake_run_output_quality_suite)

    assert (
        output_quality.main(
            [
                "--surface",
                "operator_cli",
                "--tasks",
                "astro_docs_site_v1",
                "--artifact-root",
                str(tmp_path / "private_runs"),
                "--skip-latest-update",
            ]
        )
        == 0
    )

    assert captured["artifact_root"] == (tmp_path / "private_runs").resolve()
    assert captured["publish_latest"] is False


def test_run_arm_operator_cli_skips_repair_when_verification_binding_is_off(
    tmp_path: Path,
    monkeypatch,
) -> None:
    task_pack = output_quality.task_pack_by_name("astro_docs_site_v1")
    operator_calls: list[dict[str, object]] = []

    @contextmanager
    def _fake_env():
        yield {}

    monkeypatch.setattr(output_quality, "isolated_codex_home_env", _fake_env)
    monkeypatch.setattr(
        output_quality,
        "prepare_seeded_workspace",
        lambda **_kwargs: tmp_path,
    )
    monkeypatch.setattr(
        output_quality,
        "run_openai_operator_single_turn",
        lambda **kwargs: operator_calls.append(kwargs) or {
            "failure_class": None,
            "model": "gpt-5.3-codex",
            "attempted_models": ["gpt-5.3-codex"],
            "thread_id": "thread-1",
            "output_text": "done",
        },
    )
    monkeypatch.setattr(
        output_quality,
        "_evaluate_operator_turn_output",
        lambda **_kwargs: {
            "evaluation": {
                "status": "failed",
                "failure_class": "hidden_test_failed",
                "objective_pass": True,
                "hidden_quality_pass": False,
                "failing_checks": ["hidden_test"],
                "first_failure_excerpt": "missing hidden integration",
                "checks": [],
            },
            "changed_files": {},
            "repairable": True,
            "parse": {
                "parse_error": None,
                "blocked_reason": None,
                "blocked_message": None,
                "parsed_paths": [],
            },
        },
    )
    monkeypatch.setattr(output_quality, "write_json", lambda *_args, **_kwargs: None)

    result = output_quality._run_arm(
        task_pack=task_pack,
        arm="cortex",
        model="gpt-5.3-codex",
        surface="operator_cli",
        task_root=tmp_path,
        seed_workspace=tmp_path,
        shared_install_result={"exit_code": 0, "stdout": "", "stderr": ""},
        ablation_config=OutputQualityAblationConfig(
            verification_binding="off",
            repair_turn="on",
        ),
    )

    assert result["attempt_count"] == 1
    assert len(operator_calls) == 1


def test_prepare_seeded_workspace_initializes_git_for_operator_diffs(tmp_path: Path) -> None:
    template_root = tmp_path / "template"
    seed_root = tmp_path / "seed"
    (template_root / "src").mkdir(parents=True)
    (template_root / "src" / "App.tsx").write_text("export default 1;\n", encoding="utf-8")
    seed_root.mkdir(parents=True)

    workspace = output_quality.prepare_seeded_workspace(
        template_root=template_root,
        seed_workspace_root=seed_root,
        run_root=tmp_path / "run",
    )

    assert (workspace / ".git").exists()
    (workspace / "src" / "App.tsx").write_text("export default 2;\n", encoding="utf-8")

    assert collect_modified_files(workspace) == ["src/App.tsx"]


def test_evaluate_operator_turn_output_uses_workspace_edits_when_files_changed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    template_root = tmp_path / "template"
    seed_root = tmp_path / "seed"
    (template_root / "src").mkdir(parents=True)
    (template_root / "src" / "App.tsx").write_text("export default 1;\n", encoding="utf-8")
    seed_root.mkdir(parents=True)
    workspace = output_quality.prepare_seeded_workspace(
        template_root=template_root,
        seed_workspace_root=seed_root,
        run_root=tmp_path / "workspace",
    )
    (workspace / "src" / "App.tsx").write_text("export default 2;\n", encoding="utf-8")

    task_pack = output_quality.OutputQualityTaskPack(
        task_id="toy_operator_case",
        prompt_text="Fix the file.",
        template_root=template_root,
        allowed_write_paths=("src/App.tsx",),
        visible_context_paths=("src/App.tsx",),
        verifier_only_paths=(),
        install_command=("true",),
        lint_command=("true",),
        typecheck_command=("true",),
        build_command=("true",),
        visible_test_command=("true",),
        hidden_test_command=("true",),
    )

    monkeypatch.setattr(
        output_quality,
        "evaluate_workspace",
        lambda **_kwargs: OutputQualityEvaluation(
            status="passed",
            failure_class=None,
            objective_pass=True,
            hidden_quality_pass=True,
            failing_checks=(),
            first_failure_excerpt=None,
            checks=(),
        ),
    )

    payload = output_quality._evaluate_operator_turn_output(
        task_pack=task_pack,
        project_root=workspace,
        output_text="Implemented the fix.",
        shared_install_result={"exit_code": 0, "stdout": "", "stderr": ""},
        failure_class=None,
        attempted_models=["gpt-5.3-codex"],
        thread_id="thread-1",
    )

    assert payload["evaluation"]["status"] == "passed"
    assert payload["parse"]["parse_error"] is None
    assert payload["changed_files"] == {"src/App.tsx": "export default 2;\n"}
