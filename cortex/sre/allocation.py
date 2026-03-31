"""Small typed allocation-score carriers for neutral-dominance checks."""

from __future__ import annotations

from dataclasses import dataclass, field
from numbers import Real
from typing import Any

from .families import SoftControlFamily


@dataclass(frozen=True, slots=True)
class AllocationScore:
    family: SoftControlFamily
    score: float
    admissible: bool = True
    reason_tags: frozenset[str] = field(default_factory=frozenset)
    online_score: float | None = None
    memory_score: float = 0.0
    allocated_score: float | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.family, SoftControlFamily):
            actual_type = type(self.family).__name__
            raise TypeError(
                "AllocationScore.family must be SoftControlFamily, "
                f"got {actual_type}."
            )
        if not isinstance(self.score, Real):
            actual_type = type(self.score).__name__
            raise TypeError(
                "AllocationScore.score must be numeric, "
                f"got {actual_type}."
            )
        if not isinstance(self.admissible, bool):
            actual_type = type(self.admissible).__name__
            raise TypeError(
                "AllocationScore.admissible must be bool, "
                f"got {actual_type}."
            )
        if any(not tag.strip() for tag in self.reason_tags):
            raise ValueError(
                "AllocationScore.reason_tags must contain only non-empty values "
                "after trimming."
            )
        if self.online_score is not None and not isinstance(self.online_score, Real):
            actual_type = type(self.online_score).__name__
            raise TypeError(
                "AllocationScore.online_score must be numeric when provided, "
                f"got {actual_type}."
            )
        if not isinstance(self.memory_score, Real):
            actual_type = type(self.memory_score).__name__
            raise TypeError(
                "AllocationScore.memory_score must be numeric, "
                f"got {actual_type}."
            )
        if self.allocated_score is not None and not isinstance(self.allocated_score, Real):
            actual_type = type(self.allocated_score).__name__
            raise TypeError(
                "AllocationScore.allocated_score must be numeric when provided, "
                f"got {actual_type}."
            )
        object.__setattr__(
            self,
            "allocated_score",
            float(self.score) if self.allocated_score is None else float(self.allocated_score),
        )
        object.__setattr__(
            self,
            "online_score",
            self.allocated_score if self.online_score is None else float(self.online_score),
        )

    def as_summary(self) -> dict[str, Any]:
        return {
            "family": self.family.value,
            "online_score": self.online_score,
            "memory_score": float(self.memory_score),
            "allocated_score": self.allocated_score,
            "admissible": self.admissible,
            "reason_tags": sorted(self.reason_tags),
        }


@dataclass(frozen=True, slots=True)
class AllocationScorecard:
    scores: tuple[AllocationScore, ...]
    activation_threshold: float
    alpha_t: float = 1.0

    def __post_init__(self) -> None:
        if any(not isinstance(score, AllocationScore) for score in self.scores):
            raise TypeError(
                "AllocationScorecard.scores must contain only AllocationScore instances."
            )
        if not isinstance(self.activation_threshold, Real):
            actual_type = type(self.activation_threshold).__name__
            raise TypeError(
                "AllocationScorecard.activation_threshold must be numeric, "
                f"got {actual_type}."
            )
        if not isinstance(self.alpha_t, Real):
            actual_type = type(self.alpha_t).__name__
            raise TypeError(
                "AllocationScorecard.alpha_t must be numeric, "
                f"got {actual_type}."
            )
        if not 0.0 <= float(self.alpha_t) <= 1.0:
            raise ValueError("AllocationScorecard.alpha_t must be between 0.0 and 1.0.")


def build_allocation_diagnostics_payload(
    scorecard: AllocationScorecard,
    *,
    selected_delta_over_neutral: float,
    mediation_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not isinstance(scorecard, AllocationScorecard):
        actual_type = type(scorecard).__name__
        raise TypeError(
            "build_allocation_diagnostics_payload.scorecard must be AllocationScorecard, "
            f"got {actual_type}."
        )
    if not isinstance(selected_delta_over_neutral, Real):
        actual_type = type(selected_delta_over_neutral).__name__
        raise TypeError(
            "build_allocation_diagnostics_payload.selected_delta_over_neutral must be numeric, "
            f"got {actual_type}."
        )
    if mediation_payload is not None and not isinstance(mediation_payload, dict):
        actual_type = type(mediation_payload).__name__
        raise TypeError(
            "build_allocation_diagnostics_payload.mediation_payload must be "
            f"dict[str, Any] | None, got {actual_type}."
        )
    payload = {
        "alpha_t": float(scorecard.alpha_t),
        "activation_threshold": float(scorecard.activation_threshold),
        "selected_delta_over_neutral": float(selected_delta_over_neutral),
        "scores": [score.as_summary() for score in scorecard.scores],
    }
    if mediation_payload is not None:
        payload["mediation"] = mediation_payload
    return payload


__all__ = [
    "AllocationScore",
    "AllocationScorecard",
    "build_allocation_diagnostics_payload",
]
