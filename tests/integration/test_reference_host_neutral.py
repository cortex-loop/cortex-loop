"""Focused integration tests for the reference-host neutral-only slice."""

from cortex.core.dispatch import DispatchLane
from cortex.drivers.reference_host_neutral import (
    NeutralContinuationCode,
    evaluate_reference_host_neutral,
)


def test_ordinary_context_event_yields_explicit_neutral_continuation_result() -> None:
    result = evaluate_reference_host_neutral(
        "ContextLoad",
        {"session_id": " session-1 "},
    )

    assert result.dispatch_decision.lane is DispatchLane.CHEAP
    assert result.neutral_decision.allowed is True
    assert result.neutral_decision.result_code is NeutralContinuationCode.NEUTRAL_ALLOWED


def test_proposal_like_event_is_rejected_from_neutral_only_path() -> None:
    result = evaluate_reference_host_neutral(
        "ApprovalRequest",
        {"candidate_id": "candidate-1"},
    )

    assert result.dispatch_decision.lane is DispatchLane.CANDIDATE_BEARING
    assert result.neutral_decision.allowed is False
    assert (
        result.neutral_decision.result_code
        is NeutralContinuationCode.CANDIDATE_PATH_REQUIRED
    )


def test_full_commitment_event_is_rejected_from_neutral_only_path() -> None:
    result = evaluate_reference_host_neutral(
        "ApprovalResult",
        {"externally_consequential": True},
    )

    assert result.dispatch_decision.lane is DispatchLane.FULL_COMMITMENT
    assert result.neutral_decision.allowed is False
    assert (
        result.neutral_decision.result_code
        is NeutralContinuationCode.FULL_COMMITMENT_PATH_REQUIRED
    )


def test_vertical_slice_stays_observe_bind_driven_and_preserves_raw_host_metadata() -> None:
    result = evaluate_reference_host_neutral(
        "SessionStart",
        {"session_id": " session-4 "},
    )
    metadata = {
        field.key: field.value
        for field in result.bound_event.observation.event.payload_metadata
    }

    assert result.bound_event.observation.event.native_event_name == "session/start"
    assert metadata["raw_host_event_name"] == "SessionStart"
    assert metadata["session_id"] == "session-4"
    assert result.bound_event.normalized_payload == {"session_id": "session-4"}
