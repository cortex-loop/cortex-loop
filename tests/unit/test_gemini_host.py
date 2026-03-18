"""Focused tests for the Gemini host observe/bind slice."""

import pytest

from cortex.core.dispatch import DispatchLane, classify_dispatch
from cortex.drivers.gemini_host import GEMINI_HOST_SURFACE, observe_gemini_host_event


def test_documented_gemini_event_binds_to_canonical_core_name_and_preserves_raw_name() -> None:
    bound = observe_gemini_host_event(
        "content.delta",
        {"interaction": {"id": "gm-1"}, "delta": {"type": "text"}},
    )

    metadata = {field.key: field.value for field in bound.observation.event.payload_metadata}

    assert bound.observation.event.native_event_name == "external/observation"
    assert bound.observation.event.facet_tags == frozenset({"external/observation"})
    assert bound.observation.event.channel_tags == frozenset({"external"})
    assert metadata["raw_host_event_name"] == "content.delta"
    assert metadata["interaction_id"] == "gm-1"


def test_normalized_gemini_payload_preserves_stable_generic_fields_when_present() -> None:
    bound = observe_gemini_host_event(
        "content.delta",
        {
            "session_id": " session-2 ",
            "tool": " mcp.query ",
            "commitment_fields": {" claim_id ": "gm-claim"},
        },
    )

    assert bound.normalized_payload["session_id"] == "session-2"
    assert bound.normalized_payload["tool_name"] == "mcp.query"
    assert bound.normalized_payload["commitment_fields"] == {"claim_id": "gm-claim"}
    assert bound.normalized_payload["commitment_fields_source"] == "native"


def test_bound_gemini_event_contains_surface_observation_and_remains_dispatch_cheap() -> None:
    bound = observe_gemini_host_event(
        "content.delta",
        {"interaction": {"id": "gm-3"}, "delta": {"type": "text"}},
    )
    decision = classify_dispatch(
        bound.observation,
        payload=bound.normalized_payload,
        native_commitment_fields=bound.normalized_payload.get("commitment_fields"),
    )

    assert bound.lifecycle_surface is GEMINI_HOST_SURFACE
    assert bound.observation.payload_view.payload_handle is not None
    assert bound.observation.payload_view.payload_handle is bound.observation.event.payload_handle
    assert bound.observation.payload_view.payload_handle.payload_kind == "gemini-host-payload"
    assert decision.lane is DispatchLane.CHEAP


def test_gemini_surface_gap_emits_explicit_warning_instead_of_fabricated_parity() -> None:
    bound = observe_gemini_host_event("response.started", {"interaction": {"id": "gm-4"}})

    assert bound.observation.event.native_event_name == "external/observation"
    assert bound.warnings == (
        "No documented Gemini lifecycle mapping for 'response.started'; "
        "using conservative external/observation binding.",
    )


def test_empty_raw_gemini_event_name_is_rejected_before_conservative_fallback() -> None:
    with pytest.raises(ValueError, match="non-empty raw event name"):
        observe_gemini_host_event("", {})
