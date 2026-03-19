"""Build or emit candidate reference-lane packet-example evidence."""

from __future__ import annotations

import json
import sys

from cortex.core.dispatch import DispatchLane
from cortex.drivers.reference_host_commitment import evaluate_reference_host_commitment
from cortex.eval.artifacts import CurrentPairFragment, EventTraceArtifact
from cortex.eval.harness import build_evaluation_harness_result
from cortex.eval.packets import WithheldField, build_evaluation_packet
from tests.integration._reference_lane import (
    assert_reference_packet_preserves_degradation_pair,
    full_commitment_event,
    host_surface_degradation_pair,
    provenance_manifest_for,
    reference_environment_handle,
)


def build_reference_lane_packet_example_snapshot() -> dict[str, object]:
    contradiction, degradation = host_surface_degradation_pair(
        summary="write receipt was incomplete",
        evidence_tags=frozenset({"receipt", "result-artifact"}),
    )
    event_name, payload = full_commitment_event(
        commitment_id="commit-packet-1",
        session_id="packet-session-1",
    )
    result = evaluate_reference_host_commitment(
        event_name,
        payload,
        environment_handle=reference_environment_handle(),
        provenance_manifest=provenance_manifest_for("artifact-packet-1"),
        degradation_refs=(degradation,),
        contradiction_refs=(contradiction,),
    )

    assert result.dispatch_decision.lane is DispatchLane.FULL_COMMITMENT
    assert result.candidate is not None
    assert result.verdict is not None

    event_trace = EventTraceArtifact(
        trace_id=f"reference-lane:{result.candidate.candidate_id}",
        event_refs=(result.bound_event.observation.event.native_event_name,),
        record_refs=tuple(
            ref.reference_id for ref in result.verdict.provenance_manifest.evidence_refs
        ),
        contradiction_refs=result.verdict.contradiction_refs,
        degradation_refs=result.verdict.degradation_refs,
    )
    current_pair = CurrentPairFragment(
        event_trace=event_trace,
        verdict_status=result.verdict.status,
        candidate_id=result.candidate.candidate_id,
        contradiction_refs=result.verdict.contradiction_refs,
        degradation_refs=result.verdict.degradation_refs,
    )
    harness_result = build_evaluation_harness_result(
        event_trace=event_trace,
        current_pair=current_pair,
        contradiction_refs=result.verdict.contradiction_refs,
        degradation_refs=result.verdict.degradation_refs,
        warnings=result.warnings,
    )
    packet = build_evaluation_packet(
        harness_result=harness_result,
        withheld_fields=(
            WithheldField(
                field_ref="current_pair.verdict_reason_code",
                reason_code="not-material-in-minimal-example",
            ),
        ),
    )

    assert packet.current_pair is current_pair
    assert packet.blocker is None
    assert packet.warnings == result.warnings
    assert_reference_packet_preserves_degradation_pair(
        current_pair,
        packet,
        contradiction,
        degradation,
    )

    return {
        "source_event": {
            "raw_host_event_name": _payload_metadata(result, "raw_host_event_name"),
            "canonical_event_name": result.bound_event.observation.event.native_event_name,
        },
        "dispatch_lane": result.dispatch_decision.lane.value,
        "candidate_id": result.candidate.candidate_id,
        "verdict_status": result.verdict.status.value,
        "packet_kind": packet.packet_kind.value,
        "event_trace": {
            "trace_id": event_trace.trace_id,
            "event_refs": list(event_trace.event_refs),
            "record_refs": list(event_trace.record_refs),
        },
        "withheld_fields": [
            {
                "field_ref": field.field_ref,
                "reason_code": field.reason_code,
            }
            for field in packet.withheld_fields
        ],
        "contradiction_refs": [
            {
                "source_tag": record.source_tag,
                "summary": record.summary,
            }
            for record in packet.contradiction_refs
        ],
        "degradation_refs": [
            {
                "reason_code": record.reason_code,
                "capability_tags": sorted(record.capability_tags),
            }
            for record in packet.degradation_refs
        ],
        "warnings": list(packet.warnings),
    }


def emit_reference_lane_packet_example_snapshot() -> None:
    json.dump(build_reference_lane_packet_example_snapshot(), sys.stdout, indent=2)
    sys.stdout.write("\n")


def _payload_metadata(result: object, key: str) -> object:
    payload_metadata = result.bound_event.observation.event.payload_metadata
    for field in payload_metadata:
        if field.key == key:
            return field.value
    raise AssertionError(f"Missing payload metadata field: {key}")


if __name__ == "__main__":
    emit_reference_lane_packet_example_snapshot()
