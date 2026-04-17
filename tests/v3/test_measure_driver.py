"""Behavior tests for the V3 measurement driver."""

from __future__ import annotations

import json

from lab.v3 import measure
from lab.v3.replay import ReplayOutcome


def test_measure_driver_live_mode_marks_missing_keys_and_keeps_grid_order(
    monkeypatch,
    tmp_path,
) -> None:
    output_path = tmp_path / "measurement.json"

    def _fake_provider_has_key(provider: str) -> bool:
        return provider == "openai"

    def _fake_run_replay_case(adapter, task, *, arm: str) -> ReplayOutcome:
        return ReplayOutcome(
            task_id=task.task_id,
            provider=adapter.provider,
            model=task.request.model,
            arm=arm,
            attempt_count=1,
            decision="continue",
            verification_status="passed",
            failure_class=None,
            pytest_passed=3,
            pytest_failed=0,
            parsed_paths=task.request.work_contract.allowed_write_paths,
            duration_seconds=0.01,
            warnings=tuple(),
        )

    monkeypatch.setattr(measure, "_provider_has_key", _fake_provider_has_key)
    monkeypatch.setattr(measure, "run_replay_case", _fake_run_replay_case)

    exit_code = measure.main(
        [
            "--mode", "live",
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
    assert payload["config"] == {
        "mode": "live",
        "trials": 1,
        "providers": ["openai", "claude", "gemini"],
        "max_tokens": 4096,
    }
    assert len(payload["rows"]) == 18
    assert payload["rows"] == sorted(
        payload["rows"],
        key=lambda row: (row["provider"], row["task_id"], row["arm"], row["trial"]),
    )

    missing_rows = [row for row in payload["rows"] if row["error"] == "missing_api_key"]
    measured_rows = [row for row in payload["rows"] if row["error"] is None]

    assert len(missing_rows) == 12
    assert {row["provider"] for row in missing_rows} == {"claude", "gemini"}
    assert all(row["verification_status"] is None for row in missing_rows)

    assert len(measured_rows) == 6
    assert {row["provider"] for row in measured_rows} == {"openai"}
    assert all(row["verification_status"] == "passed" for row in measured_rows)
    assert all(row["decision"] == "continue" for row in measured_rows)


def test_measure_driver_fixture_mode_executes_passing_openai_grid(tmp_path) -> None:
    output_path = tmp_path / "measurement.json"

    exit_code = measure.main(
        [
            "--mode",
            "fixture",
            "--trials",
            "1",
            "--providers",
            "openai",
            "--output",
            str(output_path),
        ]
    )

    assert exit_code == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert len(payload["rows"]) == 6
    assert {row["provider"] for row in payload["rows"]} == {"openai"}
    assert {row["task_id"] for row in payload["rows"]} == {
        "bookmarks_app_template",
        "project_template",
        "feature_flags_template",
    }
    for row in payload["rows"]:
        assert row["verification_status"] == "passed"
        assert row["decision"] == "continue"
        assert row["attempt_count"] == 1
        assert row["pytest_failed"] == 0
        assert row["error"] is None
