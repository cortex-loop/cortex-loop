"""Reference-host runtime step composition over landed driver/core/SRE surfaces."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

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
    CAPABILITY_VIEW,
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
from cortex.sre.brake import BrakeState
from cortex.sre.families import SoftControlFamily
from cortex.sre.reference_builder import build_reference_executive_state
from cortex.sre.reference_scoring import select_reference_soft_control
from cortex.sre.state import ReferenceExecutiveState

_ALLOWED_COMMITMENT_RESULT_KINDS = frozenset(status.value for status in CommitmentStatus)


@dataclass(frozen=True, slots=True)
class ReferenceRuntimeSession:
    session_id: str | None = None
    event_index: int = 0
    branch_registry: tuple[str, ...] = ("main",)
    pending_goal_refs: tuple[str, ...] = ()
    budget_history: tuple[str, ...] = ()
    brake_history: tuple[str, ...] = ()
    last_selected_family: SoftControlFamily | None = None
    last_commitment_result_summary: str | None = None

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
        if any(not (isinstance(ref, str) and ref.strip()) for ref in self.pending_goal_refs):
            raise ValueError(
                "ReferenceRuntimeSession.pending_goal_refs must contain only non-empty values after trimming."
            )
        if any(not (isinstance(entry, str) and entry.strip()) for entry in self.budget_history):
            raise ValueError(
                "ReferenceRuntimeSession.budget_history must contain only non-empty values after trimming."
            )
        if any(not (isinstance(entry, str) and entry.strip()) for entry in self.brake_history):
            raise ValueError(
                "ReferenceRuntimeSession.brake_history must contain only non-empty values after trimming."
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

    def as_summary(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "event_index": self.event_index,
            "branch_registry": list(self.branch_registry),
            "pending_goal_refs": list(self.pending_goal_refs),
            "budget_history": list(self.budget_history),
            "brake_history": list(self.brake_history),
            "last_selected_family": (
                self.last_selected_family.value
                if self.last_selected_family is not None
                else None
            ),
            "last_commitment_result_summary": self.last_commitment_result_summary,
        }


@dataclass(frozen=True, slots=True)
class ReferenceRuntimeStepResult:
    event_index: int
    bound_event: BoundReferenceHostEvent
    dispatch_decision: DispatchDecision
    executive_state: ReferenceExecutiveState
    selected_family: SoftControlFamily
    brake_state: BrakeState
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
        if not isinstance(self.brake_state, BrakeState):
            actual_type = type(self.brake_state).__name__
            raise TypeError(
                "ReferenceRuntimeStepResult.brake_state must be BrakeState, "
                f"got {actual_type}."
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


def run_reference_runtime_step(
    raw_event_name: str,
    raw_payload: Mapping[str, Any] | None,
    session: ReferenceRuntimeSession | None = None,
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

    provisional_session = ReferenceRuntimeSession(
        session_id=_resolve_session_id(prior_session, normalized_payload),
        event_index=prior_session.event_index + 1,
        branch_registry=prior_session.branch_registry,
        pending_goal_refs=prior_session.pending_goal_refs,
        budget_history=prior_session.budget_history + (_budget_entry_for_lane(dispatch_decision.lane),),
        brake_history=prior_session.brake_history,
        last_selected_family=prior_session.last_selected_family,
        last_commitment_result_summary=prior_session.last_commitment_result_summary,
    )
    executive_state = build_reference_executive_state(
        bound_event.observation,
        _build_support_snapshot(
            provisional_session=provisional_session,
            bound_event=bound_event,
            dispatch_decision=dispatch_decision,
            warnings=warnings,
        ),
        _build_executive_environment_view(normalized_payload),
        provisional_session,
    )
    selection = select_reference_soft_control(executive_state)
    selected_family = selection.selected_family
    brake_state = executive_state.brake.brake_state
    updated_session = ReferenceRuntimeSession(
        session_id=provisional_session.session_id,
        event_index=provisional_session.event_index,
        branch_registry=provisional_session.branch_registry,
        pending_goal_refs=provisional_session.pending_goal_refs,
        budget_history=provisional_session.budget_history,
        brake_history=prior_session.brake_history + (brake_state.value,),
        last_selected_family=selected_family,
        last_commitment_result_summary=_commitment_summary_for_lane(
            dispatch_decision.lane,
            commitment_result_kind,
        ),
    )
    return ReferenceRuntimeStepResult(
        event_index=updated_session.event_index,
        bound_event=bound_event,
        dispatch_decision=dispatch_decision,
        executive_state=executive_state,
        selected_family=selected_family,
        brake_state=brake_state,
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


def _resolve_session_id(
    prior_session: ReferenceRuntimeSession,
    normalized_payload: Mapping[str, Any],
) -> str | None:
    payload_session_id = _as_non_empty_string(normalized_payload.get("session_id"))
    return prior_session.session_id or payload_session_id


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
    available_query_kinds = {
        CAPABILITY_VIEW,
        EXECUTION_TRACE,
    }
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


def _build_support_snapshot(
    *,
    provisional_session: ReferenceRuntimeSession,
    bound_event: BoundReferenceHostEvent,
    dispatch_decision: DispatchDecision,
    warnings: Sequence[str],
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


__all__ = [
    "ReferenceRuntimeSession",
    "ReferenceRuntimeStepResult",
    "run_reference_runtime_step",
]
