"""Focused tests for the L2 live-testing support harness."""

from __future__ import annotations

import sys
from pathlib import Path

TOOLS_ROOT = Path(__file__).resolve().parents[2] / "tools"
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

import live_cortex_host_control as live_host_control
import live_host_native_product_paths as live_host_native_product_paths
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
    model_ladder,
    parse_json_lines,
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
    assert classify_failure("OAuth token has expired") == "auth_expired"
    assert (
        classify_failure("You have exhausted your capacity on this model.")
        == "capacity_exhausted"
    )
    assert classify_failure("Requested entity was not found.") == "model_unavailable"
    assert classify_failure("model_not_found") == "model_unavailable"
    assert classify_failure("totally different error") is None


def test_should_collapse_after_failure_matches_blocking_classes() -> None:
    for failure_class in BLOCKING_FAILURE_CLASSES:
        assert should_collapse_after_failure(failure_class) is True
    assert should_collapse_after_failure("runtime_error") is False
    assert should_collapse_after_failure(None) is False


def test_parse_json_lines_extracts_structured_records_only() -> None:
    text = '\n'.join(
        [
            '{"type":"init","session_id":"s-1"}',
            "not json",
            '{"type":"item.completed","item":{"type":"agent_message","text":"OK"}}',
        ]
    )

    records = parse_json_lines(text)

    assert records == [
        {"type": "init", "session_id": "s-1"},
        {"type": "item.completed", "item": {"type": "agent_message", "text": "OK"}},
    ]
    assert extract_event_labels(records) == ["init", "item:agent_message"]
    assert extract_result_text(records, text) == "OK"


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
    assert catalog["operator_continuity"]["turn_1_prompt"] == "restart_continuity_turn1_operator.md"
    assert catalog["host_caveats"]["claude"] == "host_caveat_operator_claude.md"
    assert catalog["host_caveats"]["openai"] == "host_caveat_operator_openai_app_server.md"
    assert catalog["openai_operator_surfaces"]["smoke"] == "codex exec"
    assert catalog["openai_operator_surfaces"]["lifecycle_proof"] == "codex app-server"
    assert catalog["gemini_operator_model_ladder"] == [
        "auto",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
    ]
    assert MODEL_MATRIX["openai"]["operator"].preferred == "gpt-5.3-codex"
    assert MODEL_MATRIX["gemini"]["operator"].preferred == "auto"
    assert MODEL_MATRIX["gemini"]["operator"].fallback == "gemini-2.5-flash"


def test_gemini_model_ladder_and_choose_model_follow_auto_then_flash_then_flash_lite() -> None:
    assert model_ladder("gemini", "operator") == GEMINI_OPERATOR_FULL_LADDER
    assert model_ladder("gemini", "operator", auto_supported=False) == (
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
    )
    assert choose_model("gemini", "operator") == "auto"
    assert choose_model("gemini", "operator", auto_supported=False) == "gemini-2.5-flash"
    assert (
        choose_model(
            "gemini",
            "operator",
            current_model="auto",
            first_failure="model_unavailable",
            auto_supported=False,
        )
        == "gemini-2.5-flash"
    )
    assert (
        choose_model(
            "gemini",
            "operator",
            current_model="auto",
            first_failure="operator_timeout",
            auto_supported=False,
        )
        == "gemini-2.5-flash"
    )
    assert (
        choose_model(
            "gemini",
            "operator",
            current_model="gemini-2.5-flash",
            first_failure="capacity_exhausted",
            auto_supported=False,
        )
        == "gemini-2.5-flash-lite"
    )


def test_automation_auth_readiness_defaults_to_missing_without_machine_creds() -> None:
    env = {}
    assert automation_auth_readiness("claude", env)["status"] == "missing"
    assert automation_auth_readiness("gemini", env)["status"] == "missing"
    assert automation_auth_readiness("openai", env)["status"] == "missing"


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
        provider_payloads={"claude": {"provider": "claude", "runs": []}},
    )

    assert summary["lane"] == "automation"
    assert summary["providers"] == {"claude": {"provider": "claude", "runs": []}}


def test_provider_baseline_requested_model_ladder_uses_current_model_matrix() -> None:
    assert live_provider_baselines._requested_model_ladder(
        provider="openai",
        lane="operator",
        preferred_model_override=None,
        fallback_model_override=None,
        disable_auto_probe=False,
    ) == ("gpt-5.3-codex", "gpt-5.4")


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
        auth_mode="google_login",
    )
    assert "-m" not in captured["product_path"]


def test_decide_verdict_prefers_blocker_honesty_before_optimism() -> None:
    assert decide_verdict(
        operator_pass_count=3,
        operator_truthful_gap_count=2,
        automation_pass_count=0,
        service_success_count=1,
        blocker_classes=set(),
    )[0] == "lifecycle-first is already paying off clearly"

    assert decide_verdict(
        operator_pass_count=0,
        operator_truthful_gap_count=0,
        automation_pass_count=0,
        service_success_count=0,
        blocker_classes={"auth_missing"},
    )[0] == "lifecycle-first is not yet paying off enough on real hosts"

    assert decide_verdict(
        operator_pass_count=2,
        operator_truthful_gap_count=1,
        automation_pass_count=0,
        service_success_count=0,
        blocker_classes={"runtime_error"},
    )[0] == "lifecycle-first is promising but under-instrumented"
