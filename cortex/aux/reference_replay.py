"""Reference-only replay evaluation over explicit AUX-owned Q_mem priors."""

from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite
from numbers import Real

from cortex.core.envelopes import MetadataField
from cortex.core.support import SupportSnapshot
from cortex.sre.allocation import AllocationScorecard
from cortex.sre.families import SoftControlFamily
from cortex.sre.memory_priors import SupportMemoryPriorAppendix
from cortex.sre.reference_scoring import select_reference_soft_control
from cortex.sre.state import ReferenceExecutiveState

from .distillation import _distill_offline_support_publication_from_snapshots
from .publication import (
    OfflineSupportPublication,
    augment_snapshot_with_offline_publication,
)
from .support_priors import build_support_memory_prior_appendix


AUX_REFERENCE_REPLAY_FAILURE_LABELS = frozenset(
    {
        "no_preferred_family_lift",
        "no_selected_family_change",
        "counterexample_dominates",
    }
)


def _validate_text_values(
    values: tuple[str, ...],
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


def _validate_failure_labels(
    labels: tuple[str, ...],
    *,
    field_name: str,
) -> None:
    _validate_text_values(labels, field_name=field_name)
    invalid = sorted(set(labels) - AUX_REFERENCE_REPLAY_FAILURE_LABELS)
    if invalid:
        raise ValueError(
            f"{field_name} must use only fixed replay failure labels, got {invalid!r}."
        )


def _allocated_score(scorecard: AllocationScorecard, family: SoftControlFamily) -> float:
    for score in scorecard.scores:
        if score.family is family:
            return float(score.allocated_score)
    raise KeyError(f"Missing allocation score for family {family.value!r}.")


def _reason_tags(scorecard: AllocationScorecard, family: SoftControlFamily) -> frozenset[str]:
    for score in scorecard.scores:
        if score.family is family:
            return score.reason_tags
    raise KeyError(f"Missing allocation score for family {family.value!r}.")


def _choose_dominant_failure_label(counts: dict[str, int]) -> str | None:
    active = {label: count for label, count in counts.items() if count > 0}
    if not active:
        return None
    return max(sorted(active), key=lambda label: active[label])


def _case_result_by_id(
    case_results: tuple[AuxReferenceReplayCaseResult, ...],
    scenario_id: str,
) -> AuxReferenceReplayCaseResult | None:
    for result in case_results:
        if result.scenario_id == scenario_id:
            return result
    return None


@dataclass(frozen=True, slots=True)
class AuxReferenceReplayScenario:
    scenario_id: str
    source_snapshots: tuple[SupportSnapshot, ...]
    target_snapshot: SupportSnapshot
    executive_state: ReferenceExecutiveState
    preferred_family: SoftControlFamily
    expect_improvement: bool
    notes: tuple[str, ...] = field(default_factory=tuple)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not (isinstance(self.scenario_id, str) and self.scenario_id.strip()):
            raise ValueError("AuxReferenceReplayScenario.scenario_id must be non-empty after trimming.")
        if not isinstance(self.source_snapshots, tuple):
            actual_type = type(self.source_snapshots).__name__
            raise TypeError(
                "AuxReferenceReplayScenario.source_snapshots must be tuple[SupportSnapshot, ...], "
                f"got {actual_type}.",
            )
        if not self.source_snapshots:
            raise ValueError("AuxReferenceReplayScenario.source_snapshots must not be empty.")
        if any(not isinstance(snapshot, SupportSnapshot) for snapshot in self.source_snapshots):
            raise TypeError(
                "AuxReferenceReplayScenario.source_snapshots must contain only SupportSnapshot instances."
            )
        if not isinstance(self.target_snapshot, SupportSnapshot):
            actual_type = type(self.target_snapshot).__name__
            raise TypeError(
                "AuxReferenceReplayScenario.target_snapshot must be SupportSnapshot, "
                f"got {actual_type}.",
            )
        if any(snapshot is self.target_snapshot for snapshot in self.source_snapshots):
            raise ValueError(
                "AuxReferenceReplayScenario requires time-separated source and target snapshots."
            )
        if not isinstance(self.executive_state, ReferenceExecutiveState):
            actual_type = type(self.executive_state).__name__
            raise TypeError(
                "AuxReferenceReplayScenario.executive_state must be ReferenceExecutiveState, "
                f"got {actual_type}.",
            )
        if not isinstance(self.preferred_family, SoftControlFamily):
            actual_type = type(self.preferred_family).__name__
            raise TypeError(
                "AuxReferenceReplayScenario.preferred_family must be SoftControlFamily, "
                f"got {actual_type}.",
            )
        if not isinstance(self.expect_improvement, bool):
            actual_type = type(self.expect_improvement).__name__
            raise TypeError(
                "AuxReferenceReplayScenario.expect_improvement must be bool, "
                f"got {actual_type}.",
            )
        _validate_text_values(self.notes, field_name="AuxReferenceReplayScenario.notes")
        _validate_metadata(self.metadata, field_name="AuxReferenceReplayScenario.metadata")


@dataclass(frozen=True, slots=True)
class AuxReferenceReplayCaseResult:
    scenario_id: str
    publication: OfflineSupportPublication
    support_memory_priors: SupportMemoryPriorAppendix
    baseline_scorecard: AllocationScorecard
    replay_scorecard: AllocationScorecard
    baseline_selected_family: SoftControlFamily
    replay_selected_family: SoftControlFamily
    preferred_family: SoftControlFamily
    preferred_family_baseline_score: float
    preferred_family_replay_score: float
    preferred_family_allocated_delta: float
    selected_family_changed_to_preferred: bool
    expect_improvement: bool
    failure_labels: tuple[str, ...] = field(default_factory=tuple)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not (isinstance(self.scenario_id, str) and self.scenario_id.strip()):
            raise ValueError("AuxReferenceReplayCaseResult.scenario_id must be non-empty after trimming.")
        if not isinstance(self.publication, OfflineSupportPublication):
            actual_type = type(self.publication).__name__
            raise TypeError(
                "AuxReferenceReplayCaseResult.publication must be OfflineSupportPublication, "
                f"got {actual_type}.",
            )
        if not isinstance(self.support_memory_priors, SupportMemoryPriorAppendix):
            actual_type = type(self.support_memory_priors).__name__
            raise TypeError(
                "AuxReferenceReplayCaseResult.support_memory_priors must be SupportMemoryPriorAppendix, "
                f"got {actual_type}.",
            )
        if not isinstance(self.baseline_scorecard, AllocationScorecard):
            actual_type = type(self.baseline_scorecard).__name__
            raise TypeError(
                "AuxReferenceReplayCaseResult.baseline_scorecard must be AllocationScorecard, "
                f"got {actual_type}.",
            )
        if not isinstance(self.replay_scorecard, AllocationScorecard):
            actual_type = type(self.replay_scorecard).__name__
            raise TypeError(
                "AuxReferenceReplayCaseResult.replay_scorecard must be AllocationScorecard, "
                f"got {actual_type}.",
            )
        if not isinstance(self.baseline_selected_family, SoftControlFamily):
            actual_type = type(self.baseline_selected_family).__name__
            raise TypeError(
                "AuxReferenceReplayCaseResult.baseline_selected_family must be SoftControlFamily, "
                f"got {actual_type}.",
            )
        if not isinstance(self.replay_selected_family, SoftControlFamily):
            actual_type = type(self.replay_selected_family).__name__
            raise TypeError(
                "AuxReferenceReplayCaseResult.replay_selected_family must be SoftControlFamily, "
                f"got {actual_type}.",
            )
        if not isinstance(self.preferred_family, SoftControlFamily):
            actual_type = type(self.preferred_family).__name__
            raise TypeError(
                "AuxReferenceReplayCaseResult.preferred_family must be SoftControlFamily, "
                f"got {actual_type}.",
            )
        _validate_finite_number(
            self.preferred_family_baseline_score,
            field_name="AuxReferenceReplayCaseResult.preferred_family_baseline_score",
        )
        _validate_finite_number(
            self.preferred_family_replay_score,
            field_name="AuxReferenceReplayCaseResult.preferred_family_replay_score",
        )
        _validate_finite_number(
            self.preferred_family_allocated_delta,
            field_name="AuxReferenceReplayCaseResult.preferred_family_allocated_delta",
        )
        if not isinstance(self.selected_family_changed_to_preferred, bool):
            actual_type = type(self.selected_family_changed_to_preferred).__name__
            raise TypeError(
                "AuxReferenceReplayCaseResult.selected_family_changed_to_preferred must be bool, "
                f"got {actual_type}.",
            )
        if not isinstance(self.expect_improvement, bool):
            actual_type = type(self.expect_improvement).__name__
            raise TypeError(
                "AuxReferenceReplayCaseResult.expect_improvement must be bool, "
                f"got {actual_type}.",
            )
        _validate_failure_labels(
            self.failure_labels,
            field_name="AuxReferenceReplayCaseResult.failure_labels",
        )
        _validate_metadata(
            self.metadata,
            field_name="AuxReferenceReplayCaseResult.metadata",
        )


@dataclass(frozen=True, slots=True)
class AuxReferenceReplayEvaluationResult:
    case_results: tuple[AuxReferenceReplayCaseResult, ...]
    improved_preferred_family_case_count: int
    selected_family_change_case_count: int
    negative_case_stable_count: int
    counterexample_case_count: int
    acceptance_passed: bool
    dominant_failure_label: str | None = None
    failure_labels: tuple[str, ...] = field(default_factory=tuple)
    failure_reasons: tuple[str, ...] = field(default_factory=tuple)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.case_results:
            raise ValueError("AuxReferenceReplayEvaluationResult.case_results must not be empty.")
        if any(not isinstance(case_result, AuxReferenceReplayCaseResult) for case_result in self.case_results):
            raise TypeError(
                "AuxReferenceReplayEvaluationResult.case_results must contain only AuxReferenceReplayCaseResult instances."
            )
        _validate_non_negative_int(
            self.improved_preferred_family_case_count,
            field_name="AuxReferenceReplayEvaluationResult.improved_preferred_family_case_count",
        )
        _validate_non_negative_int(
            self.selected_family_change_case_count,
            field_name="AuxReferenceReplayEvaluationResult.selected_family_change_case_count",
        )
        _validate_non_negative_int(
            self.negative_case_stable_count,
            field_name="AuxReferenceReplayEvaluationResult.negative_case_stable_count",
        )
        _validate_non_negative_int(
            self.counterexample_case_count,
            field_name="AuxReferenceReplayEvaluationResult.counterexample_case_count",
        )
        if not isinstance(self.acceptance_passed, bool):
            actual_type = type(self.acceptance_passed).__name__
            raise TypeError(
                "AuxReferenceReplayEvaluationResult.acceptance_passed must be bool, "
                f"got {actual_type}.",
            )
        if self.dominant_failure_label is not None:
            _validate_failure_labels(
                (self.dominant_failure_label,),
                field_name="AuxReferenceReplayEvaluationResult.dominant_failure_label",
            )
        _validate_failure_labels(
            self.failure_labels,
            field_name="AuxReferenceReplayEvaluationResult.failure_labels",
        )
        _validate_text_values(
            self.failure_reasons,
            field_name="AuxReferenceReplayEvaluationResult.failure_reasons",
        )
        _validate_metadata(
            self.metadata,
            field_name="AuxReferenceReplayEvaluationResult.metadata",
        )


def _case_failure_labels(
    *,
    expect_improvement: bool,
    baseline_selected_family: SoftControlFamily,
    replay_selected_family: SoftControlFamily,
    preferred_family: SoftControlFamily,
    preferred_family_delta: float,
) -> tuple[str, ...]:
    labels: list[str] = []
    if expect_improvement:
        if preferred_family_delta <= 0.0:
            labels.append("no_preferred_family_lift")
        if (
            baseline_selected_family is not preferred_family
            and replay_selected_family is not preferred_family
        ):
            labels.append("no_selected_family_change")
    elif preferred_family_delta > 0.0 or (
        baseline_selected_family is not preferred_family
        and replay_selected_family is preferred_family
    ):
        labels.append("counterexample_dominates")
    return tuple(labels)


def evaluate_aux_reference_q_mem_replay(
    scenarios: tuple[AuxReferenceReplayScenario, ...],
) -> AuxReferenceReplayEvaluationResult:
    if not isinstance(scenarios, tuple):
        actual_type = type(scenarios).__name__
        raise TypeError(
            "evaluate_aux_reference_q_mem_replay() requires tuple[AuxReferenceReplayScenario, ...], "
            f"got {actual_type}.",
        )
    if not scenarios:
        raise ValueError("evaluate_aux_reference_q_mem_replay() requires at least one scenario.")
    if any(not isinstance(scenario, AuxReferenceReplayScenario) for scenario in scenarios):
        raise TypeError(
            "evaluate_aux_reference_q_mem_replay() requires only AuxReferenceReplayScenario instances."
        )

    case_results: list[AuxReferenceReplayCaseResult] = []
    failure_counts = {label: 0 for label in AUX_REFERENCE_REPLAY_FAILURE_LABELS}

    for scenario in scenarios:
        publication = _distill_offline_support_publication_from_snapshots(
            scenario.source_snapshots,
            host_name="reference",
            source_label="aux/reference-replay",
            publication_tags=frozenset({"aux/offline-publication", "aux/reference-replay"}),
            notes=("offline publication replayed into reference-only Q_mem evaluation",),
        )
        augmented_target = augment_snapshot_with_offline_publication(
            scenario.target_snapshot,
            publication,
        )
        support_memory_priors = build_support_memory_prior_appendix(augmented_target)
        baseline_selection = select_reference_soft_control(scenario.executive_state)
        replay_selection = select_reference_soft_control(
            scenario.executive_state,
            memory_priors=support_memory_priors,
        )
        baseline_preferred_score = _allocated_score(
            baseline_selection.scorecard,
            scenario.preferred_family,
        )
        replay_preferred_score = _allocated_score(
            replay_selection.scorecard,
            scenario.preferred_family,
        )
        preferred_family_delta = replay_preferred_score - baseline_preferred_score
        selected_family_changed_to_preferred = (
            baseline_selection.selected_family is not scenario.preferred_family
            and replay_selection.selected_family is scenario.preferred_family
        )
        failure_labels = _case_failure_labels(
            expect_improvement=scenario.expect_improvement,
            baseline_selected_family=baseline_selection.selected_family,
            replay_selected_family=replay_selection.selected_family,
            preferred_family=scenario.preferred_family,
            preferred_family_delta=preferred_family_delta,
        )
        case_results.append(
            AuxReferenceReplayCaseResult(
                scenario_id=scenario.scenario_id,
                publication=publication,
                support_memory_priors=support_memory_priors,
                baseline_scorecard=baseline_selection.scorecard,
                replay_scorecard=replay_selection.scorecard,
                baseline_selected_family=baseline_selection.selected_family,
                replay_selected_family=replay_selection.selected_family,
                preferred_family=scenario.preferred_family,
                preferred_family_baseline_score=baseline_preferred_score,
                preferred_family_replay_score=replay_preferred_score,
                preferred_family_allocated_delta=preferred_family_delta,
                selected_family_changed_to_preferred=selected_family_changed_to_preferred,
                expect_improvement=scenario.expect_improvement,
                failure_labels=failure_labels,
                metadata=scenario.metadata,
            )
        )

    positive_results = tuple(result for result in case_results if result.expect_improvement)
    negative_results = tuple(result for result in case_results if not result.expect_improvement)
    improved_preferred_family_case_count = sum(
        1 for result in positive_results if result.preferred_family_allocated_delta > 0.0
    )
    selected_family_change_case_count = sum(
        1 for result in positive_results if result.selected_family_changed_to_preferred
    )
    negative_case_stable_count = sum(
        1
        for result in negative_results
        if (
            result.preferred_family_allocated_delta <= 0.0
            and result.replay_selected_family is not result.preferred_family
        )
    )
    counterexample_case_count = len(negative_results) - negative_case_stable_count
    contradiction_case = _case_result_by_id(tuple(case_results), "contradiction-review")
    uncertainty_case = _case_result_by_id(tuple(case_results), "uncertainty-brake-calibration")
    contradiction_reason_tags_preserved = (
        contradiction_case is None
        or "q_mem-signal:contradiction"
        in _reason_tags(contradiction_case.replay_scorecard, SoftControlFamily.CHECK)
    )
    uncertainty_reason_tags_preserved = (
        uncertainty_case is None
        or "q_mem-signal:uncertainty"
        in _reason_tags(uncertainty_case.replay_scorecard, SoftControlFamily.BRAKE)
    )
    if improved_preferred_family_case_count < len(positive_results):
        failure_counts["no_preferred_family_lift"] += 1
    if selected_family_change_case_count < 1:
        failure_counts["no_selected_family_change"] += 1
    if counterexample_case_count > 0:
        failure_counts["counterexample_dominates"] += 1

    failure_labels = tuple(
        label for label in AUX_REFERENCE_REPLAY_FAILURE_LABELS if failure_counts[label] > 0
    )
    failure_reasons: list[str] = []
    if improved_preferred_family_case_count < len(positive_results):
        failure_reasons.append(
            "not all positive replay scenarios improved preferred-family allocated score"
        )
    if selected_family_change_case_count < 1:
        failure_reasons.append(
            "no positive replay scenario changed selected_family to preferred_family"
        )
    if counterexample_case_count > 0:
        failure_reasons.append(
            "one or more negative replay counterexamples improved or selected the preferred family"
        )
    if not contradiction_reason_tags_preserved:
        failure_reasons.append(
            "contradiction-review replay did not preserve q_mem contradiction signal tags"
        )
    if not uncertainty_reason_tags_preserved:
        failure_reasons.append(
            "uncertainty-brake replay did not preserve q_mem uncertainty signal tags"
        )
    acceptance_passed = not failure_reasons

    return AuxReferenceReplayEvaluationResult(
        case_results=tuple(case_results),
        improved_preferred_family_case_count=improved_preferred_family_case_count,
        selected_family_change_case_count=selected_family_change_case_count,
        negative_case_stable_count=negative_case_stable_count,
        counterexample_case_count=counterexample_case_count,
        acceptance_passed=acceptance_passed,
        dominant_failure_label=_choose_dominant_failure_label(failure_counts),
        failure_labels=failure_labels,
        failure_reasons=tuple(failure_reasons),
        metadata=(MetadataField("source", "aux/reference-replay"),),
    )


__all__ = [
    "AUX_REFERENCE_REPLAY_FAILURE_LABELS",
    "AuxReferenceReplayCaseResult",
    "AuxReferenceReplayEvaluationResult",
    "AuxReferenceReplayScenario",
    "evaluate_aux_reference_q_mem_replay",
]
