"""Evaluation-first AUX geometry reports derived from lawful public support state."""

from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite
from numbers import Real

from cortex.core.envelopes import MetadataField
from cortex.core.support import SupportReference, SupportSnapshot

from ._support_match import (
    _dedupe_support_refs,
    _match_score,
    _reference_tokens,
    _retrieval_candidate_pool,
    _source_refs_for_retrieval,
)
from .cost import AuxBurdenReport


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


def _validate_tags_or_notes(
    values: frozenset[str] | tuple[str, ...],
    *,
    field_name: str,
) -> None:
    if any(not (isinstance(value, str) and value.strip()) for value in values):
        raise ValueError(f"{field_name} must contain only non-empty values after trimming.")


def _validate_unit_score(value: float, *, field_name: str) -> None:
    if isinstance(value, bool):
        raise TypeError(f"{field_name} must be numeric, got bool.")
    if not isinstance(value, Real):
        actual_type = type(value).__name__
        raise TypeError(f"{field_name} must be numeric, got {actual_type}.")
    if not isfinite(value):
        raise ValueError(f"{field_name} must be finite.")
    if not 0.0 <= float(value) <= 1.0:
        raise ValueError(f"{field_name} must be between 0.0 and 1.0.")


def _derive_retrieval_shadow_candidates(snapshot: SupportSnapshot) -> tuple[AuxMatchScore, ...]:
    sources = _source_refs_for_retrieval(snapshot)
    candidate_pool = _retrieval_candidate_pool(snapshot)
    matches: list[AuxMatchScore] = []
    for source_ref in sources:
        for candidate_ref in candidate_pool:
            score = _match_score(source_ref, candidate_ref, base_score=0.25)
            if score < 0.25:
                continue
            tags = {"retrieval-shadow"}
            if source_ref.reference_kind == "goal":
                tags.add("goal-conditioned")
            if source_ref.reference_kind == "reminder":
                tags.add("continuity-conditioned")
            matches.append(
                AuxMatchScore(
                    source_ref=source_ref,
                    candidate_ref=candidate_ref,
                    score=score,
                    tags=frozenset(tags),
                )
            )
    matches.sort(key=lambda match: (-match.score, match.source_ref.reference_id, match.candidate_ref.reference_id))
    return tuple(matches[:6])


def _derive_branch_resume_matches(snapshot: SupportSnapshot) -> tuple[AuxMatchScore, ...]:
    branches = tuple(
        SupportReference("branch", branch_ref, tags=frozenset({"resume-track"}))
        for branch_ref in snapshot.session.branch_registry
        if branch_ref != "main"
    )
    if not branches:
        return ()
    goals = tuple(
        SupportReference("goal", goal_ref, tags=frozenset({"pending-goal"}))
        for goal_ref in snapshot.session.pending_goal_refs
    )
    candidate_pool = goals + _retrieval_candidate_pool(snapshot)
    matches: list[AuxMatchScore] = []
    for branch_ref in branches:
        for candidate_ref in candidate_pool:
            score = _match_score(branch_ref, candidate_ref, base_score=0.20)
            if snapshot.session.reminders:
                score = min(1.0, score + 0.10)
            if candidate_ref.reference_kind == "goal":
                score = min(1.0, score + 0.15)
            if score < 0.25:
                continue
            matches.append(
                AuxMatchScore(
                    source_ref=branch_ref,
                    candidate_ref=candidate_ref,
                    score=score,
                    tags=frozenset({"resume-match"}),
                )
            )
    matches.sort(key=lambda match: (-match.score, match.source_ref.reference_id, match.candidate_ref.reference_id))
    return tuple(matches[:6])


def _derive_contradiction_clusters(snapshot: SupportSnapshot) -> tuple[AuxContradictionCluster, ...]:
    clusters: list[AuxContradictionCluster] = []
    support_refs = _retrieval_candidate_pool(snapshot)
    for record in snapshot.trace.degradation_records:
        member_refs = support_refs or (
            SupportReference("degradation", record.reason_code, tags=frozenset(record.capability_tags)),
        )
        contradiction_tags = {record.reason_code}
        notes = ["preserve contradiction instead of smoothing"]
        for contradiction in record.contradiction_records:
            contradiction_tags.add(contradiction.source_tag)
            contradiction_tags.update(contradiction.evidence_tags)
            notes.append(contradiction.summary)
        clusters.append(
            AuxContradictionCluster(
                cluster_tag=record.reason_code,
                member_refs=member_refs,
                contradiction_tags=frozenset(sorted(contradiction_tags)),
                notes=tuple(notes),
            )
        )
    return tuple(clusters)


def _derive_default_burden(
    snapshot: SupportSnapshot,
    *,
    retrieval_shadow_candidates: tuple["AuxMatchScore", ...],
    branch_resume_matches: tuple["AuxMatchScore", ...],
    contradiction_clusters: tuple["AuxContradictionCluster", ...],
) -> AuxBurdenReport:
    return AuxBurdenReport(
        compute_overhead=min(1.0, 0.03 * len(snapshot.trace.recent_events)),
        memory_overhead=min(1.0, 0.05 * len(snapshot.exec_memory_pub.published_memory_refs)),
        latency_overhead=min(1.0, 0.02 * len(snapshot.trace.wake_receipts)),
        environment_query_cost=min(1.0, 0.03 * len(snapshot.trace.degradation_records)),
        retrieval_cost=min(1.0, 0.08 * len(retrieval_shadow_candidates)),
        intervention_burden=min(
            1.0,
            (0.05 * len(branch_resume_matches)) + (0.04 * len(contradiction_clusters)),
        ),
    )


@dataclass(frozen=True, slots=True)
class AuxMatchScore:
    source_ref: SupportReference
    candidate_ref: SupportReference
    score: float
    tags: frozenset[str] = field(default_factory=frozenset)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not isinstance(self.source_ref, SupportReference):
            actual_type = type(self.source_ref).__name__
            raise TypeError(
                "AuxMatchScore.source_ref must be SupportReference, "
                f"got {actual_type}.",
            )
        if not isinstance(self.candidate_ref, SupportReference):
            actual_type = type(self.candidate_ref).__name__
            raise TypeError(
                "AuxMatchScore.candidate_ref must be SupportReference, "
                f"got {actual_type}.",
            )
        _validate_unit_score(self.score, field_name="AuxMatchScore.score")
        _validate_tags_or_notes(self.tags, field_name="AuxMatchScore.tags")
        _validate_metadata(self.metadata, field_name="AuxMatchScore.metadata")


@dataclass(frozen=True, slots=True)
class AuxContradictionCluster:
    cluster_tag: str
    member_refs: tuple[SupportReference, ...]
    contradiction_tags: frozenset[str] = field(default_factory=frozenset)
    notes: tuple[str, ...] = field(default_factory=tuple)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not (isinstance(self.cluster_tag, str) and self.cluster_tag.strip()):
            raise ValueError(
                "AuxContradictionCluster.cluster_tag must be non-empty after trimming.",
            )
        if any(not isinstance(reference, SupportReference) for reference in self.member_refs):
            raise TypeError(
                "AuxContradictionCluster.member_refs must contain only SupportReference instances.",
            )
        _validate_tags_or_notes(
            self.contradiction_tags,
            field_name="AuxContradictionCluster.contradiction_tags",
        )
        _validate_tags_or_notes(
            self.notes,
            field_name="AuxContradictionCluster.notes",
        )
        _validate_metadata(
            self.metadata,
            field_name="AuxContradictionCluster.metadata",
        )


@dataclass(frozen=True, slots=True)
class AuxGeometryReport:
    source_snapshot: SupportSnapshot
    retrieval_shadow_candidates: tuple[AuxMatchScore, ...] = field(default_factory=tuple)
    branch_resume_matches: tuple[AuxMatchScore, ...] = field(default_factory=tuple)
    uncertainty_brake_hints: tuple[str, ...] = field(default_factory=tuple)
    contradiction_clusters: tuple[AuxContradictionCluster, ...] = field(default_factory=tuple)
    burden: AuxBurdenReport = field(default_factory=AuxBurdenReport)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not isinstance(self.source_snapshot, SupportSnapshot):
            actual_type = type(self.source_snapshot).__name__
            raise TypeError(
                "AuxGeometryReport.source_snapshot must be SupportSnapshot, "
                f"got {actual_type}.",
            )
        if any(
            not isinstance(candidate, AuxMatchScore)
            for candidate in self.retrieval_shadow_candidates
        ):
            raise TypeError(
                "AuxGeometryReport.retrieval_shadow_candidates must contain only AuxMatchScore instances.",
            )
        if any(
            not isinstance(match, AuxMatchScore)
            for match in self.branch_resume_matches
        ):
            raise TypeError(
                "AuxGeometryReport.branch_resume_matches must contain only AuxMatchScore instances.",
            )
        _validate_tags_or_notes(
            self.uncertainty_brake_hints,
            field_name="AuxGeometryReport.uncertainty_brake_hints",
        )
        if any(
            not isinstance(cluster, AuxContradictionCluster)
            for cluster in self.contradiction_clusters
        ):
            raise TypeError(
                "AuxGeometryReport.contradiction_clusters must contain only AuxContradictionCluster instances.",
            )
        if not isinstance(self.burden, AuxBurdenReport):
            actual_type = type(self.burden).__name__
            raise TypeError(
                "AuxGeometryReport.burden must be AuxBurdenReport, "
                f"got {actual_type}.",
            )
        _validate_metadata(self.metadata, field_name="AuxGeometryReport.metadata")


def _derive_default_hints(snapshot: SupportSnapshot) -> tuple[str, ...]:
    hints: list[str] = []
    if snapshot.exec_memory_pub.published_memory_refs or snapshot.exec_memory_pub.artifact_refs:
        hints.append("support-evidence-present")
    if snapshot.session.pending_goal_refs or snapshot.session.branch_registry:
        hints.append("branch-resume-pressure")
    if snapshot.trace.degradation_records or snapshot.session.brake_history:
        hints.append("uncertainty-brake-pressure")
    if snapshot.session.reminders or snapshot.trace.wake_receipts:
        hints.append("continuity-reminder-present")
    return tuple(hints)


def _merge_unique_strings(*groups: tuple[str, ...]) -> tuple[str, ...]:
    ordered: list[str] = []
    seen: set[str] = set()
    for group in groups:
        for value in group:
            if value not in seen:
                seen.add(value)
                ordered.append(value)
    return tuple(ordered)


def _merge_unique_matches(
    *groups: tuple[AuxMatchScore, ...],
) -> tuple[AuxMatchScore, ...]:
    ordered: list[AuxMatchScore] = []
    seen: set[tuple[str, str, str, str]] = set()
    for group in groups:
        for match in group:
            key = (
                match.source_ref.reference_kind,
                match.source_ref.reference_id,
                match.candidate_ref.reference_kind,
                match.candidate_ref.reference_id,
            )
            if key in seen:
                continue
            seen.add(key)
            ordered.append(match)
    return tuple(ordered)


def _merge_unique_clusters(
    *groups: tuple[AuxContradictionCluster, ...],
) -> tuple[AuxContradictionCluster, ...]:
    ordered: list[AuxContradictionCluster] = []
    seen: set[str] = set()
    for group in groups:
        for cluster in group:
            if cluster.cluster_tag in seen:
                continue
            seen.add(cluster.cluster_tag)
            ordered.append(cluster)
    return tuple(ordered)


def build_aux_geometry_report(
    snapshot: SupportSnapshot,
    *,
    retrieval_shadow_candidates: tuple[AuxMatchScore, ...] = (),
    branch_resume_matches: tuple[AuxMatchScore, ...] = (),
    uncertainty_brake_hints: tuple[str, ...] = (),
    contradiction_clusters: tuple[AuxContradictionCluster, ...] = (),
    burden: AuxBurdenReport | None = None,
    metadata: tuple[MetadataField, ...] = (),
) -> AuxGeometryReport:
    if not isinstance(snapshot, SupportSnapshot):
        actual_type = type(snapshot).__name__
        raise TypeError(
            "build_aux_geometry_report() requires SupportSnapshot, "
            f"got {actual_type}.",
        )

    derived_retrieval_candidates = _derive_retrieval_shadow_candidates(snapshot)
    derived_branch_matches = _derive_branch_resume_matches(snapshot)
    derived_contradiction_clusters = _derive_contradiction_clusters(snapshot)
    merged_retrieval_candidates = _merge_unique_matches(
        retrieval_shadow_candidates,
        derived_retrieval_candidates,
    )
    merged_branch_matches = _merge_unique_matches(
        branch_resume_matches,
        derived_branch_matches,
    )
    merged_contradiction_clusters = _merge_unique_clusters(
        contradiction_clusters,
        derived_contradiction_clusters,
    )
    resolved_burden = (
        _derive_default_burden(
            snapshot,
            retrieval_shadow_candidates=merged_retrieval_candidates,
            branch_resume_matches=merged_branch_matches,
            contradiction_clusters=merged_contradiction_clusters,
        )
        if burden is None
        else burden
    )
    return AuxGeometryReport(
        source_snapshot=snapshot,
        retrieval_shadow_candidates=merged_retrieval_candidates,
        branch_resume_matches=merged_branch_matches,
        uncertainty_brake_hints=_merge_unique_strings(
            _derive_default_hints(snapshot),
            uncertainty_brake_hints,
        ),
        contradiction_clusters=merged_contradiction_clusters,
        burden=resolved_burden,
        metadata=metadata,
    )


__all__ = [
    "AuxContradictionCluster",
    "AuxGeometryReport",
    "AuxMatchScore",
    "build_aux_geometry_report",
]
