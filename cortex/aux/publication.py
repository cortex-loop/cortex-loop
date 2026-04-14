"""Support-only offline publication contracts and augmentation-only re-entry."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

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


def _metadata_field_as_payload(field: MetadataField) -> dict[str, Any]:
    if not isinstance(field, MetadataField):
        actual_type = type(field).__name__
        raise TypeError(
            "offline_support_publication_as_payload() metadata must contain only MetadataField instances, "
            f"got {actual_type}."
        )
    return {
        "key": field.key,
        "value": field.value,
    }


def _parse_metadata_field_payload(
    payload: Mapping[str, Any],
    *,
    label: str,
) -> MetadataField:
    if not isinstance(payload, Mapping):
        actual_type = type(payload).__name__
        raise TypeError(f"{label} must be an object, got {actual_type}.")
    if tuple(payload) != ("key", "value"):
        raise ValueError(f"{label} must preserve the locked key order ('key', 'value').")
    return MetadataField(
        _required_payload_string(payload.get("key"), label=f"{label}.key"),
        payload.get("value"),
    )


def _support_reference_as_payload(reference: SupportReference) -> dict[str, Any]:
    if not isinstance(reference, SupportReference):
        actual_type = type(reference).__name__
        raise TypeError(
            "offline_support_publication_as_payload() support refs must contain only SupportReference instances, "
            f"got {actual_type}."
        )
    return {
        "reference_kind": reference.reference_kind,
        "reference_id": reference.reference_id,
        "tags": sorted(reference.tags),
        "metadata": [_metadata_field_as_payload(field) for field in reference.metadata],
    }


def _parse_support_reference_payload(
    payload: Mapping[str, Any],
    *,
    label: str,
) -> SupportReference:
    if not isinstance(payload, Mapping):
        actual_type = type(payload).__name__
        raise TypeError(f"{label} must be an object, got {actual_type}.")
    if tuple(payload) != ("reference_kind", "reference_id", "tags", "metadata"):
        raise ValueError(
            f"{label} must preserve the locked key order "
            "('reference_kind', 'reference_id', 'tags', 'metadata')."
        )
    tags = payload.get("tags")
    if not isinstance(tags, list):
        actual_type = type(tags).__name__
        raise TypeError(f"{label}.tags must be a list[str], got {actual_type}.")
    metadata = payload.get("metadata")
    if not isinstance(metadata, list):
        actual_type = type(metadata).__name__
        raise TypeError(f"{label}.metadata must be a list[dict[str, Any]], got {actual_type}.")
    return SupportReference(
        _required_payload_string(payload.get("reference_kind"), label=f"{label}.reference_kind"),
        _required_payload_string(payload.get("reference_id"), label=f"{label}.reference_id"),
        tags=frozenset(
            _required_payload_string(tag, label=f"{label}.tags[{index}]")
            for index, tag in enumerate(tags)
        ),
        metadata=tuple(
            _parse_metadata_field_payload(item, label=f"{label}.metadata[{index}]")
            for index, item in enumerate(metadata)
        ),
    )


def _required_payload_string(value: Any, *, label: str) -> str:
    if not isinstance(value, str):
        actual_type = type(value).__name__
        raise TypeError(f"{label} must be a string, got {actual_type}.")
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"{label} must be non-empty after trimming.")
    return stripped


def _string_list_payload(
    values: frozenset[str] | tuple[str, ...],
    *,
    field_name: str,
) -> list[str]:
    _validate_text_values(values, field_name=field_name)
    return sorted(values) if isinstance(values, frozenset) else list(values)


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


def offline_support_publication_as_payload(
    publication: OfflineSupportPublication,
) -> dict[str, Any]:
    if not isinstance(publication, OfflineSupportPublication):
        actual_type = type(publication).__name__
        raise TypeError(
            "offline_support_publication_as_payload() requires OfflineSupportPublication, "
            f"got {actual_type}."
        )
    return {
        "retrieval_prior_refs": [
            _support_reference_as_payload(reference)
            for reference in publication.retrieval_prior_refs
        ],
        "branch_prior_refs": [
            _support_reference_as_payload(reference)
            for reference in publication.branch_prior_refs
        ],
        "contradiction_summary_refs": [
            _support_reference_as_payload(reference)
            for reference in publication.contradiction_summary_refs
        ],
        "uncertainty_calibration_refs": [
            _support_reference_as_payload(reference)
            for reference in publication.uncertainty_calibration_refs
        ],
        "published_memory_summary_refs": [
            _support_reference_as_payload(reference)
            for reference in publication.published_memory_summary_refs
        ],
        "publication_tags": _string_list_payload(
            publication.publication_tags,
            field_name="OfflineSupportPublication.publication_tags",
        ),
        "notes": _string_list_payload(
            publication.notes,
            field_name="OfflineSupportPublication.notes",
        ),
        "metadata": [
            _metadata_field_as_payload(field)
            for field in publication.metadata
        ],
    }


def parse_offline_support_publication_payload(
    payload: Mapping[str, Any],
) -> OfflineSupportPublication:
    if not isinstance(payload, Mapping):
        actual_type = type(payload).__name__
        raise TypeError(
            "parse_offline_support_publication_payload() requires a mapping, "
            f"got {actual_type}."
        )
    required_keys = (
        "retrieval_prior_refs",
        "branch_prior_refs",
        "contradiction_summary_refs",
        "uncertainty_calibration_refs",
        "published_memory_summary_refs",
        "publication_tags",
        "notes",
        "metadata",
    )
    if tuple(payload) != required_keys:
        raise ValueError(
            "parse_offline_support_publication_payload() requires the locked key order "
            f"{required_keys!r}."
        )

    def _ref_list(key: str) -> tuple[SupportReference, ...]:
        value = payload.get(key)
        if not isinstance(value, list):
            actual_type = type(value).__name__
            raise TypeError(
                f"parse_offline_support_publication_payload().{key} must be a list[dict[str, Any]], "
                f"got {actual_type}."
            )
        return tuple(
            _parse_support_reference_payload(item, label=f"offline_publication.{key}[{index}]")
            for index, item in enumerate(value)
        )

    def _string_tuple(key: str) -> tuple[str, ...]:
        value = payload.get(key)
        if not isinstance(value, list):
            actual_type = type(value).__name__
            raise TypeError(
                f"parse_offline_support_publication_payload().{key} must be a list[str], "
                f"got {actual_type}."
            )
        return tuple(
            _required_payload_string(item, label=f"offline_publication.{key}[{index}]")
            for index, item in enumerate(value)
        )

    metadata = payload.get("metadata")
    if not isinstance(metadata, list):
        actual_type = type(metadata).__name__
        raise TypeError(
            "parse_offline_support_publication_payload().metadata must be a list[dict[str, Any]], "
            f"got {actual_type}."
        )

    return OfflineSupportPublication(
        retrieval_prior_refs=_ref_list("retrieval_prior_refs"),
        branch_prior_refs=_ref_list("branch_prior_refs"),
        contradiction_summary_refs=_ref_list("contradiction_summary_refs"),
        uncertainty_calibration_refs=_ref_list("uncertainty_calibration_refs"),
        published_memory_summary_refs=_ref_list("published_memory_summary_refs"),
        publication_tags=frozenset(_string_tuple("publication_tags")),
        notes=_string_tuple("notes"),
        metadata=tuple(
            _parse_metadata_field_payload(item, label=f"offline_publication.metadata[{index}]")
            for index, item in enumerate(metadata)
        ),
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
    "offline_support_publication_as_payload",
    "parse_offline_support_publication_payload",
    "augment_snapshot_with_offline_publication",
]
