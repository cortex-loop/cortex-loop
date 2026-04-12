"""Evaluation-first AUX geometry reports derived from lawful public support state."""

from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite
from numbers import Real

from cortex.core.envelopes import MetadataField
from cortex.core.support import SupportReference, SupportSnapshot

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

    return AuxGeometryReport(
        source_snapshot=snapshot,
        retrieval_shadow_candidates=retrieval_shadow_candidates,
        branch_resume_matches=branch_resume_matches,
        uncertainty_brake_hints=_merge_unique_strings(
            _derive_default_hints(snapshot),
            uncertainty_brake_hints,
        ),
        contradiction_clusters=contradiction_clusters,
        burden=AuxBurdenReport() if burden is None else burden,
        metadata=metadata,
    )


__all__ = [
    "AuxContradictionCluster",
    "AuxGeometryReport",
    "AuxMatchScore",
    "build_aux_geometry_report",
]
