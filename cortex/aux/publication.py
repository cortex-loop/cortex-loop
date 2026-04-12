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


def _dedupe_refs(references: tuple[SupportReference, ...]) -> tuple[SupportReference, ...]:
    ordered: list[SupportReference] = []
    seen: set[tuple[str, str]] = set()
    for reference in references:
        key = (reference.reference_kind, reference.reference_id)
        if key in seen:
            continue
        seen.add(key)
        ordered.append(reference)
    return tuple(ordered)


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
        return _dedupe_refs(
            self.retrieval_prior_refs
            + self.branch_prior_refs
            + self.contradiction_summary_refs
            + self.uncertainty_calibration_refs
            + self.published_memory_summary_refs
        )


def build_offline_support_publication(
    snapshot: SupportSnapshot,
    *,
    publication_tags: frozenset[str] = frozenset(),
    notes: tuple[str, ...] = (),
    metadata: tuple[MetadataField, ...] = (),
) -> OfflineSupportPublication:
    if not isinstance(snapshot, SupportSnapshot):
        actual_type = type(snapshot).__name__
        raise TypeError(
            "build_offline_support_publication() requires SupportSnapshot, "
            f"got {actual_type}.",
        )
    retrieval_prior_refs = _dedupe_refs(
        snapshot.exec_memory_pub.published_memory_refs + snapshot.exec_memory_pub.artifact_refs
    )
    branch_prior_refs = _dedupe_refs(
        tuple(
            SupportReference("branch", branch_ref, tags=frozenset({"branch-prior"}))
            for branch_ref in snapshot.session.branch_registry
            if branch_ref != "main"
        )
    )
    contradiction_summary_refs = _dedupe_refs(
        tuple(
            SupportReference(
                "contradiction",
                record.reason_code,
                tags=frozenset(record.capability_tags | {record.reason_code}),
            )
            for record in snapshot.trace.degradation_records
        )
    )
    uncertainty_calibration_refs = _dedupe_refs(
        tuple(
            SupportReference("uncertainty", brake_entry, tags=frozenset({"brake-history"}))
            for brake_entry in snapshot.session.brake_history
        )
        + tuple(
            SupportReference(
                "wake",
                receipt.reason_tag,
                tags=frozenset({"wake-receipt"}),
            )
            for receipt in snapshot.trace.wake_receipts
        )
    )
    merged_tags = frozenset({"aux/offline-publication", "claim-conservative"}) | publication_tags
    merged_notes = (
        "support-only publication derived from lawful public support snapshot",
    ) + notes
    merged_metadata = (MetadataField("source", "aux/offline-publication"),) + metadata
    return OfflineSupportPublication(
        retrieval_prior_refs=retrieval_prior_refs,
        branch_prior_refs=branch_prior_refs,
        contradiction_summary_refs=contradiction_summary_refs,
        uncertainty_calibration_refs=uncertainty_calibration_refs,
        published_memory_summary_refs=snapshot.exec_memory_pub.published_memory_refs,
        publication_tags=merged_tags,
        notes=merged_notes,
        metadata=merged_metadata,
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
    "build_offline_support_publication",
    "augment_snapshot_with_offline_publication",
]
