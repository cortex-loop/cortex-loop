"""Reference-host neutral-only cheap-path evaluation."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from cortex.core.dispatch import DispatchDecision, DispatchLane, classify_dispatch

from .reference_host import BoundReferenceHostEvent, observe_reference_host_event


class NeutralContinuationCode(Enum):
    NEUTRAL_ALLOWED = "neutral-allowed"
    CANDIDATE_PATH_REQUIRED = "candidate-path-required"
    FULL_COMMITMENT_PATH_REQUIRED = "full-commitment-path-required"


@dataclass(frozen=True, slots=True)
class NeutralContinuationDecision:
    allowed: bool
    result_code: NeutralContinuationCode


@dataclass(frozen=True, slots=True)
class ReferenceHostNeutralResult:
    bound_event: BoundReferenceHostEvent
    dispatch_decision: DispatchDecision
    neutral_decision: NeutralContinuationDecision
    warnings: tuple[str, ...] = field(default_factory=tuple)


def evaluate_reference_host_neutral(
    raw_event_name: str,
    raw_payload: Mapping[str, Any] | None = None,
    *,
    allow_message_commitment_fallback: bool = False,
) -> ReferenceHostNeutralResult:
    bound_event = observe_reference_host_event(
        raw_event_name,
        raw_payload,
        allow_message_commitment_fallback=allow_message_commitment_fallback,
    )
    normalized_payload = bound_event.normalized_payload
    native_commitment_fields = _native_commitment_fields(normalized_payload)
    dispatch_decision = classify_dispatch(
        bound_event.observation,
        payload=normalized_payload,
        native_commitment_fields=native_commitment_fields,
    )

    return ReferenceHostNeutralResult(
        bound_event=bound_event,
        dispatch_decision=dispatch_decision,
        neutral_decision=_neutral_decision_for_lane(dispatch_decision.lane),
        warnings=_merge_warnings(bound_event.warnings, dispatch_decision.warnings),
    )


def _native_commitment_fields(payload: Mapping[str, Any]) -> Mapping[str, Any] | None:
    commitment_fields = payload.get("commitment_fields")
    if payload.get("commitment_fields_source") != "native":
        return None
    if isinstance(commitment_fields, Mapping):
        return commitment_fields
    return None


def _neutral_decision_for_lane(lane: DispatchLane) -> NeutralContinuationDecision:
    if lane is DispatchLane.CHEAP:
        return NeutralContinuationDecision(
            allowed=True,
            result_code=NeutralContinuationCode.NEUTRAL_ALLOWED,
        )
    if lane is DispatchLane.CANDIDATE_BEARING:
        return NeutralContinuationDecision(
            allowed=False,
            result_code=NeutralContinuationCode.CANDIDATE_PATH_REQUIRED,
        )
    return NeutralContinuationDecision(
        allowed=False,
        result_code=NeutralContinuationCode.FULL_COMMITMENT_PATH_REQUIRED,
    )


def _merge_warnings(*groups: tuple[str, ...]) -> tuple[str, ...]:
    warnings: list[str] = []
    for group in groups:
        for warning in group:
            if warning not in warnings:
                warnings.append(warning)
    return tuple(warnings)


__all__ = [
    "NeutralContinuationCode",
    "NeutralContinuationDecision",
    "ReferenceHostNeutralResult",
    "evaluate_reference_host_neutral",
]
