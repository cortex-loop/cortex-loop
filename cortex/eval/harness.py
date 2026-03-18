"""Minimal contradiction-preserving evaluation harness composition."""

from __future__ import annotations

from dataclasses import dataclass, field

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


__all__ = [
    "EvaluationHarnessResult",
    "build_evaluation_harness_result",
]
