"""Support-only offline publication contracts and augmentation-only re-entry."""

from __future__ import annotations

from dataclasses import dataclass, field

from cortex.core.envelopes import MetadataField
from cortex.core.support import SupportReference, SupportSnapshot

from .augmentation import AuxiliarySupportAppendix, AugmentedSupportSnapshot, augment_snapshot


def _validate_refs(
    refs: tuple[SupportReference, ...],
    *,
    field_name: str,
) -> None:
    if any(not isinstance(reference, SupportReference) for reference in refs):
        raise TypeError(f"{field_name} must contain only SupportReference instances.")


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
class OfflineSupportPublication:
    retrieval_prior_refs: tuple[SupportReference, ...] = field(default_factory=tuple)
    branch_prior_refs: tuple[SupportReference, ...] = field(default_factory=tuple)
    contradiction_summary_refs: tuple[SupportReference, ...] = field(default_factory=tuple)
    uncertainty_calibration_refs: tuple[SupportReference, ...] = field(default_factory=tuple)
    published_memory_summary_refs: tuple[SupportReference, ...] = field(default_factory=tuple)
    publication_tags: frozenset[str] = field(default_factory=frozenset)
    notes: tuple[str, ...] = field(default_factory=tuple)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        _validate_refs(
            self.retrieval_prior_refs,
            field_name="OfflineSupportPublication.retrieval_prior_refs",
        )
        _validate_refs(
            self.branch_prior_refs,
            field_name="OfflineSupportPublication.branch_prior_refs",
        )
        _validate_refs(
            self.contradiction_summary_refs,
            field_name="OfflineSupportPublication.contradiction_summary_refs",
        )
        _validate_refs(
            self.uncertainty_calibration_refs,
            field_name="OfflineSupportPublication.uncertainty_calibration_refs",
        )
        _validate_refs(
            self.published_memory_summary_refs,
            field_name="OfflineSupportPublication.published_memory_summary_refs",
        )
        _validate_text_values(
            self.publication_tags,
            field_name="OfflineSupportPublication.publication_tags",
        )
        _validate_text_values(
            self.notes,
            field_name="OfflineSupportPublication.notes",
        )
        _validate_metadata(
            self.metadata,
            field_name="OfflineSupportPublication.metadata",
        )

    def support_refs(self) -> tuple[SupportReference, ...]:
        return (
            self.retrieval_prior_refs
            + self.branch_prior_refs
            + self.contradiction_summary_refs
            + self.uncertainty_calibration_refs
            + self.published_memory_summary_refs
        )


def augment_snapshot_with_offline_publication(
    snapshot: SupportSnapshot,
    publication: OfflineSupportPublication,
) -> AugmentedSupportSnapshot:
    if not isinstance(snapshot, SupportSnapshot):
        actual_type = type(snapshot).__name__
        raise TypeError(
            "augment_snapshot_with_offline_publication() requires SupportSnapshot, "
            f"got {actual_type}.",
        )
    if not isinstance(publication, OfflineSupportPublication):
        actual_type = type(publication).__name__
        raise TypeError(
            "augment_snapshot_with_offline_publication() requires OfflineSupportPublication, "
            f"got {actual_type}.",
        )

    return augment_snapshot(
        snapshot,
        AuxiliarySupportAppendix(
            derived_support_refs=publication.support_refs(),
            derived_tags=frozenset({"aux/offline-publication"}) | publication.publication_tags,
            notes=publication.notes,
            metadata=publication.metadata,
        ),
    )


__all__ = [
    "OfflineSupportPublication",
    "augment_snapshot_with_offline_publication",
]
