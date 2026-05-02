"""Focused tests for the Cortex-law conformance harness."""

from __future__ import annotations

import json
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

import pytest

from lab import cortex_conformance as conformance
from cortex.sre.verified_work import VerificationOutcome, WorkContract


def _work_contract() -> WorkContract:
    return WorkContract(
        allowed_write_paths=("src/bookmarks_api/main.py",),
        verification_profile="python_workspace_pytest_v1",
        output_carrier="full_files",
        max_repair_turns=1,
    )


def _fixed_utc_iso(hour: int, minute: int = 0) -> str:
    return datetime(2026, 4, 8, hour, minute, tzinfo=UTC).isoformat()


def test_train_charter_requires_all_fields() -> None:
    with pytest.raises(ValueError, match="cortex_invariant"):
        conformance.TrainCharter(
            cortex_invariant="",
            borrowed_mechanism="tiny verifier",
            primary_proving_wiring="openai:operator_cli",
            conformance_surfaces=("openai:operator_cli",),
            kill_criteria=("cut if no lift",),
        )

    charter = conformance.TrainCharter(
        cortex_invariant="bounded verified-work law",
        borrowed_mechanism="tiny verifier",
        primary_proving_wiring="openai:operator_cli",
        conformance_surfaces=("openai:operator_cli", "claude:operator_cli"),
        kill_criteria=("cut if no lift",),
    )

    assert charter.as_payload()["primary_proving_wiring"] == "openai:operator_cli"


def test_contract_pack_exposes_required_train_charter() -> None:
    pack = conformance.ContractPack(
        contract_pack="verified_work_bookmarks_v1",
        prompt_text="build bookmarks app",
        workspace_template_relpath="tests/lab/fixtures/live_validation/bookmarks_app_template",
        work_contract=_work_contract(),
        train_charter=conformance.TrainCharter(
            cortex_invariant="bounded verified-work law",
            borrowed_mechanism="tiny verifier",
            primary_proving_wiring="openai:operator_cli",
            conformance_surfaces=("openai:operator_cli",),
            kill_criteria=("cut if no lift",),
        ),
        shipping_default="openai:operator_cli",
    )

    payload = pack.as_payload()

    assert payload["contract_pack"] == "verified_work_bookmarks_v1"
    assert payload["workspace_template_relpath"] == "tests/lab/fixtures/live_validation/bookmarks_app_template"
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
        "tests/lab/fixtures/live_validation/project_template"
    )
    assert normalize_pack.work_contract.verification_profile == (
        "python_workspace_pytest_port_fix_v1"
    )
    assert feature_flags_pack.contract_pack == "verified_work_feature_flags_v1"
    assert feature_flags_pack.workspace_template_relpath == (
        "tests/lab/fixtures/live_validation/feature_flags_template"
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
                primary_proving_wiring="openai:operator_cli",
                conformance_surfaces=("openai:operator_cli",),
                kill_criteria=("cut if no lift",),
            ),
            shipping_default="openai:operator_cli",
        )


def test_strongest_native_surface_matches_current_wiring_order() -> None:
    pack = conformance.active_contract_pack()

    assert conformance.strongest_native_surface("openai", pack) == "operator_cli"
    assert conformance.strongest_native_surface("claude", pack) == "operator_cli"
    assert conformance.strongest_native_surface("gemini", pack) == "operator_cli"
    assert (
        conformance.strongest_native_surface(
            "openai",
            pack,
            openai_surface="service_api",
        )
        == "service_api"
    )


def test_preflight_surface_distinguishes_env_blocked_and_unwired(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        conformance,
        "api_key_presence",
        lambda: {"OPENAI_API_KEY": False, "GEMINI_API_KEY": False},
    )
    monkeypatch.setattr(conformance, "command_exists", lambda command: command not in {"gemini", "codex"})
    monkeypatch.setattr(
        conformance,
        "run_command",
        lambda *_args, **_kwargs: {"exit_code": 1, "stdout": "", "stderr": "not logged in"},
    )

    openai_probe = conformance.preflight_surface("openai", "operator_cli")
    gemini_probe = conformance.preflight_surface("gemini", "operator_cli")
    unknown_probe = conformance.preflight_surface("claude", "service_api")  # type: ignore[arg-type]

    assert openai_probe.status == "env_blocked"
    assert gemini_probe.status == "env_blocked"
    assert unknown_probe.status == "unwired"

    monkeypatch.setattr(conformance, "command_exists", lambda _command: True)
    monkeypatch.setattr(
        conformance,
        "run_command",
        lambda *_args, **_kwargs: {
            "exit_code": 0,
            "stdout": "Logged in using ChatGPT",
            "stderr": "",
        },
    )
    openai_ready_probe = conformance.preflight_surface("openai", "operator_cli")
    gemini_ready_probe = conformance.preflight_surface("gemini", "operator_cli")
    assert openai_ready_probe.status == "conformant"
    assert gemini_ready_probe.status == "partial"


def test_main_default_openai_active_does_not_require_service_spend_approval(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pack = conformance.active_contract_pack()
    monkeypatch.delenv("CORTEX_LIVE_SERVICE_SPEND_APPROVED", raising=False)
    monkeypatch.setattr(
        conformance,
        "run_active_conformance",
        lambda **_kwargs: {"ok": True},
    )
    monkeypatch.setattr(conformance, "load_local_env_file", lambda: None)
    monkeypatch.setattr(
        conformance,
        "contract_pack_by_name",
        lambda _name: pack,
    )

    assert conformance.main(["--mode", "active", "--brain", "openai"]) == 0


def test_main_requires_service_spend_approval_for_backup_openai_service_lane(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CORTEX_LIVE_SERVICE_SPEND_APPROVED", raising=False)
    monkeypatch.setattr(
        conformance,
        "run_active_conformance",
        lambda **_kwargs: pytest.fail("run_active_conformance should not be called"),
    )

    with pytest.raises(SystemExit, match="service-lane spend is blocked"):
        conformance.main(
            ["--mode", "active", "--brain", "openai", "--openai-surface", "service_api"]
        )


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
            pytest_passed=4,
            pytest_failed=7,
            attempt_count=1,
            repair_conversion="failed_without_repair",
        )
    ]

    assert (
        conformance.decide_iteration_outcome(results, shipping_default="openai:operator_cli")
        == "revise"
    )


def test_stage_contract_pack_workspace_copies_fixture_tree() -> None:
    pack = conformance.active_contract_pack()

    with conformance._stage_contract_pack_workspace(pack, prefix="cortex-test-workspace-") as workspace:
        assert workspace.exists()
        assert workspace != Path(pack.workspace_template_relpath)
        assert (workspace / "README_TASK.md").exists()
        assert (workspace / "tests" / "test_bookmarks_api.py").exists()


def test_run_openai_operator_cli_conformance_skips_resume_after_pass(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run_root = tmp_path
    commands: list[tuple[list[str], Path | None, dict[str, str] | None]] = []
    isolated_env = {"CODEX_HOME": "/tmp/cortex-codex-home"}
    monkeypatch.setattr(
        conformance,
        "resolve_auth_mode",
        lambda _provider, _lane: "codex_cli",
    )
    monkeypatch.setattr(
        conformance,
        "choose_model",
        lambda *_args, **_kwargs: "gpt-5.3-codex",
    )

    @contextmanager
    def _fake_isolated_codex_home_env():
        yield isolated_env

    monkeypatch.setattr(conformance, "isolated_codex_home_env", _fake_isolated_codex_home_env)

    def _fake_run_command(command, *, cwd=None, env=None, timeout_seconds=300.0):
        _ = timeout_seconds
        commands.append((list(command), cwd, env))
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
            "session_id": "thread-1",
            "extraction_mode": "jsonl",
            "note": "executed",
        },
    )

    result = conformance._run_openai_operator_cli_conformance(
        contract_pack=conformance.active_contract_pack(),
        run_root=run_root,
    )

    assert result.status == "conformant"
    assert result.attempt_count == 1
    assert len(commands) == 1
    command, cwd, env = commands[0]
    assert command[:3] == ["codex", "exec", "--json"]
    prompt = command[-1]
    assert "Workspace context for the task follows." in prompt
    assert "=== CONTEXT FILE: src/bookmarks_api/main.py ===" in prompt
    assert "=== CONTEXT FILE: tests/test_bookmarks_api.py ===" in prompt
    assert "The work happens directly on the staged workspace." in prompt
    assert (
        "Tests, compile checks, syntax checks, and other validation shell commands "
        "are not part of this turn."
    ) in prompt
    assert "Follow this exact output contract" not in prompt
    assert cwd is not None
    assert env == isolated_env


def test_run_openai_operator_cli_conformance_resumes_after_failed_first_attempt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run_root = tmp_path
    commands: list[tuple[list[str], Path | None, dict[str, str] | None]] = []
    isolated_env = {"CODEX_HOME": "/tmp/cortex-codex-home"}
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
                "session_id": "thread-1",
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
                "session_id": "thread-1",
                "extraction_mode": "jsonl",
                "note": "executed",
            },
        )
    )
    monkeypatch.setattr(
        conformance,
        "resolve_auth_mode",
        lambda _provider, _lane: "codex_cli",
    )
    monkeypatch.setattr(
        conformance,
        "choose_model",
        lambda *_args, **_kwargs: "gpt-5.3-codex",
    )

    @contextmanager
    def _fake_isolated_codex_home_env():
        yield isolated_env

    monkeypatch.setattr(conformance, "isolated_codex_home_env", _fake_isolated_codex_home_env)

    def _fake_run_command(command, *, cwd=None, env=None, timeout_seconds=300.0):
        _ = timeout_seconds
        commands.append((list(command), cwd, env))
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

    result = conformance._run_openai_operator_cli_conformance(
        contract_pack=conformance.active_contract_pack(),
        run_root=run_root,
    )

    assert result.status == "conformant"
    assert result.attempt_count == 2
    assert len(commands) == 2
    assert commands[1][0][:4] == ["codex", "exec", "resume", "--json"]
    assert "--skip-git-repo-check" in commands[1][0]
    assert commands[0][2] == isolated_env
    assert commands[1][2] == isolated_env


def test_run_openai_operator_cli_conformance_does_not_resume_after_output_invalid(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run_root = tmp_path
    commands: list[tuple[list[str], Path | None]] = []
    monkeypatch.setattr(
        conformance,
        "resolve_auth_mode",
        lambda _provider, _lane: "codex_cli",
    )
    monkeypatch.setattr(
        conformance,
        "choose_model",
        lambda *_args, **_kwargs: "gpt-5.3-codex",
    )

    def _fake_run_command(command, *, cwd=None, env=None, timeout_seconds=180.0):
        _ = env, timeout_seconds
        commands.append((list(command), cwd))
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
                status="failed",
                failure_class="output_invalid",
                parse_error="unexpected text outside protocol blocks: nope",
            ),
            "session_id": "thread-1",
            "extraction_mode": "raw_fallback",
            "note": "executed",
        },
    )

    result = conformance._run_openai_operator_cli_conformance(
        contract_pack=conformance.active_contract_pack(),
        run_root=run_root,
    )

    assert result.status == "divergent"
    assert result.attempt_count == 1
    assert result.final_failure_class == "output_invalid"
    assert len(commands) == 1


def test_run_openai_operator_cli_conformance_does_not_resume_after_timeout(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run_root = tmp_path
    commands: list[tuple[list[str], Path | None]] = []
    monkeypatch.setattr(
        conformance,
        "resolve_auth_mode",
        lambda _provider, _lane: "codex_cli",
    )
    monkeypatch.setattr(
        conformance,
        "choose_model",
        lambda *_args, **_kwargs: "gpt-5.3-codex",
    )

    def _fake_run_command(command, *, cwd=None, env=None, timeout_seconds=180.0):
        _ = env, timeout_seconds
        commands.append((list(command), cwd))
        return {
            "command": list(command),
            "exit_code": 124,
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
            "status": "timed_out",
            "transport_failure_class": "operator_timeout",
            "extraction_mode": "jsonl",
            "note": "operator timed out before returning a publishable result",
        },
    )

    result = conformance._run_openai_operator_cli_conformance(
        contract_pack=conformance.active_contract_pack(),
        run_root=run_root,
    )

    assert result.status == "divergent"
    assert result.attempt_count == 1
    assert result.first_attempt_failure_class == "operator_timeout"
    assert result.final_failure_class == "operator_timeout"
    assert len(commands) == 1


def test_run_openai_operator_cli_conformance_returns_env_blocked_without_isolated_auth(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run_root = tmp_path
    monkeypatch.setattr(
        conformance,
        "resolve_auth_mode",
        lambda _provider, _lane: "codex_cli",
    )
    monkeypatch.setattr(
        conformance,
        "choose_model",
        lambda *_args, **_kwargs: "gpt-5.3-codex",
    )

    @contextmanager
    def _missing_isolated_codex_home_env():
        raise RuntimeError("OpenAI operator run requires ~/.codex/auth.json")
        yield

    monkeypatch.setattr(
        conformance,
        "isolated_codex_home_env",
        _missing_isolated_codex_home_env,
    )

    result = conformance._run_openai_operator_cli_conformance(
        contract_pack=conformance.active_contract_pack(),
        run_root=run_root,
    )

    assert result.status == "env_blocked"
    assert result.divergence_class == "env_blocked"
    assert result.transport_failure_class == "auth_missing"
    assert "~/.codex/auth.json" in (result.note or "")


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
    assert command[command.index("--tools") + 1] == "Read,Glob,Grep,LS,Edit,MultiEdit,Write"
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
    assert (
        first_command[first_command.index("--tools") + 1]
        == "Read,Glob,Grep,LS,Edit,MultiEdit,Write"
    )
    assert (
        second_command[second_command.index("--tools") + 1]
        == "Read,Glob,Grep,LS,Edit,MultiEdit,Write"
    )
    assert second_command[second_command.index("-r") + 1] == "cl-session"


def test_run_gemini_cli_conformance_uses_locked_model_and_skips_resume_after_pass(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run_root = tmp_path
    commands: list[tuple[list[str], Path | None]] = []
    monkeypatch.setattr(
        conformance,
        "choose_model",
        lambda _provider, _lane: "auto",
    )

    def _fake_run_command(command, *, cwd=None, env=None, timeout_seconds=180.0):
        _ = env, timeout_seconds
        commands.append((list(command), cwd))
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
            "session_id": "gm-session",
            "extraction_mode": "json_object",
            "note": "executed",
        },
    )

    result = conformance._run_gemini_cli_conformance(
        contract_pack=conformance.active_contract_pack(),
        run_root=run_root,
    )

    assert result.status == "conformant"
    assert result.attempt_count == 1
    assert len(commands) == 1
    command, cwd = commands[0]
    assert command[:2] == ["gemini", "-p"]
    assert "Build me a small FastAPI app" in command[2]
    assert "The exact output contract follows:" in command[2]
    assert "-m" not in command
    assert cwd is not None


def test_run_gemini_cli_conformance_reuses_locked_model_on_resume(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run_root = tmp_path
    commands: list[tuple[list[str], Path | None]] = []
    monkeypatch.setattr(
        conformance,
        "choose_model",
        lambda _provider, _lane: "auto",
    )
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
                "session_id": "gm-session",
                "extraction_mode": "json_object",
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
                "session_id": "gm-session",
                "extraction_mode": "json_object",
                "note": "executed",
            },
        )
    )

    def _fake_run_command(command, *, cwd=None, env=None, timeout_seconds=180.0):
        _ = env, timeout_seconds
        commands.append((list(command), cwd))
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

    result = conformance._run_gemini_cli_conformance(
        contract_pack=conformance.active_contract_pack(),
        run_root=run_root,
    )

    assert result.status == "conformant"
    assert result.attempt_count == 2
    assert len(commands) == 2
    first_command, _first_cwd = commands[0]
    second_command, _second_cwd = commands[1]
    assert first_command[:2] == ["gemini", "-p"]
    assert "Build me a small FastAPI app" in first_command[2]
    assert "-m" not in first_command
    assert "-m" not in second_command
    assert second_command[second_command.index("--resume") + 1] == "gm-session"


def test_run_gemini_cli_conformance_requires_resumable_session_id(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run_root = tmp_path
    commands: list[tuple[list[str], Path | None]] = []
    monkeypatch.setattr(
        conformance,
        "choose_model",
        lambda _provider, _lane: "auto",
    )
    monkeypatch.setattr(
        conformance,
        "_evaluate_operator_attempt",
        lambda **_kwargs: {
            "status": "executed",
            "verification": VerificationOutcome(
                status="failed",
                failure_class="test_failed",
                import_smoke_ok=True,
                pytest_passed=4,
                pytest_failed=7,
            ),
            "session_id": None,
            "extraction_mode": "json_object",
            "note": "executed",
        },
    )

    def _fake_run_command(command, *, cwd=None, env=None, timeout_seconds=180.0):
        _ = env, timeout_seconds
        commands.append((list(command), cwd))
        return {
            "command": list(command),
            "exit_code": 0,
            "stdout": "",
            "stderr": "",
            "started_at": "t0",
            "ended_at": "t1",
        }

    monkeypatch.setattr(conformance, "run_command", _fake_run_command)

    result = conformance._run_gemini_cli_conformance(
        contract_pack=conformance.active_contract_pack(),
        run_root=run_root,
    )

    assert result.status == "divergent"
    assert result.divergence_class == "surface_wiring"
    assert result.repair_conversion == "failed_without_repair"
    assert result.note == "Gemini operator surface did not return a resumable session id."
    assert len(commands) == 1


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


def test_evaluate_operator_attempt_prefers_explicit_protocol_blocks_over_workspace_materialization(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workspace = tmp_path / "workspace"
    (workspace / "src" / "bookmarks_api").mkdir(parents=True)
    (workspace / "tests").mkdir(parents=True)
    (workspace / "src" / "bookmarks_api" / "main.py").write_text(
        "before\n",
        encoding="utf-8",
    )
    (workspace / "tests" / "test_bookmarks_api.py").write_text(
        "baseline\n",
        encoding="utf-8",
    )
    baseline = conformance.capture_workspace_state(workspace)
    (workspace / "src" / "bookmarks_api" / "main.py").write_text(
        "after-from-workspace\n",
        encoding="utf-8",
    )
    seen: dict[str, str] = {}

    def _fake_verify(result_text, _work_contract):
        seen["result_text"] = result_text
        return {}, VerificationOutcome(status="passed", failure_class=None)

    monkeypatch.setattr(conformance, "verify_verified_work_result", _fake_verify)

    result = conformance._evaluate_operator_attempt(
        provider="openai",
        command_result={
            "command": ["codex"],
            "exit_code": 0,
            "stdout": "\n".join(
                (
                    '{"type":"thread.started","thread_id":"thread-1"}',
                    '{"result":"=== FILE: src/bookmarks_api/main.py ===\\nfrom-protocol\\n=== END FILE ==="}',
                )
            ),
            "stderr": "",
        },
        work_contract=_work_contract(),
        project_root=workspace,
        workspace_baseline=baseline,
    )

    assert result["status"] == "executed"
    assert result["extraction_mode"] == "jsonl"
    assert seen["result_text"] == (
        "=== FILE: src/bookmarks_api/main.py ===\nfrom-protocol\n=== END FILE ==="
    )


def test_evaluate_operator_attempt_materializes_allowed_workspace_edits_for_openai(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workspace = tmp_path / "workspace"
    (workspace / "src" / "bookmarks_api").mkdir(parents=True)
    (workspace / "tests").mkdir(parents=True)
    (workspace / "src" / "bookmarks_api" / "main.py").write_text(
        "before\n",
        encoding="utf-8",
    )
    (workspace / "tests" / "test_bookmarks_api.py").write_text(
        "baseline\n",
        encoding="utf-8",
    )
    baseline = conformance.capture_workspace_state(workspace)
    (workspace / "src" / "bookmarks_api" / "main.py").write_text(
        "after-from-workspace\n",
        encoding="utf-8",
    )
    seen: dict[str, str] = {}

    def _fake_verify(result_text, _work_contract):
        seen["result_text"] = result_text
        return {}, VerificationOutcome(status="passed", failure_class=None)

    monkeypatch.setattr(conformance, "verify_verified_work_result", _fake_verify)

    result = conformance._evaluate_operator_attempt(
        provider="openai",
        command_result={
            "command": ["codex"],
            "exit_code": 0,
            "stdout": "\n".join(
                (
                    '{"type":"thread.started","thread_id":"thread-1"}',
                    '{"type":"item.completed","item":{"type":"agent_message","text":"editing workspace directly"}}',
                )
            ),
            "stderr": "",
        },
        work_contract=_work_contract(),
        project_root=workspace,
        workspace_baseline=baseline,
    )

    assert result["status"] == "executed"
    assert result["extraction_mode"] == "codex_workspace_materialized"
    assert "=== FILE: src/bookmarks_api/main.py ===" in seen["result_text"]
    assert "after-from-workspace" in seen["result_text"]


def test_evaluate_operator_attempt_materializes_changed_allowed_paths_in_contract_order(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workspace = tmp_path / "workspace"
    (workspace / "src" / "bookmarks_api").mkdir(parents=True)
    (workspace / "tests").mkdir(parents=True)
    for relative_path, content in {
        "src/bookmarks_api/main.py": "before-main\n",
        "src/bookmarks_api/models.py": "before-models\n",
        "src/bookmarks_api/store.py": "before-store\n",
        "tests/test_bookmarks_api.py": "baseline\n",
    }.items():
        target = workspace / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    baseline = conformance.capture_workspace_state(workspace)
    (workspace / "src" / "bookmarks_api" / "main.py").write_text(
        "after-main\n",
        encoding="utf-8",
    )
    (workspace / "src" / "bookmarks_api" / "store.py").write_text(
        "after-store\n",
        encoding="utf-8",
    )
    seen: dict[str, str] = {}

    def _fake_verify(result_text, _work_contract):
        seen["result_text"] = result_text
        return {}, VerificationOutcome(status="passed", failure_class=None)

    monkeypatch.setattr(conformance, "verify_verified_work_result", _fake_verify)
    work_contract = WorkContract(
        allowed_write_paths=(
            "src/bookmarks_api/store.py",
            "src/bookmarks_api/main.py",
            "src/bookmarks_api/models.py",
        ),
        verification_profile="python_workspace_pytest_v1",
        output_carrier="full_files",
        max_repair_turns=1,
    )

    result = conformance._evaluate_operator_attempt(
        provider="openai",
        command_result={
            "command": ["codex"],
            "exit_code": 0,
            "stdout": "\n".join(
                (
                    '{"type":"thread.started","thread_id":"thread-1"}',
                    '{"type":"item.completed","item":{"type":"agent_message","text":"edited allowed workspace files directly"}}',
                    '{"type":"item.completed","item":{"type":"file_change","changes":[{"path":"<temp-workspace>","kind":"update"}]}}',
                )
            ),
            "stderr": "",
        },
        work_contract=work_contract,
        project_root=workspace,
        workspace_baseline=baseline,
    )

    assert result["status"] == "executed"
    assert result["extraction_mode"] == "codex_workspace_materialized"
    assert seen["result_text"] == (
        "=== FILE: src/bookmarks_api/store.py ===\n"
        "after-store\n"
        "=== END FILE ===\n\n"
        "=== FILE: src/bookmarks_api/main.py ===\n"
        "after-main\n"
        "=== END FILE ==="
    )


def test_evaluate_operator_attempt_rejects_disallowed_tracked_path_changes(
    tmp_path: Path,
) -> None:
    workspace = tmp_path / "workspace"
    (workspace / "src" / "bookmarks_api").mkdir(parents=True)
    (workspace / "tests").mkdir(parents=True)
    (workspace / "src" / "bookmarks_api" / "main.py").write_text(
        "before\n",
        encoding="utf-8",
    )
    (workspace / "tests" / "test_bookmarks_api.py").write_text(
        "baseline\n",
        encoding="utf-8",
    )
    baseline = conformance.capture_workspace_state(workspace)
    (workspace / "tests" / "test_bookmarks_api.py").write_text(
        "changed-disallowed\n",
        encoding="utf-8",
    )

    result = conformance._evaluate_operator_attempt(
        provider="openai",
        command_result={
            "command": ["codex"],
            "exit_code": 0,
            "stdout": "\n".join(
                (
                    '{"type":"thread.started","thread_id":"thread-1"}',
                    '{"type":"item.completed","item":{"type":"command_execution","command":"sed","aggregated_output":"baseline"}}',
                )
            ),
            "stderr": "",
        },
        work_contract=_work_contract(),
        project_root=workspace,
        workspace_baseline=baseline,
    )

    verification = result["verification"]
    assert isinstance(verification, VerificationOutcome)
    assert verification.failure_class == "output_invalid"
    assert "disallowed path changes" in result["note"]


def test_evaluate_operator_attempt_classifies_openai_timeout_after_work_events(
) -> None:
    result = conformance._evaluate_operator_attempt(
        provider="openai",
        command_result={
            "command": ["codex"],
            "exit_code": 124,
            "stdout": "\n".join(
                (
                    '{"type":"thread.started","thread_id":"thread-1"}',
                    '{"type":"item.completed","item":{"type":"command_execution","command":"sed","aggregated_output":"baseline"}}',
                )
            ),
            "stderr": "",
        },
        work_contract=_work_contract(),
    )

    assert result["status"] == "timed_out"
    assert result["transport_failure_class"] == "operator_timeout"
    assert result["extraction_mode"] == "jsonl"
    assert "real work events" in result["note"]


def test_evaluate_operator_attempt_classifies_realistic_openai_timeout_artifact(
) -> None:
    result = conformance._evaluate_operator_attempt(
        provider="openai",
        command_result={
            "command": ["codex"],
            "exit_code": 124,
            "stdout": "\n".join(
                (
                    '{"type":"thread.started","thread_id":"thread-1"}',
                    '{"type":"turn.started"}',
                    '{"type":"item.completed","item":{"id":"item_0","type":"agent_message","text":"Implementing the FastAPI bookmark starter app now across the three allowed files."}}',
                    '{"type":"item.completed","item":{"id":"item_1","type":"file_change","changes":[{"path":"<temp-workspace>","kind":"update"}],"status":"completed"}}',
                    '{"type":"item.completed","item":{"id":"item_2","type":"agent_message","text":"Store behavior is in place; next I am connecting the FastAPI endpoints."}}',
                )
            ),
            "stderr": "\n".join(
                (
                    "2026-04-12T16:15:53.808474Z  WARN codex_state::runtime: failed to open state db at $HOME/.codex/state_5.sqlite: migration 23 was previously applied but is missing in the resolved migrations",
                    "2026-04-12T16:15:53.834731Z  WARN codex_rollout::list: state db discrepancy during find_thread_path_by_id_str_in_subdir: falling_back",
                    "operator timed out before returning a publishable result",
                )
            ),
        },
        work_contract=_work_contract(),
    )

    assert result["status"] == "timed_out"
    assert result["transport_failure_class"] == "operator_timeout"
    assert result["extraction_mode"] == "jsonl"
    assert "state db" in result["note"]
    assert "real work events" in result["note"]


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
            shipping_default="openai:operator_cli",
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
            shipping_default="openai:operator_cli",
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
        lambda: _fixed_utc_iso(8),
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
            surface="operator_cli",
            status="conformant",
            reason="ready",
        ),
    )
    monkeypatch.setattr(
        conformance,
        "_run_conformance",
        lambda **_kwargs: conformance.ConformanceRunResult(
            brain="openai",
            surface="operator_cli",
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
    assert summary["openai_ablation_config"] is None
    assert not (tmp_path / "summary.latest.json").exists()
    assert not (tmp_path / "summary.latest.md").exists()


def test_run_active_conformance_records_openai_ablation_config(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(conformance, "CONFORMANCE_ROOT", tmp_path)
    monkeypatch.setattr(conformance, "now_utc_iso", lambda: _fixed_utc_iso(8, 30))
    monkeypatch.setattr(conformance, "load_local_env_file", lambda: None)
    monkeypatch.setattr(
        conformance,
        "preflight_surface",
        lambda _brain, _surface: conformance.SurfaceProbe(
            brain="openai",
            surface="operator_cli",
            status="conformant",
            reason="ready",
        ),
    )
    monkeypatch.setattr(
        conformance,
        "_run_conformance",
        lambda **_kwargs: conformance.ConformanceRunResult(
            brain="openai",
            surface="operator_cli",
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

    summary = conformance.run_active_conformance(
        brains=("openai",),
        openai_ablation_config=conformance.OpenAIHostControlAblationConfig(
            verification_binding="off",
        ),
    )

    assert summary["openai_ablation_config"]["verification_binding"] == "off"


def test_run_active_conformance_reserves_unique_run_root_when_timestamp_repeats(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(conformance, "CONFORMANCE_ROOT", tmp_path)
    monkeypatch.setattr(conformance, "now_utc_iso", lambda: _fixed_utc_iso(8, 30))
    monkeypatch.setattr(conformance, "load_local_env_file", lambda: None)
    monkeypatch.setattr(
        conformance,
        "preflight_surface",
        lambda _brain, _surface: conformance.SurfaceProbe(
            brain="openai",
            surface="operator_cli",
            status="conformant",
            reason="ready",
        ),
    )
    monkeypatch.setattr(
        conformance,
        "_run_conformance",
        lambda *, run_root, **_kwargs: conformance.ConformanceRunResult(
            brain="openai",
            surface="operator_cli",
            contract_pack="verified_work_bookmarks_v1",
            status="conformant",
            attempt_count=1,
            verification_status="passed",
            parseable=True,
            import_smoke_ok=True,
            pytest_passed=11,
            repair_conversion="passed_without_repair",
            artifact_relpath=str(run_root),
        ),
    )

    first = conformance.run_active_conformance(brains=("openai",))
    second = conformance.run_active_conformance(brains=("openai",))

    first_relpath = first["results"][0]["artifact_relpath"]
    second_relpath = second["results"][0]["artifact_relpath"]
    assert first_relpath != second_relpath
    assert (tmp_path / "run_20260408T083000+0000").exists()
    assert (tmp_path / "run_20260408T083000+0000_2").exists()


def test_run_active_conformance_keeps_bookmarks_as_only_latest_summary_anchor(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    written_paths: list[Path] = []

    monkeypatch.setattr(conformance, "CONFORMANCE_ROOT", tmp_path)
    monkeypatch.setattr(
        conformance,
        "now_utc_iso",
        lambda: _fixed_utc_iso(8),
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
        lambda *, brain, surface, contract_pack, run_root, **_kwargs: conformance.ConformanceRunResult(
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


def test_run_active_conformance_does_not_publish_latest_for_backup_openai_service_lane(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    written_paths: list[Path] = []

    monkeypatch.setattr(conformance, "CONFORMANCE_ROOT", tmp_path)
    monkeypatch.setattr(
        conformance,
        "now_utc_iso",
        lambda: _fixed_utc_iso(8, 15),
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
        lambda *, brain, surface, contract_pack, **_kwargs: conformance.ConformanceRunResult(
            brain=brain,
            surface=surface,
            contract_pack=contract_pack.contract_pack,
            status="conformant",
            attempt_count=1,
            verification_status="passed",
            parseable=True,
            import_smoke_ok=True,
            pytest_passed=3,
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
        openai_surface="service_api",
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
        lambda: _fixed_utc_iso(9),
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
        lambda *, brain, surface, contract_pack, run_root, **_kwargs: conformance.ConformanceRunResult(
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
    monkeypatch.setattr(conformance, "accepted_conformance_next_decision", lambda: "promote")
    monkeypatch.setattr(conformance, "render_summary_markdown", lambda _summary: "")

    older_run = tmp_path / "run_20260408T070000+0000"
    newer_run = tmp_path / "run_20260408T071000+0000"
    older_run.mkdir(parents=True)
    newer_run.mkdir(parents=True)

    for run_dir in (older_run, newer_run):
        for artifact_name in (
            "openai_operator_cli",
            "claude_operator_cli",
            "gemini_operator_cli",
        ):
            (run_dir / artifact_name).mkdir()

    older_summary = {
        "generated_at": _fixed_utc_iso(7),
        "results": [
            {
                "brain": "openai",
                "surface": "operator_cli",
                "status": "conformant",
                "divergence_class": None,
                "parseable": True,
                "import_smoke_ok": True,
                "pytest_passed": 11,
                "pytest_failed": None,
                "repair_conversion": "passed_without_repair",
                "extraction_mode": None,
                "note": "runtime move: continue",
                "artifact_relpath": "run_20260408T070000+0000/openai_operator_cli",
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
        "shipping_truth": {"default": "openai:operator_cli"},
        "iteration_outcome": "promote",
        "overall_divergence_class": None,
        "contract_pack": conformance.active_contract_pack().as_payload(),
    }
    newer_summary = {
        "generated_at": _fixed_utc_iso(7, 10),
        "results": [
            {
                "brain": "openai",
                "surface": "operator_cli",
                "status": "conformant",
                "divergence_class": None,
                "parseable": True,
                "import_smoke_ok": True,
                "pytest_passed": 11,
                "pytest_failed": None,
                "repair_conversion": "passed_without_repair",
                "extraction_mode": None,
                "note": "runtime move: continue",
                "artifact_relpath": "run_20260408T071000+0000/openai_operator_cli",
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
        "shipping_truth": {"default": "openai:operator_cli"},
        "iteration_outcome": "revise",
        "overall_divergence_class": None,
        "contract_pack": conformance.active_contract_pack().as_payload(),
    }
    (older_run / "summary.json").write_text(json.dumps(older_summary), encoding="utf-8")
    (newer_run / "summary.json").write_text(json.dumps(newer_summary), encoding="utf-8")

    reconciled = conformance.reconcile_latest_summary()

    assert reconciled["generated_at"] == _fixed_utc_iso(7)
    assert (tmp_path / "summary.latest.json").exists()


def test_reconcile_latest_summary_prefers_publishable_cli_anchor_over_newer_backup_lane_run(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(conformance, "CONFORMANCE_ROOT", tmp_path)
    monkeypatch.setattr(conformance, "ROOT", tmp_path)
    monkeypatch.setattr(conformance, "accepted_conformance_next_decision", lambda: "promote")
    monkeypatch.setattr(conformance, "render_summary_markdown", lambda _summary: "")

    cli_run = tmp_path / "run_20260408T070000+0000"
    backup_run = tmp_path / "run_20260408T071000+0000"
    cli_run.mkdir(parents=True)
    backup_run.mkdir(parents=True)

    for run_dir, openai_dir in (
        (cli_run, "openai_operator_cli"),
        (backup_run, "openai_service_api"),
    ):
        for artifact_name in (
            openai_dir,
            "claude_operator_cli",
            "gemini_operator_cli",
        ):
            (run_dir / artifact_name).mkdir()

    cli_summary = {
        "generated_at": _fixed_utc_iso(7),
        "results": [
            {
                "brain": "openai",
                "surface": "operator_cli",
                "artifact_relpath": "run_20260408T070000+0000/openai_operator_cli",
            },
            {
                "brain": "claude",
                "surface": "operator_cli",
                "artifact_relpath": "run_20260408T070000+0000/claude_operator_cli",
            },
            {
                "brain": "gemini",
                "surface": "operator_cli",
                "artifact_relpath": "run_20260408T070000+0000/gemini_operator_cli",
            },
        ],
        "next_decision": "promote",
        "shipping_truth": {"default": "openai:operator_cli"},
        "iteration_outcome": "promote",
        "overall_divergence_class": None,
        "contract_pack": conformance.active_contract_pack().as_payload(),
    }
    backup_summary = {
        "generated_at": _fixed_utc_iso(7, 10),
        "results": [
            {
                "brain": "openai",
                "surface": "service_api",
                "artifact_relpath": "run_20260408T071000+0000/openai_service_api",
            },
            {
                "brain": "claude",
                "surface": "operator_cli",
                "artifact_relpath": "run_20260408T071000+0000/claude_operator_cli",
            },
            {
                "brain": "gemini",
                "surface": "operator_cli",
                "artifact_relpath": "run_20260408T071000+0000/gemini_operator_cli",
            },
        ],
        "next_decision": "promote",
        "shipping_truth": {"default": "openai:operator_cli"},
        "iteration_outcome": "promote",
        "overall_divergence_class": None,
        "contract_pack": conformance.active_contract_pack().as_payload(),
    }
    (cli_run / "summary.json").write_text(json.dumps(cli_summary), encoding="utf-8")
    (backup_run / "summary.json").write_text(json.dumps(backup_summary), encoding="utf-8")

    reconciled = conformance.reconcile_latest_summary()

    assert reconciled["generated_at"] == _fixed_utc_iso(7)
    assert reconciled["results"][0]["surface"] == "operator_cli"


def test_reconcile_latest_summary_ignores_newer_non_anchor_pack_full_runs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(conformance, "CONFORMANCE_ROOT", tmp_path)
    monkeypatch.setattr(conformance, "ROOT", tmp_path)
    monkeypatch.setattr(conformance, "accepted_conformance_next_decision", lambda: "promote")
    monkeypatch.setattr(conformance, "render_summary_markdown", lambda _summary: "")

    older_run = tmp_path / "run_20260408T070000+0000"
    newer_run = tmp_path / "run_20260408T080000+0000"
    older_run.mkdir(parents=True)
    newer_run.mkdir(parents=True)
    for run_dir in (older_run, newer_run):
        for artifact_name in (
            "openai_operator_cli",
            "claude_operator_cli",
            "gemini_operator_cli",
        ):
            (run_dir / artifact_name).mkdir()

    older_summary = {
        "generated_at": _fixed_utc_iso(7),
        "results": [
            {
                "brain": "openai",
                "surface": "operator_cli",
                "artifact_relpath": "run_20260408T070000+0000/openai_operator_cli",
            },
            {
                "brain": "claude",
                "surface": "operator_cli",
                "artifact_relpath": "run_20260408T070000+0000/claude_operator_cli",
            },
            {
                "brain": "gemini",
                "surface": "operator_cli",
                "artifact_relpath": "run_20260408T070000+0000/gemini_operator_cli",
            },
        ],
        "next_decision": "promote",
        "shipping_truth": {"default": "openai:operator_cli"},
        "iteration_outcome": "promote",
        "overall_divergence_class": None,
        "contract_pack": conformance.active_contract_pack().as_payload(),
    }
    newer_summary = {
        "generated_at": _fixed_utc_iso(8),
        "results": [
            {
                "brain": "openai",
                "artifact_relpath": "run_20260408T080000+0000/openai_operator_cli",
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
        "shipping_truth": {"default": "openai:operator_cli"},
        "iteration_outcome": "promote",
        "overall_divergence_class": None,
        "contract_pack": conformance.contract_pack_by_name(
            conformance.NORMALIZE_PORT_CONTRACT_PACK
        ).as_payload(),
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
    monkeypatch.setattr(conformance, "accepted_conformance_next_decision", lambda: "promote")

    newer_run = tmp_path / "run_20260408T071000+0000"
    newer_run.mkdir(parents=True)
    for artifact_name in (
        "openai_operator_cli",
        "claude_operator_cli",
        "gemini_operator_cli",
    ):
        (newer_run / artifact_name).mkdir()

    newer_summary = {
        "generated_at": _fixed_utc_iso(7, 10),
        "results": [
            {
                "brain": "openai",
                "surface": "operator_cli",
                "status": "conformant",
                "divergence_class": None,
                "parseable": True,
                "import_smoke_ok": True,
                "pytest_passed": 11,
                "pytest_failed": None,
                "repair_conversion": "passed_without_repair",
                "extraction_mode": None,
                "note": "runtime move: continue",
                "artifact_relpath": "run_20260408T071000+0000/openai_operator_cli",
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
        "shipping_truth": {"default": "openai:operator_cli"},
        "iteration_outcome": "revise",
        "overall_divergence_class": None,
        "contract_pack": conformance.active_contract_pack().as_payload(),
    }
    (newer_run / "summary.json").write_text(json.dumps(newer_summary), encoding="utf-8")

    reconciled = conformance.reconcile_latest_summary()

    assert reconciled["generated_at"] == _fixed_utc_iso(7, 10)


def test_reconcile_latest_summary_fails_when_only_backup_lane_full_runs_survive(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(conformance, "CONFORMANCE_ROOT", tmp_path)
    monkeypatch.setattr(conformance, "ROOT", tmp_path)
    monkeypatch.setattr(conformance, "accepted_conformance_next_decision", lambda: "promote")

    run_dir = tmp_path / "run_20260408T071000+0000"
    run_dir.mkdir(parents=True)
    for artifact_name in (
        "openai_service_api",
        "claude_operator_cli",
        "gemini_operator_cli",
    ):
        (run_dir / artifact_name).mkdir()

    backup_summary = {
        "generated_at": _fixed_utc_iso(7, 10),
        "results": [
            {
                "brain": "openai",
                "surface": "service_api",
                "artifact_relpath": "run_20260408T071000+0000/openai_service_api",
            },
            {
                "brain": "claude",
                "surface": "operator_cli",
                "artifact_relpath": "run_20260408T071000+0000/claude_operator_cli",
            },
            {
                "brain": "gemini",
                "surface": "operator_cli",
                "artifact_relpath": "run_20260408T071000+0000/gemini_operator_cli",
            },
        ],
        "next_decision": "promote",
        "shipping_truth": {"default": "openai:operator_cli"},
        "iteration_outcome": "promote",
        "overall_divergence_class": None,
        "contract_pack": conformance.active_contract_pack().as_payload(),
    }
    (run_dir / "summary.json").write_text(json.dumps(backup_summary), encoding="utf-8")

    with pytest.raises(RuntimeError, match="publishable full tri-brain conformance summary"):
        conformance.reconcile_latest_summary()
