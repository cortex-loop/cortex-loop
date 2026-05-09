"""Contract tests for the Cortex overnight evaluator loop guardrail."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from internal.automation import cortex_overnight_loop as loop


def _status(
    slug: str = "cortex-executive-effectiveness-evaluator-build",
    *,
    work_slug: str | None = None,
    work_note: str = "",
    surface: str = "no-live lab/proof evaluator build",
    guardrail: str = "No live Codex run. No product host behavior change.",
    primary_metric: str = "Build evaluator_design.json, episode_table.jsonl, summary.json, and leaderboard.json.",
    kill_rule: str = "Fail if simple or silent succeeds equally.",
    extra: dict[str, object] | None = None,
) -> dict[str, object]:
    next_train: dict[str, object] = {
        "slug": slug,
        "surface": surface,
        "guardrail": guardrail,
        "primary_metric": primary_metric,
        "kill_rule": kill_rule,
    }
    if extra:
        next_train.update(extra)
    return {
        "work_today": {
            "slug": work_slug or slug,
            "note": work_note,
        },
        "next_product_train": next_train,
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


def test_classify_next_work_allows_simple_hook_and_live_gate1_sequence() -> None:
    live_gate = loop.classify_next_work(
        _status(
            slug="cortex-executive-effectiveness-evaluator-live-gate1",
            surface="no-live lab/proof evaluator live-interface gate",
            guardrail="No live Codex run in this seam.",
            primary_metric="Register future live command/env pairs.",
        ),
        _git(),
    )
    simple_hook = loop.classify_next_work(
        _status(
            slug="cortex-simple-hook-baseline-challenger",
            surface="no-live lab/proof evaluator baseline",
            guardrail="No live Codex run in this seam.",
            primary_metric="Implement the simple-hook challenger.",
        ),
        _git(),
    )

    assert live_gate.status == "ready"
    assert "python3 lab/cortex_effectiveness_evaluator.py --live-gate1 --require-pass" in live_gate.allowed_commands
    assert simple_hook.status == "ready"
    assert (
        "python3 lab/cortex_effectiveness_evaluator.py --simple-hook-baseline-gate0 --require-pass"
        in simple_hook.allowed_commands
    )
    assert simple_hook.live_codex_allowed is False


def test_classify_next_work_allows_measurement_stack_rebuild_with_strict_packet() -> None:
    decision = loop.classify_next_work(
        _status(
            slug="cortex-effectiveness-measurement-stack-rebuild",
            surface="no-live lab/proof evaluator measurement-stack remediation",
            guardrail=(
                "No live Codex run. Do not change product behavior, scoring to favor Cortex, "
                "hidden-verifier boundaries, or positive value claims."
            ),
            primary_metric=(
                "Preserve failure_silent_perception_contamination and rebuild measurement "
                "without crediting simple-hook parity."
            ),
        ),
        _git(),
    )

    assert decision.status == "ready"
    assert decision.safe_to_auto_merge is True
    assert decision.live_codex_allowed is False
    assert (
        "python3 lab/cortex_effectiveness_evaluator.py --measurement-stack-rebuild-gate0 --require-pass"
        in decision.allowed_commands
    )


def test_classify_next_work_allows_v2_live_matrix_gate1_no_live() -> None:
    decision = loop.classify_next_work(
        _status(
            slug="cortex-effectiveness-v2-live-matrix-gate1",
            surface="no-live lab/proof evaluator v2 live-matrix interface",
            guardrail="No live Codex run in this seam.",
            primary_metric=(
                "Produce a 60-row v2 live-matrix dry-run plan from the v2 case registry."
            ),
        ),
        _git(),
    )

    assert decision.status == "ready"
    assert decision.safe_to_auto_merge is True
    assert decision.live_codex_allowed is False
    assert (
        "python3 lab/cortex_effectiveness_evaluator.py --v2-live-matrix-gate1 --require-pass"
        in decision.allowed_commands
    )


def test_classify_next_work_allows_registered_v2_live_but_never_auto_merges() -> None:
    decision = loop.classify_next_work(
        _status(
            slug="cortex-effectiveness-v2-live-matrix-run",
            surface="approval-gated live evaluator v2 matrix run",
            guardrail="Codex CLI v2 live matrix is allowed only through the exact registered command/env pair.",
            primary_metric="Run the v2 live evaluator matrix after no-spend preflight.",
            extra={
                "registered_live_commands": [
                    {
                        "command": "python3 lab/cortex_effectiveness_evaluator.py --v2-live-matrix",
                        "env": {
                            "CORTEX_CODEX_APP_CLI_EVALUATOR_LIVE_APPROVED": "approved"
                        },
                    }
                ]
            },
        ),
        _git(),
    )

    assert decision.status == "ready"
    assert decision.live_codex_allowed is True
    assert decision.safe_to_auto_merge is False
    assert (
        "CORTEX_CODEX_APP_CLI_EVALUATOR_LIVE_APPROVED=approved python3 lab/cortex_effectiveness_evaluator.py --v2-live-matrix"
        in decision.allowed_commands
    )


def test_fresh_chat_work_packet_forces_repo_grounding_and_anti_reinvention() -> None:
    status = _status(
        slug="cortex-effectiveness-measurement-stack-rebuild",
        surface="no-live lab/proof evaluator measurement-stack remediation",
    )
    decision = loop.classify_next_work(status, _git())
    packet = loop.build_work_packet(status, _git(), decision)

    assert packet.do_not_use_prior_chat_context is True
    assert packet.blocked_is_success is True
    assert packet.model_io_path == loop.LAB_PROOF_MODEL_IO_PATH
    assert packet.current_binding_evidence["artifact"] == "run_20260508T221352Z"
    assert packet.current_binding_evidence["verdict"] == "failure_silent_perception_contamination"
    assert "internal/truth/cortex_status.json" in packet.required_boot_reads
    assert "lab/cortex_effectiveness_evaluator.py" in packet.required_code_owner_reads
    assert any("failure_silent_perception_contamination" in command for command in packet.anti_reinvention_searches)
    assert any("why this cycle is allowed" in item for item in packet.orientation_checklist)
    assert any("blocked is a successful" in rule for rule in packet.stop_rules)


def test_v2_live_matrix_gate1_packet_forces_registry_grounding() -> None:
    status = _status(
        slug="cortex-effectiveness-v2-live-matrix-gate1",
        surface="no-live lab/proof evaluator v2 live-matrix interface",
    )
    decision = loop.classify_next_work(status, _git())
    packet = loop.build_work_packet(status, _git(), decision)

    assert packet.model_io_path == loop.LAB_PROOF_MODEL_IO_PATH
    assert (
        ".cortex/live_validation/cortex_effectiveness_v2_case_registry_gate0/v2_case_registry.json"
        in packet.required_code_owner_reads
    )
    assert any(
        "build_v2_live_matrix_plan" in command
        for command in packet.anti_reinvention_searches
    )
    assert any(
        "failure_silent_perception_contamination" in command
        for command in packet.anti_reinvention_searches
    )


def test_v2_live_matrix_run_packet_forces_gate1_and_runner_grounding() -> None:
    status = _status(
        slug="cortex-effectiveness-v2-live-matrix-run",
        surface="approval-gated live evaluator v2 matrix run",
        extra={
            "registered_live_commands": [
                {
                    "command": "python3 lab/cortex_effectiveness_evaluator.py --v2-live-matrix",
                    "env": {
                        "CORTEX_CODEX_APP_CLI_EVALUATOR_LIVE_APPROVED": "approved"
                    },
                }
            ]
        },
    )
    decision = loop.classify_next_work(status, _git())
    packet = loop.build_work_packet(status, _git(), decision)

    assert (
        ".cortex/live_validation/cortex_effectiveness_v2_live_matrix_gate1/live_plan.json"
        in packet.required_code_owner_reads
    )
    assert any(
        "run_cortex_effectiveness_v2_live_matrix" in command
        for command in packet.anti_reinvention_searches
    )
    assert any("--v2-live-matrix" in command for command in packet.allowed_commands)


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
            slug="cortex-executive-effectiveness-evaluator-live-matrix-run",
            surface="approval-gated live evaluator proof",
            guardrail="Codex CLI live matrix is allowed inside registered evaluator plan.",
            primary_metric="Run live evaluator matrix only after deterministic replay.",
            extra={
                "registered_live_commands": [
                    {
                        "command": "python3 lab/cortex_effectiveness_evaluator.py --live-matrix",
                        "env": {
                            "CORTEX_CODEX_APP_CLI_EVALUATOR_LIVE_APPROVED": "approved"
                        },
                    }
                ]
            },
        ),
        _git(),
    )

    assert decision.status == "ready"
    assert decision.live_codex_allowed is True
    assert decision.safe_to_auto_merge is False
    assert (
        "CORTEX_CODEX_APP_CLI_EVALUATOR_LIVE_APPROVED=approved python3 lab/cortex_effectiveness_evaluator.py --live-matrix"
        in decision.allowed_commands
    )


def test_classify_next_work_refuses_unregistered_live() -> None:
    decision = loop.classify_next_work(
        _status(
            slug="cortex-executive-effectiveness-evaluator-live-matrix-run",
            surface="approval-gated live evaluator proof",
            guardrail="Codex CLI live matrix is allowed inside registered evaluator plan.",
            primary_metric="Run live evaluator matrix only after deterministic replay.",
        ),
        _git(),
    )

    assert decision.status == "blocked"
    assert any("exact registered command" in reason for reason in decision.reasons)


def test_classify_next_work_enforces_overnight_hours_and_noop_dedupe() -> None:
    off_hours = loop.classify_next_work(
        _status(),
        _git(),
        now=datetime(2026, 5, 8, 12, tzinfo=timezone.utc),
    )
    no_op = loop.classify_next_work(
        _status(),
        _git(),
        now=datetime(2026, 5, 8, 23, tzinfo=timezone.utc),
        previous_cycle={
            "decision": {
                "status": "ready",
                "next_slug": "cortex-executive-effectiveness-evaluator-build",
            },
            "git_state": {"branch": "main"},
        },
    )

    assert off_hours.status == "blocked"
    assert any("outside the registered overnight" in reason for reason in off_hours.reasons)
    assert no_op.status == "blocked"
    assert any("no-op cycle" in reason for reason in no_op.reasons)


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
    assert growth.non_test_loc_added == 27
    assert growth.policy_lab_loc_added == 25
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


def test_non_test_loc_budget_blocks_non_exempt_growth() -> None:
    bloat = loop.BloatMetrics(
        loc_added=300,
        loc_deleted=0,
        changed_files=("internal/automation/large.py",),
        new_policy_paths=(),
        duplicate_policy_removed=False,
        contraction_debt_increased=False,
        non_test_loc_added=300,
    )
    blocked = loop.classify_next_work(
        _status(slug="cortex-executive-effectiveness-evaluator-followup"),
        _git(),
        bloat,
    )
    exempt = loop.classify_next_work(_status(), _git(), bloat)

    assert blocked.status == "blocked"
    assert any("non-test LOC budget" in reason for reason in blocked.reasons)
    assert exempt.status == "ready"


def test_simple_hook_baseline_is_bloat_exempt_but_not_live_allowed() -> None:
    bloat = loop.BloatMetrics(
        loc_added=430,
        loc_deleted=0,
        changed_files=(
            "lab/cortex_simple_hook_baseline.py",
            "lab/cortex_effectiveness_evaluator.py",
        ),
        new_policy_paths=(),
        duplicate_policy_removed=False,
        contraction_debt_increased=False,
        non_test_loc_added=430,
        policy_lab_loc_added=430,
        policy_lab_loc_deleted=0,
    )
    decision = loop.classify_next_work(
        _status(
            slug="cortex-simple-hook-baseline-challenger",
            surface="no-live lab/proof evaluator baseline",
            guardrail="No live Codex run in this seam.",
            primary_metric="Implement the simple-hook challenger.",
        ),
        _git(),
        bloat,
    )

    assert decision.status == "ready"
    assert decision.live_codex_allowed is False


def test_managed_current_work_slug_preserves_build_exemption_after_next_train_advances() -> None:
    bloat = loop.BloatMetrics(
        loc_added=700,
        loc_deleted=0,
        changed_files=("lab/cortex_effectiveness_evaluator.py",),
        new_policy_paths=(),
        duplicate_policy_removed=False,
        contraction_debt_increased=False,
        non_test_loc_added=700,
        policy_lab_loc_added=300,
        policy_lab_loc_deleted=0,
    )

    decision = loop.classify_next_work(
        _status(
            slug="cortex-executive-effectiveness-evaluator-live-gate1",
            work_slug="cortex-executive-effectiveness-evaluator-build",
            work_note=(
                "The Cortex executive effectiveness evaluator build passed as a "
                "no-live lab/proof seam. No live Codex run occurred."
            ),
            surface="no-live lab/proof evaluator live-interface gate",
            guardrail="No live Codex run in this seam.",
        ),
        _git(
            branch=(
                "codex/20260508-214601-"
                "cortex-executive-effectiveness-evaluator-build"
            ),
            dirty=True,
        ),
        bloat,
    )

    assert decision.status == "ready"
    assert decision.next_slug == "cortex-executive-effectiveness-evaluator-build"
    assert (
        "python3 lab/cortex_effectiveness_evaluator.py --build --require-pass"
        in decision.allowed_commands
    )


def test_policy_lab_growth_requires_contraction_candidate_outside_build() -> None:
    bloat = loop.BloatMetrics(
        loc_added=20,
        loc_deleted=0,
        changed_files=("lab/new_policy_search.py",),
        new_policy_paths=(),
        duplicate_policy_removed=False,
        contraction_debt_increased=False,
        non_test_loc_added=20,
        policy_lab_loc_added=20,
        policy_lab_loc_deleted=0,
    )
    blocked = loop.classify_next_work(
        _status(slug="cortex-executive-effectiveness-evaluator-followup"),
        _git(),
        bloat,
    )
    allowed_with_contraction = loop.classify_next_work(
        _status(slug="cortex-executive-effectiveness-evaluator-followup"),
        _git(),
        bloat,
        candidate_contraction=("posttooluse_stop",),
    )

    assert blocked.status == "blocked"
    assert any("contraction candidate" in reason for reason in blocked.reasons)
    assert allowed_with_contraction.status == "ready"


def _candidate_row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "candidate_id": "candidate-001",
        "parent_id": "champion",
        "policy_candidate": "posttooluse_stop",
        "executive_function": "truthful_closure",
        "loop_stage": "improved_model_behavior",
        "control_mode": "model_visible_context",
        "truth_scope": "shipping_truth",
        "model_io_path": "Codex PostToolUse hookSpecificOutput.additionalContext",
        "product_spine": [
            "truthful_closure",
            "task_standard_state_law",
            "posttooluse_context_decision",
            "Codex PostToolUse",
            "hookSpecificOutput.additionalContext",
        ],
        "changed_files": ["cortex/hosts/openai/posttooluse_task_standard_actuator.py"],
        "authorized_by_next_train": "cortex-executive-effectiveness-evaluator-followup",
        "mutation_reason": "bounded policy candidate",
        "metrics": {},
        "score": 0,
        "failure_class": "failure_simple_baseline_parity",
        "contraction_implication": "none_with_reason",
    }
    row.update(overrides)
    return row


def test_lab_eval_changes_are_support_not_product_with_contraction() -> None:
    bloat = loop.BloatMetrics(
        loc_added=12,
        loc_deleted=0,
        changed_files=("lab/evaluator_support.py",),
        new_policy_paths=(),
        duplicate_policy_removed=False,
        contraction_debt_increased=False,
        non_test_loc_added=12,
        policy_lab_loc_added=12,
        policy_lab_loc_deleted=0,
    )
    decision = loop.classify_next_work(
        _status(slug="cortex-executive-effectiveness-evaluator-followup"),
        _git(),
        bloat,
        candidate_contraction=("old_posttooluse_gate0",),
    )

    assert decision.status == "ready"
    assert decision.safe_to_auto_merge is True


def test_cortex_candidate_changes_require_product_spine_and_model_io_path() -> None:
    bloat = loop.BloatMetrics(
        loc_added=10,
        loc_deleted=0,
        changed_files=("cortex/hosts/openai/posttooluse_task_standard_actuator.py",),
        new_policy_paths=("cortex/hosts/openai/posttooluse_task_standard_actuator.py",),
        duplicate_policy_removed=False,
        contraction_debt_increased=True,
        non_test_loc_added=10,
        policy_lab_loc_added=10,
        policy_lab_loc_deleted=0,
    )
    missing_row = loop.classify_next_work(
        _status(slug="cortex-executive-effectiveness-evaluator-followup"),
        _git(),
        bloat,
        candidate_contraction=("old_path",),
    )
    bad_row = loop.classify_next_work(
        _status(slug="cortex-executive-effectiveness-evaluator-followup"),
        _git(),
        bloat,
        candidate_contraction=("old_path",),
        candidate_rows=(
            _candidate_row(
                model_io_path=loop.LAB_PROOF_MODEL_IO_PATH,
                product_spine=[],
            ),
        ),
    )
    good_row = loop.classify_next_work(
        _status(slug="cortex-executive-effectiveness-evaluator-followup"),
        _git(),
        bloat,
        candidate_contraction=("old_path",),
        candidate_rows=(_candidate_row(),),
    )

    assert missing_row.status == "blocked"
    assert any("mission objective candidate record" in reason for reason in missing_row.reasons)
    assert bad_row.status == "blocked"
    assert any("model-I/O path" in reason and "product_spine" in reason for reason in bad_row.reasons)
    assert good_row.status == "ready"


def test_candidate_mutation_of_evaluator_or_cortex_docs_is_blocked() -> None:
    bloat = loop.BloatMetrics(
        loc_added=5,
        loc_deleted=0,
        changed_files=("lab/cortex_effectiveness_evaluator.py", "docs/CORTEX_V2_CORE_2.md"),
        new_policy_paths=(),
        duplicate_policy_removed=False,
        contraction_debt_increased=False,
        non_test_loc_added=5,
    )
    decision = loop.classify_next_work(
        _status(slug="cortex-executive-effectiveness-evaluator-followup"),
        _git(),
        bloat,
    )

    assert decision.status == "blocked"
    assert "lab/cortex_effectiveness_evaluator.py" in loop.forbidden_candidate_paths(bloat.changed_files)
    assert "docs/CORTEX_V2_CORE_2.md" in loop.forbidden_candidate_paths(bloat.changed_files)


def test_candidate_row_cannot_mutate_generated_product_docs() -> None:
    bloat = loop.BloatMetrics(
        loc_added=2,
        loc_deleted=0,
        changed_files=("docs/CORTEX.md",),
        new_policy_paths=(),
        duplicate_policy_removed=False,
        contraction_debt_increased=False,
        non_test_loc_added=2,
    )
    row = _candidate_row(
        changed_files=["docs/CORTEX.md"],
        model_io_path=loop.LAB_PROOF_MODEL_IO_PATH,
        product_spine=[],
    )
    decision = loop.classify_next_work(
        _status(slug="cortex-executive-effectiveness-evaluator-followup"),
        _git(),
        bloat,
        candidate_rows=(row,),
    )

    assert decision.status == "blocked"
    assert any("forbidden candidate mutation surfaces" in reason for reason in decision.reasons)


def test_structured_positive_value_claim_forces_user_review() -> None:
    bloat = loop.BloatMetrics(
        loc_added=0,
        loc_deleted=0,
        changed_files=(),
        new_policy_paths=(),
        duplicate_policy_removed=False,
        contraction_debt_increased=False,
    )
    decision = loop.classify_next_work(
        _status(slug="cortex-executive-effectiveness-evaluator-followup"),
        _git(),
        bloat,
        candidate_rows=(_candidate_row(metrics={"exactness_value_lift_claim_allowed": True}),),
    )

    assert decision.status == "blocked"
    assert any("structured positive value" in reason for reason in decision.reasons)


def test_digest_includes_mission_contract_review_fields() -> None:
    text = loop.render_digest(
        now=datetime(2026, 5, 8, 23, tzinfo=timezone.utc),
        git_state=_git(),
        decision=loop.classify_next_work(
            _status(slug="cortex-executive-effectiveness-evaluator-followup"),
            _git(),
        ),
        bloat=loop.BloatMetrics(
            loc_added=0,
            loc_deleted=0,
            changed_files=(),
            new_policy_paths=(),
            duplicate_policy_removed=False,
            contraction_debt_increased=False,
        ),
        candidate_rows=(_candidate_row(),),
    )

    assert "Which Cortex executive function was served" in text
    assert "Which loop stage improved" in text
    assert "Model-I/O path" in text
    assert "Simple-hook result" in text
    assert "Contraction implication" in text


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
    assert report["work_packet"]["do_not_use_prior_chat_context"] is True
    assert "internal/truth/cortex_status.json" in report["work_packet"]["required_boot_reads"]
    digest_path = Path(report["digest_path"])
    assert digest_path.exists()
    assert Path(report["cycle_state_path"]).exists()
    assert (tmp_path / "digests" / "latest_cycle_state.json").exists()
    text = digest_path.read_text()
    assert "Cortex Overnight Digest" in text
    assert "Fresh-Chat Work Packet" in text
    assert "dirty resting state" in text
    assert "User Input Needed" in text


def test_load_candidate_rows_feeds_simple_baseline_contraction(tmp_path: Path) -> None:
    candidate_db = tmp_path / ".cortex/automation/candidates/candidates.jsonl"
    candidate_db.parent.mkdir(parents=True)
    candidate_db.write_text(
        '{"candidate_id":"a","policy_candidate":"stop_only","failure_class":"failure_simple_baseline_parity"}\n'
        '{"candidate_id":"b","policy_candidate":"stop_only","failure_class":"failure_simple_baseline_parity"}\n',
        encoding="utf-8",
    )

    rows = loop.load_candidate_rows(tmp_path, candidate_db)

    assert loop.repeated_simple_baseline_losses(rows) == ("stop_only",)


def test_candidate_record_schema_is_complete() -> None:
    assert set(loop.CANDIDATE_RECORD_FIELDS) == {
        "candidate_id",
        "parent_id",
        "policy_candidate",
        "executive_function",
        "loop_stage",
        "control_mode",
        "truth_scope",
        "model_io_path",
        "product_spine",
        "changed_files",
        "mutation_reason",
        "metrics",
        "score",
        "failure_class",
        "contraction_implication",
    }
