"""Contract tests for the Cortex overnight evaluator loop guardrail."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from internal.automation import cortex_overnight_loop as loop


def _status(
    slug: str = "cortex-executive-effectiveness-evaluator-build",
    *,
    surface: str = "no-live lab/proof evaluator build",
    guardrail: str = "No live Codex run. No product host behavior change.",
    primary_metric: str = "Build evaluator_design.json, episode_table.jsonl, summary.json, and leaderboard.json.",
    kill_rule: str = "Fail if simple or silent succeeds equally.",
) -> dict[str, object]:
    return {
        "next_product_train": {
            "slug": slug,
            "surface": surface,
            "guardrail": guardrail,
            "primary_metric": primary_metric,
            "kill_rule": kill_rule,
        }
    }


def _git(
    *,
    branch: str = "main",
    dirty: bool = False,
    synced: bool = True,
    managed: bool | None = None,
) -> loop.GitState:
    return loop.GitState(
        branch=branch,
        dirty=dirty,
        synced=synced,
        managed_branch=branch.startswith(("codex/", "claude/", "maint/")) if managed is None else managed,
        status_short=" M file.py\n" if dirty else "",
    )


def test_classify_next_work_allows_clean_evaluator_build_auto_merge() -> None:
    decision = loop.classify_next_work(_status(), _git())

    assert decision.status == "ready"
    assert decision.next_slug == "cortex-executive-effectiveness-evaluator-build"
    assert decision.safe_to_auto_merge is True
    assert decision.live_codex_allowed is False
    assert decision.user_input_required is False
    assert "start-session" in decision.recommended_commands[0]


def test_classify_next_work_refuses_dirty_main_but_allows_managed_resume() -> None:
    dirty_main = loop.classify_next_work(_status(), _git(dirty=True))
    managed_branch = loop.classify_next_work(
        _status(),
        _git(branch="codex/20260508-210934-cortex-overnight-evaluator-automation-hardening", dirty=True),
    )

    assert dirty_main.status == "blocked"
    assert "dirty resting state" in dirty_main.reasons[0]
    assert managed_branch.status == "ready"
    assert managed_branch.recommended_commands[0].startswith("continue managed session branch")


def test_classify_next_work_refuses_strategic_or_paid_boundaries() -> None:
    product_law = loop.classify_next_work(
        _status(guardrail="Requires product law revision before continuing."),
        _git(),
    )
    external_paid = loop.classify_next_work(
        _status(guardrail="Requires external paid service-lane credentials."),
        _git(),
    )

    assert product_law.status == "blocked"
    assert product_law.user_input_required is True
    assert external_paid.status == "blocked"
    assert external_paid.user_input_required is True


def test_classify_next_work_allows_registered_live_but_never_auto_merges() -> None:
    decision = loop.classify_next_work(
        _status(
            slug="cortex-executive-effectiveness-evaluator-live-matrix",
            surface="approval-gated live evaluator proof",
            guardrail="Codex CLI live matrix is allowed inside registered evaluator plan.",
            primary_metric="Run live evaluator matrix only after deterministic replay.",
        ),
        _git(),
    )

    assert decision.status == "ready"
    assert decision.live_codex_allowed is True
    assert decision.safe_to_auto_merge is False


def test_bloat_metrics_detects_policy_growth_and_contraction() -> None:
    growth = loop.bloat_metrics_from_numstat(
        "25\t3\tcortex/hosts/openai/new_policy.py\n"
        "2\t0\tdocs/recon/example.md\n"
    )
    contraction = loop.bloat_metrics_from_numstat(
        "3\t40\tcortex/hosts/openai/posttooluse_task_standard_actuator.py\n"
    )

    assert growth.loc_added == 27
    assert growth.loc_deleted == 3
    assert growth.new_policy_paths == ("cortex/hosts/openai/new_policy.py",)
    assert growth.contraction_debt_increased is True
    assert contraction.duplicate_policy_removed is True
    assert contraction.contraction_debt_increased is False


def test_bloat_metrics_counts_untracked_files(tmp_path: Path) -> None:
    new_file = tmp_path / "internal/automation/new_runner.py"
    new_file.parent.mkdir(parents=True)
    new_file.write_text("one\n two\n", encoding="utf-8")
    bloat = loop._with_untracked_files(
        tmp_path,
        loop.bloat_metrics_from_numstat("1\t0\tdocs/recon/example.md\n"),
        ("internal/automation/new_runner.py",),
    )

    assert bloat.loc_added == 3
    assert "internal/automation/new_runner.py" in bloat.changed_files


def test_candidate_guards_find_forbidden_paths_and_task_specific_harness() -> None:
    paths = [
        "cortex/core/dispatch.py",
        "docs/CORTEX_V2_CORE_2.md",
        "internal/workflow/repo_workflow.py",
        "tests/fixtures/hidden_scoring_case.json",
        "lab/codex_app_cli_hook_native_behavior_comparison.py",
    ]
    bloat = loop.BloatMetrics(
        loc_added=10,
        loc_deleted=0,
        changed_files=tuple(paths),
        new_policy_paths=(),
        duplicate_policy_removed=False,
        contraction_debt_increased=False,
    )
    decision = loop.classify_next_work(_status(), _git(), bloat)

    assert "cortex/core/dispatch.py" in loop.forbidden_candidate_paths(paths)
    assert "docs/CORTEX_V2_CORE_2.md" in loop.forbidden_candidate_paths(paths)
    assert "internal/workflow/repo_workflow.py" in loop.forbidden_candidate_paths(paths)
    assert "tests/fixtures/hidden_scoring_case.json" in loop.forbidden_candidate_paths(paths)
    assert loop.task_specific_harness_paths(paths) == (
        "lab/codex_app_cli_hook_native_behavior_comparison.py",
    )
    assert decision.status == "blocked"
    assert any("general evaluator episode rows" in reason for reason in decision.reasons)


def test_repeated_simple_baseline_losses_create_contraction_candidates() -> None:
    rows = [
        {"candidate_id": "a", "policy_candidate": "posttooluse_stop", "failure_class": "failure_simple_baseline_parity"},
        {"candidate_id": "b", "policy_candidate": "posttooluse_stop", "failure_class": "failure_simple_baseline_parity"},
        {"candidate_id": "c", "policy_candidate": "stop_only", "failure_class": "pass_active_value"},
    ]

    assert loop.repeated_simple_baseline_losses(rows) == ("posttooluse_stop",)


def test_run_once_emits_digest_even_when_blocked(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(loop, "load_status", lambda root: _status())
    monkeypatch.setattr(loop, "inspect_git_state", lambda root: _git(dirty=True))
    monkeypatch.setattr(
        loop,
        "collect_bloat_metrics",
        lambda root: loop.BloatMetrics(
            loc_added=0,
            loc_deleted=0,
            changed_files=(),
            new_policy_paths=(),
            duplicate_policy_removed=False,
            contraction_debt_increased=False,
        ),
    )

    report = loop.run_once(
        tmp_path,
        now=datetime(2026, 5, 8, 23, tzinfo=timezone.utc),
        digest_root=tmp_path / "digests",
    )

    assert report["decision"]["status"] == "blocked"
    digest_path = Path(report["digest_path"])
    assert digest_path.exists()
    text = digest_path.read_text()
    assert "Cortex Overnight Digest" in text
    assert "dirty resting state" in text
    assert "User Input Needed" in text


def test_candidate_record_schema_is_complete() -> None:
    assert set(loop.CANDIDATE_RECORD_FIELDS) == {
        "candidate_id",
        "parent_id",
        "policy_candidate",
        "changed_files",
        "mutation_reason",
        "metrics",
        "score",
        "failure_class",
        "contraction_implication",
    }
