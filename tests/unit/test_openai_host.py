"""Focused tests for the OpenAI Responses observe/bind slice."""

import pytest

from cortex.drivers.common_normalization import NormalizedDriverEvent
from cortex.core.dispatch import DispatchLane, classify_dispatch
from cortex.drivers.openai_host import (
    OPENAI_HOST_SURFACE,
    BoundOpenAIHostEvent,
    bind_openai_event_envelope,
    observe_openai_host_event,
)


def test_documented_openai_event_binds_to_canonical_core_name_and_preserves_raw_name() -> None:
    bound = observe_openai_host_event(
        "response.output_text.delta",
        {"response_id": "resp_1", "delta": "Hello"},
    )

    metadata = {field.key: field.value for field in bound.observation.event.payload_metadata}

    assert bound.observation.event.native_event_name == "external/observation"
    assert bound.observation.event.facet_tags == frozenset({"external/observation"})
    assert bound.observation.event.channel_tags == frozenset({"external"})
    assert metadata["raw_host_event_name"] == "response.output_text.delta"
    assert metadata["response_id"] == "resp_1"


def test_normalized_openai_payload_preserves_stable_generic_fields_when_present() -> None:
    bound = observe_openai_host_event(
        "response.output_text.delta",
        {
            "session_id": " session-2 ",
            "tool": " file_search ",
            "commitment_fields": {" claim_id ": "oa-claim"},
        },
    )

    assert bound.normalized_payload["session_id"] == "session-2"
    assert bound.normalized_payload["tool_name"] == "file_search"
    assert bound.normalized_payload["commitment_fields"] == {"claim_id": "oa-claim"}
    assert bound.normalized_payload["commitment_fields_source"] == "native"


def test_bound_openai_event_contains_surface_observation_and_remains_dispatch_cheap() -> None:
    bound = observe_openai_host_event(
        "response.output_text.delta",
        {"response_id": "resp_3", "delta": "Hi"},
    )
    decision = classify_dispatch(
        bound.observation,
        payload=bound.normalized_payload,
        native_commitment_fields=bound.normalized_payload.get("commitment_fields"),
    )

    assert bound.lifecycle_surface is OPENAI_HOST_SURFACE
    assert bound.observation.payload_view.payload_handle is not None
    assert bound.observation.payload_view.payload_handle is bound.observation.event.payload_handle
    assert bound.observation.payload_view.payload_handle.payload_kind == "openai-host-payload"
    assert decision.lane is DispatchLane.CHEAP


def test_openai_surface_gap_emits_explicit_warning_instead_of_fabricated_parity() -> None:
    bound = observe_openai_host_event("response.tool_event", {"response_id": "resp_4"})

    assert bound.observation.event.native_event_name == "external/observation"
    assert bound.warnings == (
        "No documented OpenAI lifecycle mapping for 'response.tool_event'; "
        "using conservative external/observation binding.",
    )


def test_empty_raw_openai_event_name_is_rejected_before_conservative_fallback() -> None:
    with pytest.raises(ValueError, match="non-empty raw event name"):
        observe_openai_host_event("", {})


def test_bound_openai_host_event_requires_typed_components() -> None:
    bound = observe_openai_host_event("response.output_text.delta", {"response_id": "oa-typed-1"})

    with pytest.raises(
        TypeError,
        match="lifecycle_surface must be LifecycleSurface, got str",
    ):
        BoundOpenAIHostEvent(
            lifecycle_surface="not-a-surface",
            observation=bound.observation,
            normalized_payload=bound.normalized_payload,
        )

    with pytest.raises(
        TypeError,
        match="observation must be ObservationBundle, got str",
    ):
        BoundOpenAIHostEvent(
            lifecycle_surface=bound.lifecycle_surface,
            observation="not-an-observation",
            normalized_payload=bound.normalized_payload,
        )

    with pytest.raises(
        TypeError,
        match="normalized_payload must be dict\\[str, Any\\], got tuple",
    ):
        BoundOpenAIHostEvent(
            lifecycle_surface=bound.lifecycle_surface,
            observation=bound.observation,
            normalized_payload=(),
        )


def test_bound_openai_host_event_requires_clean_warnings_and_typed_bind_input() -> None:
    bound = observe_openai_host_event("response.output_text.delta", {"response_id": "oa-typed-2"})
    normalized_event = NormalizedDriverEvent(
        native_event_name="response.output_text.delta",
        event_name="external/observation",
        payload={},
    )

    with pytest.raises(
        ValueError,
        match="warnings must contain only non-empty values after trimming",
    ):
        BoundOpenAIHostEvent(
            lifecycle_surface=bound.lifecycle_surface,
            observation=bound.observation,
            normalized_payload=bound.normalized_payload,
            warnings=("   ",),
        )

    with pytest.raises(
        TypeError,
        match="warnings must be tuple\\[str, \\.\\.\\.\\], got list",
    ):
        BoundOpenAIHostEvent(
            lifecycle_surface=bound.lifecycle_surface,
            observation=bound.observation,
            normalized_payload=bound.normalized_payload,
            warnings=["x"],
        )

    with pytest.raises(
        TypeError,
        match="warnings must contain only str instances, got int",
    ):
        BoundOpenAIHostEvent(
            lifecycle_surface=bound.lifecycle_surface,
            observation=bound.observation,
            normalized_payload=bound.normalized_payload,
            warnings=(1,),
        )

    envelope = bind_openai_event_envelope(normalized_event)
    assert envelope.native_event_name == "external/observation"

    with pytest.raises(
        TypeError,
        match="bind_openai_event_envelope\\.normalized_event must be NormalizedDriverEvent, got str",
    ):
        bind_openai_event_envelope("not-a-normalized-event")
