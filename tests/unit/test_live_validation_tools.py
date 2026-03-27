"""Focused tests for the L2 live-testing support harness."""

from __future__ import annotations

from tools.live_validation_common import (
    BLOCKING_FAILURE_CLASSES,
    MODEL_MATRIX,
    build_scenario_catalog,
    classify_failure,
    decide_verdict,
    extract_event_labels,
    extract_result_text,
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
    assert MODEL_MATRIX["openai"]["operator"].preferred == "gpt-5.3-codex"
    assert MODEL_MATRIX["gemini"]["operator"].fallback == "gemini-2.5-flash"


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
