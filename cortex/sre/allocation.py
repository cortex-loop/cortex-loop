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


@dataclass(frozen=True, slots=True)
class AllocationScorecard:
    scores: tuple[AllocationScore, ...]
    activation_threshold: float


__all__ = ["AllocationScore", "AllocationScorecard"]
