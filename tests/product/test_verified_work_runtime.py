"""Focused tests for the shared verified-work runtime helpers."""

from __future__ import annotations

import pytest

from cortex.runtime.verified_work_runtime import (
    build_verified_work_input_text,
    build_verified_work_instructions,
    build_verified_work_repair_ticket,
    verify_verified_work_result,
)
from cortex.sre.preservation import derive_preservation_state
from cortex.sre.verified_work import VerificationOutcome, WorkContract

from tests.product._verified_work_fixtures import (
    VALID_FEATURE_FLAG_FILE_MAP,
    VALID_FILE_MAP,
    VALID_NORMALIZE_PORT_FILE_MAP,
    render_full_files_result,
)


def _work_contract(max_repair_turns: int = 1) -> WorkContract:
    return WorkContract(
        allowed_write_paths=tuple(VALID_FILE_MAP),
        verification_profile="python_workspace_pytest_v1",
        output_carrier="full_files",
        max_repair_turns=max_repair_turns,
    )


def _normalize_port_work_contract(max_repair_turns: int = 1) -> WorkContract:
    return WorkContract(
        allowed_write_paths=tuple(VALID_NORMALIZE_PORT_FILE_MAP),
        verification_profile="python_workspace_pytest_port_fix_v1",
        output_carrier="full_files",
        max_repair_turns=max_repair_turns,
    )


def _feature_flags_work_contract(max_repair_turns: int = 1) -> WorkContract:
    return WorkContract(
        allowed_write_paths=tuple(VALID_FEATURE_FLAG_FILE_MAP),
        verification_profile="python_workspace_pytest_feature_flags_v1",
        output_carrier="full_files",
        max_repair_turns=max_repair_turns,
    )


def test_build_verified_work_instructions_lists_allowed_paths() -> None:
    instructions = build_verified_work_instructions(_work_contract())

    assert "=== FILE: relative/path ===" in instructions
    assert "=== BLOCKED: needs_user_input ===" in instructions
    assert "=== BLOCKED: unsafe_request ===" in instructions
    assert "Do not return prose" in instructions
    assert "src/bookmarks_api/main.py" in instructions


def test_build_verified_work_contract_binding_lean_shortens_instructions_and_repair_ticket() -> None:
    instructions = build_verified_work_instructions(
        _work_contract(),
        contract_binding_profile="lean",
    )

    assert "Return only protocol blocks for the allowed paths." in instructions
    assert "Do not return prose" not in instructions

    state = derive_preservation_state(
        None,
        _work_contract(),
        ("src/bookmarks_api/main.py",),
        VerificationOutcome(
            status="failed",
            failure_class="test_failed",
            parsed_paths=("src/bookmarks_api/main.py",),
            import_smoke_ok=True,
            pytest_ok=False,
            pytest_exit_code=1,
            pytest_passed=3,
            pytest_failed=1,
            failing_tests=("tests/test_bookmarks_api.py::test_create_and_get_bookmark_by_id",),
            first_failure_excerpt="FAILED tests/test_bookmarks_api.py::test_create_and_get_bookmark_by_id",
        ),
        remaining_repairs=1,
    )

    ticket = build_verified_work_repair_ticket(
        state,
        contract_binding_profile="lean",
    )

    assert "trusted_checks:" not in ticket
    assert "failure_class: test_failed" in ticket


def test_build_verified_work_input_text_attaches_workspace_context() -> None:
    input_text = build_verified_work_input_text("build bookmarks app", _work_contract())

    assert input_text.startswith("build bookmarks app")
    assert "Read-only workspace context follows." in input_text
    assert "=== CONTEXT FILE: src/bookmarks_api/main.py ===" in input_text
    assert "=== CONTEXT FILE: tests/test_bookmarks_api.py ===" in input_text
    assert "app = FastAPI(title=\"Bookmarks API\")" in input_text
    assert "test_create_and_get_bookmark_by_id" in input_text


def test_build_verified_work_input_text_attaches_normalize_port_context() -> None:
    input_text = build_verified_work_input_text("fix normalize_port", _normalize_port_work_contract())

    assert input_text.startswith("fix normalize_port")
    assert "=== CONTEXT FILE: src/normalize_port.py ===" in input_text
    assert "=== CONTEXT FILE: tests/test_normalize_port.py ===" in input_text
    assert "if port >= 65535" in input_text
    assert "assert normalize_port(65535) == 65535" in input_text


def test_build_verified_work_input_text_attaches_feature_flags_context() -> None:
    input_text = build_verified_work_input_text(
        "implement feature flags",
        _feature_flags_work_contract(),
    )

    assert input_text.startswith("implement feature flags")
    assert "=== CONTEXT FILE: src/feature_flags/models.py ===" in input_text
    assert "=== CONTEXT FILE: src/feature_flags/evaluator.py ===" in input_text
    assert "=== CONTEXT FILE: tests/test_feature_flags.py ===" in input_text
    assert "FeatureFlag" in input_text
    assert "test_deny_country_wins_over_allow_and_rollout" in input_text


def test_build_verified_work_input_text_can_disable_or_narrow_context() -> None:
    no_context = build_verified_work_input_text(
        "build bookmarks app",
        _work_contract(),
        context_mode="off",
    )
    writable_only = build_verified_work_input_text(
        "build bookmarks app",
        _work_contract(),
        context_mode="writable_files_only",
    )

    assert no_context == "build bookmarks app"
    assert "=== CONTEXT FILE: tests/test_bookmarks_api.py ===" not in writable_only
    assert "=== CONTEXT FILE: src/bookmarks_api/main.py ===" in writable_only


def test_build_verified_work_input_text_lean_uses_shorter_context_intro() -> None:
    input_text = build_verified_work_input_text(
        "build bookmarks app",
        _work_contract(),
        context_mode="writable_files_only",
        contract_binding_profile="lean",
    )

    assert input_text.startswith("build bookmarks app")
    assert "Workspace context follows. Edit only allowed paths." in input_text
    assert "Read-only workspace context follows." not in input_text
    assert "=== CONTEXT FILE: src/bookmarks_api/main.py ===" in input_text
    assert "=== CONTEXT FILE: tests/test_bookmarks_api.py ===" not in input_text


def test_verify_verified_work_result_rejects_unapproved_path() -> None:
    _, outcome = verify_verified_work_result(
        "\n".join(
            [
                "=== FILE: src/bookmarks_api/main.py ===",
                "from fastapi import FastAPI",
                "app = FastAPI()",
                "=== END FILE ===",
                "=== FILE: src/bookmarks_api/extra.py ===",
                "x = 1",
                "=== END FILE ===",
            ]
        ),
        _work_contract(),
    )

    assert outcome.status == "failed"
    assert outcome.failure_class == "output_invalid"
    assert "unapproved write path" in (outcome.parse_error or "")


def test_verify_verified_work_result_preserves_blocked_missing_info() -> None:
    _, outcome = verify_verified_work_result(
        "\n".join(
            [
                "=== BLOCKED: needs_user_input ===",
                "Need a retention rule for archived bookmarks.",
                "=== END BLOCKED ===",
            ]
        ),
        _work_contract(),
    )

    assert outcome.status == "blocked"
    assert outcome.failure_class == "blocked_missing_info"
    assert outcome.blocked_message == "Need a retention rule for archived bookmarks."


def test_verify_verified_work_result_ignores_blank_lines_between_file_blocks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "cortex.runtime.verified_work_runtime._run_verified_work_verifier",
        lambda file_map, work_contract: VerificationOutcome(
            status="passed",
            failure_class=None,
            parsed_paths=tuple(file_map),
            import_smoke_ok=True,
            pytest_ok=True,
            pytest_exit_code=0,
            pytest_passed=11,
            pytest_failed=0,
        ),
    )
    result_text = (
        "=== FILE: src/bookmarks_api/models.py ===\n"
        "from pydantic import BaseModel\n"
        "=== END FILE ===\n\n"
        "=== FILE: src/bookmarks_api/store.py ===\n"
        "class BookmarkStore:\n"
        "    pass\n"
        "=== END FILE ===\n\n"
        "=== FILE: src/bookmarks_api/main.py ===\n"
        "from fastapi import FastAPI\n"
        "app = FastAPI()\n"
        "=== END FILE ===\n"
    )

    file_map, outcome = verify_verified_work_result(result_text, _work_contract())

    assert file_map is not None
    assert outcome.status == "passed"


def test_verify_verified_work_result_catches_import_failures(monkeypatch: pytest.MonkeyPatch) -> None:
    broken_file_map = dict(VALID_FILE_MAP)
    broken_file_map["src/bookmarks_api/main.py"] = "from fastapi import FastAPI\napp = FastAPI(\n"
    monkeypatch.setattr(
        "cortex.runtime.verified_work_runtime._run_verified_work_verifier",
        lambda file_map, work_contract: VerificationOutcome(
            status="failed",
            failure_class="import_smoke_failed",
            parsed_paths=tuple(file_map),
            import_smoke_ok=False,
            import_smoke_excerpt="E   SyntaxError: '(' was never closed",
            first_failure_excerpt="E   SyntaxError: '(' was never closed",
        ),
    )

    _, outcome = verify_verified_work_result(
        render_full_files_result(broken_file_map),
        _work_contract(),
    )

    assert outcome.status == "failed"
    assert outcome.failure_class == "import_smoke_failed"
    assert outcome.import_smoke_ok is False
    assert outcome.first_failure_excerpt is not None


def test_verify_verified_work_result_accepts_passing_submission(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "cortex.runtime.verified_work_runtime._run_verified_work_verifier",
        lambda file_map, work_contract: VerificationOutcome(
            status="passed",
            failure_class=None,
            parsed_paths=tuple(file_map),
            import_smoke_ok=True,
            pytest_ok=True,
            pytest_exit_code=0,
            pytest_passed=11,
            pytest_failed=0,
        ),
    )
    file_map, outcome = verify_verified_work_result(
        render_full_files_result(VALID_FILE_MAP),
        _work_contract(),
    )

    assert file_map == VALID_FILE_MAP
    assert outcome.status == "passed"
    assert outcome.failure_class is None
    assert outcome.import_smoke_ok is True
    assert outcome.pytest_ok is True
    assert outcome.pytest_passed == 11
    assert outcome.pytest_failed == 0


def test_verify_verified_work_result_overlays_preserved_files_for_repair_verification(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repaired_main_only = {
        "src/bookmarks_api/main.py": VALID_FILE_MAP["src/bookmarks_api/main.py"],
    }
    seen: dict[str, object] = {}

    def _fake_run_verified_work_verifier(file_map, work_contract):
        seen["file_map"] = dict(file_map)
        seen["work_contract"] = work_contract
        return VerificationOutcome(
            status="passed",
            failure_class=None,
            parsed_paths=tuple(file_map),
            import_smoke_ok=True,
            pytest_ok=True,
            pytest_exit_code=0,
            pytest_passed=11,
            pytest_failed=0,
        )

    monkeypatch.setattr(
        "cortex.runtime.verified_work_runtime._run_verified_work_verifier",
        _fake_run_verified_work_verifier,
    )
    narrowed_contract = WorkContract(
        allowed_write_paths=("src/bookmarks_api/main.py",),
        verification_profile="python_workspace_pytest_v1",
        output_carrier="full_files",
        max_repair_turns=0,
    )

    file_map, outcome = verify_verified_work_result(
        render_full_files_result(repaired_main_only),
        narrowed_contract,
        preserved_file_map={
            "src/bookmarks_api/models.py": VALID_FILE_MAP["src/bookmarks_api/models.py"],
            "src/bookmarks_api/store.py": VALID_FILE_MAP["src/bookmarks_api/store.py"],
        },
        verifier_contract=_work_contract(),
    )

    assert file_map == VALID_FILE_MAP
    assert outcome.status == "passed"
    assert seen["file_map"] == VALID_FILE_MAP
    assert seen["work_contract"] == _work_contract()


def test_build_verified_work_repair_ticket_is_factual_only() -> None:
    state = derive_preservation_state(
        None,
        _work_contract(),
        (),
        VerificationOutcome(
            status="blocked",
            failure_class="blocked_unsafe",
            blocked_message="Cannot help with that.",
        ),
        remaining_repairs=1,
    )

    ticket = build_verified_work_repair_ticket(state)

    assert "task_anchor: verified-work:python_workspace_pytest_v1:" in ticket
    assert "failure_class: blocked_unsafe" in ticket
    assert "falsified_checks: blocked" in ticket
    assert "lawful_repair_surface: <none>" in ticket


def test_build_verified_work_repair_ticket_supports_minimal_style() -> None:
    state = derive_preservation_state(
        None,
        _work_contract(),
        ("src/bookmarks_api/main.py",),
        VerificationOutcome(
            status="failed",
            failure_class="test_failed",
            parsed_paths=("src/bookmarks_api/main.py",),
            import_smoke_ok=True,
            pytest_ok=False,
            pytest_exit_code=1,
            pytest_passed=3,
            pytest_failed=1,
            failing_tests=("tests/test_bookmarks_api.py::test_create_and_get_bookmark_by_id",),
            first_failure_excerpt="FAILED tests/test_bookmarks_api.py::test_create_and_get_bookmark_by_id",
        ),
        remaining_repairs=1,
    )

    ticket = build_verified_work_repair_ticket(
        state,
        style="minimal",
    )

    assert "task_anchor: verified-work:python_workspace_pytest_v1:" in ticket
    assert "failure_class: test_failed" in ticket
    assert "falsified_checks: pytest" in ticket
    assert "lawful_repair_surface: src/bookmarks_api/main.py" in ticket
    assert "remaining_repairs: 1" in ticket


def test_verify_verified_work_result_uses_profile_specific_verifier_targets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    commands: list[list[str]] = []

    class _Result:
        def __init__(self, returncode: int = 0, stdout: str = "", stderr: str = "") -> None:
            self.returncode = returncode
            self.stdout = stdout
            self.stderr = stderr

    monkeypatch.setattr(
        "cortex.runtime.verified_work_runtime._prepare_verified_work_python",
        lambda _project_root: "/usr/bin/python3",
    )

    def _fake_run_command(command, *, cwd):
        _ = cwd
        commands.append(list(command))
        return _Result(returncode=0, stdout="2 passed", stderr="")

    monkeypatch.setattr(
        "cortex.runtime.verified_work_runtime._run_command",
        _fake_run_command,
    )

    _, bookmarks_outcome = verify_verified_work_result(
        render_full_files_result(VALID_FILE_MAP),
        _work_contract(),
    )
    _, port_outcome = verify_verified_work_result(
        render_full_files_result(VALID_NORMALIZE_PORT_FILE_MAP),
        _normalize_port_work_contract(),
    )
    _, feature_flags_outcome = verify_verified_work_result(
        render_full_files_result(VALID_FEATURE_FLAG_FILE_MAP),
        _feature_flags_work_contract(),
    )

    assert bookmarks_outcome.status == "passed"
    assert port_outcome.status == "passed"
    assert feature_flags_outcome.status == "passed"
    assert commands[0] == [
        "/usr/bin/python3",
        "-c",
        "import importlib; importlib.import_module('bookmarks_api.main')",
    ]
    assert commands[1] == [
        "/usr/bin/python3",
        "-m",
        "pytest",
        "-q",
        "tests/test_bookmarks_api.py",
    ]
    assert commands[2] == [
        "/usr/bin/python3",
        "-c",
        "import importlib; importlib.import_module('normalize_port')",
    ]
    assert commands[3] == [
        "/usr/bin/python3",
        "-m",
        "pytest",
        "-q",
        "tests/test_normalize_port.py",
    ]
    assert commands[4] == [
        "/usr/bin/python3",
        "-c",
        "import importlib; importlib.import_module('feature_flags.evaluator')",
    ]
    assert commands[5] == [
        "/usr/bin/python3",
        "-m",
        "pytest",
        "-q",
        "tests/test_feature_flags.py",
    ]
