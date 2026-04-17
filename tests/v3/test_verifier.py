"""Verified-work protocol, parity, and verifier tests for Cortex v3."""

from __future__ import annotations

import pytest

from cortex.runtime.verified_work_runtime import (
    build_verified_work_input_text as build_v2_input_text,
)
from cortex.runtime.verified_work_runtime import (
    build_verified_work_instructions as build_v2_instructions,
)
from cortex.runtime.verified_work_runtime import (
    verify_verified_work_result as verify_v2_result,
)
from cortex.sre.preservation import derive_preservation_state as derive_v2_preservation_state
from cortex.sre.verified_work import VerificationOutcome as V2VerificationOutcome
from cortex.sre.verified_work import WorkContract as V2WorkContract
from cortex_v3.contracts import PreservationState, VerificationOutcome, WorkContract
from cortex_v3.preservation import derive_preservation_state
from cortex_v3.verifier import (
    build_verified_work_input_text,
    build_verified_work_instructions,
    build_verified_work_repair_ticket,
    build_verified_work_repair_prompt,
    _falsified_checks,
    verify_verified_work_result,
)
from tests.product._verified_work_fixtures import (
    VALID_FEATURE_FLAG_FILE_MAP,
    VALID_FILE_MAP,
    VALID_NORMALIZE_PORT_FILE_MAP,
    render_full_files_result,
)


def _bookmarks_contract(max_repair_turns: int = 1) -> WorkContract:
    return WorkContract(
        allowed_write_paths=(
            "src/bookmarks_api/main.py",
            "src/bookmarks_api/models.py",
            "src/bookmarks_api/store.py",
        ),
        verification_profile="python_workspace_pytest_v1",
        max_repair_turns=max_repair_turns,
    )


def _normalize_port_contract(max_repair_turns: int = 1) -> WorkContract:
    return WorkContract(
        allowed_write_paths=("src/normalize_port.py",),
        verification_profile="python_workspace_pytest_port_fix_v1",
        max_repair_turns=max_repair_turns,
    )


def _feature_flags_contract(max_repair_turns: int = 1) -> WorkContract:
    return WorkContract(
        allowed_write_paths=(
            "src/feature_flags/models.py",
            "src/feature_flags/evaluator.py",
        ),
        verification_profile="python_workspace_pytest_feature_flags_v1",
        max_repair_turns=max_repair_turns,
    )


@pytest.mark.parametrize(
    ("task_prompt", "contract"),
    [
        ("build bookmarks app", _bookmarks_contract()),
        ("fix normalize_port", _normalize_port_contract()),
        ("fix feature flag evaluator", _feature_flags_contract()),
    ],
)
def test_v3_build_verified_work_instructions_matches_v2(
    task_prompt: str,
    contract: WorkContract,
) -> None:
    del task_prompt
    v2_contract = V2WorkContract(**contract.as_payload())

    assert build_verified_work_instructions(contract) == build_v2_instructions(v2_contract)


@pytest.mark.parametrize(
    ("task_prompt", "contract"),
    [
        ("build bookmarks app", _bookmarks_contract()),
        ("fix normalize_port", _normalize_port_contract()),
        ("fix feature flag evaluator", _feature_flags_contract()),
    ],
)
def test_v3_build_verified_work_input_text_matches_v2_default_context(
    task_prompt: str,
    contract: WorkContract,
) -> None:
    v2_contract = V2WorkContract(**contract.as_payload())

    assert build_verified_work_input_text(task_prompt, contract) == build_v2_input_text(
        task_prompt,
        v2_contract,
    )


@pytest.mark.parametrize(
    ("contract", "file_map"),
    [
        (_bookmarks_contract(), VALID_FILE_MAP),
        (_normalize_port_contract(), VALID_NORMALIZE_PORT_FILE_MAP),
        (_feature_flags_contract(), VALID_FEATURE_FLAG_FILE_MAP),
    ],
)
def test_v3_verify_verified_work_result_matches_v2_for_valid_workspace(
    contract: WorkContract,
    file_map: dict[str, str],
) -> None:
    v2_contract = V2WorkContract(**contract.as_payload())
    result_text = render_full_files_result(file_map)

    v3_file_map, v3_outcome = verify_verified_work_result(result_text, contract)
    v2_file_map, v2_outcome = verify_v2_result(result_text, v2_contract)

    assert v3_file_map == v2_file_map
    assert v3_outcome.as_payload() == v2_outcome.as_payload()


@pytest.mark.parametrize(
    "blocked_text",
    [
        "=== BLOCKED: needs_user_input ===\nNeed the archive retention policy.\n=== END BLOCKED ===",
        "=== BLOCKED: unsafe_request ===\nDeleting production data is unsafe.\n=== END BLOCKED ===",
    ],
)
def test_v3_verify_verified_work_result_matches_v2_for_blocked_markers(
    blocked_text: str,
) -> None:
    contract = _bookmarks_contract()
    v2_contract = V2WorkContract(**contract.as_payload())

    v3_file_map, v3_outcome = verify_verified_work_result(blocked_text, contract)
    v2_file_map, v2_outcome = verify_v2_result(blocked_text, v2_contract)

    assert v3_file_map == v2_file_map
    assert v3_outcome.as_payload() == v2_outcome.as_payload()


def test_v3_build_verified_work_repair_prompt_keeps_peer_files_visible_and_writes_narrowed() -> None:
    contract = _bookmarks_contract()
    broken_main = "from fastapi import FastAPI\napp = FastAPI(\n"
    first_attempt = render_full_files_result({"src/bookmarks_api/main.py": broken_main})
    file_map, outcome = verify_verified_work_result(first_attempt, contract)

    assert file_map is not None
    state = derive_preservation_state(
        contract.allowed_write_paths[0],
        contract,
        outcome,
        remaining_repairs=1,
    )

    repair_contract = WorkContract(
        allowed_write_paths=("src/bookmarks_api/main.py",),
        verification_profile=contract.verification_profile,
        max_repair_turns=0,
    )
    prompt = build_verified_work_repair_prompt(
        "build bookmarks app",
        repair_contract,
        state,
        writable_file_map=file_map,
        visible_context_paths=contract.allowed_write_paths,
    )

    assert "build bookmarks app" in prompt
    assert "failure_class: import_smoke_failed" in prompt
    assert "=== CONTEXT FILE: src/bookmarks_api/main.py ===" in prompt
    assert "=== CONTEXT FILE: src/bookmarks_api/models.py ===" in prompt
    assert "=== CONTEXT FILE: src/bookmarks_api/store.py ===" in prompt
    assert "=== CONTEXT FILE: tests/test_bookmarks_api.py ===" in prompt
    assert broken_main.strip() in prompt


def test_v3_build_verified_work_repair_ticket_follows_canonical_spec() -> None:
    state = PreservationState(
        task_anchor="verified-work:test:src/example.py",
        trusted_checks=("pytest", "parse", "import_smoke"),
        trusted_paths=("src/zeta.py", "src/alpha.py"),
        failure_class="test_failed",
        failing_tests=("tests/test_zeta.py::test_two", "tests/test_alpha.py::test_one"),
        blocked_message=None,
        lawful_repair_surface=("src/zeta.py", "src/alpha.py"),
        allowed_moves=("repair", "check"),
        remaining_repairs=1,
    )

    ticket = build_verified_work_repair_ticket(state)

    assert ticket.splitlines() == [
        "task_anchor: verified-work:test:src/example.py",
        "trusted_checks: import_smoke, parse, pytest",
        "trusted_paths: src/alpha.py, src/zeta.py",
        "failure_class: test_failed",
        "falsified_checks: pytest",
        "failing_tests: tests/test_alpha.py::test_one, tests/test_zeta.py::test_two",
        "lawful_repair_surface: src/alpha.py, src/zeta.py",
        "remaining_repairs: 1",
        "allowed_moves: check, repair",
    ]
    assert _falsified_checks("import_smoke_failed") == ("import_smoke",)
    assert _falsified_checks("blocked_missing_info") == ("blocked",)
    assert _falsified_checks(None) == ()


def test_v3_build_verified_work_repair_ticket_renders_none_for_empty_list_fields() -> None:
    state = PreservationState(
        task_anchor="verified-work:test:src/example.py",
        trusted_checks=(),
        trusted_paths=(),
        failure_class=None,
        failing_tests=(),
        blocked_message=None,
        lawful_repair_surface=(),
        allowed_moves=("continue",),
        remaining_repairs=0,
    )

    ticket = build_verified_work_repair_ticket(state)

    assert "trusted_checks: <none>" in ticket
    assert "trusted_paths: <none>" in ticket
    assert "falsified_checks: <none>" in ticket
    assert "failing_tests: <none>" in ticket
    assert "lawful_repair_surface: <none>" in ticket


def test_v3_preservation_state_matches_v2_law_for_repairable_failure() -> None:
    contract = _bookmarks_contract()
    outcome = VerificationOutcome(
        status="failed",
        failure_class="test_failed",
        parsed_paths=("src/bookmarks_api/main.py",),
        import_smoke_ok=True,
        pytest_ok=False,
        pytest_exit_code=1,
        pytest_passed=12,
        pytest_failed=1,
        failing_tests=("tests/test_bookmarks_api.py::test_create_and_get_bookmark_by_id",),
        first_failure_excerpt="FAILED tests/test_bookmarks_api.py::test_create_and_get_bookmark_by_id",
    )
    v2_state = derive_v2_preservation_state(
        None,
        V2WorkContract(**contract.as_payload()),
        outcome.parsed_paths,
        V2VerificationOutcome(
            status=outcome.status,
            failure_class=outcome.failure_class,
            parsed_paths=outcome.parsed_paths,
            import_smoke_ok=outcome.import_smoke_ok,
            pytest_ok=outcome.pytest_ok,
            pytest_exit_code=outcome.pytest_exit_code,
            pytest_passed=outcome.pytest_passed,
            pytest_failed=outcome.pytest_failed,
            failing_tests=outcome.failing_tests,
            first_failure_excerpt=outcome.first_failure_excerpt,
        ),
        remaining_repairs=1,
    )
    v3_state = derive_preservation_state(None, contract, outcome, remaining_repairs=1)

    assert set(v3_state.allowed_moves) == set(v2_state.intervention_budget.allowed_moves)
    assert set(v3_state.lawful_repair_surface) == set(v2_state.lawful_repair_surface)


@pytest.mark.parametrize(
    ("failure_class", "blocked_message"),
    [
        ("blocked_missing_info", "Need the archive retention policy."),
        ("blocked_unsafe", "Deleting production data is unsafe."),
    ],
)
def test_v3_preservation_state_matches_v2_law_for_blocked_outcomes(
    failure_class: str,
    blocked_message: str,
) -> None:
    contract = _bookmarks_contract()
    outcome = VerificationOutcome(
        status="blocked",
        failure_class=failure_class,
        blocked_message=blocked_message,
    )
    v2_state = derive_v2_preservation_state(
        None,
        V2WorkContract(**contract.as_payload()),
        outcome.parsed_paths,
        V2VerificationOutcome(
            status=outcome.status,
            failure_class=outcome.failure_class,
            blocked_message=outcome.blocked_message,
        ),
        remaining_repairs=1,
    )
    v3_state = derive_preservation_state(None, contract, outcome, remaining_repairs=1)

    assert set(v3_state.allowed_moves) == set(v2_state.intervention_budget.allowed_moves)
    assert set(v3_state.lawful_repair_surface) == set(v2_state.lawful_repair_surface)
