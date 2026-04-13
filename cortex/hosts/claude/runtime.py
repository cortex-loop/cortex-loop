"""Claude documented host-event runtime shell over landed driver/core/SRE surfaces."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from cortex.core.certification import certify_commitment
from cortex.core.commitments import (
    BoundaryAssessment,
    CertificationContext,
    CommitmentStatus,
    ProvenanceManifest,
)
from cortex.core.dispatch import DispatchDecision, DispatchLane, classify_dispatch
from cortex.core.environment import (
    EXECUTION_TRACE,
    EXTERNAL_RECORD,
    RESULT_ARTIFACT,
    CommitmentEnvironmentHandle,
    ExecutiveEnvironmentView,
)
from cortex.core.support import (
    SupportExecMemoryState,
    SupportHostState,
    SupportSessionState,
    SupportSnapshot,
    SupportTraceState,
)
from cortex.drivers._commitment_common import (
    extract_native_commitment_fields,
    merge_warnings,
    resolve_commitment_extract_for_dispatch,
)
from cortex.drivers.claude_host import (
    BoundClaudeHostEvent,
    is_raw_claude_host_event_name,
    observe_claude_host_event,
)
from cortex.drivers.claude_host_commitment import bind_claude_host_candidate
from cortex.hosts._executive_closure import (
    build_runtime_executive_signal_summary_inputs,
    canonicalize_executive_modulator_memory,
    closure_reason_tags,
    recent_warning_bearing_success_present,
)
from cortex.sre.allocation import build_allocation_diagnostics_payload
from cortex.sre.branching import BranchOperation
from cortex.sre.brake import BrakeState
from cortex.sre.executive_summary import (
    ExecutiveSignalSummary,
    build_executive_signal_summary,
)
from cortex.sre.families import SoftControlFamily
from cortex.sre.feedback import (
    ReferenceFeedbackWindowSummary,
    ReferenceRealizationFeedback,
    ReferenceRealizationFeedbackWindow,
    summarize_reference_feedback_window,
)
from cortex.sre.modulators import (
    ExecutiveModulatorMemory,
    ExecutiveModulatorState,
    update_executive_modulators,
)
from cortex.sre.policy_view import ExecutivePolicyView, build_executive_policy_view
from cortex.sre.reference_builder import build_reference_executive_state
from cortex.sre.reference_scoring import select_reference_soft_control
from cortex.sre.state import ReferenceExecutiveState

_ALLOWED_COMMITMENT_RESULT_KINDS = frozenset(status.value for status in CommitmentStatus)


@dataclass(frozen=True, slots=True)
class ClaudeRuntimeSession:
    session_id: str | None = None
    event_index: int = 0
    branch_registry: tuple[str, ...] = ("main",)
    active_track_ref: str = "main"
    pending_goal_refs: tuple[str, ...] = ()
    budget_history: tuple[str, ...] = ()
    brake_history: tuple[str, ...] = ()
    last_selected_family: SoftControlFamily | None = None
    last_commitment_result_summary: str | None = None
    last_realization_feedback: ReferenceRealizationFeedback | None = None
    feedback_window: ReferenceRealizationFeedbackWindow = field(
        default_factory=ReferenceRealizationFeedbackWindow
    )
    executive_modulator_memory: ExecutiveModulatorMemory | None = None

    def __post_init__(self) -> None:
        if self.session_id is not None and not (
            isinstance(self.session_id, str) and self.session_id.strip()
        ):
            raise ValueError(
                "ClaudeRuntimeSession.session_id must be non-empty after trimming when provided."
            )
        if isinstance(self.event_index, bool) or not isinstance(self.event_index, int):
            actual_type = type(self.event_index).__name__
            raise TypeError(
                "ClaudeRuntimeSession.event_index must be a non-negative integer, "
                f"got {actual_type}."
            )
        if self.event_index < 0:
            raise ValueError("ClaudeRuntimeSession.event_index must be non-negative.")
        if any(not (isinstance(ref, str) and ref.strip()) for ref in self.branch_registry):
            raise ValueError(
                "ClaudeRuntimeSession.branch_registry must contain only non-empty values after trimming."
            )
        if not (isinstance(self.active_track_ref, str) and self.active_track_ref.strip()):
            raise ValueError(
                "ClaudeRuntimeSession.active_track_ref must be non-empty after trimming."
            )
        if self.active_track_ref != "main" and self.active_track_ref not in self.branch_registry:
            raise ValueError(
                "ClaudeRuntimeSession.active_track_ref must be `main` or a member of branch_registry."
            )
        if any(not (isinstance(ref, str) and ref.strip()) for ref in self.pending_goal_refs):
            raise ValueError(
                "ClaudeRuntimeSession.pending_goal_refs must contain only non-empty values after trimming."
            )
        if any(not (isinstance(entry, str) and entry.strip()) for entry in self.budget_history):
            raise ValueError(
                "ClaudeRuntimeSession.budget_history must contain only non-empty values after trimming."
            )
        if any(not (isinstance(entry, str) and entry.strip()) for entry in self.brake_history):
            raise ValueError(
                "ClaudeRuntimeSession.brake_history must contain only non-empty values after trimming."
            )
        if self.last_selected_family is not None and not isinstance(
            self.last_selected_family,
            SoftControlFamily,
        ):
            actual_type = type(self.last_selected_family).__name__
            raise TypeError(
                "ClaudeRuntimeSession.last_selected_family must be SoftControlFamily | None, "
                f"got {actual_type}."
            )
        if self.last_commitment_result_summary is not None and not (
            isinstance(self.last_commitment_result_summary, str)
            and self.last_commitment_result_summary.strip()
        ):
            raise ValueError(
                "ClaudeRuntimeSession.last_commitment_result_summary must be non-empty after trimming when provided."
            )
        if self.last_realization_feedback is not None and not isinstance(
            self.last_realization_feedback,
            ReferenceRealizationFeedback,
        ):
            actual_type = type(self.last_realization_feedback).__name__
            raise TypeError(
                "ClaudeRuntimeSession.last_realization_feedback must be "
                f"ReferenceRealizationFeedback | None, got {actual_type}."
            )
        if not isinstance(self.feedback_window, ReferenceRealizationFeedbackWindow):
            actual_type = type(self.feedback_window).__name__
            raise TypeError(
                "ClaudeRuntimeSession.feedback_window must be "
                f"ReferenceRealizationFeedbackWindow, got {actual_type}."
            )
        if self.executive_modulator_memory is not None and not isinstance(
            self.executive_modulator_memory,
            ExecutiveModulatorMemory,
        ):
            actual_type = type(self.executive_modulator_memory).__name__
            raise TypeError(
                "ClaudeRuntimeSession.executive_modulator_memory must be "
                f"ExecutiveModulatorMemory | None, got {actual_type}."
            )

        normalized_last_realization_feedback = self.last_realization_feedback
        normalized_feedback_window = self.feedback_window
        normalized_executive_modulator_memory = canonicalize_executive_modulator_memory(
            self.executive_modulator_memory
        )
        if normalized_executive_modulator_memory != self.executive_modulator_memory:
            object.__setattr__(
                self,
                "executive_modulator_memory",
                normalized_executive_modulator_memory,
            )
        if (
            normalized_last_realization_feedback is not None
            and not normalized_feedback_window.entries
        ):
            normalized_feedback_window = ReferenceRealizationFeedbackWindow(
                entries=(normalized_last_realization_feedback,)
            )
            object.__setattr__(self, "feedback_window", normalized_feedback_window)
        elif normalized_last_realization_feedback is None and normalized_feedback_window.entries:
            normalized_last_realization_feedback = normalized_feedback_window.entries[-1]
            object.__setattr__(
                self,
                "last_realization_feedback",
                normalized_last_realization_feedback,
            )
        if (
            normalized_last_realization_feedback is not None
            and normalized_feedback_window.entries
            and normalized_feedback_window.entries[-1] != normalized_last_realization_feedback
        ):
            raise ValueError(
                "ClaudeRuntimeSession.feedback_window newest entry must match "
                "last_realization_feedback when both are present."
            )
        if normalized_last_realization_feedback is None and normalized_feedback_window.entries:
            raise ValueError(
                "ClaudeRuntimeSession.feedback_window must be empty when "
                "last_realization_feedback is None."
            )

    def as_summary(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "event_index": self.event_index,
            "branch_registry": list(self.branch_registry),
            "active_track_ref": self.active_track_ref,
            "pending_goal_refs": list(self.pending_goal_refs),
            "budget_history": list(self.budget_history),
            "brake_history": list(self.brake_history),
            "feedback_window_size": len(self.feedback_window.entries),
            "last_selected_family": (
                self.last_selected_family.value
                if self.last_selected_family is not None
                else None
            ),
            "last_commitment_result_summary": self.last_commitment_result_summary,
        }


@dataclass(frozen=True, slots=True)
class ClaudeControlLedger:
    event_class: str
    admissible_families: tuple[SoftControlFamily, ...]
    selected_family: SoftControlFamily
    realized_family: SoftControlFamily
    dominant_uncertainty_sources: tuple[str, ...]
    brake_state: BrakeState
    budget_band: str
    primary_reason: str | None = None
    allocation_diagnostics: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not (isinstance(self.event_class, str) and self.event_class.strip()):
            raise ValueError(
                "ClaudeControlLedger.event_class must be non-empty after trimming."
            )
        if any(not isinstance(family, SoftControlFamily) for family in self.admissible_families):
            raise TypeError(
                "ClaudeControlLedger.admissible_families must contain only SoftControlFamily instances."
            )
        if not isinstance(self.selected_family, SoftControlFamily):
            actual_type = type(self.selected_family).__name__
            raise TypeError(
                "ClaudeControlLedger.selected_family must be SoftControlFamily, "
                f"got {actual_type}."
            )
        if not isinstance(self.realized_family, SoftControlFamily):
            actual_type = type(self.realized_family).__name__
            raise TypeError(
                "ClaudeControlLedger.realized_family must be SoftControlFamily, "
                f"got {actual_type}."
            )
        if any(
            not (isinstance(source, str) and source.strip())
            for source in self.dominant_uncertainty_sources
        ):
            raise ValueError(
                "ClaudeControlLedger.dominant_uncertainty_sources must contain only non-empty values after trimming."
            )
        if not isinstance(self.brake_state, BrakeState):
            actual_type = type(self.brake_state).__name__
            raise TypeError(
                "ClaudeControlLedger.brake_state must be BrakeState, "
                f"got {actual_type}."
            )
        if not (isinstance(self.budget_band, str) and self.budget_band.strip()):
            raise ValueError(
                "ClaudeControlLedger.budget_band must be non-empty after trimming."
            )
        if self.primary_reason is not None and not (
            isinstance(self.primary_reason, str) and self.primary_reason.strip()
        ):
            raise ValueError(
                "ClaudeControlLedger.primary_reason must be non-empty after trimming when provided."
            )
        _validate_allocation_diagnostics_payload(
            self.allocation_diagnostics,
            "ClaudeControlLedger.allocation_diagnostics",
        )

    def as_summary(self) -> dict[str, Any]:
        return {
            "event_class": self.event_class,
            "admissible_families": [
                family.value for family in self.admissible_families
            ],
            "selected_family": self.selected_family.value,
            "realized_family": self.realized_family.value,
            "dominant_uncertainty_sources": list(self.dominant_uncertainty_sources),
            "brake_state": self.brake_state.value,
            "budget_band": self.budget_band,
            "primary_reason": self.primary_reason,
            "allocation_diagnostics": _copy_allocation_diagnostics_payload(
                self.allocation_diagnostics
            ),
        }


@dataclass(frozen=True, slots=True)
class ClaudeRuntimeStepResult:
    event_index: int
    bound_event: BoundClaudeHostEvent
    dispatch_decision: DispatchDecision
    executive_state: ReferenceExecutiveState
    selected_family: SoftControlFamily
    realized_family: SoftControlFamily
    brake_state: BrakeState
    control_ledger: ClaudeControlLedger
    feedback_window_summary: ReferenceFeedbackWindowSummary = field(
        default_factory=ReferenceFeedbackWindowSummary
    )
    executive_signal_summary: ExecutiveSignalSummary = field(
        default_factory=lambda: ExecutiveSignalSummary(
            uncertainty=0.0,
            repeated_failure_pressure=0.0,
            quota_pressure=0.0,
            continuity_demand=0.0,
            novelty_pressure=0.0,
            verification_conflict_pressure=0.0,
        )
    )
    executive_modulator_state: ExecutiveModulatorState = field(
        default_factory=lambda: ExecutiveModulatorState(
            focus_gain=0.0,
            explore_gain=0.0,
            stop_pressure=0.0,
            update_pressure=0.0,
        )
    )
    executive_policy_view: ExecutivePolicyView = field(
        default_factory=lambda: ExecutivePolicyView(
            default_profile_bonus=0.0,
            switch_margin=0.0,
            stop_threshold=0.75,
            allow_extra_read_pass=False,
            verification_intensity=0.30,
        )
    )
    closure_required: bool = False
    closure_reason_tags: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    session: ClaudeRuntimeSession = field(default_factory=ClaudeRuntimeSession)
    commitment_result_kind: str | None = None

    def __post_init__(self) -> None:
        if isinstance(self.event_index, bool) or not isinstance(self.event_index, int):
            actual_type = type(self.event_index).__name__
            raise TypeError(
                "ClaudeRuntimeStepResult.event_index must be a positive integer, "
                f"got {actual_type}."
            )
        if self.event_index <= 0:
            raise ValueError("ClaudeRuntimeStepResult.event_index must be positive.")
        if not isinstance(self.bound_event, BoundClaudeHostEvent):
            actual_type = type(self.bound_event).__name__
            raise TypeError(
                "ClaudeRuntimeStepResult.bound_event must be BoundClaudeHostEvent, "
                f"got {actual_type}."
            )
        if not isinstance(self.dispatch_decision, DispatchDecision):
            actual_type = type(self.dispatch_decision).__name__
            raise TypeError(
                "ClaudeRuntimeStepResult.dispatch_decision must be DispatchDecision, "
                f"got {actual_type}."
            )
        if not isinstance(self.executive_state, ReferenceExecutiveState):
            actual_type = type(self.executive_state).__name__
            raise TypeError(
                "ClaudeRuntimeStepResult.executive_state must be ReferenceExecutiveState, "
                f"got {actual_type}."
            )
        if not isinstance(self.selected_family, SoftControlFamily):
            actual_type = type(self.selected_family).__name__
            raise TypeError(
                "ClaudeRuntimeStepResult.selected_family must be SoftControlFamily, "
                f"got {actual_type}."
            )
        if not isinstance(self.realized_family, SoftControlFamily):
            actual_type = type(self.realized_family).__name__
            raise TypeError(
                "ClaudeRuntimeStepResult.realized_family must be SoftControlFamily, "
                f"got {actual_type}."
            )
        if not isinstance(self.brake_state, BrakeState):
            actual_type = type(self.brake_state).__name__
            raise TypeError(
                "ClaudeRuntimeStepResult.brake_state must be BrakeState, "
                f"got {actual_type}."
            )
        if not isinstance(self.control_ledger, ClaudeControlLedger):
            actual_type = type(self.control_ledger).__name__
            raise TypeError(
                "ClaudeRuntimeStepResult.control_ledger must be ClaudeControlLedger, "
                f"got {actual_type}."
            )
        if not isinstance(self.feedback_window_summary, ReferenceFeedbackWindowSummary):
            actual_type = type(self.feedback_window_summary).__name__
            raise TypeError(
                "ClaudeRuntimeStepResult.feedback_window_summary must be "
                f"ReferenceFeedbackWindowSummary, got {actual_type}."
            )
        if not isinstance(self.executive_signal_summary, ExecutiveSignalSummary):
            actual_type = type(self.executive_signal_summary).__name__
            raise TypeError(
                "ClaudeRuntimeStepResult.executive_signal_summary must be "
                f"ExecutiveSignalSummary, got {actual_type}."
            )
        if not isinstance(self.executive_modulator_state, ExecutiveModulatorState):
            actual_type = type(self.executive_modulator_state).__name__
            raise TypeError(
                "ClaudeRuntimeStepResult.executive_modulator_state must be "
                f"ExecutiveModulatorState, got {actual_type}."
            )
        if not isinstance(self.executive_policy_view, ExecutivePolicyView):
            actual_type = type(self.executive_policy_view).__name__
            raise TypeError(
                "ClaudeRuntimeStepResult.executive_policy_view must be "
                f"ExecutivePolicyView, got {actual_type}."
            )
        if not isinstance(self.closure_required, bool):
            actual_type = type(self.closure_required).__name__
            raise TypeError(
                "ClaudeRuntimeStepResult.closure_required must be bool, "
                f"got {actual_type}."
            )
        if any(
            not (isinstance(tag, str) and tag.strip())
            for tag in self.closure_reason_tags
        ):
            raise ValueError(
                "ClaudeRuntimeStepResult.closure_reason_tags must contain only non-empty values after trimming."
            )
        if any(not (isinstance(warning, str) and warning.strip()) for warning in self.warnings):
            raise ValueError(
                "ClaudeRuntimeStepResult.warnings must contain only non-empty values after trimming."
            )
        if not isinstance(self.session, ClaudeRuntimeSession):
            actual_type = type(self.session).__name__
            raise TypeError(
                "ClaudeRuntimeStepResult.session must be ClaudeRuntimeSession, "
                f"got {actual_type}."
            )
        if self.event_index != self.session.event_index:
            raise ValueError(
                "ClaudeRuntimeStepResult.event_index must match session.event_index."
            )
        if (
            self.commitment_result_kind is not None
            and self.commitment_result_kind not in _ALLOWED_COMMITMENT_RESULT_KINDS
        ):
            raise ValueError(
                "ClaudeRuntimeStepResult.commitment_result_kind must be one of the canonical "
                "commitment status values or None."
            )

    @property
    def session_summary(self) -> dict[str, Any]:
        return self.session.as_summary()

    @property
    def executive_state_summary(self) -> dict[str, Any]:
        return {
            "mode_tag": self.executive_state.mode_and_gating.mode_tag,
            "family_mask": sorted(
                family.value for family in self.executive_state.mode_and_gating.family_mask
            ),
            "budget_band": self.executive_state.control_allocation.budget_band,
            "top_family_set": sorted(
                family.value for family in self.executive_state.control_allocation.top_family_set
            ),
            "host_friction_tags": sorted(
                self.executive_state.control_allocation.host_friction_tags
            ),
            "active_track_ref": self.executive_state.goal_continuity.active_track_ref,
            "pending_goal_refs": list(self.executive_state.goal_continuity.pending_goal_refs),
        }

    @property
    def control_ledger_summary(self) -> dict[str, Any]:
        return self.control_ledger.as_summary()

    @property
    def feedback_window_summary_payload(self) -> dict[str, Any]:
        return self.feedback_window_summary.as_summary()

    @property
    def executive_signal_summary_payload(self) -> dict[str, Any]:
        return self.executive_signal_summary.as_payload()

    @property
    def executive_modulator_state_payload(self) -> dict[str, Any]:
        return self.executive_modulator_state.as_payload()

    @property
    def executive_policy_view_payload(self) -> dict[str, Any]:
        return self.executive_policy_view.as_payload()


def run_claude_runtime_step(
    raw_event_name: str,
    raw_payload: Mapping[str, Any] | None,
    session: ClaudeRuntimeSession | None = None,
) -> ClaudeRuntimeStepResult:
    if not is_raw_claude_host_event_name(raw_event_name):
        raise ValueError(
            "run_claude_runtime_step.event_name must be a raw Claude host event name, "
            "not a canonical Cortex event name."
        )
    prior_session = _coerce_session(session)
    bound_event = observe_claude_host_event(raw_event_name, raw_payload)
    normalized_payload = bound_event.normalized_payload
    native_commitment_fields = extract_native_commitment_fields(normalized_payload)
    dispatch_decision = classify_dispatch(
        bound_event.observation,
        payload=normalized_payload,
        native_commitment_fields=native_commitment_fields,
    )

    extraction_result = resolve_commitment_extract_for_dispatch(
        payload=normalized_payload,
        dispatch_decision=dispatch_decision,
        native_commitment_fields=native_commitment_fields,
        allow_message_commitment_fallback=False,
    )
    warnings = merge_warnings(
        bound_event.warnings,
        dispatch_decision.warnings,
        extraction_result.warnings if extraction_result is not None else (),
    )
    session_id, session_id_warnings = _resolve_session_id(prior_session, normalized_payload)
    warnings = merge_warnings(warnings, session_id_warnings)
    prior_feedback_window_summary = summarize_reference_feedback_window(
        prior_session.feedback_window
    )

    candidate = None
    commitment_result_kind: str | None = None
    if dispatch_decision.lane is not DispatchLane.CHEAP:
        candidate, candidate_warnings = bind_claude_host_candidate(
            bound_event,
            dispatch_decision,
            extraction_result,
        )
        warnings = merge_warnings(warnings, candidate_warnings)

    if dispatch_decision.lane is DispatchLane.FULL_COMMITMENT and candidate is not None:
        boundary_assessment, boundary_warnings = _build_boundary_assessment(normalized_payload)
        warnings = merge_warnings(warnings, boundary_warnings)
        verdict = certify_commitment(
            CertificationContext(
                candidate=candidate,
                observation=bound_event.observation,
                environment_handle=_build_environment_handle(normalized_payload),
                wake_reasons=dispatch_decision.wake_decision.reason_tags,
                boundary_tags=boundary_assessment.boundary_tags,
            ),
            provenance_manifest=_build_provenance_manifest(normalized_payload),
            boundary_assessment=boundary_assessment,
        )
        commitment_result_kind = verdict.status.value

    (
        next_branch_registry,
        next_active_track_ref,
        next_pending_goal_refs,
        continuity_warnings,
        continuity_reminders,
    ) = _apply_continuity_update(prior_session, normalized_payload)
    warnings = merge_warnings(warnings, continuity_warnings)
    provisional_session = ClaudeRuntimeSession(
        session_id=session_id,
        event_index=prior_session.event_index + 1,
        branch_registry=next_branch_registry,
        active_track_ref=next_active_track_ref,
        pending_goal_refs=next_pending_goal_refs,
        budget_history=prior_session.budget_history
        + (_budget_entry_for_lane(dispatch_decision.lane),),
        brake_history=prior_session.brake_history,
        last_selected_family=prior_session.last_selected_family,
        last_commitment_result_summary=prior_session.last_commitment_result_summary,
        last_realization_feedback=prior_session.last_realization_feedback,
        feedback_window=prior_session.feedback_window,
    )
    executive_state = build_reference_executive_state(
        bound_event.observation,
        _build_support_snapshot(
            provisional_session=provisional_session,
            bound_event=bound_event,
            dispatch_decision=dispatch_decision,
            warnings=warnings,
            reminders=continuity_reminders,
        ),
        _build_executive_environment_view(normalized_payload),
        provisional_session,
    )
    selection = select_reference_soft_control(executive_state)
    selected_family = selection.selected_family
    brake_state = executive_state.brake.brake_state
    dominant_uncertainty_sources = _dominant_uncertainty_sources(executive_state)
    realized_family, enforcement_warnings = _realize_family(
        selected_family,
        brake_state=brake_state,
        dominant_uncertainty_sources=dominant_uncertainty_sources,
        feedback_pressure_tags=executive_state.control_allocation.feedback_pressure_tags,
    )
    warnings = merge_warnings(warnings, enforcement_warnings)
    control_ledger = ClaudeControlLedger(
        event_class=dispatch_decision.lane.value,
        admissible_families=_admissible_families(executive_state),
        selected_family=selected_family,
        realized_family=realized_family,
        dominant_uncertainty_sources=dominant_uncertainty_sources,
        brake_state=brake_state,
        budget_band=executive_state.control_allocation.budget_band,
        primary_reason=_primary_reason(warnings),
        allocation_diagnostics=build_allocation_diagnostics_payload(
            selection.scorecard,
            selected_delta_over_neutral=selection.neutral_dominance.margin_over_neutral,
            applied_activation_threshold=selection.neutral_dominance.activation_threshold,
            chi_t=selection.chi_t,
        ),
    )
    realization_feedback = ReferenceRealizationFeedback(
        selected_family=selected_family,
        realized_family=realized_family,
        brake_state=brake_state,
        commitment_result_kind=commitment_result_kind,
        warning_codes=tuple(warnings),
        host_friction_tags=tuple(
            sorted(executive_state.control_allocation.host_friction_tags)
        ),
    )
    updated_session = ClaudeRuntimeSession(
        session_id=provisional_session.session_id,
        event_index=provisional_session.event_index,
        branch_registry=provisional_session.branch_registry,
        active_track_ref=provisional_session.active_track_ref,
        pending_goal_refs=provisional_session.pending_goal_refs,
        budget_history=provisional_session.budget_history,
        brake_history=prior_session.brake_history + (brake_state.value,),
        last_selected_family=selected_family,
        last_commitment_result_summary=_commitment_summary_for_lane(
            dispatch_decision.lane,
            commitment_result_kind,
        ),
        last_realization_feedback=realization_feedback,
        feedback_window=prior_session.feedback_window.append(realization_feedback),
        executive_modulator_memory=prior_session.executive_modulator_memory,
    )
    consequential_write_pending = bool(normalized_payload.get("externally_consequential"))
    approval_required = dispatch_decision.lane is not DispatchLane.CHEAP
    evidence_gap = (
        consequential_write_pending
        and _first_concrete_artifact_ref(normalized_payload) is None
    )
    executive_signal_summary = build_executive_signal_summary(
        build_runtime_executive_signal_summary_inputs(
            executive_state=executive_state,
            dispatch_decision=dispatch_decision,
            active_track_ref=provisional_session.active_track_ref,
            pending_goal_refs=provisional_session.pending_goal_refs,
            continuity_warnings=continuity_warnings,
            continuity_reminders=continuity_reminders,
            approval_required=approval_required,
            evidence_gap=evidence_gap,
            consequential_write_pending=consequential_write_pending,
            prior_failed_before_completion=False,
            recent_product_failure_class=None,
            recent_warning_bearing_success_present=recent_warning_bearing_success_present(
                prior_session.feedback_window,
                failed_before_completion=False,
            ),
            preservation_active=False,
        )
    )
    executive_modulator_update = update_executive_modulators(
        executive_signal_summary,
        previous=prior_session.executive_modulator_memory,
    )
    executive_policy_view = build_executive_policy_view(
        executive_signal_summary,
        executive_modulator_update.state,
        chi_t=selection.chi_t,
    )
    closure_reason_tags_value = closure_reason_tags(
        active_track_ref=provisional_session.active_track_ref,
        warnings=warnings,
        continuity_reminders=continuity_reminders,
        brake_state=brake_state,
        feedback_window_summary=prior_feedback_window_summary,
        pending_goal_refs=provisional_session.pending_goal_refs,
    )
    closure_required = bool(closure_reason_tags_value)
    updated_session = ClaudeRuntimeSession(
        session_id=updated_session.session_id,
        event_index=updated_session.event_index,
        branch_registry=updated_session.branch_registry,
        active_track_ref=updated_session.active_track_ref,
        pending_goal_refs=updated_session.pending_goal_refs,
        budget_history=updated_session.budget_history,
        brake_history=updated_session.brake_history,
        last_selected_family=updated_session.last_selected_family,
        last_commitment_result_summary=updated_session.last_commitment_result_summary,
        last_realization_feedback=updated_session.last_realization_feedback,
        feedback_window=updated_session.feedback_window,
        executive_modulator_memory=canonicalize_executive_modulator_memory(
            executive_modulator_update.next_memory
        ),
    )
    return ClaudeRuntimeStepResult(
        event_index=updated_session.event_index,
        bound_event=bound_event,
        dispatch_decision=dispatch_decision,
        executive_state=executive_state,
        selected_family=selected_family,
        realized_family=realized_family,
        brake_state=brake_state,
        control_ledger=control_ledger,
        feedback_window_summary=prior_feedback_window_summary,
        executive_signal_summary=executive_signal_summary,
        executive_modulator_state=executive_modulator_update.state,
        executive_policy_view=executive_policy_view,
        closure_required=closure_required,
        closure_reason_tags=closure_reason_tags_value,
        warnings=warnings,
        session=updated_session,
        commitment_result_kind=commitment_result_kind,
    )


def _coerce_session(session: ClaudeRuntimeSession | None) -> ClaudeRuntimeSession:
    if session is None:
        return ClaudeRuntimeSession()
    if not isinstance(session, ClaudeRuntimeSession):
        actual_type = type(session).__name__
        raise TypeError(
            "run_claude_runtime_step.session must be ClaudeRuntimeSession | None, "
            f"got {actual_type}."
        )
    return session


def _resolve_session_id(
    prior_session: ClaudeRuntimeSession,
    normalized_payload: Mapping[str, Any],
) -> tuple[str | None, tuple[str, ...]]:
    payload_session_id = _as_non_empty_string(normalized_payload.get("session_id"))
    if prior_session.session_id is None:
        return payload_session_id, ()
    if payload_session_id is None or payload_session_id == prior_session.session_id:
        return prior_session.session_id, ()
    return (
        prior_session.session_id,
        (f"session-rejected:mismatched-session-id:{payload_session_id}",),
    )


def _apply_continuity_update(
    prior_session: ClaudeRuntimeSession,
    normalized_payload: Mapping[str, Any],
) -> tuple[tuple[str, ...], str, tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    operation = _branch_operation(normalized_payload)
    branch_registry = list(prior_session.branch_registry)
    active_track_ref = prior_session.active_track_ref
    pending_goal_refs = list(prior_session.pending_goal_refs)
    branch_track_ref = _continuity_track_ref(normalized_payload)
    payload_goal_refs = _pending_goal_refs_from_payload(normalized_payload)
    warnings: tuple[str, ...] = ()
    reminders: tuple[str, ...] = ()

    if operation is None:
        if payload_goal_refs:
            pending_goal_refs = _merge_unique_refs(tuple(pending_goal_refs), payload_goal_refs)
        return (
            tuple(branch_registry),
            active_track_ref,
            tuple(pending_goal_refs),
            warnings,
            reminders,
        )

    if operation is BranchOperation.OPEN:
        if branch_track_ref is None:
            warnings = ("continuity-rejected:missing-open-track-ref",)
            return (
                tuple(prior_session.branch_registry),
                prior_session.active_track_ref,
                tuple(prior_session.pending_goal_refs),
                warnings,
                reminders,
            )
        if branch_track_ref not in branch_registry:
            branch_registry.append(branch_track_ref)
        active_track_ref = branch_track_ref
        pending_goal_refs = [
            goal_ref for goal_ref in pending_goal_refs if goal_ref != branch_track_ref
        ]
        pending_goal_refs = _merge_unique_refs(tuple(pending_goal_refs), payload_goal_refs)
    elif operation is BranchOperation.SUSPEND:
        if (
            branch_track_ref is None
            or branch_track_ref not in branch_registry
            or active_track_ref != branch_track_ref
        ):
            warnings = (_continuity_warning("missing-active-branch", branch_track_ref),)
            return (
                tuple(prior_session.branch_registry),
                prior_session.active_track_ref,
                tuple(prior_session.pending_goal_refs),
                warnings,
                reminders,
            )
        active_track_ref = "main"
        pending_goal_refs = _merge_unique_refs(
            tuple(pending_goal_refs),
            (branch_track_ref, *payload_goal_refs),
        )
    elif operation is BranchOperation.RESUME:
        if branch_track_ref is None or branch_track_ref not in branch_registry:
            warnings = (_continuity_warning("missing-active-branch", branch_track_ref),)
            return (
                tuple(prior_session.branch_registry),
                prior_session.active_track_ref,
                tuple(prior_session.pending_goal_refs),
                warnings,
                reminders,
            )
        if branch_track_ref not in pending_goal_refs:
            warnings = (_continuity_warning("missing-resume-anchor", branch_track_ref),)
            reminders = ("resume-anchor-missing",)
            return (
                tuple(prior_session.branch_registry),
                prior_session.active_track_ref,
                tuple(prior_session.pending_goal_refs),
                warnings,
                reminders,
            )
        active_track_ref = branch_track_ref
        pending_goal_refs = [
            goal_ref for goal_ref in pending_goal_refs if goal_ref != branch_track_ref
        ]
        pending_goal_refs = _merge_unique_refs(tuple(pending_goal_refs), payload_goal_refs)
    elif operation is BranchOperation.MERGE:
        if branch_track_ref is None or branch_track_ref not in branch_registry:
            warnings = (_continuity_warning("missing-active-branch", branch_track_ref),)
            return (
                tuple(prior_session.branch_registry),
                prior_session.active_track_ref,
                tuple(prior_session.pending_goal_refs),
                warnings,
                reminders,
            )
        merge_target_ref = _merge_target_ref(normalized_payload)
        if (
            merge_target_ref is not None
            and merge_target_ref != "main"
            and merge_target_ref not in branch_registry
        ):
            warnings = (_continuity_warning("illegal-merge-target", merge_target_ref),)
            return (
                tuple(prior_session.branch_registry),
                prior_session.active_track_ref,
                tuple(prior_session.pending_goal_refs),
                warnings,
                reminders,
            )
        if branch_track_ref in pending_goal_refs or active_track_ref != branch_track_ref:
            warnings = (
                _continuity_warning(
                    "continuity-mismatch-after-suspension",
                    branch_track_ref,
                ),
            )
            return (
                tuple(prior_session.branch_registry),
                prior_session.active_track_ref,
                tuple(prior_session.pending_goal_refs),
                warnings,
                reminders,
            )
        branch_registry = [
            branch_ref for branch_ref in branch_registry if branch_ref != branch_track_ref
        ]
        if not branch_registry:
            branch_registry = ["main"]
        active_track_ref = merge_target_ref or "main"
        pending_goal_refs = [
            goal_ref for goal_ref in pending_goal_refs if goal_ref != branch_track_ref
        ]
        pending_goal_refs = _merge_unique_refs(tuple(pending_goal_refs), payload_goal_refs)

    if active_track_ref != "main" and active_track_ref not in branch_registry:
        active_track_ref = "main"
    return (
        tuple(branch_registry),
        active_track_ref,
        tuple(pending_goal_refs),
        warnings,
        reminders,
    )


def _build_environment_handle(
    normalized_payload: Mapping[str, Any],
) -> CommitmentEnvironmentHandle:
    available_query_kinds = {EXECUTION_TRACE}
    capability_tags = {"trace/read"}

    if _first_concrete_artifact_ref(normalized_payload) is not None:
        available_query_kinds.add(RESULT_ARTIFACT)
        capability_tags.add("artifact/read")
    if _as_non_empty_string(normalized_payload.get("external_record_ref")) is not None:
        available_query_kinds.add(EXTERNAL_RECORD)
        capability_tags.add("external-record/read")

    return CommitmentEnvironmentHandle(
        available_query_kinds=frozenset(available_query_kinds),
        capability_tags=frozenset(capability_tags),
    )


def _build_executive_environment_view(
    normalized_payload: Mapping[str, Any],
) -> ExecutiveEnvironmentView:
    available_query_kinds = {EXECUTION_TRACE}
    host_capability_tags = {
        "claude-host",
        "local-cli-runtime",
    }
    if _first_concrete_artifact_ref(normalized_payload) is not None:
        available_query_kinds.add(RESULT_ARTIFACT)
    if _as_non_empty_string(normalized_payload.get("external_record_ref")) is not None:
        available_query_kinds.add(EXTERNAL_RECORD)
    return ExecutiveEnvironmentView(
        available_query_kinds=frozenset(available_query_kinds),
        host_capability_tags=frozenset(host_capability_tags),
    )


def _build_support_snapshot(
    *,
    provisional_session: ClaudeRuntimeSession,
    bound_event: BoundClaudeHostEvent,
    dispatch_decision: DispatchDecision,
    warnings: Sequence[str],
    reminders: Sequence[str] = (),
) -> SupportSnapshot:
    approval_boundary_tags = (
        frozenset({"approval-required"})
        if dispatch_decision.lane is not DispatchLane.CHEAP
        else frozenset()
    )
    constraint_tags = frozenset({"runtime-warning"}) if warnings else frozenset()
    affordance_tags = frozenset(
        set(bound_event.lifecycle_surface.context_affordances)
        | set(bound_event.lifecycle_surface.tool_affordances)
        | set(bound_event.lifecycle_surface.turn_affordances)
    )
    return SupportSnapshot(
        trace=SupportTraceState(recent_events=(bound_event.observation.event,)),
        session=SupportSessionState(
            branch_registry=provisional_session.branch_registry,
            pending_goal_refs=provisional_session.pending_goal_refs,
            budget_history=provisional_session.budget_history,
            brake_history=provisional_session.brake_history,
            reminders=tuple(reminders),
        ),
        host=SupportHostState(
            affordance_tags=affordance_tags,
            approval_boundary_tags=approval_boundary_tags,
            constraint_tags=constraint_tags,
        ),
        exec_memory_pub=SupportExecMemoryState(),
    )


def _build_provenance_manifest(
    normalized_payload: Mapping[str, Any],
) -> ProvenanceManifest | None:
    evidence_refs = []
    artifact_ref = _first_concrete_artifact_ref(normalized_payload)
    if artifact_ref is not None:
        from cortex.core.commitments import ProvenanceEvidenceRef

        evidence_refs.append(
            ProvenanceEvidenceRef(
                source_family="result_artifact",
                reference_id=artifact_ref,
            )
        )
    external_record_ref = _as_non_empty_string(normalized_payload.get("external_record_ref"))
    if external_record_ref is not None:
        from cortex.core.commitments import ProvenanceEvidenceRef

        evidence_refs.append(
            ProvenanceEvidenceRef(
                source_family="external_record",
                reference_id=external_record_ref,
            )
        )
    if not evidence_refs:
        return None
    return ProvenanceManifest(evidence_refs=tuple(evidence_refs))


def _build_boundary_assessment(
    normalized_payload: Mapping[str, Any],
) -> tuple[BoundaryAssessment, tuple[str, ...]]:
    blocked = bool(normalized_payload.get("boundary_blocked"))
    reason_code = _as_non_empty_string(normalized_payload.get("boundary_reason_code"))
    warnings: tuple[str, ...] = ()
    if blocked and reason_code is None:
        blocked = False
        warnings = (
            "Ignored boundary_blocked=True because no boundary_reason_code was provided.",
        )
    return (
        BoundaryAssessment(
            blocked=blocked,
            reason_code=reason_code if blocked else None,
            boundary_tags=_as_tag_set(normalized_payload.get("boundary_tags")),
            capability_tags=_as_tag_set(normalized_payload.get("boundary_capability_tags")),
        ),
        warnings,
    )


def _budget_entry_for_lane(lane: DispatchLane) -> str:
    if lane is DispatchLane.CHEAP:
        return "shell-low"
    if lane is DispatchLane.CANDIDATE_BEARING:
        return "shell-medium"
    return "shell-high"


def _commitment_summary_for_lane(
    lane: DispatchLane,
    commitment_result_kind: str | None,
) -> str | None:
    if lane is DispatchLane.CHEAP:
        return None
    if lane is DispatchLane.CANDIDATE_BEARING:
        return "candidate-only"
    return commitment_result_kind


def _first_concrete_artifact_ref(normalized_payload: Mapping[str, Any]) -> str | None:
    for key in ("result_artifact_ref", "artifact_ref"):
        value = _as_non_empty_string(normalized_payload.get(key))
        if value is not None:
            return value
    return None


def _as_tag_set(value: Any) -> frozenset[str]:
    if value is None:
        return frozenset()
    if isinstance(value, str):
        tag = value.strip()
        return frozenset({tag}) if tag else frozenset()
    if not isinstance(value, Sequence) or isinstance(value, (bytes, bytearray)):
        return frozenset()
    tags: list[str] = []
    for item in value:
        tag = _as_non_empty_string(item)
        if tag is not None and tag not in tags:
            tags.append(tag)
    return frozenset(tags)


def _as_non_empty_string(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


def _branch_operation(normalized_payload: Mapping[str, Any]) -> BranchOperation | None:
    raw_operation = _as_non_empty_string(normalized_payload.get("branch_operation"))
    if raw_operation is None:
        return None
    try:
        return BranchOperation(raw_operation)
    except ValueError:
        return None


def _continuity_track_ref(normalized_payload: Mapping[str, Any]) -> str | None:
    branch_track_ref = _as_non_empty_string(normalized_payload.get("branch_track_ref"))
    if branch_track_ref is not None:
        return branch_track_ref
    active_track_ref = _as_non_empty_string(normalized_payload.get("active_track_ref"))
    if active_track_ref == "main":
        return None
    return active_track_ref


def _merge_target_ref(normalized_payload: Mapping[str, Any]) -> str | None:
    return _as_non_empty_string(normalized_payload.get("merge_target_ref"))


def _pending_goal_refs_from_payload(normalized_payload: Mapping[str, Any]) -> tuple[str, ...]:
    value = normalized_payload.get("pending_goal_refs")
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return ()
    refs: list[str] = []
    for item in value:
        goal_ref = _as_non_empty_string(item)
        if goal_ref is not None and goal_ref not in refs:
            refs.append(goal_ref)
    return tuple(refs)


def _merge_unique_refs(
    existing_refs: tuple[str, ...],
    incoming_refs: Sequence[str],
) -> list[str]:
    ordered_refs: list[str] = []
    for goal_ref in existing_refs:
        if goal_ref not in ordered_refs:
            ordered_refs.append(goal_ref)
    for goal_ref in incoming_refs:
        if goal_ref not in ordered_refs:
            ordered_refs.append(goal_ref)
    return ordered_refs


def _continuity_warning(reason_code: str, subject: str | None) -> str:
    if subject is None:
        return f"continuity-rejected:{reason_code}"
    return f"continuity-rejected:{reason_code}:{subject}"


def _admissible_families(
    executive_state: ReferenceExecutiveState,
) -> tuple[SoftControlFamily, ...]:
    admissible: list[SoftControlFamily] = []
    for family in SoftControlFamily:
        if family is SoftControlFamily.NEUTRAL or family in executive_state.mode_and_gating.family_mask:
            admissible.append(family)
    return tuple(admissible)


def _dominant_uncertainty_sources(
    executive_state: ReferenceExecutiveState,
) -> tuple[str, ...]:
    ranked = sorted(
        executive_state.uncertainty_monitoring.classwise_uncertainty,
        key=lambda estimate: (-estimate.level, estimate.class_tag),
    )
    return tuple(estimate.class_tag for estimate in ranked[:2])


def _realize_family(
    selected_family: SoftControlFamily,
    *,
    brake_state: BrakeState,
    dominant_uncertainty_sources: tuple[str, ...],
    feedback_pressure_tags: frozenset[str],
) -> tuple[SoftControlFamily, tuple[str, ...]]:
    if selected_family in {
        SoftControlFamily.NEUTRAL,
        SoftControlFamily.CHECK,
        SoftControlFamily.BRAKE,
    }:
        return selected_family, ()
    if (
        brake_state is BrakeState.GUARDED
        and _has_guarded_feedback_enforcement_pressure(feedback_pressure_tags)
    ):
        if any(source in {"evidence", "environment"} for source in dominant_uncertainty_sources):
            realized_family = SoftControlFamily.CHECK
        else:
            realized_family = SoftControlFamily.NEUTRAL
        return (
            realized_family,
            (
                f"guarded-feedback-enforced:{selected_family.value}:{realized_family.value}",
            ),
        )
    if brake_state is not BrakeState.LATCHED:
        return selected_family, ()
    if any(source in {"evidence", "environment"} for source in dominant_uncertainty_sources):
        realized_family = SoftControlFamily.CHECK
    else:
        realized_family = SoftControlFamily.NEUTRAL
    return (
        realized_family,
        (
            f"latched-brake-enforced:{selected_family.value}:{realized_family.value}",
        ),
    )


def _has_guarded_feedback_enforcement_pressure(
    feedback_pressure_tags: frozenset[str],
) -> bool:
    return bool(
        {
            "feedback:override-pressure",
            "feedback:rejection-pressure",
        }
        & feedback_pressure_tags
    )


def _primary_reason(warnings: tuple[str, ...]) -> str | None:
    for warning in warnings:
        if warning.startswith(
            ("latched-brake-enforced:", "guarded-feedback-enforced:")
        ):
            return warning
    return warnings[0] if warnings else None


_ALLOCATION_DIAGNOSTICS_KEYS = (
    "alpha_t",
    "activation_threshold",
    "selected_delta_over_neutral",
    "chi_t",
    "scores",
)
_ALLOCATION_SCORE_KEYS = (
    "family",
    "online_score",
    "memory_score",
    "allocated_score",
    "activation_threshold",
    "admissible",
    "reason_tags",
)


def _validate_allocation_diagnostics_payload(payload: dict[str, Any], label: str) -> None:
    if not isinstance(payload, dict):
        actual_type = type(payload).__name__
        raise TypeError(f"{label} must be dict[str, Any], got {actual_type}.")
    if tuple(payload) != _ALLOCATION_DIAGNOSTICS_KEYS:
        raise ValueError(
            f"{label} must preserve the locked key order {_ALLOCATION_DIAGNOSTICS_KEYS!r}."
        )
    for key in ("alpha_t", "activation_threshold", "selected_delta_over_neutral", "chi_t"):
        value = payload[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            actual_type = type(value).__name__
            raise TypeError(f"{label}.{key} must be numeric, got {actual_type}.")
    scores = payload["scores"]
    if not isinstance(scores, list):
        actual_type = type(scores).__name__
        raise TypeError(f"{label}.scores must be list[dict[str, Any]], got {actual_type}.")
    for index, score in enumerate(scores):
        score_label = f"{label}.scores[{index}]"
        if not isinstance(score, dict):
            actual_type = type(score).__name__
            raise TypeError(f"{score_label} must be dict[str, Any], got {actual_type}.")
        if tuple(score) != _ALLOCATION_SCORE_KEYS:
            raise ValueError(
                f"{score_label} must preserve the locked key order {_ALLOCATION_SCORE_KEYS!r}."
            )
        if not (isinstance(score["family"], str) and score["family"].strip()):
            raise ValueError(f"{score_label}.family must be non-empty after trimming.")
        for key in ("online_score", "memory_score", "allocated_score", "activation_threshold"):
            value = score[key]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                actual_type = type(value).__name__
                raise TypeError(f"{score_label}.{key} must be numeric, got {actual_type}.")
        if not isinstance(score["admissible"], bool):
            actual_type = type(score["admissible"]).__name__
            raise TypeError(f"{score_label}.admissible must be bool, got {actual_type}.")
        reason_tags = score["reason_tags"]
        if not isinstance(reason_tags, list):
            actual_type = type(reason_tags).__name__
            raise TypeError(f"{score_label}.reason_tags must be list[str], got {actual_type}.")
        if any(not (isinstance(tag, str) and tag.strip()) for tag in reason_tags):
            raise ValueError(f"{score_label}.reason_tags must contain only non-empty strings.")


def _copy_allocation_diagnostics_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "alpha_t": payload["alpha_t"],
        "activation_threshold": payload["activation_threshold"],
        "selected_delta_over_neutral": payload["selected_delta_over_neutral"],
        "chi_t": payload["chi_t"],
        "scores": [
            {
                "family": score["family"],
                "online_score": score["online_score"],
                "memory_score": score["memory_score"],
                "allocated_score": score["allocated_score"],
                "admissible": score["admissible"],
                "reason_tags": list(score["reason_tags"]),
            }
            for score in payload["scores"]
        ],
    }


__all__ = [
    "ClaudeControlLedger",
    "ClaudeRuntimeSession",
    "ClaudeRuntimeStepResult",
    "run_claude_runtime_step",
]
