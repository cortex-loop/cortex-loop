"""Focused tests for the shipped preservation-state machine."""

from __future__ import annotations

import pytest

from cortex.sre.preservation import (
    FalsifiedStructure,
    InterventionBudget,
    PreservationState,
    TrustedStructure,
    choose_preservation_move,
    derive_preservation_state,
)
from cortex.sre.verified_work import VerificationOutcome, WorkContract


def _work_contract() -> WorkContract:
    return WorkContract(
        allowed_write_paths=(
            "src/bookmarks_api/main.py",
            "src/bookmarks_api/models.py",
            "src/bookmarks_api/store.py",
        ),
        verification_profile="python_workspace_pytest_v1",
        output_carrier="full_files",
        max_repair_turns=1,
    )


def test_preservation_state_payload_roundtrip_preserves_sorted_fact_sets() -> None:
    state = PreservationState(
        task_anchor="verified-work:python_workspace_pytest_v1:src/bookmarks_api/main.py",
        trusted_structure=TrustedStructure(
            checks=frozenset({"pytest", "parse"}),
            paths=frozenset({"src/bookmarks_api/main.py"}),
        ),
        falsified_structure=FalsifiedStructure(
            failure_class="test_failed",
            checks=frozenset({"pytest"}),
            failing_tests=frozenset({"tests/test_bookmarks_api.py::test_create_and_get_bookmark_by_id"}),
            blocked_message=None,
        ),
        lawful_repair_surface=frozenset({"src/bookmarks_api/main.py"}),
        intervention_budget=InterventionBudget(
            allowed_moves=frozenset({"repair"}),
            remaining_repairs=1,
        ),
    )

    payload = state.as_payload()
    restored = PreservationState.from_payload(payload)

    assert payload == {
        "task_anchor": "verified-work:python_workspace_pytest_v1:src/bookmarks_api/main.py",
        "trusted_structure": {
            "checks": ["parse", "pytest"],
            "paths": ["src/bookmarks_api/main.py"],
        },
        "falsified_structure": {
            "failure_class": "test_failed",
            "checks": ["pytest"],
            "failing_tests": [
                "tests/test_bookmarks_api.py::test_create_and_get_bookmark_by_id"
            ],
            "blocked_message": None,
        },
        "lawful_repair_surface": ["src/bookmarks_api/main.py"],
        "intervention_budget": {
            "allowed_moves": ["repair"],
            "remaining_repairs": 1,
        },
    }
    assert restored == state


def test_derive_preservation_state_for_clean_pass_sets_continue_and_trusted_structure() -> None:
    state = derive_preservation_state(
        None,
        _work_contract(),
        ("src/bookmarks_api/main.py", "src/bookmarks_api/models.py"),
        VerificationOutcome(
            status="passed",
            failure_class=None,
            parsed_paths=(
                "src/bookmarks_api/main.py",
                "src/bookmarks_api/models.py",
            ),
            import_smoke_ok=True,
            pytest_ok=True,
            pytest_exit_code=0,
            pytest_passed=11,
            pytest_failed=0,
        ),
        remaining_repairs=1,
    )

    assert state.task_anchor == (
        "verified-work:python_workspace_pytest_v1:"
        "src/bookmarks_api/main.py|src/bookmarks_api/models.py|src/bookmarks_api/store.py"
    )
    assert state.trusted_structure.checks == frozenset({"parse", "import_smoke", "pytest"})
    assert state.trusted_structure.paths == frozenset(
        {"src/bookmarks_api/main.py", "src/bookmarks_api/models.py"}
    )
    assert state.falsified_structure.failure_class is None
    assert state.lawful_repair_surface == frozenset()
    assert state.intervention_budget.allowed_moves == frozenset({"continue"})
    assert choose_preservation_move(state) == "continue"


def test_derive_preservation_state_for_import_failure_narrows_to_parsed_paths() -> None:
    state = derive_preservation_state(
        "goal-bookmarks-fix",
        _work_contract(),
        ("src/bookmarks_api/main.py",),
        VerificationOutcome(
            status="failed",
            failure_class="import_smoke_failed",
            parsed_paths=("src/bookmarks_api/main.py",),
            import_smoke_ok=False,
            import_smoke_excerpt="E   SyntaxError",
            first_failure_excerpt="E   SyntaxError",
        ),
        remaining_repairs=1,
    )

    assert state.task_anchor == "goal-bookmarks-fix"
    assert state.trusted_structure.checks == frozenset({"parse"})
    assert state.falsified_structure.checks == frozenset({"import_smoke"})
    assert state.lawful_repair_surface == frozenset({"src/bookmarks_api/main.py"})
    assert state.intervention_budget.allowed_moves == frozenset({"repair"})
    assert choose_preservation_move(state) == "repair"


def test_derive_preservation_state_for_pytest_failure_preserves_failing_tests_and_zero_budget_stops() -> None:
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
        remaining_repairs=0,
    )

    assert state.trusted_structure.checks == frozenset({"parse", "import_smoke"})
    assert state.falsified_structure.checks == frozenset({"pytest"})
    assert state.falsified_structure.failing_tests == frozenset(
        {"tests/test_bookmarks_api.py::test_create_and_get_bookmark_by_id"}
    )
    assert state.intervention_budget.allowed_moves == frozenset({"stop"})
    assert choose_preservation_move(state) == "stop"


@pytest.mark.parametrize(
    ("failure_class", "expected_move"),
    (
        ("blocked_missing_info", "check"),
        ("blocked_unsafe", "stop"),
    ),
)
def test_derive_preservation_state_for_blocked_outcomes_sets_non_repair_moves(
    failure_class: str,
    expected_move: str,
) -> None:
    state = derive_preservation_state(
        None,
        _work_contract(),
        (),
        VerificationOutcome(
            status="blocked",
            failure_class=failure_class,
            blocked_message="Need one more field.",
        ),
        remaining_repairs=1,
    )

    assert state.trusted_structure.checks == frozenset()
    assert state.falsified_structure.checks == frozenset({"blocked"})
    assert state.lawful_repair_surface == frozenset()
    assert choose_preservation_move(state) == expected_move


def test_derive_preservation_state_parse_invalid_without_paths_falls_back_to_allowed_surface() -> None:
    contract = _work_contract()
    state = derive_preservation_state(
        None,
        contract,
        (),
        VerificationOutcome(
            status="failed",
            failure_class="output_invalid",
            parse_error="missing end marker",
        ),
        remaining_repairs=1,
    )

    assert state.trusted_structure.checks == frozenset()
    assert state.falsified_structure.checks == frozenset({"parse"})
    assert state.lawful_repair_surface == frozenset(contract.allowed_write_paths)
    assert choose_preservation_move(state) == "repair"
