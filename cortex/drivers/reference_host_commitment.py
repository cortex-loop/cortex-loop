"""Reference-host commitment-path composition over landed core surfaces."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from cortex.core.certification import certify_commitment
from cortex.core.commitment_extract import (
    CommitmentExtractionResult,
    NO_COMMITMENT_SOURCE,
    reconcile_commitment_field,
    resolve_commitment_extract,
)
from cortex.core.commitments import (
    BoundaryAssessment,
    CertificationContext,
    CommitmentCandidate,
    CommitmentVerdict,
    ProvenanceManifest,
)
from cortex.core.dispatch import DispatchDecision, DispatchLane, classify_dispatch
from cortex.core.envelopes import MetadataField
from cortex.core.environment import CommitmentEnvironmentHandle
from cortex.core.errors import ContradictionRecord, DegradationRecord

from ._commitment_common import (
    CANDIDATE_ID_KEYS as _CANDIDATE_ID_KEYS,
    candidate_id_from_value,
    candidate_id_source_label,
    candidate_surface_tags,
    extract_native_commitment_fields,
    merge_warnings,
    resolve_commitment_extract_for_dispatch,
    synthesized_candidate_id,
)
from .reference_host import BoundReferenceHostEvent, observe_reference_host_event


@dataclass(frozen=True, slots=True)
class ReferenceHostCommitmentResult:
    bound_event: BoundReferenceHostEvent
    dispatch_decision: DispatchDecision
    extraction_result: CommitmentExtractionResult | None = None
    candidate: CommitmentCandidate | None = None
    verdict: CommitmentVerdict | None = None
    warnings: tuple[str, ...] = field(default_factory=tuple)


def bind_reference_host_candidate(
    bound_event: BoundReferenceHostEvent,
    dispatch_decision: DispatchDecision,
    extraction_result: CommitmentExtractionResult | None = None,
) -> tuple[CommitmentCandidate, tuple[str, ...]]:
    commitment_fields = extraction_result.commitment_fields if extraction_result is not None else None
    carrier_source = (
        extraction_result.carrier_source if extraction_result is not None else NO_COMMITMENT_SOURCE
    )

    warnings: list[str] = []
    for key in _CANDIDATE_ID_KEYS:
        resolution = reconcile_commitment_field(
            key=key,
            payload=bound_event.normalized_payload,
            commitment_fields=commitment_fields,
            carrier_source=carrier_source,
            value_label="candidate id",
        )
        candidate_id = candidate_id_from_value(resolution.value)
        if candidate_id is None:
            continue
        warnings.extend(resolution.warnings)
        return (
            CommitmentCandidate(
                candidate_id=candidate_id,
                surface_tags=candidate_surface_tags(
                    facet_tags=bound_event.observation.event.facet_tags,
                    wake_reason_tags=dispatch_decision.wake_decision.reason_tags,
                ),
                payload_handle=bound_event.observation.payload_view.payload_handle,
                metadata=(
                    MetadataField("candidate_id_source", candidate_id_source_label(key, resolution.source)),
                    MetadataField("candidate_id_key", key),
                ),
            ),
            tuple(warnings),
        )

    synthesized_id = synthesized_candidate_id(
        native_event_name=bound_event.observation.event.native_event_name,
        normalized_payload=bound_event.normalized_payload,
        payload_handle=bound_event.observation.payload_view.payload_handle,
    )
    warnings.append(
        "Synthesized deterministic local candidate id because no direct or extracted identifier was present."
    )
    return (
        CommitmentCandidate(
            candidate_id=synthesized_id,
            surface_tags=candidate_surface_tags(
                facet_tags=bound_event.observation.event.facet_tags,
                wake_reason_tags=dispatch_decision.wake_decision.reason_tags,
            ),
            payload_handle=bound_event.observation.payload_view.payload_handle,
            metadata=(
                MetadataField("candidate_id_source", "synthesized-local"),
                MetadataField("candidate_id_synthesized", True),
            ),
        ),
        tuple(warnings),
    )


def evaluate_reference_host_commitment(
    raw_event_name: str,
    raw_payload: Mapping[str, Any] | None,
    *,
    environment_handle: CommitmentEnvironmentHandle,
    provenance_manifest: ProvenanceManifest | None = None,
    boundary_assessment: BoundaryAssessment | None = None,
    degradation_refs: tuple[DegradationRecord, ...] = (),
    contradiction_refs: tuple[ContradictionRecord, ...] = (),
    allow_message_commitment_fallback: bool = False,
) -> ReferenceHostCommitmentResult:
    bound_event = observe_reference_host_event(
        raw_event_name,
        raw_payload,
        allow_message_commitment_fallback=allow_message_commitment_fallback,
    )
    native_commitment_fields = extract_native_commitment_fields(bound_event.normalized_payload)
    dispatch_decision = classify_dispatch(
        bound_event.observation,
        payload=bound_event.normalized_payload,
        native_commitment_fields=native_commitment_fields,
    )

    extraction_result = resolve_commitment_extract_for_dispatch(
        payload=bound_event.normalized_payload,
        dispatch_decision=dispatch_decision,
        native_commitment_fields=native_commitment_fields,
        allow_message_commitment_fallback=allow_message_commitment_fallback,
    )

    candidate = None
    candidate_warnings: tuple[str, ...] = ()
    if dispatch_decision.lane is not DispatchLane.CHEAP:
        candidate, candidate_warnings = bind_reference_host_candidate(
            bound_event,
            dispatch_decision,
            extraction_result,
        )

    verdict = None
    if dispatch_decision.lane is DispatchLane.FULL_COMMITMENT and candidate is not None:
        effective_boundary_assessment = boundary_assessment or BoundaryAssessment(blocked=False)
        verdict = certify_commitment(
            CertificationContext(
                candidate=candidate,
                observation=bound_event.observation,
                environment_handle=environment_handle,
                wake_reasons=dispatch_decision.wake_decision.reason_tags,
                boundary_tags=effective_boundary_assessment.boundary_tags,
            ),
            provenance_manifest=provenance_manifest,
            boundary_assessment=effective_boundary_assessment,
            degradation_refs=degradation_refs,
            contradiction_refs=contradiction_refs,
        )

    return ReferenceHostCommitmentResult(
        bound_event=bound_event,
        dispatch_decision=dispatch_decision,
        extraction_result=extraction_result,
        candidate=candidate,
        verdict=verdict,
        warnings=merge_warnings(
            bound_event.warnings,
            dispatch_decision.warnings,
            extraction_result.warnings if extraction_result is not None else (),
            candidate_warnings,
        ),
    )


__all__ = [
    "ReferenceHostCommitmentResult",
    "bind_reference_host_candidate",
    "evaluate_reference_host_commitment",
]
