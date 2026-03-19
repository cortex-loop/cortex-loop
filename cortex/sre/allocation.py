"""Small typed allocation-score carriers for neutral-dominance checks."""

from __future__ import annotations

from dataclasses import dataclass, field
from numbers import Real

from .families import SoftControlFamily


@dataclass(frozen=True, slots=True)
class AllocationScore:
    family: SoftControlFamily
    score: float
    admissible: bool = True
    reason_tags: frozenset[str] = field(default_factory=frozenset)

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


@dataclass(frozen=True, slots=True)
class AllocationScorecard:
    scores: tuple[AllocationScore, ...]
    activation_threshold: float

    def __post_init__(self) -> None:
        if any(not isinstance(score, AllocationScore) for score in self.scores):
            raise TypeError(
                "AllocationScorecard.scores must contain only AllocationScore instances."
            )


__all__ = ["AllocationScore", "AllocationScorecard"]
