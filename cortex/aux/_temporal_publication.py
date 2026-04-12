"""Private helpers for time-separated offline-publication merging."""

from __future__ import annotations

from cortex.core.envelopes import MetadataField
from cortex.core.support import SupportReference, SupportSnapshot

from .publication import OfflineSupportPublication, build_offline_support_publication


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


def _merge_notes(*groups: tuple[str, ...]) -> tuple[str, ...]:
    ordered: list[str] = []
    seen: set[str] = set()
    for group in groups:
        for value in group:
            if value in seen:
                continue
            seen.add(value)
            ordered.append(value)
    return tuple(ordered)


def _merge_temporal_publication(
    source_snapshots: tuple[SupportSnapshot, ...],
    *,
    source_label: str,
    extra_tags: frozenset[str] = frozenset(),
    extra_notes: tuple[str, ...] = (),
) -> OfflineSupportPublication:
    publications = tuple(build_offline_support_publication(snapshot) for snapshot in source_snapshots)
    return OfflineSupportPublication(
        retrieval_prior_refs=_dedupe_refs(
            tuple(
                reference
                for publication in publications
                for reference in publication.retrieval_prior_refs
            )
        ),
        branch_prior_refs=_dedupe_refs(
            tuple(
                reference
                for publication in publications
                for reference in publication.branch_prior_refs
            )
        ),
        contradiction_summary_refs=_dedupe_refs(
            tuple(
                reference
                for publication in publications
                for reference in publication.contradiction_summary_refs
            )
        ),
        uncertainty_calibration_refs=_dedupe_refs(
            tuple(
                reference
                for publication in publications
                for reference in publication.uncertainty_calibration_refs
            )
        ),
        published_memory_summary_refs=_dedupe_refs(
            tuple(
                reference
                for publication in publications
                for reference in publication.published_memory_summary_refs
            )
        ),
        publication_tags=frozenset(extra_tags | {tag for publication in publications for tag in publication.publication_tags}),
        notes=_merge_notes(
            extra_notes,
            tuple(note for publication in publications for note in publication.notes),
        ),
        metadata=(
            MetadataField("source", source_label),
            MetadataField("source_snapshot_count", len(source_snapshots)),
        ),
    )


__all__ = ["_merge_temporal_publication"]
