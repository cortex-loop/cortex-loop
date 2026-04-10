"""Build or emit candidate reference mediated-lane packet-example evidence."""

from __future__ import annotations

import json
import sys

from cortex.core.dispatch import DispatchLane
from cortex.drivers.reference_host_commitment import evaluate_reference_host_commitment
from lab.eval.artifacts import CurrentPairFragment, EventTraceArtifact
from lab.eval.harness import build_evaluation_harness_result
from lab.eval.packets import WithheldField, build_evaluation_packet
from cortex.sre.mediation import ReferenceMediationMode
from tests.archive.legacy_integration._reference_host_realization_pairs import (
    DEFAULT_REFERENCE_HOST_REALIZATION_PAIR_KEY,
    REFERENCE_HOST_REALIZATION_PAIR_SPECS,
)
from tests.archive.legacy_integration._reference_host_realization_runtime import (
    build_reference_host_realization_runtime_snapshot,
)
from tests.conformance.integration._reference_lane import (
    assert_reference_packet_preserves_degradation_pair,
    full_commitment_event,
    host_surface_degradation_pair,
    provenance_manifest_for,
    reference_environment_handle,
)


def build_reference_host_realization_specialization_snapshot(
    *,
    pair_key: str = DEFAULT_REFERENCE_HOST_REALIZATION_PAIR_KEY,
    clearly_superior: bool,
) -> dict[str, object]:
    runtime_control = build_reference_host_realization_runtime_snapshot(
        pair_key,
        mediation_mode=(
            ReferenceMediationMode.HOST_REALIZATION_EXPERIMENTAL
            if clearly_superior
            else ReferenceMediationMode.IDENTITY
        ),
    )
    mediation = runtime_control["mediation"]

    assert isinstance(mediation, dict)
    assert runtime_control["selected_family"] == "seek-context"
    if clearly_superior:
        assert mediation["preferred_opportunity_ref"] == "mcp.query"
        assert mediation["direct_opportunity_specialization_used"] is True
    else:
        assert mediation["preferred_opportunity_ref"] is None
        assert mediation["direct_opportunity_specialization_used"] is False

    return {
        "selected_family": runtime_control["selected_family"],
        "realized_family": runtime_control["realized_family"],
        "preferred_opportunity_ref": mediation["preferred_opportunity_ref"],
        "direct_opportunity_specialization_used": (
            mediation["direct_opportunity_specialization_used"]
        ),
        "host_opportunity_refs": runtime_control["host_opportunity_refs"],
    }


def build_reference_mediated_lane_packet_example_snapshot(
    pair_key: str = DEFAULT_REFERENCE_HOST_REALIZATION_PAIR_KEY,
) -> dict[str, object]:
    spec = REFERENCE_HOST_REALIZATION_PAIR_SPECS[pair_key]
    runtime_control = build_reference_host_realization_runtime_snapshot(
        pair_key,
        mediation_mode=ReferenceMediationMode.HOST_REALIZATION_EXPERIMENTAL,
    )
    contradiction, degradation = host_surface_degradation_pair(
        source_tag=spec.contradiction_source_tag,
        summary=spec.contradiction_summary,
        evidence_tags=frozenset({"receipt", "result-artifact"}),
        reason_code=spec.degradation_reason_code,
    )
    event_name, payload = full_commitment_event(
        commitment_id=spec.commitment_id,
        session_id=spec.session_id,
    )
    result = evaluate_reference_host_commitment(
        event_name,
        payload,
        environment_handle=reference_environment_handle(),
        provenance_manifest=provenance_manifest_for(spec.provenance_artifact_id),
        degradation_refs=(degradation,),
        contradiction_refs=(contradiction,),
    )

    assert result.dispatch_decision.lane is DispatchLane.FULL_COMMITMENT
    assert result.candidate is not None
    assert result.verdict is not None

    event_trace = EventTraceArtifact(
        trace_id=f"reference-mediated-lane:{result.candidate.candidate_id}",
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
    specialization = build_reference_host_realization_specialization_snapshot(
        pair_key=pair_key,
        clearly_superior=True,
    )

    assert packet.current_pair is current_pair
    assert packet.blocker is None
    assert packet.warnings == result.warnings
    assert runtime_control["selected_family"] == "seek-context"
    assert runtime_control["realized_family"] == "seek-context"
    assert runtime_control["host_opportunity_refs"] == ["mcp.query"]
    assert runtime_control["mediation"]["mediation_active"] is True
    assert runtime_control["mediation"]["preferred_opportunity_ref"] == "mcp.query"
    assert runtime_control["mediation"]["direct_opportunity_specialization_used"] is True
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
        "runtime_control": runtime_control,
        "opportunity_specialization": specialization,
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


def emit_reference_mediated_lane_packet_example_snapshot() -> None:
    json.dump(build_reference_mediated_lane_packet_example_snapshot(), sys.stdout, indent=2)
    sys.stdout.write("\n")


def _payload_metadata(result: object, key: str) -> object:
    payload_metadata = result.bound_event.observation.event.payload_metadata
    for field in payload_metadata:
        if field.key == key:
            return field.value
    raise AssertionError(f"Missing payload metadata field: {key}")


if __name__ == "__main__":
    emit_reference_mediated_lane_packet_example_snapshot()
