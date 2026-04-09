"""Compact SRE policy-view derivation from summary and modulator state."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from numbers import Real

from .executive_summary import ExecutiveSignalSummary
from .modulators import ExecutiveModulatorState


def _clip_unit(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


@dataclass(frozen=True, slots=True)
class ExecutivePolicyView:
    default_profile_bonus: float
    switch_margin: float
    stop_threshold: float
    allow_extra_read_pass: bool
    verification_intensity: float

    def __post_init__(self) -> None:
        for field_name in (
            "default_profile_bonus",
            "switch_margin",
            "stop_threshold",
            "verification_intensity",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, Real):
                actual_type = type(value).__name__
                raise TypeError(
                    f"ExecutivePolicyView.{field_name} must be numeric, got {actual_type}."
                )
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(
                    f"ExecutivePolicyView.{field_name} must be between 0.0 and 1.0."
                )
        if not isinstance(self.allow_extra_read_pass, bool):
            actual_type = type(self.allow_extra_read_pass).__name__
            raise TypeError(
                "ExecutivePolicyView.allow_extra_read_pass must be bool, "
                f"got {actual_type}."
            )

    def as_payload(self) -> dict[str, float | bool]:
        payload = asdict(self)
        for key in ("default_profile_bonus", "switch_margin", "stop_threshold", "verification_intensity"):
            payload[key] = round(float(payload[key]), 4)
        return payload


def build_executive_policy_view(
    summary: ExecutiveSignalSummary,
    modulators: ExecutiveModulatorState,
) -> ExecutivePolicyView:
    if not isinstance(summary, ExecutiveSignalSummary):
        actual_type = type(summary).__name__
        raise TypeError(
            "build_executive_policy_view.summary must be ExecutiveSignalSummary, "
            f"got {actual_type}."
        )
    if not isinstance(modulators, ExecutiveModulatorState):
        actual_type = type(modulators).__name__
        raise TypeError(
            "build_executive_policy_view.modulators must be ExecutiveModulatorState, "
            f"got {actual_type}."
        )

    default_profile_bonus = min(
        0.20,
        (0.12 * modulators.focus_gain) + (0.04 * summary.continuity_demand),
    )
    switch_margin = max(
        0.0,
        min(
            0.20,
            0.08 + (0.08 * modulators.focus_gain) - (0.08 * modulators.explore_gain),
        ),
    )
    stop_threshold = max(
        0.40,
        min(
            0.75,
            0.75
            - (0.20 * summary.quota_pressure)
            - (0.10 * summary.verification_conflict_pressure)
            + (0.05 * summary.continuity_demand),
        ),
    )
    allow_extra_read_pass = (
        modulators.update_pressure >= 0.50
        and summary.uncertainty >= 0.35
        and summary.quota_pressure < 0.60
    )
    verification_intensity = _clip_unit(
        0.30
        + (0.50 * modulators.focus_gain)
        + (0.20 * modulators.update_pressure)
    )
    return ExecutivePolicyView(
        default_profile_bonus=default_profile_bonus,
        switch_margin=switch_margin,
        stop_threshold=stop_threshold,
        allow_extra_read_pass=allow_extra_read_pass,
        verification_intensity=verification_intensity,
    )


__all__ = [
    "ExecutivePolicyView",
    "build_executive_policy_view",
]
