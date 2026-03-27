"""Focused tests for the L1 live-validation support harness."""

from __future__ import annotations

from tools.live_validation_common import (
    BLOCKING_FAILURE_CLASSES,
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
            '{"type":"result","result":"OK"}',
        ]
    )

    records = parse_json_lines(text)

    assert records == [
        {"type": "init", "session_id": "s-1"},
        {"type": "result", "result": "OK"},
    ]
    assert extract_event_labels(records) == ["init", "result"]
    assert extract_result_text(records, text) == "OK"


def test_build_scenario_catalog_exposes_common_and_host_tailored_rows() -> None:
    catalog = build_scenario_catalog()

    assert "claude" in catalog
    assert "gemini" in catalog
    assert "openai" in catalog
    assert any(
        row["scenario_id"] == "core_01_single_turn_summary" for row in catalog["claude"]
    )
    assert any(
        row["scenario_id"] == "claude_01_messages_shape" for row in catalog["claude"]
    )
    assert any(
        row["scenario_id"] == "gemini_01_stream_variance" for row in catalog["gemini"]
    )
    assert any(
        row["scenario_id"] == "openai_01_long_responses" for row in catalog["openai"]
    )


def test_decide_verdict_prefers_blocker_honesty_before_optimism() -> None:
    assert decide_verdict(
        provider_success_count=3,
        cortex_success_count=3,
        blocker_classes=set(),
    )[0] == "lifecycle-first is already paying off clearly"

    assert decide_verdict(
        provider_success_count=1,
        cortex_success_count=0,
        blocker_classes={"auth_missing"},
    )[0] == "lifecycle-first is not yet paying off enough on real hosts"

    assert decide_verdict(
        provider_success_count=2,
        cortex_success_count=1,
        blocker_classes={"runtime_error"},
    )[0] == "lifecycle-first is promising but under-instrumented"
