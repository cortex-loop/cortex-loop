"""Typed goal-debt and closure-pressure state over bounded runtime signals."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from numbers import Real

from .brake import BrakeState


def _clip_unit(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


@dataclass(frozen=True, slots=True)
class GoalDebtState:
    unfinished_goal_debt: float
    contradiction_rejection_debt: float
    verification_debt: float
    quota_burden_stop_pressure: float

    def __post_init__(self) -> None:
        for field_name in asdict(self):
            value = getattr(self, field_name)
            if not isinstance(value, Real):
                actual_type = type(value).__name__
                raise TypeError(f"GoalDebtState.{field_name} must be numeric, got {actual_type}.")
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(f"GoalDebtState.{field_name} must be between 0.0 and 1.0.")

    def as_payload(self) -> dict[str, float]:
        return {
            field_name: round(float(value), 4)
            for field_name, value in asdict(self).items()
        }


@dataclass(frozen=True, slots=True)
class ClosurePressureState:
    goal_debt: GoalDebtState
    closure_pressure: float
    closure_required: bool
    closure_reason_tags: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.goal_debt, GoalDebtState):
            actual_type = type(self.goal_debt).__name__
            raise TypeError(
                "ClosurePressureState.goal_debt must be GoalDebtState, "
                f"got {actual_type}."
            )
        if not isinstance(self.closure_required, bool):
            actual_type = type(self.closure_required).__name__
            raise TypeError(
                "ClosurePressureState.closure_required must be bool, "
                f"got {actual_type}."
            )
        if not isinstance(self.closure_pressure, Real):
            actual_type = type(self.closure_pressure).__name__
            raise TypeError(
                "ClosurePressureState.closure_pressure must be numeric, "
                f"got {actual_type}."
            )
        if not 0.0 <= float(self.closure_pressure) <= 1.0:
            raise ValueError(
                "ClosurePressureState.closure_pressure must be between 0.0 and 1.0."
            )
        if any(not (isinstance(tag, str) and tag.strip()) for tag in self.closure_reason_tags):
            raise ValueError(
                "ClosurePressureState.closure_reason_tags must contain only non-empty values."
            )


def build_goal_debt_state(
    *,
    active_track_ref: str,
    pending_goal_refs: tuple[str, ...],
    continuity_warnings: tuple[str, ...],
    continuity_reminders: tuple[str, ...],
    degradation_pressure_bonus: int,
    sustained_spike_flags: tuple[str, ...],
    repeated_failure_pressure: float,
    verification_conflict_pressure: float,
    quota_pressure: float,
    brake_state: BrakeState,
) -> GoalDebtState:
    if not isinstance(brake_state, BrakeState):
        actual_type = type(brake_state).__name__
        raise TypeError(
            "build_goal_debt_state.brake_state must be BrakeState, "
            f"got {actual_type}."
        )

    continuity_rejection_present = any(
        warning.startswith("continuity-rejected:")
        for warning in continuity_warnings
    )
    unfinished_goal_debt = 0.0
    if pending_goal_refs or continuity_reminders:
        unfinished_goal_debt = 1.0
    elif active_track_ref != "main":
        unfinished_goal_debt = 0.7

    contradiction_rejection_debt = _clip_unit(
        (1.0 if continuity_rejection_present else 0.0)
        + (0.20 * float(min(3, degradation_pressure_bonus)))
        + (0.15 if sustained_spike_flags else 0.0)
        + (0.20 * float(repeated_failure_pressure))
    )
    verification_debt = _clip_unit(
        float(verification_conflict_pressure)
        + (0.10 if continuity_rejection_present else 0.0)
    )
    quota_burden_stop_pressure = _clip_unit(
        float(quota_pressure)
        + (0.15 if brake_state is BrakeState.GUARDED else 0.0)
        + (0.25 if brake_state is BrakeState.LATCHED else 0.0)
    )
    return GoalDebtState(
        unfinished_goal_debt=unfinished_goal_debt,
        contradiction_rejection_debt=contradiction_rejection_debt,
        verification_debt=verification_debt,
        quota_burden_stop_pressure=quota_burden_stop_pressure,
    )


def build_closure_pressure_state(
    *,
    active_track_ref: str,
    pending_goal_refs: tuple[str, ...],
    continuity_warnings: tuple[str, ...],
    continuity_reminders: tuple[str, ...],
    degradation_pressure_bonus: int,
    sustained_spike_flags: tuple[str, ...],
    repeated_failure_pressure: float,
    verification_conflict_pressure: float,
    quota_pressure: float,
    brake_state: BrakeState,
) -> ClosurePressureState:
    goal_debt = build_goal_debt_state(
        active_track_ref=active_track_ref,
        pending_goal_refs=pending_goal_refs,
        continuity_warnings=continuity_warnings,
        continuity_reminders=continuity_reminders,
        degradation_pressure_bonus=degradation_pressure_bonus,
        sustained_spike_flags=sustained_spike_flags,
        repeated_failure_pressure=repeated_failure_pressure,
        verification_conflict_pressure=verification_conflict_pressure,
        quota_pressure=quota_pressure,
        brake_state=brake_state,
    )
    tags: set[str] = set()
    continuity_rejection_present = any(
        warning.startswith("continuity-rejected:")
        for warning in continuity_warnings
    )
    if pending_goal_refs:
        tags.add("pending_goal_debt")
    if continuity_rejection_present:
        tags.add("continuity_rejection")
    if continuity_reminders:
        tags.add("continuity_reminder")
    if brake_state is BrakeState.LATCHED:
        tags.add("latched_brake")
    if degradation_pressure_bonus > 0:
        tags.add("degradation_pressure")
    if sustained_spike_flags:
        tags.add("contradiction_spike")

    closure_pressure = max(
        goal_debt.unfinished_goal_debt,
        goal_debt.contradiction_rejection_debt,
        goal_debt.verification_debt,
        goal_debt.quota_burden_stop_pressure,
    )
    return ClosurePressureState(
        goal_debt=goal_debt,
        closure_pressure=closure_pressure,
        closure_required=bool(tags),
        closure_reason_tags=tuple(sorted(tags)),
    )


__all__ = [
    "ClosurePressureState",
    "GoalDebtState",
    "build_closure_pressure_state",
    "build_goal_debt_state",
]
