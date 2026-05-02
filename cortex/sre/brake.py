"""Compact brake-state evaluation for SRE uncertainty handling."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .debt_control import DebtControlPressure
from .uncertainty import UncertaintyEstimate

_LATCHING_SPIKES = frozenset(
    {
        "contradiction-expected-vs-observed",
        "sudden-degradation",
        "environment-inconsistency",
    }
)


class BrakeState(str, Enum):
    QUIESCENT = "quiescent"
    GUARDED = "guarded"
    LATCHED = "latched"


_TONIC_DECAY_RHO = 0.60
_TONIC_ENTER_GUARDED = 0.35


def _clip_unit(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


@dataclass(frozen=True, slots=True)
class BrakeTonic:
    """Smoothed EMA baseline for brake pressure across steps.

    SRE_2 §7.5 narrows the brake exit to threshold-hysteresis-only; the
    rest-side EMA (`tonic_quiescence`) is retired because the landed exit
    gate did not consume it and carrying it as diagnostics-only telemetry
    drifted doctrine from code.
    """

    tonic_pressure: float = 0.0

    def __post_init__(self) -> None:
        if not 0.0 <= float(self.tonic_pressure) <= 1.0:
            raise ValueError("BrakeTonic.tonic_pressure must be between 0.0 and 1.0.")


@dataclass(frozen=True, slots=True)
class BrakeEvaluation:
    state: BrakeState
    dominant_cause: str | None = None
    max_uncertainty: float = 0.0
    spike_tags: frozenset[str] = field(default_factory=frozenset)
    tonic: BrakeTonic | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.state, BrakeState):
            actual_type = type(self.state).__name__
            raise TypeError(
                "BrakeEvaluation.state must be BrakeState, "
                f"got {actual_type}."
            )
        if any(not tag.strip() for tag in self.spike_tags):
            raise ValueError(
                "BrakeEvaluation.spike_tags must contain only non-empty values after trimming."
            )
        if self.dominant_cause is not None and not self.dominant_cause.strip():
            raise ValueError(
                "BrakeEvaluation.dominant_cause must be non-empty after trimming when provided."
            )
        if self.tonic is not None and not isinstance(self.tonic, BrakeTonic):
            actual_type = type(self.tonic).__name__
            raise TypeError(
                f"BrakeEvaluation.tonic must be BrakeTonic when provided, got {actual_type}."
            )


def evaluate_brake_state(
    uncertainty_estimates: tuple[UncertaintyEstimate, ...],
    *,
    repeated_failures: int = 0,
    repeated_degradations: int = 0,
    missing_resume_anchor: bool = False,
    host_friction_level: float = 0.0,
    debt_control_pressure: DebtControlPressure | None = None,
    prior_state: BrakeState | None = None,
    prior_tonic: BrakeTonic | None = None,
) -> BrakeEvaluation:
    for estimate in uncertainty_estimates:
        if not isinstance(estimate, UncertaintyEstimate):
            actual_type = type(estimate).__name__
            raise TypeError(
                "evaluate_brake_state.uncertainty_estimates must contain only "
                f"UncertaintyEstimate instances, got {actual_type}."
            )
    if repeated_failures < 0:
        raise ValueError("repeated_failures must be non-negative.")
    if repeated_degradations < 0:
        raise ValueError("repeated_degradations must be non-negative.")
    if not 0.0 <= host_friction_level <= 1.0:
        raise ValueError("host_friction_level must be between 0.0 and 1.0.")
    if debt_control_pressure is not None and not isinstance(
        debt_control_pressure, DebtControlPressure
    ):
        actual_type = type(debt_control_pressure).__name__
        raise TypeError(
            "evaluate_brake_state.debt_control_pressure must be "
            f"DebtControlPressure | None, got {actual_type}."
        )
    if prior_state is not None and not isinstance(prior_state, BrakeState):
        actual_type = type(prior_state).__name__
        raise TypeError(
            "evaluate_brake_state.prior_state must be BrakeState | None, "
            f"got {actual_type}."
        )
    if prior_tonic is not None and not isinstance(prior_tonic, BrakeTonic):
        actual_type = type(prior_tonic).__name__
        raise TypeError(
            f"evaluate_brake_state.prior_tonic must be BrakeTonic | None, got {actual_type}."
        )

    max_estimate = _max_estimate(uncertainty_estimates)
    spike_tags = _all_spike_tags(uncertainty_estimates)
    next_tonic = _update_brake_tonic(
        prior_tonic=prior_tonic,
        max_uncertainty=max_estimate.level,
        host_friction_level=host_friction_level,
        spike_tags=spike_tags,
        repeated_failures=repeated_failures,
        repeated_degradations=repeated_degradations,
        debt_tonic_pressure=(
            debt_control_pressure.debt_pressure
            if debt_control_pressure is not None
            else 0.0
        ),
    )

    if (
        spike_tags & _LATCHING_SPIKES
        or repeated_failures >= 2
        or repeated_degradations >= 2
        or max_estimate.level >= 0.85
    ):
        return BrakeEvaluation(
            state=BrakeState.LATCHED,
            dominant_cause=_dominant_cause(
                max_estimate=max_estimate,
                spike_tags=spike_tags,
                repeated_failures=repeated_failures,
                repeated_degradations=repeated_degradations,
                missing_resume_anchor=missing_resume_anchor,
                host_friction_level=host_friction_level,
                debt_control_pressure=debt_control_pressure,
            ),
            max_uncertainty=max_estimate.level,
            spike_tags=spike_tags,
            tonic=next_tonic,
        )

    if _should_stay_latched(
        prior_state=prior_state,
        spike_tags=spike_tags,
        repeated_failures=repeated_failures,
        repeated_degradations=repeated_degradations,
        host_friction_level=host_friction_level,
        max_uncertainty=max_estimate.level,
    ):
        return BrakeEvaluation(
            state=BrakeState.LATCHED,
            dominant_cause=_dominant_cause(
                max_estimate=max_estimate,
                spike_tags=spike_tags,
                repeated_failures=repeated_failures,
                repeated_degradations=repeated_degradations,
                missing_resume_anchor=missing_resume_anchor,
                host_friction_level=host_friction_level,
                debt_control_pressure=debt_control_pressure,
            ),
            max_uncertainty=max_estimate.level,
            spike_tags=spike_tags,
            tonic=next_tonic,
        )

    if _should_be_guarded(
        prior_state=prior_state,
        spike_tags=spike_tags,
        repeated_failures=repeated_failures,
        repeated_degradations=repeated_degradations,
        missing_resume_anchor=missing_resume_anchor,
        host_friction_level=host_friction_level,
        max_uncertainty=max_estimate.level,
        next_tonic=next_tonic,
        debt_tonic_pressure=(
            debt_control_pressure.debt_pressure
            if debt_control_pressure is not None
            else 0.0
        ),
    ):
        return BrakeEvaluation(
            state=BrakeState.GUARDED,
            dominant_cause=_dominant_cause(
                max_estimate=max_estimate,
                spike_tags=spike_tags,
                repeated_failures=repeated_failures,
                repeated_degradations=repeated_degradations,
                missing_resume_anchor=missing_resume_anchor,
                host_friction_level=host_friction_level,
                debt_control_pressure=debt_control_pressure,
            ),
            max_uncertainty=max_estimate.level,
            spike_tags=spike_tags,
            tonic=next_tonic,
        )

    return BrakeEvaluation(
        state=BrakeState.QUIESCENT,
        dominant_cause=None,
        max_uncertainty=max_estimate.level,
        spike_tags=spike_tags,
        tonic=next_tonic,
    )


def _should_stay_latched(
    *,
    prior_state: BrakeState | None,
    spike_tags: frozenset[str],
    repeated_failures: int,
    repeated_degradations: int,
    host_friction_level: float,
    max_uncertainty: float,
) -> bool:
    if prior_state is not BrakeState.LATCHED:
        return False
    return bool(
        spike_tags & _LATCHING_SPIKES
        or repeated_failures >= 2
        or repeated_degradations >= 2
        or host_friction_level >= 0.75
        or max_uncertainty >= 0.70
    )


def _should_be_guarded(
    *,
    prior_state: BrakeState | None,
    spike_tags: frozenset[str],
    repeated_failures: int,
    repeated_degradations: int,
    missing_resume_anchor: bool,
    host_friction_level: float,
    max_uncertainty: float,
    next_tonic: BrakeTonic,
    debt_tonic_pressure: float,
) -> bool:
    # Immediate phasic entry: spike tags, contradiction, missing anchor.
    if spike_tags or missing_resume_anchor:
        return True
    # Repeated failure/degradation remain immediate (already counter-bounded).
    if repeated_failures >= 1 or repeated_degradations >= 1:
        return True
    # Soft-pressure paths: friction or uncertainty cross threshold.
    guarded_host_threshold = 0.55 if prior_state is BrakeState.GUARDED else 0.60
    guarded_uncertainty_threshold = 0.45 if prior_state is BrakeState.GUARDED else 0.55
    phasic_soft_pressure = (
        host_friction_level >= guarded_host_threshold
        or max_uncertainty >= guarded_uncertainty_threshold
    )
    debt_soft_pressure = debt_tonic_pressure >= _TONIC_ENTER_GUARDED
    if not (phasic_soft_pressure or debt_soft_pressure):
        return False
    # Already guarded — stay on phasic evidence alone (exit-side hysteresis).
    if prior_state is BrakeState.GUARDED:
        return True
    # Entry from quiescent: require tonic confirmation so a single noisy tick
    # does not flip brake state (SRE_2 §7.5 tonic-pressure gate).
    return next_tonic.tonic_pressure >= _TONIC_ENTER_GUARDED


def _update_brake_tonic(
    *,
    prior_tonic: BrakeTonic | None,
    max_uncertainty: float,
    host_friction_level: float,
    spike_tags: frozenset[str],
    repeated_failures: int,
    repeated_degradations: int,
    debt_tonic_pressure: float,
) -> BrakeTonic:
    current_pressure = _clip_unit(
        max(
            max_uncertainty,
            host_friction_level,
            debt_tonic_pressure,
            0.6 if (spike_tags & _LATCHING_SPIKES) else 0.0,
            0.5 if repeated_failures >= 1 else 0.0,
            0.5 if repeated_degradations >= 1 else 0.0,
        )
    )

    if prior_tonic is None:
        next_pressure = current_pressure
    else:
        next_pressure = _clip_unit(
            (_TONIC_DECAY_RHO * prior_tonic.tonic_pressure)
            + ((1.0 - _TONIC_DECAY_RHO) * current_pressure)
        )

    return BrakeTonic(tonic_pressure=next_pressure)


def _max_estimate(
    uncertainty_estimates: tuple[UncertaintyEstimate, ...],
) -> UncertaintyEstimate:
    if not uncertainty_estimates:
        return UncertaintyEstimate(class_tag="evidence", level=0.0)
    return max(uncertainty_estimates, key=lambda estimate: estimate.level)


def _all_spike_tags(
    uncertainty_estimates: tuple[UncertaintyEstimate, ...],
) -> frozenset[str]:
    spike_tags: set[str] = set()
    for estimate in uncertainty_estimates:
        spike_tags.update(estimate.spike_tags)
    return frozenset(spike_tags)


def _dominant_cause(
    *,
    max_estimate: UncertaintyEstimate,
    spike_tags: frozenset[str],
    repeated_failures: int,
    repeated_degradations: int,
    missing_resume_anchor: bool,
    host_friction_level: float,
    debt_control_pressure: DebtControlPressure | None,
) -> str:
    if spike_tags & _LATCHING_SPIKES:
        return sorted(spike_tags & _LATCHING_SPIKES)[0]
    if repeated_failures >= 1:
        return "repeated-failure"
    if repeated_degradations >= 1:
        return "repeated-degradation"
    if missing_resume_anchor:
        return "missing-resume-anchor"
    if host_friction_level >= 0.6:
        return "host-friction"
    if (
        debt_control_pressure is not None
        and debt_control_pressure.debt_pressure >= _TONIC_ENTER_GUARDED
    ):
        return "resolution-deficit"
    if spike_tags:
        return sorted(spike_tags)[0]
    return f"uncertainty:{max_estimate.class_tag}"


__all__ = ["BrakeEvaluation", "BrakeState", "BrakeTonic", "evaluate_brake_state"]
