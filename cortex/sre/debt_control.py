"""Bounded debt-control pressure derived from expectation and goal debt."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from numbers import Real
from typing import TYPE_CHECKING, Any

from .expectations import ResolutionDeficitState

if TYPE_CHECKING:
    from .goal_debt import GoalDebtState


def _clip_unit(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


@dataclass(frozen=True, slots=True)
class DebtControlPressure:
    """Internal pressure view for routing/brake control.

    This is diagnostic control state only. It must not be rendered into
    model-visible text.
    """

    resolution_pressure: float = 0.0
    persistence: float = 0.0
    forward_commit_pressure: float = 0.0
    goal_drag: float = 0.0
    debt_pressure: float = 0.0
    verification_relief_bias: float = 0.0
    reason_tags: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        for field_name in (
            "resolution_pressure",
            "persistence",
            "forward_commit_pressure",
            "goal_drag",
            "debt_pressure",
            "verification_relief_bias",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, Real):
                actual_type = type(value).__name__
                raise TypeError(
                    f"DebtControlPressure.{field_name} must be numeric, got {actual_type}."
                )
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(
                    f"DebtControlPressure.{field_name} must be between 0.0 and 1.0."
                )
        if any(not tag.strip() for tag in self.reason_tags):
            raise ValueError(
                "DebtControlPressure.reason_tags must contain only non-empty values."
            )

    def as_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            key: round(float(value), 4)
            for key, value in asdict(self).items()
            if key != "reason_tags"
        }
        payload["reason_tags"] = sorted(self.reason_tags)
        return payload


def build_debt_control_pressure(
    *,
    resolution_deficit: ResolutionDeficitState,
    goal_debt: "GoalDebtState",
    task_mode: Any,
) -> DebtControlPressure:
    from .goal_debt import GoalDebtState

    if not isinstance(resolution_deficit, ResolutionDeficitState):
        actual_type = type(resolution_deficit).__name__
        raise TypeError(
            "build_debt_control_pressure.resolution_deficit must be "
            f"ResolutionDeficitState, got {actual_type}."
        )
    if not isinstance(goal_debt, GoalDebtState):
        actual_type = type(goal_debt).__name__
        raise TypeError(
            f"build_debt_control_pressure.goal_debt must be GoalDebtState, got {actual_type}."
        )

    task_mode_value = _task_mode_value(task_mode)
    forward_commit_pressure = _forward_commit_pressure(task_mode_value)
    resolution_pressure = _clip_unit(resolution_deficit.negative_prediction_error)
    overdue_ratio = _overdue_ratio(resolution_deficit)
    persistence = _clip_unit((0.70 * resolution_pressure) + (0.30 * overdue_ratio))
    goal_drag = _clip_unit(
        (
            (0.60 * float(goal_debt.unfinished_goal_debt))
            + (0.40 * float(goal_debt.verification_debt))
        )
        * persistence
        * forward_commit_pressure
    )
    debt_pressure = _clip_unit((0.60 * resolution_pressure) + (0.40 * goal_drag))
    verification_relief_bias = _clip_unit(
        max(resolution_pressure, goal_debt.verification_debt) * (1.0 - forward_commit_pressure)
    )

    reason_tags: set[str] = {f"task_mode:{task_mode_value}"}
    if resolution_pressure > 0.0:
        reason_tags.add("resolution-deficit")
    if resolution_deficit.overdue_weight > 0.0:
        reason_tags.add("overdue-expectation")
    if goal_drag > 0.0:
        reason_tags.add("goal-drag")
    if verification_relief_bias > 0.0:
        reason_tags.add("verification-relief")

    return DebtControlPressure(
        resolution_pressure=resolution_pressure,
        persistence=persistence,
        forward_commit_pressure=forward_commit_pressure,
        goal_drag=goal_drag,
        debt_pressure=debt_pressure,
        verification_relief_bias=verification_relief_bias,
        reason_tags=frozenset(reason_tags),
    )


def build_runtime_debt_control_pressure(
    *,
    resolution_deficit: ResolutionDeficitState,
    task_mode: Any,
    active_track_ref: str,
    pending_goal_refs: tuple[str, ...],
    continuity_warnings: tuple[str, ...],
    continuity_reminders: tuple[str, ...],
    degradation_pressure_bonus: int,
    sustained_spike_flags: tuple[str, ...],
    prior_brake_state: Any = None,
) -> DebtControlPressure:
    from .brake import BrakeState
    from .goal_debt import build_goal_debt_state

    brake_state = prior_brake_state if isinstance(prior_brake_state, BrakeState) else BrakeState.QUIESCENT
    verification_conflict_pressure = (
        resolution_deficit.negative_prediction_error
        if resolution_deficit.dominant_deficit_kind == "verification"
        else 0.0
    )
    goal_debt = build_goal_debt_state(
        active_track_ref=active_track_ref,
        pending_goal_refs=pending_goal_refs,
        continuity_warnings=continuity_warnings,
        continuity_reminders=continuity_reminders,
        degradation_pressure_bonus=degradation_pressure_bonus,
        sustained_spike_flags=sustained_spike_flags,
        repeated_failure_pressure=0.0,
        verification_conflict_pressure=verification_conflict_pressure,
        quota_pressure=0.0,
        brake_state=brake_state,
    )
    return build_debt_control_pressure(
        resolution_deficit=resolution_deficit,
        goal_debt=goal_debt,
        task_mode=task_mode,
    )


def _task_mode_value(task_mode: Any) -> str:
    value = getattr(task_mode, "value", task_mode)
    if not isinstance(value, str) or not value.strip():
        actual_type = type(task_mode).__name__
        raise TypeError(
            "build_debt_control_pressure.task_mode must be an OperatorTaskMode-like "
            f"value, got {actual_type}."
        )
    return value.strip()


def _forward_commit_pressure(task_mode_value: str) -> float:
    if task_mode_value == "execute":
        return 1.0
    if task_mode_value == "resume_execute":
        return 0.75
    if task_mode_value == "inspect":
        return 0.0
    return 0.0


def _overdue_ratio(resolution_deficit: ResolutionDeficitState) -> float:
    denominator = max(
        0.1,
        float(resolution_deficit.due_weight)
        + float(resolution_deficit.overdue_weight)
        + float(resolution_deficit.suspended_weight),
    )
    return _clip_unit(float(resolution_deficit.overdue_weight) / denominator)


__all__ = [
    "DebtControlPressure",
    "build_debt_control_pressure",
    "build_runtime_debt_control_pressure",
]
