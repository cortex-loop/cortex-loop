"""Compact brake-state evaluation for SRE uncertainty handling."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

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


@dataclass(frozen=True, slots=True)
class BrakeEvaluation:
    state: BrakeState
    dominant_cause: str | None = None
    max_uncertainty: float = 0.0
    spike_tags: frozenset[str] = field(default_factory=frozenset)

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


def evaluate_brake_state(
    uncertainty_estimates: tuple[UncertaintyEstimate, ...],
    *,
    repeated_failures: int = 0,
    repeated_degradations: int = 0,
    missing_resume_anchor: bool = False,
    host_friction_level: float = 0.0,
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

    max_estimate = _max_estimate(uncertainty_estimates)
    spike_tags = _all_spike_tags(uncertainty_estimates)

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
            ),
            max_uncertainty=max_estimate.level,
            spike_tags=spike_tags,
        )

    if (
        spike_tags
        or repeated_failures == 1
        or repeated_degradations == 1
        or missing_resume_anchor
        or host_friction_level >= 0.6
        or max_estimate.level >= 0.55
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
            ),
            max_uncertainty=max_estimate.level,
            spike_tags=spike_tags,
        )

    return BrakeEvaluation(
        state=BrakeState.QUIESCENT,
        dominant_cause=None,
        max_uncertainty=max_estimate.level,
        spike_tags=spike_tags,
    )


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
    if spike_tags:
        return sorted(spike_tags)[0]
    return f"uncertainty:{max_estimate.class_tag}"


__all__ = ["BrakeEvaluation", "BrakeState", "evaluate_brake_state"]
