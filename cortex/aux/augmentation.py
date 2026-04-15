"""Explicit AUX-side support snapshot augmentation."""

from __future__ import annotations

from dataclasses import dataclass, field

from cortex.core.envelopes import MetadataField
from cortex.core.support import SupportReference, SupportSnapshot
from cortex.sre.memory_priors import HostReliabilityPrior


@dataclass(frozen=True, slots=True)
class AuxiliarySupportAppendix:
    derived_support_refs: tuple[SupportReference, ...] = field(default_factory=tuple)
    derived_tags: frozenset[str] = field(default_factory=frozenset)
    notes: tuple[str, ...] = field(default_factory=tuple)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)
    published_host_reliability_prior: HostReliabilityPrior | None = None

    def __post_init__(self) -> None:
        if any(
            not isinstance(reference, SupportReference)
            for reference in self.derived_support_refs
        ):
            raise TypeError(
                "AuxiliarySupportAppendix.derived_support_refs must contain only SupportReference instances.",
            )
        if any(not (isinstance(tag, str) and tag.strip()) for tag in self.derived_tags):
            raise ValueError(
                "AuxiliarySupportAppendix.derived_tags must contain only non-empty values after trimming.",
            )
        if any(not (isinstance(note, str) and note.strip()) for note in self.notes):
            raise ValueError(
                "AuxiliarySupportAppendix.notes must contain only non-empty values after trimming.",
            )
        if any(not isinstance(field, MetadataField) for field in self.metadata):
            raise TypeError(
                "AuxiliarySupportAppendix.metadata must contain only MetadataField instances.",
            )
        if self.published_host_reliability_prior is not None and not isinstance(
            self.published_host_reliability_prior,
            HostReliabilityPrior,
        ):
            actual_type = type(self.published_host_reliability_prior).__name__
            raise TypeError(
                "AuxiliarySupportAppendix.published_host_reliability_prior must be "
                f"HostReliabilityPrior | None, got {actual_type}.",
            )


@dataclass(frozen=True, slots=True)
class AugmentedSupportSnapshot:
    core_snapshot: SupportSnapshot
    auxiliary_support: AuxiliarySupportAppendix

    def __post_init__(self) -> None:
        if not isinstance(self.core_snapshot, SupportSnapshot):
            actual_type = type(self.core_snapshot).__name__
            raise TypeError(
                "AugmentedSupportSnapshot.core_snapshot must be SupportSnapshot, "
                f"got {actual_type}.",
            )
        if not isinstance(self.auxiliary_support, AuxiliarySupportAppendix):
            actual_type = type(self.auxiliary_support).__name__
            raise TypeError(
                "AugmentedSupportSnapshot.auxiliary_support must be AuxiliarySupportAppendix, "
                f"got {actual_type}.",
            )


def augment_snapshot(
    snapshot: SupportSnapshot,
    auxiliary_support: AuxiliarySupportAppendix,
) -> AugmentedSupportSnapshot:
    if not isinstance(snapshot, SupportSnapshot):
        actual_type = type(snapshot).__name__
        raise TypeError(
            "augment_snapshot() requires SupportSnapshot, "
            f"got {actual_type}.",
        )
    if not isinstance(auxiliary_support, AuxiliarySupportAppendix):
        actual_type = type(auxiliary_support).__name__
        raise TypeError(
            "augment_snapshot() requires AuxiliarySupportAppendix, "
            f"got {actual_type}.",
        )
    return AugmentedSupportSnapshot(
        core_snapshot=snapshot,
        auxiliary_support=auxiliary_support,
    )


__all__ = [
    "AugmentedSupportSnapshot",
    "AuxiliarySupportAppendix",
    "augment_snapshot",
]
