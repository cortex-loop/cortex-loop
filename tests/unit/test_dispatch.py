"""Unit tests for conservative event-local dispatch classification."""

import pytest

from cortex.core.dispatch import (
    DispatchDecision,
    DispatchLane,
    EvidencePlan,
    WakeDecision,
    classify_dispatch,
)
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


def test_wake_decision_requires_non_empty_reason_tags() -> None:
    direct = WakeDecision(
        full_commitment_required=False,
        reason_tags=frozenset({"proposal-surface"}),
    )
    emitted = classify_dispatch(
        _make_observation(
            native_event_name="durable-write",
            facet_tags=("durable-write",),
        )
    )

    assert direct.reason_tags == frozenset({"proposal-surface"})
    assert emitted.wake_decision.reason_tags == frozenset({"durable-write"})

    with pytest.raises(
        ValueError,
        match="reason_tags must contain only non-empty values after trimming",
    ):
        WakeDecision(
            full_commitment_required=False,
            reason_tags=frozenset({""}),
        )

    with pytest.raises(
        ValueError,
        match="reason_tags must contain only non-empty values after trimming",
    ):
        WakeDecision(
            full_commitment_required=False,
            reason_tags=frozenset({"   "}),
        )


def test_wake_decision_requires_bool_full_commitment_required() -> None:
    direct = WakeDecision(
        full_commitment_required=False,
        reason_tags=frozenset({"proposal-surface"}),
    )
    emitted = classify_dispatch(
        _make_observation(
            native_event_name="durable-write",
            facet_tags=("durable-write",),
        )
    )

    assert direct.full_commitment_required is False
    assert emitted.wake_decision.full_commitment_required is True

    with pytest.raises(
        TypeError,
        match="full_commitment_required must be bool, got str",
    ):
        WakeDecision(full_commitment_required="yes")


def test_evidence_plan_requires_bool_fields() -> None:
    direct = EvidencePlan(
        requires_candidate_extraction=True,
        requires_provenance=False,
        requires_boundary_assessment=False,
    )
    emitted = classify_dispatch(_make_observation(native_event_name="stream/token"))

    assert direct.requires_candidate_extraction is True
    assert emitted.evidence_plan.requires_candidate_extraction is False
    assert emitted.evidence_plan.requires_provenance is False
    assert emitted.evidence_plan.requires_boundary_assessment is False

    with pytest.raises(
        TypeError,
        match="requires_candidate_extraction must be bool, got str",
    ):
        EvidencePlan(
            requires_candidate_extraction="yes",
            requires_provenance=False,
            requires_boundary_assessment=False,
        )

    with pytest.raises(
        TypeError,
        match="requires_provenance must be bool, got int",
    ):
        EvidencePlan(
            requires_candidate_extraction=False,
            requires_provenance=1,
            requires_boundary_assessment=False,
        )

    with pytest.raises(
        TypeError,
        match="requires_boundary_assessment must be bool, got str",
    ):
        EvidencePlan(
            requires_candidate_extraction=False,
            requires_provenance=False,
            requires_boundary_assessment="no",
        )


def test_dispatch_decision_requires_typed_wake_decision() -> None:
    direct = DispatchDecision(
        lane=DispatchLane.CHEAP,
        wake_decision=WakeDecision(full_commitment_required=False, reason_tags=frozenset()),
        evidence_plan=EvidencePlan(False, False, False),
        candidate_present=False,
    )
    emitted = classify_dispatch(_make_observation(native_event_name="stream/token"))

    assert direct.wake_decision.full_commitment_required is False
    assert emitted.wake_decision.reason_tags == frozenset()

    with pytest.raises(
        TypeError,
        match="wake_decision must be WakeDecision, got str",
    ):
        DispatchDecision(
            lane=DispatchLane.CHEAP,
            wake_decision="not-a-wake",
            evidence_plan=EvidencePlan(False, False, False),
            candidate_present=False,
        )


def test_dispatch_decision_requires_typed_evidence_plan() -> None:
    direct = DispatchDecision(
        lane=DispatchLane.CHEAP,
        wake_decision=WakeDecision(full_commitment_required=False, reason_tags=frozenset()),
        evidence_plan=EvidencePlan(False, False, False),
        candidate_present=False,
    )
    emitted = classify_dispatch(_make_observation(native_event_name="stream/token"))

    assert direct.evidence_plan.requires_candidate_extraction is False
    assert emitted.evidence_plan.requires_candidate_extraction is False
    assert emitted.evidence_plan.requires_provenance is False
    assert emitted.evidence_plan.requires_boundary_assessment is False

    with pytest.raises(
        TypeError,
        match="evidence_plan must be EvidencePlan, got str",
    ):
        DispatchDecision(
            lane=DispatchLane.CHEAP,
            wake_decision=WakeDecision(full_commitment_required=False, reason_tags=frozenset()),
            evidence_plan="not-a-plan",
            candidate_present=False,
        )


def test_dispatch_decision_requires_bool_candidate_present() -> None:
    direct = DispatchDecision(
        lane=DispatchLane.CHEAP,
        wake_decision=WakeDecision(full_commitment_required=False, reason_tags=frozenset()),
        evidence_plan=EvidencePlan(False, False, False),
        candidate_present=False,
    )
    emitted = classify_dispatch(_make_observation(native_event_name="stream/token"))

    assert direct.candidate_present is False
    assert emitted.candidate_present is False

    with pytest.raises(
        TypeError,
        match="candidate_present must be bool, got str",
    ):
        DispatchDecision(
            lane=DispatchLane.CHEAP,
            wake_decision=WakeDecision(full_commitment_required=False, reason_tags=frozenset()),
            evidence_plan=EvidencePlan(False, False, False),
            candidate_present="yes",
        )


def test_dispatch_decision_requires_canonical_commitment_carrier_source() -> None:
    direct = DispatchDecision(
        lane=DispatchLane.CHEAP,
        wake_decision=WakeDecision(full_commitment_required=False, reason_tags=frozenset()),
        evidence_plan=EvidencePlan(False, False, False),
        candidate_present=False,
    )
    emitted = classify_dispatch(
        _make_observation(native_event_name="tool/post"),
        payload={"stop_fields": {"commitment": "update the repo"}},
    )

    assert direct.commitment_carrier_source == "none"
    assert emitted.commitment_carrier_source == "payload.stop_fields"

    with pytest.raises(
        ValueError,
        match="commitment_carrier_source must be one of the canonical source labels",
    ):
        DispatchDecision(
            lane=DispatchLane.CHEAP,
            wake_decision=WakeDecision(full_commitment_required=False, reason_tags=frozenset()),
            evidence_plan=EvidencePlan(False, False, False),
            candidate_present=False,
            commitment_carrier_source="mystery",
        )


def test_dispatch_decision_requires_typed_lane() -> None:
    direct = DispatchDecision(
        lane=DispatchLane.CHEAP,
        wake_decision=WakeDecision(full_commitment_required=False, reason_tags=frozenset()),
        evidence_plan=EvidencePlan(False, False, False),
        candidate_present=False,
    )
    emitted = classify_dispatch(_make_observation(native_event_name="stream/token"))

    assert direct.lane is DispatchLane.CHEAP
    assert emitted.lane is DispatchLane.CHEAP

    with pytest.raises(
        TypeError,
        match="lane must be DispatchLane, got str",
    ):
        DispatchDecision(
            lane="cheap",
            wake_decision=WakeDecision(full_commitment_required=False, reason_tags=frozenset()),
            evidence_plan=EvidencePlan(False, False, False),
            candidate_present=False,
        )


def test_dispatch_decision_requires_bool_structured_payload_violation() -> None:
    direct = DispatchDecision(
        lane=DispatchLane.CHEAP,
        wake_decision=WakeDecision(full_commitment_required=False, reason_tags=frozenset()),
        evidence_plan=EvidencePlan(False, False, False),
        candidate_present=False,
        structured_payload_violation=False,
    )
    emitted = classify_dispatch(_make_observation(native_event_name="stream/token"))

    assert direct.structured_payload_violation is False
    assert emitted.structured_payload_violation is False

    with pytest.raises(
        TypeError,
        match="structured_payload_violation must be bool, got str",
    ):
        DispatchDecision(
            lane=DispatchLane.CHEAP,
            wake_decision=WakeDecision(full_commitment_required=False, reason_tags=frozenset()),
            evidence_plan=EvidencePlan(False, False, False),
            candidate_present=False,
            structured_payload_violation="yes",
        )


def test_dispatch_decision_requires_non_empty_string_warnings() -> None:
    direct = DispatchDecision(
        lane=DispatchLane.CHEAP,
        wake_decision=WakeDecision(full_commitment_required=False, reason_tags=frozenset()),
        evidence_plan=EvidencePlan(False, False, False),
        candidate_present=False,
        warnings=("warning",),
    )
    emitted = classify_dispatch(_make_observation(native_event_name="stream/token"))

    assert direct.warnings == ("warning",)
    assert emitted.warnings == ()

    with pytest.raises(
        TypeError,
        match="warnings must contain only string entries",
    ):
        DispatchDecision(
            lane=DispatchLane.CHEAP,
            wake_decision=WakeDecision(full_commitment_required=False, reason_tags=frozenset()),
            evidence_plan=EvidencePlan(False, False, False),
            candidate_present=False,
            warnings=("ok", 7),
        )

    with pytest.raises(
        ValueError,
        match="warnings must contain only non-empty strings after trimming",
    ):
        DispatchDecision(
            lane=DispatchLane.CHEAP,
            wake_decision=WakeDecision(full_commitment_required=False, reason_tags=frozenset()),
            evidence_plan=EvidencePlan(False, False, False),
            candidate_present=False,
            warnings=("   ",),
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


def test_dispatch_cannot_start_from_empty_native_event_name() -> None:
    with pytest.raises(ValueError, match="native_event_name must be non-empty after trimming"):
        _make_observation(native_event_name="")


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
