"""Unit tests for the minimal contradiction-preserving eval harness."""

import pytest

from cortex.core.commitments import CommitmentStatus
from cortex.core.errors import ContradictionRecord, DegradationRecord
from experimental.eval.artifacts import BlockerFragment, CurrentPairFragment, EventTraceArtifact
from experimental.eval.harness import EvaluationHarnessResult, build_evaluation_harness_result


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


def test_harness_result_requires_typed_members_and_clean_warnings() -> None:
    trace = EventTraceArtifact(trace_id="trace-typed", event_refs=("event-typed",))
    blocker = BlockerFragment(reason_code="approval-required")

    result = build_evaluation_harness_result(
        event_trace=trace,
        blocker=blocker,
        warnings=("typed warning",),
    )

    assert result.warnings == ("typed warning",)

    with pytest.raises(
        TypeError,
        match="EventTraceArtifact\\.event_refs must be tuple\\[str, \\.\\.\\.\\], got list",
    ):
        EventTraceArtifact(trace_id="trace-list", event_refs=["event-typed"])

    with pytest.raises(
        TypeError,
        match="BlockerFragment\\.boundary_tags must be frozenset\\[str\\], got set",
    ):
        BlockerFragment(
            reason_code="approval-required",
            boundary_tags={"boundary"},
        )

    with pytest.raises(
        TypeError,
        match="BlockerFragment\\.reason_code must be str, got int",
    ):
        BlockerFragment(reason_code=1)

    with pytest.raises(
        TypeError,
        match="EvaluationHarnessResult\\.event_trace must be EventTraceArtifact, got str",
    ):
        build_evaluation_harness_result(
            event_trace="not-a-trace",
            blocker=blocker,
        )

    with pytest.raises(
        TypeError,
        match="EvaluationHarnessResult\\.blocker must be BlockerFragment \\| None, got str",
    ):
        build_evaluation_harness_result(
            event_trace=trace,
            blocker="not-a-blocker",
        )

    with pytest.raises(
        TypeError,
        match="EvaluationHarnessResult\\.contradiction_refs must contain only ContradictionRecord instances",
    ):
        build_evaluation_harness_result(
            event_trace=trace,
            blocker=blocker,
            contradiction_refs=("not-a-contradiction",),
        )

    with pytest.raises(
        ValueError,
        match="EvaluationHarnessResult\\.warnings must contain only non-empty values after trimming",
    ):
        build_evaluation_harness_result(
            event_trace=trace,
            blocker=blocker,
            warnings=("   ",),
        )

    with pytest.raises(
        TypeError,
        match="EvaluationHarnessResult\\.warnings must be tuple\\[str, \\.\\.\\.\\], got list",
    ):
        EvaluationHarnessResult(
            event_trace=trace,
            blocker=blocker,
            warnings=["warn"],
        )
