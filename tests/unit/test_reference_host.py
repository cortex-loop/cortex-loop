"""Focused tests for the reference-host observe/bind slice."""

from cortex.core.dispatch import DispatchLane, classify_dispatch
from experimental.drivers.reference_host import (
    REFERENCE_HOST_SURFACE,
    observe_reference_host_event,
)


def test_alias_event_name_binds_to_canonical_core_name_and_preserves_raw_name() -> None:
    bound = observe_reference_host_event("PreToolUse", {"session_id": " session-1 "})

    metadata = {field.key: field.value for field in bound.observation.event.payload_metadata}

    assert bound.observation.event.native_event_name == "tool/pre"
    assert bound.observation.event.facet_tags == frozenset({"tool/pre"})
    assert bound.observation.event.channel_tags == frozenset({"tool"})
    assert metadata["raw_host_event_name"] == "PreToolUse"


def test_normalized_payload_trims_generic_fields_and_preserves_structured_commitment_carriers() -> None:
    bound = observe_reference_host_event(
        "tool/post",
        {
            "session_id": " session-2 ",
            "tool": " apply_patch ",
            "commitment_fields": {" claim_id ": "abc-123"},
        },
    )

    assert bound.normalized_payload["session_id"] == "session-2"
    assert bound.normalized_payload["tool_name"] == "apply_patch"
    assert bound.normalized_payload["commitment_fields"] == {"claim_id": "abc-123"}
    assert bound.normalized_payload["commitment_fields_source"] == "native"


def test_bound_event_carrier_contains_surface_observation_and_normalized_payload() -> None:
    bound = observe_reference_host_event("SessionStart", {"session_id": "session-3"})

    assert bound.lifecycle_surface is REFERENCE_HOST_SURFACE
    assert bound.observation.payload_view.payload_handle is bound.observation.event.payload_handle
    assert bound.observation.payload_view.payload_handle is not None
    assert bound.observation.payload_view.payload_handle.payload_kind == "reference-host-payload"
    assert bound.normalized_payload == {"session_id": "session-3"}
    assert bound.warnings == ()
    assert bound.lifecycle_surface.mcp_affordances == frozenset({"mcp.query"})


def test_proposal_like_raw_host_event_binds_cleanly_and_is_dispatch_ready() -> None:
    bound = observe_reference_host_event("ApprovalRequest", {"session_id": "session-4"})
    decision = classify_dispatch(
        bound.observation,
        payload=bound.normalized_payload,
        native_commitment_fields=bound.normalized_payload.get("commitment_fields"),
    )

    assert bound.observation.event.native_event_name == "approval/request"
    assert decision.lane is DispatchLane.CANDIDATE_BEARING
    assert decision.wake_decision.reason_tags == frozenset({"proposal-surface"})


def test_ordinary_context_event_binds_without_commitment_time_work() -> None:
    bound = observe_reference_host_event("ContextLoad", {"session_id": "session-5"})
    decision = classify_dispatch(
        bound.observation,
        payload=bound.normalized_payload,
        native_commitment_fields=bound.normalized_payload.get("commitment_fields"),
    )

    assert bound.observation.event.native_event_name == "context/load"
    assert decision.lane is DispatchLane.CHEAP
    assert decision.evidence_plan.requires_provenance is False
    assert decision.evidence_plan.requires_boundary_assessment is False
