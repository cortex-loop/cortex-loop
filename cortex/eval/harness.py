"""Minimal contradiction-preserving evaluation harness composition."""

from __future__ import annotations

from dataclasses import dataclass, field

from cortex.core.commitments import CommitmentStatus
from cortex.core.errors import ContradictionRecord, DegradationRecord

from .artifacts import BlockerFragment, CurrentPairFragment, EventTraceArtifact


@dataclass(frozen=True, slots=True)
class EvaluationHarnessResult:
    event_trace: EventTraceArtifact
    current_pair: CurrentPairFragment | None = None
    blocker: BlockerFragment | None = None
    contradiction_refs: tuple[ContradictionRecord, ...] = field(default_factory=tuple)
    degradation_refs: tuple[DegradationRecord, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not isinstance(self.event_trace, EventTraceArtifact):
            actual_type = type(self.event_trace).__name__
            raise TypeError(
                "EvaluationHarnessResult.event_trace must be EventTraceArtifact, "
                f"got {actual_type}.",
            )
        if self.current_pair is not None and not isinstance(self.current_pair, CurrentPairFragment):
            actual_type = type(self.current_pair).__name__
            raise TypeError(
                "EvaluationHarnessResult.current_pair must be CurrentPairFragment | None, "
                f"got {actual_type}.",
            )
        if self.blocker is not None and not isinstance(self.blocker, BlockerFragment):
            actual_type = type(self.blocker).__name__
            raise TypeError(
                "EvaluationHarnessResult.blocker must be BlockerFragment | None, "
                f"got {actual_type}.",
            )
        _validate_typed_tuple(
            self.contradiction_refs,
            ContradictionRecord,
            "EvaluationHarnessResult.contradiction_refs",
        )
        _validate_typed_tuple(
            self.degradation_refs,
            DegradationRecord,
            "EvaluationHarnessResult.degradation_refs",
        )
        _validate_warning_tuple(self.warnings, "EvaluationHarnessResult.warnings")
        has_current_pair = self.current_pair is not None
        has_blocker = self.blocker is not None
        if has_current_pair == has_blocker:
            raise ValueError(
                "EvaluationHarnessResult requires exactly one of current_pair or blocker",
            )
        if has_current_pair and self.current_pair.event_trace != self.event_trace:
            raise ValueError(
                "EvaluationHarnessResult current_pair.event_trace must match event_trace",
            )
        if has_current_pair and self.current_pair.verdict_status is CommitmentStatus.BLOCKED:
            raise ValueError(
                "EvaluationHarnessResult current_pair cannot carry CommitmentStatus.BLOCKED; use blocker",
            )


def build_evaluation_harness_result(
    *,
    event_trace: EventTraceArtifact,
    current_pair: CurrentPairFragment | None = None,
    blocker: BlockerFragment | None = None,
    contradiction_refs: tuple[ContradictionRecord, ...] = (),
    degradation_refs: tuple[DegradationRecord, ...] = (),
    warnings: tuple[str, ...] = (),
) -> EvaluationHarnessResult:
    return EvaluationHarnessResult(
        event_trace=event_trace,
        current_pair=current_pair,
        blocker=blocker,
        contradiction_refs=contradiction_refs,
        degradation_refs=degradation_refs,
        warnings=warnings,
    )


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
    "EvaluationHarnessResult",
    "build_evaluation_harness_result",
]
