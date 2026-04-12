"""Deterministic evaluation-first AUX runners over lawful public support state."""

from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite
from numbers import Real

from cortex.core.envelopes import MetadataField
from cortex.core.support import SupportReference, SupportSnapshot
from cortex.sre.memory_priors import SupportMemoryPriorAppendix

from ._support_match import _match_score, _reference_tokens, _source_refs_for_retrieval
from ._temporal_publication import _merge_temporal_publication
from .augmentation import AugmentedSupportSnapshot
from .cost import AuxBurdenReport
from .geometry import (
    AuxContradictionCluster,
    AuxGeometryReport,
    AuxMatchScore,
    build_aux_geometry_report,
)
from .lift import AUX_LIFT_DIRECTIONS, AuxLiftMetric, AuxLiftReport, build_aux_lift_report, total_aux_burden
from .publication import (
    OfflineSupportPublication,
    augment_snapshot_with_offline_publication,
)
from .support_priors import build_support_memory_prior_appendix


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


def _validate_text_values(
    values: frozenset[str] | tuple[str, ...],
    *,
    field_name: str,
) -> None:
    if any(not (isinstance(value, str) and value.strip()) for value in values):
        raise ValueError(f"{field_name} must contain only non-empty values after trimming.")


def _validate_non_negative_int(value: int, *, field_name: str) -> None:
    if isinstance(value, bool):
        raise TypeError(f"{field_name} must be int, got bool.")
    if not isinstance(value, int):
        actual_type = type(value).__name__
        raise TypeError(f"{field_name} must be int, got {actual_type}.")
    if value < 0:
        raise ValueError(f"{field_name} must be non-negative.")


def _validate_finite_number(value: float, *, field_name: str) -> None:
    if isinstance(value, bool):
        raise TypeError(f"{field_name} must be numeric, got bool.")
    if not isinstance(value, Real):
        actual_type = type(value).__name__
        raise TypeError(f"{field_name} must be numeric, got {actual_type}.")
    if not isfinite(float(value)):
        raise ValueError(f"{field_name} must be finite.")


def _metric_regressed(metric: AuxLiftMetric) -> bool:
    if metric.direction == "higher_is_better":
        return metric.delta_value < 0.0
    return metric.delta_value > 0.0


def _average_match_score(match_scores: tuple[object, ...]) -> float:
    if not match_scores:
        return 0.0
    total = sum(float(getattr(match, "score")) for match in match_scores)
    return total / len(match_scores)


def _best_match_score(match_scores: tuple[AuxMatchScore, ...]) -> float:
    if not match_scores:
        return 0.0
    return max(float(match.score) for match in match_scores)


def _uncertainty_hint_value(report: AuxGeometryReport) -> float:
    return min(1.0, 0.15 * len(report.uncertainty_brake_hints))


def _contradiction_quality(report: AuxGeometryReport) -> float:
    if not report.contradiction_clusters:
        return 0.0
    tag_weight = sum(len(cluster.contradiction_tags) for cluster in report.contradiction_clusters)
    ref_weight = sum(len(cluster.member_refs) for cluster in report.contradiction_clusters)
    return min(1.0, (0.08 * tag_weight) + (0.04 * ref_weight))

def _merge_publications(
    source_snapshots: tuple[SupportSnapshot, ...],
) -> OfflineSupportPublication:
    return _merge_temporal_publication(
        source_snapshots,
        source_label="aux/temporal-corpus",
        extra_tags=frozenset({"aux/offline-publication", "aux/temporal-corpus"}),
        extra_notes=("time-separated offline publication for later target evaluation",),
    )


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


def _build_temporal_retrieval_candidates(
    target_snapshot: SupportSnapshot,
    publication: OfflineSupportPublication,
) -> tuple[AuxMatchScore, ...]:
    sources = _source_refs_for_retrieval(target_snapshot)
    candidate_pool = publication.retrieval_prior_refs + publication.published_memory_summary_refs
    matches: list[AuxMatchScore] = []
    for source_ref in sources:
        for publication_ref in candidate_pool:
            normalized_candidate = _normalized_candidate(publication_ref)
            token_overlap = _reference_tokens(source_ref) & _reference_tokens(normalized_candidate)
            if not token_overlap:
                continue
            score = _match_score(source_ref, normalized_candidate, base_score=0.18)
            if score < 0.30:
                continue
            tags = {"retrieval-shadow", "offline-publication", "time-separated"}
            if source_ref.reference_kind == "goal":
                tags.add("goal-conditioned")
            matches.append(
                AuxMatchScore(
                    source_ref=source_ref,
                    candidate_ref=publication_ref,
                    score=score,
                    tags=frozenset(tags),
                )
            )
    matches.sort(key=lambda match: (-match.score, match.source_ref.reference_id, match.candidate_ref.reference_id))
    return tuple(matches[:6])


def _build_temporal_branch_matches(
    target_snapshot: SupportSnapshot,
    publication: OfflineSupportPublication,
) -> tuple[AuxMatchScore, ...]:
    branch_refs = tuple(
        SupportReference("branch", branch_ref, tags=frozenset({"resume-track"}))
        for branch_ref in target_snapshot.session.branch_registry
        if branch_ref != "main"
    )
    candidate_pool = (
        publication.branch_prior_refs
        + publication.retrieval_prior_refs
        + publication.published_memory_summary_refs
    )
    matches: list[AuxMatchScore] = []
    for branch_ref in branch_refs:
        for publication_ref in candidate_pool:
            normalized_candidate = _normalized_candidate(publication_ref)
            token_overlap = _reference_tokens(branch_ref) & _reference_tokens(normalized_candidate)
            if not token_overlap:
                continue
            score = _match_score(branch_ref, normalized_candidate, base_score=0.16)
            if publication_ref.reference_kind == "branch":
                score = min(1.0, score + 0.20)
            if target_snapshot.session.reminders:
                score = min(1.0, score + 0.05)
            if score < 0.30:
                continue
            matches.append(
                AuxMatchScore(
                    source_ref=branch_ref,
                    candidate_ref=publication_ref,
                    score=score,
                    tags=frozenset({"resume-match", "offline-publication", "time-separated"}),
                )
            )
    matches.sort(key=lambda match: (-match.score, match.source_ref.reference_id, match.candidate_ref.reference_id))
    return tuple(matches[:6])


def _build_temporal_contradiction_clusters(
    target_snapshot: SupportSnapshot,
    publication: OfflineSupportPublication,
) -> tuple[AuxContradictionCluster, ...]:
    clusters: list[AuxContradictionCluster] = []
    for record in target_snapshot.trace.degradation_records:
        target_ref = SupportReference(
            "contradiction",
            record.reason_code,
            tags=frozenset(record.capability_tags | {record.reason_code}),
        )
        publication_refs = tuple(
            reference
            for reference in publication.contradiction_summary_refs
            if _reference_tokens(_normalized_candidate(reference)) & _reference_tokens(target_ref)
        )
        member_refs = (target_ref,) + publication_refs if publication_refs else (target_ref,)
        contradiction_tags = {record.reason_code}
        notes = ["preserve contradiction instead of smoothing"]
        if publication_refs:
            notes.append("offline contradiction summary reused on later target")
        for publication_ref in publication_refs:
            contradiction_tags.add(publication_ref.reference_id)
            contradiction_tags.update(publication_ref.tags)
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


def _build_temporal_uncertainty_hints(
    target_snapshot: SupportSnapshot,
    publication: OfflineSupportPublication,
) -> tuple[str, ...]:
    hints: list[str] = []
    if publication.uncertainty_calibration_refs and (
        target_snapshot.trace.degradation_records
        or target_snapshot.session.brake_history
        or target_snapshot.trace.wake_receipts
    ):
        hints.append("offline-uncertainty-calibration")
    return tuple(hints)


def _derive_temporal_burden(
    publication: OfflineSupportPublication,
    *,
    retrieval_shadow_candidates: tuple[AuxMatchScore, ...],
    branch_resume_matches: tuple[AuxMatchScore, ...],
    contradiction_clusters: tuple[AuxContradictionCluster, ...],
    source_snapshot_count: int,
) -> AuxBurdenReport:
    publication_ref_count = len(publication.support_refs())
    return AuxBurdenReport(
        compute_overhead=min(1.0, 0.04 * source_snapshot_count),
        memory_overhead=min(
            1.0,
            (0.03 * len(publication.published_memory_summary_refs))
            + (0.02 * len(publication.retrieval_prior_refs)),
        ),
        latency_overhead=min(
            1.0,
            (0.02 * source_snapshot_count)
            + (0.01 * len(publication.uncertainty_calibration_refs)),
        ),
        environment_query_cost=min(1.0, 0.03 * len(publication.contradiction_summary_refs)),
        retrieval_cost=min(
            1.0,
            (0.06 * len(retrieval_shadow_candidates))
            + (0.01 * publication_ref_count),
        ),
        intervention_burden=min(
            1.0,
            (0.05 * len(branch_resume_matches))
            + (0.04 * len(contradiction_clusters)),
        ),
        metadata=(MetadataField("source", "aux/temporal-corpus"),),
    )


def _build_case_failure_reasons(lift_report: AuxLiftReport) -> tuple[str, ...]:
    metric_map = {metric.metric_tag: metric for metric in lift_report.metrics}
    quality_improved_count = sum(
        1
        for metric in lift_report.metrics
        if metric.metric_tag != "burden_overhead_cost" and metric.improved
    )
    reasons: list[str] = []
    if quality_improved_count == 0:
        reasons.append("no quality lift over baseline target")
    if quality_improved_count == 0 and not metric_map["burden_overhead_cost"].improved:
        reasons.append("burden increased without offsetting quality lift")
    if _metric_regressed(metric_map["contradiction_preserving_clustering_quality"]):
        reasons.append("contradiction preservation regressed")
    return tuple(reasons)


def _metric_summary_passed(summary: "AuxCorpusMetricSummary") -> bool:
    if AUX_LIFT_DIRECTIONS[summary.metric_tag] == "higher_is_better":
        return summary.improved_case_count > summary.regressed_case_count and summary.average_delta > 0.0
    return summary.improved_case_count > summary.regressed_case_count and summary.average_delta < 0.0


@dataclass(frozen=True, slots=True)
class AuxEvaluationResult:
    geometry_report: AuxGeometryReport
    lift_report: AuxLiftReport


@dataclass(frozen=True, slots=True)
class AuxTemporalScenario:
    scenario_id: str
    source_snapshots: tuple[SupportSnapshot, ...]
    target_snapshot: SupportSnapshot
    notes: tuple[str, ...] = field(default_factory=tuple)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not (isinstance(self.scenario_id, str) and self.scenario_id.strip()):
            raise ValueError("AuxTemporalScenario.scenario_id must be non-empty after trimming.")
        if not isinstance(self.source_snapshots, tuple):
            actual_type = type(self.source_snapshots).__name__
            raise TypeError(
                "AuxTemporalScenario.source_snapshots must be tuple[SupportSnapshot, ...], "
                f"got {actual_type}.",
            )
        if not self.source_snapshots:
            raise ValueError("AuxTemporalScenario.source_snapshots must not be empty.")
        if any(not isinstance(snapshot, SupportSnapshot) for snapshot in self.source_snapshots):
            raise TypeError(
                "AuxTemporalScenario.source_snapshots must contain only SupportSnapshot instances."
            )
        if not isinstance(self.target_snapshot, SupportSnapshot):
            actual_type = type(self.target_snapshot).__name__
            raise TypeError(
                "AuxTemporalScenario.target_snapshot must be SupportSnapshot, "
                f"got {actual_type}.",
            )
        if any(snapshot is self.target_snapshot for snapshot in self.source_snapshots):
            raise ValueError(
                "AuxTemporalScenario requires time-separated source and target snapshots."
            )
        _validate_text_values(self.notes, field_name="AuxTemporalScenario.notes")
        _validate_metadata(self.metadata, field_name="AuxTemporalScenario.metadata")


@dataclass(frozen=True, slots=True)
class AuxCorpusCaseResult:
    scenario_id: str
    publication: OfflineSupportPublication
    augmented_target: AugmentedSupportSnapshot
    support_memory_priors: SupportMemoryPriorAppendix
    baseline_geometry_report: AuxGeometryReport
    geometry_report: AuxGeometryReport
    lift_report: AuxLiftReport
    failure_reasons: tuple[str, ...] = field(default_factory=tuple)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not (isinstance(self.scenario_id, str) and self.scenario_id.strip()):
            raise ValueError("AuxCorpusCaseResult.scenario_id must be non-empty after trimming.")
        if not isinstance(self.publication, OfflineSupportPublication):
            actual_type = type(self.publication).__name__
            raise TypeError(
                "AuxCorpusCaseResult.publication must be OfflineSupportPublication, "
                f"got {actual_type}.",
            )
        if not isinstance(self.augmented_target, AugmentedSupportSnapshot):
            actual_type = type(self.augmented_target).__name__
            raise TypeError(
                "AuxCorpusCaseResult.augmented_target must be AugmentedSupportSnapshot, "
                f"got {actual_type}.",
            )
        if not isinstance(self.support_memory_priors, SupportMemoryPriorAppendix):
            actual_type = type(self.support_memory_priors).__name__
            raise TypeError(
                "AuxCorpusCaseResult.support_memory_priors must be SupportMemoryPriorAppendix, "
                f"got {actual_type}.",
            )
        if not isinstance(self.baseline_geometry_report, AuxGeometryReport):
            actual_type = type(self.baseline_geometry_report).__name__
            raise TypeError(
                "AuxCorpusCaseResult.baseline_geometry_report must be AuxGeometryReport, "
                f"got {actual_type}.",
            )
        if not isinstance(self.geometry_report, AuxGeometryReport):
            actual_type = type(self.geometry_report).__name__
            raise TypeError(
                "AuxCorpusCaseResult.geometry_report must be AuxGeometryReport, "
                f"got {actual_type}.",
            )
        if not isinstance(self.lift_report, AuxLiftReport):
            actual_type = type(self.lift_report).__name__
            raise TypeError(
                "AuxCorpusCaseResult.lift_report must be AuxLiftReport, "
                f"got {actual_type}.",
            )
        _validate_text_values(self.failure_reasons, field_name="AuxCorpusCaseResult.failure_reasons")
        _validate_metadata(self.metadata, field_name="AuxCorpusCaseResult.metadata")


@dataclass(frozen=True, slots=True)
class AuxCorpusMetricSummary:
    metric_tag: str
    improved_case_count: int
    regressed_case_count: int
    average_delta: float
    case_count: int
    improved_case_ids: tuple[str, ...] = field(default_factory=tuple)
    regressed_case_ids: tuple[str, ...] = field(default_factory=tuple)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.metric_tag not in AUX_LIFT_DIRECTIONS:
            raise ValueError(
                "AuxCorpusMetricSummary.metric_tag must be one of the fixed AUX lift metrics."
            )
        _validate_non_negative_int(
            self.improved_case_count,
            field_name="AuxCorpusMetricSummary.improved_case_count",
        )
        _validate_non_negative_int(
            self.regressed_case_count,
            field_name="AuxCorpusMetricSummary.regressed_case_count",
        )
        _validate_non_negative_int(
            self.case_count,
            field_name="AuxCorpusMetricSummary.case_count",
        )
        _validate_finite_number(
            self.average_delta,
            field_name="AuxCorpusMetricSummary.average_delta",
        )
        _validate_text_values(
            self.improved_case_ids,
            field_name="AuxCorpusMetricSummary.improved_case_ids",
        )
        _validate_text_values(
            self.regressed_case_ids,
            field_name="AuxCorpusMetricSummary.regressed_case_ids",
        )
        _validate_metadata(self.metadata, field_name="AuxCorpusMetricSummary.metadata")


@dataclass(frozen=True, slots=True)
class AuxCorpusEvaluationResult:
    case_results: tuple[AuxCorpusCaseResult, ...]
    metric_summaries: tuple[AuxCorpusMetricSummary, ...]
    total_burden: float
    worst_case_burden: float
    retention_recommendation: str
    acceptance_passed: bool
    failure_reasons: tuple[str, ...] = field(default_factory=tuple)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.case_results:
            raise ValueError("AuxCorpusEvaluationResult.case_results must not be empty.")
        if any(not isinstance(case_result, AuxCorpusCaseResult) for case_result in self.case_results):
            raise TypeError(
                "AuxCorpusEvaluationResult.case_results must contain only AuxCorpusCaseResult instances."
            )
        if any(
            not isinstance(summary, AuxCorpusMetricSummary)
            for summary in self.metric_summaries
        ):
            raise TypeError(
                "AuxCorpusEvaluationResult.metric_summaries must contain only AuxCorpusMetricSummary instances."
            )
        metric_tags = {summary.metric_tag for summary in self.metric_summaries}
        if metric_tags != set(AUX_LIFT_DIRECTIONS):
            raise ValueError(
                "AuxCorpusEvaluationResult.metric_summaries must cover the full fixed AUX metric set exactly once."
            )
        _validate_finite_number(self.total_burden, field_name="AuxCorpusEvaluationResult.total_burden")
        _validate_finite_number(self.worst_case_burden, field_name="AuxCorpusEvaluationResult.worst_case_burden")
        if self.retention_recommendation not in {
            "keep-experimental",
            "observe",
            "prune-candidate",
        }:
            raise ValueError(
                "AuxCorpusEvaluationResult.retention_recommendation must be a fixed AUX retention label."
            )
        if not isinstance(self.acceptance_passed, bool):
            actual_type = type(self.acceptance_passed).__name__
            raise TypeError(
                "AuxCorpusEvaluationResult.acceptance_passed must be bool, "
                f"got {actual_type}.",
            )
        _validate_text_values(
            self.failure_reasons,
            field_name="AuxCorpusEvaluationResult.failure_reasons",
        )
        _validate_metadata(self.metadata, field_name="AuxCorpusEvaluationResult.metadata")


def evaluate_aux_support_snapshot(
    snapshot: SupportSnapshot,
) -> AuxEvaluationResult:
    if not isinstance(snapshot, SupportSnapshot):
        actual_type = type(snapshot).__name__
        raise TypeError(
            "evaluate_aux_support_snapshot() requires SupportSnapshot, "
            f"got {actual_type}.",
        )

    geometry_report = build_aux_geometry_report(snapshot)
    retrieval_baseline = 0.10 if snapshot.trace.candidate_refs else 0.0
    branch_baseline = 0.15 if snapshot.session.branch_registry else 0.0
    uncertainty_baseline = 0.15 if snapshot.trace.degradation_records else 0.0
    contradiction_baseline = 0.15 if snapshot.trace.degradation_records else 0.0
    uncertainty_aux_value = min(
        1.0,
        0.15 * len(geometry_report.uncertainty_brake_hints),
    )
    contradiction_aux_value = min(
        1.0,
        0.25 * len(geometry_report.contradiction_clusters),
    )
    lift_report = build_aux_lift_report(
        geometry_report,
        retrieval_usefulness=(
            retrieval_baseline,
            _average_match_score(geometry_report.retrieval_shadow_candidates),
        ),
        branch_resume_fidelity=(
            branch_baseline,
            _average_match_score(geometry_report.branch_resume_matches),
        ),
        uncertainty_brake_diagnostic_lift=(
            uncertainty_baseline,
            uncertainty_aux_value,
        ),
        contradiction_preserving_clustering_quality=(
            contradiction_baseline,
            contradiction_aux_value,
        ),
    )
    return AuxEvaluationResult(
        geometry_report=geometry_report,
        lift_report=lift_report,
    )


def _evaluate_temporal_scenario(
    scenario: AuxTemporalScenario,
) -> AuxCorpusCaseResult:
    publication = _merge_publications(scenario.source_snapshots)
    augmented_target = augment_snapshot_with_offline_publication(
        scenario.target_snapshot,
        publication,
    )
    support_memory_priors = build_support_memory_prior_appendix(augmented_target)
    baseline_geometry_report = build_aux_geometry_report(scenario.target_snapshot)
    temporal_retrieval_candidates = _build_temporal_retrieval_candidates(
        scenario.target_snapshot,
        publication,
    )
    temporal_branch_matches = _build_temporal_branch_matches(
        scenario.target_snapshot,
        publication,
    )
    temporal_contradiction_clusters = _build_temporal_contradiction_clusters(
        scenario.target_snapshot,
        publication,
    )
    temporal_uncertainty_hints = _build_temporal_uncertainty_hints(
        scenario.target_snapshot,
        publication,
    )
    geometry_report = build_aux_geometry_report(
        scenario.target_snapshot,
        retrieval_shadow_candidates=temporal_retrieval_candidates,
        branch_resume_matches=temporal_branch_matches,
        uncertainty_brake_hints=temporal_uncertainty_hints,
        contradiction_clusters=temporal_contradiction_clusters,
        burden=_derive_temporal_burden(
            publication,
            retrieval_shadow_candidates=temporal_retrieval_candidates,
            branch_resume_matches=temporal_branch_matches,
            contradiction_clusters=temporal_contradiction_clusters,
            source_snapshot_count=len(scenario.source_snapshots),
        ),
        metadata=(MetadataField("source", "aux/temporal-corpus"),) + scenario.metadata,
    )
    lift_report = build_aux_lift_report(
        geometry_report,
        retrieval_usefulness=(
            _best_match_score(baseline_geometry_report.retrieval_shadow_candidates),
            _best_match_score(geometry_report.retrieval_shadow_candidates),
        ),
        branch_resume_fidelity=(
            _best_match_score(baseline_geometry_report.branch_resume_matches),
            _best_match_score(geometry_report.branch_resume_matches),
        ),
        uncertainty_brake_diagnostic_lift=(
            _uncertainty_hint_value(baseline_geometry_report),
            _uncertainty_hint_value(geometry_report),
        ),
        contradiction_preserving_clustering_quality=(
            _contradiction_quality(baseline_geometry_report),
            _contradiction_quality(geometry_report),
        ),
        burden_overhead_cost=(
            total_aux_burden(baseline_geometry_report.burden),
            total_aux_burden(geometry_report.burden),
        ),
        metadata=(MetadataField("scenario", scenario.scenario_id),),
    )
    return AuxCorpusCaseResult(
        scenario_id=scenario.scenario_id,
        publication=publication,
        augmented_target=augmented_target,
        support_memory_priors=support_memory_priors,
        baseline_geometry_report=baseline_geometry_report,
        geometry_report=geometry_report,
        lift_report=lift_report,
        failure_reasons=_build_case_failure_reasons(lift_report),
        metadata=scenario.metadata,
    )


def _summarize_metric(
    case_results: tuple[AuxCorpusCaseResult, ...],
    metric_tag: str,
) -> AuxCorpusMetricSummary:
    metrics = tuple(
        next(
            metric
            for metric in case_result.lift_report.metrics
            if metric.metric_tag == metric_tag
        )
        for case_result in case_results
    )
    improved_case_ids = tuple(
        case_result.scenario_id
        for case_result, metric in zip(case_results, metrics)
        if metric.improved
    )
    regressed_case_ids = tuple(
        case_result.scenario_id
        for case_result, metric in zip(case_results, metrics)
        if _metric_regressed(metric)
    )
    return AuxCorpusMetricSummary(
        metric_tag=metric_tag,
        improved_case_count=len(improved_case_ids),
        regressed_case_count=len(regressed_case_ids),
        average_delta=sum(metric.delta_value for metric in metrics) / len(metrics),
        case_count=len(metrics),
        improved_case_ids=improved_case_ids,
        regressed_case_ids=regressed_case_ids,
    )


def _choose_corpus_retention(
    metric_summaries: tuple[AuxCorpusMetricSummary, ...],
    *,
    acceptance_passed: bool,
) -> str:
    if acceptance_passed:
        return "keep-experimental"
    if any(
        summary.metric_tag != "burden_overhead_cost" and summary.improved_case_count > 0
        for summary in metric_summaries
    ):
        return "observe"
    return "prune-candidate"


def evaluate_aux_support_corpus(
    scenarios: tuple[AuxTemporalScenario, ...],
) -> AuxCorpusEvaluationResult:
    if not isinstance(scenarios, tuple):
        actual_type = type(scenarios).__name__
        raise TypeError(
            "evaluate_aux_support_corpus() requires tuple[AuxTemporalScenario, ...], "
            f"got {actual_type}.",
        )
    if not scenarios:
        raise ValueError("evaluate_aux_support_corpus() requires at least one scenario.")
    if any(not isinstance(scenario, AuxTemporalScenario) for scenario in scenarios):
        raise TypeError(
            "evaluate_aux_support_corpus() requires only AuxTemporalScenario instances."
        )

    case_results = tuple(_evaluate_temporal_scenario(scenario) for scenario in scenarios)
    metric_summaries = tuple(
        _summarize_metric(case_results, metric_tag)
        for metric_tag in AUX_LIFT_DIRECTIONS
    )
    improved_metric_count = sum(
        1
        for summary in metric_summaries
        if _metric_summary_passed(summary)
    )
    contradiction_summary = next(
        summary
        for summary in metric_summaries
        if summary.metric_tag == "contradiction_preserving_clustering_quality"
    )
    failure_reasons: list[str] = []
    if improved_metric_count < 3:
        failure_reasons.append("fewer than 3 fixed metrics improved across corpus")
    if contradiction_summary.regressed_case_count > 0:
        failure_reasons.append("contradiction-preserving clustering regressed")
    acceptance_passed = not failure_reasons
    return AuxCorpusEvaluationResult(
        case_results=case_results,
        metric_summaries=metric_summaries,
        total_burden=sum(
            total_aux_burden(case_result.geometry_report.burden)
            for case_result in case_results
        ),
        worst_case_burden=max(
            total_aux_burden(case_result.geometry_report.burden)
            for case_result in case_results
        ),
        retention_recommendation=_choose_corpus_retention(
            metric_summaries,
            acceptance_passed=acceptance_passed,
        ),
        acceptance_passed=acceptance_passed,
        failure_reasons=tuple(failure_reasons),
        metadata=(MetadataField("source", "aux/temporal-corpus"),),
    )


__all__ = [
    "AuxCorpusCaseResult",
    "AuxCorpusEvaluationResult",
    "AuxCorpusMetricSummary",
    "AuxEvaluationResult",
    "AuxTemporalScenario",
    "evaluate_aux_support_corpus",
    "evaluate_aux_support_snapshot",
]
