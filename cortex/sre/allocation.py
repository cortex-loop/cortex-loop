"""Small typed allocation-score carriers for neutral-dominance checks."""

from __future__ import annotations

from dataclasses import dataclass, field

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


@dataclass(frozen=True, slots=True)
class AllocationScorecard:
    scores: tuple[AllocationScore, ...]
    activation_threshold: float


__all__ = ["AllocationScore", "AllocationScorecard"]
