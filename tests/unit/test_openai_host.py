"""Focused tests for the OpenAI Responses observe/bind slice."""

from cortex.core.dispatch import DispatchLane, classify_dispatch
from cortex.drivers.openai_host import OPENAI_HOST_SURFACE, observe_openai_host_event


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
