"""Claude host commitment-path composition over landed core surfaces."""

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

from cortex.drivers._commitment_common import (
    CANDIDATE_ID_KEYS as _CANDIDATE_ID_KEYS,
    candidate_id_from_value,
    candidate_id_source_label,
    candidate_surface_tags,
    extract_native_commitment_fields,
    merge_warnings,
    resolve_commitment_extract_for_dispatch,
    synthesized_candidate_id,
)
from .claude_host import BoundClaudeHostEvent, observe_claude_host_event


@dataclass(frozen=True, slots=True)
class ClaudeHostCommitmentResult:
    bound_event: BoundClaudeHostEvent
    dispatch_decision: DispatchDecision
    extraction_result: CommitmentExtractionResult | None = None
    candidate: CommitmentCandidate | None = None
    verdict: CommitmentVerdict | None = None
    warnings: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not isinstance(self.bound_event, BoundClaudeHostEvent):
            actual_type = type(self.bound_event).__name__
            raise TypeError(
                "ClaudeHostCommitmentResult.bound_event must be BoundClaudeHostEvent, "
                f"got {actual_type}.",
            )
        if not isinstance(self.dispatch_decision, DispatchDecision):
            actual_type = type(self.dispatch_decision).__name__
            raise TypeError(
                "ClaudeHostCommitmentResult.dispatch_decision must be DispatchDecision, "
                f"got {actual_type}.",
            )
        if self.extraction_result is not None and not isinstance(
            self.extraction_result,
            CommitmentExtractionResult,
        ):
            actual_type = type(self.extraction_result).__name__
            raise TypeError(
                "ClaudeHostCommitmentResult.extraction_result must be "
                f"CommitmentExtractionResult | None, got {actual_type}.",
            )
        if self.candidate is not None and not isinstance(self.candidate, CommitmentCandidate):
            actual_type = type(self.candidate).__name__
            raise TypeError(
                "ClaudeHostCommitmentResult.candidate must be CommitmentCandidate | None, "
                f"got {actual_type}.",
            )
        if self.verdict is not None and not isinstance(self.verdict, CommitmentVerdict):
            actual_type = type(self.verdict).__name__
            raise TypeError(
                "ClaudeHostCommitmentResult.verdict must be CommitmentVerdict | None, "
                f"got {actual_type}.",
            )
        _validate_warning_tuple(self.warnings, "ClaudeHostCommitmentResult.warnings")


def bind_claude_host_candidate(
    bound_event: BoundClaudeHostEvent,
    dispatch_decision: DispatchDecision,
    extraction_result: CommitmentExtractionResult | None = None,
) -> tuple[CommitmentCandidate, tuple[str, ...]]:
    if not isinstance(bound_event, BoundClaudeHostEvent):
        actual_type = type(bound_event).__name__
        raise TypeError(
            "bind_claude_host_candidate.bound_event must be BoundClaudeHostEvent, "
            f"got {actual_type}.",
        )
    if not isinstance(dispatch_decision, DispatchDecision):
        actual_type = type(dispatch_decision).__name__
        raise TypeError(
            "bind_claude_host_candidate.dispatch_decision must be DispatchDecision, "
            f"got {actual_type}.",
        )
    if extraction_result is not None and not isinstance(extraction_result, CommitmentExtractionResult):
        actual_type = type(extraction_result).__name__
        raise TypeError(
            "bind_claude_host_candidate.extraction_result must be "
            f"CommitmentExtractionResult | None, got {actual_type}.",
        )
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


def evaluate_claude_host_commitment(
    raw_event_name: str,
    raw_payload: Mapping[str, Any] | None,
    *,
    environment_handle: CommitmentEnvironmentHandle,
    provenance_manifest: ProvenanceManifest | None = None,
    boundary_assessment: BoundaryAssessment | None = None,
    degradation_refs: tuple[DegradationRecord, ...] = (),
    contradiction_refs: tuple[ContradictionRecord, ...] = (),
    allow_message_commitment_fallback: bool = False,
) -> ClaudeHostCommitmentResult:
    if not isinstance(environment_handle, CommitmentEnvironmentHandle):
        actual_type = type(environment_handle).__name__
        raise TypeError(
            "evaluate_claude_host_commitment.environment_handle must be "
            f"CommitmentEnvironmentHandle, got {actual_type}.",
        )
    if provenance_manifest is not None and not isinstance(provenance_manifest, ProvenanceManifest):
        actual_type = type(provenance_manifest).__name__
        raise TypeError(
            "evaluate_claude_host_commitment.provenance_manifest must be "
            f"ProvenanceManifest | None, got {actual_type}.",
        )
    if boundary_assessment is not None and not isinstance(boundary_assessment, BoundaryAssessment):
        actual_type = type(boundary_assessment).__name__
        raise TypeError(
            "evaluate_claude_host_commitment.boundary_assessment must be "
            f"BoundaryAssessment | None, got {actual_type}.",
        )
    for degradation in degradation_refs:
        if not isinstance(degradation, DegradationRecord):
            raise TypeError(
                "evaluate_claude_host_commitment.degradation_refs must contain only "
                "DegradationRecord instances.",
            )
    for contradiction in contradiction_refs:
        if not isinstance(contradiction, ContradictionRecord):
            raise TypeError(
                "evaluate_claude_host_commitment.contradiction_refs must contain only "
                "ContradictionRecord instances.",
            )
    bound_event = observe_claude_host_event(
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
        candidate, candidate_warnings = bind_claude_host_candidate(
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

    return ClaudeHostCommitmentResult(
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


def _validate_warning_tuple(warnings: tuple[str, ...], label: str) -> None:
    if not isinstance(warnings, tuple):
        actual_type = type(warnings).__name__
        raise TypeError(f"{label} must be tuple[str, ...], got {actual_type}.")
    for warning in warnings:
        if not isinstance(warning, str):
            actual_type = type(warning).__name__
            raise TypeError(f"{label} must contain only str instances, got {actual_type}.")
        if not warning.strip():
            raise ValueError(f"{label} must contain only non-empty values after trimming.")


__all__ = [
    "ClaudeHostCommitmentResult",
    "bind_claude_host_candidate",
    "evaluate_claude_host_commitment",
]
