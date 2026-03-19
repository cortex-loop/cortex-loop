"""OpenAI host neutral-only cheap-path evaluation."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from cortex.core.dispatch import DispatchDecision, DispatchLane, classify_dispatch

from ._neutral_common import (
    extract_native_commitment_fields,
    merge_warnings,
    neutral_outcome_for_lane,
)
from .openai_host import BoundOpenAIHostEvent, observe_openai_host_event


class OpenAINeutralContinuationCode(Enum):
    NEUTRAL_ALLOWED = "neutral-allowed"
    CANDIDATE_PATH_REQUIRED = "candidate-path-required"
    FULL_COMMITMENT_PATH_REQUIRED = "full-commitment-path-required"


@dataclass(frozen=True, slots=True)
class OpenAINeutralContinuationDecision:
    allowed: bool
    result_code: OpenAINeutralContinuationCode

    def __post_init__(self) -> None:
        if not isinstance(self.allowed, bool):
            actual_type = type(self.allowed).__name__
            raise TypeError(
                "OpenAINeutralContinuationDecision.allowed must be bool, "
                f"got {actual_type}.",
            )
        if not isinstance(self.result_code, OpenAINeutralContinuationCode):
            actual_type = type(self.result_code).__name__
            raise TypeError(
                "OpenAINeutralContinuationDecision.result_code must be "
                f"OpenAINeutralContinuationCode, got {actual_type}.",
            )


@dataclass(frozen=True, slots=True)
class OpenAIHostNeutralResult:
    bound_event: BoundOpenAIHostEvent
    dispatch_decision: DispatchDecision
    neutral_decision: OpenAINeutralContinuationDecision
    warnings: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not isinstance(self.bound_event, BoundOpenAIHostEvent):
            actual_type = type(self.bound_event).__name__
            raise TypeError(
                "OpenAIHostNeutralResult.bound_event must be BoundOpenAIHostEvent, "
                f"got {actual_type}.",
            )
        if not isinstance(self.dispatch_decision, DispatchDecision):
            actual_type = type(self.dispatch_decision).__name__
            raise TypeError(
                "OpenAIHostNeutralResult.dispatch_decision must be DispatchDecision, "
                f"got {actual_type}.",
            )
        if not isinstance(self.neutral_decision, OpenAINeutralContinuationDecision):
            actual_type = type(self.neutral_decision).__name__
            raise TypeError(
                "OpenAIHostNeutralResult.neutral_decision must be "
                f"OpenAINeutralContinuationDecision, got {actual_type}.",
            )
        _validate_warning_tuple(self.warnings, "OpenAIHostNeutralResult.warnings")


def evaluate_openai_host_neutral(
    raw_event_name: str,
    raw_payload: Mapping[str, Any] | None = None,
    *,
    allow_message_commitment_fallback: bool = False,
) -> OpenAIHostNeutralResult:
    bound_event = observe_openai_host_event(
        raw_event_name,
        raw_payload,
        allow_message_commitment_fallback=allow_message_commitment_fallback,
    )
    normalized_payload = bound_event.normalized_payload
    native_commitment_fields = extract_native_commitment_fields(normalized_payload)
    dispatch_decision = classify_dispatch(
        bound_event.observation,
        payload=normalized_payload,
        native_commitment_fields=native_commitment_fields,
    )

    return OpenAIHostNeutralResult(
        bound_event=bound_event,
        dispatch_decision=dispatch_decision,
        neutral_decision=_neutral_decision_for_lane(dispatch_decision.lane),
        warnings=merge_warnings(bound_event.warnings, dispatch_decision.warnings),
    )


def _neutral_decision_for_lane(lane: DispatchLane) -> OpenAINeutralContinuationDecision:
    allowed, result_code = neutral_outcome_for_lane(
        lane,
        cheap_code=OpenAINeutralContinuationCode.NEUTRAL_ALLOWED,
        candidate_code=OpenAINeutralContinuationCode.CANDIDATE_PATH_REQUIRED,
        full_commitment_code=OpenAINeutralContinuationCode.FULL_COMMITMENT_PATH_REQUIRED,
    )
    return OpenAINeutralContinuationDecision(
        allowed=allowed,
        result_code=result_code,
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
    "OpenAIHostNeutralResult",
    "OpenAINeutralContinuationCode",
    "OpenAINeutralContinuationDecision",
    "evaluate_openai_host_neutral",
]
