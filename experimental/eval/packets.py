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

    def __post_init__(self) -> None:
        if not isinstance(self.field_ref, str):
            actual_type = type(self.field_ref).__name__
            raise TypeError(
                f"WithheldField.field_ref must be str, got {actual_type}.",
            )
        if not isinstance(self.reason_code, str):
            actual_type = type(self.reason_code).__name__
            raise TypeError(
                f"WithheldField.reason_code must be str, got {actual_type}.",
            )
        if not self.field_ref.strip():
            raise ValueError("WithheldField.field_ref must be non-empty after trimming.")
        if not self.reason_code.strip():
            raise ValueError("WithheldField.reason_code must be non-empty after trimming.")


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
        if not isinstance(self.harness_result, EvaluationHarnessResult):
            actual_type = type(self.harness_result).__name__
            raise TypeError(
                "EvaluationPacket.harness_result must be EvaluationHarnessResult, "
                f"got {actual_type}.",
            )
        if not isinstance(self.packet_kind, EvaluationPacketKind):
            actual_type = type(self.packet_kind).__name__
            raise TypeError(
                "EvaluationPacket.packet_kind must be EvaluationPacketKind, "
                f"got {actual_type}.",
            )
        if self.current_pair is not None and not isinstance(self.current_pair, CurrentPairFragment):
            actual_type = type(self.current_pair).__name__
            raise TypeError(
                "EvaluationPacket.current_pair must be CurrentPairFragment | None, "
                f"got {actual_type}.",
            )
        if self.blocker is not None and not isinstance(self.blocker, BlockerFragment):
            actual_type = type(self.blocker).__name__
            raise TypeError(
                "EvaluationPacket.blocker must be BlockerFragment | None, "
                f"got {actual_type}.",
            )
        _validate_typed_tuple(
            self.withheld_fields,
            WithheldField,
            "EvaluationPacket.withheld_fields",
        )
        _validate_typed_tuple(
            self.contradiction_refs,
            ContradictionRecord,
            "EvaluationPacket.contradiction_refs",
        )
        _validate_typed_tuple(
            self.degradation_refs,
            DegradationRecord,
            "EvaluationPacket.degradation_refs",
        )
        _validate_warning_tuple(self.warnings, "EvaluationPacket.warnings")
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
    if not isinstance(harness_result, EvaluationHarnessResult):
        actual_type = type(harness_result).__name__
        raise TypeError(
            "build_evaluation_packet.harness_result must be EvaluationHarnessResult, "
            f"got {actual_type}.",
        )
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


def _validate_typed_tuple(values: tuple[object, ...], expected_type: type[object], label: str) -> None:
    if not isinstance(values, tuple):
        actual_type = type(values).__name__
        raise TypeError(
            f"{label} must be tuple[{expected_type.__name__}, ...], got {actual_type}.",
        )
    for value in values:
        if not isinstance(value, expected_type):
            raise TypeError(
                f"{label} must contain only {expected_type.__name__} instances.",
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
    "EvaluationPacket",
    "EvaluationPacketKind",
    "WithheldField",
    "build_evaluation_packet",
]
