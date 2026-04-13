"""Bounded event-to-state builder for the reference executive shell slice."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from cortex.core.environment import CAPABILITY_VIEW, EXECUTION_TRACE, ExecutiveEnvironmentView
from cortex.core.observation import ObservationBundle
from cortex.core.support import SupportSnapshot

from .brake import BrakeState, evaluate_brake_state
from .feedback import (
    ReferenceFeedbackWindowSummary,
    ReferenceRealizationFeedbackWindow,
    summarize_reference_feedback_window,
)
from .families import SoftControlFamily
from .goals import GoalContinuityView, parse_resume_reminder_track
from .opportunities import HostNativeOpportunity, PROBE_FAILURE_CLASSES
from .state import (
    ReferenceBrakeView,
    ReferenceControlAllocationView,
    ReferenceExecutiveState,
    ReferenceModeAndGatingView,
    ReferenceUncertaintyMonitoringView,
)
from .uncertainty import UncertaintyEstimate

_SEEK_CONTEXT_PRESSURE_TAGS = frozenset(
    {
        "missing-capability",
        "capability-view-missing",
        "execution-trace-missing",
    }
)
_CONTINUITY_RELIEF_HOST_FRICTION_TAGS = frozenset(
    {"capability-view-missing", "execution-trace-missing", "runtime-warning"}
)


class PriorReferenceRuntimeSessionLike(Protocol):
    branch_registry: tuple[str, ...]
    active_track_ref: str
    pending_goal_refs: tuple[str, ...]
    continuity_reminders: tuple[str, ...]
    budget_history: tuple[str, ...]
    brake_history: tuple[str, ...]
    last_selected_family: SoftControlFamily | None
    feedback_window: ReferenceRealizationFeedbackWindow


def build_reference_executive_state(
    observation: ObservationBundle,
    support_snapshot: SupportSnapshot,
    executive_environment_view: ExecutiveEnvironmentView,
    prior_session: PriorReferenceRuntimeSessionLike | None = None,
    opportunities: Sequence[HostNativeOpportunity] = (),
    audit_intensity: str = "minimal",
) -> ReferenceExecutiveState:
    if not isinstance(observation, ObservationBundle):
        actual_type = type(observation).__name__
        raise TypeError(
            "build_reference_executive_state.observation must be ObservationBundle, "
            f"got {actual_type}."
        )
    if not isinstance(support_snapshot, SupportSnapshot):
        actual_type = type(support_snapshot).__name__
        raise TypeError(
            "build_reference_executive_state.support_snapshot must be SupportSnapshot, "
            f"got {actual_type}."
        )
    if not isinstance(executive_environment_view, ExecutiveEnvironmentView):
        actual_type = type(executive_environment_view).__name__
        raise TypeError(
            "build_reference_executive_state.executive_environment_view must be "
            f"ExecutiveEnvironmentView, got {actual_type}."
        )
    if audit_intensity not in {"minimal", "focused", "structured"}:
        raise ValueError(
            "build_reference_executive_state.audit_intensity must be one of "
            "['minimal', 'focused', 'structured']."
        )

    branch_registry = _branch_registry(support_snapshot, prior_session)
    pending_goal_refs = _pending_goal_refs(support_snapshot, prior_session)
    missing_resume_anchor = "resume-anchor-missing" in support_snapshot.session.reminders
    active_track_ref = _active_track_ref(branch_registry, prior_session)
    main_goal_ref = pending_goal_refs[0] if pending_goal_refs else None
    prior_feedback_window_summary = _prior_feedback_window_summary(prior_session)
    prior_brake_state = _prior_brake_state(prior_session)
    recent_probe_result_class = _recent_probe_result_class(prior_session)
    contradiction_spike_flags = _contradiction_spike_flags(
        support_snapshot,
        missing_resume_anchor,
        prior_feedback_window_summary.sustained_spike_flags,
    )
    anchor_source, anchor_freshness, branch_intent_present = _continuity_signals(
        support_snapshot=support_snapshot,
        active_track_ref=active_track_ref,
        pending_goal_refs=pending_goal_refs,
        missing_resume_anchor=missing_resume_anchor,
        prior_feedback_window_summary=prior_feedback_window_summary,
    )
    goal_continuity = GoalContinuityView(
        main_goal_ref=main_goal_ref,
        active_track_ref=active_track_ref,
        pending_goal_refs=pending_goal_refs,
        resume_anchor_available=(
            active_track_ref is not None
            and active_track_ref != "main"
            and branch_intent_present
            and anchor_freshness != "absent"
        ),
        anchor_source=anchor_source,
        anchor_freshness=anchor_freshness,
        branch_intent_present=branch_intent_present,
        open_branch_count=_open_branch_count(branch_registry),
        resume_anchor_quality=_resume_anchor_quality(
            active_track_ref=active_track_ref,
            anchor_source=anchor_source,
            anchor_freshness=anchor_freshness,
            branch_intent_present=branch_intent_present,
            prior_feedback_window_summary=prior_feedback_window_summary,
        ),
        merge_confidence=_merge_confidence(
            active_track_ref=active_track_ref,
            anchor_source=anchor_source,
            anchor_freshness=anchor_freshness,
            branch_intent_present=branch_intent_present,
            prior_feedback_window_summary=prior_feedback_window_summary,
        ),
    )
    probe_path_state = _probe_path_state(opportunities)
    probe_backed_families = _probe_backed_families(opportunities)
    host_friction_tags = _host_friction_tags(support_snapshot, executive_environment_view)

    uncertainty_estimates = _uncertainty_estimates(
        native_event_name=observation.event.native_event_name,
        support_snapshot=support_snapshot,
        executive_environment_view=executive_environment_view,
        branch_registry=branch_registry,
        pending_goal_refs=pending_goal_refs,
        contradiction_spike_flags=contradiction_spike_flags,
        goal_progress_floor=prior_feedback_window_summary.goal_progress_floor,
    )
    brake_evaluation = evaluate_brake_state(
        uncertainty_estimates,
        repeated_degradations=(
            len(support_snapshot.trace.degradation_records)
            + prior_feedback_window_summary.degradation_pressure_bonus
        ),
        missing_resume_anchor=missing_resume_anchor,
        host_friction_level=_host_friction_level(
            support_snapshot,
            executive_environment_view,
            goal_continuity=goal_continuity,
            host_friction_tags=host_friction_tags,
            probe_path_state=_probe_path_state(opportunities),
            recent_probe_result_class=recent_probe_result_class,
        ),
        prior_state=prior_brake_state,
    )
    host_friction_level = _host_friction_level(
        support_snapshot,
        executive_environment_view,
        goal_continuity=goal_continuity,
        host_friction_tags=host_friction_tags,
        probe_path_state=probe_path_state,
        recent_probe_result_class=recent_probe_result_class,
    )
    explainability_profile = _resolve_explainability_profile(
        brake_state=brake_evaluation.state,
        uncertainty_estimates=uncertainty_estimates,
        recent_probe_result_class=recent_probe_result_class,
        requested_audit_intensity=audit_intensity,
    )
    mode_and_gating = ReferenceModeAndGatingView(
        mode_tag=_mode_tag_for_event(
            observation.event.native_event_name,
            brake_evaluation.state,
            goal_continuity,
        ),
        family_mask=_family_mask_for_state(
            branch_registry,
            brake_evaluation.state,
            host_friction_tags,
            uncertainty_estimates,
            goal_continuity=goal_continuity,
            probe_backed_families=probe_backed_families,
        ),
    )
    control_allocation = ReferenceControlAllocationView(
        budget_band=_budget_band_for_state(observation.event.native_event_name, prior_session),
        top_family_set=_top_family_set(
            native_event_name=observation.event.native_event_name,
            branch_registry=branch_registry,
            brake_state=brake_evaluation.state,
            host_friction_tags=host_friction_tags,
            uncertainty_estimates=uncertainty_estimates,
            goal_continuity=goal_continuity,
            probe_backed_families=probe_backed_families,
        ),
        host_friction_tags=host_friction_tags,
        feedback_pressure_tags=_feedback_pressure_tags(
            prior_feedback_window_summary,
            recent_probe_result_class=recent_probe_result_class,
        ),
        probe_backed_families=probe_backed_families,
        productive_exploration_bonus=_productive_exploration_bonus(
            prior_feedback_window_summary
        ),
        oscillation_penalty=_oscillation_penalty(prior_feedback_window_summary),
        host_friction_level=host_friction_level,
        visible_burden_scale=_visible_burden_scale(explainability_profile),
        explainability_profile=explainability_profile,
        probe_path_state=probe_path_state,
        probe_unavailable_reason=_probe_unavailable_reason(opportunities, probe_path_state),
        recent_probe_result_class=recent_probe_result_class,
    )
    brake_view = ReferenceBrakeView(
        brake_state=brake_evaluation.state,
        dominant_cause_family=(
            SoftControlFamily.BRAKE
            if brake_evaluation.state is not BrakeState.QUIESCENT
            else None
        ),
    )
    return ReferenceExecutiveState(
        goal_continuity=goal_continuity,
        uncertainty_monitoring=ReferenceUncertaintyMonitoringView(
            classwise_uncertainty=uncertainty_estimates,
            contradiction_spike_flags=contradiction_spike_flags,
        ),
        mode_and_gating=mode_and_gating,
        control_allocation=control_allocation,
        brake=brake_view,
    )


def _branch_registry(
    support_snapshot: SupportSnapshot,
    prior_session: PriorReferenceRuntimeSessionLike | None,
) -> tuple[str, ...]:
    session_branches = tuple(support_snapshot.session.branch_registry)
    if session_branches:
        return session_branches
    if prior_session is None:
        return ("main",)
    return tuple(prior_session.branch_registry) or ("main",)


def _pending_goal_refs(
    support_snapshot: SupportSnapshot,
    prior_session: PriorReferenceRuntimeSessionLike | None,
) -> tuple[str, ...]:
    ordered_refs: list[str] = []
    for goal_ref in support_snapshot.session.pending_goal_refs:
        if goal_ref not in ordered_refs:
            ordered_refs.append(goal_ref)
    if prior_session is not None:
        for goal_ref in prior_session.pending_goal_refs:
            if goal_ref not in ordered_refs:
                ordered_refs.append(goal_ref)
    return tuple(ordered_refs)


def _active_track_ref(
    branch_registry: tuple[str, ...],
    prior_session: PriorReferenceRuntimeSessionLike | None,
) -> str:
    if prior_session is not None:
        if prior_session.active_track_ref == "main":
            return "main"
        if prior_session.active_track_ref in branch_registry:
            return prior_session.active_track_ref
    for branch_ref in reversed(branch_registry):
        if branch_ref != "main":
            return branch_ref
    return "main"


def _open_branch_count(branch_registry: tuple[str, ...]) -> int:
    return sum(1 for branch_ref in branch_registry if branch_ref != "main")


def _continuity_signals(
    *,
    support_snapshot: SupportSnapshot,
    active_track_ref: str,
    pending_goal_refs: tuple[str, ...],
    missing_resume_anchor: bool,
    prior_feedback_window_summary: ReferenceFeedbackWindowSummary,
) -> tuple[str, str, bool]:
    if active_track_ref in (None, "main"):
        return "none", "absent", False

    reminder_track_refs = _resume_reminder_track_refs(support_snapshot.session.reminders)
    wake_receipt_resume_present = any(
        receipt.reason_tag.startswith("resume")
        for receipt in support_snapshot.trace.wake_receipts
    )
    branch_intent_present = (
        active_track_ref in pending_goal_refs
        or bool(pending_goal_refs)
        or active_track_ref in reminder_track_refs
        or (bool(reminder_track_refs) and len(reminder_track_refs) == 1)
        or wake_receipt_resume_present
    )

    anchor_source = "branch_registry_only"
    if active_track_ref in pending_goal_refs:
        anchor_source = "pending_goal"
    elif active_track_ref in reminder_track_refs or (
        reminder_track_refs and len(reminder_track_refs) == 1
    ):
        anchor_source = "continuity_reminder"
    elif wake_receipt_resume_present:
        anchor_source = "trace_wake"

    if missing_resume_anchor:
        anchor_freshness = "stale"
    elif anchor_source in {"pending_goal", "continuity_reminder", "trace_wake"}:
        anchor_freshness = "fresh"
    else:
        anchor_freshness = "stale" if branch_intent_present else "absent"

    if (
        anchor_freshness == "fresh"
        and "prior-continuity-rejection" in prior_feedback_window_summary.sustained_spike_flags
    ):
        anchor_freshness = "stale"

    if not branch_intent_present:
        return "none", "absent", False
    return anchor_source, anchor_freshness, True


def _resume_reminder_track_refs(reminders: tuple[str, ...]) -> frozenset[str]:
    track_refs = {
        track_ref
        for reminder in reminders
        if (track_ref := parse_resume_reminder_track(reminder)) is not None
    }
    return frozenset(track_refs)


def _contradiction_spike_flags(
    support_snapshot: SupportSnapshot,
    missing_resume_anchor: bool,
    prior_feedback_spike_flags: frozenset[str],
) -> frozenset[str]:
    flags: set[str] = set()
    for degradation_record in support_snapshot.trace.degradation_records:
        flags.add(degradation_record.reason_code)
        for contradiction_record in degradation_record.contradiction_records:
            flags.add(contradiction_record.source_tag)
    if missing_resume_anchor:
        flags.add("resume-anchor-missing")
    flags.update(prior_feedback_spike_flags)
    return frozenset(flags)


def _uncertainty_estimates(
    *,
    native_event_name: str,
    support_snapshot: SupportSnapshot,
    executive_environment_view: ExecutiveEnvironmentView,
    branch_registry: tuple[str, ...],
    pending_goal_refs: tuple[str, ...],
    contradiction_spike_flags: frozenset[str],
    goal_progress_floor: float,
) -> tuple[UncertaintyEstimate, ...]:
    event_base = _event_base_uncertainty(native_event_name)
    degradation_spikes = frozenset(
        record.reason_code for record in support_snapshot.trace.degradation_records
    )
    evidence_level = event_base
    environment_level = 0.2
    host_capability_level = 0.2
    goal_progress_level = 0.2

    if support_snapshot.trace.degradation_records:
        environment_level = max(environment_level, 0.6)
    if EXECUTION_TRACE not in executive_environment_view.available_query_kinds:
        environment_level = max(environment_level, 0.45)
    if support_snapshot.host.constraint_tags:
        host_capability_level = max(host_capability_level, 0.55)
    if CAPABILITY_VIEW not in executive_environment_view.available_query_kinds:
        host_capability_level = max(host_capability_level, 0.55)
    if pending_goal_refs:
        goal_progress_level = max(goal_progress_level, 0.35)
    if any(branch_ref != "main" for branch_ref in branch_registry):
        goal_progress_level = max(goal_progress_level, 0.55)
    goal_progress_level = max(goal_progress_level, goal_progress_floor)

    return (
        UncertaintyEstimate(
            class_tag="evidence",
            level=evidence_level,
            source_tags=frozenset({native_event_name}),
        ),
        UncertaintyEstimate(
            class_tag="environment",
            level=environment_level,
            source_tags=frozenset({"support-snapshot"}),
            spike_tags=degradation_spikes,
        ),
        UncertaintyEstimate(
            class_tag="host-capability",
            level=host_capability_level,
            source_tags=frozenset({"executive-environment-view"}),
        ),
        UncertaintyEstimate(
            class_tag="goal-progress",
            level=goal_progress_level,
            source_tags=frozenset({"goal-continuity"}),
            spike_tags=contradiction_spike_flags,
        ),
    )


def _prior_feedback_window_summary(
    prior_session: PriorReferenceRuntimeSessionLike | None,
) -> ReferenceFeedbackWindowSummary:
    if prior_session is None:
        return ReferenceFeedbackWindowSummary()
    return summarize_reference_feedback_window(prior_session.feedback_window)


def _host_friction_level(
    support_snapshot: SupportSnapshot,
    executive_environment_view: ExecutiveEnvironmentView,
    *,
    goal_continuity: GoalContinuityView,
    host_friction_tags: frozenset[str],
    probe_path_state: str,
    recent_probe_result_class: str | None = None,
) -> float:
    heuristic_level = 0.0
    if support_snapshot.host.constraint_tags:
        heuristic_level = max(heuristic_level, 0.65)
    if CAPABILITY_VIEW not in executive_environment_view.available_query_kinds:
        heuristic_level = max(heuristic_level, 0.6)
    if EXECUTION_TRACE not in executive_environment_view.available_query_kinds:
        heuristic_level = max(heuristic_level, 0.45)
    if recent_probe_result_class == "succeeded":
        return min(heuristic_level, 0.2) if heuristic_level > 0.0 else 0.1
    if recent_probe_result_class == "timed-out":
        return max(heuristic_level, 0.8)
    if recent_probe_result_class in {"degraded", "unsupported"}:
        return max(heuristic_level, 0.65)
    if (
        _continuity_relief_active(goal_continuity)
        and not support_snapshot.host.constraint_tags
        and recent_probe_result_class is None
        and probe_path_state == "unavailable"
        and host_friction_tags <= _CONTINUITY_RELIEF_HOST_FRICTION_TAGS
    ):
        return 0.0
    if probe_path_state == "available":
        return 0.0
    return heuristic_level


def _mode_tag_for_event(
    native_event_name: str,
    brake_state: BrakeState,
    goal_continuity: GoalContinuityView,
) -> str:
    if brake_state is BrakeState.LATCHED:
        return "latched_review"
    if native_event_name == "approval/request":
        return "review_pending"
    if native_event_name == "approval/result":
        return "commitment_path"
    if _continuity_relief_active(goal_continuity):
        return "review_pending"
    if brake_state is BrakeState.GUARDED:
        return "guarded_review"
    return "pass_through"


def _family_mask_for_state(
    branch_registry: tuple[str, ...],
    brake_state: BrakeState,
    host_friction_tags: frozenset[str],
    uncertainty_estimates: tuple[UncertaintyEstimate, ...],
    *,
    goal_continuity: GoalContinuityView,
    probe_backed_families: frozenset[SoftControlFamily],
) -> frozenset[SoftControlFamily]:
    families = {
        SoftControlFamily.NEUTRAL,
        SoftControlFamily.CHECK,
    }
    if any(branch_ref != "main" for branch_ref in branch_registry):
        families.add(SoftControlFamily.BRANCH)
        families.add(SoftControlFamily.REDIRECT)
    if brake_state is not BrakeState.QUIESCENT:
        families.add(SoftControlFamily.BRAKE)
    if _has_seek_context_pressure(
        host_friction_tags,
        uncertainty_estimates=uncertainty_estimates,
        brake_state=brake_state,
        goal_continuity=goal_continuity,
        probe_backed_families=probe_backed_families,
    ):
        families.add(SoftControlFamily.SEEK_CONTEXT)
    return frozenset(families)


def _budget_band_for_state(
    native_event_name: str,
    prior_session: PriorReferenceRuntimeSessionLike | None,
) -> str:
    if prior_session is not None and prior_session.budget_history:
        return prior_session.budget_history[-1].replace("shell-", "", 1)
    if native_event_name == "approval/result":
        return "high"
    if native_event_name == "approval/request":
        return "medium"
    return "low"


def _top_family_set(
    *,
    native_event_name: str,
    branch_registry: tuple[str, ...],
    brake_state: BrakeState,
    host_friction_tags: frozenset[str],
    uncertainty_estimates: tuple[UncertaintyEstimate, ...],
    goal_continuity: GoalContinuityView,
    probe_backed_families: frozenset[SoftControlFamily],
) -> frozenset[SoftControlFamily]:
    families = {SoftControlFamily.NEUTRAL}
    if native_event_name == "approval/request":
        families.add(SoftControlFamily.CHECK)
    if any(branch_ref != "main" for branch_ref in branch_registry):
        families.add(SoftControlFamily.BRANCH)
    if _stale_anchor_redirect(goal_continuity):
        families.add(SoftControlFamily.REDIRECT)
        families.add(SoftControlFamily.CHECK)
    if brake_state is not BrakeState.QUIESCENT:
        families.add(SoftControlFamily.BRAKE)
    if _has_seek_context_pressure(
        host_friction_tags,
        uncertainty_estimates=uncertainty_estimates,
        brake_state=brake_state,
        goal_continuity=goal_continuity,
        probe_backed_families=probe_backed_families,
    ):
        families.add(SoftControlFamily.SEEK_CONTEXT)
    return frozenset(families)


def _host_friction_tags(
    support_snapshot: SupportSnapshot,
    executive_environment_view: ExecutiveEnvironmentView,
) -> frozenset[str]:
    tags = set(support_snapshot.host.constraint_tags)
    if support_snapshot.host.approval_boundary_tags:
        tags.add("approval-boundary-present")
    if CAPABILITY_VIEW not in executive_environment_view.available_query_kinds:
        tags.add("capability-view-missing")
    if EXECUTION_TRACE not in executive_environment_view.available_query_kinds:
        tags.add("execution-trace-missing")
    return frozenset(tags)


def _has_seek_context_pressure(
    host_friction_tags: frozenset[str],
    *,
    uncertainty_estimates: tuple[UncertaintyEstimate, ...],
    brake_state: BrakeState,
    goal_continuity: GoalContinuityView,
    probe_backed_families: frozenset[SoftControlFamily],
) -> bool:
    if (
        _continuity_relief_active(goal_continuity)
        and host_friction_tags
        and host_friction_tags <= _CONTINUITY_RELIEF_HOST_FRICTION_TAGS
    ):
        return False
    if (
        SoftControlFamily.SEEK_CONTEXT in probe_backed_families
        and any(
            estimate.class_tag in {"environment", "host-capability"}
            and estimate.level >= 0.45
            for estimate in uncertainty_estimates
        )
    ):
        return True
    if not any(tag in _SEEK_CONTEXT_PRESSURE_TAGS for tag in host_friction_tags):
        return False
    if brake_state is not BrakeState.LATCHED:
        return True
    return _allow_latched_seek_context_relief(uncertainty_estimates)


def _continuity_relief_active(goal_continuity: GoalContinuityView) -> bool:
    return (
        goal_continuity.active_track_ref not in (None, "main")
        and goal_continuity.branch_intent_present
        and goal_continuity.anchor_freshness == "fresh"
        and goal_continuity.resume_anchor_quality >= 0.7
    )


def _stale_anchor_redirect(goal_continuity: GoalContinuityView) -> bool:
    return (
        goal_continuity.active_track_ref not in (None, "main")
        and (
            not goal_continuity.branch_intent_present
            or goal_continuity.anchor_freshness == "stale"
        )
    )


def _allow_latched_seek_context_relief(
    uncertainty_estimates: tuple[UncertaintyEstimate, ...],
) -> bool:
    dominant_classes = tuple(
        estimate.class_tag
        for estimate in sorted(
            uncertainty_estimates,
            key=lambda estimate: (-estimate.level, estimate.class_tag),
        )[:2]
    )
    return any(
        class_tag in {"evidence", "environment", "host-capability"}
        for class_tag in dominant_classes
    )


def _feedback_pressure_tags(
    prior_feedback_window_summary: ReferenceFeedbackWindowSummary,
    *,
    recent_probe_result_class: str | None,
) -> frozenset[str]:
    tags: set[str] = set()
    if prior_feedback_window_summary.rejection_count >= 1:
        tags.add("feedback:rejection-pressure")
    if prior_feedback_window_summary.override_count >= 1:
        tags.add("feedback:override-pressure")
    if prior_feedback_window_summary.latched_count >= 1:
        tags.add("feedback:latched-history")
    if prior_feedback_window_summary.degradation_pressure_bonus >= 1:
        tags.add("feedback:degradation-pressure")
    if prior_feedback_window_summary.family_change_without_evidence_count >= 1:
        tags.add("feedback:oscillation-pressure")
    if (
        prior_feedback_window_summary.evidence_state_move_count >= 1
        or prior_feedback_window_summary.continuity_improvement_count >= 1
    ):
        tags.add("feedback:productive-exploration")
    if recent_probe_result_class in PROBE_FAILURE_CLASSES:
        tags.add("feedback:probe-friction")
    if recent_probe_result_class == "succeeded":
        tags.add("feedback:probe-success")
    return frozenset(tags)


def _prior_brake_state(
    prior_session: PriorReferenceRuntimeSessionLike | None,
) -> BrakeState | None:
    if prior_session is None or not prior_session.brake_history:
        return None
    return BrakeState(prior_session.brake_history[-1])


def _recent_probe_result_class(
    prior_session: PriorReferenceRuntimeSessionLike | None,
) -> str | None:
    if prior_session is None:
        return None
    for feedback in reversed(prior_session.feedback_window.entries):
        if feedback.probe_result_class is not None:
            return feedback.probe_result_class
    return None


def _probe_backed_families(
    opportunities: Sequence[HostNativeOpportunity],
) -> frozenset[SoftControlFamily]:
    return frozenset(
        opportunity.probe_contract.allowed_family
        for opportunity in opportunities
        if opportunity.realizable and opportunity.probe_contract is not None
    )


def _probe_path_state(
    opportunities: Sequence[HostNativeOpportunity],
) -> str:
    has_relevant_probe = any(
        opportunity.probe_contract is not None for opportunity in opportunities
    )
    if not has_relevant_probe:
        return "absent"
    if any(
        opportunity.probe_contract is not None and opportunity.realizable
        for opportunity in opportunities
    ):
        return "available"
    return "unavailable"


def _probe_unavailable_reason(
    opportunities: Sequence[HostNativeOpportunity],
    probe_path_state: str,
) -> str | None:
    if probe_path_state != "unavailable":
        return None
    for opportunity in opportunities:
        if (
            opportunity.probe_contract is not None
            and not opportunity.realizable
            and opportunity.degradation_reason is not None
        ):
            return opportunity.degradation_reason
    return None


def _explainability_profile(
    *,
    brake_state: BrakeState,
    uncertainty_estimates: tuple[UncertaintyEstimate, ...],
    recent_probe_result_class: str | None,
) -> str:
    max_uncertainty = max(
        (estimate.level for estimate in uncertainty_estimates),
        default=0.0,
    )
    if (
        brake_state is BrakeState.LATCHED
        or max_uncertainty >= 0.75
        or recent_probe_result_class in PROBE_FAILURE_CLASSES
    ):
        return "structured"
    if brake_state is BrakeState.GUARDED or max_uncertainty >= 0.55:
        return "focused"
    return "minimal"


def _resolve_explainability_profile(
    *,
    brake_state: BrakeState,
    uncertainty_estimates: tuple[UncertaintyEstimate, ...],
    recent_probe_result_class: str | None,
    requested_audit_intensity: str,
) -> str:
    automatic_profile = _explainability_profile(
        brake_state=brake_state,
        uncertainty_estimates=uncertainty_estimates,
        recent_probe_result_class=recent_probe_result_class,
    )
    order = {"minimal": 0, "focused": 1, "structured": 2}
    return max(
        (automatic_profile, requested_audit_intensity),
        key=lambda profile: order[profile],
    )


def _visible_burden_scale(profile: str) -> float:
    if profile == "structured":
        return 0.35
    if profile == "focused":
        return 0.65
    return 1.0


def _productive_exploration_bonus(
    prior_feedback_window_summary: ReferenceFeedbackWindowSummary,
) -> float:
    bonus = 0.0
    bonus += min(0.08, 0.04 * prior_feedback_window_summary.evidence_state_move_count)
    bonus += min(0.08, 0.04 * prior_feedback_window_summary.continuity_improvement_count)
    if prior_feedback_window_summary.clean_success_streak >= 2:
        bonus += 0.02
    return min(0.12, bonus)


def _oscillation_penalty(
    prior_feedback_window_summary: ReferenceFeedbackWindowSummary,
) -> float:
    penalty = min(
        0.18,
        0.07 * prior_feedback_window_summary.family_change_without_evidence_count,
    )
    if prior_feedback_window_summary.override_count >= 2:
        penalty += 0.04
    return min(0.20, penalty)


def _resume_anchor_quality(
    *,
    active_track_ref: str,
    anchor_source: str,
    anchor_freshness: str,
    branch_intent_present: bool,
    prior_feedback_window_summary: ReferenceFeedbackWindowSummary,
) -> float:
    if active_track_ref in (None, "main"):
        return 0.0
    quality = {
        "fresh": 0.82,
        "stale": 0.45,
        "absent": 0.20,
    }[anchor_freshness]
    quality += {
        "pending_goal": 0.05,
        "continuity_reminder": 0.04,
        "trace_wake": 0.02,
        "branch_registry_only": -0.05,
        "none": -0.10,
    }[anchor_source]
    if branch_intent_present and anchor_freshness != "absent":
        quality += 0.03
    if prior_feedback_window_summary.rejection_count >= 1:
        quality -= 0.10
    if "prior-continuity-rejection" in prior_feedback_window_summary.sustained_spike_flags:
        quality -= 0.15
    return max(0.0, min(1.0, quality))


def _merge_confidence(
    *,
    active_track_ref: str,
    anchor_source: str,
    anchor_freshness: str,
    branch_intent_present: bool,
    prior_feedback_window_summary: ReferenceFeedbackWindowSummary,
) -> float:
    if active_track_ref in (None, "main"):
        return 0.0
    confidence = {
        "fresh": 0.70,
        "stale": 0.42,
        "absent": 0.18,
    }[anchor_freshness]
    confidence += {
        "pending_goal": 0.04,
        "continuity_reminder": 0.03,
        "trace_wake": 0.02,
        "branch_registry_only": -0.04,
        "none": -0.08,
    }[anchor_source]
    if branch_intent_present and anchor_freshness != "absent":
        confidence += 0.02
    if prior_feedback_window_summary.override_count >= 1:
        confidence -= 0.10
    if "prior-continuity-rejection" in prior_feedback_window_summary.sustained_spike_flags:
        confidence -= 0.15
    if prior_feedback_window_summary.continuity_improvement_count >= 1:
        confidence += 0.05
    return max(0.0, min(1.0, confidence))


def _event_base_uncertainty(native_event_name: str) -> float:
    if native_event_name == "approval/request":
        return 0.45
    if native_event_name == "approval/result":
        return 0.25
    return 0.15


__all__ = ["PriorReferenceRuntimeSessionLike", "build_reference_executive_state"]
