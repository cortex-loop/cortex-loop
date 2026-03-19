"""Focused tests for the Gemini host neutral-only slice."""

import pytest

from cortex.core.dispatch import DispatchLane
from cortex.drivers.gemini_host import observe_gemini_host_event
from cortex.drivers.gemini_host_neutral import (
    GeminiHostNeutralResult,
    GeminiNeutralContinuationCode,
    GeminiNeutralContinuationDecision,
    evaluate_gemini_host_neutral,
)


def test_ordinary_gemini_streaming_event_yields_explicit_neutral_continuation_result() -> None:
    result = evaluate_gemini_host_neutral(
        "content.delta",
        {"interaction": {"id": "gm-1"}, "delta": {"type": "text"}},
    )

    assert result.dispatch_decision.lane is DispatchLane.CHEAP
    assert result.neutral_decision.allowed is True
    assert (
        result.neutral_decision.result_code
        is GeminiNeutralContinuationCode.NEUTRAL_ALLOWED
    )


def test_candidate_bearing_gemini_event_is_rejected_from_neutral_only_path() -> None:
    result = evaluate_gemini_host_neutral(
        "content.delta",
        {"stop_fields": {"claim_id": "candidate-1"}},
    )

    assert result.dispatch_decision.lane is DispatchLane.CANDIDATE_BEARING
    assert result.neutral_decision.allowed is False
    assert (
        result.neutral_decision.result_code
        is GeminiNeutralContinuationCode.CANDIDATE_PATH_REQUIRED
    )


def test_full_commitment_gemini_event_is_rejected_from_neutral_only_path() -> None:
    result = evaluate_gemini_host_neutral(
        "interaction.complete",
        {"externally_consequential": True},
    )

    assert result.dispatch_decision.lane is DispatchLane.FULL_COMMITMENT
    assert result.neutral_decision.allowed is False
    assert (
        result.neutral_decision.result_code
        is GeminiNeutralContinuationCode.FULL_COMMITMENT_PATH_REQUIRED
    )


def test_malformed_native_commitment_carrier_surfaces_warning_while_staying_full_commitment() -> None:
    result = evaluate_gemini_host_neutral(
        "interaction.complete",
        {
            "externally_consequential": True,
            "commitment_fields_source": "native",
            "commitment_fields": "not-a-mapping",
        },
    )

    assert result.dispatch_decision.lane is DispatchLane.FULL_COMMITMENT
    assert result.neutral_decision.allowed is False
    assert (
        result.neutral_decision.result_code
        is GeminiNeutralContinuationCode.FULL_COMMITMENT_PATH_REQUIRED
    )
    assert "Ignoring invalid native commitment carrier; expected an object." in result.warnings


def test_slice_stays_observe_bind_driven_and_preserves_raw_gemini_metadata_and_warnings() -> None:
    result = evaluate_gemini_host_neutral(
        "response.started",
        {"interaction": {"id": "gm-4"}},
    )
    metadata = {
        field.key: field.value
        for field in result.bound_event.observation.event.payload_metadata
    }

    assert result.bound_event.observation.event.native_event_name == "external/observation"
    assert metadata["raw_host_event_name"] == "response.started"
    assert metadata["interaction_id"] == "gm-4"
    assert result.warnings == (
        "No documented Gemini lifecycle mapping for 'response.started'; "
        "using conservative external/observation binding.",
    )


def test_empty_raw_gemini_event_name_cannot_enter_neutral_slice() -> None:
    with pytest.raises(ValueError, match="non-empty raw event name"):
        evaluate_gemini_host_neutral("", {})


def test_gemini_neutral_carriers_require_typed_components_and_clean_warnings() -> None:
    bound = observe_gemini_host_event("content.delta", {"interaction": {"id": "gm-neutral-1"}})
    result = evaluate_gemini_host_neutral("content.delta", {"interaction": {"id": "gm-neutral-2"}})

    decision = GeminiNeutralContinuationDecision(
        allowed=True,
        result_code=GeminiNeutralContinuationCode.NEUTRAL_ALLOWED,
    )
    assert decision.allowed is True

    with pytest.raises(
        TypeError,
        match="allowed must be bool, got str",
    ):
        GeminiNeutralContinuationDecision(
            allowed="yes",
            result_code=GeminiNeutralContinuationCode.NEUTRAL_ALLOWED,
        )

    with pytest.raises(
        TypeError,
        match="result_code must be GeminiNeutralContinuationCode, got str",
    ):
        GeminiNeutralContinuationDecision(
            allowed=True,
            result_code="neutral-allowed",
        )

    with pytest.raises(
        TypeError,
        match="bound_event must be BoundGeminiHostEvent, got str",
    ):
        GeminiHostNeutralResult(
            bound_event="not-a-bound-event",
            dispatch_decision=result.dispatch_decision,
            neutral_decision=decision,
        )

    with pytest.raises(
        TypeError,
        match="dispatch_decision must be DispatchDecision, got str",
    ):
        GeminiHostNeutralResult(
            bound_event=bound,
            dispatch_decision="not-a-dispatch",
            neutral_decision=decision,
        )

    with pytest.raises(
        TypeError,
        match="neutral_decision must be GeminiNeutralContinuationDecision, got str",
    ):
        GeminiHostNeutralResult(
            bound_event=bound,
            dispatch_decision=result.dispatch_decision,
            neutral_decision="not-a-decision",
        )

    with pytest.raises(
        ValueError,
        match="warnings must contain only non-empty values after trimming",
    ):
        GeminiHostNeutralResult(
            bound_event=bound,
            dispatch_decision=result.dispatch_decision,
            neutral_decision=decision,
            warnings=("   ",),
        )
