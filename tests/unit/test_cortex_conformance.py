"""Focused tests for the Cortex-law conformance harness."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


TOOLS_ROOT = Path(__file__).resolve().parents[2] / "tools"
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

import cortex_conformance as conformance
from cortex.sre.verified_work import VerificationOutcome, WorkContract


def _work_contract() -> WorkContract:
    return WorkContract(
        allowed_write_paths=("src/bookmarks_api/main.py",),
        verification_profile="python_workspace_pytest_v1",
        output_carrier="full_files",
        max_repair_turns=1,
    )


def test_train_charter_requires_all_fields() -> None:
    with pytest.raises(ValueError, match="cortex_invariant"):
        conformance.TrainCharter(
            cortex_invariant="",
            borrowed_mechanism="tiny verifier",
            primary_proving_wiring="openai:service_api",
            conformance_surfaces=("openai:service_api",),
            kill_criteria=("cut if no lift",),
        )

    charter = conformance.TrainCharter(
        cortex_invariant="bounded verified-work law",
        borrowed_mechanism="tiny verifier",
        primary_proving_wiring="openai:service_api",
        conformance_surfaces=("openai:service_api", "claude:operator_cli"),
        kill_criteria=("cut if no lift",),
    )

    assert charter.as_payload()["primary_proving_wiring"] == "openai:service_api"


def test_contract_pack_exposes_required_train_charter() -> None:
    pack = conformance.ContractPack(
        contract_pack="verified_work_bookmarks_v1",
        prompt_text="build bookmarks app",
        workspace_template_relpath="tests/fixtures/live_validation/bookmarks_app_template",
        work_contract=_work_contract(),
        train_charter=conformance.TrainCharter(
            cortex_invariant="bounded verified-work law",
            borrowed_mechanism="tiny verifier",
            primary_proving_wiring="openai:service_api",
            conformance_surfaces=("openai:service_api",),
            kill_criteria=("cut if no lift",),
        ),
        shipping_default="openai:service_api",
    )

    payload = pack.as_payload()

    assert payload["contract_pack"] == "verified_work_bookmarks_v1"
    assert payload["workspace_template_relpath"] == "tests/fixtures/live_validation/bookmarks_app_template"
    assert payload["train_charter"]["cortex_invariant"] == "bounded verified-work law"


def test_contract_pack_registry_resolves_bookmarks_normalize_port_and_feature_flags() -> None:
    bookmarks_pack = conformance.contract_pack_by_name(conformance.ACTIVE_CONTRACT_PACK)
    normalize_pack = conformance.contract_pack_by_name(
        conformance.NORMALIZE_PORT_CONTRACT_PACK
    )
    feature_flags_pack = conformance.contract_pack_by_name(
        conformance.FEATURE_FLAGS_CONTRACT_PACK
    )

    assert bookmarks_pack.contract_pack == "verified_work_bookmarks_v1"
    assert normalize_pack.contract_pack == "verified_work_normalize_port_v1"
    assert normalize_pack.workspace_template_relpath == (
        "tests/fixtures/live_validation/project_template"
    )
    assert normalize_pack.work_contract.verification_profile == (
        "python_workspace_pytest_port_fix_v1"
    )
    assert feature_flags_pack.contract_pack == "verified_work_feature_flags_v1"
    assert feature_flags_pack.workspace_template_relpath == (
        "tests/fixtures/live_validation/feature_flags_template"
    )
    assert feature_flags_pack.work_contract.verification_profile == (
        "python_workspace_pytest_feature_flags_v1"
    )


def test_contract_pack_with_max_repair_turns_overrides_only_repair_budget() -> None:
    original_pack = conformance.contract_pack_by_name(conformance.FEATURE_FLAGS_CONTRACT_PACK)

    overridden = conformance.contract_pack_with_max_repair_turns(
        original_pack,
        max_repair_turns=0,
    )

    assert overridden.contract_pack == original_pack.contract_pack
    assert overridden.prompt_text == original_pack.prompt_text
    assert overridden.workspace_template_relpath == original_pack.workspace_template_relpath
    assert overridden.work_contract.allowed_write_paths == original_pack.work_contract.allowed_write_paths
    assert overridden.work_contract.verification_profile == original_pack.work_contract.verification_profile
    assert overridden.work_contract.max_repair_turns == 0
    assert original_pack.work_contract.max_repair_turns == 1


def test_contract_pack_rejects_absolute_workspace_template_path() -> None:
    with pytest.raises(ValueError, match="repo-relative"):
        conformance.ContractPack(
            contract_pack="verified_work_bookmarks_v1",
            prompt_text="build bookmarks app",
            workspace_template_relpath="/tmp/not-allowed",
            work_contract=_work_contract(),
            train_charter=conformance.TrainCharter(
                cortex_invariant="bounded verified-work law",
                borrowed_mechanism="tiny verifier",
                primary_proving_wiring="openai:service_api",
                conformance_surfaces=("openai:service_api",),
                kill_criteria=("cut if no lift",),
            ),
            shipping_default="openai:service_api",
        )


def test_strongest_native_surface_matches_current_wiring_order() -> None:
    pack = conformance.active_contract_pack()

    assert conformance.strongest_native_surface("openai", pack) == "service_api"
    assert conformance.strongest_native_surface("claude", pack) == "operator_cli"
    assert conformance.strongest_native_surface("gemini", pack) == "operator_cli"


def test_preflight_surface_distinguishes_env_blocked_and_unwired(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(conformance, "api_key_presence", lambda: {"OPENAI_API_KEY": False, "GEMINI_API_KEY": False})
    monkeypatch.setattr(conformance, "command_exists", lambda command: command != "gemini")

    openai_probe = conformance.preflight_surface("openai", "service_api")
    gemini_probe = conformance.preflight_surface("gemini", "operator_cli")
    unknown_probe = conformance.preflight_surface("claude", "service_api")  # type: ignore[arg-type]

    assert openai_probe.status == "env_blocked"
    assert gemini_probe.status == "env_blocked"
    assert unknown_probe.status == "unwired"

    monkeypatch.setattr(conformance, "command_exists", lambda _command: True)
    gemini_ready_probe = conformance.preflight_surface("gemini", "operator_cli")
    assert gemini_ready_probe.status == "partial"


def test_classify_outcome_divergence_maps_surface_and_brain_failures() -> None:
    passed = VerificationOutcome(status="passed", failure_class=None)
    test_failed = VerificationOutcome(status="failed", failure_class="test_failed")
    output_invalid = VerificationOutcome(status="failed", failure_class="output_invalid", parse_error="bad prefix")

    assert conformance.classify_outcome_divergence(surface="service_api", outcome=passed) == (
        "conformant",
        None,
    )
    assert conformance.classify_outcome_divergence(surface="service_api", outcome=test_failed) == (
        "partial",
        "brain_wiring",
    )
    assert conformance.classify_outcome_divergence(surface="operator_cli", outcome=output_invalid) == (
        "divergent",
        "surface_wiring",
    )


def test_classify_shared_divergence_only_returns_cortex_law_for_repeated_same_failure() -> None:
    results = [
        conformance.ConformanceRunResult(
            brain="openai",
            surface="service_api",
            contract_pack="verified_work_bookmarks_v1",
            status="partial",
            divergence_class="brain_wiring",
            first_attempt_status="failed",
            first_attempt_failure_class="test_failed",
            final_failure_class="test_failed",
            verification_status="failed",
            parseable=True,
            import_smoke_ok=True,
            pytest_passed=3,
            pytest_failed=8,
            attempt_count=1,
            repair_conversion="failed_without_repair",
        ),
        conformance.ConformanceRunResult(
            brain="claude",
            surface="operator_cli",
            contract_pack="verified_work_bookmarks_v1",
            status="partial",
            divergence_class="brain_wiring",
            first_attempt_status="failed",
            first_attempt_failure_class="test_failed",
            final_failure_class="test_failed",
            verification_status="failed",
            parseable=True,
            import_smoke_ok=True,
            pytest_passed=2,
            pytest_failed=9,
            attempt_count=1,
            repair_conversion="failed_without_repair",
        ),
    ]

    assert conformance.classify_shared_divergence(results) == "cortex_law"


def test_decide_iteration_outcome_requires_revision_for_shipping_regression() -> None:
    results = [
        conformance.ConformanceRunResult(
            brain="openai",
            surface="service_api",
            contract_pack="verified_work_bookmarks_v1",
            status="partial",
            divergence_class="brain_wiring",
            first_attempt_status="failed",
            first_attempt_failure_class="test_failed",
            final_failure_class="test_failed",
            verification_status="failed",
            parseable=True,
            import_smoke_ok=True,
            pytest_passed=4,
            pytest_failed=7,
            attempt_count=1,
            repair_conversion="failed_without_repair",
        )
    ]

    assert (
        conformance.decide_iteration_outcome(results, shipping_default="openai:service_api")
        == "revise"
    )


def test_stage_contract_pack_workspace_copies_fixture_tree() -> None:
    pack = conformance.active_contract_pack()

    with conformance._stage_contract_pack_workspace(pack, prefix="cortex-test-workspace-") as workspace:
        assert workspace.exists()
        assert workspace != Path(pack.workspace_template_relpath)
        assert (workspace / "README_TASK.md").exists()
        assert (workspace / "tests" / "test_bookmarks_api.py").exists()


def test_run_claude_cli_conformance_uses_read_only_tools_and_skips_resume_after_pass(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run_root = tmp_path
    commands: list[tuple[list[str], Path | None]] = []
    workspace_has_fixture: list[bool] = []

    def _fake_run_command(command, *, cwd=None, env=None, timeout_seconds=180.0):
        _ = env, timeout_seconds
        commands.append((list(command), cwd))
        workspace_has_fixture.append(
            bool(cwd is not None and (cwd / "tests" / "test_bookmarks_api.py").exists())
        )
        return {
            "command": list(command),
            "exit_code": 0,
            "stdout": "",
            "stderr": "",
            "started_at": "t0",
            "ended_at": "t1",
        }

    monkeypatch.setattr(conformance, "run_command", _fake_run_command)
    monkeypatch.setattr(
        conformance,
        "_evaluate_operator_attempt",
        lambda **_kwargs: {
            "status": "executed",
            "verification": VerificationOutcome(
                status="passed",
                failure_class=None,
                import_smoke_ok=True,
                pytest_passed=11,
            ),
            "session_id": "cl-session",
            "extraction_mode": "jsonl",
            "note": "executed",
        },
    )

    result = conformance._run_claude_cli_conformance(
        contract_pack=conformance.active_contract_pack(),
        run_root=run_root,
    )

    assert result.status == "conformant"
    assert result.attempt_count == 1
    assert len(commands) == 1
    command, cwd = commands[0]
    assert "--bare" not in command
    assert command[command.index("--tools") + 1] == "Read,Glob,Grep,LS"
    assert cwd is not None
    assert workspace_has_fixture == [True]


def test_run_claude_cli_conformance_reuses_workspace_and_tools_on_resume(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run_root = tmp_path
    commands: list[tuple[list[str], Path | None]] = []
    staged_cwds: list[Path | None] = []
    evaluations = iter(
        (
            {
                "status": "executed",
                "verification": VerificationOutcome(
                    status="failed",
                    failure_class="test_failed",
                    import_smoke_ok=True,
                    pytest_passed=4,
                    pytest_failed=7,
                ),
                "session_id": "cl-session",
                "extraction_mode": "jsonl",
                "note": "executed",
            },
            {
                "status": "executed",
                "verification": VerificationOutcome(
                    status="passed",
                    failure_class=None,
                    import_smoke_ok=True,
                    pytest_passed=11,
                ),
                "session_id": "cl-session",
                "extraction_mode": "jsonl",
                "note": "executed",
            },
        )
    )

    def _fake_run_command(command, *, cwd=None, env=None, timeout_seconds=180.0):
        _ = env, timeout_seconds
        commands.append((list(command), cwd))
        staged_cwds.append(cwd)
        return {
            "command": list(command),
            "exit_code": 0,
            "stdout": "",
            "stderr": "",
            "started_at": "t0",
            "ended_at": "t1",
        }

    monkeypatch.setattr(conformance, "run_command", _fake_run_command)
    monkeypatch.setattr(
        conformance,
        "_evaluate_operator_attempt",
        lambda **_kwargs: next(evaluations),
    )

    result = conformance._run_claude_cli_conformance(
        contract_pack=conformance.active_contract_pack(),
        run_root=run_root,
    )

    assert result.status == "conformant"
    assert result.attempt_count == 2
    assert len(commands) == 2
    assert staged_cwds[0] == staged_cwds[1]
    first_command, _first_cwd = commands[0]
    second_command, _second_cwd = commands[1]
    assert first_command[first_command.index("--tools") + 1] == "Read,Glob,Grep,LS"
    assert second_command[second_command.index("--tools") + 1] == "Read,Glob,Grep,LS"
    assert second_command[second_command.index("-r") + 1] == "cl-session"


def test_evaluate_operator_attempt_classifies_empty_timeout_as_env_blocked() -> None:
    result = conformance._evaluate_operator_attempt(
        provider="claude",
        command_result={
            "command": ["claude"],
            "exit_code": 124,
            "stdout": "",
            "stderr": "",
        },
        work_contract=_work_contract(),
    )

    assert result["status"] == "env_blocked"
    assert result["transport_failure_class"] == "operator_timeout"


def test_evaluate_operator_attempt_preserves_structured_timeout_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        conformance,
        "verify_verified_work_result",
        lambda result_text, _work_contract: (
            {},
            VerificationOutcome(status="passed", failure_class=None, blocked_message=result_text),
        ),
    )

    result = conformance._evaluate_operator_attempt(
        provider="claude",
        command_result={
            "command": ["claude"],
            "exit_code": 124,
            "stdout": '{"session_id":"cl-1","result":"=== FILE: src/bookmarks_api/main.py ===\\napp = object()\\n=== END FILE ==="}',
            "stderr": "",
        },
        work_contract=_work_contract(),
    )

    assert result["status"] == "executed"
    assert result["extraction_mode"] == "jsonl"
    assert "operator timeout" in result["note"]


def test_next_decision_prefers_shipping_default_gap_once_non_shipping_divergence_clears() -> None:
    results = [
        {
            "brain": "openai",
            "status": "partial",
            "divergence_class": "brain_wiring",
        },
        {
            "brain": "claude",
            "status": "conformant",
            "divergence_class": None,
        },
        {
            "brain": "gemini",
            "status": "partial",
            "divergence_class": "brain_wiring",
        },
    ]

    assert (
        conformance._next_decision(
            results,
            None,
            shipping_default="openai:service_api",
        )
        == "improve_shipping_default"
    )


def test_next_decision_promotes_when_only_non_shipping_env_blocks_remain() -> None:
    results = [
        {
            "brain": "openai",
            "status": "conformant",
            "divergence_class": None,
        },
        {
            "brain": "claude",
            "status": "env_blocked",
            "divergence_class": "env_blocked",
        },
        {
            "brain": "gemini",
            "status": "conformant",
            "divergence_class": None,
        },
    ]

    assert (
        conformance._next_decision(
            results,
            None,
            shipping_default="openai:service_api",
        )
        == "promote"
    )


def test_run_active_conformance_does_not_publish_latest_for_targeted_runs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(conformance, "CONFORMANCE_ROOT", tmp_path)
    monkeypatch.setattr(
        conformance,
        "now_utc_iso",
        lambda: "2026-04-08T08:00:00+00:00",
    )
    monkeypatch.setattr(
        conformance,
        "load_local_env_file",
        lambda: None,
    )
    monkeypatch.setattr(
        conformance,
        "preflight_surface",
        lambda _brain, _surface: conformance.SurfaceProbe(
            brain="openai",
            surface="service_api",
            status="conformant",
            reason="ready",
        ),
    )
    monkeypatch.setattr(
        conformance,
        "_run_conformance",
        lambda **_kwargs: conformance.ConformanceRunResult(
            brain="openai",
            surface="service_api",
            contract_pack="verified_work_bookmarks_v1",
            status="conformant",
            attempt_count=1,
            verification_status="passed",
            parseable=True,
            import_smoke_ok=True,
            pytest_passed=11,
            repair_conversion="passed_without_repair",
        ),
    )

    summary = conformance.run_active_conformance(brains=("openai",))

    assert summary["results"][0]["brain"] == "openai"
    assert not (tmp_path / "summary.latest.json").exists()
    assert not (tmp_path / "summary.latest.md").exists()


def test_run_active_conformance_keeps_bookmarks_as_only_latest_summary_anchor(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    written_paths: list[Path] = []

    monkeypatch.setattr(conformance, "CONFORMANCE_ROOT", tmp_path)
    monkeypatch.setattr(
        conformance,
        "now_utc_iso",
        lambda: "2026-04-08T08:00:00+00:00",
    )
    monkeypatch.setattr(conformance, "load_local_env_file", lambda: None)
    monkeypatch.setattr(
        conformance,
        "preflight_surface",
        lambda brain, surface: conformance.SurfaceProbe(
            brain=brain,
            surface=surface,
            status="conformant",
            reason="ready",
        ),
    )
    monkeypatch.setattr(
        conformance,
        "_run_conformance",
        lambda *, brain, surface, contract_pack, run_root: conformance.ConformanceRunResult(
            brain=brain,
            surface=surface,
            contract_pack=contract_pack.contract_pack,
            status="conformant",
            attempt_count=1,
            verification_status="passed",
            parseable=True,
            import_smoke_ok=True,
            pytest_passed=2,
            repair_conversion="passed_without_repair",
        ),
    )
    monkeypatch.setattr(
        conformance,
        "write_json",
        lambda path, payload: written_paths.append(path),
    )
    monkeypatch.setattr(
        conformance,
        "write_text",
        lambda path, text: written_paths.append(path),
    )

    conformance.run_active_conformance(
        brains=("openai", "claude", "gemini"),
        contract_pack=conformance.contract_pack_by_name(
            conformance.NORMALIZE_PORT_CONTRACT_PACK
        ),
    )

    assert tmp_path / "summary.latest.json" not in written_paths
    assert tmp_path / "summary.latest.md" not in written_paths


def test_run_active_conformance_does_not_publish_feature_flags_as_latest_summary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    written_paths: list[Path] = []

    monkeypatch.setattr(conformance, "CONFORMANCE_ROOT", tmp_path)
    monkeypatch.setattr(
        conformance,
        "now_utc_iso",
        lambda: "2026-04-08T09:00:00+00:00",
    )
    monkeypatch.setattr(conformance, "load_local_env_file", lambda: None)
    monkeypatch.setattr(
        conformance,
        "preflight_surface",
        lambda brain, surface: conformance.SurfaceProbe(
            brain=brain,
            surface=surface,
            status="conformant",
            reason="ready",
        ),
    )
    monkeypatch.setattr(
        conformance,
        "_run_conformance",
        lambda *, brain, surface, contract_pack, run_root: conformance.ConformanceRunResult(
            brain=brain,
            surface=surface,
            contract_pack=contract_pack.contract_pack,
            status="conformant",
            attempt_count=1,
            verification_status="passed",
            parseable=True,
            import_smoke_ok=True,
            pytest_passed=6,
            repair_conversion="passed_without_repair",
        ),
    )
    monkeypatch.setattr(
        conformance,
        "write_json",
        lambda path, payload: written_paths.append(path),
    )
    monkeypatch.setattr(
        conformance,
        "write_text",
        lambda path, text: written_paths.append(path),
    )

    conformance.run_active_conformance(
        brains=("openai", "claude", "gemini"),
        contract_pack=conformance.contract_pack_by_name(
            conformance.FEATURE_FLAGS_CONTRACT_PACK
        ),
    )

    assert tmp_path / "summary.latest.json" not in written_paths
    assert tmp_path / "summary.latest.md" not in written_paths


def test_reconcile_latest_summary_prefers_newest_surviving_full_run_matching_ct2_truth(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(conformance, "CONFORMANCE_ROOT", tmp_path)
    monkeypatch.setattr(conformance, "ROOT", tmp_path)
    phase_gates_path = tmp_path / "phase_gates.md"
    phase_gates_path.write_text(
        "| `CT2` active verified-work tri-brain conformance | evidence | owner | landed | current shipping-default decision is `promote` |\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(conformance, "PHASE_GATES_PATH", phase_gates_path)
    monkeypatch.setattr(conformance, "render_summary_markdown", lambda _summary: "")

    older_run = tmp_path / "run_20260408T070000+0000"
    newer_run = tmp_path / "run_20260408T071000+0000"
    older_run.mkdir(parents=True)
    newer_run.mkdir(parents=True)

    for run_dir in (older_run, newer_run):
        for artifact_name in (
            "openai_service_api",
            "claude_operator_cli",
            "gemini_operator_cli",
        ):
            (run_dir / artifact_name).mkdir()

    older_summary = {
        "generated_at": "2026-04-08T07:00:00+00:00",
        "results": [
            {
                "brain": "openai",
                "surface": "service_api",
                "status": "conformant",
                "divergence_class": None,
                "parseable": True,
                "import_smoke_ok": True,
                "pytest_passed": 11,
                "pytest_failed": None,
                "repair_conversion": "passed_without_repair",
                "extraction_mode": None,
                "note": "runtime move: continue",
                "artifact_relpath": "run_20260408T070000+0000/openai_service_api",
            },
            {
                "brain": "claude",
                "surface": "operator_cli",
                "status": "env_blocked",
                "divergence_class": "env_blocked",
                "parseable": None,
                "import_smoke_ok": None,
                "pytest_passed": None,
                "pytest_failed": None,
                "repair_conversion": None,
                "extraction_mode": None,
                "note": "provider blocked",
                "artifact_relpath": "run_20260408T070000+0000/claude_operator_cli",
            },
            {
                "brain": "gemini",
                "surface": "operator_cli",
                "status": "conformant",
                "divergence_class": None,
                "parseable": True,
                "import_smoke_ok": True,
                "pytest_passed": 11,
                "pytest_failed": None,
                "repair_conversion": "passed_without_repair",
                "extraction_mode": "json_object",
                "note": "executed",
                "artifact_relpath": "run_20260408T070000+0000/gemini_operator_cli",
            },
        ],
        "next_decision": "promote",
        "shipping_truth": {"default": "openai:service_api"},
        "iteration_outcome": "promote",
        "overall_divergence_class": None,
        "contract_pack": {"contract_pack": "verified_work_bookmarks_v1"},
    }
    newer_summary = {
        "generated_at": "2026-04-08T07:10:00+00:00",
        "results": [
            {
                "brain": "openai",
                "surface": "service_api",
                "status": "conformant",
                "divergence_class": None,
                "parseable": True,
                "import_smoke_ok": True,
                "pytest_passed": 11,
                "pytest_failed": None,
                "repair_conversion": "passed_without_repair",
                "extraction_mode": None,
                "note": "runtime move: continue",
                "artifact_relpath": "run_20260408T071000+0000/openai_service_api",
            },
            {
                "brain": "claude",
                "surface": "operator_cli",
                "status": "env_blocked",
                "divergence_class": "env_blocked",
                "parseable": None,
                "import_smoke_ok": None,
                "pytest_passed": None,
                "pytest_failed": None,
                "repair_conversion": None,
                "extraction_mode": None,
                "note": "provider blocked",
                "artifact_relpath": "run_20260408T071000+0000/claude_operator_cli",
            },
            {
                "brain": "gemini",
                "surface": "operator_cli",
                "status": "conformant",
                "divergence_class": None,
                "parseable": True,
                "import_smoke_ok": True,
                "pytest_passed": 11,
                "pytest_failed": None,
                "repair_conversion": "passed_without_repair",
                "extraction_mode": "json_object",
                "note": "executed",
                "artifact_relpath": "run_20260408T071000+0000/gemini_operator_cli",
            },
        ],
        "next_decision": "fix_wiring_only",
        "shipping_truth": {"default": "openai:service_api"},
        "iteration_outcome": "revise",
        "overall_divergence_class": None,
        "contract_pack": {"contract_pack": "verified_work_bookmarks_v1"},
    }
    (older_run / "summary.json").write_text(json.dumps(older_summary), encoding="utf-8")
    (newer_run / "summary.json").write_text(json.dumps(newer_summary), encoding="utf-8")

    reconciled = conformance.reconcile_latest_summary()

    assert reconciled["generated_at"] == "2026-04-08T07:00:00+00:00"
    assert (tmp_path / "summary.latest.json").exists()


def test_reconcile_latest_summary_ignores_newer_non_anchor_pack_full_runs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(conformance, "CONFORMANCE_ROOT", tmp_path)
    monkeypatch.setattr(conformance, "ROOT", tmp_path)
    phase_gates_path = tmp_path / "phase_gates.md"
    phase_gates_path.write_text(
        "| `CT2` active verified-work tri-brain conformance | evidence | owner | landed | current shipping-default decision is `promote` |\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(conformance, "PHASE_GATES_PATH", phase_gates_path)
    monkeypatch.setattr(conformance, "render_summary_markdown", lambda _summary: "")

    older_run = tmp_path / "run_20260408T070000+0000"
    newer_run = tmp_path / "run_20260408T080000+0000"
    older_run.mkdir(parents=True)
    newer_run.mkdir(parents=True)
    for run_dir in (older_run, newer_run):
        for artifact_name in (
            "openai_service_api",
            "claude_operator_cli",
            "gemini_operator_cli",
        ):
            (run_dir / artifact_name).mkdir()

    older_summary = {
        "generated_at": "2026-04-08T07:00:00+00:00",
        "results": [
            {
                "brain": "openai",
                "artifact_relpath": "run_20260408T070000+0000/openai_service_api",
            },
            {
                "brain": "claude",
                "artifact_relpath": "run_20260408T070000+0000/claude_operator_cli",
            },
            {
                "brain": "gemini",
                "artifact_relpath": "run_20260408T070000+0000/gemini_operator_cli",
            },
        ],
        "next_decision": "promote",
        "shipping_truth": {"default": "openai:service_api"},
        "iteration_outcome": "promote",
        "overall_divergence_class": None,
        "contract_pack": {"contract_pack": "verified_work_bookmarks_v1"},
    }
    newer_summary = {
        "generated_at": "2026-04-08T08:00:00+00:00",
        "results": [
            {
                "brain": "openai",
                "artifact_relpath": "run_20260408T080000+0000/openai_service_api",
            },
            {
                "brain": "claude",
                "artifact_relpath": "run_20260408T080000+0000/claude_operator_cli",
            },
            {
                "brain": "gemini",
                "artifact_relpath": "run_20260408T080000+0000/gemini_operator_cli",
            },
        ],
        "next_decision": "promote",
        "shipping_truth": {"default": "openai:service_api"},
        "iteration_outcome": "promote",
        "overall_divergence_class": None,
        "contract_pack": {"contract_pack": "verified_work_normalize_port_v1"},
    }
    (older_run / "summary.json").write_text(json.dumps(older_summary), encoding="utf-8")
    (newer_run / "summary.json").write_text(json.dumps(newer_summary), encoding="utf-8")

    reconciled = conformance.reconcile_latest_summary()

    assert reconciled["contract_pack"]["contract_pack"] == "verified_work_bookmarks_v1"


def test_reconcile_latest_summary_falls_back_to_newest_surviving_full_run_when_ct2_match_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(conformance, "CONFORMANCE_ROOT", tmp_path)
    monkeypatch.setattr(conformance, "ROOT", tmp_path)
    phase_gates_path = tmp_path / "phase_gates.md"
    phase_gates_path.write_text(
        "| `CT2` active verified-work tri-brain conformance | evidence | owner | partial | current shipping-default decision is `promote` |\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(conformance, "PHASE_GATES_PATH", phase_gates_path)

    newer_run = tmp_path / "run_20260408T071000+0000"
    newer_run.mkdir(parents=True)
    for artifact_name in (
        "openai_service_api",
        "claude_operator_cli",
        "gemini_operator_cli",
    ):
        (newer_run / artifact_name).mkdir()

    newer_summary = {
        "generated_at": "2026-04-08T07:10:00+00:00",
        "results": [
            {
                "brain": "openai",
                "surface": "service_api",
                "status": "conformant",
                "divergence_class": None,
                "parseable": True,
                "import_smoke_ok": True,
                "pytest_passed": 11,
                "pytest_failed": None,
                "repair_conversion": "passed_without_repair",
                "extraction_mode": None,
                "note": "runtime move: continue",
                "artifact_relpath": "run_20260408T071000+0000/openai_service_api",
            },
            {
                "brain": "claude",
                "surface": "operator_cli",
                "status": "divergent",
                "divergence_class": "surface_wiring",
                "parseable": False,
                "import_smoke_ok": None,
                "pytest_passed": None,
                "pytest_failed": None,
                "repair_conversion": "repair_attempt_no_recovery",
                "extraction_mode": "jsonl",
                "note": "executed",
                "artifact_relpath": "run_20260408T071000+0000/claude_operator_cli",
            },
            {
                "brain": "gemini",
                "surface": "operator_cli",
                "status": "conformant",
                "divergence_class": None,
                "parseable": True,
                "import_smoke_ok": True,
                "pytest_passed": 11,
                "pytest_failed": None,
                "repair_conversion": "passed_without_repair",
                "extraction_mode": "json_object",
                "note": "executed",
                "artifact_relpath": "run_20260408T071000+0000/gemini_operator_cli",
            },
        ],
        "next_decision": "fix_wiring_only",
        "shipping_truth": {"default": "openai:service_api"},
        "iteration_outcome": "revise",
        "overall_divergence_class": None,
        "contract_pack": {"contract_pack": "verified_work_bookmarks_v1"},
    }
    (newer_run / "summary.json").write_text(json.dumps(newer_summary), encoding="utf-8")

    reconciled = conformance.reconcile_latest_summary()

    assert reconciled["generated_at"] == "2026-04-08T07:10:00+00:00"
