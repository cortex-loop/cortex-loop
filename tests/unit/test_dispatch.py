"""Unit tests for conservative event-local dispatch classification."""

from cortex.core.dispatch import DispatchLane, classify_dispatch
from cortex.core.envelopes import LifecycleEventEnvelope, MetadataField
from cortex.core.observation import ObservationBundle, PayloadView


def test_cheap_event_stays_cheap_with_no_evidence_burden() -> None:
    decision = classify_dispatch(
        _make_observation(
            native_event_name="stream/token",
            facet_tags=("stream-token",),
            summary_tags=("read-only",),
        )
    )

    assert decision.lane is DispatchLane.CHEAP
    assert decision.wake_decision.full_commitment_required is False
    assert decision.wake_decision.reason_tags == frozenset()
    assert decision.evidence_plan.requires_candidate_extraction is False
    assert decision.evidence_plan.requires_provenance is False
    assert decision.evidence_plan.requires_boundary_assessment is False


def test_proposal_like_event_becomes_candidate_bearing() -> None:
    decision = classify_dispatch(
        _make_observation(
            native_event_name="write/proposal",
            facet_tags=("write-proposal",),
        )
    )

    assert decision.lane is DispatchLane.CANDIDATE_BEARING
    assert decision.wake_decision.full_commitment_required is False
    assert decision.wake_decision.reason_tags == frozenset({"proposal-surface"})


def test_explicit_full_commitment_wake_becomes_full_commitment() -> None:
    decision = classify_dispatch(
        _make_observation(
            native_event_name="durable-write",
            facet_tags=("durable-write",),
        )
    )

    assert decision.lane is DispatchLane.FULL_COMMITMENT
    assert decision.wake_decision.full_commitment_required is True
    assert decision.wake_decision.reason_tags == frozenset({"durable-write"})


def test_boundary_required_marker_forces_full_commitment() -> None:
    decision = classify_dispatch(
        _make_observation(
            native_event_name="tool/post",
            payload_metadata=(MetadataField("boundary_required", True),),
        )
    )

    assert decision.lane is DispatchLane.FULL_COMMITMENT
    assert decision.wake_decision.full_commitment_required is True
    assert "boundary-required" in decision.wake_decision.reason_tags


def test_candidate_presence_alone_becomes_candidate_bearing() -> None:
    decision = classify_dispatch(
        _make_observation(native_event_name="tool/post"),
        payload={"stop_fields": {"commitment": "update the repo"}},
    )

    assert decision.lane is DispatchLane.CANDIDATE_BEARING
    assert decision.candidate_present is True
    assert decision.commitment_carrier_source == "payload.stop_fields"
    assert decision.wake_decision.full_commitment_required is False
    assert decision.wake_decision.reason_tags == frozenset({"candidate-present"})


def test_candidate_presence_alone_does_not_overwake_to_full_commitment() -> None:
    decision = classify_dispatch(
        _make_observation(
            native_event_name="write/proposal",
            facet_tags=("write-proposal",),
        ),
        payload={"stop_fields": {"commitment": "update the repo"}},
    )

    assert decision.lane is DispatchLane.CANDIDATE_BEARING
    assert decision.candidate_present is True
    assert decision.commitment_carrier_source == "payload.stop_fields"
    assert decision.wake_decision.full_commitment_required is False
    assert decision.wake_decision.reason_tags == frozenset(
        {"candidate-present", "proposal-surface"}
    )


def test_evidence_plan_matches_the_dispatched_lane() -> None:
    cheap = classify_dispatch(_make_observation(native_event_name="stream/token"))
    candidate = classify_dispatch(
        _make_observation(
            native_event_name="approval/request",
            facet_tags=("approval/request",),
        )
    )
    full = classify_dispatch(
        _make_observation(
            native_event_name="task-complete",
            summary_tags=("explicit-completion-claim",),
        )
    )

    assert (
        cheap.evidence_plan.requires_candidate_extraction,
        cheap.evidence_plan.requires_provenance,
        cheap.evidence_plan.requires_boundary_assessment,
    ) == (False, False, False)
    assert (
        candidate.evidence_plan.requires_candidate_extraction,
        candidate.evidence_plan.requires_provenance,
        candidate.evidence_plan.requires_boundary_assessment,
    ) == (True, False, False)
    assert (
        full.evidence_plan.requires_candidate_extraction,
        full.evidence_plan.requires_provenance,
        full.evidence_plan.requires_boundary_assessment,
    ) == (True, True, True)


def _make_observation(
    *,
    native_event_name: str,
    facet_tags: tuple[str, ...] = (),
    summary_tags: tuple[str, ...] = (),
    payload_metadata: tuple[MetadataField, ...] = (),
) -> ObservationBundle:
    return ObservationBundle(
        event=LifecycleEventEnvelope(
            native_event_name=native_event_name,
            facet_tags=frozenset(facet_tags),
            payload_metadata=payload_metadata,
        ),
        payload_view=PayloadView(summary_tags=frozenset(summary_tags)),
    )
