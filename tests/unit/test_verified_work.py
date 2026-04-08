"""Focused tests for the shared verified-work law."""

from __future__ import annotations

import pytest

from cortex.sre.verified_work import (
    VerificationOutcome,
    WorkContract,
    choose_verified_work_followup,
)


def _work_contract(max_repair_turns: int = 1) -> WorkContract:
    return WorkContract(
        allowed_write_paths=(
            "src/bookmarks_api/main.py",
            "src/bookmarks_api/models.py",
            "src/bookmarks_api/store.py",
        ),
        verification_profile="python_workspace_pytest_v1",
        output_carrier="full_files",
        max_repair_turns=max_repair_turns,
    )


def test_work_contract_accepts_only_first_train_shape() -> None:
    contract = _work_contract()

    assert contract.as_payload() == {
        "allowed_write_paths": [
            "src/bookmarks_api/main.py",
            "src/bookmarks_api/models.py",
            "src/bookmarks_api/store.py",
        ],
        "verification_profile": "python_workspace_pytest_v1",
        "output_carrier": "full_files",
        "max_repair_turns": 1,
    }

    second_contract = WorkContract(
        allowed_write_paths=("src/normalize_port.py",),
        verification_profile="python_workspace_pytest_port_fix_v1",
        output_carrier="full_files",
        max_repair_turns=1,
    )

    assert second_contract.as_payload() == {
        "allowed_write_paths": ["src/normalize_port.py"],
        "verification_profile": "python_workspace_pytest_port_fix_v1",
        "output_carrier": "full_files",
        "max_repair_turns": 1,
    }


def test_work_contract_rejects_duplicate_or_unbounded_paths() -> None:
    with pytest.raises(ValueError, match="duplicates"):
        WorkContract(
            allowed_write_paths=("src/bookmarks_api/main.py", "src/bookmarks_api/main.py"),
            verification_profile="python_workspace_pytest_v1",
            output_carrier="full_files",
            max_repair_turns=1,
        )

    with pytest.raises(ValueError, match="bounded relative paths"):
        WorkContract(
            allowed_write_paths=("../escape.py",),
            verification_profile="python_workspace_pytest_v1",
            output_carrier="full_files",
            max_repair_turns=1,
        )


def test_choose_verified_work_followup_matches_exact_first_train_law() -> None:
    contract = _work_contract()

    assert choose_verified_work_followup(contract, None, remaining_repairs=1) == "continue"
    assert (
        choose_verified_work_followup(
            contract,
            VerificationOutcome(status="passed", failure_class=None),
            remaining_repairs=1,
        )
        == "continue"
    )
    assert (
        choose_verified_work_followup(
            contract,
            VerificationOutcome(status="failed", failure_class="output_invalid"),
            remaining_repairs=1,
        )
        == "repair"
    )
    assert (
        choose_verified_work_followup(
            contract,
            VerificationOutcome(status="failed", failure_class="test_failed"),
            remaining_repairs=0,
        )
        == "stop"
    )
    assert (
        choose_verified_work_followup(
            contract,
            VerificationOutcome(
                status="blocked",
                failure_class="blocked_missing_info",
                blocked_message="Need one more field.",
            ),
            remaining_repairs=1,
        )
        == "check"
    )
    assert (
        choose_verified_work_followup(
            contract,
            VerificationOutcome(
                status="blocked",
                failure_class="blocked_unsafe",
                blocked_message="Unsafe request.",
            ),
            remaining_repairs=1,
        )
        == "stop"
    )


def test_verification_outcome_rejects_incoherent_status_and_failure_class() -> None:
    with pytest.raises(ValueError, match="must be None when status is `passed`"):
        VerificationOutcome(status="passed", failure_class="output_invalid")

    with pytest.raises(ValueError, match="must be present when status is not `passed`"):
        VerificationOutcome(status="failed", failure_class=None)
