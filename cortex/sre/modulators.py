"""Compact persistent SRE modulator carriers and update law."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from numbers import Real

from .executive_summary import ExecutiveSignalSummary


def _clip_unit(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


@dataclass(frozen=True, slots=True)
class ExecutiveModulatorMemory:
    focus_tonic: float
    explore_tonic: float
    stop_tonic: float
    update_tonic: float

    def __post_init__(self) -> None:
        for field_name in asdict(self):
            value = getattr(self, field_name)
            if not isinstance(value, Real):
                actual_type = type(value).__name__
                raise TypeError(
                    f"ExecutiveModulatorMemory.{field_name} must be numeric, got {actual_type}."
                )
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(
                    f"ExecutiveModulatorMemory.{field_name} must be between 0.0 and 1.0."
                )

    def as_payload(self) -> dict[str, float]:
        return {
            field_name: round(float(value), 4)
            for field_name, value in asdict(self).items()
        }


@dataclass(frozen=True, slots=True)
class ExecutiveModulatorState:
    focus_gain: float
    explore_gain: float
    stop_pressure: float
    update_pressure: float

    def __post_init__(self) -> None:
        for field_name in asdict(self):
            value = getattr(self, field_name)
            if not isinstance(value, Real):
                actual_type = type(value).__name__
                raise TypeError(
                    f"ExecutiveModulatorState.{field_name} must be numeric, got {actual_type}."
                )
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(
                    f"ExecutiveModulatorState.{field_name} must be between 0.0 and 1.0."
                )

    def as_payload(self) -> dict[str, float]:
        return {
            field_name: round(float(value), 4)
            for field_name, value in asdict(self).items()
        }


@dataclass(frozen=True, slots=True)
class ExecutiveModulatorUpdate:
    summary: ExecutiveSignalSummary
    previous_memory: ExecutiveModulatorMemory | None
    next_memory: ExecutiveModulatorMemory
    state: ExecutiveModulatorState
    reason_tags: frozenset[str]

    def __post_init__(self) -> None:
        if not isinstance(self.summary, ExecutiveSignalSummary):
            actual_type = type(self.summary).__name__
            raise TypeError(
                "ExecutiveModulatorUpdate.summary must be ExecutiveSignalSummary, "
                f"got {actual_type}."
            )
        if self.previous_memory is not None and not isinstance(
            self.previous_memory, ExecutiveModulatorMemory
        ):
            actual_type = type(self.previous_memory).__name__
            raise TypeError(
                "ExecutiveModulatorUpdate.previous_memory must be ExecutiveModulatorMemory | None, "
                f"got {actual_type}."
            )
        if not isinstance(self.next_memory, ExecutiveModulatorMemory):
            actual_type = type(self.next_memory).__name__
            raise TypeError(
                "ExecutiveModulatorUpdate.next_memory must be ExecutiveModulatorMemory, "
                f"got {actual_type}."
            )
        if not isinstance(self.state, ExecutiveModulatorState):
            actual_type = type(self.state).__name__
            raise TypeError(
                "ExecutiveModulatorUpdate.state must be ExecutiveModulatorState, "
                f"got {actual_type}."
            )
        if any(not tag.strip() for tag in self.reason_tags):
            raise ValueError(
                "ExecutiveModulatorUpdate.reason_tags must contain only non-empty values."
            )


ZERO_EXECUTIVE_MODULATOR_MEMORY = ExecutiveModulatorMemory(
    focus_tonic=0.0,
    explore_tonic=0.0,
    stop_tonic=0.0,
    update_tonic=0.0,
)

_RHO_FOCUS = 0.70
_RHO_EXPLORE = 0.55
_RHO_STOP = 0.75
_RHO_UPDATE = 0.45


def update_executive_modulators(
    summary: ExecutiveSignalSummary,
    previous: ExecutiveModulatorMemory | None = None,
) -> ExecutiveModulatorUpdate:
    if not isinstance(summary, ExecutiveSignalSummary):
        actual_type = type(summary).__name__
        raise TypeError(
            "update_executive_modulators.summary must be ExecutiveSignalSummary, "
            f"got {actual_type}."
        )
    previous_memory = previous
    if previous is None:
        previous = ZERO_EXECUTIVE_MODULATOR_MEMORY
    if not isinstance(previous, ExecutiveModulatorMemory):
        actual_type = type(previous).__name__
        raise TypeError(
            "update_executive_modulators.previous must be ExecutiveModulatorMemory | None, "
            f"got {actual_type}."
        )

    focus_drive = (
        0.15
        + (0.55 * summary.continuity_demand)
        - (0.30 * summary.uncertainty)
        - (0.35 * summary.repeated_failure_pressure)
        - (0.20 * summary.verification_conflict_pressure)
    )
    explore_drive = (
        0.05
        + (0.45 * summary.uncertainty)
        + (0.40 * summary.repeated_failure_pressure)
        - (0.25 * summary.continuity_demand)
        + (0.20 * summary.novelty_pressure)
    )
    stop_drive = (
        (0.65 * summary.quota_pressure)
        + (0.35 * summary.repeated_failure_pressure)
        + (0.15 * summary.uncertainty)
        + (0.20 * summary.verification_conflict_pressure)
    )
    update_drive = (
        0.10
        + (0.50 * summary.novelty_pressure)
        + (0.30 * summary.uncertainty)
        - (0.20 * summary.continuity_demand)
        + (0.25 * summary.verification_conflict_pressure)
    )

    if previous_memory is None:
        next_memory = ExecutiveModulatorMemory(
            focus_tonic=_clip_unit(focus_drive),
            explore_tonic=_clip_unit(explore_drive),
            stop_tonic=_clip_unit(stop_drive),
            update_tonic=_clip_unit(update_drive),
        )
    else:
        next_memory = ExecutiveModulatorMemory(
            focus_tonic=_clip_unit(
                (_RHO_FOCUS * previous.focus_tonic) + ((1.0 - _RHO_FOCUS) * focus_drive)
            ),
            explore_tonic=_clip_unit(
                (_RHO_EXPLORE * previous.explore_tonic) + ((1.0 - _RHO_EXPLORE) * explore_drive)
            ),
            stop_tonic=_clip_unit(
                (_RHO_STOP * previous.stop_tonic) + ((1.0 - _RHO_STOP) * stop_drive)
            ),
            update_tonic=_clip_unit(
                (_RHO_UPDATE * previous.update_tonic) + ((1.0 - _RHO_UPDATE) * update_drive)
            ),
        )

    state = ExecutiveModulatorState(
        focus_gain=next_memory.focus_tonic,
        explore_gain=next_memory.explore_tonic,
        stop_pressure=next_memory.stop_tonic,
        update_pressure=next_memory.update_tonic,
    )

    reason_tags: set[str] = set()
    if summary.uncertainty >= 0.60:
        reason_tags.add("high_uncertainty")
    if summary.repeated_failure_pressure >= 0.50:
        reason_tags.add("repeated_failure")
    if summary.quota_pressure >= 0.60:
        reason_tags.add("quota_pressure")
    if summary.continuity_demand >= 0.60:
        reason_tags.add("continuity_bias")
    if summary.novelty_pressure >= 0.50:
        reason_tags.add("novelty_bias")

    return ExecutiveModulatorUpdate(
        summary=summary,
        previous_memory=previous_memory,
        next_memory=next_memory,
        state=state,
        reason_tags=frozenset(reason_tags),
    )


__all__ = [
    "ExecutiveModulatorMemory",
    "ExecutiveModulatorState",
    "ExecutiveModulatorUpdate",
    "ZERO_EXECUTIVE_MODULATOR_MEMORY",
    "update_executive_modulators",
]
