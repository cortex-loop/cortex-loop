"""Store-backed offline publication distillation for bounded AUX support memory."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from cortex.core.envelopes import MetadataField
from cortex.core.support import SupportReference, SupportSnapshot

from ._support_match import _match_score, _reference_tokens
from .persistence import (
    SqliteSupportMemoryStore,
    SupportMemoryEpisode,
    episode_from_support_snapshot,
)
from .publication import OfflineSupportPublication

_GENERIC_CLUSTER_TOKENS = frozenset(
    {"artifact", "memory", "memo", "result", "summary", "checklist", "prior"}
)


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


def _normalized_candidate(reference: SupportReference) -> SupportReference:
    normalized_kind = {
        "retrieval-prior": "memory",
        "memory-summary": "memory",
        "branch-prior": "branch",
        "contradiction-summary": "contradiction",
        "uncertainty-calibration": "uncertainty",
    }.get(reference.reference_kind, reference.reference_kind)
    if normalized_kind == reference.reference_kind:
        return reference
    return SupportReference(
        normalized_kind,
        reference.reference_id,
        tags=reference.tags,
        metadata=reference.metadata,
    )


def _reason_tokens(episode: SupportMemoryEpisode) -> set[str]:
    values = (
        episode.degradation_reason_codes
        + episode.contradiction_source_tags
        + episode.contradiction_evidence_tags
        + tuple(reference.reference_id for reference in episode.published_memory_refs)
        + tuple(reference.reference_id for reference in episode.artifact_refs)
        + tuple(tag for reference in episode.published_memory_refs for tag in reference.tags)
        + tuple(tag for reference in episode.artifact_refs for tag in reference.tags)
    )
    tokens: set[str] = set()
    for value in values:
        normalized = value.replace("-", "_")
        tokens.update(part for part in normalized.split("_") if part)
    return tokens


def _contradiction_heavy(episodes: tuple[SupportMemoryEpisode, ...]) -> bool:
    if not episodes:
        return False
    heavy_count = sum(
        1
        for episode in episodes
        if (
            episode.degradation_reason_codes
            or episode.contradiction_source_tags
            or episode.contradiction_evidence_tags
        )
    )
    return heavy_count * 2 >= len(episodes)


def _burden_heavy(episodes: tuple[SupportMemoryEpisode, ...]) -> bool:
    if not episodes:
        return False
    burden_tokens = {"burden", "drift", "heavy", "latched", "overhead"}
    heavy_count = sum(
        1
        for episode in episodes
        if _reason_tokens(episode) & burden_tokens
    )
    return heavy_count * 2 >= len(episodes)


def _ref_from_projection(reference) -> SupportReference:
    return reference.as_support_reference()


@dataclass(frozen=True, slots=True)
class _EpisodeReference:
    episode_fingerprint: str
    reference: SupportReference


def _semantic_match(source_ref: SupportReference, candidate_ref: SupportReference) -> bool:
    normalized_source = _normalized_candidate(source_ref)
    normalized_candidate = _normalized_candidate(candidate_ref)
    overlap = _reference_tokens(normalized_source) & _reference_tokens(normalized_candidate)
    overlap -= {
        normalized_source.reference_kind,
        normalized_candidate.reference_kind,
        *_GENERIC_CLUSTER_TOKENS,
    }
    if not overlap:
        return False
    return _match_score(normalized_source, normalized_candidate, base_score=0.0) >= 0.35


def _cluster_supported_refs(
    episode_refs: tuple[_EpisodeReference, ...],
) -> tuple[SupportReference, ...]:
    supported: list[SupportReference] = []
    for item in episode_refs:
        supporting_episodes = {
            other.episode_fingerprint
            for other in episode_refs
            if _semantic_match(item.reference, other.reference)
        }
        if len(supporting_episodes) < 2:
            continue
        supported.append(item.reference)
    return _dedupe_refs(tuple(supported))


def _exact_repeat_refs(
    episodes: tuple[SupportMemoryEpisode, ...],
    *,
    values_for_episode,
    make_reference,
) -> tuple[SupportReference, ...]:
    supporting_episodes: dict[str, set[str]] = {}
    ordered_values: list[str] = []
    for episode in episodes:
        for value in values_for_episode(episode):
            if value not in supporting_episodes:
                supporting_episodes[value] = set()
                ordered_values.append(value)
            supporting_episodes[value].add(episode.episode_fingerprint)
    return tuple(
        make_reference(value)
        for value in ordered_values
        if len(supporting_episodes[value]) >= 2
    )


def _distilled_retrieval_refs(episodes: tuple[SupportMemoryEpisode, ...]) -> tuple[SupportReference, ...]:
    return _cluster_supported_refs(
        tuple(
            _EpisodeReference(
                episode.episode_fingerprint,
                _ref_from_projection(reference),
            )
            for episode in episodes
            for reference in episode.published_memory_refs + episode.artifact_refs
        )
    )


def _distilled_branch_refs(episodes: tuple[SupportMemoryEpisode, ...]) -> tuple[SupportReference, ...]:
    return _exact_repeat_refs(
        episodes,
        values_for_episode=lambda episode: tuple(
            branch_ref
            for branch_ref in episode.branch_registry
            if branch_ref != "main"
        ),
        make_reference=lambda value: SupportReference(
            "branch",
            value,
            tags=frozenset({"branch-prior"}),
        ),
    )


def _distilled_contradiction_refs(
    episodes: tuple[SupportMemoryEpisode, ...],
) -> tuple[SupportReference, ...]:
    refs: list[SupportReference] = []
    for episode in episodes:
        contradiction_tags = frozenset(
            set(episode.contradiction_source_tags)
            | set(episode.contradiction_evidence_tags)
        )
        for reason_code in episode.degradation_reason_codes:
            refs.append(
                SupportReference(
                    "contradiction",
                    reason_code,
                    tags=frozenset(set(contradiction_tags) | {reason_code}),
                )
            )
    return _dedupe_refs(tuple(refs))


def _distilled_uncertainty_refs(
    episodes: tuple[SupportMemoryEpisode, ...],
) -> tuple[SupportReference, ...]:
    uncertainty_refs = _exact_repeat_refs(
        episodes,
        values_for_episode=lambda episode: episode.brake_history,
        make_reference=lambda value: SupportReference(
            "uncertainty",
            value,
            tags=frozenset({"brake-history"}),
        ),
    )
    wake_refs = _exact_repeat_refs(
        episodes,
        values_for_episode=lambda episode: episode.wake_reason_tags,
        make_reference=lambda value: SupportReference(
            "wake",
            value,
            tags=frozenset({"wake-receipt"}),
        ),
    )
    return _dedupe_refs(uncertainty_refs + wake_refs)


def _distilled_memory_summary_refs(
    episodes: tuple[SupportMemoryEpisode, ...],
) -> tuple[SupportReference, ...]:
    return _cluster_supported_refs(
        tuple(
            _EpisodeReference(
                episode.episode_fingerprint,
                _ref_from_projection(reference),
            )
            for episode in episodes
            for reference in episode.published_memory_refs
        )
    )


@dataclass(frozen=True, slots=True)
class _DistillationWindow:
    episodes: tuple[SupportMemoryEpisode, ...]
    positive_priors_suppressed: bool
    suppression_reason: str | None = None


def _distillation_window(
    store: SqliteSupportMemoryStore,
    *,
    host_name: str,
    source_label: str | None,
    horizon_hours: int,
    limit: int,
    now: datetime | None,
) -> _DistillationWindow:
    episodes = store.load_episodes(
        host_name=host_name,
        source_label=source_label,
        horizon_hours=horizon_hours,
        limit=limit,
        now=now,
    )
    contradiction_heavy = _contradiction_heavy(episodes)
    burden_heavy = _burden_heavy(episodes)
    suppression_reason = None
    if burden_heavy:
        suppression_reason = "suppressed:burden-heavy"
    elif contradiction_heavy:
        suppression_reason = "suppressed:contradiction-heavy"
    return _DistillationWindow(
        episodes=episodes,
        positive_priors_suppressed=contradiction_heavy or burden_heavy,
        suppression_reason=suppression_reason,
    )


def distill_offline_support_publication(
    *,
    store: SqliteSupportMemoryStore,
    host_name: str,
    source_label: str | None = None,
    horizon_hours: int = 72,
    limit: int = 32,
    publication_tags: frozenset[str] = frozenset(),
    notes: tuple[str, ...] = (),
    now: datetime | None = None,
) -> OfflineSupportPublication:
    if not isinstance(store, SqliteSupportMemoryStore):
        actual_type = type(store).__name__
        raise TypeError(
            "distill_offline_support_publication() requires SqliteSupportMemoryStore, "
            f"got {actual_type}.",
        )
    window = _distillation_window(
        store,
        host_name=host_name,
        source_label=source_label,
        horizon_hours=horizon_hours,
        limit=limit,
        now=now,
    )
    episodes = window.episodes
    contradiction_summary_refs = _distilled_contradiction_refs(episodes)
    retrieval_prior_refs = ()
    branch_prior_refs = ()
    uncertainty_calibration_refs = ()
    published_memory_summary_refs = ()
    if not window.positive_priors_suppressed:
        retrieval_prior_refs = _distilled_retrieval_refs(episodes)
        branch_prior_refs = _distilled_branch_refs(episodes)
        uncertainty_calibration_refs = _distilled_uncertainty_refs(episodes)
        published_memory_summary_refs = _distilled_memory_summary_refs(episodes)
    merged_tags = frozenset(
        {"aux/offline-publication", "aux/distillation"}
    ) | publication_tags
    merged_notes = _merge_notes(
        ("support-only publication distilled from bounded AUX episode store",),
        notes,
    )
    metadata = (
        MetadataField("source", "aux/distillation"),
        MetadataField("host_name", host_name),
        MetadataField("episode_count", len(episodes)),
        MetadataField("horizon_hours", horizon_hours),
        MetadataField("source_snapshot_count", len(episodes)),
    )
    if source_label is not None:
        metadata = metadata + (MetadataField("source_label", source_label),)
    if window.suppression_reason is not None:
        metadata = metadata + (
            MetadataField("positive_prior_state", window.suppression_reason),
        )
    if window.positive_priors_suppressed:
        merged_notes = merged_notes + (
            "positive priors suppressed by contradiction-heavy or burden-heavy window",
        )
    return OfflineSupportPublication(
        retrieval_prior_refs=retrieval_prior_refs,
        branch_prior_refs=branch_prior_refs,
        contradiction_summary_refs=contradiction_summary_refs,
        uncertainty_calibration_refs=uncertainty_calibration_refs,
        published_memory_summary_refs=published_memory_summary_refs,
        publication_tags=merged_tags,
        notes=merged_notes,
        metadata=metadata,
    )


def _distill_offline_support_publication_from_snapshots(
    source_snapshots: tuple[SupportSnapshot, ...],
    *,
    host_name: str,
    source_label: str,
    horizon_hours: int = 72,
    limit: int = 32,
    publication_tags: frozenset[str] = frozenset(),
    notes: tuple[str, ...] = (),
) -> OfflineSupportPublication:
    if not isinstance(source_snapshots, tuple):
        actual_type = type(source_snapshots).__name__
        raise TypeError(
            "distill_offline_support_publication_from_snapshots() requires tuple[SupportSnapshot, ...], "
            f"got {actual_type}.",
        )
    if any(not isinstance(snapshot, SupportSnapshot) for snapshot in source_snapshots):
        raise TypeError(
            "distill_offline_support_publication_from_snapshots() requires only SupportSnapshot instances."
        )
    store = SqliteSupportMemoryStore(":memory:")
    for snapshot in source_snapshots:
        store.insert_episode(
            episode_from_support_snapshot(
                snapshot,
                host_name=host_name,
                source_label=source_label,
            )
        )
    return distill_offline_support_publication(
        store=store,
        host_name=host_name,
        source_label=source_label,
        horizon_hours=horizon_hours,
        limit=limit,
        publication_tags=publication_tags,
        notes=notes,
    )


__all__ = [
    "distill_offline_support_publication",
]
