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
_SCENARIO_CLASSES = (
    "retrieval_reuse",
    "branch_resume",
    "check_review",
    "weighted_burden_counterexample",
    "fresh_contradiction_invalidation",
)
_CONTINUITY_BASES = ("host_local", "reference_projected", "not_applicable")
_CLAIM_MODES = ("full_cross_host", "reference_plus_shared_non_reference_shell")
_NON_REFERENCE_EVIDENCE_MODES = ("host_distinct", "shared_shell")
_FAILURE_LABEL_ORDER = (
    "missing_repeat_stable_host_lift",
    "single_host_only_lift",
    "counterexample_dominates",
    "stale_prior_survives_contradiction",
    "memory_removal_not_reverting",
    "missing_branch_family_lift",
    "host_local_branch_basis_insufficient",
    "shared_branch_lift_insufficient",
    "missing_reliability_active_check_lift",
    "weighted_counterexample_dominates",
    "host_aliasing_detected",
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


def _validate_scenario_class(value: str, *, field_name: str) -> None:
    if value not in _SCENARIO_CLASSES:
        raise ValueError(f"{field_name} must be one of {_SCENARIO_CLASSES!r}.")


def _validate_continuity_basis(value: str, *, field_name: str) -> None:
    if value not in _CONTINUITY_BASES:
        raise ValueError(f"{field_name} must be one of {_CONTINUITY_BASES!r}.")


def _validate_claim_mode(value: str, *, field_name: str) -> None:
    if value not in _CLAIM_MODES:
        raise ValueError(f"{field_name} must be one of {_CLAIM_MODES!r}.")


def _validate_non_reference_evidence_mode(value: str, *, field_name: str) -> None:
    if value not in _NON_REFERENCE_EVIDENCE_MODES:
        raise ValueError(f"{field_name} must be one of {_NON_REFERENCE_EVIDENCE_MODES!r}.")


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


def _metadata_value(
    metadata: tuple[MetadataField, ...],
    key: str,
) -> str:
    for field in metadata:
        if field.key == key and isinstance(field.value, str):
            return field.value
    return ""


def _trace_structural_signature(target_snapshot: SupportSnapshot) -> tuple[str, ...]:
    trace_entries: list[str] = []
    for index, event in enumerate(target_snapshot.trace.recent_events):
        payload_kind = (
            event.payload_handle.payload_kind
            if event.payload_handle is not None
            else "none"
        )
        raw_host_event_name = _metadata_value(
            event.payload_metadata,
            "raw_host_event_name",
        ) or "none"
        payload_metadata_keys = ",".join(
            sorted(field.key for field in event.payload_metadata)
        ) or "none"
        trace_entries.append(
            "trace-struct:"
            f"{index}:{event.native_event_name}|{payload_kind}|"
            f"{raw_host_event_name}|{payload_metadata_keys}"
        )
    return tuple(trace_entries)


def _host_signature(
    *,
    scenario_class: str,
    continuity_basis: str,
    target_snapshot: SupportSnapshot,
    executive_state: ReferenceExecutiveState,
    baseline_preferred_score: float,
    replay_preferred_score: float,
) -> tuple[str, ...]:
    return (
        f"scenario-class:{scenario_class}",
        f"continuity-basis:{continuity_basis}",
        "family-mask:" + ",".join(
            sorted(
                family.value
                for family in executive_state.mode_and_gating.family_mask
            )
        ),
        "top-family-set:" + ",".join(
            sorted(
                family.value
                for family in executive_state.control_allocation.top_family_set
            )
        ),
        "host-friction-tags:" + ",".join(
            sorted(executive_state.control_allocation.host_friction_tags)
        ),
        "approval-boundary-tags:" + ",".join(
            sorted(target_snapshot.host.approval_boundary_tags)
        ),
        "affordance-tags:" + ",".join(sorted(target_snapshot.host.affordance_tags)),
        "constraint-tags:" + ",".join(sorted(target_snapshot.host.constraint_tags)),
        f"baseline-preferred-score:{baseline_preferred_score:.6f}",
        f"replay-preferred-score:{replay_preferred_score:.6f}",
        *_trace_structural_signature(target_snapshot),
    )


def _non_reference_scenario_signatures(
    case_results: tuple["AuxCrossHostShadowCaseResult", ...],
) -> dict[tuple[str, str], dict[str, tuple[str, ...]]]:
    scenario_signatures: dict[tuple[str, str], dict[str, tuple[str, ...]]] = {}
    for result in case_results:
        if result.host_name not in {"claude", "gemini"}:
            continue
        scenario_signatures.setdefault(
            (result.scenario_class, result.continuity_basis),
            {},
        )[
            result.host_name
        ] = result.host_signature
    return scenario_signatures


def _non_reference_hosts_alias(
    case_results: tuple["AuxCrossHostShadowCaseResult", ...],
) -> bool:
    scenario_signatures = _non_reference_scenario_signatures(case_results)
    expected_keys = {
        ("retrieval_reuse", "not_applicable"),
        ("branch_resume", "host_local"),
        ("branch_resume", "reference_projected"),
        ("check_review", "not_applicable"),
        ("weighted_burden_counterexample", "not_applicable"),
        ("fresh_contradiction_invalidation", "not_applicable"),
    }
    if set(scenario_signatures) != expected_keys:
        return False
    return all(
        signatures.get("claude") == signatures.get("gemini")
        for signatures in scenario_signatures.values()
    )


def _distinct_non_reference_signature_classes(
    case_results: tuple["AuxCrossHostShadowCaseResult", ...],
) -> tuple[str, ...]:
    scenario_signatures = _non_reference_scenario_signatures(case_results)
    expected_keys = {
        ("retrieval_reuse", "not_applicable"),
        ("branch_resume", "host_local"),
        ("branch_resume", "reference_projected"),
        ("check_review", "not_applicable"),
        ("weighted_burden_counterexample", "not_applicable"),
        ("fresh_contradiction_invalidation", "not_applicable"),
    }
    if set(scenario_signatures) != expected_keys:
        return ()
    distinct_classes = {
        scenario_class
        for (scenario_class, _continuity_basis), signatures in scenario_signatures.items()
        if signatures.get("claude") != signatures.get("gemini")
    }
    return tuple(sorted(distinct_classes))


def _choose_dominant_failure_label(counts: dict[str, int]) -> str | None:
    active = {label: count for label, count in counts.items() if count > 0}
    if not active:
        return None
    order = {label: index for index, label in enumerate(_FAILURE_LABEL_ORDER)}
    return max(
        active,
        key=lambda label: (active[label], -order.get(label, len(_FAILURE_LABEL_ORDER))),
    )


def _case_failure_labels(
    *,
    scenario_class: str,
    expect_improvement: bool,
    replay_selected_family: SoftControlFamily,
    preferred_family: SoftControlFamily,
    preferred_family_total_delta: float,
    preferred_family_reliability_delta: float,
    contradiction_invalidated_prior: bool,
    reliability_component_active: bool,
    memory_removal_reverts_to_baseline: bool,
) -> tuple[str, ...]:
    labels: list[str] = []
    if expect_improvement and preferred_family_total_delta <= 0.0:
        labels.append("missing_repeat_stable_host_lift")
    if (
        scenario_class == "branch_resume"
        and expect_improvement
        and replay_selected_family is not preferred_family
        and preferred_family_total_delta <= 0.0
    ):
        labels.append("missing_branch_family_lift")
    if (
        scenario_class == "check_review"
        and expect_improvement
        and (not reliability_component_active or preferred_family_reliability_delta <= 0.0)
    ):
        labels.append("missing_reliability_active_check_lift")
    if scenario_class == "weighted_burden_counterexample" and (
        preferred_family_total_delta > 0.0 or replay_selected_family is preferred_family
    ):
        labels.append("counterexample_dominates")
    if (
        scenario_class == "weighted_burden_counterexample"
        and (
            preferred_family_total_delta > 0.0
            or replay_selected_family is preferred_family
        )
    ):
        labels.append("weighted_counterexample_dominates")
    if contradiction_invalidated_prior and preferred_family_reliability_delta > 0.0:
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
        and case_result.preferred_family_total_delta > 0.0
    )


@dataclass(frozen=True, slots=True)
class AuxCrossHostShadowScenario:
    scenario_id: str
    scenario_class: str
    host_name: str
    source_snapshots: tuple[SupportSnapshot, ...]
    target_snapshot: SupportSnapshot
    executive_state: ReferenceExecutiveState
    preferred_family: SoftControlFamily
    expect_improvement: bool
    continuity_basis: str = "not_applicable"
    notes: tuple[str, ...] = field(default_factory=tuple)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not (isinstance(self.scenario_id, str) and self.scenario_id.strip()):
            raise ValueError("AuxCrossHostShadowScenario.scenario_id must be non-empty after trimming.")
        _validate_scenario_class(
            self.scenario_class,
            field_name="AuxCrossHostShadowScenario.scenario_class",
        )
        _validate_host_name(
            self.host_name,
            field_name="AuxCrossHostShadowScenario.host_name",
        )
        _validate_continuity_basis(
            self.continuity_basis,
            field_name="AuxCrossHostShadowScenario.continuity_basis",
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
    scenario_class: str
    host_name: str
    continuity_basis: str
    publication: OfflineSupportPublication
    support_memory_priors: SupportMemoryPriorAppendix
    baseline_scorecard: AllocationScorecard
    replay_scorecard: AllocationScorecard
    baseline_selected_family: SoftControlFamily
    replay_selected_family: SoftControlFamily
    preferred_family: SoftControlFamily
    preferred_family_baseline_score: float
    preferred_family_replay_score: float
    preferred_family_total_delta: float
    preferred_family_reliability_delta: float
    preferred_family_uses_reliability_weight: bool
    selected_family_changed_to_preferred: bool
    expect_improvement: bool
    reliability_component_active: bool
    contradiction_invalidated_prior: bool
    memory_removal_reverts_to_baseline: bool
    host_signature: tuple[str, ...]
    failure_labels: tuple[str, ...] = field(default_factory=tuple)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not (isinstance(self.scenario_id, str) and self.scenario_id.strip()):
            raise ValueError("AuxCrossHostShadowCaseResult.scenario_id must be non-empty after trimming.")
        _validate_scenario_class(
            self.scenario_class,
            field_name="AuxCrossHostShadowCaseResult.scenario_class",
        )
        _validate_host_name(
            self.host_name,
            field_name="AuxCrossHostShadowCaseResult.host_name",
        )
        _validate_continuity_basis(
            self.continuity_basis,
            field_name="AuxCrossHostShadowCaseResult.continuity_basis",
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
            self.preferred_family_total_delta,
            field_name="AuxCrossHostShadowCaseResult.preferred_family_total_delta",
        )
        _validate_finite_number(
            self.preferred_family_reliability_delta,
            field_name="AuxCrossHostShadowCaseResult.preferred_family_reliability_delta",
        )
        for field_name in (
            "preferred_family_uses_reliability_weight",
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
        _validate_text_values(
            self.host_signature,
            field_name="AuxCrossHostShadowCaseResult.host_signature",
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
    claim_mode: str = "reference_plus_shared_non_reference_shell"
    non_reference_evidence_mode: str = "shared_shell"
    distinct_signature_classes: tuple[str, ...] = field(default_factory=tuple)
    host_aliasing_detected: bool = False
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
        _validate_claim_mode(
            self.claim_mode,
            field_name="AuxCrossHostShadowEvaluationResult.claim_mode",
        )
        _validate_non_reference_evidence_mode(
            self.non_reference_evidence_mode,
            field_name="AuxCrossHostShadowEvaluationResult.non_reference_evidence_mode",
        )
        for value in self.distinct_signature_classes:
            _validate_scenario_class(
                value,
                field_name="AuxCrossHostShadowEvaluationResult.distinct_signature_classes",
            )
        if not isinstance(self.host_aliasing_detected, bool):
            actual_type = type(self.host_aliasing_detected).__name__
            raise TypeError(
                "AuxCrossHostShadowEvaluationResult.host_aliasing_detected must be bool, "
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
        support_memory_priors_without_reliability = build_support_memory_prior_appendix(
            augmented_target,
            enable_host_reliability=False,
        )
        baseline_selection = select_reference_soft_control(scenario.executive_state)
        replay_selection = select_reference_soft_control(
            scenario.executive_state,
            memory_priors=support_memory_priors,
        )
        replay_without_reliability_selection = select_reference_soft_control(
            scenario.executive_state,
            memory_priors=support_memory_priors_without_reliability,
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
        replay_without_reliability_preferred_score = _allocated_score(
            replay_without_reliability_selection.scorecard,
            scenario.preferred_family,
        )
        preferred_family_total_delta = replay_preferred_score - baseline_preferred_score
        preferred_family_reliability_delta = (
            replay_preferred_score - replay_without_reliability_preferred_score
        )
        selected_family_changed_to_preferred = (
            baseline_selection.selected_family is not scenario.preferred_family
            and replay_selection.selected_family is scenario.preferred_family
        )
        replay_reason_tags = _reason_tags(
            replay_selection.scorecard,
            scenario.preferred_family,
        )
        reliability_component_active = (
            "q_mem-host:reliability-active" in replay_reason_tags
        )
        contradiction_invalidated_prior = (
            "q_mem-host:contradiction-invalidated" in replay_reason_tags
        )
        memory_removal_reverts_to_baseline = (
            removed_selection.selected_family is baseline_selection.selected_family
            and removed_selection.scorecard == baseline_selection.scorecard
        )
        preferred_family_uses_reliability_weight = (
            preferred_family_reliability_delta > 0.0
        )
        host_signature = _host_signature(
            scenario_class=scenario.scenario_class,
            continuity_basis=scenario.continuity_basis,
            target_snapshot=scenario.target_snapshot,
            executive_state=scenario.executive_state,
            baseline_preferred_score=baseline_preferred_score,
            replay_preferred_score=replay_preferred_score,
        )
        failure_labels = _case_failure_labels(
            scenario_class=scenario.scenario_class,
            expect_improvement=scenario.expect_improvement,
            replay_selected_family=replay_selection.selected_family,
            preferred_family=scenario.preferred_family,
            preferred_family_total_delta=preferred_family_total_delta,
            preferred_family_reliability_delta=preferred_family_reliability_delta,
            contradiction_invalidated_prior=contradiction_invalidated_prior,
            reliability_component_active=reliability_component_active,
            memory_removal_reverts_to_baseline=memory_removal_reverts_to_baseline,
        )
        case_result = AuxCrossHostShadowCaseResult(
            scenario_id=scenario.scenario_id,
            scenario_class=scenario.scenario_class,
            host_name=scenario.host_name,
            continuity_basis=scenario.continuity_basis,
            publication=publication,
            support_memory_priors=support_memory_priors,
            baseline_scorecard=baseline_selection.scorecard,
            replay_scorecard=replay_selection.scorecard,
            baseline_selected_family=baseline_selection.selected_family,
            replay_selected_family=replay_selection.selected_family,
            preferred_family=scenario.preferred_family,
            preferred_family_baseline_score=baseline_preferred_score,
            preferred_family_replay_score=replay_preferred_score,
            preferred_family_total_delta=preferred_family_total_delta,
            preferred_family_reliability_delta=preferred_family_reliability_delta,
            preferred_family_uses_reliability_weight=preferred_family_uses_reliability_weight,
            selected_family_changed_to_preferred=selected_family_changed_to_preferred,
            expect_improvement=scenario.expect_improvement,
            reliability_component_active=reliability_component_active,
            contradiction_invalidated_prior=contradiction_invalidated_prior,
            memory_removal_reverts_to_baseline=memory_removal_reverts_to_baseline,
            host_signature=host_signature,
            failure_labels=failure_labels,
            metadata=scenario.metadata,
        )
        case_results.append(case_result)
        if scenario.expect_improvement:
            positive_case_counts[scenario.host_name] += 1
            if preferred_family_total_delta > 0.0:
                improved_case_counts[scenario.host_name] += 1
        elif scenario.scenario_class == "weighted_burden_counterexample":
            if (
                preferred_family_total_delta <= 0.0
                and replay_selection.selected_family is not scenario.preferred_family
                and preferred_family_reliability_delta <= 0.0
            ):
                negative_stable_counts[scenario.host_name] += 1
        elif scenario.scenario_class == "fresh_contradiction_invalidation":
            if (
                preferred_family_reliability_delta <= 0.0
                and replay_selection.selected_family is not scenario.preferred_family
            ):
                negative_stable_counts[scenario.host_name] += 1

    case_results_tuple = tuple(case_results)
    repeat_stable_hosts: list[str] = []
    counterexample_case_count = 0
    weighted_counterexample_dominates = False
    stale_prior_survives_contradiction = False
    memory_removal_not_reverting = any(
        not result.memory_removal_reverts_to_baseline for result in case_results_tuple
    )
    missing_branch_family_lift = False
    host_local_branch_basis_insufficient = False
    shared_branch_lift_insufficient = False
    missing_reliability_active_check_lift = False
    failure_reasons: list[str] = []
    host_aliasing_detected = _non_reference_hosts_alias(case_results_tuple)
    distinct_signature_classes = _distinct_non_reference_signature_classes(
        case_results_tuple
    )

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
        positive_classes = {result.scenario_class for result in host_positive_cases}
        negative_classes = {result.scenario_class for result in host_negative_cases}
        branch_host_local_case = next(
            (
                result
                for result in host_positive_cases
                if result.scenario_class == "branch_resume"
                and result.continuity_basis == "host_local"
            ),
            None,
        )
        branch_reference_projected_case = next(
            (
                result
                for result in host_positive_cases
                if result.scenario_class == "branch_resume"
                and result.continuity_basis == "reference_projected"
            ),
            None,
        )
        check_case = next(
            (
                result
                for result in host_positive_cases
                if result.scenario_class == "check_review"
            ),
            None,
        )
        if len(host_positive_cases) != positive_case_counts[host_name]:
            positive_case_counts[host_name] = len(host_positive_cases)
        unstable_negative_cases = tuple(
            result
            for result in host_negative_cases
            if result.scenario_class == "weighted_burden_counterexample"
            and not (
                result.preferred_family_total_delta <= 0.0
                and result.replay_selected_family is not result.preferred_family
                and result.preferred_family_reliability_delta <= 0.0
            )
        )
        counterexample_case_count += len(unstable_negative_cases)
        if unstable_negative_cases:
            weighted_counterexample_dominates = True
        if any(
            result.scenario_class == "fresh_contradiction_invalidation"
            and result.preferred_family_reliability_delta > 0.0
            for result in host_negative_cases
        ):
            stale_prior_survives_contradiction = True
        host_local_branch_passed = (
            branch_host_local_case is not None
            and _positive_case_switch_or_margin(branch_host_local_case)
        )
        reference_projected_branch_passed = (
            branch_reference_projected_case is not None
            and _positive_case_switch_or_margin(branch_reference_projected_case)
        )
        if not host_local_branch_passed or not reference_projected_branch_passed:
            missing_branch_family_lift = True
        if not host_local_branch_passed and reference_projected_branch_passed:
            host_local_branch_basis_insufficient = True
        elif not host_local_branch_passed and not reference_projected_branch_passed:
            shared_branch_lift_insufficient = True
        if (
            check_case is None
            or not check_case.reliability_component_active
            or check_case.preferred_family_reliability_delta <= 0.0
        ):
            missing_reliability_active_check_lift = True
        if (
            len(host_positive_cases) == 4
            and len(host_negative_cases) == 2
            and positive_classes
            == {"retrieval_reuse", "branch_resume", "check_review"}
            and negative_classes
            == {"weighted_burden_counterexample", "fresh_contradiction_invalidation"}
            and improved_case_counts[host_name] == len(host_positive_cases)
            and negative_stable_counts[host_name] == len(host_negative_cases)
            and host_local_branch_passed
            and reference_projected_branch_passed
            and check_case is not None
            and check_case.reliability_component_active
            and check_case.preferred_family_reliability_delta > 0.0
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
    if weighted_counterexample_dominates:
        failure_counts["weighted_counterexample_dominates"] += 1
        failure_reasons.append(
            "the weighted burden counterexample improved or selected a reliability-weighted family"
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
    if missing_branch_family_lift:
        failure_counts["missing_branch_family_lift"] += 1
        failure_reasons.append(
            "at least one host failed to produce branch-family lift on the positive branch-resume comparisons"
        )
    if host_local_branch_basis_insufficient:
        failure_counts["host_local_branch_basis_insufficient"] += 1
        failure_reasons.append(
            "at least one host improved under reference-projected branch continuity but not under host-local continuity, so the blocker is a local continuity basis weakness rather than shared shadow law alone"
        )
    if shared_branch_lift_insufficient:
        failure_counts["shared_branch_lift_insufficient"] += 1
        failure_reasons.append(
            "at least one host failed branch-family lift under both host-local and reference-projected continuity bases, so the blocker remains a shared shadow insufficiency"
        )
    if missing_reliability_active_check_lift:
        failure_counts["missing_reliability_active_check_lift"] += 1
        failure_reasons.append(
            "at least one host failed to show a reliability-active positive check-review lift"
        )
    if host_aliasing_detected:
        failure_counts["host_aliasing_detected"] += 1
        failure_reasons.append(
            "claude and gemini still alias on the lawful host-signature projection, so only a shared documented non-reference shell claim is earned"
        )

    failure_labels = tuple(label for label in _FAILURE_LABEL_ORDER if failure_counts[label] > 0)
    acceptance_passed = not failure_labels
    claim_mode = (
        "full_cross_host"
        if acceptance_passed
        else "reference_plus_shared_non_reference_shell"
    )
    non_reference_evidence_mode = (
        "host_distinct"
        if (
            len(distinct_signature_classes) >= 2
            and "fresh_contradiction_invalidation" in distinct_signature_classes
            and any(
                scenario_class in distinct_signature_classes
                for scenario_class in ("retrieval_reuse", "branch_resume", "check_review")
            )
        )
        else "shared_shell"
    )
    dominant_failure_label = _choose_dominant_failure_label(
        failure_counts
    )

    return AuxCrossHostShadowEvaluationResult(
        case_results=case_results_tuple,
        per_host_positive_case_counts=_count_rows(positive_case_counts),
        per_host_improved_case_counts=_count_rows(improved_case_counts),
        per_host_negative_stable_counts=_count_rows(negative_stable_counts),
        repeat_stable_hosts=tuple(repeat_stable_hosts),
        counterexample_case_count=counterexample_case_count,
        acceptance_passed=acceptance_passed,
        claim_mode=claim_mode,
        non_reference_evidence_mode=non_reference_evidence_mode,
        distinct_signature_classes=distinct_signature_classes,
        host_aliasing_detected=host_aliasing_detected,
        dominant_failure_label=dominant_failure_label,
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
