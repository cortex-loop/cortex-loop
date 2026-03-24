"""Bounded event-to-state builder for the reference executive shell slice."""

from __future__ import annotations

from typing import Protocol

from cortex.core.environment import CAPABILITY_VIEW, EXECUTION_TRACE, ExecutiveEnvironmentView
from cortex.core.observation import ObservationBundle
from cortex.core.support import SupportSnapshot

from .brake import BrakeState, evaluate_brake_state
from .families import SoftControlFamily
from .goals import GoalContinuityView
from .state import (
    ReferenceBrakeView,
    ReferenceControlAllocationView,
    ReferenceExecutiveState,
    ReferenceModeAndGatingView,
    ReferenceUncertaintyMonitoringView,
)
from .uncertainty import UncertaintyEstimate


class PriorReferenceRuntimeSessionLike(Protocol):
    branch_registry: tuple[str, ...]
    active_track_ref: str
    pending_goal_refs: tuple[str, ...]
    budget_history: tuple[str, ...]
    brake_history: tuple[str, ...]
    last_selected_family: SoftControlFamily | None


def build_reference_executive_state(
    observation: ObservationBundle,
    support_snapshot: SupportSnapshot,
    executive_environment_view: ExecutiveEnvironmentView,
    prior_session: PriorReferenceRuntimeSessionLike | None = None,
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

    branch_registry = _branch_registry(support_snapshot, prior_session)
    pending_goal_refs = _pending_goal_refs(support_snapshot, prior_session)
    missing_resume_anchor = "resume-anchor-missing" in support_snapshot.session.reminders
    active_track_ref = _active_track_ref(branch_registry, prior_session)
    main_goal_ref = pending_goal_refs[0] if pending_goal_refs else None
    contradiction_spike_flags = _contradiction_spike_flags(support_snapshot, missing_resume_anchor)

    uncertainty_estimates = _uncertainty_estimates(
        native_event_name=observation.event.native_event_name,
        support_snapshot=support_snapshot,
        executive_environment_view=executive_environment_view,
        branch_registry=branch_registry,
        pending_goal_refs=pending_goal_refs,
        contradiction_spike_flags=contradiction_spike_flags,
    )
    brake_evaluation = evaluate_brake_state(
        uncertainty_estimates,
        repeated_degradations=len(support_snapshot.trace.degradation_records),
        missing_resume_anchor=missing_resume_anchor,
        host_friction_level=_host_friction_level(support_snapshot, executive_environment_view),
    )

    goal_continuity = GoalContinuityView(
        main_goal_ref=main_goal_ref,
        active_track_ref=active_track_ref,
        pending_goal_refs=pending_goal_refs,
        resume_anchor_available=(
            active_track_ref is not None
            and active_track_ref != "main"
            and not missing_resume_anchor
        ),
    )
    mode_and_gating = ReferenceModeAndGatingView(
        mode_tag=_mode_tag_for_event(observation.event.native_event_name, brake_evaluation.state),
        family_mask=_family_mask_for_state(branch_registry, brake_evaluation.state),
    )
    control_allocation = ReferenceControlAllocationView(
        budget_band=_budget_band_for_state(observation.event.native_event_name, prior_session),
        top_family_set=_top_family_set(
            native_event_name=observation.event.native_event_name,
            branch_registry=branch_registry,
            brake_state=brake_evaluation.state,
        ),
        host_friction_tags=_host_friction_tags(support_snapshot, executive_environment_view),
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


def _contradiction_spike_flags(
    support_snapshot: SupportSnapshot,
    missing_resume_anchor: bool,
) -> frozenset[str]:
    flags: set[str] = set()
    for degradation_record in support_snapshot.trace.degradation_records:
        flags.add(degradation_record.reason_code)
        for contradiction_record in degradation_record.contradiction_records:
            flags.add(contradiction_record.source_tag)
    if missing_resume_anchor:
        flags.add("resume-anchor-missing")
    return frozenset(flags)


def _uncertainty_estimates(
    *,
    native_event_name: str,
    support_snapshot: SupportSnapshot,
    executive_environment_view: ExecutiveEnvironmentView,
    branch_registry: tuple[str, ...],
    pending_goal_refs: tuple[str, ...],
    contradiction_spike_flags: frozenset[str],
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


def _host_friction_level(
    support_snapshot: SupportSnapshot,
    executive_environment_view: ExecutiveEnvironmentView,
) -> float:
    if support_snapshot.host.constraint_tags:
        return 0.65
    if CAPABILITY_VIEW not in executive_environment_view.available_query_kinds:
        return 0.6
    return 0.0


def _mode_tag_for_event(native_event_name: str, brake_state: BrakeState) -> str:
    if brake_state is BrakeState.LATCHED:
        return "latched_review"
    if brake_state is BrakeState.GUARDED:
        return "guarded_review"
    if native_event_name == "approval/request":
        return "review_pending"
    if native_event_name == "approval/result":
        return "commitment_path"
    return "pass_through"


def _family_mask_for_state(
    branch_registry: tuple[str, ...],
    brake_state: BrakeState,
) -> frozenset[SoftControlFamily]:
    families = {
        SoftControlFamily.NEUTRAL,
        SoftControlFamily.CHECK,
    }
    if any(branch_ref != "main" for branch_ref in branch_registry):
        families.add(SoftControlFamily.BRANCH)
    if brake_state is not BrakeState.QUIESCENT:
        families.add(SoftControlFamily.BRAKE)
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
) -> frozenset[SoftControlFamily]:
    families = {SoftControlFamily.NEUTRAL}
    if native_event_name == "approval/request":
        families.add(SoftControlFamily.CHECK)
    if any(branch_ref != "main" for branch_ref in branch_registry):
        families.add(SoftControlFamily.BRANCH)
    if brake_state is not BrakeState.QUIESCENT:
        families.add(SoftControlFamily.BRAKE)
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


def _event_base_uncertainty(native_event_name: str) -> float:
    if native_event_name == "approval/request":
        return 0.45
    if native_event_name == "approval/result":
        return 0.25
    return 0.15


__all__ = ["PriorReferenceRuntimeSessionLike", "build_reference_executive_state"]
