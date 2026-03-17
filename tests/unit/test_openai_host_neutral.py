"""Focused tests for the OpenAI neutral-only slice."""

from cortex.core.dispatch import DispatchLane
from cortex.drivers.openai_host_neutral import (
    OpenAIHostNeutralResult,
    OpenAINeutralContinuationCode,
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
