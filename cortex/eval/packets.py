"""Minimal truthful-withheld evaluation packet surface."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TypeVar

from cortex.core.errors import ContradictionRecord, DegradationRecord

from .artifacts import BlockerFragment, CurrentPairFragment
from .harness import EvaluationHarnessResult

_T = TypeVar("_T")


class EvaluationPacketKind(str, Enum):
    CURRENT_PAIR = "current-pair"
    BLOCKER = "blocker"


@dataclass(frozen=True, slots=True)
class WithheldField:
    field_ref: str
    reason_code: str


@dataclass(frozen=True, slots=True)
class EvaluationPacket:
    harness_result: EvaluationHarnessResult
    packet_kind: EvaluationPacketKind
    current_pair: CurrentPairFragment | None = None
    blocker: BlockerFragment | None = None
    withheld_fields: tuple[WithheldField, ...] = field(default_factory=tuple)
    contradiction_refs: tuple[ContradictionRecord, ...] = field(default_factory=tuple)
    degradation_refs: tuple[DegradationRecord, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.packet_kind is EvaluationPacketKind.CURRENT_PAIR:
            if self.current_pair != self.harness_result.current_pair or self.blocker is not None:
                raise ValueError(
                    "current-pair packets must expose the harness current_pair and no blocker",
                )
            return

        if self.packet_kind is EvaluationPacketKind.BLOCKER:
            if self.blocker != self.harness_result.blocker or self.current_pair is not None:
                raise ValueError(
                    "blocker packets must expose the harness blocker and no current_pair",
                )
            return

        raise ValueError("unsupported evaluation packet kind")


def build_evaluation_packet(
    *,
    harness_result: EvaluationHarnessResult,
    withheld_fields: tuple[WithheldField, ...] = (),
    contradiction_refs: tuple[ContradictionRecord, ...] = (),
    degradation_refs: tuple[DegradationRecord, ...] = (),
    warnings: tuple[str, ...] = (),
) -> EvaluationPacket:
    current_pair = harness_result.current_pair
    blocker = harness_result.blocker
    packet_kind = (
        EvaluationPacketKind.CURRENT_PAIR
        if current_pair is not None
        else EvaluationPacketKind.BLOCKER
    )
    outcome_contradictions = (
        current_pair.contradiction_refs if current_pair is not None else blocker.contradiction_refs
    )
    outcome_degradations = (
        current_pair.degradation_refs if current_pair is not None else blocker.degradation_refs
    )

    return EvaluationPacket(
        harness_result=harness_result,
        packet_kind=packet_kind,
        current_pair=current_pair,
        blocker=blocker,
        withheld_fields=withheld_fields,
        contradiction_refs=_merge_unique(
            harness_result.event_trace.contradiction_refs,
            outcome_contradictions,
            harness_result.contradiction_refs,
            contradiction_refs,
        ),
        degradation_refs=_merge_unique(
            harness_result.event_trace.degradation_refs,
            outcome_degradations,
            harness_result.degradation_refs,
            degradation_refs,
        ),
        warnings=harness_result.warnings + warnings,
    )


def _merge_unique(*groups: tuple[_T, ...]) -> tuple[_T, ...]:
    merged: list[_T] = []
    seen: set[_T] = set()
    for group in groups:
        for item in group:
            if item in seen:
                continue
            seen.add(item)
            merged.append(item)
    return tuple(merged)


__all__ = [
    "EvaluationPacket",
    "EvaluationPacketKind",
    "WithheldField",
    "build_evaluation_packet",
]
