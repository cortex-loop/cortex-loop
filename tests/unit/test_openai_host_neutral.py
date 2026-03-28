"""Focused tests for the OpenAI neutral-only slice."""

import pytest

from cortex.core.dispatch import DispatchLane
from cortex.drivers.openai_host import observe_openai_host_event
from cortex.drivers.openai_host_neutral import (
    OpenAIHostNeutralResult,
    OpenAINeutralContinuationCode,
    OpenAINeutralContinuationDecision,
    evaluate_openai_host_neutral,
)


def test_ordinary_openai_streaming_event_yields_explicit_neutral_continuation_result() -> None:
    result = evaluate_openai_host_neutral(
        "response.output_text.delta",
        {"response_id": "oa-1", "delta": "Hello"},
    )

    assert result.dispatch_decision.lane is DispatchLane.CHEAP
    assert result.neutral_decision.allowed is True
    assert (
        result.neutral_decision.result_code
        is OpenAINeutralContinuationCode.NEUTRAL_ALLOWED
    )


def test_candidate_bearing_openai_event_is_rejected_from_neutral_only_path() -> None:
    result = evaluate_openai_host_neutral(
        "response.output_text.delta",
        {"stop_fields": {"claim_id": "candidate-1"}},
    )

    assert result.dispatch_decision.lane is DispatchLane.CANDIDATE_BEARING
    assert result.neutral_decision.allowed is False
    assert (
        result.neutral_decision.result_code
        is OpenAINeutralContinuationCode.CANDIDATE_PATH_REQUIRED
    )


def test_full_commitment_openai_event_is_rejected_from_neutral_only_path() -> None:
    result = evaluate_openai_host_neutral(
        "response.completed",
        {"externally_consequential": True},
    )

    assert result.dispatch_decision.lane is DispatchLane.FULL_COMMITMENT
    assert result.neutral_decision.allowed is False
    assert (
        result.neutral_decision.result_code
        is OpenAINeutralContinuationCode.FULL_COMMITMENT_PATH_REQUIRED
    )


def test_malformed_native_commitment_carrier_surfaces_warning_while_staying_full_commitment() -> None:
    result = evaluate_openai_host_neutral(
        "response.completed",
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
        is OpenAINeutralContinuationCode.FULL_COMMITMENT_PATH_REQUIRED
    )
    assert "Ignoring invalid native commitment carrier; expected an object." in result.warnings


def test_slice_stays_observe_bind_driven_and_preserves_raw_openai_metadata_and_warnings() -> None:
    result = evaluate_openai_host_neutral(
        "response.in_progress",
        {"response": {"id": "oa-4"}},
    )
    metadata = {
        field.key: field.value
        for field in result.bound_event.observation.event.payload_metadata
    }

    assert isinstance(result, OpenAIHostNeutralResult)
    assert result.bound_event.observation.event.native_event_name == "external/observation"
    assert metadata["raw_host_event_name"] == "response.in_progress"
    assert metadata["response_id"] == "oa-4"
    assert result.warnings == (
        "No documented OpenAI lifecycle mapping for 'response.in_progress'; "
        "using conservative external/observation binding.",
    )


def test_empty_raw_openai_event_name_cannot_enter_neutral_slice() -> None:
    with pytest.raises(ValueError, match="non-empty raw event name"):
        evaluate_openai_host_neutral("", {})


def test_openai_neutral_carriers_require_typed_components_and_clean_warnings() -> None:
    bound = observe_openai_host_event("response.output_text.delta", {"response_id": "oa-neutral-1"})
    result = evaluate_openai_host_neutral("response.output_text.delta", {"response_id": "oa-neutral-2"})

    decision = OpenAINeutralContinuationDecision(
        allowed=True,
        result_code=OpenAINeutralContinuationCode.NEUTRAL_ALLOWED,
    )
    assert decision.allowed is True

    with pytest.raises(
        TypeError,
        match="allowed must be bool, got str",
    ):
        OpenAINeutralContinuationDecision(
            allowed="yes",
            result_code=OpenAINeutralContinuationCode.NEUTRAL_ALLOWED,
        )

    with pytest.raises(
        TypeError,
        match="result_code must be OpenAINeutralContinuationCode, got str",
    ):
        OpenAINeutralContinuationDecision(
            allowed=True,
            result_code="neutral-allowed",
        )

    with pytest.raises(
        TypeError,
        match="bound_event must be BoundOpenAIHostEvent, got str",
    ):
        OpenAIHostNeutralResult(
            bound_event="not-a-bound-event",
            dispatch_decision=result.dispatch_decision,
            neutral_decision=decision,
        )

    with pytest.raises(
        TypeError,
        match="dispatch_decision must be DispatchDecision, got str",
    ):
        OpenAIHostNeutralResult(
            bound_event=bound,
            dispatch_decision="not-a-dispatch",
            neutral_decision=decision,
        )

    with pytest.raises(
        TypeError,
        match="neutral_decision must be OpenAINeutralContinuationDecision, got str",
    ):
        OpenAIHostNeutralResult(
            bound_event=bound,
            dispatch_decision=result.dispatch_decision,
            neutral_decision="not-a-decision",
        )

    with pytest.raises(
        ValueError,
        match="warnings must contain only non-empty values after trimming",
    ):
        OpenAIHostNeutralResult(
            bound_event=bound,
            dispatch_decision=result.dispatch_decision,
            neutral_decision=decision,
            warnings=("   ",),
        )

    with pytest.raises(
        TypeError,
        match="warnings must be tuple\\[str, \\.\\.\\.\\], got list",
    ):
        OpenAIHostNeutralResult(
            bound_event=bound,
            dispatch_decision=result.dispatch_decision,
            neutral_decision=decision,
            warnings=["x"],
        )
