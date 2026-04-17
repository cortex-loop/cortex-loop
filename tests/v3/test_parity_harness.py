"""Behavior tests for the V2/V3 deterministic parity harness."""

from __future__ import annotations

from pathlib import Path

from lab.v3 import parity
from lab.v3.parity_oracle import broken_payload_for_task


_TASK_IDS = (
    "bookmarks_app_template",
    "project_template",
    "feature_flags_template",
)


def test_run_all_checks_can_report_full_match(monkeypatch) -> None:
    _install_matching_stubs(monkeypatch)

    rows = parity.run_all_checks()

    assert len(rows) == 15
    assert all(
        set(row) == {
            "axis",
            "task_id",
            "completion_source",
            "v2",
            "v3",
            "equal",
            "classification",
            "classification_reason",
            "divergence_keys",
            "diff_text",
        }
        for row in rows
    )
    assert all(row["equal"] for row in rows)
    assert all(row["classification"] == "identity" for row in rows)


def test_run_all_checks_localizes_repair_ticket_only_divergence(monkeypatch) -> None:
    _install_matching_stubs(monkeypatch)
    monkeypatch.setattr(
        parity,
        "v3_build_repair_ticket",
        lambda state: (
            "repair-ticket::divergent"
            if tuple(sorted(state.lawful_repair_surface)) == ("src/normalize_port.py",)
            else "repair-ticket"
        ),
    )

    rows = parity.run_all_checks()
    divergent_rows = [row for row in rows if not row["equal"]]

    assert divergent_rows == [
        {
            "axis": "repair_ticket",
            "task_id": "project_template",
            "completion_source": "shared",
            "v2": "repair-ticket",
            "v3": "repair-ticket::divergent",
            "equal": False,
            "classification": "cosmetic-canonical",
            "classification_reason": "repair-ticket text diverges from the canonical shared format",
            "divergence_keys": ["text"],
            "diff_text": "--- v2\n+++ v3\n@@ -1 +1 @@\n-repair-ticket\n+repair-ticket::divergent",
        }
    ]


def test_parity_harness_does_not_import_tests_modules() -> None:
    source = Path(parity.__file__).read_text(encoding="utf-8")

    assert "from tests." not in source
    assert "import tests." not in source
    assert "tests.product" not in source


def _install_matching_stubs(monkeypatch) -> None:
    broken_payloads = {broken_payload_for_task(task_id) for task_id in _TASK_IDS}

    monkeypatch.setattr(parity, "v2_build_instructions", lambda contract: "instructions")
    monkeypatch.setattr(parity, "v3_build_instructions", lambda contract: "instructions")
    monkeypatch.setattr(parity, "v2_build_input_text", lambda task_prompt, contract: f"input::{task_prompt}")
    monkeypatch.setattr(parity, "v3_build_input_text", lambda task_prompt, contract: f"input::{task_prompt}")
    monkeypatch.setattr(parity, "v2_build_repair_ticket", lambda state: "repair-ticket")
    monkeypatch.setattr(parity, "v3_build_repair_ticket", lambda state: "repair-ticket")

    def _v2_verify(result_text, work_contract):
        return None, _outcome(
            parity.V2VerificationOutcome,
            result_text in broken_payloads,
            work_contract.allowed_write_paths,
        )

    def _v3_verify(result_text, work_contract):
        return None, _outcome(
            parity.V3VerificationOutcome,
            result_text in broken_payloads,
            work_contract.allowed_write_paths,
        )

    monkeypatch.setattr(parity, "v2_verify", _v2_verify)
    monkeypatch.setattr(parity, "v3_verify", _v3_verify)


def _outcome(outcome_cls, is_broken: bool, parsed_paths: tuple[str, ...]):
    if is_broken:
        return outcome_cls(
            status="failed",
            failure_class="test_failed",
            parsed_paths=parsed_paths,
            import_smoke_ok=True,
            pytest_ok=False,
            pytest_exit_code=1,
            pytest_passed=2,
            pytest_failed=1,
            failing_tests=("tests/test_example.py::test_case",),
            first_failure_excerpt="FAILED tests/test_example.py::test_case",
        )
    return outcome_cls(
        status="passed",
        failure_class=None,
        parsed_paths=parsed_paths,
        import_smoke_ok=True,
        pytest_ok=True,
        pytest_exit_code=0,
        pytest_passed=3,
        pytest_failed=0,
        failing_tests=(),
    )
