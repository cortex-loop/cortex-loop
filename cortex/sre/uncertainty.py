"""Bounded classwise uncertainty carriers for SRE."""

from __future__ import annotations

from dataclasses import dataclass, field

REFERENCE_UNCERTAINTY_CLASSES = frozenset(
    {
        "evidence",
        "environment",
        "host-capability",
        "goal-progress",
    }
)


@dataclass(frozen=True, slots=True)
class UncertaintyEstimate:
    class_tag: str
    level: float
    source_tags: frozenset[str] = field(default_factory=frozenset)
    spike_tags: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if self.class_tag not in REFERENCE_UNCERTAINTY_CLASSES:
            raise ValueError(
                f"Unknown uncertainty class {self.class_tag!r}; "
                f"expected one of {sorted(REFERENCE_UNCERTAINTY_CLASSES)!r}."
            )
        if any(not source_tag.strip() for source_tag in self.source_tags):
            raise ValueError(
                "UncertaintyEstimate.source_tags must contain only non-empty values after trimming."
            )
        if any(not spike_tag.strip() for spike_tag in self.spike_tags):
            raise ValueError(
                "UncertaintyEstimate.spike_tags must contain only non-empty values after trimming."
            )
        if not 0.0 <= self.level <= 1.0:
            raise ValueError("UncertaintyEstimate.level must be between 0.0 and 1.0.")


__all__ = ["REFERENCE_UNCERTAINTY_CLASSES", "UncertaintyEstimate"]
