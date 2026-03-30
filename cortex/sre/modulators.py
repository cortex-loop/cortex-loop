"""Compact SRE modulator carriers and update law."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from numbers import Real


def _clip_unit(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


@dataclass(frozen=True, slots=True)
class ExecutiveModulatorInputs:
    uncertainty: float
    repeated_failure_pressure: float
    quota_pressure: float
    continuity_demand: float
    novelty_pressure: float

    def __post_init__(self) -> None:
        for field_name in (
            "uncertainty",
            "repeated_failure_pressure",
            "quota_pressure",
            "continuity_demand",
            "novelty_pressure",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, Real):
                actual_type = type(value).__name__
                raise TypeError(
                    f"ExecutiveModulatorInputs.{field_name} must be numeric, got {actual_type}."
                )
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(
                    f"ExecutiveModulatorInputs.{field_name} must be between 0.0 and 1.0."
                )

    def as_vector(self) -> tuple[float, ...]:
        return (
            float(self.uncertainty),
            float(self.repeated_failure_pressure),
            float(self.quota_pressure),
            float(self.continuity_demand),
            float(self.novelty_pressure),
        )


@dataclass(frozen=True, slots=True)
class ExecutiveModulatorState:
    focus_gain: float
    explore_gain: float
    stop_pressure: float
    update_pressure: float

    def __post_init__(self) -> None:
        for field_name in (
            "focus_gain",
            "explore_gain",
            "stop_pressure",
            "update_pressure",
        ):
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
    inputs: ExecutiveModulatorInputs
    state: ExecutiveModulatorState
    reason_tags: frozenset[str]

    def __post_init__(self) -> None:
        if not isinstance(self.inputs, ExecutiveModulatorInputs):
            actual_type = type(self.inputs).__name__
            raise TypeError(
                "ExecutiveModulatorUpdate.inputs must be ExecutiveModulatorInputs, "
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


ZERO_EXECUTIVE_MODULATOR_UPDATE = ExecutiveModulatorUpdate(
    inputs=ExecutiveModulatorInputs(
        uncertainty=0.0,
        repeated_failure_pressure=0.0,
        quota_pressure=0.0,
        continuity_demand=0.0,
        novelty_pressure=0.0,
    ),
    state=ExecutiveModulatorState(
        focus_gain=0.0,
        explore_gain=0.0,
        stop_pressure=0.0,
        update_pressure=0.0,
    ),
    reason_tags=frozenset(),
)


def update_executive_modulators(
    inputs: ExecutiveModulatorInputs,
) -> ExecutiveModulatorUpdate:
    if not isinstance(inputs, ExecutiveModulatorInputs):
        actual_type = type(inputs).__name__
        raise TypeError(
            "update_executive_modulators.inputs must be ExecutiveModulatorInputs, "
            f"got {actual_type}."
        )

    focus_gain = _clip_unit(
        0.15
        + (0.55 * inputs.continuity_demand)
        - (0.30 * inputs.uncertainty)
        - (0.35 * inputs.repeated_failure_pressure)
    )
    explore_gain = _clip_unit(
        0.05
        + (0.45 * inputs.uncertainty)
        + (0.40 * inputs.repeated_failure_pressure)
        - (0.25 * inputs.continuity_demand)
    )
    stop_pressure = _clip_unit(
        (0.65 * inputs.quota_pressure)
        + (0.35 * inputs.repeated_failure_pressure)
        + (0.15 * inputs.uncertainty)
    )
    update_pressure = _clip_unit(
        0.10
        + (0.50 * inputs.novelty_pressure)
        + (0.30 * inputs.uncertainty)
        - (0.20 * inputs.continuity_demand)
    )

    reason_tags: set[str] = set()
    if inputs.uncertainty >= 0.60:
        reason_tags.add("high_uncertainty")
    if inputs.repeated_failure_pressure >= 0.50:
        reason_tags.add("repeated_failure")
    if inputs.quota_pressure >= 0.60:
        reason_tags.add("quota_pressure")
    if inputs.continuity_demand >= 0.60:
        reason_tags.add("continuity_bias")
    if inputs.novelty_pressure >= 0.50:
        reason_tags.add("novelty_bias")

    return ExecutiveModulatorUpdate(
        inputs=inputs,
        state=ExecutiveModulatorState(
            focus_gain=focus_gain,
            explore_gain=explore_gain,
            stop_pressure=stop_pressure,
            update_pressure=update_pressure,
        ),
        reason_tags=frozenset(reason_tags),
    )


__all__ = [
    "ExecutiveModulatorInputs",
    "ExecutiveModulatorState",
    "ExecutiveModulatorUpdate",
    "ZERO_EXECUTIVE_MODULATOR_UPDATE",
    "update_executive_modulators",
]
