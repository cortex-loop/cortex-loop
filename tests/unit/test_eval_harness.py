"""Unit tests for the minimal contradiction-preserving eval harness."""

import pytest

from cortex.core.commitments import CommitmentStatus
from cortex.core.errors import ContradictionRecord, DegradationRecord
from cortex.eval.artifacts import BlockerFragment, CurrentPairFragment, EventTraceArtifact
from cortex.eval.harness import EvaluationHarnessResult, build_evaluation_harness_result


def test_harness_result_carries_current_pair_without_losing_refs() -> None:
    contradiction = ContradictionRecord(
        source_tag="trace-artifact",
        summary="trace and record set disagree",
        evidence_tags=frozenset({"trace", "record"}),
    )
    degradation = DegradationRecord(
        reason_code="partial-evidence",
        capability_tags=frozenset({"trace"}),
        contradiction_records=(contradiction,),
    )
    trace = EventTraceArtifact(
        trace_id="trace-1",
        event_refs=("event-1",),
        contradiction_refs=(contradiction,),
        degradation_refs=(degradation,),
    )
    current_pair = CurrentPairFragment(
        event_trace=trace,
        verdict_status=CommitmentStatus.UNCERTIFIED,
        candidate_id="candidate-1",
        verdict_reason_code="insufficient-evidence",
        contradiction_refs=(contradiction,),
        degradation_refs=(degradation,),
    )

    result = build_evaluation_harness_result(
        event_trace=trace,
        current_pair=current_pair,
        contradiction_refs=(contradiction,),
        degradation_refs=(degradation,),
        warnings=("artifact set is incomplete",),
    )

    assert result.event_trace is trace
    assert result.current_pair is current_pair
    assert result.blocker is None
    assert result.contradiction_refs == (contradiction,)
    assert result.degradation_refs == (degradation,)
    assert result.warnings == ("artifact set is incomplete",)


def test_harness_result_carries_blocker_without_smoothing_blocker_truth() -> None:
    contradiction = ContradictionRecord(
        source_tag="boundary-check",
        summary="boundary check conflicts with visible approval state",
        evidence_tags=frozenset({"boundary", "approval"}),
    )
    degradation = DegradationRecord(
        reason_code="boundary-evidence-partial",
        capability_tags=frozenset({"boundary"}),
        contradiction_records=(contradiction,),
    )
    trace = EventTraceArtifact(trace_id="trace-2", event_refs=("event-2",))
    blocker = BlockerFragment(
        reason_code="approval-required",
        boundary_tags=frozenset({"external-boundary"}),
        capability_tags=frozenset({"approval"}),
        contradiction_refs=(contradiction,),
        degradation_refs=(degradation,),
    )

    result = build_evaluation_harness_result(
        event_trace=trace,
        blocker=blocker,
        contradiction_refs=(contradiction,),
        degradation_refs=(degradation,),
    )

    assert result.event_trace is trace
    assert result.current_pair is None
    assert result.blocker is blocker
    assert result.blocker.reason_code == "approval-required"
    assert result.blocker.contradiction_refs == (contradiction,)
    assert result.degradation_refs == (degradation,)


def test_harness_requires_exactly_one_outcome_fragment() -> None:
    trace = EventTraceArtifact(trace_id="trace-3")
    current_pair = CurrentPairFragment(
        event_trace=trace,
        verdict_status=CommitmentStatus.CERTIFIED,
        candidate_id="candidate-3",
    )
    blocker = BlockerFragment(reason_code="blocked")

    with pytest.raises(ValueError, match="exactly one"):
        build_evaluation_harness_result(event_trace=trace)

    with pytest.raises(ValueError, match="exactly one"):
        build_evaluation_harness_result(
            event_trace=trace,
            current_pair=current_pair,
            blocker=blocker,
        )


def test_harness_rejects_mismatched_current_pair_event_trace() -> None:
    trace = EventTraceArtifact(trace_id="trace-a", event_refs=("event-a",))
    mismatched_trace = EventTraceArtifact(trace_id="trace-b", event_refs=("event-b",))
    current_pair = CurrentPairFragment(
        event_trace=mismatched_trace,
        verdict_status=CommitmentStatus.CERTIFIED,
        candidate_id="candidate-mismatch",
    )

    with pytest.raises(ValueError, match="current_pair\\.event_trace must match event_trace"):
        build_evaluation_harness_result(
            event_trace=trace,
            current_pair=current_pair,
        )


def test_harness_rejects_blocked_current_pair_construction() -> None:
    trace = EventTraceArtifact(trace_id="trace-blocked", event_refs=("event-blocked",))
    current_pair = CurrentPairFragment(
        event_trace=trace,
        verdict_status=CommitmentStatus.BLOCKED,
        verdict_reason_code="approval-required",
    )

    with pytest.raises(
        ValueError,
        match="current_pair cannot carry CommitmentStatus\\.BLOCKED; use blocker",
    ):
        build_evaluation_harness_result(
            event_trace=trace,
            current_pair=current_pair,
        )


def test_harness_result_needs_no_publication_packet_surface() -> None:
    trace = EventTraceArtifact(trace_id="trace-4", event_refs=("event-4",))
    current_pair = CurrentPairFragment(
        event_trace=trace,
        verdict_status=CommitmentStatus.CERTIFIED,
        candidate_id="candidate-4",
    )

    result = build_evaluation_harness_result(
        event_trace=trace,
        current_pair=current_pair,
    )

    assert isinstance(result, EvaluationHarnessResult)
    assert result.current_pair is current_pair
