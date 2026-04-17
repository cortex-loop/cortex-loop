"""Behavior tests for the V2/V3 deterministic parity harness."""

from __future__ import annotations

from lab.v3 import parity


def test_run_all_checks_reports_expected_rows_with_matching_verification(monkeypatch) -> None:
    def _same_v2_verify(result_text, work_contract):
        del result_text, work_contract
        return None, parity.V2VerificationOutcome(
            status="passed",
            failure_class=None,
            parsed_paths=("src/example.py",),
            import_smoke_ok=True,
            pytest_ok=True,
            pytest_passed=3,
            pytest_failed=0,
            failing_tests=(),
        )

    def _same_v3_verify(result_text, work_contract):
        del result_text, work_contract
        return None, parity.V3VerificationOutcome(
            status="passed",
            failure_class=None,
            parsed_paths=("src/example.py",),
            import_smoke_ok=True,
            pytest_ok=True,
            pytest_passed=3,
            pytest_failed=0,
            failing_tests=(),
        )

    monkeypatch.setattr(parity, "v2_verify", _same_v2_verify)
    monkeypatch.setattr(parity, "v3_verify", _same_v3_verify)

    rows = parity.run_all_checks()

    assert len(rows) == 15
    for row in rows:
        assert set(row) == {
            "axis",
            "task_id",
            "completion_source",
            "v2",
            "v3",
            "equal",
            "divergence_keys",
            "diff_text",
        }
    verification_rows = [row for row in rows if row["axis"] == "verification"]
    assert len(verification_rows) == 6
    assert all(row["equal"] for row in verification_rows)
    assert all(row["divergence_keys"] == [] for row in verification_rows)


def test_run_all_checks_reports_named_verification_divergence(monkeypatch) -> None:
    def _same_v2_verify(result_text, work_contract):
        del result_text, work_contract
        return None, parity.V2VerificationOutcome(
            status="passed",
            failure_class=None,
            parsed_paths=("src/example.py",),
            import_smoke_ok=True,
            pytest_ok=True,
            pytest_passed=3,
            pytest_failed=0,
            failing_tests=(),
        )

    def _different_v3_verify(result_text, work_contract):
        del result_text, work_contract
        return None, parity.V3VerificationOutcome(
            status="failed",
            failure_class="test_failed",
            parsed_paths=("src/example.py",),
            import_smoke_ok=True,
            pytest_ok=False,
            pytest_passed=2,
            pytest_failed=1,
            failing_tests=("tests/test_example.py::test_case",),
        )

    monkeypatch.setattr(parity, "v2_verify", _same_v2_verify)
    monkeypatch.setattr(parity, "v3_verify", _different_v3_verify)

    rows = parity.run_all_checks()
    divergent_verification_rows = [row for row in rows if row["axis"] == "verification" and not row["equal"]]

    assert divergent_verification_rows
    assert all("status" in row["divergence_keys"] for row in divergent_verification_rows)
