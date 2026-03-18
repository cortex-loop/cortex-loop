"""Unit tests for minimal truthful-withheld eval packet publication."""

import pytest

from cortex.core.commitments import CommitmentStatus
from cortex.core.errors import ContradictionRecord, DegradationRecord
from cortex.eval.artifacts import BlockerFragment, CurrentPairFragment, EventTraceArtifact
from cortex.eval.harness import build_evaluation_harness_result
from cortex.eval.packets import (
    EvaluationPacket,
    EvaluationPacketKind,
    WithheldField,
    build_evaluation_packet,
)


def test_packet_built_from_current_pair_preserves_truth_and_withheld_fields() -> None:
    contradiction = ContradictionRecord(
        source_tag="trace-record",
        summary="trace evidence conflicts with artifact evidence",
        evidence_tags=frozenset({"trace", "artifact"}),
    )
    degradation = DegradationRecord(
        reason_code="partial-provenance",
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
        contradiction_refs=(contradiction,),
        degradation_refs=(degradation,),
    )
    harness_result = build_evaluation_harness_result(
        event_trace=trace,
        current_pair=current_pair,
        contradiction_refs=(contradiction,),
        degradation_refs=(degradation,),
        warnings=("trace redacted",),
    )

    packet = build_evaluation_packet(
        harness_result=harness_result,
        withheld_fields=(
            WithheldField(
                field_ref="current_pair.verdict_reason_code",
                reason_code="truthful-withheld",
            ),
        ),
        warnings=("packet built without report formatting",),
    )

    assert packet.packet_kind is EvaluationPacketKind.CURRENT_PAIR
    assert packet.current_pair is current_pair
    assert packet.blocker is None
    assert packet.withheld_fields == (
        WithheldField(
            field_ref="current_pair.verdict_reason_code",
            reason_code="truthful-withheld",
        ),
    )
    assert packet.warnings == (
        "trace redacted",
        "packet built without report formatting",
    )


def test_packet_built_from_blocker_preserves_truth_and_withheld_fields() -> None:
    contradiction = ContradictionRecord(
        source_tag="boundary-check",
        summary="approval state is contradictory",
        evidence_tags=frozenset({"approval"}),
    )
    trace = EventTraceArtifact(trace_id="trace-2", event_refs=("event-2",))
    blocker = BlockerFragment(
        reason_code="approval-required",
        boundary_tags=frozenset({"external-boundary"}),
        contradiction_refs=(contradiction,),
    )
    harness_result = build_evaluation_harness_result(
        event_trace=trace,
        blocker=blocker,
    )

    packet = build_evaluation_packet(
        harness_result=harness_result,
        withheld_fields=(
            WithheldField(
                field_ref="blocker.capability_tags",
                reason_code="truthful-withheld",
            ),
        ),
    )

    assert packet.packet_kind is EvaluationPacketKind.BLOCKER
    assert packet.current_pair is None
    assert packet.blocker is blocker
    assert packet.withheld_fields[0].field_ref == "blocker.capability_tags"
    assert packet.withheld_fields[0].reason_code == "truthful-withheld"


def test_packet_build_preserves_contradictions_and_degradations() -> None:
    trace_contradiction = ContradictionRecord(
        source_tag="trace",
        summary="trace disagrees with state",
        evidence_tags=frozenset({"trace"}),
    )
    packet_contradiction = ContradictionRecord(
        source_tag="packet",
        summary="publication omits non-authoritative field",
        evidence_tags=frozenset({"packet"}),
    )
    degradation = DegradationRecord(
        reason_code="partial-evidence",
        capability_tags=frozenset({"trace"}),
        contradiction_records=(trace_contradiction,),
    )
    trace = EventTraceArtifact(
        trace_id="trace-3",
        contradiction_refs=(trace_contradiction,),
        degradation_refs=(degradation,),
    )
    current_pair = CurrentPairFragment(
        event_trace=trace,
        verdict_status=CommitmentStatus.CERTIFIED,
        contradiction_refs=(trace_contradiction,),
        degradation_refs=(degradation,),
    )
    harness_result = build_evaluation_harness_result(
        event_trace=trace,
        current_pair=current_pair,
        contradiction_refs=(packet_contradiction,),
        degradation_refs=(degradation,),
    )

    packet = build_evaluation_packet(
        harness_result=harness_result,
        contradiction_refs=(packet_contradiction,),
        degradation_refs=(degradation,),
    )

    assert packet.contradiction_refs == (trace_contradiction, packet_contradiction)
    assert packet.degradation_refs == (degradation,)


def test_packet_build_requires_no_measured_example_or_runtime_wiring() -> None:
    trace = EventTraceArtifact(trace_id="trace-4")
    current_pair = CurrentPairFragment(
        event_trace=trace,
        verdict_status=CommitmentStatus.CERTIFIED,
        candidate_id="candidate-4",
    )
    harness_result = build_evaluation_harness_result(
        event_trace=trace,
        current_pair=current_pair,
    )

    packet = build_evaluation_packet(harness_result=harness_result)

    assert isinstance(packet, EvaluationPacket)
    assert packet.packet_kind is EvaluationPacketKind.CURRENT_PAIR


def test_packet_build_cannot_start_from_mismatched_harness_event_trace() -> None:
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


def test_packet_build_cannot_start_from_blocked_current_pair_harness_result() -> None:
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


def test_packet_build_cannot_start_from_empty_blocker_reason_fragment() -> None:
    with pytest.raises(ValueError, match="reason_code must be non-empty after trimming"):
        BlockerFragment(reason_code="")
