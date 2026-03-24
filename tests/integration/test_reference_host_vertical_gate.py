"""Real first-host-vertical integration coverage over landed reference-host behavior."""

from __future__ import annotations

import pytest

from cortex.core.dispatch import DispatchLane, classify_dispatch
from cortex.core.environment import (
    EXECUTION_TRACE,
    ExecutiveEnvironmentView,
)
from cortex.drivers.reference_host import observe_reference_host_event
from cortex.drivers.reference_host_commitment import evaluate_reference_host_commitment
from cortex.sre.allocation import AllocationScore, AllocationScorecard
from cortex.sre.families import SoftControlFamily
from cortex.sre.policy import neutral_dominance_decision
from tests.integration._reference_lane import (
    assert_reference_candidate_bearing_without_verdict,
    assert_reference_commitment_result_preserves_degradation_pair,
    assert_reference_cheap_path_neutral_allowed,
    assert_reference_full_commitment_certified,
    cheap_path_event,
    evaluate_reference_candidate_bearing_case,
    evaluate_reference_cheap_path_case,
    evaluate_reference_full_commitment_case,
    full_commitment_event,
    host_surface_degradation_pair,
    provenance_manifest_for,
)


def test_cheap_path_integration_stays_cheap_and_neutral_allowed() -> None:
    result = evaluate_reference_cheap_path_case()

    assert_reference_cheap_path_neutral_allowed(result)


def test_candidate_bearing_integration_binds_candidate_and_returns_no_verdict() -> None:
    result = evaluate_reference_candidate_bearing_case()

    assert_reference_candidate_bearing_without_verdict(result)


def test_full_commitment_integration_reaches_certified_with_lawful_evidence() -> None:
    result = evaluate_reference_full_commitment_case(
        commitment_id="commit-1",
        provenance_reference_id="artifact-1",
    )

    assert_reference_full_commitment_certified(result)


def test_degradation_roundtrip_preserves_degradation_and_contradictions() -> None:
    contradiction, degradation = host_surface_degradation_pair(
        summary="expected write receipt was absent",
        evidence_tags=frozenset({"receipt-missing"}),
    )

    result = evaluate_reference_full_commitment_case(
        commitment_id="commit-2",
        provenance_reference_id="artifact-2",
        degradation_refs=(degradation,),
    )

    assert_reference_commitment_result_preserves_degradation_pair(
        result,
        contradiction,
        degradation,
    )


def test_firewall_integration_rejects_executive_environment_view() -> None:
    with pytest.raises(TypeError, match="CommitmentEnvironmentHandle"):
        evaluate_reference_host_commitment(
            *full_commitment_event(commitment_id="commit-3"),
            environment_handle=ExecutiveEnvironmentView(
                available_query_kinds=frozenset({EXECUTION_TRACE}),
                host_capability_tags=frozenset({"trace/read"}),
            ),
            provenance_manifest=provenance_manifest_for("artifact-3"),
        )


def test_driver_to_core_to_sre_smoke_stays_observe_bind_dispatch_and_neutral() -> None:
    event_name, payload = cheap_path_event(session_id=" session-6 ")
    bound_event = observe_reference_host_event(event_name, payload)
    dispatch_decision = classify_dispatch(
        bound_event.observation,
        payload=bound_event.normalized_payload,
        native_commitment_fields=bound_event.normalized_payload.get("commitment_fields"),
    )
    sre_decision = neutral_dominance_decision(
        AllocationScorecard(
            scores=(
                AllocationScore(SoftControlFamily.NEUTRAL, 1.0),
                AllocationScore(SoftControlFamily.CHECK, 1.05),
                AllocationScore(SoftControlFamily.SEEK_CONTEXT, 0.9),
            ),
            activation_threshold=0.1,
        )
    )
    metadata = {
        field.key: field.value
        for field in bound_event.observation.event.payload_metadata
    }

    assert dispatch_decision.lane is DispatchLane.CHEAP
    assert sre_decision.selected_family is SoftControlFamily.NEUTRAL
    assert metadata["raw_host_event_name"] == "ContextLoad"
    assert metadata["session_id"] == "session-6"
