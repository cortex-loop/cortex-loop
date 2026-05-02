"""Reference-host runtime step composition over landed driver/core/SRE surfaces."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from math import isfinite
from typing import TYPE_CHECKING, Any

from cortex.core.certification import certify_commitment
from cortex.core.commitments import (
    BoundaryAssessment,
    CertificationContext,
    CommitmentStatus,
    ProvenanceEvidenceRef,
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
from cortex.drivers.reference_host import BoundReferenceHostEvent, observe_reference_host_event
from cortex.drivers.reference_host_commitment import bind_reference_host_candidate
from cortex.hosts._executive_closure import (
    assert_post_step_feedback_window_alignment,
    assert_runtime_posture_alignment,
    build_shared_realization_feedback,
    build_runtime_operator_task_state,
    build_runtime_executive_signal_summary_inputs,
    canonicalize_executive_modulator_memory,
    classify_runtime_progress_signal,
    closure_reason_tags,
    probe_result_class_for_runtime,
    public_posture_for_task_mode,
    recent_probe_failure_class as recent_probe_failure_class_from_feedback_window,
    recent_warning_bearing_success_present,
    task_mode_for_runtime,
    verification_state_for_runtime,
)
from cortex.sre.allocation import (
    build_allocation_diagnostics_payload,
    build_audit_projection_payload,
)
from cortex.sre.branching import BranchOperation
from cortex.sre.brake import BrakeState
from cortex.sre.debt_control import (
    DebtControlPressure,
    build_runtime_debt_control_pressure,
)
from cortex.sre.executive_summary import (
    ExecutiveSignalSummary,
    build_executive_signal_summary,
)
from cortex.sre.families import SoftControlFamily
from cortex.sre.goals import make_resume_reminder, parse_resume_reminder_track
from cortex.sre.mediation import ReferenceMediationMode
from cortex.sre.modulators import (
    ExecutiveModulatorMemory,
    ExecutiveModulatorState,
    update_executive_modulators,
)
from cortex.sre.operator_routing import (
    OperatorRouteDecision,
    OperatorTaskState,
    build_operator_route_diagnostics,
    select_operator_route_with_policy,
)
from cortex.sre.opportunities import BoundedProbeContract, HostNativeOpportunity
from cortex.sre.policy_view import ExecutivePolicyView, build_executive_policy_view
from cortex.sre.reference_builder import build_reference_executive_state
from cortex.sre.feedback import (
    ReferenceFeedbackWindowSummary,
    ReferenceRealizationFeedback,
    ReferenceRealizationFeedbackWindow,
    summarize_reference_feedback_window,
)
from cortex.sre.expectations import (
    ExpectationLedger,
    ResolutionDeficitState,
    update_expectation_ledger_for_structured_step,
)
from cortex.sre.reference_scoring import (
    rejected_cheaper_families as scorecard_rejected_cheaper_families,
)
from cortex.sre.reference_scoring import select_reference_soft_control
from cortex.sre.state import ReferenceExecutiveState

if TYPE_CHECKING:
    from cortex.aux.publication import OfflineSupportPublication

_ALLOWED_COMMITMENT_RESULT_KINDS = frozenset(status.value for status in CommitmentStatus)


@dataclass(frozen=True, slots=True)
class ReferenceRuntimeSession:
    session_id: str | None = None
    event_index: int = 0
    branch_registry: tuple[str, ...] = ("main",)
    active_track_ref: str = "main"
    pending_goal_refs: tuple[str, ...] = ()
    continuity_reminders: tuple[str, ...] = ()
    budget_history: tuple[str, ...] = ()
    brake_history: tuple[str, ...] = ()
    brake_tonic_history: tuple[float, ...] = ()
    last_selected_family: SoftControlFamily | None = None
    last_commitment_result_summary: str | None = None
    last_realization_feedback: ReferenceRealizationFeedback | None = None
    feedback_window: ReferenceRealizationFeedbackWindow = field(
        default_factory=ReferenceRealizationFeedbackWindow
    )
    expectation_ledger: ExpectationLedger = field(default_factory=ExpectationLedger)
    executive_modulator_memory: ExecutiveModulatorMemory | None = None

    def __post_init__(self) -> None:
        if self.session_id is not None and not (
            isinstance(self.session_id, str) and self.session_id.strip()
        ):
            raise ValueError(
                "ReferenceRuntimeSession.session_id must be non-empty after trimming when provided."
            )
        if isinstance(self.event_index, bool) or not isinstance(self.event_index, int):
            actual_type = type(self.event_index).__name__
            raise TypeError(
                "ReferenceRuntimeSession.event_index must be a non-negative integer, "
                f"got {actual_type}."
            )
        if self.event_index < 0:
            raise ValueError("ReferenceRuntimeSession.event_index must be non-negative.")
        if any(not (isinstance(ref, str) and ref.strip()) for ref in self.branch_registry):
            raise ValueError(
                "ReferenceRuntimeSession.branch_registry must contain only non-empty values after trimming."
            )
        if not (isinstance(self.active_track_ref, str) and self.active_track_ref.strip()):
            raise ValueError(
                "ReferenceRuntimeSession.active_track_ref must be non-empty after trimming."
            )
        if self.active_track_ref != "main" and self.active_track_ref not in self.branch_registry:
            raise ValueError(
                "ReferenceRuntimeSession.active_track_ref must be `main` or a member of branch_registry."
            )
        if any(not (isinstance(ref, str) and ref.strip()) for ref in self.pending_goal_refs):
            raise ValueError(
                "ReferenceRuntimeSession.pending_goal_refs must contain only non-empty values after trimming."
            )
        if any(
            not (isinstance(reminder, str) and reminder.strip())
            for reminder in self.continuity_reminders
        ):
            raise ValueError(
                "ReferenceRuntimeSession.continuity_reminders must contain only non-empty values after trimming."
            )
        if any(not (isinstance(entry, str) and entry.strip()) for entry in self.budget_history):
            raise ValueError(
                "ReferenceRuntimeSession.budget_history must contain only non-empty values after trimming."
            )
        if any(not (isinstance(entry, str) and entry.strip()) for entry in self.brake_history):
            raise ValueError(
                "ReferenceRuntimeSession.brake_history must contain only non-empty values after trimming."
            )
        for entry in self.brake_tonic_history:
            if isinstance(entry, bool) or not isinstance(entry, (int, float)):
                actual_type = type(entry).__name__
                raise TypeError(
                    "ReferenceRuntimeSession.brake_tonic_history must contain only "
                    f"numeric values in [0.0, 1.0], got {actual_type}."
                )
            if not 0.0 <= float(entry) <= 1.0:
                raise ValueError(
                    "ReferenceRuntimeSession.brake_tonic_history entries must be between 0.0 and 1.0."
                )
        if self.last_selected_family is not None and not isinstance(
            self.last_selected_family,
            SoftControlFamily,
        ):
            actual_type = type(self.last_selected_family).__name__
            raise TypeError(
                "ReferenceRuntimeSession.last_selected_family must be SoftControlFamily | None, "
                f"got {actual_type}."
            )
        if self.last_commitment_result_summary is not None and not (
            isinstance(self.last_commitment_result_summary, str)
            and self.last_commitment_result_summary.strip()
        ):
            raise ValueError(
                "ReferenceRuntimeSession.last_commitment_result_summary must be non-empty after trimming when provided."
            )
        if self.last_realization_feedback is not None and not isinstance(
            self.last_realization_feedback,
            ReferenceRealizationFeedback,
        ):
            actual_type = type(self.last_realization_feedback).__name__
            raise TypeError(
                "ReferenceRuntimeSession.last_realization_feedback must be "
                f"ReferenceRealizationFeedback | None, got {actual_type}."
            )
        if not isinstance(self.feedback_window, ReferenceRealizationFeedbackWindow):
            actual_type = type(self.feedback_window).__name__
            raise TypeError(
                "ReferenceRuntimeSession.feedback_window must be "
                f"ReferenceRealizationFeedbackWindow, got {actual_type}."
            )
        if not isinstance(self.expectation_ledger, ExpectationLedger):
            actual_type = type(self.expectation_ledger).__name__
            raise TypeError(
                "ReferenceRuntimeSession.expectation_ledger must be "
                f"ExpectationLedger, got {actual_type}."
            )
        if self.executive_modulator_memory is not None and not isinstance(
            self.executive_modulator_memory,
            ExecutiveModulatorMemory,
        ):
            actual_type = type(self.executive_modulator_memory).__name__
            raise TypeError(
                "ReferenceRuntimeSession.executive_modulator_memory must be "
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
        elif (
            normalized_last_realization_feedback is None
            and normalized_feedback_window.entries
        ):
            normalized_last_realization_feedback = normalized_feedback_window.entries[-1]
            object.__setattr__(
                self,
                "last_realization_feedback",
                normalized_last_realization_feedback,
            )
        if (
            normalized_last_realization_feedback is not None
            and normalized_feedback_window.entries
            and normalized_feedback_window.entries[-1]
            != normalized_last_realization_feedback
        ):
            raise ValueError(
                "ReferenceRuntimeSession.feedback_window newest entry must match "
                "last_realization_feedback when both are present."
            )
        if (
            normalized_last_realization_feedback is None
            and normalized_feedback_window.entries
        ):
            raise ValueError(
                "ReferenceRuntimeSession.feedback_window must be empty when "
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
            "expectation_ledger": self.expectation_ledger.as_payload(),
            "last_selected_family": (
                self.last_selected_family.value
                if self.last_selected_family is not None
                else None
            ),
            "last_commitment_result_summary": self.last_commitment_result_summary,
        }


@dataclass(frozen=True, slots=True)
class ReferenceControlLedger:
    event_class: str
    admissible_families: tuple[SoftControlFamily, ...]
    selected_family: SoftControlFamily
    realized_family: SoftControlFamily
    dominant_uncertainty_sources: tuple[str, ...]
    brake_state: BrakeState
    budget_band: str
    primary_reason: str | None = None
    allocation_diagnostics: dict[str, Any] = field(default_factory=dict)
    audit_projection: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if not (isinstance(self.event_class, str) and self.event_class.strip()):
            raise ValueError(
                "ReferenceControlLedger.event_class must be non-empty after trimming."
            )
        if any(not isinstance(family, SoftControlFamily) for family in self.admissible_families):
            raise TypeError(
                "ReferenceControlLedger.admissible_families must contain only SoftControlFamily instances."
            )
        if not isinstance(self.selected_family, SoftControlFamily):
            actual_type = type(self.selected_family).__name__
            raise TypeError(
                "ReferenceControlLedger.selected_family must be SoftControlFamily, "
                f"got {actual_type}."
            )
        if not isinstance(self.realized_family, SoftControlFamily):
            actual_type = type(self.realized_family).__name__
            raise TypeError(
                "ReferenceControlLedger.realized_family must be SoftControlFamily, "
                f"got {actual_type}."
            )
        if any(
            not (isinstance(source, str) and source.strip())
            for source in self.dominant_uncertainty_sources
        ):
            raise ValueError(
                "ReferenceControlLedger.dominant_uncertainty_sources must contain only non-empty values after trimming."
            )
        if not isinstance(self.brake_state, BrakeState):
            actual_type = type(self.brake_state).__name__
            raise TypeError(
                "ReferenceControlLedger.brake_state must be BrakeState, "
                f"got {actual_type}."
            )
        if not (isinstance(self.budget_band, str) and self.budget_band.strip()):
            raise ValueError(
                "ReferenceControlLedger.budget_band must be non-empty after trimming."
            )
        if self.primary_reason is not None and not (
            isinstance(self.primary_reason, str) and self.primary_reason.strip()
        ):
            raise ValueError(
                "ReferenceControlLedger.primary_reason must be non-empty after trimming when provided."
            )
        _validate_allocation_diagnostics_payload(
            self.allocation_diagnostics,
            "ReferenceControlLedger.allocation_diagnostics",
        )
        if self.audit_projection is not None:
            _validate_audit_projection_payload(
                self.audit_projection,
                "ReferenceControlLedger.audit_projection",
            )

    def as_summary(self) -> dict[str, Any]:
        payload = {
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
        if self.audit_projection is not None:
            payload["audit_projection"] = _copy_audit_projection_payload(
                self.audit_projection
            )
        return payload


@dataclass(frozen=True, slots=True)
class ReferenceRuntimeStepResult:
    event_index: int
    bound_event: BoundReferenceHostEvent
    dispatch_decision: DispatchDecision
    executive_state: ReferenceExecutiveState
    selected_family: SoftControlFamily
    realized_family: SoftControlFamily
    brake_state: BrakeState
    control_ledger: ReferenceControlLedger
    feedback_window_summary: ReferenceFeedbackWindowSummary = field(
        default_factory=ReferenceFeedbackWindowSummary
    )
    resolution_deficit: ResolutionDeficitState = field(
        default_factory=ResolutionDeficitState
    )
    debt_control: DebtControlPressure = field(default_factory=DebtControlPressure)
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
    operator_task_state: OperatorTaskState | None = None
    operator_route: OperatorRouteDecision | None = None
    closure_required: bool = False
    closure_reason_tags: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    session: ReferenceRuntimeSession = field(default_factory=ReferenceRuntimeSession)
    commitment_result_kind: str | None = None

    def __post_init__(self) -> None:
        if isinstance(self.event_index, bool) or not isinstance(self.event_index, int):
            actual_type = type(self.event_index).__name__
            raise TypeError(
                "ReferenceRuntimeStepResult.event_index must be a positive integer, "
                f"got {actual_type}."
            )
        if self.event_index <= 0:
            raise ValueError("ReferenceRuntimeStepResult.event_index must be positive.")
        if not isinstance(self.bound_event, BoundReferenceHostEvent):
            actual_type = type(self.bound_event).__name__
            raise TypeError(
                "ReferenceRuntimeStepResult.bound_event must be BoundReferenceHostEvent, "
                f"got {actual_type}."
            )
        if not isinstance(self.dispatch_decision, DispatchDecision):
            actual_type = type(self.dispatch_decision).__name__
            raise TypeError(
                "ReferenceRuntimeStepResult.dispatch_decision must be DispatchDecision, "
                f"got {actual_type}."
            )
        if not isinstance(self.executive_state, ReferenceExecutiveState):
            actual_type = type(self.executive_state).__name__
            raise TypeError(
                "ReferenceRuntimeStepResult.executive_state must be ReferenceExecutiveState, "
                f"got {actual_type}."
            )
        if not isinstance(self.selected_family, SoftControlFamily):
            actual_type = type(self.selected_family).__name__
            raise TypeError(
                "ReferenceRuntimeStepResult.selected_family must be SoftControlFamily, "
                f"got {actual_type}."
            )
        if not isinstance(self.realized_family, SoftControlFamily):
            actual_type = type(self.realized_family).__name__
            raise TypeError(
                "ReferenceRuntimeStepResult.realized_family must be SoftControlFamily, "
                f"got {actual_type}."
            )
        if not isinstance(self.brake_state, BrakeState):
            actual_type = type(self.brake_state).__name__
            raise TypeError(
                "ReferenceRuntimeStepResult.brake_state must be BrakeState, "
                f"got {actual_type}."
            )
        if not isinstance(self.control_ledger, ReferenceControlLedger):
            actual_type = type(self.control_ledger).__name__
            raise TypeError(
                "ReferenceRuntimeStepResult.control_ledger must be ReferenceControlLedger, "
                f"got {actual_type}."
            )
        if not isinstance(self.feedback_window_summary, ReferenceFeedbackWindowSummary):
            actual_type = type(self.feedback_window_summary).__name__
            raise TypeError(
                "ReferenceRuntimeStepResult.feedback_window_summary must be "
                f"ReferenceFeedbackWindowSummary, got {actual_type}."
            )
        if not isinstance(self.resolution_deficit, ResolutionDeficitState):
            actual_type = type(self.resolution_deficit).__name__
            raise TypeError(
                "ReferenceRuntimeStepResult.resolution_deficit must be "
                f"ResolutionDeficitState, got {actual_type}."
            )
        if not isinstance(self.debt_control, DebtControlPressure):
            actual_type = type(self.debt_control).__name__
            raise TypeError(
                "ReferenceRuntimeStepResult.debt_control must be "
                f"DebtControlPressure, got {actual_type}."
            )
        if not isinstance(self.executive_signal_summary, ExecutiveSignalSummary):
            actual_type = type(self.executive_signal_summary).__name__
            raise TypeError(
                "ReferenceRuntimeStepResult.executive_signal_summary must be "
                f"ExecutiveSignalSummary, got {actual_type}."
            )
        if not isinstance(self.executive_modulator_state, ExecutiveModulatorState):
            actual_type = type(self.executive_modulator_state).__name__
            raise TypeError(
                "ReferenceRuntimeStepResult.executive_modulator_state must be "
                f"ExecutiveModulatorState, got {actual_type}."
            )
        if not isinstance(self.executive_policy_view, ExecutivePolicyView):
            actual_type = type(self.executive_policy_view).__name__
            raise TypeError(
                "ReferenceRuntimeStepResult.executive_policy_view must be "
                f"ExecutivePolicyView, got {actual_type}."
            )
        if not isinstance(self.operator_task_state, OperatorTaskState):
            actual_type = type(self.operator_task_state).__name__
            raise TypeError(
                "ReferenceRuntimeStepResult.operator_task_state must be "
                f"OperatorTaskState, got {actual_type}."
            )
        if not isinstance(self.operator_route, OperatorRouteDecision):
            actual_type = type(self.operator_route).__name__
            raise TypeError(
                "ReferenceRuntimeStepResult.operator_route must be "
                f"OperatorRouteDecision, got {actual_type}."
            )
        if not isinstance(self.closure_required, bool):
            actual_type = type(self.closure_required).__name__
            raise TypeError(
                "ReferenceRuntimeStepResult.closure_required must be bool, "
                f"got {actual_type}."
            )
        if any(
            not (isinstance(tag, str) and tag.strip())
            for tag in self.closure_reason_tags
        ):
            raise ValueError(
                "ReferenceRuntimeStepResult.closure_reason_tags must contain only non-empty values after trimming."
            )
        if any(not (isinstance(warning, str) and warning.strip()) for warning in self.warnings):
            raise ValueError(
                "ReferenceRuntimeStepResult.warnings must contain only non-empty values after trimming."
            )
        if not isinstance(self.session, ReferenceRuntimeSession):
            actual_type = type(self.session).__name__
            raise TypeError(
                "ReferenceRuntimeStepResult.session must be ReferenceRuntimeSession, "
                f"got {actual_type}."
            )
        if self.event_index != self.session.event_index:
            raise ValueError(
                "ReferenceRuntimeStepResult.event_index must match session.event_index."
            )
        if (
            self.commitment_result_kind is not None
            and self.commitment_result_kind not in _ALLOWED_COMMITMENT_RESULT_KINDS
        ):
            raise ValueError(
                "ReferenceRuntimeStepResult.commitment_result_kind must be one of the canonical "
                "commitment status values or None."
            )

    @property
    def session_summary(self) -> dict[str, Any]:
        return self.session.as_summary()

    @property
    def executive_state_summary(self) -> dict[str, Any]:
        return {
            "posture": public_posture_for_task_mode(
                self.executive_state.mode_and_gating.task_mode
            ),
            "anti_thrash_state": self.executive_state.control_allocation.anti_thrash_state,
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
            "probe_path_state": self.executive_state.control_allocation.probe_path_state,
            "probe_unavailable_reason": (
                self.executive_state.control_allocation.probe_unavailable_reason
            ),
            "active_track_ref": self.executive_state.goal_continuity.active_track_ref,
            "pending_goal_refs": list(self.executive_state.goal_continuity.pending_goal_refs),
            "anchor_source": self.executive_state.goal_continuity.anchor_source,
            "anchor_freshness": self.executive_state.goal_continuity.anchor_freshness,
            "branch_intent_present": (
                self.executive_state.goal_continuity.branch_intent_present
            ),
        }

    @property
    def control_ledger_summary(self) -> dict[str, Any]:
        return self.control_ledger.as_summary()

    @property
    def feedback_window_summary_payload(self) -> dict[str, Any]:
        return self.feedback_window_summary.as_summary()

    @property
    def resolution_deficit_payload(self) -> dict[str, Any]:
        return self.resolution_deficit.as_payload()

    @property
    def debt_control_payload(self) -> dict[str, Any]:
        return self.debt_control.as_payload()

    @property
    def executive_signal_summary_payload(self) -> dict[str, Any]:
        return self.executive_signal_summary.as_payload()

    @property
    def executive_modulator_state_payload(self) -> dict[str, Any]:
        return self.executive_modulator_state.as_payload()

    @property
    def executive_policy_view_payload(self) -> dict[str, Any]:
        return self.executive_policy_view.as_payload()

    @property
    def operator_route_payload(self) -> dict[str, Any]:
        return build_operator_route_diagnostics(
            self.operator_task_state,
            self.operator_route,
        )


def run_reference_runtime_step(
    raw_event_name: str,
    raw_payload: Mapping[str, Any] | None,
    session: ReferenceRuntimeSession | None = None,
    *,
    executive_environment_view: ExecutiveEnvironmentView | None = None,
    mediation_mode: ReferenceMediationMode = ReferenceMediationMode.IDENTITY,
    offline_publication: OfflineSupportPublication | None = None,
    audit_intensity: str = "minimal",
) -> ReferenceRuntimeStepResult:
    prior_session = _coerce_session(session)
    bound_event = observe_reference_host_event(raw_event_name, raw_payload)
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
    consequential_write_pending = bool(normalized_payload.get("externally_consequential"))
    approval_required = dispatch_decision.lane is not DispatchLane.CHEAP
    evidence_gap = (
        consequential_write_pending
        and _first_concrete_artifact_ref(normalized_payload) is None
    )

    candidate = None
    commitment_result_kind: str | None = None
    if dispatch_decision.lane is not DispatchLane.CHEAP:
        candidate, candidate_warnings = bind_reference_host_candidate(
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
    ) = _apply_continuity_update(
        prior_session,
        normalized_payload,
    )
    warnings = merge_warnings(warnings, continuity_warnings)
    provisional_session = ReferenceRuntimeSession(
        session_id=session_id,
        event_index=prior_session.event_index + 1,
        branch_registry=next_branch_registry,
        active_track_ref=next_active_track_ref,
        pending_goal_refs=next_pending_goal_refs,
        continuity_reminders=continuity_reminders,
        budget_history=prior_session.budget_history + (_budget_entry_for_lane(dispatch_decision.lane),),
        brake_history=prior_session.brake_history,
        brake_tonic_history=prior_session.brake_tonic_history,
        last_selected_family=prior_session.last_selected_family,
        last_commitment_result_summary=prior_session.last_commitment_result_summary,
        last_realization_feedback=prior_session.last_realization_feedback,
        feedback_window=prior_session.feedback_window,
        expectation_ledger=prior_session.expectation_ledger,
    )
    support_snapshot = _build_support_snapshot(
        provisional_session=provisional_session,
        bound_event=bound_event,
        dispatch_decision=dispatch_decision,
        warnings=warnings,
        reminders=continuity_reminders,
    )
    opportunities = _reference_host_native_opportunities(bound_event)
    runtime_task_mode = task_mode_for_runtime(
        dispatch_decision=dispatch_decision,
        active_track_ref=provisional_session.active_track_ref,
        pending_goal_refs=provisional_session.pending_goal_refs,
        continuity_warnings=continuity_warnings,
        continuity_reminders=continuity_reminders,
        approval_required=approval_required,
        evidence_gap=evidence_gap,
        consequential_write_pending=consequential_write_pending,
        preservation_active=False,
    )
    prior_resolution_deficit = prior_session.expectation_ledger.resolution_deficit(
        current_step=provisional_session.event_index
    )
    debt_control = build_runtime_debt_control_pressure(
        resolution_deficit=prior_resolution_deficit,
        task_mode=runtime_task_mode,
        active_track_ref=provisional_session.active_track_ref,
        pending_goal_refs=provisional_session.pending_goal_refs,
        continuity_warnings=continuity_warnings,
        continuity_reminders=continuity_reminders,
        degradation_pressure_bonus=prior_feedback_window_summary.degradation_pressure_bonus,
        sustained_spike_flags=prior_feedback_window_summary.sustained_spike_flags,
        prior_brake_state=_prior_runtime_brake_state(prior_session.brake_history),
    )
    executive_state = build_reference_executive_state(
        bound_event.observation,
        support_snapshot,
        _coerce_executive_environment_view(
            executive_environment_view,
            normalized_payload=normalized_payload,
        ),
        provisional_session,
        opportunities=opportunities,
        audit_intensity=audit_intensity,
        task_mode=runtime_task_mode,
        debt_control_pressure=debt_control,
    )
    recent_probe_failure_class = recent_probe_failure_class_from_feedback_window(
        prior_session.feedback_window
    )
    memory_priors = None
    if offline_publication is not None:
        from cortex.aux.publication import (
            OfflineSupportPublication as _OfflineSupportPublication,
            augment_snapshot_with_offline_publication,
        )
        from cortex.aux.support_priors import (
            build_support_memory_prior_appendix,
            filter_live_support_memory_prior_appendix,
        )

        if not isinstance(offline_publication, _OfflineSupportPublication):
            actual_type = type(offline_publication).__name__
            raise TypeError(
                "run_reference_runtime_step.offline_publication must be "
                f"OfflineSupportPublication | None, got {actual_type}."
            )
        memory_priors = filter_live_support_memory_prior_appendix(
            support_snapshot,
            build_support_memory_prior_appendix(
                augment_snapshot_with_offline_publication(
                    support_snapshot,
                    offline_publication,
                ),
                recent_probe_failure_class=recent_probe_failure_class,
            ),
            target_host_name="reference",
            recent_probe_failure_class=recent_probe_failure_class,
        )
    selection = select_reference_soft_control(
        executive_state,
        mediation_mode=mediation_mode,
        memory_priors=memory_priors,
        opportunities=opportunities,
    )
    selected_family = selection.selected_family
    brake_state = executive_state.brake.brake_state
    dominant_uncertainty_sources = _dominant_uncertainty_sources(executive_state)
    realized_family, enforcement_warnings = _realize_family(
        selected_family,
        brake_state=brake_state,
        dominant_uncertainty_sources=dominant_uncertainty_sources,
        feedback_pressure_tags=executive_state.control_allocation.feedback_pressure_tags,
        seek_context_opportunity_available=_has_realizable_seek_context_opportunity(
            opportunities
        ),
    )
    warnings = merge_warnings(warnings, enforcement_warnings)
    allocation_diagnostics = build_allocation_diagnostics_payload(
        selection.scorecard,
        selected_delta_over_neutral=selection.neutral_dominance.margin_over_neutral,
        applied_activation_threshold=selection.neutral_dominance.activation_threshold,
        chi_t=selection.chi_t,
        rejected_cheaper_families=scorecard_rejected_cheaper_families(
            selection.scorecard,
            selected_family=selected_family,
        ),
        probe_path_state=executive_state.control_allocation.probe_path_state,
        probe_unavailable_reason=(
            executive_state.control_allocation.probe_unavailable_reason
        ),
        probe_result_class=probe_result_class_for_runtime(
            realized_family=realized_family,
            executive_state=executive_state,
            opportunities=opportunities,
        ),
        verification_state=verification_state_for_runtime(
            dispatch_decision=dispatch_decision,
            commitment_result_kind=commitment_result_kind,
        ),
        explainability_profile=executive_state.control_allocation.explainability_profile,
        anti_thrash_state=executive_state.control_allocation.anti_thrash_state,
        repetition_target_family=(
            executive_state.control_allocation.repetition_target_family
        ),
        repetition_tax=executive_state.control_allocation.repetition_tax,
        anti_thrash_reason_tags=(
            executive_state.control_allocation.anti_thrash_reason_tags
        ),
        mediation_payload=selection.mediation_finalization.as_payload(),
        risk_weight=executive_state.control_allocation.risk_weight,
        brake_tonic=executive_state.brake.tonic,
    )
    allocation_diagnostics = {
        "alpha_t": allocation_diagnostics["alpha_t"],
        "activation_threshold": allocation_diagnostics["activation_threshold"],
        "selected_delta_over_neutral": allocation_diagnostics["selected_delta_over_neutral"],
        "chi_t": allocation_diagnostics["chi_t"],
        "risk_weight": allocation_diagnostics["risk_weight"],
        "brake_tonic": allocation_diagnostics["brake_tonic"],
        "debt_control": debt_control.as_payload(),
        "rejected_cheaper_families": allocation_diagnostics["rejected_cheaper_families"],
        "probe_path_state": allocation_diagnostics["probe_path_state"],
        "probe_unavailable_reason": allocation_diagnostics["probe_unavailable_reason"],
        "probe_result_class": allocation_diagnostics["probe_result_class"],
        "verification_state": allocation_diagnostics["verification_state"],
        "explainability_profile": allocation_diagnostics["explainability_profile"],
        "anti_thrash": allocation_diagnostics["anti_thrash"],
        "memory_reentry": _build_memory_reentry_diagnostics_payload(
            memory_priors,
            selected_family=selected_family,
            allocation_diagnostics=allocation_diagnostics,
            target_host_name="reference",
        ),
        "scores": allocation_diagnostics["scores"],
        "mediation": allocation_diagnostics["mediation"],
    }
    audit_projection = None
    if _should_emit_audit_projection(
        executive_state.control_allocation.explainability_profile
    ):
        audit_projection = build_audit_projection_payload(
            selected_family=selected_family,
            realized_family=realized_family,
            dominant_uncertainty_sources=dominant_uncertainty_sources,
            allocation_diagnostics=allocation_diagnostics,
        )
    control_ledger = ReferenceControlLedger(
        event_class=dispatch_decision.lane.value,
        admissible_families=_admissible_families(executive_state),
        selected_family=selected_family,
        realized_family=realized_family,
        dominant_uncertainty_sources=dominant_uncertainty_sources,
        brake_state=brake_state,
        budget_band=executive_state.control_allocation.budget_band,
        primary_reason=_primary_reason(warnings),
        allocation_diagnostics=allocation_diagnostics,
        audit_projection=audit_projection,
    )
    progress_signal = classify_runtime_progress_signal(
        dispatch_decision=dispatch_decision,
        normalized_payload=normalized_payload,
        commitment_result_kind=commitment_result_kind,
        prior_session=prior_session,
        provisional_session=provisional_session,
    )
    realization_feedback = build_shared_realization_feedback(
        task_mode=runtime_task_mode,
        selected_family=selected_family,
        realized_family=realized_family,
        brake_state=brake_state,
        commitment_result_kind=commitment_result_kind,
        warning_codes=tuple(warnings),
        host_friction_tags=tuple(
            sorted(executive_state.control_allocation.host_friction_tags)
        ),
        progress_signal=progress_signal,
        probe_result_class=probe_result_class_for_runtime(
            realized_family=realized_family,
            executive_state=executive_state,
            opportunities=opportunities,
        ),
    )
    expectation_ledger = update_expectation_ledger_for_structured_step(
        ledger=prior_session.expectation_ledger,
        dispatch_decision=dispatch_decision,
        current_step=provisional_session.event_index,
        source_event_ref=f"reference:{provisional_session.event_index}",
        evidence_progress_class=realization_feedback.evidence_progress_class,
        continuity_progress_class=realization_feedback.continuity_progress_class,
        commitment_result_kind=commitment_result_kind,
        task_mode=runtime_task_mode.value,
        warning_codes=tuple(warnings),
    )
    updated_session = ReferenceRuntimeSession(
        session_id=provisional_session.session_id,
        event_index=provisional_session.event_index,
        branch_registry=provisional_session.branch_registry,
        active_track_ref=provisional_session.active_track_ref,
        pending_goal_refs=provisional_session.pending_goal_refs,
        continuity_reminders=provisional_session.continuity_reminders,
        budget_history=provisional_session.budget_history,
        brake_history=prior_session.brake_history + (brake_state.value,),
        brake_tonic_history=_bounded_tonic_history(
            prior_session.brake_tonic_history, executive_state.brake.tonic
        ),
        last_selected_family=selected_family,
        last_commitment_result_summary=_commitment_summary_for_lane(
            dispatch_decision.lane,
            commitment_result_kind,
        ),
        last_realization_feedback=realization_feedback,
        feedback_window=prior_session.feedback_window.append(realization_feedback),
        expectation_ledger=expectation_ledger,
        executive_modulator_memory=prior_session.executive_modulator_memory,
    )
    executive_summary_inputs = build_runtime_executive_signal_summary_inputs(
        task_mode=runtime_task_mode,
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
        recent_probe_failure_class=recent_probe_failure_class,
        recent_warning_bearing_success_present=recent_warning_bearing_success_present(
            prior_session.feedback_window,
            failed_before_completion=False,
        ),
        preservation_active=False,
    )
    executive_signal_summary = build_executive_signal_summary(executive_summary_inputs)
    assert_runtime_posture_alignment(
        runtime_task_mode=runtime_task_mode,
        executive_state=executive_state,
        executive_signal_summary=executive_signal_summary,
    )
    executive_modulator_update = update_executive_modulators(
        executive_signal_summary,
        previous=prior_session.executive_modulator_memory,
    )
    executive_policy_view = build_executive_policy_view(
        executive_signal_summary,
        executive_modulator_update.state,
        chi_t=selection.chi_t,
        debt_control_pressure=debt_control,
    )
    operator_task_state = build_runtime_operator_task_state(
        summary_inputs=executive_summary_inputs,
        executive_state=executive_state,
    )
    operator_route = select_operator_route_with_policy(
        operator_task_state,
        executive_modulator_update,
        executive_policy_view,
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
    updated_session = ReferenceRuntimeSession(
        session_id=updated_session.session_id,
        event_index=updated_session.event_index,
        branch_registry=updated_session.branch_registry,
        active_track_ref=updated_session.active_track_ref,
        pending_goal_refs=updated_session.pending_goal_refs,
        continuity_reminders=updated_session.continuity_reminders,
        budget_history=updated_session.budget_history,
        brake_history=updated_session.brake_history,
        brake_tonic_history=updated_session.brake_tonic_history,
        last_selected_family=updated_session.last_selected_family,
        last_commitment_result_summary=updated_session.last_commitment_result_summary,
        last_realization_feedback=updated_session.last_realization_feedback,
        feedback_window=updated_session.feedback_window,
        expectation_ledger=updated_session.expectation_ledger,
        executive_modulator_memory=canonicalize_executive_modulator_memory(
            executive_modulator_update.next_memory
        ),
    )
    post_feedback_window_summary = summarize_reference_feedback_window(
        updated_session.feedback_window
    )
    resolution_deficit = updated_session.expectation_ledger.resolution_deficit(
        current_step=updated_session.event_index
    )
    assert_post_step_feedback_window_alignment(
        feedback_window=updated_session.feedback_window,
        last_realization_feedback=updated_session.last_realization_feedback,
        feedback_window_summary=post_feedback_window_summary,
    )
    return ReferenceRuntimeStepResult(
        event_index=updated_session.event_index,
        bound_event=bound_event,
        dispatch_decision=dispatch_decision,
        executive_state=executive_state,
        selected_family=selected_family,
        realized_family=realized_family,
        brake_state=brake_state,
        control_ledger=control_ledger,
        feedback_window_summary=post_feedback_window_summary,
        resolution_deficit=resolution_deficit,
        debt_control=debt_control,
        executive_signal_summary=executive_signal_summary,
        executive_modulator_state=executive_modulator_update.state,
        executive_policy_view=executive_policy_view,
        operator_task_state=operator_task_state,
        operator_route=operator_route,
        closure_required=closure_required,
        closure_reason_tags=closure_reason_tags_value,
        warnings=warnings,
        session=updated_session,
        commitment_result_kind=commitment_result_kind,
    )


def _coerce_session(session: ReferenceRuntimeSession | None) -> ReferenceRuntimeSession:
    if session is None:
        return ReferenceRuntimeSession()
    if not isinstance(session, ReferenceRuntimeSession):
        actual_type = type(session).__name__
        raise TypeError(
            "run_reference_runtime_step.session must be ReferenceRuntimeSession | None, "
            f"got {actual_type}."
        )
    return session


def _prior_runtime_brake_state(brake_history: tuple[str, ...]) -> BrakeState | None:
    if not brake_history:
        return None
    return BrakeState(brake_history[-1])


def _resolve_session_id(
    prior_session: ReferenceRuntimeSession,
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
    prior_session: ReferenceRuntimeSession,
    normalized_payload: Mapping[str, Any],
) -> tuple[tuple[str, ...], str, tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    operation = _branch_operation(normalized_payload)
    branch_registry = list(prior_session.branch_registry)
    active_track_ref = prior_session.active_track_ref
    pending_goal_refs = list(prior_session.pending_goal_refs)
    continuity_reminders = list(prior_session.continuity_reminders)
    branch_track_ref = _continuity_track_ref(normalized_payload)
    payload_goal_refs = _pending_goal_refs_from_payload(normalized_payload)
    warnings: tuple[str, ...] = ()

    if operation is None:
        if payload_goal_refs:
            pending_goal_refs = _merge_unique_refs(tuple(pending_goal_refs), payload_goal_refs)
        return (
            tuple(branch_registry),
            active_track_ref,
            tuple(pending_goal_refs),
            warnings,
            tuple(continuity_reminders),
        )

    if operation is BranchOperation.OPEN:
        if branch_track_ref is None:
            warnings = ("continuity-rejected:missing-open-track-ref",)
            return (
                tuple(prior_session.branch_registry),
                prior_session.active_track_ref,
                tuple(prior_session.pending_goal_refs),
                warnings,
                tuple(prior_session.continuity_reminders),
            )
        if branch_track_ref not in branch_registry:
            branch_registry.append(branch_track_ref)
        active_track_ref = branch_track_ref
        continuity_reminders = list(
            _without_track_reminders(continuity_reminders, branch_track_ref)
        )
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
                tuple(prior_session.continuity_reminders),
            )
        active_track_ref = "main"
        continuity_reminders = list(
            _merge_distinct_strings(
                _without_track_reminders(continuity_reminders, branch_track_ref),
                (make_resume_reminder(branch_track_ref),),
            )
        )
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
                tuple(prior_session.continuity_reminders),
            )
        if branch_track_ref not in pending_goal_refs:
            warnings = (_continuity_warning("missing-resume-anchor", branch_track_ref),)
            continuity_reminders = list(
                _merge_distinct_strings(
                    _without_track_reminders(continuity_reminders, branch_track_ref),
                    (make_resume_reminder(branch_track_ref), "resume-anchor-missing"),
                )
            )
            return (
                tuple(prior_session.branch_registry),
                prior_session.active_track_ref,
                tuple(prior_session.pending_goal_refs),
                warnings,
                tuple(continuity_reminders),
            )
        active_track_ref = branch_track_ref
        continuity_reminders = list(
            _without_track_reminders(continuity_reminders, branch_track_ref)
        )
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
                tuple(prior_session.continuity_reminders),
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
                tuple(prior_session.continuity_reminders),
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
                tuple(prior_session.continuity_reminders),
            )
        branch_registry = [
            branch_ref for branch_ref in branch_registry if branch_ref != branch_track_ref
        ]
        if not branch_registry:
            branch_registry = ["main"]
        active_track_ref = merge_target_ref or "main"
        continuity_reminders = list(
            _without_track_reminders(continuity_reminders, branch_track_ref)
        )
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
        tuple(continuity_reminders),
    )


def _merge_distinct_strings(
    existing: tuple[str, ...],
    additions: tuple[str, ...],
) -> tuple[str, ...]:
    ordered = list(existing)
    for value in additions:
        if value not in ordered:
            ordered.append(value)
    return tuple(ordered)


def _without_track_reminders(
    reminders: list[str],
    track_ref: str | None,
) -> tuple[str, ...]:
    if track_ref is None:
        return tuple(
            reminder for reminder in reminders if reminder != "resume-anchor-missing"
        )
    return tuple(
        reminder
        for reminder in reminders
        if reminder != "resume-anchor-missing"
        and parse_resume_reminder_track(reminder) != track_ref
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
        "reference-host",
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


def _coerce_executive_environment_view(
    executive_environment_view: ExecutiveEnvironmentView | None,
    *,
    normalized_payload: Mapping[str, Any],
) -> ExecutiveEnvironmentView:
    if executive_environment_view is None:
        return _build_executive_environment_view(normalized_payload)
    if not isinstance(executive_environment_view, ExecutiveEnvironmentView):
        actual_type = type(executive_environment_view).__name__
        raise TypeError(
            "run_reference_runtime_step.executive_environment_view must be "
            f"ExecutiveEnvironmentView | None, got {actual_type}."
        )
    return executive_environment_view


def _build_support_snapshot(
    *,
    provisional_session: ReferenceRuntimeSession,
    bound_event: BoundReferenceHostEvent,
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


def _reference_host_native_opportunities(
    bound_event: BoundReferenceHostEvent,
) -> tuple[HostNativeOpportunity, ...]:
    opportunities: list[HostNativeOpportunity] = []
    if "mcp.query" in bound_event.lifecycle_surface.mcp_affordances:
        opportunities.append(
            HostNativeOpportunity(
                opportunity_ref="mcp.query.probe",
                supported_families=frozenset({SoftControlFamily.CHECK}),
                clearly_superior=True,
                native_surface_tags=frozenset({"mcp", "bounded-probe"}),
                probe_contract=BoundedProbeContract(
                    uncertainty_target="environment",
                    allowed_family=SoftControlFamily.CHECK,
                    timeout_seconds=2,
                    output_cap=64,
                    failure_classes=frozenset({"timed-out", "degraded", "unsupported"}),
                ),
            )
        )
        opportunities.append(
            HostNativeOpportunity(
                opportunity_ref="mcp.query",
                supported_families=frozenset({SoftControlFamily.SEEK_CONTEXT}),
                clearly_superior=True,
                native_surface_tags=frozenset({"mcp", "structured-query"}),
                probe_contract=BoundedProbeContract(
                    uncertainty_target="host-capability",
                    allowed_family=SoftControlFamily.SEEK_CONTEXT,
                    timeout_seconds=5,
                    output_cap=256,
                    failure_classes=frozenset({"timed-out", "degraded", "unsupported"}),
                ),
            )
        )
    return tuple(opportunities)


def _build_provenance_manifest(
    normalized_payload: Mapping[str, Any],
) -> ProvenanceManifest | None:
    evidence_refs: list[ProvenanceEvidenceRef] = []

    artifact_ref = _first_concrete_artifact_ref(normalized_payload)
    if artifact_ref is not None:
        evidence_refs.append(
            ProvenanceEvidenceRef(
                source_family="result_artifact",
                reference_id=artifact_ref,
            )
        )

    external_record_ref = _as_non_empty_string(normalized_payload.get("external_record_ref"))
    if external_record_ref is not None:
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


_MAX_TONIC_HISTORY = 16


def _bounded_tonic_history(
    prior: tuple[float, ...],
    tonic: "BrakeTonic | None",
) -> tuple[float, ...]:
    from cortex.sre.brake import BrakeTonic

    if tonic is None or not isinstance(tonic, BrakeTonic):
        return prior[-_MAX_TONIC_HISTORY:] if len(prior) > _MAX_TONIC_HISTORY else prior
    updated = prior + (tonic.tonic_pressure,)
    return updated[-_MAX_TONIC_HISTORY:]


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
    seek_context_opportunity_available: bool,
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
        if any(
            source in {"evidence", "environment"}
            for source in dominant_uncertainty_sources
        ):
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

    if (
        selected_family is SoftControlFamily.SEEK_CONTEXT
        and seek_context_opportunity_available
        and any(
            source in {"evidence", "environment", "host-capability"}
            for source in dominant_uncertainty_sources
        )
    ):
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


def _has_realizable_seek_context_opportunity(
    opportunities: tuple[HostNativeOpportunity, ...],
) -> bool:
    return any(
        opportunity.realizable
        and opportunity.clearly_superior
        and SoftControlFamily.SEEK_CONTEXT in opportunity.supported_families
        for opportunity in opportunities
    )


def _primary_reason(warnings: tuple[str, ...]) -> str | None:
    for warning in warnings:
        if warning.startswith(
            ("latched-brake-enforced:", "guarded-feedback-enforced:")
        ):
            return warning
    return warnings[0] if warnings else None


def _metadata_str_from_fields(
    metadata: tuple[Any, ...],
    key: str,
) -> str | None:
    for field in metadata:
        if getattr(field, "key", None) != key:
            continue
        value = getattr(field, "value", None)
        if value is None:
            return None
        return str(value)
    return None


def _score_memory_value(
    allocation_diagnostics: dict[str, Any],
    family: SoftControlFamily,
) -> float:
    for score in allocation_diagnostics["scores"]:
        if score["family"] == family.value:
            return float(score["memory_score"])
    raise KeyError(f"Missing allocation score for family {family.value!r}.")


def _support_ref_payload(
    memory_priors: Any,
    selected_family: SoftControlFamily,
) -> list[dict[str, str]]:
    if memory_priors is None:
        return []
    score = memory_priors.score_for(selected_family)
    if float(score.score) <= 0.0:
        return []
    return [
        {
            "reference_kind": reference.reference_kind,
            "reference_id": reference.reference_id,
        }
        for reference in score.support_refs
    ]


def _build_memory_reentry_diagnostics_payload(
    memory_priors: Any,
    *,
    selected_family: SoftControlFamily,
    allocation_diagnostics: dict[str, Any],
    target_host_name: str,
) -> dict[str, Any]:
    if memory_priors is None:
        return {
            "state": "inactive",
            "source_host_name": None,
            "target_host_name": target_host_name,
            "eligible_families": [],
            "invalidated_families": [],
            "selected_family_support_refs": [],
            "selected_family_memory_score": 0.0,
            "selected_family_reliability_delta": 0.0,
        }

    state = _metadata_str_from_fields(memory_priors.metadata, "live_reentry_state")
    source_host_name = _metadata_str_from_fields(
        memory_priors.metadata,
        "live_source_host_name",
    )
    invalidated_families = sorted(
        score.family.value
        for score in memory_priors.scores
        if any(
            tag.startswith("q_mem-live:invalidated:")
            for tag in score.reason_tags
        )
    )
    return {
        "state": state or ("active" if memory_priors.active else "inactive"),
        "source_host_name": source_host_name,
        "target_host_name": target_host_name,
        "eligible_families": [
            SoftControlFamily.CHECK.value,
            SoftControlFamily.SEEK_CONTEXT.value,
            SoftControlFamily.BRANCH.value,
            SoftControlFamily.REDIRECT.value,
        ],
        "invalidated_families": invalidated_families,
        "selected_family_support_refs": _support_ref_payload(
            memory_priors,
            selected_family,
        ),
        "selected_family_memory_score": _score_memory_value(
            allocation_diagnostics,
            selected_family,
        ),
        "selected_family_reliability_delta": _reliability_delta_for_family(
            memory_priors,
            selected_family,
        ),
    }


def _reliability_delta_for_family(
    memory_priors: Any,
    family: SoftControlFamily,
) -> float:
    for score in memory_priors.scores:
        if score.family is not family:
            continue
        for field in score.metadata:
            if field.key != "q_mem-host:reliability_delta":
                continue
            try:
                return float(field.value)
            except (TypeError, ValueError):
                return 0.0
    return 0.0


_ALLOCATION_DIAGNOSTICS_KEYS = (
    "alpha_t",
    "activation_threshold",
    "selected_delta_over_neutral",
    "chi_t",
    "risk_weight",
    "brake_tonic",
    "debt_control",
    "rejected_cheaper_families",
    "probe_path_state",
    "probe_unavailable_reason",
    "probe_result_class",
    "verification_state",
    "explainability_profile",
    "anti_thrash",
    "memory_reentry",
    "scores",
    "mediation",
)
_RISK_WEIGHT_DIAGNOSTICS_KEYS = (
    "fn_cost_weight",
    "fp_cost_weight",
    "adjustment_sign",
    "dominant_risk_source",
)
_BRAKE_TONIC_DIAGNOSTICS_KEYS = (
    "tonic_pressure",
)
_DEBT_CONTROL_DIAGNOSTICS_KEYS = (
    "resolution_pressure",
    "persistence",
    "forward_commit_pressure",
    "goal_drag",
    "debt_pressure",
    "verification_relief_bias",
    "reason_tags",
)
_ANTI_THRASH_DIAGNOSTICS_KEYS = (
    "state",
    "target_family",
    "repetition_tax",
    "reason_tags",
)
_MEMORY_REENTRY_DIAGNOSTICS_KEYS = (
    "state",
    "source_host_name",
    "target_host_name",
    "eligible_families",
    "invalidated_families",
    "selected_family_support_refs",
    "selected_family_memory_score",
    "selected_family_reliability_delta",
)
_MEMORY_REENTRY_REF_KEYS = ("reference_kind", "reference_id")
_ALLOCATION_SCORE_KEYS = (
    "family",
    "online_score",
    "memory_score",
    "allocated_score",
    "activation_threshold",
    "admissible",
    "reason_tags",
)
_MEDIATION_DIAGNOSTICS_KEYS = (
    "mediation_active",
    "mediation_identity",
    "selected_family_before_finalization",
    "selected_family_after_finalization",
    "preferred_opportunity_ref",
    "direct_opportunity_specialization_used",
    "mediation_reason_tags",
)
_AUDIT_PROJECTION_KEYS = (
    "selected_family",
    "realized_family",
    "dominant_uncertainty_sources",
    "activation_threshold",
    "selected_delta_over_neutral",
    "rejected_cheaper_families",
    "verification_state",
    "explainability_profile",
    "probe_path_state",
    "probe_result_class",
    "probe_unavailable_reason",
)


def _validate_risk_weight_diagnostics_payload(
    payload: dict[str, Any], label: str
) -> None:
    if not isinstance(payload, dict):
        actual_type = type(payload).__name__
        raise TypeError(f"{label} must be dict[str, Any], got {actual_type}.")
    if tuple(payload) != _RISK_WEIGHT_DIAGNOSTICS_KEYS:
        raise ValueError(
            f"{label} must preserve the locked key order {_RISK_WEIGHT_DIAGNOSTICS_KEYS!r}."
        )
    for key in ("fn_cost_weight", "fp_cost_weight"):
        value = payload[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            actual_type = type(value).__name__
            raise TypeError(f"{label}.{key} must be numeric, got {actual_type}.")
        if not 0.0 <= float(value) <= 1.0:
            raise ValueError(f"{label}.{key} must be in [0.0, 1.0].")
    if payload["adjustment_sign"] not in {"balanced", "fn-heavy", "fp-heavy"}:
        raise ValueError(
            f"{label}.adjustment_sign must be one of ['balanced', 'fn-heavy', 'fp-heavy']."
        )
    dominant = payload["dominant_risk_source"]
    if dominant is not None and not (isinstance(dominant, str) and dominant.strip()):
        raise ValueError(
            f"{label}.dominant_risk_source must be non-empty after trimming when provided."
        )


def _validate_brake_tonic_diagnostics_payload(
    payload: dict[str, Any] | None, label: str
) -> None:
    if payload is None:
        return
    if not isinstance(payload, dict):
        actual_type = type(payload).__name__
        raise TypeError(f"{label} must be dict[str, Any] | None, got {actual_type}.")
    if tuple(payload) != _BRAKE_TONIC_DIAGNOSTICS_KEYS:
        raise ValueError(
            f"{label} must preserve the locked key order {_BRAKE_TONIC_DIAGNOSTICS_KEYS!r}."
        )
    for key in ("tonic_pressure",):
        value = payload[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            actual_type = type(value).__name__
            raise TypeError(f"{label}.{key} must be numeric, got {actual_type}.")
        if not 0.0 <= float(value) <= 1.0:
            raise ValueError(f"{label}.{key} must be in [0.0, 1.0].")


def _validate_debt_control_diagnostics_payload(payload: dict[str, Any], label: str) -> None:
    if not isinstance(payload, dict):
        actual_type = type(payload).__name__
        raise TypeError(f"{label} must be dict[str, Any], got {actual_type}.")
    if tuple(payload) != _DEBT_CONTROL_DIAGNOSTICS_KEYS:
        raise ValueError(
            f"{label} must preserve the locked key order {_DEBT_CONTROL_DIAGNOSTICS_KEYS!r}."
        )
    for key in _DEBT_CONTROL_DIAGNOSTICS_KEYS[:-1]:
        value = payload[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            actual_type = type(value).__name__
            raise TypeError(f"{label}.{key} must be numeric, got {actual_type}.")
        if not 0.0 <= float(value) <= 1.0:
            raise ValueError(f"{label}.{key} must be in [0.0, 1.0].")
    reason_tags = payload["reason_tags"]
    if not isinstance(reason_tags, list):
        actual_type = type(reason_tags).__name__
        raise TypeError(f"{label}.reason_tags must be list[str], got {actual_type}.")
    if any(not (isinstance(tag, str) and tag.strip()) for tag in reason_tags):
        raise ValueError(f"{label}.reason_tags must contain only non-empty strings.")


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
    _validate_risk_weight_diagnostics_payload(payload["risk_weight"], f"{label}.risk_weight")
    _validate_brake_tonic_diagnostics_payload(payload["brake_tonic"], f"{label}.brake_tonic")
    _validate_debt_control_diagnostics_payload(
        payload["debt_control"], f"{label}.debt_control"
    )
    rejected_cheaper_families = payload["rejected_cheaper_families"]
    if not isinstance(rejected_cheaper_families, list):
        actual_type = type(rejected_cheaper_families).__name__
        raise TypeError(
            f"{label}.rejected_cheaper_families must be list[str], got {actual_type}."
        )
    if any(
        not (isinstance(family, str) and family.strip())
        for family in rejected_cheaper_families
    ):
        raise ValueError(
            f"{label}.rejected_cheaper_families must contain only non-empty strings."
        )
    if payload["probe_path_state"] not in {"available", "unavailable", "absent"}:
        raise ValueError(
            f"{label}.probe_path_state must be one of ['absent', 'available', 'unavailable']."
        )
    probe_unavailable_reason = payload["probe_unavailable_reason"]
    if probe_unavailable_reason is not None and not (
        isinstance(probe_unavailable_reason, str) and probe_unavailable_reason.strip()
    ):
        raise ValueError(
            f"{label}.probe_unavailable_reason must be non-empty after trimming when provided."
        )
    if payload["probe_path_state"] == "unavailable" and probe_unavailable_reason is None:
        raise ValueError(
            f"{label}.probe_unavailable_reason is required when probe_path_state is `unavailable`."
        )
    if payload["probe_path_state"] != "unavailable" and probe_unavailable_reason is not None:
        raise ValueError(
            f"{label}.probe_unavailable_reason is only valid when probe_path_state is `unavailable`."
        )
    probe_result_class = payload["probe_result_class"]
    if probe_result_class is not None and not (
        isinstance(probe_result_class, str) and probe_result_class.strip()
    ):
        raise ValueError(
            f"{label}.probe_result_class must be non-empty after trimming when provided."
        )
    for key in ("verification_state", "explainability_profile"):
        value = payload[key]
        if not (isinstance(value, str) and value.strip()):
            raise ValueError(f"{label}.{key} must be non-empty after trimming.")
    anti_thrash = payload["anti_thrash"]
    if not isinstance(anti_thrash, dict):
        actual_type = type(anti_thrash).__name__
        raise TypeError(f"{label}.anti_thrash must be dict[str, Any], got {actual_type}.")
    if tuple(anti_thrash) != _ANTI_THRASH_DIAGNOSTICS_KEYS:
        raise ValueError(
            f"{label}.anti_thrash must preserve the locked key order {_ANTI_THRASH_DIAGNOSTICS_KEYS!r}."
        )
    if anti_thrash["state"] not in {"inactive", "taxed", "reopened"}:
        raise ValueError(
            f"{label}.anti_thrash.state must be one of ['inactive', 'taxed', 'reopened']."
        )
    target_family = anti_thrash["target_family"]
    if target_family is not None and not (
        isinstance(target_family, str) and target_family.strip()
    ):
        raise ValueError(
            f"{label}.anti_thrash.target_family must be non-empty after trimming when provided."
        )
    repetition_tax = anti_thrash["repetition_tax"]
    if isinstance(repetition_tax, bool) or not isinstance(repetition_tax, (int, float)):
        actual_type = type(repetition_tax).__name__
        raise TypeError(
            f"{label}.anti_thrash.repetition_tax must be numeric, got {actual_type}."
        )
    reason_tags = anti_thrash["reason_tags"]
    if not isinstance(reason_tags, list):
        actual_type = type(reason_tags).__name__
        raise TypeError(
            f"{label}.anti_thrash.reason_tags must be list[str], got {actual_type}."
        )
    if any(not (isinstance(tag, str) and tag.strip()) for tag in reason_tags):
        raise ValueError(
            f"{label}.anti_thrash.reason_tags must contain only non-empty values after trimming."
        )
    memory_reentry = payload["memory_reentry"]
    if not isinstance(memory_reentry, dict):
        actual_type = type(memory_reentry).__name__
        raise TypeError(
            f"{label}.memory_reentry must be dict[str, Any], got {actual_type}."
        )
    if tuple(memory_reentry) != _MEMORY_REENTRY_DIAGNOSTICS_KEYS:
        raise ValueError(
            f"{label}.memory_reentry must preserve the locked key order "
            f"{_MEMORY_REENTRY_DIAGNOSTICS_KEYS!r}."
        )
    if memory_reentry["state"] not in {"inactive", "active", "host-mismatch"}:
        raise ValueError(
            f"{label}.memory_reentry.state must be one of ['active', 'host-mismatch', 'inactive']."
        )
    source_host_name = memory_reentry["source_host_name"]
    if source_host_name is not None and not (
        isinstance(source_host_name, str) and source_host_name.strip()
    ):
        raise ValueError(
            f"{label}.memory_reentry.source_host_name must be non-empty after trimming when provided."
        )
    target_host_name = memory_reentry["target_host_name"]
    if not (isinstance(target_host_name, str) and target_host_name.strip()):
        raise ValueError(
            f"{label}.memory_reentry.target_host_name must be non-empty after trimming."
        )
    for key in ("eligible_families", "invalidated_families"):
        value = memory_reentry[key]
        if not isinstance(value, list):
            actual_type = type(value).__name__
            raise TypeError(
                f"{label}.memory_reentry.{key} must be list[str], got {actual_type}."
            )
        if any(not (isinstance(entry, str) and entry.strip()) for entry in value):
            raise ValueError(
                f"{label}.memory_reentry.{key} must contain only non-empty strings."
            )
    selected_family_support_refs = memory_reentry["selected_family_support_refs"]
    if not isinstance(selected_family_support_refs, list):
        actual_type = type(selected_family_support_refs).__name__
        raise TypeError(
            f"{label}.memory_reentry.selected_family_support_refs must be list[dict[str, str]], got {actual_type}."
        )
    for index, reference_payload in enumerate(selected_family_support_refs):
        reference_label = f"{label}.memory_reentry.selected_family_support_refs[{index}]"
        if not isinstance(reference_payload, dict):
            actual_type = type(reference_payload).__name__
            raise TypeError(
                f"{reference_label} must be dict[str, str], got {actual_type}."
            )
        if tuple(reference_payload) != _MEMORY_REENTRY_REF_KEYS:
            raise ValueError(
                f"{reference_label} must preserve the locked key order "
                f"{_MEMORY_REENTRY_REF_KEYS!r}."
            )
        for ref_key in _MEMORY_REENTRY_REF_KEYS:
            ref_value = reference_payload[ref_key]
            if not (isinstance(ref_value, str) and ref_value.strip()):
                raise ValueError(
                    f"{reference_label}.{ref_key} must be non-empty after trimming."
                )
    selected_family_memory_score = memory_reentry["selected_family_memory_score"]
    if isinstance(selected_family_memory_score, bool) or not isinstance(
        selected_family_memory_score,
        (int, float),
    ):
        actual_type = type(selected_family_memory_score).__name__
        raise TypeError(
            f"{label}.memory_reentry.selected_family_memory_score must be numeric, got {actual_type}."
        )
    selected_family_reliability_delta = memory_reentry["selected_family_reliability_delta"]
    if isinstance(selected_family_reliability_delta, bool) or not isinstance(
        selected_family_reliability_delta,
        (int, float),
    ):
        actual_type = type(selected_family_reliability_delta).__name__
        raise TypeError(
            f"{label}.memory_reentry.selected_family_reliability_delta must be numeric, got {actual_type}."
        )
    if not isfinite(float(selected_family_reliability_delta)):
        raise ValueError(
            f"{label}.memory_reentry.selected_family_reliability_delta must be finite."
        )
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
    mediation = payload["mediation"]
    if not isinstance(mediation, dict):
        actual_type = type(mediation).__name__
        raise TypeError(f"{label}.mediation must be dict[str, Any], got {actual_type}.")
    if tuple(mediation) != _MEDIATION_DIAGNOSTICS_KEYS:
        raise ValueError(
            f"{label}.mediation must preserve the locked key order "
            f"{_MEDIATION_DIAGNOSTICS_KEYS!r}."
        )
    if not isinstance(mediation["mediation_active"], bool):
        actual_type = type(mediation["mediation_active"]).__name__
        raise TypeError(
            f"{label}.mediation.mediation_active must be bool, got {actual_type}."
        )
    if not isinstance(mediation["mediation_identity"], bool):
        actual_type = type(mediation["mediation_identity"]).__name__
        raise TypeError(
            f"{label}.mediation.mediation_identity must be bool, got {actual_type}."
        )
    for key in (
        "selected_family_before_finalization",
        "selected_family_after_finalization",
    ):
        value = mediation[key]
        if not (isinstance(value, str) and value.strip()):
            raise ValueError(f"{label}.mediation.{key} must be non-empty after trimming.")
    preferred_opportunity_ref = mediation["preferred_opportunity_ref"]
    if preferred_opportunity_ref is not None and not (
        isinstance(preferred_opportunity_ref, str) and preferred_opportunity_ref.strip()
    ):
        raise ValueError(
            f"{label}.mediation.preferred_opportunity_ref must be non-empty after trimming when provided."
        )
    if not isinstance(mediation["direct_opportunity_specialization_used"], bool):
        actual_type = type(mediation["direct_opportunity_specialization_used"]).__name__
        raise TypeError(
            f"{label}.mediation.direct_opportunity_specialization_used must be bool, got {actual_type}."
        )
    mediation_reason_tags = mediation["mediation_reason_tags"]
    if not isinstance(mediation_reason_tags, list):
        actual_type = type(mediation_reason_tags).__name__
        raise TypeError(
            f"{label}.mediation.mediation_reason_tags must be list[str], got {actual_type}."
        )
    if any(
        not (isinstance(tag, str) and tag.strip()) for tag in mediation_reason_tags
    ):
        raise ValueError(
            f"{label}.mediation.mediation_reason_tags must contain only non-empty strings."
        )


def _validate_audit_projection_payload(payload: dict[str, Any], label: str) -> None:
    if not isinstance(payload, dict):
        actual_type = type(payload).__name__
        raise TypeError(f"{label} must be dict[str, Any], got {actual_type}.")
    if tuple(payload) != _AUDIT_PROJECTION_KEYS:
        raise ValueError(
            f"{label} must preserve the locked key order {_AUDIT_PROJECTION_KEYS!r}."
        )
    for key in (
        "selected_family",
        "realized_family",
        "verification_state",
        "explainability_profile",
        "probe_path_state",
    ):
        value = payload[key]
        if not (isinstance(value, str) and value.strip()):
            raise ValueError(f"{label}.{key} must be non-empty after trimming.")
    if payload["probe_path_state"] not in {"available", "unavailable", "absent"}:
        raise ValueError(
            f"{label}.probe_path_state must be one of ['absent', 'available', 'unavailable']."
        )
    for key in ("activation_threshold", "selected_delta_over_neutral"):
        value = payload[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            actual_type = type(value).__name__
            raise TypeError(f"{label}.{key} must be numeric, got {actual_type}.")
    dominant_uncertainty_sources = payload["dominant_uncertainty_sources"]
    if not isinstance(dominant_uncertainty_sources, list):
        actual_type = type(dominant_uncertainty_sources).__name__
        raise TypeError(
            f"{label}.dominant_uncertainty_sources must be list[str], got {actual_type}."
        )
    if any(
        not (isinstance(source, str) and source.strip())
        for source in dominant_uncertainty_sources
    ):
        raise ValueError(
            f"{label}.dominant_uncertainty_sources must contain only non-empty strings."
        )
    rejected_cheaper_families = payload["rejected_cheaper_families"]
    if not isinstance(rejected_cheaper_families, list):
        actual_type = type(rejected_cheaper_families).__name__
        raise TypeError(
            f"{label}.rejected_cheaper_families must be list[str], got {actual_type}."
        )
    if any(
        not (isinstance(family, str) and family.strip())
        for family in rejected_cheaper_families
    ):
        raise ValueError(
            f"{label}.rejected_cheaper_families must contain only non-empty strings."
        )
    probe_result_class = payload["probe_result_class"]
    if probe_result_class is not None and not (
        isinstance(probe_result_class, str) and probe_result_class.strip()
    ):
        raise ValueError(
            f"{label}.probe_result_class must be non-empty after trimming when provided."
        )
    probe_unavailable_reason = payload["probe_unavailable_reason"]
    if probe_unavailable_reason is not None and not (
        isinstance(probe_unavailable_reason, str) and probe_unavailable_reason.strip()
    ):
        raise ValueError(
            f"{label}.probe_unavailable_reason must be non-empty after trimming when provided."
        )


def _copy_allocation_diagnostics_payload(payload: dict[str, Any]) -> dict[str, Any]:
    risk_weight_payload = payload["risk_weight"]
    brake_tonic_payload = payload["brake_tonic"]
    return {
        "alpha_t": payload["alpha_t"],
        "activation_threshold": payload["activation_threshold"],
        "selected_delta_over_neutral": payload["selected_delta_over_neutral"],
        "chi_t": payload["chi_t"],
        "risk_weight": {
            "fn_cost_weight": risk_weight_payload["fn_cost_weight"],
            "fp_cost_weight": risk_weight_payload["fp_cost_weight"],
            "adjustment_sign": risk_weight_payload["adjustment_sign"],
            "dominant_risk_source": risk_weight_payload["dominant_risk_source"],
        },
        "brake_tonic": (
            None
            if brake_tonic_payload is None
            else {
                "tonic_pressure": brake_tonic_payload["tonic_pressure"],
            }
        ),
        "debt_control": {
            "resolution_pressure": payload["debt_control"]["resolution_pressure"],
            "persistence": payload["debt_control"]["persistence"],
            "forward_commit_pressure": payload["debt_control"]["forward_commit_pressure"],
            "goal_drag": payload["debt_control"]["goal_drag"],
            "debt_pressure": payload["debt_control"]["debt_pressure"],
            "verification_relief_bias": payload["debt_control"]["verification_relief_bias"],
            "reason_tags": list(payload["debt_control"]["reason_tags"]),
        },
        "rejected_cheaper_families": list(payload["rejected_cheaper_families"]),
        "probe_path_state": payload["probe_path_state"],
        "probe_unavailable_reason": payload["probe_unavailable_reason"],
        "probe_result_class": payload["probe_result_class"],
        "verification_state": payload["verification_state"],
        "explainability_profile": payload["explainability_profile"],
        "anti_thrash": {
            "state": payload["anti_thrash"]["state"],
            "target_family": payload["anti_thrash"]["target_family"],
            "repetition_tax": payload["anti_thrash"]["repetition_tax"],
            "reason_tags": list(payload["anti_thrash"]["reason_tags"]),
        },
        "memory_reentry": {
            "state": payload["memory_reentry"]["state"],
            "source_host_name": payload["memory_reentry"]["source_host_name"],
            "target_host_name": payload["memory_reentry"]["target_host_name"],
            "eligible_families": list(payload["memory_reentry"]["eligible_families"]),
            "invalidated_families": list(payload["memory_reentry"]["invalidated_families"]),
            "selected_family_support_refs": [
                {
                    "reference_kind": reference["reference_kind"],
                    "reference_id": reference["reference_id"],
                }
                for reference in payload["memory_reentry"]["selected_family_support_refs"]
            ],
            "selected_family_memory_score": payload["memory_reentry"][
                "selected_family_memory_score"
            ],
            "selected_family_reliability_delta": payload["memory_reentry"][
                "selected_family_reliability_delta"
            ],
        },
        "scores": [
            {
                "family": score["family"],
                "online_score": score["online_score"],
                "memory_score": score["memory_score"],
                "allocated_score": score["allocated_score"],
                "activation_threshold": score["activation_threshold"],
                "admissible": score["admissible"],
                "reason_tags": list(score["reason_tags"]),
            }
            for score in payload["scores"]
        ],
        "mediation": {
            "mediation_active": payload["mediation"]["mediation_active"],
            "mediation_identity": payload["mediation"]["mediation_identity"],
            "selected_family_before_finalization": payload["mediation"][
                "selected_family_before_finalization"
            ],
            "selected_family_after_finalization": payload["mediation"][
                "selected_family_after_finalization"
            ],
            "preferred_opportunity_ref": payload["mediation"]["preferred_opportunity_ref"],
            "direct_opportunity_specialization_used": payload["mediation"][
                "direct_opportunity_specialization_used"
            ],
            "mediation_reason_tags": list(payload["mediation"]["mediation_reason_tags"]),
        },
    }


def _copy_audit_projection_payload(payload: dict[str, Any]) -> dict[str, Any]:
    _validate_audit_projection_payload(
        payload,
        "_copy_audit_projection_payload.payload",
    )
    return {
        "selected_family": payload["selected_family"],
        "realized_family": payload["realized_family"],
        "dominant_uncertainty_sources": list(payload["dominant_uncertainty_sources"]),
        "activation_threshold": payload["activation_threshold"],
        "selected_delta_over_neutral": payload["selected_delta_over_neutral"],
        "rejected_cheaper_families": list(payload["rejected_cheaper_families"]),
        "verification_state": payload["verification_state"],
        "explainability_profile": payload["explainability_profile"],
        "probe_path_state": payload["probe_path_state"],
        "probe_result_class": payload["probe_result_class"],
        "probe_unavailable_reason": payload["probe_unavailable_reason"],
    }


def _should_emit_audit_projection(explainability_profile: str) -> bool:
    return explainability_profile in {"focused", "structured"}


__all__ = [
    "ReferenceControlLedger",
    "ReferenceRuntimeSession",
    "ReferenceRuntimeStepResult",
    "run_reference_runtime_step",
]
