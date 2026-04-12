"""Typed support-memory priors for bounded allocation law."""

from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite
from numbers import Real

from cortex.core.envelopes import MetadataField
from cortex.core.support import SupportReference

from .families import SoftControlFamily


def _validate_unit_score(value: float, *, field_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, Real):
        actual_type = type(value).__name__
        raise TypeError(f"{field_name} must be numeric, got {actual_type}.")
    if not isfinite(float(value)):
        raise ValueError(f"{field_name} must be finite.")
    if not 0.0 <= float(value) <= 1.0:
        raise ValueError(f"{field_name} must be between 0.0 and 1.0.")


def _validate_text_values(
    values: frozenset[str] | tuple[str, ...],
    *,
    field_name: str,
) -> None:
    if any(not (isinstance(value, str) and value.strip()) for value in values):
        raise ValueError(f"{field_name} must contain only non-empty values after trimming.")


def _validate_metadata(
    metadata: tuple[MetadataField, ...],
    *,
    field_name: str,
) -> None:
    if not isinstance(metadata, tuple):
        actual_type = type(metadata).__name__
        raise TypeError(f"{field_name} must be tuple[MetadataField, ...], got {actual_type}.")
    if any(not isinstance(item, MetadataField) for item in metadata):
        raise TypeError(f"{field_name} must contain only MetadataField instances.")


@dataclass(frozen=True, slots=True)
class SupportMemoryPriorScore:
    family: SoftControlFamily
    score: float
    reason_tags: frozenset[str] = field(default_factory=frozenset)
    support_refs: tuple[SupportReference, ...] = field(default_factory=tuple)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not isinstance(self.family, SoftControlFamily):
            actual_type = type(self.family).__name__
            raise TypeError(
                "SupportMemoryPriorScore.family must be SoftControlFamily, "
                f"got {actual_type}."
            )
        _validate_unit_score(self.score, field_name="SupportMemoryPriorScore.score")
        _validate_text_values(
            self.reason_tags,
            field_name="SupportMemoryPriorScore.reason_tags",
        )
        if any(not isinstance(reference, SupportReference) for reference in self.support_refs):
            raise TypeError(
                "SupportMemoryPriorScore.support_refs must contain only SupportReference instances."
            )
        _validate_metadata(
            self.metadata,
            field_name="SupportMemoryPriorScore.metadata",
        )


@dataclass(frozen=True, slots=True)
class SupportMemoryPriorAppendix:
    scores: tuple[SupportMemoryPriorScore, ...] = field(default_factory=tuple)
    appendix_tags: frozenset[str] = field(default_factory=frozenset)
    notes: tuple[str, ...] = field(default_factory=tuple)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if any(not isinstance(score, SupportMemoryPriorScore) for score in self.scores):
            raise TypeError(
                "SupportMemoryPriorAppendix.scores must contain only SupportMemoryPriorScore instances."
            )
        seen_families: set[SoftControlFamily] = set()
        for score in self.scores:
            if score.family in seen_families:
                raise ValueError(
                    "SupportMemoryPriorAppendix.scores must contain at most one score per family."
                )
            seen_families.add(score.family)
        _validate_text_values(
            self.appendix_tags,
            field_name="SupportMemoryPriorAppendix.appendix_tags",
        )
        _validate_text_values(
            self.notes,
            field_name="SupportMemoryPriorAppendix.notes",
        )
        _validate_metadata(
            self.metadata,
            field_name="SupportMemoryPriorAppendix.metadata",
        )

    def score_for(self, family: SoftControlFamily) -> SupportMemoryPriorScore:
        if not isinstance(family, SoftControlFamily):
            actual_type = type(family).__name__
            raise TypeError(
                "SupportMemoryPriorAppendix.score_for.family must be SoftControlFamily, "
                f"got {actual_type}."
            )
        for score in self.scores:
            if score.family is family:
                return score
        return SupportMemoryPriorScore(family=family, score=0.0)

    @property
    def active(self) -> bool:
        return any(score.score > 0.0 for score in self.scores)


__all__ = [
    "SupportMemoryPriorAppendix",
    "SupportMemoryPriorScore",
]
