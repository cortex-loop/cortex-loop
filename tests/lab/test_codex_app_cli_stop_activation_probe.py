"""Lab locks for the Codex App/CLI Stop activation Gate 0 harness."""

from __future__ import annotations

import inspect
import json
from pathlib import Path

from lab import codex_app_cli_stop_activation_probe
from lab.codex_app_cli_stop_activation_probe import (
    EXPECTED_OVERDUE_VERIFICATION_TEXT,
    LIVE_APPROVAL_ENV,
    run_gate0_probe,
    run_live_canary_probe,
)


def test_gate0_probe_passes_with_isolated_product_subject_config(tmp_path: Path) -> None:
    root_config = Path(".codex/config.toml")
    root_config_before = root_config.read_text(encoding="utf-8")

    report = run_gate0_probe(output_root=tmp_path)

    assert report["passed"] is True
    assert report["live_canary_ran"] is False
    assert report["boundary_results"] == {
        "actuator_stimulus_not_perception_evidence": True,
        "root_config_unchanged": True,
        "subject_config_product_hook_only": True,
    }
    assert root_config.read_text(encoding="utf-8") == root_config_before
    subject_config = Path(str(report["subject_config_path"])).read_text(encoding="utf-8")
    assert "codex_app_cli_hook_client" in subject_config
    assert "cortex_mission_reflection_stop_hook" not in subject_config
    assert subject_config.count("[[hooks.Stop.hooks]]") == 1


def test_gate0_trajectory_records_required_diagnostics(tmp_path: Path) -> None:
    report = run_gate0_probe(output_root=tmp_path)
    rows = [
        json.loads(line)
        for line in Path(str(report["trajectory_path"]))
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    by_case = {row["case_id"]: row for row in rows}

    assert set(by_case) == {
        "normal_stop_blocks",
        "title_stop_stays_silent",
        "stop_hook_active_stays_silent",
        "non_stop_allows",
        "missing_snapshot_fails_open",
        "malformed_input_fails_open",
    }
    normal = by_case["normal_stop_blocks"]
    assert normal["payload"]
    assert normal["coordinator_diagnostics"]
    assert normal["runtime_snapshot_hash"] == report["runtime_snapshot_hash"]
    assert normal["stdout_payload"] == {
        "decision": "block",
        "reason": EXPECTED_OVERDUE_VERIFICATION_TEXT,
    }
    assert normal["actual_rendered_text_hash"]
    assert normal["stdout_payload_hash"]
    assert normal["silence_reason"] is None
    assert by_case["title_stop_stays_silent"]["silence_reason"] == (
        "non_assistant_lifecycle_event"
    )
    assert by_case["stop_hook_active_stays_silent"]["silence_reason"] == (
        "stop_hook_active"
    )
    assert by_case["missing_snapshot_fails_open"]["fail_open"] is True
    assert by_case["malformed_input_fails_open"]["fail_open"] is True


def test_live_canary_refuses_without_explicit_approval(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.delenv(LIVE_APPROVAL_ENV, raising=False)

    report = run_live_canary_probe(output_root=tmp_path)

    assert report["passed"] is False
    assert report["live_canary_ran"] is False
    assert report["blocked_reason"] == "live_canary_requires_explicit_current_turn_approval"


def test_activation_harness_does_not_read_fixed_prompt_fixtures() -> None:
    source = inspect.getsource(codex_app_cli_stop_activation_probe)

    forbidden = (
        "truth_gap_recheck_operator",
        "verification_debt_continuation_operator",
        "fixtures/live_validation/prompts",
        "cortex_mission_reflection_stop_hook",
    )
    for fragment in forbidden:
        assert fragment not in source
