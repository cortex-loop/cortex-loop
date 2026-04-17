"""Fixture-mode behavior test for the V3 measurement driver."""

from __future__ import annotations

import json

from lab.v3.measure import main


def test_measure_driver_fixture_mode_writes_full_grid(tmp_path) -> None:
    output_path = tmp_path / "measurement.json"

    exit_code = main(
        [
            "--mode",
            "fixture",
            "--trials",
            "1",
            "--providers",
            "openai,claude,gemini",
            "--output",
            str(output_path),
        ]
    )

    assert exit_code == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert set(payload) == {"started_at", "completed_at", "config", "rows"}
    assert len(payload["rows"]) == 18
    for row in payload["rows"]:
        assert set(row) == {
            "provider",
            "task_id",
            "arm",
            "trial",
            "verification_status",
            "failure_class",
            "pytest_passed",
            "pytest_failed",
            "attempt_count",
            "decision",
            "duration_seconds",
            "model",
            "cost_usd",
            "error",
        }
        assert row["verification_status"] in {"passed", "failed", "blocked"}
