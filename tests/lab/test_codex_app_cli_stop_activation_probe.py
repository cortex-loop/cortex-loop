"""Lab locks for the Codex App/CLI Stop activation Gate 0 harness."""

from __future__ import annotations

import inspect
import json
from pathlib import Path

from lab import codex_app_cli_stop_activation_probe
from lab.codex_app_cli_stop_activation_probe import (
    EXPECTED_OVERDUE_VERIFICATION_TEXT,
    LIVE_APPROVAL_ENV,
    PRODUCT_EVENT_CAPTURE_APPROVAL_ENV,
    PRODUCT_EVENT_CAPTURE_HOOK_EVENTS,
    PRODUCT_EVENT_CAPTURE_LIVE_PROMPT,
    PRODUCT_EVENT_CAPTURE_OUTPUT_ROOT,
    PRODUCT_PERCEPTION_LIVE_APPROVAL_ENV,
    PRODUCT_PERCEPTION_LIVE_OUTPUT_ROOT,
    PRODUCT_PERCEPTION_LIVE_PROMPT,
    STOP_CONTINUATION_RESOLUTION_APPROVAL_ENV,
    STOP_CONTINUATION_RESOLUTION_HOOK_EVENTS,
    STOP_CONTINUATION_RESOLUTION_LIVE_PROMPT,
    STOP_CONTINUATION_RESOLUTION_OUTPUT_ROOT,
    run_gate0_probe,
    run_live_canary_probe,
    run_product_event_capture_live_probe,
    run_product_perception_gate0_probe,
    run_product_perception_live_probe,
    run_stop_continuation_resolution_gate0_probe,
    run_stop_continuation_resolution_live_probe,
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


def test_product_perception_live_refuses_without_explicit_approval(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.delenv(PRODUCT_PERCEPTION_LIVE_APPROVAL_ENV, raising=False)

    report = run_product_perception_live_probe(output_root=tmp_path)

    assert report["passed"] is False
    assert report["live_probe_ran"] is False
    assert report["verdict"] == "not_run"
    assert report["blocked_reason"] == (
        "product_perception_live_requires_explicit_current_turn_approval"
    )
    assert report["approval_env"] == PRODUCT_PERCEPTION_LIVE_APPROVAL_ENV


def test_product_event_capture_live_refuses_without_explicit_approval(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.delenv(PRODUCT_EVENT_CAPTURE_APPROVAL_ENV, raising=False)

    report = run_product_event_capture_live_probe(output_root=tmp_path)

    assert report["passed"] is False
    assert report["live_probe_ran"] is False
    assert report["verdict"] == "not_run"
    assert report["blocked_reason"] == (
        "product_event_capture_live_requires_explicit_current_turn_approval"
    )
    assert report["approval_env"] == PRODUCT_EVENT_CAPTURE_APPROVAL_ENV


def test_stop_continuation_resolution_live_refuses_without_explicit_approval(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.delenv(STOP_CONTINUATION_RESOLUTION_APPROVAL_ENV, raising=False)

    report = run_stop_continuation_resolution_live_probe(output_root=tmp_path)

    assert report["passed"] is False
    assert report["live_probe_ran"] is False
    assert report["verdict"] == "not_run"
    assert report["blocked_reason"] == (
        "stop_continuation_resolution_live_requires_explicit_current_turn_approval"
    )
    assert report["approval_env"] == STOP_CONTINUATION_RESOLUTION_APPROVAL_ENV


def test_product_perception_gate0_derives_state_without_snapshot_fixture(
    tmp_path: Path,
) -> None:
    root_config = Path(".codex/config.toml")
    root_config_before = root_config.read_text(encoding="utf-8")

    report = run_product_perception_gate0_probe(output_root=tmp_path)

    assert report["passed"] is True
    assert report["boundary_results"] == {
        "root_config_unchanged": True,
        "subject_config_product_hook_only": True,
        "no_runtime_snapshot_fixture": True,
    }
    assert report["case_results"] == {
        "product_prompt_then_closure_blocks": True,
        "observed_check_then_closure_stays_silent": True,
        "waiting_response_stays_silent": True,
    }
    assert root_config.read_text(encoding="utf-8") == root_config_before
    rows = [
        json.loads(line)
        for line in Path(str(report["trajectory_path"]))
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    aggregate = {
        row["case_id"]: row
        for row in rows
        if row["case_id"] in report["case_results"]
    }
    assert aggregate["product_prompt_then_closure_blocks"]["final_stdout_payload"] == {
        "decision": "block",
        "reason": EXPECTED_OVERDUE_VERIFICATION_TEXT,
    }
    assert aggregate["product_prompt_then_closure_blocks"][
        "product_perception_without_runtime_snapshot"
    ] is True


def test_stop_continuation_resolution_gate0_distinguishes_resolution_states(
    tmp_path: Path,
) -> None:
    report = run_stop_continuation_resolution_gate0_probe(output_root=tmp_path)

    assert report["passed"] is True
    assert report["case_results"] == {
        "continuation_check_resolves": True,
        "continuation_unrelated_preserves_open": True,
        "continuation_narrowing_resolves": True,
        "continuation_blocker_resolves": True,
    }
    assert report["boundary_results"] == {
        "root_config_unchanged": True,
        "subject_config_product_hook_only": True,
        "subject_config_omits_runtime_snapshot": True,
        "no_runtime_snapshot_fixture": True,
        "non_stop_steps_emit_no_stdout": True,
    }


def test_stop_continuation_resolution_gate0_records_expectation_state(
    tmp_path: Path,
) -> None:
    report = run_stop_continuation_resolution_gate0_probe(output_root=tmp_path)
    rows = [
        json.loads(line)
        for line in Path(str(report["trajectory_path"]))
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    sequence_rows = {row["case_id"]: row for row in rows if "steps" in row}

    resolved = sequence_rows["continuation_check_resolves"]
    preserved = sequence_rows["continuation_unrelated_preserves_open"]

    assert resolved["first_stdout_payload"] == {
        "decision": "block",
        "reason": EXPECTED_OVERDUE_VERIFICATION_TEXT,
    }
    assert resolved["final_silence_reason"] == "pressure_below_visible_threshold"
    assert resolved["final_active_expectation_ids"] == []
    assert resolved["final_resolved_expectation_ids"]
    assert resolved["final_expectation_evidence_refs"]
    assert preserved["final_silence_reason"] == (
        "stop_hook_active_unresolved_verification_expectation"
    )
    assert preserved["final_active_expectation_ids"]
    assert preserved["final_resolved_expectation_ids"] == []


def test_product_perception_live_uses_separate_no_snapshot_output_root() -> None:
    selected_root = codex_app_cli_stop_activation_probe._selected_output_root(
        SimpleArgs(
            output_root=None,
            product_perception_live=True,
        )
    )

    assert selected_root == PRODUCT_PERCEPTION_LIVE_OUTPUT_ROOT
    assert "codex_app_cli_product_perception_live_probe" in str(selected_root)


def test_product_event_capture_live_uses_separate_output_root() -> None:
    selected_root = codex_app_cli_stop_activation_probe._selected_output_root(
        SimpleArgs(
            output_root=None,
            product_perception_live=False,
            product_event_capture_live=True,
        )
    )

    assert selected_root == PRODUCT_EVENT_CAPTURE_OUTPUT_ROOT
    assert "codex_app_cli_product_event_capture_remediation" in str(selected_root)


def test_stop_continuation_resolution_uses_separate_output_root() -> None:
    selected_root = codex_app_cli_stop_activation_probe._selected_output_root(
        SimpleArgs(
            output_root=None,
            product_perception_live=False,
            stop_continuation_resolution_live=True,
        )
    )

    assert selected_root == STOP_CONTINUATION_RESOLUTION_OUTPUT_ROOT
    assert "codex_app_cli_stop_continuation_resolution_loop" in str(selected_root)


def test_product_perception_live_subject_config_omits_runtime_snapshot(
    tmp_path: Path,
) -> None:
    subject = tmp_path / "subject"
    config_path = codex_app_cli_stop_activation_probe._write_subject_hook_config(
        subject=subject,
        state_root=tmp_path / "state",
        snapshot_path=None,
        diagnostics_path=tmp_path / "diagnostics.jsonl",
    )
    config = config_path.read_text(encoding="utf-8")

    assert "codex_app_cli_hook_client" in config
    assert "--runtime-snapshot" not in config
    assert "cortex_mission_reflection_stop_hook" not in config
    assert config.count("[[hooks.Stop.hooks]]") == 1


def test_product_event_capture_subject_config_registers_all_product_hooks(
    tmp_path: Path,
) -> None:
    subject = tmp_path / "subject"
    config_path = codex_app_cli_stop_activation_probe._write_subject_hook_config(
        subject=subject,
        state_root=tmp_path / "state",
        snapshot_path=None,
        diagnostics_path=tmp_path / "diagnostics.jsonl",
        hook_events=PRODUCT_EVENT_CAPTURE_HOOK_EVENTS,
    )
    config = config_path.read_text(encoding="utf-8")

    assert "codex_app_cli_hook_client" in config
    assert "--runtime-snapshot" not in config
    assert "cortex_mission_reflection_stop_hook" not in config
    for event_name in PRODUCT_EVENT_CAPTURE_HOOK_EVENTS:
        assert config.count(f"[[hooks.{event_name}]]") == 1
        assert config.count(f"[[hooks.{event_name}.hooks]]") == 1
    assert "[[hooks.PermissionRequest]]" not in config
    assert "[[hooks.PostToolUseFailure]]" not in config


def test_stop_continuation_resolution_subject_config_registers_all_product_hooks(
    tmp_path: Path,
) -> None:
    subject = tmp_path / "subject"
    config_path = codex_app_cli_stop_activation_probe._write_subject_hook_config(
        subject=subject,
        state_root=tmp_path / "state",
        snapshot_path=None,
        diagnostics_path=tmp_path / "diagnostics.jsonl",
        hook_events=STOP_CONTINUATION_RESOLUTION_HOOK_EVENTS,
    )
    config = config_path.read_text(encoding="utf-8")

    assert "codex_app_cli_hook_client" in config
    assert "--runtime-snapshot" not in config
    assert "cortex_mission_reflection_stop_hook" not in config
    for event_name in STOP_CONTINUATION_RESOLUTION_HOOK_EVENTS:
        assert config.count(f"[[hooks.{event_name}]]") == 1
        assert config.count(f"[[hooks.{event_name}.hooks]]") == 1
    assert "[[hooks.PermissionRequest]]" not in config
    assert "[[hooks.PostToolUseFailure]]" not in config


def test_subject_config_can_disable_model_visible_blocks_for_silent_arm(
    tmp_path: Path,
) -> None:
    subject = tmp_path / "subject"
    config_path = codex_app_cli_stop_activation_probe._write_subject_hook_config(
        subject=subject,
        state_root=tmp_path / "state",
        snapshot_path=None,
        diagnostics_path=tmp_path / "diagnostics.jsonl",
        hook_events=PRODUCT_EVENT_CAPTURE_HOOK_EVENTS,
        disable_model_visible_blocks=True,
    )
    config = config_path.read_text(encoding="utf-8")

    assert "--disable-model-visible-blocks" in config
    assert "--runtime-snapshot" not in config
    assert "cortex_mission_reflection_stop_hook" not in config


def test_live_subject_workspace_is_prepared_as_isolated_git_root(
    tmp_path: Path,
) -> None:
    subject = tmp_path / "subject"
    subject.mkdir()

    codex_app_cli_stop_activation_probe._prepare_isolated_subject_workspace(subject)

    assert codex_app_cli_stop_activation_probe._git_root(subject) == subject.resolve()


def test_live_trajectory_rows_record_no_snapshot_product_state() -> None:
    row = {
        "runtime_snapshot_loaded": False,
        "runtime_snapshot_hash": None,
        "actual_rendered_text_hash": "hash-1",
        "stdout_payload": {
            "decision": "block",
            "reason": EXPECTED_OVERDUE_VERIFICATION_TEXT,
        },
        "coordinator": {
            "hook_payload": {
                "hook_event_name": "Stop",
                "stop_hook_active": False,
                "has_transcript_backed_assistant_turn": True,
            },
            "session_state": {
                "verification_evidence_count": 0,
                "closure_claim_count": 1,
            },
            "grounded_intervention": {
                "selection_trace": {
                    "perception_source": "product_runtime_expectation",
                }
            },
            "directive": {
                "action": "block_with_identity_continuous_text",
                "silence_reason": None,
            },
        },
    }

    trajectory = codex_app_cli_stop_activation_probe._live_trajectory_rows([row])

    assert trajectory == [
        {
            "active_expectation_ids": [],
            "actual_rendered_text_hash": "hash-1",
            "model_visible_blocks_disabled": None,
            "suppressed_rendered_text_hash": None,
            "suppressed_stdout_payload": None,
            "directive_action": "block_with_identity_continuous_text",
            "expectation_evidence_refs": [],
            "fail_open": False,
            "has_transcript_backed_assistant_turn": True,
            "hook_event_name": "Stop",
            "raw_keys": None,
            "tool_name": None,
            "tool_input_present": None,
            "tool_response_present": None,
            "error_present": None,
            "prompt_text_hash": None,
            "perception_source": "product_runtime_expectation",
            "row_index": 1,
            "runtime_snapshot_hash": None,
            "runtime_snapshot_loaded": False,
            "resolved_expectation_ids": [],
            "selection_trace": {"perception_source": "product_runtime_expectation"},
            "session_state": {
                "closure_claim_count": 1,
                "verification_evidence_count": 0,
            },
            "session_state_hash": codex_app_cli_stop_activation_probe._stable_hash(
                {
                    "closure_claim_count": 1,
                    "verification_evidence_count": 0,
                }
            ),
            "silence_reason": None,
            "stdout_payload": {
                "decision": "block",
                "reason": EXPECTED_OVERDUE_VERIFICATION_TEXT,
            },
            "stdout_payload_hash": codex_app_cli_stop_activation_probe._stable_hash(
                {
                    "decision": "block",
                    "reason": EXPECTED_OVERDUE_VERIFICATION_TEXT,
                }
            ),
            "stop_hook_active": False,
        }
    ]


def test_activation_harness_does_not_read_fixed_prompt_fixtures() -> None:
    source = inspect.getsource(codex_app_cli_stop_activation_probe)

    forbidden = (
        "truth_gap_recheck_operator",
        "verification_debt_continuation_operator",
        "fixtures/live_validation/prompts",
        "cortex_mission_reflection_stop_hook",
        "visible_success_unverified",
        "hidden_quality_pass",
    )
    for fragment in forbidden:
        assert fragment not in source

    assert "PRODUCT_PERCEPTION_LIVE_PROMPT" in source
    assert "cortex_product_perception_live.txt" in PRODUCT_PERCEPTION_LIVE_PROMPT
    assert "PRODUCT_EVENT_CAPTURE_LIVE_PROMPT" in source
    assert (
        "cortex_product_event_capture_live.txt" in PRODUCT_EVENT_CAPTURE_LIVE_PROMPT
    )
    assert "STOP_CONTINUATION_RESOLUTION_LIVE_PROMPT" in source
    assert (
        "cortex_stop_continuation_resolution_live.txt"
        in STOP_CONTINUATION_RESOLUTION_LIVE_PROMPT
    )
    assert "--runtime-snapshot" in source  # legacy actuator canary remains explicit
    assert "snapshot_path=None" in source


class SimpleArgs:
    def __init__(
        self,
        *,
        output_root,
        product_perception_live,
        product_event_capture_live=False,
        stop_continuation_resolution_gate0=False,
        stop_continuation_resolution_live=False,
    ) -> None:
        self.output_root = output_root
        self.product_perception_live = product_perception_live
        self.product_event_capture_live = product_event_capture_live
        self.stop_continuation_resolution_gate0 = stop_continuation_resolution_gate0
        self.stop_continuation_resolution_live = stop_continuation_resolution_live
