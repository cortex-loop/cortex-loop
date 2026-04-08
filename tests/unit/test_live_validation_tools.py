"""Focused tests for the L2 live-testing support harness."""

from __future__ import annotations

import io
import os
import sys
import tempfile
from pathlib import Path
from contextlib import contextmanager
import json

import pytest

TOOLS_ROOT = Path(__file__).resolve().parents[2] / "tools"
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

import live_cortex_host_control as live_host_control
import live_compare as live_compare
import live_host_native_product_paths as live_host_native_product_paths
import live_hook_recorder as live_hook_recorder
import live_operator_directionality as live_operator_directionality
import live_operator_directionality_audit as live_operator_directionality_audit
import live_operator_route_state as live_operator_route_state
import live_preflight as live_preflight
import live_provider_baselines as live_provider_baselines
import live_validation_common as live_validation_common
from live_validation_common import (
    BLOCKING_FAILURE_CLASSES,
    GEMINI_AUTH_MODE_ENV,
    GEMINI_OPERATOR_FULL_LADDER,
    MODEL_MATRIX,
    automation_auth_readiness,
    build_scenario_catalog,
    choose_model,
    classify_failure,
    decide_verdict,
    extract_event_labels,
    extract_result_text,
    extract_token_usage,
    live_evidence_fields,
    model_ladder,
    parse_json_records,
    redact_claude_auth_payload,
    should_collapse_after_failure,
)


def test_redact_claude_auth_payload_omits_private_identity_fields() -> None:
    payload = {
        "loggedIn": True,
        "authMethod": "claude.ai",
        "apiProvider": "firstParty",
        "email": "private@example.com",
        "orgId": "org-123",
        "orgName": "private org",
        "subscriptionType": "pro",
    }

    redacted = redact_claude_auth_payload(payload)

    assert redacted == {
        "logged_in": True,
        "auth_method": "claude.ai",
        "api_provider": "firstParty",
        "subscription_type": "pro",
    }


def test_classify_failure_recognizes_live_auth_and_capacity_blockers() -> None:
    assert classify_failure("ANTHROPIC_API_KEY is required") == "auth_missing"
    assert (
        classify_failure(
            "When using Gemini API, you must specify the GEMINI_API_KEY environment variable."
        )
        == "auth_missing"
    )
    assert classify_failure("OAuth token has expired") == "auth_expired"
    assert (
        classify_failure("You have exhausted your capacity on this model.")
        == "capacity_exhausted"
    )
    assert classify_failure("You've hit your limit · resets 4pm (Asia/Tokyo)") == "quota_exhausted"
    assert classify_failure('Gemini interaction stream transport failed with HTTP 500: INTERNAL') == "provider_internal_error"
    assert classify_failure('{"error":{"code":500,"status":"INTERNAL","message":"internal error encountered"}}') == "provider_internal_error"
    assert classify_failure('{"code": -32600, "message": "no rollout found for thread id 123"}') == "continuity_rollout_missing"
    assert classify_failure("Requested entity was not found.") == "model_unavailable"
    assert classify_failure("model_not_found") == "model_unavailable"
    assert classify_failure("totally different error") is None


def test_live_evidence_fields_classify_watchlist_and_canonical_truth_lanes() -> None:
    assert live_evidence_fields(lane="operator") == {
        "execution_surface": "headless_cli",
        "evidence_role": "watchlist",
    }
    assert live_evidence_fields(lane="automation") == {
        "execution_surface": "direct_api",
        "evidence_role": "canonical_truth",
    }


def test_load_local_env_file_preserves_existing_env_values(tmp_path: Path, monkeypatch) -> None:
    env_path = tmp_path / ".env"
    env_path.write_text(
        "OPENAI_API_KEY=file-key\n"
        "export CORTEX_LIVE_SERVICE_SPEND_APPROVED=approved\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("OPENAI_API_KEY", "shell-key")
    monkeypatch.delenv("CORTEX_LIVE_SERVICE_SPEND_APPROVED", raising=False)

    loaded = live_validation_common.load_local_env_file(env_path)

    assert loaded["OPENAI_API_KEY"] == "shell-key"
    assert loaded["CORTEX_LIVE_SERVICE_SPEND_APPROVED"] == "approved"
    assert os.environ["OPENAI_API_KEY"] == "shell-key"
    assert os.environ["CORTEX_LIVE_SERVICE_SPEND_APPROVED"] == "approved"


def test_should_collapse_after_failure_matches_blocking_classes() -> None:
    for failure_class in BLOCKING_FAILURE_CLASSES:
        assert should_collapse_after_failure(failure_class) is True
    assert should_collapse_after_failure("runtime_error") is False
    assert should_collapse_after_failure(None) is False


def test_parse_json_records_extracts_jsonl_structured_records_only() -> None:
    text = '\n'.join(
        [
            '{"type":"init","session_id":"s-1"}',
            "not json",
            '{"type":"item.completed","item":{"type":"agent_message","text":"OK"}}',
        ]
    )

    records, extraction_mode = parse_json_records(text)

    assert records == [
        {"type": "init", "session_id": "s-1"},
        {"type": "item.completed", "item": {"type": "agent_message", "text": "OK"}},
    ]
    assert extraction_mode == "jsonl"
    assert extract_event_labels(records) == ["init", "item:agent_message"]
    assert extract_result_text(records, text) == "OK"


def test_parse_json_records_accepts_pretty_printed_single_object() -> None:
    text = json.dumps(
        {
            "session_id": "gm-1",
            "response": "=== FILE: src/bookmarks_api/main.py ===\napp = object()\n=== END FILE ===",
        },
        indent=2,
    )

    records, extraction_mode = parse_json_records(text)

    assert records == [
        {
            "session_id": "gm-1",
            "response": "=== FILE: src/bookmarks_api/main.py ===\napp = object()\n=== END FILE ===",
        }
    ]
    assert extraction_mode == "json_object"
    assert extract_result_text(records, text) == (
        "=== FILE: src/bookmarks_api/main.py ===\napp = object()\n=== END FILE ==="
    )


def test_parse_json_records_accepts_json_array_of_records() -> None:
    text = json.dumps(
        [
            {"type": "init", "session_id": "s-1"},
            {"type": "result", "result": "done"},
        ],
        indent=2,
    )

    records, extraction_mode = parse_json_records(text)

    assert records == [
        {"type": "init", "session_id": "s-1"},
        {"type": "result", "result": "done"},
    ]
    assert extraction_mode == "json_array"


def test_extract_result_text_reassembles_gemini_style_assistant_deltas() -> None:
    records = [
        {"type": "init", "session_id": "s-1"},
        {"type": "message", "role": "assistant", "content": "Task: **in", "delta": True},
        {"type": "message", "role": "assistant", "content": "complete**", "delta": True},
        {"type": "result", "status": "success"},
    ]

    assert extract_result_text(records, "") == "Task: **incomplete**"


def test_extract_result_text_does_not_fall_back_to_user_prompt_when_assistant_deltas_exist() -> None:
    records = [
        {"type": "message", "role": "user", "content": "Prompt text"},
        {"type": "message", "role": "assistant", "content": "Actual", "delta": True},
        {"type": "message", "role": "assistant", "content": " answer", "delta": True},
        {"type": "result", "status": "success"},
    ]

    assert extract_result_text(records, "") == "Actual answer"


def test_extract_token_usage_reads_gemini_result_stats() -> None:
    usage = extract_token_usage(
        "gemini",
        [
            {
                "type": "result",
                "stats": {
                    "input_tokens": 123,
                    "output_tokens": 45,
                    "cached": 67,
                },
            }
        ],
    )

    assert usage == {
        "token_usage_visible": True,
        "input_tokens": 123,
        "output_tokens": 45,
        "cache_tokens": 67,
    }


def test_extract_token_usage_reads_claude_message_usage() -> None:
    usage = extract_token_usage(
        "claude",
        [
            {
                "type": "assistant",
                "message": {
                    "usage": {
                        "input_tokens": 50,
                        "output_tokens": 10,
                        "cache_creation_input_tokens": 20,
                        "cache_read_input_tokens": 30,
                    }
                },
            }
        ],
    )

    assert usage == {
        "token_usage_visible": True,
        "input_tokens": 50,
        "output_tokens": 10,
        "cache_tokens": 50,
    }


def test_classify_truth_gap_accepts_inspection_only_unfixed_language() -> None:
    text = (
        "**Status:** Complete for the requested inspection.\n\n"
        "Bug found in src.\n\n"
        "I did not edit files and did not run tests, so the bug is not fixed or verified as resolved."
    )

    assert (
        live_validation_common.classify_truth_gap(
            text,
            test_passed=False,
            modified_files=[],
        )
        == "truthful_incomplete"
    )


def test_build_scenario_catalog_exposes_l2_harness_contract() -> None:
    catalog = build_scenario_catalog()

    assert catalog["artifact_root"] == ".cortex/live_validation"
    assert catalog["shared_template_root"] == "tests/fixtures/live_validation/project_template"
    assert catalog["test_command"] == "python -m pytest -q tests/test_normalize_port.py"
    assert any(
        row["scenario_id"] == "pass_minimal"
        for row in catalog["operator_scenarios"]
    )
    assert any(
        row["scenario_id"] == "truth_gap"
        for row in catalog["operator_scenarios"]
    )
    assert any(
        row["scenario_id"] == "restart_continuity"
        for row in catalog["operator_scenarios"]
    )
    truth_gap_row = next(
        row for row in catalog["operator_scenarios"] if row["scenario_id"] == "truth_gap"
    )
    continuity_row = next(
        row
        for row in catalog["operator_scenarios"]
        if row["scenario_id"] == "restart_continuity"
    )
    assert truth_gap_row["automation_prompt"] == "truth_gap_automation.md"
    assert continuity_row["operator_prompt"] == "restart_continuity_turn2_operator.md"
    assert continuity_row["automation_prompt"] == "restart_continuity_turn2_automation.md"
    assert catalog["operator_continuity"]["turn_1_prompt"] == "restart_continuity_turn1_operator.md"
    assert catalog["automation_continuity"]["turn_1_prompt"] == "restart_continuity_turn1_automation.md"
    assert catalog["automation_continuity"]["turn_2_prompt"] == "restart_continuity_turn2_automation.md"
    assert catalog["automation_service_suites"]["current"]["scenarios"] == [
        "service_smoke",
        "service_restart_continuity",
    ]
    assert catalog["automation_service_suites"]["canonical_anchor"]["provider_scope"] == [
        "openai",
    ]
    assert catalog["host_caveats"]["claude"] == "host_caveat_operator_claude.md"
    assert catalog["host_caveats"]["openai"] == "host_caveat_operator_openai_app_server.md"
    assert catalog["openai_operator_surfaces"]["smoke"] == "codex exec"
    assert catalog["openai_operator_surfaces"]["lifecycle_proof"] == "codex app-server"
    assert catalog["gemini_operator_model_ladder"] == ["auto"]
    assert MODEL_MATRIX["openai"]["operator"].preferred == "gpt-5.3-codex"
    assert MODEL_MATRIX["gemini"]["operator"].preferred == "auto"
    assert MODEL_MATRIX["gemini"]["operator"].fallback is None


def test_openai_automation_service_model_split_uses_mini_for_smoke_only() -> None:
    assert live_host_control._service_model_for_scenario("openai", "service_smoke") == "gpt-5.4-mini"
    assert (
        live_host_control._service_model_for_scenario("openai", "service_restart_continuity")
        == MODEL_MATRIX["openai"]["automation"].preferred
    )
    assert (
        live_host_control._service_model_for_scenario("openai", "pass_minimal")
        == MODEL_MATRIX["openai"]["automation"].preferred
    )
    assert (
        live_host_control._service_model_for_scenario("claude", "service_smoke")
        == MODEL_MATRIX["claude"]["automation"].preferred
    )


def test_gemini_model_ladder_and_choose_model_stay_auto_only() -> None:
    assert model_ladder("gemini", "operator") == GEMINI_OPERATOR_FULL_LADDER
    assert model_ladder("gemini", "operator", auto_supported=False) == ("auto",)
    assert choose_model("gemini", "operator") == "auto"
    assert choose_model("gemini", "operator", auto_supported=False) == "auto"
    assert (
        choose_model(
            "gemini",
            "operator",
            current_model="auto",
            first_failure="model_unavailable",
            auto_supported=False,
        )
        == "auto"
    )
    assert (
        choose_model(
            "gemini",
            "operator",
            current_model="auto",
            first_failure="operator_timeout",
            auto_supported=False,
        )
        == "auto"
    )
    assert (
        choose_model(
            "gemini",
            "operator",
            current_model="auto",
            first_failure="capacity_exhausted",
            auto_supported=False,
        )
        == "auto"
    )


def test_claude_turn_budget_is_scenario_specific() -> None:
    assert live_host_native_product_paths._claude_max_turns("truth_gap") == 2
    assert live_host_native_product_paths._claude_max_turns("pass_minimal") == 3
    assert live_host_native_product_paths._claude_max_turns("restart_continuity") == 2
    assert live_host_native_product_paths._claude_max_turns(
        "restart_continuity",
        resume_session="session-1",
    ) == 3


def test_live_operator_route_state_uses_exact_scenario_defaults() -> None:
    execute_state = live_operator_route_state.build_operator_task_state("pass_minimal")
    inspect_state = live_operator_route_state.build_operator_task_state("truth_gap")
    continuity_state = live_operator_route_state.build_operator_task_state("restart_continuity")

    assert execute_state.task_mode.value == "execute"
    assert execute_state.complexity == pytest.approx(0.45)
    assert execute_state.continuity_demand == pytest.approx(0.05)
    assert execute_state.verification_demand == pytest.approx(0.80)
    assert execute_state.visible_burden_sensitivity == pytest.approx(0.45)

    assert inspect_state.task_mode.value == "inspect"
    assert inspect_state.complexity == pytest.approx(0.20)
    assert inspect_state.verification_demand == pytest.approx(0.00)
    assert inspect_state.visible_burden_sensitivity == pytest.approx(0.80)

    assert continuity_state.task_mode.value == "resume_execute"
    assert continuity_state.continuity_demand == pytest.approx(0.95)
    assert continuity_state.verification_demand == pytest.approx(0.80)


def test_live_operator_route_state_applies_uncertainty_and_pressure_rules() -> None:
    calm = live_operator_route_state.build_operator_task_state(
        "pass_minimal",
        recent_baseline_clean_count=2,
    )
    warning = live_operator_route_state.build_operator_task_state(
        "pass_minimal",
        recent_warning_bearing_success_present=True,
    )
    blocked = live_operator_route_state.build_operator_task_state(
        "pass_minimal",
        recent_probe_failure_class="quota_exhausted",
    )
    failed_before_completion = live_operator_route_state.build_operator_task_state(
        "pass_minimal",
        previous_same_host_run_failed_before_completion=True,
        recent_baseline_clean_count=2,
    )

    assert calm.host_friction == pytest.approx(0.0)
    assert calm.quota_pressure == pytest.approx(0.0)
    assert warning.host_friction == pytest.approx(0.55)
    assert warning.quota_pressure == pytest.approx(0.60)
    assert blocked.host_friction == pytest.approx(0.85)
    assert blocked.quota_pressure == pytest.approx(0.90)
    assert failed_before_completion.uncertainty == pytest.approx(0.65)


def test_live_operator_route_state_builds_summary_inputs_from_observable_signals() -> None:
    state = live_operator_route_state.build_operator_task_state(
        "truth_gap",
        previous_same_host_run_failed_before_completion=True,
        recent_baseline_clean_count=2,
    )

    inputs = live_operator_route_state.build_operator_summary_inputs(
        state,
        previous_same_host_run_failed_before_completion=True,
        recent_probe_failure_class=None,
        recent_product_failure_class="runtime_error",
        recent_warning_bearing_success_present=False,
        verification_required=False,
    )

    assert inputs.uncertainty == pytest.approx(0.65)
    assert inputs.previous_same_host_run_failed_before_completion is True
    assert inputs.recent_product_failure_class == "runtime_error"
    assert inputs.quota_pressure == pytest.approx(0.0)
    assert inputs.continuity_demand == pytest.approx(0.0)
    assert inputs.verification_required is False


def test_gemini_operator_auth_mode_uses_api_key_when_selected_in_settings(tmp_path, monkeypatch) -> None:
    fake_home = tmp_path / "home"
    settings_path = fake_home / ".gemini" / "settings.json"
    settings_path.parent.mkdir(parents=True)
    settings_path.write_text(
        json.dumps({"security": {"auth": {"selectedType": "gemini-api-key"}}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(live_validation_common.Path, "home", lambda: fake_home)

    assert live_validation_common.resolve_auth_mode("gemini", "operator", env={}) == "api_key"


def test_gemini_operator_auth_mode_prefers_env_key_without_settings(monkeypatch) -> None:
    monkeypatch.setattr(
        live_validation_common.Path,
        "home",
        lambda: Path("/tmp/nonexistent-gemini-home"),
    )

    assert (
        live_validation_common.resolve_auth_mode(
            "gemini",
            "operator",
            env={"GEMINI_API_KEY": "test-key"},
        )
        == "api_key"
    )


def test_automation_auth_readiness_defaults_to_missing_without_machine_creds() -> None:
    env = {}
    assert automation_auth_readiness("claude", env)["status"] == "missing"
    assert automation_auth_readiness("gemini", env)["status"] == "missing"
    assert automation_auth_readiness("openai", env)["status"] == "missing"


def test_read_workstream_baseline_resolves_commit_from_branch_lookup(monkeypatch, tmp_path: Path) -> None:
    workstream = tmp_path / "workstream.md"
    workstream.write_text(
        "- Accepted baseline branch: `main`\n"
        "- Accepted baseline commit lookup: `git rev-parse HEAD` on clean synced `main`\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(live_validation_common, "WORKSTREAM_PATH", workstream)
    monkeypatch.setattr(
        live_validation_common,
        "run_command",
        lambda *args, **kwargs: {
            "command": ["git", "rev-parse", "main"],
            "exit_code": 0,
            "stdout": "deadbeef1234567890\n",
            "stderr": "",
            "started_at": "2026-03-29T00:00:00+00:00",
            "ended_at": "2026-03-29T00:00:00+00:00",
        },
    )

    assert live_validation_common.read_workstream_baseline() == (
        "main",
        "deadbeef1234567890",
    )


def test_automation_auth_readiness_blocks_api_key_lanes_without_spend_approval() -> None:
    assert (
        automation_auth_readiness("claude", {"ANTHROPIC_API_KEY": "test-key"})["status"]
        == "blocked_by_spend_policy"
    )
    assert (
        automation_auth_readiness("openai", {"OPENAI_API_KEY": "test-key"})["status"]
        == "blocked_by_spend_policy"
    )


def test_gemini_automation_auth_readiness_is_ready_with_vertex_adc_and_spend_approval(monkeypatch) -> None:
    monkeypatch.setattr(live_validation_common, "command_exists", lambda command: command == "gcloud")
    monkeypatch.setattr(
        live_validation_common,
        "run_command",
        lambda *args, **kwargs: {
            "command": ["gcloud", "auth", "application-default", "print-access-token"],
            "exit_code": 0,
            "stdout": "token\n",
            "stderr": "",
            "started_at": "2026-03-28T00:00:00+00:00",
            "ended_at": "2026-03-28T00:00:00+00:00",
        },
    )

    readiness = automation_auth_readiness(
        "gemini",
        {
            "GOOGLE_CLOUD_PROJECT": "project-a",
            "GOOGLE_CLOUD_LOCATION": "us-central1",
            "CORTEX_LIVE_SERVICE_SPEND_APPROVED": "1",
        },
    )

    assert readiness["auth_mode"] == "vertex_adc"
    assert readiness["vertex_adc_available"] is True
    assert readiness["status"] == "ready"


def test_gemini_automation_auth_readiness_can_be_blocked_by_spend_policy(monkeypatch) -> None:
    monkeypatch.setattr(live_validation_common, "command_exists", lambda command: command == "gcloud")
    monkeypatch.setattr(
        live_validation_common,
        "run_command",
        lambda *args, **kwargs: {
            "command": ["gcloud", "auth", "application-default", "print-access-token"],
            "exit_code": 0,
            "stdout": "token\n",
            "stderr": "",
            "started_at": "2026-03-28T00:00:00+00:00",
            "ended_at": "2026-03-28T00:00:00+00:00",
        },
    )

    readiness = automation_auth_readiness(
        "gemini",
        {
            "GOOGLE_CLOUD_PROJECT": "project-a",
            "GOOGLE_CLOUD_LOCATION": "us-central1",
        },
    )

    assert readiness["auth_mode"] == "vertex_adc"
    assert readiness["vertex_adc_available"] is True
    assert readiness["status"] == "blocked_by_spend_policy"


def test_gemini_automation_auth_readiness_can_be_mis_scoped(monkeypatch) -> None:
    monkeypatch.setattr(live_validation_common, "command_exists", lambda command: command == "gcloud")
    monkeypatch.setattr(
        live_validation_common,
        "run_command",
        lambda *args, **kwargs: {
            "command": ["gcloud", "auth", "application-default", "print-access-token"],
            "exit_code": 1,
            "stdout": "",
            "stderr": "no adc",
            "started_at": "2026-03-28T00:00:00+00:00",
            "ended_at": "2026-03-28T00:00:00+00:00",
        },
    )

    readiness = automation_auth_readiness(
        "gemini",
        {
            GEMINI_AUTH_MODE_ENV: "vertex_adc",
            "GEMINI_API_KEY": "test-key",
        },
    )

    assert readiness["auth_mode"] == "vertex_adc"
    assert readiness["vertex_adc_available"] is False
    assert readiness["api_key_present"] is True
    assert readiness["status"] == "mis_scoped"


def test_single_provider_service_summary_does_not_include_stale_other_providers() -> None:
    summary = live_host_control._build_summary(
        lane="automation",
        suite_id="current",
        provider_payloads={"claude": {"provider": "claude", "runs": []}},
    )

    assert summary["lane"] == "automation"
    assert summary["suite_id"] == "current"
    assert summary["execution_surface"] == "direct_api"
    assert summary["evidence_role"] == "canonical_truth"
    assert summary["providers"] == {"claude": {"provider": "claude", "runs": []}}


def test_provider_baseline_requested_model_ladder_uses_current_model_matrix() -> None:
    assert live_provider_baselines._requested_model_ladder(
        provider="openai",
        lane="operator",
        preferred_model_override=None,
        fallback_model_override=None,
        disable_auto_probe=False,
    ) == ("gpt-5.3-codex", "gpt-5.4")


def test_automation_provider_baseline_skips_when_auth_readiness_is_blocked(monkeypatch) -> None:
    monkeypatch.setattr(
        live_provider_baselines,
        "automation_auth_readiness",
        lambda provider: {
            "auth_mode": "api_key",
            "status": "blocked_by_spend_policy",
            "spend_approved": False,
            "api_key_present": True,
        },
    )
    monkeypatch.setattr(
        live_provider_baselines,
        "_run_provider_probe",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("probe should not run")),
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir) / ".cortex" / "live_validation" / "automation" / "claude" / "baselines"
        payload = live_provider_baselines._run_single_provider_baseline(
            provider="claude",
            lane="automation",
            repeat_index=1,
            provider_root_path=root,
            preferred_model_override=None,
            fallback_model_override=None,
            disable_auto_probe=False,
        )

    assert payload["failure_class"] == "blocked_by_spend_policy"
    assert payload["auth_readiness"]["status"] == "blocked_by_spend_policy"
    assert payload["success"] is False


def test_operator_provider_baseline_surfaces_route_diagnostics(monkeypatch) -> None:
    monkeypatch.setattr(
        live_provider_baselines,
        "recent_operator_probe_failure",
        lambda provider: None,
    )
    monkeypatch.setattr(
        live_provider_baselines,
        "_run_provider_probe",
        lambda *args, **kwargs: {
            "command": ["gemini", "-p", "Respond exactly with OK.", "-o", "stream-json", "--approval-mode", "yolo"],
            "exit_code": 0,
            "stdout": '{"type":"message","role":"assistant","content":"OK"}\n{"type":"result","status":"success"}',
            "stderr": "",
            "started_at": "2026-03-30T00:00:00+00:00",
            "ended_at": "2026-03-30T00:00:01+00:00",
        },
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        payload = live_provider_baselines._run_single_provider_baseline(
            provider="gemini",
            lane="operator",
            repeat_index=1,
            provider_root_path=Path(tmpdir),
            preferred_model_override=None,
            fallback_model_override=None,
            disable_auto_probe=False,
            prior_runs=(),
        )

    assert payload["route_profile"] == "inspect_light"
    assert payload["route_budget"]["max_turns"] == 1
    assert payload["route_budget"]["allow_extra_read_pass"] is True
    assert payload["route_budget"]["max_retries"] == 1
    assert payload["state_vector"] == [0.1, 0.0, 0.05, 0.35, 0.0, 0.0]
    assert payload["modulator_state"] == {
        "focus_gain": 0.045,
        "explore_gain": 0.3475,
        "stop_pressure": 0.0525,
        "update_pressure": 0.555,
    }
    assert payload["modulator_reason_tags"] == ["novelty_bias"]


def test_auto_supported_remains_true_for_gemini_quota_failures(monkeypatch) -> None:
    quota_result = {
        "command": ["gemini", "-p", "Respond exactly with OK.", "-o", "stream-json", "--approval-mode", "yolo"],
        "exit_code": 1,
        "stdout": "",
        "stderr": '{"type":"result","status":"error","error":{"message":"[API Error: You have exhausted your daily quota on this model.]"}}',
        "started_at": "2026-03-30T00:00:00+00:00",
        "ended_at": "2026-03-30T00:00:01+00:00",
    }

    monkeypatch.setattr(live_preflight, "_run_gemini_probe", lambda model: dict(quota_result))
    probe = live_preflight._probe_gemini_operator()
    assert probe["auto_supported"] is True

    monkeypatch.setattr(
        live_provider_baselines,
        "_run_provider_probe",
        lambda *args, **kwargs: dict(quota_result),
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        payload = live_provider_baselines._run_single_provider_baseline(
            provider="gemini",
            lane="operator",
            repeat_index=1,
            provider_root_path=Path(tmpdir),
            preferred_model_override=None,
            fallback_model_override=None,
            disable_auto_probe=False,
            prior_runs=(),
        )
    assert payload["auto_supported"] is True


def test_claude_directionality_command_uses_lower_turn_budget(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_timed_command(command, **kwargs):
        captured["command"] = command
        return {
            "command": command,
            "exit_code": 0,
            "stdout": "",
            "stderr": "",
            "started_at": "2026-03-30T00:00:00+00:00",
            "ended_at": "2026-03-30T00:00:00+00:00",
        }

    monkeypatch.setattr(live_host_native_product_paths, "_run_timed_command", fake_timed_command)

    live_operator_directionality._run_raw_claude_task(
        "Inspect only.",
        project_root=Path("/tmp"),
        model="claude-sonnet-4-6",
        auth_mode="claude_code",
        scenario_id="truth_gap",
    )

    assert "--max-turns" in captured["command"]
    max_turns_index = captured["command"].index("--max-turns")
    assert captured["command"][max_turns_index + 1] == "2"


def test_claude_hook_capture_drops_stop_hook(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()

    live_host_native_product_paths._configure_hook_capture(
        provider="claude",
        project_root=project_root,
        scenario_id="pass_minimal",
        repeat_index=1,
        log_root=tmp_path,
    )

    settings = json.loads((project_root / ".claude" / "settings.json").read_text())
    assert "Stop" not in settings["hooks"]


def test_gemini_hook_capture_skips_project_settings_for_minimal(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()

    hook_log_path = live_host_native_product_paths._configure_hook_capture(
        provider="gemini",
        project_root=project_root,
        scenario_id="pass_minimal",
        repeat_index=1,
        execution_flavor="minimal",
        log_root=tmp_path,
    )

    assert hook_log_path is None
    assert not (project_root / ".gemini" / "settings.json").exists()


def test_gemini_task_omits_hook_env_for_minimal_execution(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_timed_command(command, **kwargs):
        captured["env"] = kwargs.get("env")
        return {
            "command": command,
            "exit_code": 0,
            "stdout": "",
            "stderr": "",
            "started_at": "2026-03-30T00:00:00+00:00",
            "ended_at": "2026-03-30T00:00:00+00:00",
        }

    monkeypatch.setattr(live_host_native_product_paths, "_run_timed_command", fake_timed_command)

    live_host_native_product_paths._run_gemini_task(
        "Respond exactly with OK.",
        project_root=Path("/tmp"),
        model="auto",
        auth_mode="api_key",
        approval_mode="yolo",
        hook_log_path=None,
        inject_hook_env=False,
    )

    assert captured["env"] is None


def test_gemini_task_preserves_hook_env_for_wrapped_execution(monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}
    hook_log_path = tmp_path / "gemini.hooks.jsonl"

    def fake_timed_command(command, **kwargs):
        captured["env"] = kwargs.get("env")
        return {
            "command": command,
            "exit_code": 0,
            "stdout": "",
            "stderr": "",
            "started_at": "2026-03-30T00:00:00+00:00",
            "ended_at": "2026-03-30T00:00:00+00:00",
        }

    monkeypatch.setattr(live_host_native_product_paths, "_run_timed_command", fake_timed_command)

    live_host_native_product_paths._run_gemini_task(
        "Respond exactly with OK.",
        project_root=Path("/tmp"),
        model="auto",
        auth_mode="api_key",
        approval_mode="yolo",
        hook_log_path=hook_log_path,
        inject_hook_env=True,
    )

    assert captured["env"]["CORTEX_LIVE_HOOK_PROVIDER"] == "gemini"
    assert captured["env"]["CORTEX_LIVE_HOOK_LOG_PATH"] == str(hook_log_path)


def test_live_hook_recorder_emits_no_stdout_when_logging(capsys, monkeypatch, tmp_path: Path) -> None:
    log_path = tmp_path / "hooks.jsonl"
    monkeypatch.setenv("CORTEX_LIVE_HOOK_LOG_PATH", str(log_path))
    monkeypatch.setenv("CORTEX_LIVE_HOOK_PROVIDER", "claude")
    monkeypatch.setenv("CORTEX_LIVE_HOOK_SCENARIO_ID", "pass_minimal")
    monkeypatch.setattr(sys, "stdin", io.StringIO('{"hook_event_name":"SessionStart"}'))

    assert live_hook_recorder.main([]) == 0
    captured = capsys.readouterr()

    assert captured.out == ""
    records = [json.loads(line) for line in log_path.read_text().splitlines()]
    assert records[0]["hook_event_name"] == "SessionStart"


def test_claude_provider_window_caution_short_circuits_next_pair() -> None:
    note = live_operator_directionality._provider_window_caution(
        "claude",
        {
            "raw_host": (
                {
                    "ended_at": "2026-03-30T00:00:01+00:00",
                    "provider_window_caution": True,
                },
            ),
            "cortex_operator": (),
        },
    )

    assert note is not None
    assert "usage window is contaminated" in note


def test_operator_timeout_after_successful_verification_is_warning_not_failure(
    monkeypatch,
    tmp_path: Path,
) -> None:
    project_root = tmp_path / "workspace"
    project_root.mkdir()
    root = tmp_path / "artifacts"
    root.mkdir()

    monkeypatch.setattr(
        live_host_native_product_paths,
        "run_target_test",
        lambda project_root: {"exit_code": 0, "stdout": "2 passed", "stderr": ""},
    )
    monkeypatch.setattr(
        live_host_native_product_paths,
        "parse_json_records",
        lambda text: ([], "raw_fallback"),
    )
    monkeypatch.setattr(
        live_host_native_product_paths,
        "collect_modified_files",
        lambda project_root: ["src/normalize_port.py"],
    )
    monkeypatch.setattr(
        live_host_native_product_paths,
        "extract_result_text",
        lambda records, text: "completed",
    )
    monkeypatch.setattr(
        live_host_native_product_paths,
        "_read_hook_records",
        lambda path: [],
    )

    payload = live_host_native_product_paths._materialize_operator_run(
        provider="claude",
        scenario_id="pass_minimal",
        repeat_index=1,
        project_root=project_root,
        root=root,
        run_result={
            "command": ["claude", "-p", "prompt"],
            "stdout": "",
            "stderr": "",
            "exit_code": 124,
            "started_at": "2026-03-30T00:00:00+00:00",
            "ended_at": "2026-03-30T00:03:00+00:00",
        },
        model="claude-sonnet-4-6",
        preferred_model="claude-sonnet-4-6",
        auto_supported=None,
        attempted_models=["claude-sonnet-4-6"],
        auth_mode="claude_code",
        failure_class="operator_timeout",
        hook_log_path=None,
    )

    assert payload["success"] is True
    assert payload["failure_class"] is None
    assert payload["warning_classes"] == ["operator_timeout"]


def test_operator_directionality_truth_gap_minimal_flavor_skips_extra_read_pass(
    monkeypatch,
    tmp_path: Path,
) -> None:
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        live_operator_directionality,
        "prepare_harness_workspace",
        lambda **kwargs: tmp_path / "project_a",
    )
    monkeypatch.setattr(
        live_operator_directionality,
        "read_prompt_template",
        lambda filename: "prompt",
    )
    monkeypatch.setattr(
        live_operator_directionality,
        "resolve_auth_mode",
        lambda provider, lane: "api_key",
    )
    monkeypatch.setattr(
        live_operator_directionality,
        "recent_operator_probe_failure",
        lambda provider: None,
    )
    monkeypatch.setattr(
        live_operator_directionality.host_paths,
        "_resolve_cortex_execution_flavor",
        lambda **kwargs: (
            "minimal",
            {
                "execution_flavor_effective": "minimal",
                "execution_flavor_override": "minimal",
            },
        ),
    )
    monkeypatch.setattr(
        live_operator_directionality.host_paths,
        "_configure_hook_capture",
        lambda **kwargs: None,
    )

    def fake_run_operator_attempts(**kwargs):
        captured["execution_flavor"] = kwargs["execution_flavor"]
        return (
            {
                "command": ["gemini"],
                "exit_code": 0,
                "stdout": '{"type":"result","stats":{"input_tokens":1,"output_tokens":1,"cached":0}}',
                "stderr": "",
                "started_at": "2026-03-30T00:00:00+00:00",
                "ended_at": "2026-03-30T00:00:01+00:00",
            },
            None,
            "auto",
            "auto",
            True,
            ["auto"],
        )

    monkeypatch.setattr(
        live_operator_directionality.host_paths,
        "_run_operator_attempts",
        fake_run_operator_attempts,
    )
    monkeypatch.setattr(
        live_operator_directionality.host_paths,
        "_materialize_operator_run",
        lambda **kwargs: {
            "truth_gap_kind": "truthful_incomplete",
            "provider_limit_interference": False,
            "warning_classes": [],
            "attempted_models": ["auto"],
            **kwargs["route_diagnostics"],
        },
    )
    monkeypatch.setattr(
        live_operator_directionality,
        "_maybe_run_cli_extra_read_pass",
        lambda **kwargs: (_ for _ in ()).throw(
            AssertionError("minimal flavor should suppress extra read pass")
        ),
    )

    payload = live_operator_directionality._run_cli_variant(
        "gemini",
        variant="cortex_operator",
        scenario_id="truth_gap",
        repeat_index=1,
        precheck={"status": "ready"},
        baseline_runs=[],
        prior_runs=(),
        cortex_execution_flavor_override="minimal",
    )

    assert captured["execution_flavor"] == "minimal"
    assert payload["execution_flavor_effective"] == "minimal"
    assert payload["execution_flavor_override"] == "minimal"
    assert payload["extra_read_pass_attempted"] is False


def test_product_path_single_scenario_forwards_minimal_execution_flavor(
    monkeypatch,
    tmp_path: Path,
) -> None:
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        live_host_native_product_paths,
        "prepare_harness_workspace",
        lambda **kwargs: tmp_path / "project_a",
    )
    monkeypatch.setattr(
        live_host_native_product_paths,
        "read_prompt_template",
        lambda filename: "Respond exactly with OK.",
    )
    monkeypatch.setattr(
        live_host_native_product_paths,
        "resolve_auth_mode",
        lambda provider, lane: "api_key",
    )
    monkeypatch.setattr(
        live_host_native_product_paths,
        "recent_operator_probe_failure",
        lambda provider: None,
    )
    monkeypatch.setattr(
        live_host_native_product_paths,
        "_resolve_cortex_execution_flavor",
        lambda **kwargs: (
            "minimal",
            {
                "execution_flavor_effective": "minimal",
                "execution_flavor_override": "minimal",
            },
        ),
    )
    monkeypatch.setattr(
        live_host_native_product_paths,
        "_configure_hook_capture",
        lambda **kwargs: None,
    )

    def fake_run_operator_attempts(**kwargs):
        captured["execution_flavor"] = kwargs["execution_flavor"]
        return (
            {
                "command": ["gemini"],
                "exit_code": 1,
                "stdout": "",
                "stderr": "When using Gemini API, you must specify the GEMINI_API_KEY environment variable.",
                "started_at": "2026-03-30T00:00:00+00:00",
                "ended_at": "2026-03-30T00:00:00+00:00",
            },
            "auth_missing",
            "auto",
            "auto",
            False,
            ["auto"],
        )

    monkeypatch.setattr(
        live_host_native_product_paths,
        "_run_operator_attempts",
        fake_run_operator_attempts,
    )
    monkeypatch.setattr(
        live_host_native_product_paths,
        "_materialize_operator_run",
        lambda **kwargs: {
            "success": False,
            "failure_class": "auth_missing",
            "execution_flavor_effective": kwargs["route_diagnostics"][
                "execution_flavor_effective"
            ],
        },
    )

    payload = live_host_native_product_paths._run_single_scenario(
        "gemini",
        "pass_minimal",
        1,
        tmp_path,
        baseline_runs=[],
        prior_runs=(),
        max_attempts=1,
        cooldown_seconds=0,
        preferred_model_override=None,
        fallback_model_override=None,
        disable_auto_probe=False,
        cortex_execution_flavor_override="minimal",
    )

    assert captured["execution_flavor"] == "minimal"
    assert payload["execution_flavor_effective"] == "minimal"


def test_single_live_service_call_records_export_and_warning_timing(monkeypatch) -> None:
    @contextmanager
    def fake_running_service(provider, log_path, *, auth_mode):
        yield "http://127.0.0.1:9999"

    responses = iter(
        [
            (
                200,
                {"records": [{"type": "response"}], "error": {"message": "insufficient_quota"}},
                "2026-03-29T00:00:00+00:00",
                "2026-03-29T00:00:01+00:00",
            ),
            (
                200,
                {"session": {"id": "s-1"}},
                "2026-03-29T00:00:02+00:00",
                "2026-03-29T00:00:03+00:00",
            ),
        ]
    )

    monkeypatch.setattr(live_host_control, "_running_service", fake_running_service)
    monkeypatch.setattr(live_host_control, "_request_json", lambda *args, **kwargs: next(responses))

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir) / ".cortex" / "live_validation" / "automation" / "claude" / "service"
        payload = live_host_control._run_single_live_call(
            "claude",
            auth_mode="api_key",
            model="claude-sonnet-4-6",
            root=root,
        )

    assert payload["success"] is True
    assert payload["failure_class"] is None
    assert payload["warning_classes"] == ["quota_exhausted"]
    assert payload["first_record_at"] == "2026-03-29T00:00:01+00:00"
    assert payload["final_record_at"] == "2026-03-29T00:00:01+00:00"
    assert payload["export_received_at"] == "2026-03-29T00:00:03+00:00"
    assert payload["record_count"] == 1
    assert payload["suite_id"] == "current"
    assert payload["suite_role"] == "readiness_probe"
    assert payload["export_path"].endswith("current__cycle_001__service_smoke.export.json")


def test_claude_canonical_anchor_blocks_truthfully_when_auth_is_missing(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        live_host_control,
        "automation_auth_readiness",
        lambda provider: {
            "auth_mode": "api_key",
            "status": "missing",
            "spend_approved": True,
            "api_key_present": False,
        },
    )
    monkeypatch.setattr(
        live_host_control,
        "provider_root",
        lambda provider, lane, surface: tmp_path / lane / provider / surface,
    )

    payload = live_host_control._capture_provider("claude", suite_id="canonical_anchor")

    assert payload["suite_id"] == "canonical_anchor"
    assert payload["cycle_count"] == 1
    assert payload["latest_cycle_status"] == "blocked"
    assert payload["latest_failure_classes"] == ["auth_missing"]


def test_gemini_canonical_anchor_remains_mis_scoped(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        live_host_control,
        "automation_auth_readiness",
        lambda provider: {
            "auth_mode": "vertex_adc",
            "status": "ready",
            "spend_approved": True,
            "api_key_present": False,
            "vertex_adc_available": True,
        },
    )
    monkeypatch.setattr(
        live_host_control,
        "provider_root",
        lambda provider, lane, surface: tmp_path / lane / provider / surface,
    )

    payload = live_host_control._capture_provider("gemini", suite_id="canonical_anchor")

    assert payload["suite_id"] == "canonical_anchor"
    assert payload["cycle_count"] == 1
    assert payload["latest_cycle_status"] == "blocked"
    assert payload["latest_failure_classes"] == ["mis_scoped"]


def test_canonical_pass_minimal_applies_patch_and_runs_test(monkeypatch, tmp_path: Path) -> None:
    diff_text = """diff --git a/src/normalize_port.py b/src/normalize_port.py
--- a/src/normalize_port.py
+++ b/src/normalize_port.py
@@ -4,5 +4,5 @@ def normalize_port(value: int | str) -> int:
     port = int(value)
     if port < 0:
         raise ValueError(\"port must be non-negative\")
-    if port >= 65535:
+    if port > 65535:
         raise ValueError(\"port must be <= 65535\")
     return port
"""

    @contextmanager
    def fake_running_service(provider, log_path, *, auth_mode):
        yield "http://127.0.0.1:9999"

    responses = iter(
        [
            (
                200,
                {"records": [{"response": diff_text}]},
                "2026-03-29T00:00:00+00:00",
                "2026-03-29T00:00:01+00:00",
            )
        ]
    )

    monkeypatch.setattr(live_host_control, "_running_service", fake_running_service)
    monkeypatch.setattr(live_host_control, "_request_json", lambda *args, **kwargs: next(responses))
    monkeypatch.setattr(
        live_host_control,
        "prepare_harness_workspace",
        lambda **kwargs: live_validation_common.prepare_harness_workspace(
            provider="openai",
            lane="automation",
            scenario_id="pass_minimal",
            repeat_index=1,
        ),
    )

    root = tmp_path / ".cortex" / "live_validation" / "automation" / "openai" / "service"
    payload = live_host_control._run_pass_minimal_capture(
        provider="openai",
        auth_mode="api_key",
        model="gpt-5.4",
        root=root,
        suite_id="canonical_anchor",
        suite_role="canonical_truth_anchor",
        cycle_index=1,
    )

    assert payload["success"] is True
    assert payload["failure_class"] is None
    assert payload["modified_files"] == ["src/normalize_port.py"]
    assert payload["test_result_path"].endswith("canonical_anchor__cycle_001__pass_minimal.test.json")


def test_canonical_truth_gap_stays_theless_and_truthful(monkeypatch, tmp_path: Path) -> None:
    @contextmanager
    def fake_running_service(provider, log_path, *, auth_mode):
        yield "http://127.0.0.1:9999"

    responses = iter(
        [
            (
                200,
                {
                    "records": [
                        {
                            "response": (
                                "Task is incomplete because this is inspection only. "
                                "I did not edit files or run tests, so the bug is not verified as fixed."
                            )
                        }
                    ]
                },
                "2026-03-29T00:00:00+00:00",
                "2026-03-29T00:00:01+00:00",
            )
        ]
    )

    monkeypatch.setattr(live_host_control, "_running_service", fake_running_service)
    monkeypatch.setattr(live_host_control, "_request_json", lambda *args, **kwargs: next(responses))

    root = tmp_path / ".cortex" / "live_validation" / "automation" / "openai" / "service"
    payload = live_host_control._run_truth_gap_capture(
        provider="openai",
        auth_mode="api_key",
        model="gpt-5.4",
        root=root,
        suite_id="canonical_anchor",
        suite_role="canonical_truth_anchor",
        cycle_index=1,
    )

    assert payload["success"] is True
    assert payload["truth_gap_kind"] == "truthful_incomplete"
    assert payload["failure_class"] is None


def test_canonical_restart_continuity_uses_export_import_and_external_test(monkeypatch, tmp_path: Path) -> None:
    diff_text = """diff --git a/src/normalize_port.py b/src/normalize_port.py
--- a/src/normalize_port.py
+++ b/src/normalize_port.py
@@ -4,5 +4,5 @@ def normalize_port(value: int | str) -> int:
     port = int(value)
     if port < 0:
         raise ValueError(\"port must be non-negative\")
-    if port >= 65535:
+    if port > 65535:
         raise ValueError(\"port must be <= 65535\")
     return port
"""

    urls = iter(["http://127.0.0.1:9999", "http://127.0.0.1:9998"])

    @contextmanager
    def fake_running_service(provider, log_path, *, auth_mode):
        yield next(urls)

    responses = iter(
        [
            (
                200,
                {"records": [{"response": "Fix the `>= 65535` guard so only ports above 65535 fail."}]},
                "2026-03-29T00:00:00+00:00",
                "2026-03-29T00:00:01+00:00",
            ),
            (
                200,
                {"session": {"id": "s-1"}},
                "2026-03-29T00:00:01+00:00",
                "2026-03-29T00:00:02+00:00",
            ),
            (
                200,
                {"session": {"id": "s-1"}},
                "2026-03-29T00:00:02+00:00",
                "2026-03-29T00:00:03+00:00",
            ),
            (
                200,
                {"records": [{"response": diff_text}]},
                "2026-03-29T00:00:03+00:00",
                "2026-03-29T00:00:04+00:00",
            ),
            (
                200,
                {"session": {"id": "s-1"}},
                "2026-03-29T00:00:04+00:00",
                "2026-03-29T00:00:05+00:00",
            ),
        ]
    )

    monkeypatch.setattr(live_host_control, "_running_service", fake_running_service)
    monkeypatch.setattr(live_host_control, "_request_json", lambda *args, **kwargs: next(responses))

    root = tmp_path / ".cortex" / "live_validation" / "automation" / "openai" / "service"
    payload = live_host_control._run_canonical_restart_continuity_capture(
        provider="openai",
        auth_mode="api_key",
        model="gpt-5.4",
        root=root,
        suite_id="canonical_anchor",
        suite_role="canonical_truth_anchor",
        cycle_index=1,
    )

    assert payload["success"] is True
    assert payload["failure_class"] is None
    assert payload["modified_files"] == ["src/normalize_port.py"]
    assert payload["plan_text_path"].endswith("canonical_anchor__cycle_001__restart_continuity.plan.txt")


def test_canonical_restart_continuity_uses_second_result_text_when_records_are_lifecycle_only(
    monkeypatch,
    tmp_path: Path,
) -> None:
    diff_text = """diff --git a/src/normalize_port.py b/src/normalize_port.py
--- a/src/normalize_port.py
+++ b/src/normalize_port.py
@@ -4,5 +4,5 @@ def normalize_port(value: int | str) -> int:
     port = int(value)
     if port < 0:
         raise ValueError(\"port must be non-negative\")
-    if port >= 65535:
+    if port > 65535:
         raise ValueError(\"port must be <= 65535\")
     return port
"""

    workspace_path = live_validation_common.prepare_harness_workspace(
        provider="openai",
        lane="automation",
        scenario_id="restart_continuity",
        repeat_index=1,
    )

    monkeypatch.setattr(
        live_host_control,
        "prepare_harness_workspace",
        lambda **kwargs: workspace_path,
    )
    monkeypatch.setattr(
        live_host_control,
        "_invoke_continuity_roundtrip",
        lambda **kwargs: {
            "first_status": 200,
            "export_status": 200,
            "import_status": 200,
            "second_status": 200,
            "final_export_status": 200,
            "failure_class": None,
            "first_records": [{"response": "Change >= 65535 to > 65535."}],
            "second_records": [],
            "first_result_text": "Change >= 65535 to > 65535.",
            "second_result_text": diff_text,
            "first_request_started_at": "2026-03-29T00:00:00+00:00",
            "first_response_received_at": "2026-03-29T00:00:01+00:00",
            "second_response_received_at": "2026-03-29T00:00:04+00:00",
            "import_received_at": "2026-03-29T00:00:03+00:00",
            "final_export_received_at": "2026-03-29T00:00:05+00:00",
            "first_request_path": "first.request.json",
            "first_response_path": "first.response.json",
            "first_export_path": "first.export.json",
            "import_response_path": "import.response.json",
            "second_request_path": "second.request.json",
            "second_response_path": "second.response.json",
            "final_export_path": "final.export.json",
            "second_service_log_path": "second.stderr.log",
            "second_response": {"result_text": diff_text},
        },
    )

    root = tmp_path / ".cortex" / "live_validation" / "automation" / "openai" / "service"
    payload = live_host_control._run_canonical_restart_continuity_capture(
        provider="openai",
        auth_mode="api_key",
        model="gpt-5.4",
        root=root,
        suite_id="canonical_anchor",
        suite_role="canonical_truth_anchor",
        cycle_index=1,
    )

    assert payload["success"] is True
    assert payload["failure_class"] is None
    assert payload["modified_files"] == ["src/normalize_port.py"]
    assert payload["test_result_path"].endswith("canonical_anchor__cycle_001__restart_continuity.test.json")


def test_service_lane_delta_reports_auth_readiness_and_service_success() -> None:
    delta = live_compare._service_lane_delta(
        {
            "claude": {
                "automation_auth": {"status": "missing"},
                "automation_service": {
                    "current": {"latest_cycle_success": False},
                    "canonical_anchor": {
                        "cycle_count": 0,
                        "repeat_stable_success": False,
                    },
                },
            },
            "gemini": {
                "automation_auth": {"status": "ready"},
                "automation_service": {
                    "current": {"latest_cycle_success": False},
                    "canonical_anchor": {
                        "cycle_count": 1,
                        "repeat_stable_success": False,
                    },
                },
            },
            "openai": {
                "automation_auth": {"status": "blocked_by_spend_policy"},
                "automation_service": {
                    "current": {"latest_cycle_success": True},
                    "canonical_anchor": {
                        "cycle_count": 2,
                        "repeat_stable_success": True,
                    },
                },
            },
        },
        canonical_scope={"openai"},
    )

    assert "automation auth readiness is `none` ready" in delta
    assert "openai:blocked_by_spend_policy" in delta
    assert "direct_api canonical truth is re-earned for current scope on `openai`" in delta
    assert "headless_cli watchlist currently reads `claude:unknown, gemini:unknown, openai:unknown`" in delta
    assert "out-of-scope direct_api providers remain watchlist-only for runtime truth: `claude, gemini`" in delta


def test_live_compare_treats_smoke_only_as_readiness_not_canonical_truth(monkeypatch) -> None:
    def fake_read_json(path):
        text_path = str(path)
        if path == live_compare.PREFLIGHT_REPORT_PATH:
            return {
                "operator_probe": {"claude": {}, "gemini": {}, "openai": {}},
                "auth_surfaces": {
                    "automation": {
                        "claude": {"status": "missing"},
                        "gemini": {"status": "missing"},
                        "openai": {"status": "ready"},
                    }
                },
            }
        if text_path.endswith("automation/openai/service/service_runs.json"):
            return {
                "suites": {
                    "current": {
                        "suite_id": "current",
                        "suite_role": "readiness_probe",
                        "cycle_count": 1,
                        "successful_cycle_count": 1,
                        "latest_cycle_status": "positive",
                        "latest_cycle_success": True,
                        "latest_failure_classes": [],
                        "latest_warning_classes": [],
                        "cycles": [{"cycle_index": 1, "success": True, "cycle_status": "positive", "runs": []}],
                    }
                }
            }
        return {}

    monkeypatch.setattr(live_compare, "_read_json", fake_read_json)

    comparison = live_compare._build_comparison(
        {
            "operator_probe": {"claude": {}, "gemini": {}, "openai": {}},
            "auth_surfaces": {"automation": {"claude": {"status": "missing"}, "gemini": {"status": "missing"}, "openai": {"status": "ready"}}},
        }
    )

    assert comparison["service_success_count"] == 0
    assert comparison["verdict"] == "canonical runtime truth is still partial"
    assert comparison["providers"]["openai"]["automation_service"]["current"]["latest_cycle_success"] is True
    assert comparison["providers"]["openai"]["automation_service"]["canonical_anchor"]["repeat_stable_success"] is False


def test_live_compare_requires_repeat_stable_canonical_anchor_for_openai_truth(monkeypatch) -> None:
    def fake_read_json(path):
        text_path = str(path)
        if path == live_compare.PREFLIGHT_REPORT_PATH:
            return {
                "operator_probe": {"claude": {}, "gemini": {}, "openai": {}},
                "auth_surfaces": {
                    "automation": {
                        "claude": {"status": "missing"},
                        "gemini": {"status": "missing"},
                        "openai": {"status": "ready"},
                    }
                },
            }
        if text_path.endswith("automation/openai/service/service_runs.json"):
            return {
                "suites": {
                    "current": {
                        "suite_id": "current",
                        "suite_role": "readiness_probe",
                        "cycle_count": 1,
                        "successful_cycle_count": 1,
                        "latest_cycle_status": "positive",
                        "latest_cycle_success": True,
                        "latest_failure_classes": [],
                        "latest_warning_classes": [],
                        "cycles": [{"cycle_index": 1, "success": True, "cycle_status": "positive", "runs": []}],
                    },
                    "canonical_anchor": {
                        "suite_id": "canonical_anchor",
                        "suite_role": "canonical_truth_anchor",
                        "cycle_count": 2,
                        "successful_cycle_count": 2,
                        "repeat_stable_success": True,
                        "latest_cycle_status": "positive",
                        "latest_cycle_success": True,
                        "latest_failure_classes": [],
                        "latest_warning_classes": [],
                        "cycles": [
                            {"cycle_index": 1, "success": True, "cycle_status": "positive", "runs": []},
                            {"cycle_index": 2, "success": True, "cycle_status": "positive", "runs": []},
                        ],
                    },
                }
            }
        return {}

    monkeypatch.setattr(live_compare, "_read_json", fake_read_json)

    comparison = live_compare._build_comparison(
        {
            "operator_probe": {"claude": {}, "gemini": {}, "openai": {}},
            "auth_surfaces": {"automation": {"claude": {"status": "missing"}, "gemini": {"status": "missing"}, "openai": {"status": "ready"}}},
        }
    )

    assert comparison["service_success_count"] == 1
    assert comparison["verdict"] == "canonical runtime truth is re-earned for current scope"
    assert comparison["automation_pass_count"] == 1
    assert comparison["canonical_provider_scope"] == ["openai"]
    assert comparison["providers"]["openai"]["automation_service"]["canonical_anchor"]["repeat_stable_success"] is True


def test_live_compare_ignores_ready_out_of_scope_provider_for_current_scope_truth(monkeypatch) -> None:
    def fake_read_json(path):
        text_path = str(path)
        if path == live_compare.PREFLIGHT_REPORT_PATH:
            return {
                "operator_probe": {"claude": {}, "gemini": {}, "openai": {}},
                "auth_surfaces": {
                    "automation": {
                        "claude": {"status": "missing"},
                        "gemini": {"status": "ready"},
                        "openai": {"status": "ready"},
                    }
                },
            }
        if text_path.endswith("automation/openai/service/service_runs.json"):
            return {
                "suites": {
                    "canonical_anchor": {
                        "suite_id": "canonical_anchor",
                        "suite_role": "canonical_truth_anchor",
                        "cycle_count": 3,
                        "successful_cycle_count": 3,
                        "repeat_stable_success": True,
                        "latest_cycle_status": "positive",
                        "latest_cycle_success": True,
                        "latest_failure_classes": [],
                        "latest_warning_classes": [],
                        "cycles": [
                            {"cycle_index": 1, "success": True, "cycle_status": "positive", "runs": []},
                            {"cycle_index": 2, "success": True, "cycle_status": "positive", "runs": []},
                            {"cycle_index": 3, "success": True, "cycle_status": "positive", "runs": []},
                        ],
                    }
                }
            }
        if text_path.endswith("automation/gemini/service/service_runs.json"):
            return {
                "suites": {
                    "canonical_anchor": {
                        "suite_id": "canonical_anchor",
                        "suite_role": "canonical_truth_anchor",
                        "cycle_count": 1,
                        "successful_cycle_count": 0,
                        "repeat_stable_success": False,
                        "latest_cycle_status": "blocked",
                        "latest_cycle_success": False,
                        "latest_failure_classes": ["mis_scoped"],
                        "latest_warning_classes": [],
                        "cycles": [
                            {"cycle_index": 1, "success": False, "cycle_status": "blocked", "runs": []},
                        ],
                    }
                }
            }
        return {}

    monkeypatch.setattr(live_compare, "_read_json", fake_read_json)

    comparison = live_compare._build_comparison(
        {
            "operator_probe": {"claude": {}, "gemini": {}, "openai": {}},
            "auth_surfaces": {
                "automation": {
                    "claude": {"status": "missing"},
                    "gemini": {"status": "ready"},
                    "openai": {"status": "ready"},
                }
            },
        }
    )

    assert comparison["automation_pass_count"] == 1
    assert comparison["service_success_count"] == 1
    assert comparison["verdict"] == "canonical runtime truth is re-earned for current scope"
    assert comparison["providers"]["gemini"]["automation_service"]["in_canonical_scope"] is False
    assert "out-of-scope direct_api providers remain watchlist-only" in comparison["service_lane_delta"]
    assert comparison["next_corrective_seam"] == (
        "current OpenAI-only product scope is already re-earned on the canonical direct-API lane and the active support/eval shell is already compressed; keep out-of-scope hosts watchlist-only or future-host backlog, treat origin/main reconciliation as separate workflow hygiene, and open any later host expansion only through an explicit new train"
    )


def test_live_compare_ignores_ready_out_of_scope_claude_for_current_scope_truth(monkeypatch) -> None:
    def fake_read_json(path):
        text_path = str(path)
        if path == live_compare.PREFLIGHT_REPORT_PATH:
            return {
                "operator_probe": {"claude": {}, "gemini": {}, "openai": {}},
                "auth_surfaces": {
                    "automation": {
                        "claude": {"status": "ready"},
                        "gemini": {"status": "missing"},
                        "openai": {"status": "ready"},
                    }
                },
            }
        if text_path.endswith("automation/openai/service/service_runs.json"):
            return {
                "suites": {
                    "canonical_anchor": {
                        "suite_id": "canonical_anchor",
                        "suite_role": "canonical_truth_anchor",
                        "cycle_count": 3,
                        "successful_cycle_count": 3,
                        "repeat_stable_success": True,
                        "latest_cycle_status": "positive",
                        "latest_cycle_success": True,
                        "latest_failure_classes": [],
                        "latest_warning_classes": [],
                        "cycles": [
                            {"cycle_index": 1, "success": True, "cycle_status": "positive", "runs": []},
                            {"cycle_index": 2, "success": True, "cycle_status": "positive", "runs": []},
                            {"cycle_index": 3, "success": True, "cycle_status": "positive", "runs": []},
                        ],
                    }
                }
            }
        if text_path.endswith("automation/claude/service/service_runs.json"):
            return {
                "suites": {
                    "canonical_anchor": {
                        "suite_id": "canonical_anchor",
                        "suite_role": "canonical_truth_anchor",
                        "cycle_count": 1,
                        "successful_cycle_count": 0,
                        "repeat_stable_success": False,
                        "latest_cycle_status": "blocked",
                        "latest_cycle_success": False,
                        "latest_failure_classes": ["auth_missing"],
                        "latest_warning_classes": [],
                        "cycles": [
                            {"cycle_index": 1, "success": False, "cycle_status": "blocked", "runs": []},
                        ],
                    }
                }
            }
        return {}

    monkeypatch.setattr(live_compare, "_read_json", fake_read_json)

    comparison = live_compare._build_comparison(
        {
            "operator_probe": {"claude": {}, "gemini": {}, "openai": {}},
            "auth_surfaces": {
                "automation": {
                    "claude": {"status": "ready"},
                    "gemini": {"status": "missing"},
                    "openai": {"status": "ready"},
                }
            },
        }
    )

    assert comparison["canonical_provider_scope"] == ["openai"]
    assert comparison["automation_pass_count"] == 1
    assert comparison["service_success_count"] == 1
    assert comparison["verdict"] == "canonical runtime truth is re-earned for current scope"
    assert comparison["providers"]["claude"]["automation_service"]["in_canonical_scope"] is False
    assert "out-of-scope direct_api providers remain watchlist-only" in comparison["service_lane_delta"]


def test_live_compare_falls_back_to_accepted_watchlist_when_local_operator_artifacts_are_absent(
    monkeypatch,
) -> None:
    workstream_text = """
- the OpenAI App Server operator lane now completes:
    - `pass_minimal` twice
    - `truth_gap` truthfully
    - `restart_continuity` twice
- the Claude operator lane is now hook-backed and completes:
    - `pass_minimal` twice
    - `truth_gap` truthfully
    - `restart_continuity`
- the deeper Gemini auto-mode product-path rerun now shows:
    - `pass_minimal` succeeds twice on `auto` with explicit `capacity_exhausted` warnings
    - `truth_gap` is truthful on the latest reruns on `auto`
    - `restart_continuity` is not yet repeat-stable because the latest reruns include a `capacity_exhausted` blocker on `auto`
"""
    monkeypatch.setattr(live_compare, "WORKSTREAM_PATH", Path("/tmp/workstream.md"))
    live_compare.WORKSTREAM_PATH.write_text(workstream_text, encoding="utf-8")
    monkeypatch.setattr(
        live_compare,
        "_read_json",
        lambda path: {"operator_probe": {"claude": {}, "gemini": {}, "openai": {}}}
        if path == live_compare.PREFLIGHT_REPORT_PATH
        else {},
    )

    comparison = live_compare._build_comparison({"operator_probe": {"claude": {}, "gemini": {}, "openai": {}}, "auth_surfaces": {"automation": {}}})

    assert comparison["operator_pass_count"] == 3
    assert comparison["operator_truthful_gap_count"] == 3
    assert comparison["providers"]["claude"]["operator_lifecycle"]["source"] == "accepted_watchlist_fallback"
    assert comparison["providers"]["gemini"]["operator_lifecycle"]["restart_continuity_success"] is False
    assert comparison["providers"]["openai"]["operator_lifecycle"]["pass_minimal_success"] is True
    assert comparison["watchlist_drift_hosts"] == []


def test_live_compare_surfaces_watchlist_drift_when_local_operator_artifacts_are_partial(
    monkeypatch,
) -> None:
    workstream_text = """
- the OpenAI App Server operator lane now completes:
    - `pass_minimal` twice
    - `truth_gap` truthfully
    - `restart_continuity` twice
- the Claude operator lane is now hook-backed and completes:
    - `pass_minimal` twice
    - `truth_gap` truthfully
    - `restart_continuity`
- the deeper Gemini auto-mode product-path rerun now shows:
    - `pass_minimal` succeeds twice on `auto` with explicit `capacity_exhausted` warnings
    - `truth_gap` is truthful on the latest reruns on `auto`
    - `restart_continuity` is not yet repeat-stable because the latest reruns include a `capacity_exhausted` blocker on `auto`
"""
    monkeypatch.setattr(live_compare, "WORKSTREAM_PATH", Path("/tmp/workstream-mixed.md"))
    live_compare.WORKSTREAM_PATH.write_text(workstream_text, encoding="utf-8")

    local_product_runs = {
        "runs": [
            {
                "scenario_id": "operator_product_gate",
                "repeat_index": 1,
                "success": False,
                "failure_class": "operator_surface_missing",
            },
            {
                "scenario_id": "restart_continuity",
                "repeat_index": 1,
                "success": True,
                "failure_class": None,
                "warning_classes": ["capacity_exhausted"],
                "model": "auto",
                "preferred_model": "auto",
                "hook_event_labels": ["SessionStart", "BeforeTool", "AfterTool", "SessionEnd"],
            },
        ]
    }

    def fake_read_json(path):
        text_path = str(path)
        if path == live_compare.PREFLIGHT_REPORT_PATH:
            return {
                "operator_probe": {"claude": {}, "gemini": {}, "openai": {}},
                "auth_surfaces": {
                    "automation": {
                        "claude": {"status": "missing"},
                        "gemini": {"status": "missing"},
                        "openai": {"status": "missing"},
                    }
                },
            }
        if text_path.endswith("operator/gemini/product_paths/host_native_product_runs.json"):
            return local_product_runs
        return {}

    monkeypatch.setattr(live_compare, "_read_json", fake_read_json)

    comparison = live_compare._build_comparison(
        {
            "operator_probe": {"claude": {}, "gemini": {}, "openai": {}},
            "auth_surfaces": {"automation": {"claude": {"status": "missing"}, "gemini": {"status": "missing"}, "openai": {"status": "missing"}}},
        }
    )

    gemini = comparison["providers"]["gemini"]["operator_lifecycle"]
    assert gemini["source"] == "local_artifacts"
    assert gemini["pass_minimal_success"] is False
    assert gemini["truth_gap_preserved"] is False
    assert gemini["restart_continuity_success"] is True
    assert gemini["watchlist_status"] == "unresolved"
    assert gemini["accepted_watchlist_status"] == "unresolved"
    assert gemini["accepted_watchlist_drift_detected"] is True
    assert comparison["watchlist_drift_hosts"] == ["gemini"]


def test_gemini_continuity_requires_latest_local_runs_to_be_repeat_stable() -> None:
    runs = [
        {
            "scenario_id": "restart_continuity",
            "repeat_index": 1,
            "success": True,
            "artifact_path": ".cortex/live_validation/operator/gemini/product_paths/restart_continuity__run_001.json",
        },
        {
            "scenario_id": "restart_continuity",
            "repeat_index": 2,
            "success": False,
            "artifact_path": ".cortex/live_validation/operator/gemini/product_paths/restart_continuity_turn_1__run_002.json",
        },
        {
            "scenario_id": "restart_continuity",
            "repeat_index": 3,
            "success": True,
            "artifact_path": ".cortex/live_validation/operator/gemini/product_paths/restart_continuity__run_003.json",
        },
        {
            "scenario_id": "restart_continuity",
            "repeat_index": 4,
            "success": False,
            "artifact_path": ".cortex/live_validation/operator/gemini/product_paths/restart_continuity_turn_1__run_004.json",
        },
    ]

    assert live_compare._continuity_success(provider="gemini", operator_runs=runs) is False


def test_next_repeat_index_advances_for_existing_restart_runs() -> None:
    existing_runs = [
        {"scenario_id": "restart_continuity", "repeat_index": 1},
        {"scenario_id": "restart_continuity", "repeat_index": 2},
        {"scenario_id": "truth_gap", "repeat_index": 1},
    ]

    assert live_host_native_product_paths._next_repeat_index(existing_runs, "restart_continuity") == 3
    assert live_host_native_product_paths._next_repeat_index(existing_runs, "pass_minimal") == 1


def test_gemini_operator_commands_omit_model_flag_when_auto_is_selected(monkeypatch) -> None:
    captured: dict[str, list[str]] = {}

    def fake_run_command(command, **kwargs):
        captured["preflight"] = command
        return {
            "command": command,
            "exit_code": 0,
            "stdout": "",
            "stderr": "",
            "started_at": "2026-03-28T00:00:00+00:00",
            "ended_at": "2026-03-28T00:00:00+00:00",
        }

    monkeypatch.setattr(live_preflight, "run_command", fake_run_command)
    live_preflight._run_gemini_probe("auto")
    assert "-m" not in captured["preflight"]
    assert captured["preflight"][-1] == "yolo"

    def fake_subprocess_run(command, **kwargs):
        captured["baseline"] = command
        class Result:
            returncode = 0
            stdout = ""
            stderr = ""
        return Result()

    monkeypatch.setattr(live_provider_baselines.subprocess, "run", fake_subprocess_run)
    live_provider_baselines._run_gemini_operator_probe("auto")
    assert "-m" not in captured["baseline"]
    assert captured["baseline"][-1] == "yolo"

    def fake_timed_command(command, **kwargs):
        captured["product_path"] = command
        return {
            "command": command,
            "exit_code": 0,
            "stdout": "",
            "stderr": "",
            "started_at": "2026-03-28T00:00:00+00:00",
            "ended_at": "2026-03-28T00:00:00+00:00",
        }

    monkeypatch.setattr(live_host_native_product_paths, "_run_timed_command", fake_timed_command)
    live_host_native_product_paths._run_gemini_task(
        "Respond exactly with OK.",
        project_root=Path("/tmp"),
        model="auto",
        auth_mode="api_key",
    )
    assert "-m" not in captured["product_path"]
    assert captured["product_path"][-1] == "yolo"

    live_host_native_product_paths._run_gemini_task(
        "Respond exactly with OK.",
        project_root=Path("/tmp"),
        model="auto",
        auth_mode="api_key",
        approval_mode="plan",
    )
    assert "-m" not in captured["product_path"]
    assert captured["product_path"][-1] == "plan"


def test_gemini_baseline_keeps_auto_as_preferred_model_on_warning_bearing_success(monkeypatch) -> None:
    monkeypatch.setattr(
        live_provider_baselines,
        "_run_provider_probe",
        lambda *args, **kwargs: {
            "command": ["gemini", "-p", "Respond exactly with OK.", "-o", "stream-json", "--approval-mode", "yolo"],
            "exit_code": 0,
            "stdout": '{"type":"result","status":"success","error":{"message":"You have exhausted your capacity on this model."}}',
            "stderr": "",
            "started_at": "2026-03-29T00:00:00+00:00",
            "ended_at": "2026-03-29T00:00:01+00:00",
        },
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        payload = live_provider_baselines._run_single_provider_baseline(
            provider="gemini",
            lane="operator",
            repeat_index=1,
            provider_root_path=Path(tmpdir),
            preferred_model_override=None,
            fallback_model_override=None,
            disable_auto_probe=False,
        )

    assert payload["preferred_model"] == "auto"
    assert payload["model"] == "auto"
    assert payload["warning_classes"] == ["capacity_exhausted"]


def test_product_path_single_scenario_passes_default_approval_mode(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        live_host_native_product_paths,
        "prepare_harness_workspace",
        lambda **kwargs: tmp_path / "project_a",
    )
    monkeypatch.setattr(
        live_host_native_product_paths,
        "_configure_hook_capture",
        lambda **kwargs: None,
    )
    monkeypatch.setattr(
        live_host_native_product_paths,
        "read_prompt_template",
        lambda filename: "Respond exactly with OK.",
    )
    monkeypatch.setattr(
        live_host_native_product_paths,
        "resolve_auth_mode",
        lambda provider, lane: "api_key",
    )
    monkeypatch.setattr(
        live_host_native_product_paths,
        "recent_operator_probe_failure",
        lambda provider: None,
    )

    captured: dict[str, object] = {}

    def fake_run_operator_attempts(**kwargs):
        captured["approval_mode"] = kwargs["approval_mode"]
        return (
            {
                "command": ["gemini"],
                "exit_code": 1,
                "stdout": "",
                "stderr": "When using Gemini API, you must specify the GEMINI_API_KEY environment variable.",
                "started_at": "2026-03-30T00:00:00+00:00",
                "ended_at": "2026-03-30T00:00:00+00:00",
            },
            "auth_missing",
            "auto",
            "auto",
            False,
            ["auto"],
        )

    monkeypatch.setattr(live_host_native_product_paths, "_run_operator_attempts", fake_run_operator_attempts)
    monkeypatch.setattr(
        live_host_native_product_paths,
        "_materialize_operator_run",
        lambda **kwargs: {
            "success": False,
            "failure_class": "auth_missing",
            "artifact_path": ".cortex/live_validation/operator/gemini/product_paths/restart_continuity_turn_1__run_001.json",
        },
    )

    live_host_native_product_paths._run_single_scenario(
        "gemini",
        "pass_minimal",
        1,
        tmp_path,
        baseline_runs=[],
        prior_runs=(),
        max_attempts=1,
        cooldown_seconds=0,
        preferred_model_override=None,
        fallback_model_override=None,
        disable_auto_probe=False,
    )

    assert captured["approval_mode"] is None


def test_product_path_single_scenario_blocks_when_route_selector_blocks(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(
        live_host_native_product_paths,
        "prepare_harness_workspace",
        lambda **kwargs: tmp_path / "project_a",
    )
    monkeypatch.setattr(
        live_host_native_product_paths,
        "_configure_hook_capture",
        lambda **kwargs: None,
    )
    monkeypatch.setattr(
        live_host_native_product_paths,
        "read_prompt_template",
        lambda filename: "prompt",
    )
    monkeypatch.setattr(
        live_host_native_product_paths,
        "resolve_auth_mode",
        lambda provider, lane: "api_key",
    )
    monkeypatch.setattr(
        live_host_native_product_paths,
        "recent_operator_probe_failure",
        lambda provider: "quota_exhausted",
    )
    monkeypatch.setattr(
        live_host_native_product_paths,
        "_run_operator_attempts",
        lambda **kwargs: (_ for _ in ()).throw(AssertionError("operator call should not run")),
    )

    payload = live_host_native_product_paths._run_single_scenario(
        "gemini",
        "pass_minimal",
        1,
        tmp_path,
        baseline_runs=[],
        prior_runs=(),
        max_attempts=1,
        cooldown_seconds=0,
        preferred_model_override=None,
        fallback_model_override=None,
        disable_auto_probe=False,
    )

    assert payload["failure_class"] == "quota_exhausted"
    assert payload["route_profile"] == "blocked"
    assert payload["blocked_reason"] == "blocked_by_modulator_stop_pressure"


def test_product_path_restart_continuity_uses_default_first_turn_for_gemini(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(
        live_host_native_product_paths,
        "prepare_harness_workspace",
        lambda **kwargs: tmp_path / "project_a",
    )
    monkeypatch.setattr(
        live_host_native_product_paths,
        "_configure_hook_capture",
        lambda **kwargs: None,
    )
    monkeypatch.setattr(
        live_host_native_product_paths,
        "resolve_auth_mode",
        lambda provider, lane: "api_key",
    )
    monkeypatch.setattr(
        live_host_native_product_paths,
        "recent_operator_probe_failure",
        lambda provider: None,
    )
    monkeypatch.setattr(
        live_host_native_product_paths,
        "read_prompt_template",
        lambda filename: "prompt",
    )

    captured: dict[str, object] = {}

    def fake_run_operator_attempts(**kwargs):
        captured["approval_mode"] = kwargs["approval_mode"]
        return (
            {
                "command": ["gemini"],
                "exit_code": 1,
                "stdout": "",
                "stderr": "When using Gemini API, you must specify the GEMINI_API_KEY environment variable.",
                "started_at": "2026-03-30T00:00:00+00:00",
                "ended_at": "2026-03-30T00:00:00+00:00",
            },
            "auth_missing",
            "auto",
            "auto",
            False,
            ["auto"],
        )

    monkeypatch.setattr(live_host_native_product_paths, "_run_operator_attempts", fake_run_operator_attempts)
    monkeypatch.setattr(
        live_host_native_product_paths,
        "_materialize_operator_run",
        lambda **kwargs: {
            "success": False,
            "failure_class": "auth_missing",
            "artifact_path": ".cortex/live_validation/operator/gemini/product_paths/restart_continuity_turn_1__run_001.json",
        },
    )

    live_host_native_product_paths._run_restart_continuity(
        "gemini",
        tmp_path,
        existing_runs=[],
        baseline_runs=[],
        prior_runs=(),
        max_attempts=1,
        cooldown_seconds=0,
        preferred_model_override=None,
        fallback_model_override=None,
        disable_auto_probe=False,
    )

    assert captured["approval_mode"] is None


def test_gemini_raw_directionality_task_accepts_api_key_auth_mode(monkeypatch) -> None:
    captured: dict[str, list[str]] = {}

    def fake_timed_command(command, **kwargs):
        captured["command"] = command
        return {
            "command": command,
            "exit_code": 0,
            "stdout": "",
            "stderr": "",
            "started_at": "2026-03-30T00:00:00+00:00",
            "ended_at": "2026-03-30T00:00:00+00:00",
        }

    monkeypatch.setattr(live_host_native_product_paths, "_run_timed_command", fake_timed_command)

    live_operator_directionality._run_raw_gemini_task(
        "Respond exactly with OK.",
        project_root=Path("/tmp"),
        model="auto",
        auth_mode="api_key",
        approval_mode="plan",
    )

    assert captured["command"] == [
        "gemini",
        "-p",
        "Respond exactly with OK.",
        "-o",
        "stream-json",
        "--approval-mode",
        "plan",
    ]


def test_operator_directionality_restart_continuity_uses_default_first_turn_for_gemini(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(
        live_operator_directionality,
        "resolve_auth_mode",
        lambda provider, lane: "api_key",
    )
    monkeypatch.setattr(
        live_operator_directionality,
        "recent_operator_probe_failure",
        lambda provider: None,
    )
    monkeypatch.setattr(
        live_operator_directionality,
        "read_prompt_template",
        lambda filename: "prompt",
    )

    captured: dict[str, object] = {}

    def fake_run_operator_attempts(**kwargs):
        captured["approval_mode"] = kwargs["approval_mode"]
        return (
            {
                "command": ["gemini"],
                "exit_code": 1,
                "stdout": "",
                "stderr": "When using Gemini API, you must specify the GEMINI_API_KEY environment variable.",
                "started_at": "2026-03-30T00:00:00+00:00",
                "ended_at": "2026-03-30T00:00:00+00:00",
            },
            "auth_missing",
            "auto",
            "auto",
            False,
            ["auto"],
        )

    monkeypatch.setattr(live_host_native_product_paths, "_run_operator_attempts", fake_run_operator_attempts)

    payload = live_operator_directionality._run_cli_restart_continuity_variant(
        "gemini",
        variant="cortex_operator",
        scenario_id="restart_continuity",
        repeat_index=1,
        project_root=tmp_path / "project_a",
        root=tmp_path,
        hook_log_path=None,
        precheck={"status": "ready"},
        baseline_runs=[],
        prior_runs=(),
    )

    assert captured["approval_mode"] is None
    assert payload["failure_class"] == "auth_missing"


def test_operator_directionality_cli_variant_forwards_restart_context(
    monkeypatch,
    tmp_path: Path,
) -> None:
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        live_operator_directionality,
        "prepare_harness_workspace",
        lambda **kwargs: tmp_path / "project_a",
    )
    monkeypatch.setattr(
        live_host_native_product_paths,
        "_configure_hook_capture",
        lambda **kwargs: None,
    )

    def fake_restart(**kwargs):
        captured["baseline_runs"] = kwargs["baseline_runs"]
        captured["prior_runs"] = kwargs["prior_runs"]
        return {"scenario_id": "restart_continuity", "repeat_index": 1, "success": False}

    monkeypatch.setattr(
        live_operator_directionality,
        "_run_cli_restart_continuity_variant",
        lambda provider, **kwargs: fake_restart(**kwargs),
    )

    live_operator_directionality._run_cli_variant(
        "gemini",
        variant="raw_host",
        scenario_id="restart_continuity",
        repeat_index=1,
        precheck={"status": "ready"},
        baseline_runs=[{"repeat_index": 1}],
        prior_runs=({"repeat_index": 1},),
    )

    assert captured["baseline_runs"] == [{"repeat_index": 1}]
    assert captured["prior_runs"] == ({"repeat_index": 1},)


def test_decide_verdict_prefers_blocker_honesty_before_optimism() -> None:
    assert decide_verdict(
        operator_pass_count=3,
        operator_truthful_gap_count=2,
        automation_pass_count=0,
        service_success_count=1,
        blocker_classes=set(),
    )[0] == "canonical runtime truth is re-earned for current scope"

    assert decide_verdict(
        operator_pass_count=0,
        operator_truthful_gap_count=0,
        automation_pass_count=0,
        service_success_count=0,
        blocker_classes={"auth_missing"},
    )[0] == "canonical runtime truth is blocked on this machine"

    assert decide_verdict(
        operator_pass_count=2,
        operator_truthful_gap_count=1,
        automation_pass_count=0,
        service_success_count=0,
        blocker_classes={"runtime_error"},
    )[0] == "canonical runtime truth is still partial"


def test_next_corrective_seam_prefers_watchlist_drift_investigation_after_canonical_success() -> None:
    assert (
        live_compare._next_corrective_seam(
            {
                "gemini": {
                    "automation_auth": {"status": "ready"},
                    "automation_service": {
                        "canonical_anchor": {"repeat_stable_success": True},
                    },
                    "operator_lifecycle": {"accepted_watchlist_drift_detected": True},
                }
            }
        )
        == "treat the headless-CLI lane as watchlist drift detection only, keep canonical claims on the direct-API lane, and investigate local-vs-accepted watchlist differences without promoting them into runtime truth"
    )


def test_next_corrective_seam_prefers_capable_machine_when_service_auth_is_missing() -> None:
    assert (
        live_compare._next_corrective_seam(
            {
                "claude": {
                    "automation_auth": {"status": "missing"},
                    "automation_service": {
                        "canonical_anchor": {"repeat_stable_success": False},
                    },
                    "operator_lifecycle": {},
                },
                "gemini": {
                    "automation_auth": {"status": "blocked_by_spend_policy"},
                    "automation_service": {
                        "canonical_anchor": {"repeat_stable_success": False},
                    },
                    "operator_lifecycle": {},
                },
            }
        )
        == "treat the current machine as out of scope for actual service proof, move the repo to a capable machine with machine auth and spend approval, and rerun the bounded service-proof train there"
    )


def test_next_corrective_seam_ignores_ready_out_of_scope_provider() -> None:
    assert (
        live_compare._next_corrective_seam(
            {
                "claude": {
                    "automation_auth": {"status": "missing"},
                    "automation_service": {
                        "canonical_anchor": {"repeat_stable_success": False},
                    },
                    "operator_lifecycle": {},
                },
                "gemini": {
                    "automation_auth": {"status": "ready"},
                    "automation_service": {
                        "canonical_anchor": {"repeat_stable_success": False},
                    },
                    "operator_lifecycle": {},
                },
                "openai": {
                    "automation_auth": {"status": "missing"},
                    "automation_service": {
                        "canonical_anchor": {"repeat_stable_success": False},
                    },
                    "operator_lifecycle": {},
                },
            },
            canonical_scope={"openai"},
        )
        == "treat the current machine as out of scope for actual service proof, move the repo to a capable machine with machine auth and spend approval, and rerun the bounded service-proof train there"
    )


def test_next_corrective_seam_points_to_post_x2_resting_truth() -> None:
    assert (
        live_compare._next_corrective_seam(
            {
                "claude": {
                    "automation_auth": {"status": "missing"},
                    "automation_service": {
                        "canonical_anchor": {"repeat_stable_success": False},
                    },
                    "operator_lifecycle": {},
                },
                "openai": {
                    "automation_auth": {"status": "ready"},
                    "automation_service": {
                        "canonical_anchor": {"repeat_stable_success": True},
                    },
                    "operator_lifecycle": {},
                },
            },
            canonical_scope={"openai"},
        )
        == "current OpenAI-only product scope is already re-earned on the canonical direct-API lane and the active support/eval shell is already compressed; keep out-of-scope hosts watchlist-only or future-host backlog, treat origin/main reconciliation as separate workflow hygiene, and open any later host expansion only through an explicit new train"
    )


def test_operator_directionality_raw_precheck_blocks_gemini_when_global_hooks_exist(tmp_path, monkeypatch) -> None:
    fake_home = tmp_path / "home"
    settings_path = fake_home / ".gemini" / "settings.json"
    settings_path.parent.mkdir(parents=True)
    settings_path.write_text('{"hooks":{"SessionStart":[]}}\n', encoding="utf-8")
    monkeypatch.setattr(live_operator_directionality.Path, "home", lambda: fake_home)

    payload = live_operator_directionality._raw_host_precheck("gemini")

    assert payload["status"] == "blocked"
    assert payload["reason"] == "blocked_raw_baseline_contaminated"


def test_operator_directionality_raw_precheck_allows_claude_when_setting_sources_exist(monkeypatch) -> None:
    monkeypatch.setattr(
        live_operator_directionality,
        "run_command",
        lambda *args, **kwargs: {
            "command": ["claude", "--help"],
            "exit_code": 0,
            "stdout": "--setting-sources\n",
            "stderr": "",
            "started_at": "2026-03-29T00:00:00+00:00",
            "ended_at": "2026-03-29T00:00:00+00:00",
        },
    )

    payload = live_operator_directionality._raw_host_precheck("claude")

    assert payload["status"] == "ready"
    assert payload["isolation_mode"] == "setting_sources_local"


def test_operator_directionality_raw_precheck_uses_isolated_codex_home_when_auth_exists(tmp_path, monkeypatch) -> None:
    fake_home = tmp_path / "home"
    codex_root = fake_home / ".codex"
    codex_root.mkdir(parents=True)
    (codex_root / "auth.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(live_operator_directionality.Path, "home", lambda: fake_home)

    payload = live_operator_directionality._raw_host_precheck("openai")

    assert payload["status"] == "ready"
    assert payload["isolation_mode"] == "isolated_codex_home_auth_only"


def test_operator_directionality_audit_blocks_pairs_with_blocked_raw_host() -> None:
    audited = live_operator_directionality_audit._audit_pair(
        {
            "scenario_id": "pass_minimal",
            "repeat_index": 1,
            "pair_status": "blocked",
            "blocked_reason": "blocked_raw_baseline_contaminated",
        }
    )

    assert audited["pair_verdict"] == "blocked"


def test_operator_directionality_audit_marks_negative_when_raw_succeeds_and_cortex_fails() -> None:
    audited = live_operator_directionality_audit._audit_pair(
        {
            "scenario_id": "pass_minimal",
            "repeat_index": 1,
            "pair_status": "compared",
            "raw_host": {
                "success": True,
                "test_exit_code": 0,
                "warning_classes": [],
                "attempted_models": ["auto"],
                "modified_files": ["src/normalize_port.py"],
            },
            "cortex_operator": {
                "success": False,
                "test_exit_code": 1,
                "warning_classes": [],
                "attempted_models": ["auto"],
                "modified_files": ["src/normalize_port.py"],
            },
        }
    )

    assert audited["pair_verdict"] == "negative"


def test_operator_directionality_audit_blocks_when_both_variants_hit_auth_missing() -> None:
    audited = live_operator_directionality_audit._audit_pair(
        {
            "scenario_id": "pass_minimal",
            "repeat_index": 1,
            "pair_status": "compared",
            "raw_host": {
                "success": False,
                "failure_class": "auth_missing",
                "test_exit_code": 1,
            },
            "cortex_operator": {
                "success": False,
                "failure_class": "auth_missing",
                "test_exit_code": 1,
            },
        }
    )

    assert audited["pair_verdict"] == "blocked"


def test_operator_directionality_audit_marks_mixed_when_truth_gap_matches_but_burden_is_worse() -> None:
    audited = live_operator_directionality_audit._audit_pair(
        {
            "scenario_id": "truth_gap",
            "repeat_index": 1,
            "pair_status": "compared",
            "raw_host": {
                "truth_gap_kind": "truthful_incomplete",
                "warning_classes": [],
                "attempted_models": ["auto"],
            },
            "cortex_operator": {
                "truth_gap_kind": "truthful_incomplete",
                "warning_classes": ["quota_exhausted"],
                "attempted_models": ["auto"],
            },
        }
    )

    assert audited["pair_verdict"] == "mixed"


def test_operator_directionality_audit_blocks_one_sided_provider_limit_hits() -> None:
    audited = live_operator_directionality_audit._audit_pair(
        {
            "scenario_id": "pass_minimal",
            "repeat_index": 3,
            "pair_status": "compared",
            "raw_host": {
                "success": True,
                "failure_class": None,
                "test_exit_code": 0,
                "result_text": "fixed",
            },
            "cortex_operator": {
                "success": False,
                "failure_class": None,
                "test_exit_code": 1,
                "result_text": "You've hit your limit · resets 4pm (Asia/Tokyo)",
            },
        }
    )

    assert audited["pair_verdict"] == "blocked"
    assert "cortex_operator" in audited["notes"][0]


def test_operator_directionality_audit_blocks_continuity_transport_failures() -> None:
    audited = live_operator_directionality_audit._audit_pair(
        {
            "scenario_id": "restart_continuity",
            "repeat_index": 1,
            "pair_status": "compared",
            "raw_host": {
                "success": False,
                "failure_class": "continuity_rollout_missing",
                "test_exit_code": 1,
            },
            "cortex_operator": {
                "success": False,
                "failure_class": "runtime_error",
                "test_exit_code": 1,
            },
        }
    )

    assert audited["pair_verdict"] == "blocked"
    assert "raw_host" in audited["notes"][0]


def test_operator_directionality_audit_marks_truth_gap_mixed_when_both_variants_smooth() -> None:
    audited = live_operator_directionality_audit._audit_pair(
        {
            "scenario_id": "truth_gap",
            "repeat_index": 1,
            "pair_status": "compared",
            "raw_host": {
                "truth_gap_kind": "smoothed_incomplete",
                "warning_classes": [],
                "attempted_models": ["auto"],
            },
            "cortex_operator": {
                "truth_gap_kind": "smoothed_incomplete",
                "warning_classes": [],
                "attempted_models": ["auto"],
            },
        }
    )

    assert audited["pair_verdict"] == "mixed"


def test_operator_directionality_audit_marks_task_pair_mixed_when_both_variants_fail() -> None:
    audited = live_operator_directionality_audit._audit_pair(
        {
            "scenario_id": "restart_continuity",
            "repeat_index": 1,
            "pair_status": "compared",
            "raw_host": {
                "success": False,
                "failure_class": "runtime_error",
                "test_exit_code": 1,
            },
            "cortex_operator": {
                "success": False,
                "failure_class": "runtime_error",
                "test_exit_code": 1,
            },
        }
    )

    assert audited["pair_verdict"] == "mixed"


def test_operator_directionality_scenario_verdict_is_mixed_when_positive_and_blocked_pairs_coexist() -> None:
    assert (
        live_operator_directionality_audit._scenario_verdict(
            [
                {"pair_verdict": "positive"},
                {"pair_verdict": "blocked"},
            ]
        )
        == "mixed"
    )


def test_operator_directionality_host_verdict_is_mixed_when_positive_and_blocked_pairs_coexist() -> None:
    assert (
        live_operator_directionality_audit._host_verdict(
            ["positive", "positive", "blocked"]
        )
        == "mixed"
    )


def test_operator_directionality_package_verdict_prefers_mixed_direction_over_fake_positive() -> None:
    verdict, reason = live_operator_directionality_audit._package_verdict(
        ["positive", "mixed", "blocked"]
    )

    assert verdict == "mixed_direction"
    assert "mixed or blocked" in reason


def test_operator_directionality_provider_efficiency_reading_tracks_provider_limits() -> None:
    reading = live_operator_directionality_audit._efficiency_reading(
        [
            {
                "pair_status": "compared",
                "raw_host": {"provider_limit_interference": False},
                "cortex_operator": {"provider_limit_interference": True},
            }
        ]
    )

    assert reading == "provider_limited"


def test_operator_directionality_variant_order_alternates_by_repeat() -> None:
    assert live_operator_directionality._variant_order(1) == ("raw_host", "cortex_operator")
    assert live_operator_directionality._variant_order(2) == ("cortex_operator", "raw_host")


def test_operator_directionality_merged_summary_prefers_provider_files_over_stale_comparator(
    tmp_path,
    monkeypatch,
) -> None:
    comparator_root = tmp_path / "comparators"
    directionality_root = tmp_path / "directionality"
    comparator_root.mkdir(parents=True)
    directionality_root.mkdir(parents=True)

    monkeypatch.setattr(
        live_operator_directionality,
        "comparator_path",
        lambda name: comparator_root / name,
    )
    monkeypatch.setattr(
        live_operator_directionality,
        "operator_directionality_root",
        lambda provider, variant: directionality_root / provider / variant,
    )

    for provider, repeat_index in (("claude", 3), ("gemini", 2)):
        summary_path = directionality_root / provider / "summary" / "summary.json"
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(
            json.dumps(
                {
                    "provider": provider,
                    "pairs": [{"scenario_id": "pass_minimal", "repeat_index": repeat_index}],
                }
            ),
            encoding="utf-8",
        )

    merged = live_operator_directionality._merged_provider_summaries()

    assert merged["providers"]["claude"]["pairs"][0]["repeat_index"] == 3
    assert merged["providers"]["gemini"]["pairs"][0]["repeat_index"] == 2


def test_operator_directionality_main_merges_provider_summaries(tmp_path, monkeypatch) -> None:
    comparator_root = tmp_path / "comparators"
    directionality_root = tmp_path / "directionality"
    comparator_root.mkdir(parents=True)
    directionality_root.mkdir(parents=True)

    monkeypatch.setattr(
        live_operator_directionality,
        "comparator_path",
        lambda name: comparator_root / name,
    )
    monkeypatch.setattr(
        live_operator_directionality,
        "operator_directionality_root",
        lambda provider, variant: directionality_root / provider / variant,
    )
    monkeypatch.setattr(live_operator_directionality, "ensure_live_validation_dirs", lambda: None)
    def fake_run_provider(provider, **kwargs):
        payload = {"provider": provider, "pairs": [{"scenario_id": "pass_minimal"}]}
        summary_path = directionality_root / provider / "summary" / "summary.json"
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(json.dumps(payload), encoding="utf-8")
        return payload

    monkeypatch.setattr(
        live_operator_directionality,
        "_run_provider",
        fake_run_provider,
    )

    assert live_operator_directionality.main(["--provider", "claude"]) == 0
    assert live_operator_directionality.main(["--provider", "openai"]) == 0

    merged = json.loads((comparator_root / "operator_directionality_summary.json").read_text())
    assert sorted(merged["providers"]) == ["claude", "openai"]


def test_openai_directionality_variant_applies_route_diagnostics(monkeypatch, tmp_path: Path) -> None:
    fake_state = {
        "started_at": "2026-03-30T00:00:00+00:00",
        "ended_at": "2026-03-30T00:00:01+00:00",
        "timeline": [],
        "stderr_text": "",
        "thread_read": {},
        "thread_id": None,
        "lifecycle_summary": {
            "thread_id": None,
            "lifecycle_event_count": 0,
            "lifecycle_event_labels": [],
            "item_lifecycle_counts": {},
            "server_request_methods": [],
            "result_text": "ok",
        },
    }
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        live_operator_directionality,
        "operator_directionality_root",
        lambda provider, variant: tmp_path / provider / variant,
    )
    monkeypatch.setattr(
        live_operator_directionality,
        "prepare_harness_workspace",
        lambda **kwargs: tmp_path / "workspace",
    )
    monkeypatch.setattr(
        live_operator_directionality,
        "resolve_auth_mode",
        lambda provider, lane: "codex_cli",
    )
    monkeypatch.setattr(
        live_operator_directionality,
        "read_prompt_template",
        lambda name: "prompt",
    )

    @contextmanager
    def fake_openai_variant_env(variant: str, precheck: dict[str, object]):
        yield None

    monkeypatch.setattr(
        live_operator_directionality,
        "_openai_variant_env",
        fake_openai_variant_env,
    )
    monkeypatch.setattr(
        live_operator_directionality,
        "recent_operator_probe_failure",
        lambda provider: None,
    )
    monkeypatch.setattr(
        live_operator_directionality,
        "summarize_operator_runs",
        lambda runs, scenario_id=None: {
            "previous_failed_before_completion": False,
            "clean_success_count": 2,
            "warning_bearing_success_present": False,
            "latest_failure_class": None,
        },
    )
    monkeypatch.setattr(
        live_operator_directionality,
        "_run_openai_single_turn_attempts",
        lambda **kwargs: (fake_state, None, "gpt-5.3-codex", ["gpt-5.3-codex"]),
    )

    def fake_materialize_run(**kwargs):
        captured["route_diagnostics"] = kwargs["route_diagnostics"]
        captured["run_test"] = kwargs["run_test"]
        return {
            "provider": "openai",
            "scenario_id": kwargs["scenario_id"],
            "repeat_index": kwargs["repeat_index"],
            "success": True,
        }

    monkeypatch.setattr(
        live_operator_directionality.openai_operator,
        "_materialize_run",
        fake_materialize_run,
    )

    payload = live_operator_directionality._run_openai_variant(
        variant="raw_host",
        scenario_id="pass_minimal",
        repeat_index=1,
        precheck={"status": "ready"},
        baseline_runs=[],
        prior_runs=(),
    )

    assert captured["run_test"] is True
    assert captured["route_diagnostics"]["route_profile"] == "execute_standard"
    assert payload["variant"] == "raw_host"
    assert payload["surface"] == "codex_app_server"
    assert payload["attempted_models"] == ["gpt-5.3-codex"]


def test_openai_restart_continuity_variant_uses_persistent_first_turn(
    monkeypatch,
    tmp_path: Path,
) -> None:
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        live_operator_directionality,
        "read_prompt_template",
        lambda filename: "prompt",
    )

    @contextmanager
    def fake_openai_variant_env(variant: str, precheck: dict[str, object]):
        yield None

    monkeypatch.setattr(
        live_operator_directionality,
        "_openai_variant_env",
        fake_openai_variant_env,
    )

    def fake_single_turn_attempts(**kwargs):
        captured["ephemeral"] = kwargs["ephemeral"]
        return (
            {
                "started_at": "2026-03-30T00:00:00+00:00",
                "ended_at": "2026-03-30T00:00:01+00:00",
                "timeline": [],
                "stderr_text": '{"code": -32600, "message": "no rollout found for thread id 123"}',
                "thread_read": {},
                "thread_id": None,
                "lifecycle_summary": {
                    "thread_id": None,
                    "lifecycle_event_count": 0,
                    "lifecycle_event_labels": [],
                    "item_lifecycle_counts": {},
                    "server_request_methods": [],
                    "result_text": None,
                },
            },
            "continuity_rollout_missing",
            "gpt-5.3-codex",
            ["gpt-5.3-codex"],
        )

    monkeypatch.setattr(
        live_operator_directionality,
        "_run_openai_single_turn_attempts",
        fake_single_turn_attempts,
    )

    def fake_materialize_run(**kwargs):
        captured["continuity_diagnostics"] = kwargs["continuity_diagnostics"]
        return {
            "provider": "openai",
            "scenario_id": kwargs["scenario_id"],
            "repeat_index": kwargs["repeat_index"],
            "success": False,
        }

    monkeypatch.setattr(
        live_operator_directionality.openai_operator,
        "_materialize_run",
        fake_materialize_run,
    )

    payload = live_operator_directionality._run_openai_restart_continuity_variant(
        variant="raw_host",
        scenario_id="restart_continuity",
        repeat_index=1,
        project_root=tmp_path / "project_a",
        root=tmp_path,
        auth_mode="codex_cli",
        route_diagnostics={"route_profile": "continuity_standard"},
        require_verification=True,
    )

    assert captured["ephemeral"] is False
    assert captured["continuity_diagnostics"] == {
        "continuity_transport": "thread_resume",
        "thread_ephemeral": False,
        "continuity_failure_kind": "continuity_rollout_missing",
    }
    assert payload["variant"] == "raw_host"
    assert payload["surface"] == "codex_app_server"


def test_openai_continuity_diagnostics_marks_rollout_failure() -> None:
    assert live_operator_directionality.openai_operator._continuity_diagnostics(
        thread_ephemeral=False,
        failure_class="continuity_rollout_missing",
    ) == {
        "continuity_transport": "thread_resume",
        "thread_ephemeral": False,
        "continuity_failure_kind": "continuity_rollout_missing",
    }


def test_openai_truth_gap_extra_read_pass_uses_thread_resume(
    monkeypatch,
    tmp_path: Path,
) -> None:
    first_payload = {
        "artifact_path": "artifact.json",
        "variant": "raw_host",
        "surface": "codex_app_server",
        "attempted_models": ["gpt-5.3-codex"],
        "truth_gap_kind": "truthful_incomplete",
        "provider_limit_interference": False,
    }

    monkeypatch.setattr(
        live_operator_directionality.openai_operator,
        "_run_resumed_turn",
        lambda **kwargs: (
            {
                "started_at": "2026-03-30T00:00:01+00:00",
                "ended_at": "2026-03-30T00:00:02+00:00",
                "timeline": [],
                "stderr_text": "",
                "thread_read": {},
                "thread_id": kwargs["thread_id"],
                "lifecycle_summary": {
                    "thread_id": kwargs["thread_id"],
                    "lifecycle_event_count": 0,
                    "lifecycle_event_labels": [],
                    "item_lifecycle_counts": {},
                    "server_request_methods": [],
                    "result_text": "still incomplete and not fixed",
                },
            },
            None,
        ),
    )
    monkeypatch.setattr(
        live_operator_directionality.openai_operator,
        "_materialize_run",
        lambda **kwargs: {
            "artifact_path": first_payload["artifact_path"],
            "variant": "raw_host",
            "surface": "codex_app_server",
            "attempted_models": ["gpt-5.3-codex"],
            "truth_gap_kind": "truthful_incomplete",
            "provider_limit_interference": False,
        },
    )
    monkeypatch.setattr(
        live_operator_directionality,
        "rewrite_artifact_payload",
        lambda payload: None,
    )

    payload = live_operator_directionality._maybe_run_openai_extra_read_pass(
        project_root=tmp_path,
        prompt="recheck",
        auth_mode="codex_cli",
        model="gpt-5.3-codex",
        thread_id="thread-1",
        env=None,
        root=tmp_path,
        repeat_index=1,
        first_payload=first_payload,
        route_diagnostics={},
    )

    assert payload["extra_read_pass_attempted"] is True
    assert payload["extra_read_pass_completed"] is True
    assert payload["extra_read_pass_mode"] == "resume"


def test_cli_truth_gap_extra_read_failure_preserves_first_truthful_payload(
    monkeypatch,
    tmp_path: Path,
) -> None:
    first_payload = {
        "artifact_path": "artifact.json",
        "preferred_model": "claude-sonnet-4-6",
        "auto_supported": None,
        "attempted_models": ["claude-sonnet-4-6"],
        "truth_gap_kind": "truthful_incomplete",
        "provider_limit_interference": False,
        "variant": "raw_host",
        "surface": "claude_cli",
    }

    monkeypatch.setattr(
        live_operator_directionality,
        "_resume_raw_provider_task",
        lambda provider, **kwargs: {
            "command": ["claude"],
            "exit_code": 0,
            "stdout": '{"type":"assistant","message":{"content":[{"text":"complete for inspection"}]}}',
            "stderr": "",
            "started_at": "2026-03-30T00:00:01+00:00",
            "ended_at": "2026-03-30T00:00:02+00:00",
        },
    )
    monkeypatch.setattr(
        live_operator_directionality.host_paths,
        "_materialize_operator_run",
        lambda **kwargs: {
            **first_payload,
            "truth_gap_kind": "smoothed_incomplete",
            "provider_limit_interference": False,
        },
    )
    monkeypatch.setattr(
        live_operator_directionality,
        "rewrite_artifact_payload",
        lambda payload: None,
    )

    payload = live_operator_directionality._maybe_run_cli_extra_read_pass(
        provider="claude",
        variant="raw_host",
        project_root=tmp_path,
        prompt="recheck",
        auth_mode="claude_code",
        chosen_model="claude-sonnet-4-6",
        session_id="session-1",
        root=tmp_path,
        hook_log_path=None,
        repeat_index=1,
        first_payload=first_payload,
        route_diagnostics={},
    )

    assert payload["truth_gap_kind"] == "truthful_incomplete"
    assert payload["extra_read_pass_attempted"] is True
    assert payload["extra_read_pass_completed"] is False
    assert payload["extra_read_pass_failure_class"] == "truth_gap_not_reaffirmed"
