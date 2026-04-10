"""Build or emit candidate Gemini mediated-lane packet-example evidence."""

from __future__ import annotations

import json
import sys

from cortex.core.dispatch import DispatchLane
from cortex.drivers.gemini_host_commitment import evaluate_gemini_host_commitment
from lab.eval.artifacts import CurrentPairFragment, EventTraceArtifact
from lab.eval.harness import build_evaluation_harness_result
from lab.eval.packets import WithheldField, build_evaluation_packet
from cortex.sre.families import SoftControlFamily
from cortex.sre.opportunities import HostNativeOpportunity, specialize_host_native_opportunity
from tests.archive.legacy_integration._gemini_host_realization_pair import (
    DEFAULT_GEMINI_HOST_REALIZATION_PAIR_KEY,
    GEMINI_HOST_REALIZATION_PAIR_KEYS,
    GEMINI_HOST_REALIZATION_PAIR_SPECS,
)
from tests.archive.legacy_integration._gemini_mediation_uncertainty_episode import (
    gemini_environment_handle,
)
from tests.conformance.integration._reference_lane import (
    host_surface_degradation_pair,
    provenance_manifest_for,
)


def build_gemini_host_realization_specialization_snapshot(
    *,
    clearly_superior: bool,
) -> dict[str, object]:
    opportunity = HostNativeOpportunity(
        opportunity_ref="mcp.query",
        supported_families=frozenset({SoftControlFamily.SEEK_CONTEXT}),
        clearly_superior=clearly_superior,
        native_surface_tags=frozenset({"mcp", "structured-query"}),
    )
    specialization = specialize_host_native_opportunity(
        SoftControlFamily.SEEK_CONTEXT,
        (opportunity,),
    )

    assert specialization.selected_family is SoftControlFamily.SEEK_CONTEXT
    if clearly_superior:
        assert specialization.preferred_opportunity is opportunity
        assert specialization.direct_opportunity_specialization_used is True
    else:
        assert specialization.preferred_opportunity is None
        assert specialization.direct_opportunity_specialization_used is False

    preferred_opportunity_ref = None
    if specialization.preferred_opportunity is not None:
        preferred_opportunity_ref = specialization.preferred_opportunity.opportunity_ref

    return {
        "selected_family": specialization.selected_family.value,
        "preferred_opportunity_ref": preferred_opportunity_ref,
        "direct_opportunity_specialization_used": specialization.direct_opportunity_specialization_used,
        "host_opportunity_refs": [opportunity.opportunity_ref],
        "native_surface_tags": sorted(opportunity.native_surface_tags),
    }


def build_gemini_mediated_lane_packet_example_snapshot(
    pair_key: str = DEFAULT_GEMINI_HOST_REALIZATION_PAIR_KEY,
) -> dict[str, object]:
    assert pair_key in GEMINI_HOST_REALIZATION_PAIR_KEYS
    spec = GEMINI_HOST_REALIZATION_PAIR_SPECS[pair_key]
    contradiction, degradation = host_surface_degradation_pair(
        source_tag=spec.contradiction_source_tag,
        summary=spec.contradiction_summary,
        evidence_tags=frozenset({"gemini", "host-publication", "truthful-withheld"}),
        reason_code=spec.degradation_reason_code,
        capability_tags=frozenset({"trace/read"}),
    )
    candidate_result = evaluate_gemini_host_commitment(
        "content.delta",
        {
            "interaction": {"id": spec.session_id},
            "session_id": spec.session_id,
            "candidate_id": spec.candidate_id,
            "stop_fields": {"claim_id": spec.candidate_id},
        },
        environment_handle=gemini_environment_handle(),
    )
    result = evaluate_gemini_host_commitment(
        "interaction.complete",
        {
            "commitment_id": spec.commitment_id,
            "candidate_id": spec.candidate_id,
            "session_id": spec.session_id,
            "externally_consequential": True,
        },
        environment_handle=gemini_environment_handle(),
        provenance_manifest=provenance_manifest_for(spec.provenance_artifact_id),
        contradiction_refs=(contradiction,),
        degradation_refs=(degradation,),
    )

    assert candidate_result.dispatch_decision.lane is DispatchLane.CANDIDATE_BEARING
    assert candidate_result.candidate is not None
    assert candidate_result.verdict is None
    assert result.dispatch_decision.lane is DispatchLane.FULL_COMMITMENT
    assert result.candidate is not None
    assert result.verdict is not None

    event_trace = EventTraceArtifact(
        trace_id=f"gemini-mediated-lane:{result.candidate.candidate_id}",
        event_refs=(
            candidate_result.bound_event.observation.event.native_event_name,
            result.bound_event.observation.event.native_event_name,
        ),
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
                reason_code="truthful-withheld",
            ),
        ),
    )
    specialization = build_gemini_host_realization_specialization_snapshot(
        clearly_superior=True,
    )

    assert packet.current_pair is current_pair
    assert packet.blocker is None
    assert packet.warnings == result.warnings

    return {
        "candidate_event": {
            "raw_host_event_name": _payload_metadata(candidate_result, "raw_host_event_name"),
            "canonical_event_name": candidate_result.bound_event.observation.event.native_event_name,
        },
        "publication_event": {
            "raw_host_event_name": _payload_metadata(result, "raw_host_event_name"),
            "canonical_event_name": result.bound_event.observation.event.native_event_name,
        },
        "dispatch_lanes": {
            "candidate": candidate_result.dispatch_decision.lane.value,
            "publication": result.dispatch_decision.lane.value,
        },
        "candidate_id": result.candidate.candidate_id,
        "verdict_status": result.verdict.status.value,
        "packet_kind": packet.packet_kind.value,
        "event_trace": {
            "trace_id": event_trace.trace_id,
            "event_refs": list(event_trace.event_refs),
            "record_refs": list(event_trace.record_refs),
        },
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


def emit_gemini_mediated_lane_packet_example_snapshot() -> None:
    json.dump(build_gemini_mediated_lane_packet_example_snapshot(), sys.stdout, indent=2)
    sys.stdout.write("\n")


def _payload_metadata(result: object, key: str) -> object:
    payload_metadata = result.bound_event.observation.event.payload_metadata
    for field in payload_metadata:
        if field.key == key:
            return field.value
    raise AssertionError(f"Missing payload metadata field: {key}")


if __name__ == "__main__":
    emit_gemini_mediated_lane_packet_example_snapshot()
