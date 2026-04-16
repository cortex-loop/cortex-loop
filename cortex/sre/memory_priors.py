"""Typed support-memory priors for bounded allocation law."""

from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite
from numbers import Real

from cortex.core.envelopes import MetadataField
from cortex.core.support import SupportReference

from .families import SoftControlFamily
from .opportunities import PROBE_FAILURE_CLASSES


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
class HostReliabilityPrior:
    timeout_rate: float = 0.0
    degradation_rate: float = 0.0
    capability_availability: float = 1.0
    contradiction_counter: int = 0
    ttl_hours: int = 24
    last_validated_at: str | None = None
    probe_failure_classes: tuple[str, ...] = field(default_factory=tuple)
    affordance_scope_tags: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        for field_name in (
            "timeout_rate",
            "degradation_rate",
            "capability_availability",
        ):
            _validate_unit_score(
                getattr(self, field_name),
                field_name=f"HostReliabilityPrior.{field_name}",
            )
        if isinstance(self.contradiction_counter, bool) or not isinstance(
            self.contradiction_counter,
            int,
        ):
            raise TypeError(
                "HostReliabilityPrior.contradiction_counter must be a non-negative integer."
            )
        if self.contradiction_counter < 0:
            raise ValueError(
                "HostReliabilityPrior.contradiction_counter must be non-negative."
            )
        if isinstance(self.ttl_hours, bool) or not isinstance(self.ttl_hours, int):
            raise TypeError("HostReliabilityPrior.ttl_hours must be a positive integer.")
        if self.ttl_hours <= 0:
            raise ValueError("HostReliabilityPrior.ttl_hours must be positive.")
        if self.last_validated_at is not None and not (
            isinstance(self.last_validated_at, str) and self.last_validated_at.strip()
        ):
            raise ValueError(
                "HostReliabilityPrior.last_validated_at must be non-empty after trimming when provided."
            )
        if any(
            not isinstance(failure_class, str) or failure_class not in PROBE_FAILURE_CLASSES
            for failure_class in self.probe_failure_classes
        ):
            raise ValueError(
                "HostReliabilityPrior.probe_failure_classes must contain only canonical probe failure classes."
            )
        if not isinstance(self.affordance_scope_tags, tuple):
            actual_type = type(self.affordance_scope_tags).__name__
            raise TypeError(
                "HostReliabilityPrior.affordance_scope_tags must be tuple[str, ...], "
                f"got {actual_type}."
            )
        _validate_text_values(
            self.affordance_scope_tags,
            field_name="HostReliabilityPrior.affordance_scope_tags",
        )


@dataclass(frozen=True, slots=True)
class SupportMemoryPriorAppendix:
    scores: tuple[SupportMemoryPriorScore, ...] = field(default_factory=tuple)
    appendix_tags: frozenset[str] = field(default_factory=frozenset)
    notes: tuple[str, ...] = field(default_factory=tuple)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)
    host_reliability_prior: HostReliabilityPrior | None = None

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
        if self.host_reliability_prior is not None and not isinstance(
            self.host_reliability_prior,
            HostReliabilityPrior,
        ):
            actual_type = type(self.host_reliability_prior).__name__
            raise TypeError(
                "SupportMemoryPriorAppendix.host_reliability_prior must be "
                f"HostReliabilityPrior | None, got {actual_type}."
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
    "HostReliabilityPrior",
    "SupportMemoryPriorAppendix",
    "SupportMemoryPriorScore",
]
