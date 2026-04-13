"""Cross-host shadow evaluation over explicit AUX-owned Q_mem priors."""

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

from ._temporal_publication import _merge_temporal_publication
from .publication import (
    OfflineSupportPublication,
    augment_snapshot_with_offline_publication,
)
from .support_priors import build_support_memory_prior_appendix

_HOST_NAMES = ("claude", "gemini", "reference")
_FAILURE_LABEL_ORDER = (
    "missing_repeat_stable_host_lift",
    "single_host_only_lift",
    "counterexample_dominates",
    "stale_prior_survives_contradiction",
    "memory_removal_not_reverting",
)

AUX_CROSS_HOST_SHADOW_FAILURE_LABELS = frozenset(
    _FAILURE_LABEL_ORDER
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
    invalid = sorted(set(labels) - AUX_CROSS_HOST_SHADOW_FAILURE_LABELS)
    if invalid:
        raise ValueError(
            f"{field_name} must use only fixed cross-host shadow failure labels, got {invalid!r}."
        )


def _validate_host_name(host_name: str, *, field_name: str) -> None:
    if host_name not in _HOST_NAMES:
        raise ValueError(f"{field_name} must be one of {_HOST_NAMES!r}.")


def _validate_host_count_rows(
    rows: tuple[tuple[str, int], ...],
    *,
    field_name: str,
) -> None:
    if not isinstance(rows, tuple):
        actual_type = type(rows).__name__
        raise TypeError(f"{field_name} must be tuple[tuple[str, int], ...], got {actual_type}.")
    host_names = tuple(host_name for host_name, _ in rows)
    if host_names != _HOST_NAMES:
        raise ValueError(f"{field_name} must cover hosts exactly in {_HOST_NAMES!r}.")
    for host_name, count in rows:
        _validate_host_name(host_name, field_name=f"{field_name}.host_name")
        _validate_non_negative_int(count, field_name=f"{field_name}.{host_name}")


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


def _appendix_has_tag(appendix: SupportMemoryPriorAppendix, tag: str) -> bool:
    return any(tag in score.reason_tags for score in appendix.scores)


def _count_rows(counts: dict[str, int]) -> tuple[tuple[str, int], ...]:
    return tuple((host_name, counts.get(host_name, 0)) for host_name in _HOST_NAMES)


def _choose_dominant_failure_label(counts: dict[str, int]) -> str | None:
    active = {label: count for label, count in counts.items() if count > 0}
    if not active:
        return None
    return max(sorted(active), key=lambda label: active[label])


def _case_failure_labels(
    *,
    expect_improvement: bool,
    replay_selected_family: SoftControlFamily,
    preferred_family: SoftControlFamily,
    preferred_family_delta: float,
    contradiction_invalidated_prior: bool,
    reliability_component_active: bool,
    memory_removal_reverts_to_baseline: bool,
) -> tuple[str, ...]:
    labels: list[str] = []
    if expect_improvement and preferred_family_delta <= 0.0:
        labels.append("missing_repeat_stable_host_lift")
    if not expect_improvement and (
        preferred_family_delta > 0.0 or replay_selected_family is preferred_family
    ):
        labels.append("counterexample_dominates")
    if contradiction_invalidated_prior and reliability_component_active:
        labels.append("stale_prior_survives_contradiction")
    if not memory_removal_reverts_to_baseline:
        labels.append("memory_removal_not_reverting")
    return tuple(labels)


def _positive_case_switch_or_margin(
    case_result: AuxCrossHostShadowCaseResult,
) -> bool:
    return case_result.selected_family_changed_to_preferred or (
        case_result.baseline_selected_family is case_result.preferred_family
        and case_result.replay_selected_family is case_result.preferred_family
        and case_result.preferred_family_allocated_delta > 0.0
    )


@dataclass(frozen=True, slots=True)
class AuxCrossHostShadowScenario:
    scenario_id: str
    host_name: str
    source_snapshots: tuple[SupportSnapshot, ...]
    target_snapshot: SupportSnapshot
    executive_state: ReferenceExecutiveState
    preferred_family: SoftControlFamily
    expect_improvement: bool
    notes: tuple[str, ...] = field(default_factory=tuple)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not (isinstance(self.scenario_id, str) and self.scenario_id.strip()):
            raise ValueError("AuxCrossHostShadowScenario.scenario_id must be non-empty after trimming.")
        _validate_host_name(
            self.host_name,
            field_name="AuxCrossHostShadowScenario.host_name",
        )
        if not isinstance(self.source_snapshots, tuple):
            actual_type = type(self.source_snapshots).__name__
            raise TypeError(
                "AuxCrossHostShadowScenario.source_snapshots must be tuple[SupportSnapshot, ...], "
                f"got {actual_type}.",
            )
        if not self.source_snapshots:
            raise ValueError("AuxCrossHostShadowScenario.source_snapshots must not be empty.")
        if any(not isinstance(snapshot, SupportSnapshot) for snapshot in self.source_snapshots):
            raise TypeError(
                "AuxCrossHostShadowScenario.source_snapshots must contain only SupportSnapshot instances."
            )
        if not isinstance(self.target_snapshot, SupportSnapshot):
            actual_type = type(self.target_snapshot).__name__
            raise TypeError(
                "AuxCrossHostShadowScenario.target_snapshot must be SupportSnapshot, "
                f"got {actual_type}.",
            )
        if any(snapshot is self.target_snapshot for snapshot in self.source_snapshots):
            raise ValueError(
                "AuxCrossHostShadowScenario requires time-separated source and target snapshots."
            )
        if not isinstance(self.executive_state, ReferenceExecutiveState):
            actual_type = type(self.executive_state).__name__
            raise TypeError(
                "AuxCrossHostShadowScenario.executive_state must be ReferenceExecutiveState, "
                f"got {actual_type}.",
            )
        if not isinstance(self.preferred_family, SoftControlFamily):
            actual_type = type(self.preferred_family).__name__
            raise TypeError(
                "AuxCrossHostShadowScenario.preferred_family must be SoftControlFamily, "
                f"got {actual_type}.",
            )
        if not isinstance(self.expect_improvement, bool):
            actual_type = type(self.expect_improvement).__name__
            raise TypeError(
                "AuxCrossHostShadowScenario.expect_improvement must be bool, "
                f"got {actual_type}.",
            )
        _validate_text_values(self.notes, field_name="AuxCrossHostShadowScenario.notes")
        _validate_metadata(self.metadata, field_name="AuxCrossHostShadowScenario.metadata")


@dataclass(frozen=True, slots=True)
class AuxCrossHostShadowCaseResult:
    scenario_id: str
    host_name: str
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
    reliability_component_active: bool
    contradiction_invalidated_prior: bool
    memory_removal_reverts_to_baseline: bool
    failure_labels: tuple[str, ...] = field(default_factory=tuple)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not (isinstance(self.scenario_id, str) and self.scenario_id.strip()):
            raise ValueError("AuxCrossHostShadowCaseResult.scenario_id must be non-empty after trimming.")
        _validate_host_name(
            self.host_name,
            field_name="AuxCrossHostShadowCaseResult.host_name",
        )
        if not isinstance(self.publication, OfflineSupportPublication):
            actual_type = type(self.publication).__name__
            raise TypeError(
                "AuxCrossHostShadowCaseResult.publication must be OfflineSupportPublication, "
                f"got {actual_type}.",
            )
        if not isinstance(self.support_memory_priors, SupportMemoryPriorAppendix):
            actual_type = type(self.support_memory_priors).__name__
            raise TypeError(
                "AuxCrossHostShadowCaseResult.support_memory_priors must be SupportMemoryPriorAppendix, "
                f"got {actual_type}.",
            )
        if not isinstance(self.baseline_scorecard, AllocationScorecard):
            actual_type = type(self.baseline_scorecard).__name__
            raise TypeError(
                "AuxCrossHostShadowCaseResult.baseline_scorecard must be AllocationScorecard, "
                f"got {actual_type}.",
            )
        if not isinstance(self.replay_scorecard, AllocationScorecard):
            actual_type = type(self.replay_scorecard).__name__
            raise TypeError(
                "AuxCrossHostShadowCaseResult.replay_scorecard must be AllocationScorecard, "
                f"got {actual_type}.",
            )
        if not isinstance(self.baseline_selected_family, SoftControlFamily):
            actual_type = type(self.baseline_selected_family).__name__
            raise TypeError(
                "AuxCrossHostShadowCaseResult.baseline_selected_family must be SoftControlFamily, "
                f"got {actual_type}.",
            )
        if not isinstance(self.replay_selected_family, SoftControlFamily):
            actual_type = type(self.replay_selected_family).__name__
            raise TypeError(
                "AuxCrossHostShadowCaseResult.replay_selected_family must be SoftControlFamily, "
                f"got {actual_type}.",
            )
        if not isinstance(self.preferred_family, SoftControlFamily):
            actual_type = type(self.preferred_family).__name__
            raise TypeError(
                "AuxCrossHostShadowCaseResult.preferred_family must be SoftControlFamily, "
                f"got {actual_type}.",
            )
        _validate_finite_number(
            self.preferred_family_baseline_score,
            field_name="AuxCrossHostShadowCaseResult.preferred_family_baseline_score",
        )
        _validate_finite_number(
            self.preferred_family_replay_score,
            field_name="AuxCrossHostShadowCaseResult.preferred_family_replay_score",
        )
        _validate_finite_number(
            self.preferred_family_allocated_delta,
            field_name="AuxCrossHostShadowCaseResult.preferred_family_allocated_delta",
        )
        for field_name in (
            "selected_family_changed_to_preferred",
            "expect_improvement",
            "reliability_component_active",
            "contradiction_invalidated_prior",
            "memory_removal_reverts_to_baseline",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, bool):
                actual_type = type(value).__name__
                raise TypeError(
                    f"AuxCrossHostShadowCaseResult.{field_name} must be bool, got {actual_type}."
                )
        _validate_failure_labels(
            self.failure_labels,
            field_name="AuxCrossHostShadowCaseResult.failure_labels",
        )
        _validate_metadata(
            self.metadata,
            field_name="AuxCrossHostShadowCaseResult.metadata",
        )


@dataclass(frozen=True, slots=True)
class AuxCrossHostShadowEvaluationResult:
    case_results: tuple[AuxCrossHostShadowCaseResult, ...]
    per_host_positive_case_counts: tuple[tuple[str, int], ...]
    per_host_improved_case_counts: tuple[tuple[str, int], ...]
    per_host_negative_stable_counts: tuple[tuple[str, int], ...]
    repeat_stable_hosts: tuple[str, ...]
    counterexample_case_count: int
    acceptance_passed: bool
    dominant_failure_label: str | None = None
    failure_labels: tuple[str, ...] = field(default_factory=tuple)
    failure_reasons: tuple[str, ...] = field(default_factory=tuple)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.case_results:
            raise ValueError("AuxCrossHostShadowEvaluationResult.case_results must not be empty.")
        if any(not isinstance(case_result, AuxCrossHostShadowCaseResult) for case_result in self.case_results):
            raise TypeError(
                "AuxCrossHostShadowEvaluationResult.case_results must contain only AuxCrossHostShadowCaseResult instances."
            )
        _validate_host_count_rows(
            self.per_host_positive_case_counts,
            field_name="AuxCrossHostShadowEvaluationResult.per_host_positive_case_counts",
        )
        _validate_host_count_rows(
            self.per_host_improved_case_counts,
            field_name="AuxCrossHostShadowEvaluationResult.per_host_improved_case_counts",
        )
        _validate_host_count_rows(
            self.per_host_negative_stable_counts,
            field_name="AuxCrossHostShadowEvaluationResult.per_host_negative_stable_counts",
        )
        if any(host_name not in _HOST_NAMES for host_name in self.repeat_stable_hosts):
            raise ValueError(
                "AuxCrossHostShadowEvaluationResult.repeat_stable_hosts must contain only canonical host names."
            )
        _validate_non_negative_int(
            self.counterexample_case_count,
            field_name="AuxCrossHostShadowEvaluationResult.counterexample_case_count",
        )
        if not isinstance(self.acceptance_passed, bool):
            actual_type = type(self.acceptance_passed).__name__
            raise TypeError(
                "AuxCrossHostShadowEvaluationResult.acceptance_passed must be bool, "
                f"got {actual_type}.",
            )
        if self.dominant_failure_label is not None:
            _validate_failure_labels(
                (self.dominant_failure_label,),
                field_name="AuxCrossHostShadowEvaluationResult.dominant_failure_label",
            )
        _validate_failure_labels(
            self.failure_labels,
            field_name="AuxCrossHostShadowEvaluationResult.failure_labels",
        )
        _validate_text_values(
            self.failure_reasons,
            field_name="AuxCrossHostShadowEvaluationResult.failure_reasons",
        )
        _validate_metadata(
            self.metadata,
            field_name="AuxCrossHostShadowEvaluationResult.metadata",
        )


def evaluate_aux_cross_host_shadow(
    scenarios: tuple[AuxCrossHostShadowScenario, ...],
) -> AuxCrossHostShadowEvaluationResult:
    if not isinstance(scenarios, tuple):
        actual_type = type(scenarios).__name__
        raise TypeError(
            "evaluate_aux_cross_host_shadow() requires tuple[AuxCrossHostShadowScenario, ...], "
            f"got {actual_type}.",
        )
    if not scenarios:
        raise ValueError("evaluate_aux_cross_host_shadow() requires at least one scenario.")
    if any(not isinstance(scenario, AuxCrossHostShadowScenario) for scenario in scenarios):
        raise TypeError(
            "evaluate_aux_cross_host_shadow() requires only AuxCrossHostShadowScenario instances."
        )

    case_results: list[AuxCrossHostShadowCaseResult] = []
    failure_counts = {label: 0 for label in AUX_CROSS_HOST_SHADOW_FAILURE_LABELS}
    positive_case_counts = {host_name: 0 for host_name in _HOST_NAMES}
    improved_case_counts = {host_name: 0 for host_name in _HOST_NAMES}
    negative_stable_counts = {host_name: 0 for host_name in _HOST_NAMES}

    for scenario in scenarios:
        publication = _merge_temporal_publication(
            scenario.source_snapshots,
            source_label="aux/cross-host-shadow",
            extra_tags=frozenset({"aux/offline-publication", "aux/cross-host-shadow"}),
            extra_notes=("offline publication replayed into cross-host shadow-only Q_mem evaluation",),
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
        removed_selection = select_reference_soft_control(
            scenario.executive_state,
            memory_priors=SupportMemoryPriorAppendix(),
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
        reliability_component_active = _appendix_has_tag(
            support_memory_priors,
            "q_mem-host:reliability-active",
        )
        contradiction_invalidated_prior = _appendix_has_tag(
            support_memory_priors,
            "q_mem-host:contradiction-invalidated",
        )
        memory_removal_reverts_to_baseline = (
            removed_selection.selected_family is baseline_selection.selected_family
            and removed_selection.scorecard == baseline_selection.scorecard
        )
        failure_labels = _case_failure_labels(
            expect_improvement=scenario.expect_improvement,
            replay_selected_family=replay_selection.selected_family,
            preferred_family=scenario.preferred_family,
            preferred_family_delta=preferred_family_delta,
            contradiction_invalidated_prior=contradiction_invalidated_prior,
            reliability_component_active=reliability_component_active,
            memory_removal_reverts_to_baseline=memory_removal_reverts_to_baseline,
        )
        case_result = AuxCrossHostShadowCaseResult(
            scenario_id=scenario.scenario_id,
            host_name=scenario.host_name,
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
            reliability_component_active=reliability_component_active,
            contradiction_invalidated_prior=contradiction_invalidated_prior,
            memory_removal_reverts_to_baseline=memory_removal_reverts_to_baseline,
            failure_labels=failure_labels,
            metadata=scenario.metadata,
        )
        case_results.append(case_result)
        if scenario.expect_improvement:
            positive_case_counts[scenario.host_name] += 1
            if preferred_family_delta > 0.0:
                improved_case_counts[scenario.host_name] += 1
        elif (
            preferred_family_delta <= 0.0
            and replay_selection.selected_family is not scenario.preferred_family
        ):
            negative_stable_counts[scenario.host_name] += 1

    case_results_tuple = tuple(case_results)
    repeat_stable_hosts: list[str] = []
    counterexample_case_count = 0
    stale_prior_survives_contradiction = False
    memory_removal_not_reverting = False
    failure_reasons: list[str] = []

    for host_name in _HOST_NAMES:
        host_positive_cases = tuple(
            result
            for result in case_results_tuple
            if result.host_name == host_name and result.expect_improvement
        )
        host_negative_cases = tuple(
            result
            for result in case_results_tuple
            if result.host_name == host_name and not result.expect_improvement
        )
        if len(host_positive_cases) != positive_case_counts[host_name]:
            positive_case_counts[host_name] = len(host_positive_cases)
        if len(host_negative_cases) - negative_stable_counts[host_name] > 0:
            counterexample_case_count += len(host_negative_cases) - negative_stable_counts[host_name]
        if any(
            result.contradiction_invalidated_prior and result.reliability_component_active
            for result in host_negative_cases
        ):
            stale_prior_survives_contradiction = True
        if any(not result.memory_removal_reverts_to_baseline for result in case_results_tuple):
            memory_removal_not_reverting = True
        if (
            len(host_positive_cases) >= 2
            and improved_case_counts[host_name] == len(host_positive_cases)
            and negative_stable_counts[host_name] == len(host_negative_cases)
            and any(_positive_case_switch_or_margin(result) for result in host_positive_cases)
        ):
            repeat_stable_hosts.append(host_name)

    if len(repeat_stable_hosts) < len(_HOST_NAMES):
        failure_counts["missing_repeat_stable_host_lift"] += 1
        failure_reasons.append(
            "not every host produced repeat-stable positive lift with stable negative cases"
        )
    if 0 < len(repeat_stable_hosts) < len(_HOST_NAMES):
        failure_counts["single_host_only_lift"] += 1
        failure_reasons.append(
            "cross-host shadow lift remained partial instead of holding across claude, gemini, and reference"
        )
    if counterexample_case_count > 0:
        failure_counts["counterexample_dominates"] += 1
        failure_reasons.append(
            "one or more negative cross-host shadow counterexamples improved or selected the preferred family"
        )
    if stale_prior_survives_contradiction:
        failure_counts["stale_prior_survives_contradiction"] += 1
        failure_reasons.append(
            "fresh contradiction did not zero the reliability-derived component on at least one shadow case"
        )
    if memory_removal_not_reverting:
        failure_counts["memory_removal_not_reverting"] += 1
        failure_reasons.append(
            "removing the explicit support-memory appendix did not return behavior to the online-only baseline"
        )

    failure_labels = tuple(label for label in _FAILURE_LABEL_ORDER if failure_counts[label] > 0)
    acceptance_passed = not failure_reasons

    return AuxCrossHostShadowEvaluationResult(
        case_results=case_results_tuple,
        per_host_positive_case_counts=_count_rows(positive_case_counts),
        per_host_improved_case_counts=_count_rows(improved_case_counts),
        per_host_negative_stable_counts=_count_rows(negative_stable_counts),
        repeat_stable_hosts=tuple(repeat_stable_hosts),
        counterexample_case_count=counterexample_case_count,
        acceptance_passed=acceptance_passed,
        dominant_failure_label=_choose_dominant_failure_label(failure_counts),
        failure_labels=failure_labels,
        failure_reasons=tuple(failure_reasons),
        metadata=(MetadataField("source", "aux/cross-host-shadow"),),
    )


__all__ = [
    "AUX_CROSS_HOST_SHADOW_FAILURE_LABELS",
    "AuxCrossHostShadowCaseResult",
    "AuxCrossHostShadowEvaluationResult",
    "AuxCrossHostShadowScenario",
    "evaluate_aux_cross_host_shadow",
]
