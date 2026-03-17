"""Reference-host commitment-path composition over landed core surfaces."""

from __future__ import annotations

import hashlib
import json
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

from .reference_host import BoundReferenceHostEvent, observe_reference_host_event

_CANDIDATE_ID_KEYS = ("candidate_id", "commitment_id", "claim_id")


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
        candidate_id = _candidate_id_from_value(resolution.value)
        if candidate_id is None:
            continue
        warnings.extend(resolution.warnings)
        return (
            CommitmentCandidate(
                candidate_id=candidate_id,
                surface_tags=_candidate_surface_tags(bound_event, dispatch_decision),
                payload_handle=bound_event.observation.payload_view.payload_handle,
                metadata=(
                    MetadataField("candidate_id_source", _candidate_id_source_label(key, resolution.source)),
                    MetadataField("candidate_id_key", key),
                ),
            ),
            tuple(warnings),
        )

    synthesized_candidate_id = _synthesized_candidate_id(bound_event)
    warnings.append(
        "Synthesized deterministic local candidate id because no direct or extracted identifier was present."
    )
    return (
        CommitmentCandidate(
            candidate_id=synthesized_candidate_id,
            surface_tags=_candidate_surface_tags(bound_event, dispatch_decision),
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
    native_commitment_fields = _native_commitment_fields(bound_event.normalized_payload)
    dispatch_decision = classify_dispatch(
        bound_event.observation,
        payload=bound_event.normalized_payload,
        native_commitment_fields=native_commitment_fields,
    )

    extraction_result = _resolve_reference_host_extract(
        bound_event=bound_event,
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
        warnings=_merge_warnings(
            bound_event.warnings,
            dispatch_decision.warnings,
            extraction_result.warnings if extraction_result is not None else (),
            candidate_warnings,
        ),
    )


def _resolve_reference_host_extract(
    *,
    bound_event: BoundReferenceHostEvent,
    dispatch_decision: DispatchDecision,
    native_commitment_fields: Mapping[str, Any] | None,
    allow_message_commitment_fallback: bool,
) -> CommitmentExtractionResult | None:
    payload = bound_event.normalized_payload
    has_structured_carrier = (
        native_commitment_fields is not None
        or isinstance(payload.get("stop_fields"), Mapping)
        or "commitment_fields_source" in payload
    )
    if dispatch_decision.lane is DispatchLane.CHEAP and not has_structured_carrier:
        return None
    return resolve_commitment_extract(
        payload,
        native_commitment_fields=native_commitment_fields,
        allow_message_fallback=allow_message_commitment_fallback,
    )


def _native_commitment_fields(payload: Mapping[str, Any]) -> Mapping[str, Any] | None:
    commitment_fields = payload.get("commitment_fields")
    if payload.get("commitment_fields_source") != "native":
        return None
    if isinstance(commitment_fields, Mapping):
        return commitment_fields
    return None


def _candidate_surface_tags(
    bound_event: BoundReferenceHostEvent,
    dispatch_decision: DispatchDecision,
) -> frozenset[str]:
    return frozenset(
        set(bound_event.observation.event.facet_tags) | set(dispatch_decision.wake_decision.reason_tags)
    )


def _candidate_id_from_value(value: Any) -> str | None:
    if value is None:
        return None
    candidate_id = str(value).strip()
    return candidate_id or None


def _candidate_id_source_label(key: str, source: str) -> str:
    return f"{source}:{key}"


def _synthesized_candidate_id(bound_event: BoundReferenceHostEvent) -> str:
    payload_blob = json.dumps(
        bound_event.normalized_payload,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    payload_handle = bound_event.observation.payload_view.payload_handle
    digest_input = (
        f"{bound_event.observation.event.native_event_name}|"
        f"{payload_handle.payload_ref if payload_handle is not None else ''}|"
        f"{payload_blob}"
    )
    digest = hashlib.sha1(digest_input.encode("utf-8")).hexdigest()[:12]
    return f"local-candidate-{digest}"


def _merge_warnings(*groups: tuple[str, ...]) -> tuple[str, ...]:
    warnings: list[str] = []
    for group in groups:
        for warning in group:
            if warning not in warnings:
                warnings.append(warning)
    return tuple(warnings)


__all__ = [
    "ReferenceHostCommitmentResult",
    "bind_reference_host_candidate",
    "evaluate_reference_host_commitment",
]
