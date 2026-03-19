"""Conservative event-local dispatch classification for commitment handling."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .commitment_extract import NO_COMMITMENT_SOURCE, resolve_commitment_extract
from .envelopes import MetadataField
from .observation import ObservationBundle


class DispatchLane(Enum):
    CHEAP = "cheap"
    CANDIDATE_BEARING = "candidate-bearing"
    FULL_COMMITMENT = "full-commitment"


@dataclass(frozen=True, slots=True)
class WakeDecision:
    full_commitment_required: bool
    reason_tags: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if any(not reason_tag.strip() for reason_tag in self.reason_tags):
            raise ValueError(
                "WakeDecision.reason_tags must contain only non-empty values after trimming.",
            )


@dataclass(frozen=True, slots=True)
class EvidencePlan:
    requires_candidate_extraction: bool
    requires_provenance: bool
    requires_boundary_assessment: bool

    def __post_init__(self) -> None:
        if not isinstance(self.requires_candidate_extraction, bool):
            actual_type = type(self.requires_candidate_extraction).__name__
            raise TypeError(
                "EvidencePlan.requires_candidate_extraction must be bool, "
                f"got {actual_type}.",
            )
        if not isinstance(self.requires_provenance, bool):
            actual_type = type(self.requires_provenance).__name__
            raise TypeError(
                "EvidencePlan.requires_provenance must be bool, "
                f"got {actual_type}.",
            )
        if not isinstance(self.requires_boundary_assessment, bool):
            actual_type = type(self.requires_boundary_assessment).__name__
            raise TypeError(
                "EvidencePlan.requires_boundary_assessment must be bool, "
                f"got {actual_type}.",
            )


@dataclass(frozen=True, slots=True)
class DispatchDecision:
    lane: DispatchLane
    wake_decision: WakeDecision
    evidence_plan: EvidencePlan
    candidate_present: bool
    commitment_carrier_source: str = NO_COMMITMENT_SOURCE
    structured_payload_violation: bool = False
    warnings: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not isinstance(self.wake_decision, WakeDecision):
            actual_type = type(self.wake_decision).__name__
            raise TypeError(
                "DispatchDecision.wake_decision must be WakeDecision, "
                f"got {actual_type}.",
            )


FULL_COMMITMENT_REASON_ALIASES = {
    "commitment-subset": "commitment-subset",
    "host/commitment-subset": "commitment-subset",
    "commitment/event": "commitment-subset",
    "externally-consequential": "externally-consequential",
    "approval-gated": "approval-gated",
    "approval-required": "approval-gated",
    "durable-write": "durable-write",
    "write-executed": "durable-write",
    "write-committed": "durable-write",
    "approved-external-mutation": "approved-external-mutation",
    "external-mutation": "approved-external-mutation",
    "explicit-completion-claim": "explicit-completion-claim",
    "completion-claim": "explicit-completion-claim",
    "task-complete": "explicit-completion-claim",
    "boundary-required": "boundary-required",
    "boundary-check-required": "boundary-required",
}

CANDIDATE_REASON_ALIASES = {
    "proposal": "proposal-surface",
    "write-proposal": "proposal-surface",
    "approval/request": "proposal-surface",
    "approval-request": "proposal-surface",
    "patch-proposal": "proposal-surface",
    "write-intent": "proposal-surface",
    "candidate-bearing": "proposal-surface",
}

_CHEAP_EVIDENCE_PLAN = EvidencePlan(
    requires_candidate_extraction=False,
    requires_provenance=False,
    requires_boundary_assessment=False,
)
_CANDIDATE_EVIDENCE_PLAN = EvidencePlan(
    requires_candidate_extraction=True,
    requires_provenance=False,
    requires_boundary_assessment=False,
)
_FULL_EVIDENCE_PLAN = EvidencePlan(
    requires_candidate_extraction=True,
    requires_provenance=True,
    requires_boundary_assessment=True,
)


def classify_dispatch(
    observation: ObservationBundle,
    *,
    payload: Mapping[str, Any] | None = None,
    native_commitment_fields: Mapping[str, Any] | None = None,
    require_structured_commitment_payload: bool = False,
) -> DispatchDecision:
    if payload is None:
        payload_mapping: Mapping[str, Any] = {}
    elif isinstance(payload, Mapping):
        payload_mapping = payload
    else:
        raise TypeError("payload must be a mapping when provided")

    marker_tags = _collect_marker_tags(observation, payload_mapping)
    full_commitment_reasons = _collect_reason_tags(
        marker_tags,
        FULL_COMMITMENT_REASON_ALIASES,
    )
    candidate_reasons = _collect_reason_tags(marker_tags, CANDIDATE_REASON_ALIASES)

    extraction = None
    if native_commitment_fields is not None or payload_mapping or full_commitment_reasons or candidate_reasons:
        extraction = resolve_commitment_extract(
            payload_mapping,
            native_commitment_fields=native_commitment_fields,
            require_structured_commitment_payload=require_structured_commitment_payload,
        )

    candidate_present = bool(
        extraction
        and extraction.commitment_fields is not None
        and not extraction.structured_payload_violation
    )
    if candidate_present:
        candidate_reasons.add("candidate-present")

    if full_commitment_reasons:
        lane = DispatchLane.FULL_COMMITMENT
    elif candidate_reasons:
        lane = DispatchLane.CANDIDATE_BEARING
    else:
        lane = DispatchLane.CHEAP

    return DispatchDecision(
        lane=lane,
        wake_decision=WakeDecision(
            full_commitment_required=bool(full_commitment_reasons),
            reason_tags=frozenset(full_commitment_reasons | candidate_reasons),
        ),
        evidence_plan=_evidence_plan_for_lane(lane),
        candidate_present=candidate_present,
        commitment_carrier_source=(
            extraction.carrier_source if extraction is not None else NO_COMMITMENT_SOURCE
        ),
        structured_payload_violation=(
            extraction.structured_payload_violation if extraction is not None else False
        ),
        warnings=extraction.warnings if extraction is not None else (),
    )


def _evidence_plan_for_lane(lane: DispatchLane) -> EvidencePlan:
    if lane is DispatchLane.CHEAP:
        return _CHEAP_EVIDENCE_PLAN
    if lane is DispatchLane.CANDIDATE_BEARING:
        return _CANDIDATE_EVIDENCE_PLAN
    return _FULL_EVIDENCE_PLAN


def _collect_marker_tags(
    observation: ObservationBundle,
    payload: Mapping[str, Any],
) -> frozenset[str]:
    tags = {
        _canonical_tag(observation.event.native_event_name),
        *(_canonical_tag(tag) for tag in observation.event.facet_tags),
        *(_canonical_tag(tag) for tag in observation.event.channel_tags),
        *(_canonical_tag(tag) for tag in observation.event.extension_tags),
        *(_canonical_tag(tag) for tag in observation.payload_view.summary_tags),
    }

    for field in _iter_metadata_fields(observation):
        key = _canonical_tag(field.key)
        if key in FULL_COMMITMENT_REASON_ALIASES and _is_truthy_marker_value(field.value):
            tags.add(key)
        if key in CANDIDATE_REASON_ALIASES and _is_truthy_marker_value(field.value):
            tags.add(key)

    for key, value in payload.items():
        canonical_key = _canonical_tag(str(key))
        if canonical_key in FULL_COMMITMENT_REASON_ALIASES and _is_truthy_marker_value(value):
            tags.add(canonical_key)
        if canonical_key in CANDIDATE_REASON_ALIASES and _is_truthy_marker_value(value):
            tags.add(canonical_key)

    tags.discard("")
    return frozenset(tags)


def _iter_metadata_fields(observation: ObservationBundle) -> tuple[MetadataField, ...]:
    payload_handle = observation.payload_view.payload_handle
    handle_metadata = payload_handle.metadata if payload_handle is not None else ()
    return (
        *observation.event.payload_metadata,
        *observation.payload_view.metadata,
        *handle_metadata,
    )


def _collect_reason_tags(
    marker_tags: frozenset[str],
    aliases: Mapping[str, str],
) -> set[str]:
    return {reason for tag, reason in aliases.items() if tag in marker_tags}


def _canonical_tag(value: str) -> str:
    return value.strip().lower().replace("_", "-").replace(" ", "-")


def _is_truthy_marker_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "required"}
    return False


__all__ = [
    "DispatchDecision",
    "DispatchLane",
    "EvidencePlan",
    "WakeDecision",
    "classify_dispatch",
]
