"""OpenAI documented host-event runtime shell over landed driver/core surfaces."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
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
    EXECUTION_TRACE,
    EXTERNAL_RECORD,
    RESULT_ARTIFACT,
    CommitmentEnvironmentHandle,
)
from cortex.drivers._commitment_common import (
    extract_native_commitment_fields,
    merge_warnings,
    resolve_commitment_extract_for_dispatch,
)
from cortex.drivers.openai_host import (
    BoundOpenAIHostEvent,
    is_raw_openai_host_event_name,
    observe_openai_host_event,
)
from cortex.drivers.openai_host_commitment import bind_openai_host_candidate
from cortex.sre.branching import BranchOperation
from cortex.sre.preservation import (
    PreservationState,
    choose_preservation_move,
    derive_preservation_state,
)
from cortex.sre.verified_work import (
    VerificationOutcome,
    WorkContract,
)

_ALLOWED_COMMITMENT_RESULT_KINDS = frozenset(status.value for status in CommitmentStatus)
_ALLOWED_DECISIONS = frozenset({"continue", "check", "repair", "stop"})
_STOP_FAILURE_CLASSES = frozenset(
    {
        "auth_missing",
        "quota_exhausted",
        "provider_internal",
        "transport_error",
        "session_mismatch",
        "artifact_invalid",
        "blocked_unsafe",
    }
)
_REPAIR_FAILURE_CLASSES = frozenset(
    {
        "invalid_patch",
        "patch_apply_failed",
        "test_failed",
        "continuity_import_failed",
        "output_invalid",
        "import_smoke_failed",
    }
)
_CHECK_FAILURE_CLASSES = frozenset({"blocked_missing_info"})
_ALLOWED_FAILURE_CLASSES = (
    _STOP_FAILURE_CLASSES | _REPAIR_FAILURE_CLASSES | _CHECK_FAILURE_CLASSES
)


@dataclass(frozen=True, slots=True)
class OpenAIRuntimeSession:
    session_id: str | None = None
    event_index: int = 0
    active_goal_ref: str | None = None
    pending_goal_refs: tuple[str, ...] = ()
    confirmed_artifact_refs: tuple[str, ...] = ()
    last_failure_class: str | None = None
    next_recommended_move: str = "continue"
    preservation_state: PreservationState | None = None

    def __post_init__(self) -> None:
        if self.session_id is not None and not (
            isinstance(self.session_id, str) and self.session_id.strip()
        ):
            raise ValueError(
                "OpenAIRuntimeSession.session_id must be non-empty after trimming when provided."
            )
        if isinstance(self.event_index, bool) or not isinstance(self.event_index, int):
            actual_type = type(self.event_index).__name__
            raise TypeError(
                "OpenAIRuntimeSession.event_index must be a non-negative integer, "
                f"got {actual_type}."
            )
        if self.event_index < 0:
            raise ValueError("OpenAIRuntimeSession.event_index must be non-negative.")
        if self.active_goal_ref is not None and not (
            isinstance(self.active_goal_ref, str) and self.active_goal_ref.strip()
        ):
            raise ValueError(
                "OpenAIRuntimeSession.active_goal_ref must be non-empty after trimming when provided."
            )
        if any(not (isinstance(ref, str) and ref.strip()) for ref in self.pending_goal_refs):
            raise ValueError(
                "OpenAIRuntimeSession.pending_goal_refs must contain only non-empty values after trimming."
            )
        if any(
            not (isinstance(ref, str) and ref.strip())
            for ref in self.confirmed_artifact_refs
        ):
            raise ValueError(
                "OpenAIRuntimeSession.confirmed_artifact_refs must contain only non-empty values after trimming."
            )
        if self.last_failure_class is not None and not (
            isinstance(self.last_failure_class, str) and self.last_failure_class.strip()
        ):
            raise ValueError(
                "OpenAIRuntimeSession.last_failure_class must be non-empty after trimming when provided."
            )
        if self.last_failure_class is not None and self.last_failure_class not in _ALLOWED_FAILURE_CLASSES:
            raise ValueError(
                "OpenAIRuntimeSession.last_failure_class must be one of the accepted "
                "OpenAI product failure classes when provided."
            )
        if self.next_recommended_move not in _ALLOWED_DECISIONS:
            raise ValueError(
                "OpenAIRuntimeSession.next_recommended_move must be one of "
                "`continue`, `check`, `repair`, `stop`."
            )
        if self.active_goal_ref is not None and self.active_goal_ref in self.pending_goal_refs:
            raise ValueError(
                "OpenAIRuntimeSession.active_goal_ref may not be duplicated inside pending_goal_refs."
            )
        if self.preservation_state is not None:
            if not isinstance(self.preservation_state, PreservationState):
                actual_type = type(self.preservation_state).__name__
                raise TypeError(
                    "OpenAIRuntimeSession.preservation_state must be PreservationState | None, "
                    f"got {actual_type}."
                )
            if self.active_goal_ref != self.preservation_state.task_anchor:
                raise ValueError(
                    "OpenAIRuntimeSession.active_goal_ref must match preservation_state.task_anchor when preservation_state is present."
                )

    def as_summary(self) -> dict[str, Any]:
        summary = {
            "session_id": self.session_id,
            "event_index": self.event_index,
            "active_goal_ref": self.active_goal_ref,
            "pending_goal_refs": list(self.pending_goal_refs),
            "confirmed_artifact_refs": list(self.confirmed_artifact_refs),
            "last_failure_class": self.last_failure_class,
            "next_recommended_move": self.next_recommended_move,
        }
        if self.preservation_state is not None:
            summary["preservation_state"] = self.preservation_state.as_payload()
        return summary


@dataclass(frozen=True, slots=True)
class OpenAIProductDecision:
    decision: str
    consequential_write_pending: bool
    approval_required: bool
    evidence_gap: bool
    continuation_debt: bool
    failure_class: str | None = None

    def __post_init__(self) -> None:
        if self.decision not in _ALLOWED_DECISIONS:
            raise ValueError(
                "OpenAIProductDecision.decision must be one of "
                "`continue`, `check`, `repair`, `stop`."
            )
        for field_name in (
            "consequential_write_pending",
            "approval_required",
            "evidence_gap",
            "continuation_debt",
        ):
            if not isinstance(getattr(self, field_name), bool):
                actual_type = type(getattr(self, field_name)).__name__
                raise TypeError(
                    f"OpenAIProductDecision.{field_name} must be bool, got {actual_type}."
                )
        if self.failure_class is not None and self.failure_class not in _ALLOWED_FAILURE_CLASSES:
            raise ValueError(
                "OpenAIProductDecision.failure_class must be one of the accepted "
                "OpenAI product failure classes when provided."
            )

    def as_summary(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "consequential_write_pending": self.consequential_write_pending,
            "approval_required": self.approval_required,
            "evidence_gap": self.evidence_gap,
            "continuation_debt": self.continuation_debt,
            "failure_class": self.failure_class,
        }


OpenAIControlLedger = OpenAIProductDecision


@dataclass(frozen=True, slots=True)
class OpenAIRuntimeStepResult:
    event_index: int
    bound_event: BoundOpenAIHostEvent
    dispatch_decision: DispatchDecision
    product_decision: OpenAIProductDecision
    warnings: tuple[str, ...]
    session: OpenAIRuntimeSession
    commitment_result_kind: str | None = None

    def __post_init__(self) -> None:
        if isinstance(self.event_index, bool) or not isinstance(self.event_index, int):
            actual_type = type(self.event_index).__name__
            raise TypeError(
                "OpenAIRuntimeStepResult.event_index must be a positive integer, "
                f"got {actual_type}."
            )
        if self.event_index <= 0:
            raise ValueError("OpenAIRuntimeStepResult.event_index must be positive.")
        if not isinstance(self.bound_event, BoundOpenAIHostEvent):
            actual_type = type(self.bound_event).__name__
            raise TypeError(
                "OpenAIRuntimeStepResult.bound_event must be BoundOpenAIHostEvent, "
                f"got {actual_type}."
            )
        if not isinstance(self.dispatch_decision, DispatchDecision):
            actual_type = type(self.dispatch_decision).__name__
            raise TypeError(
                "OpenAIRuntimeStepResult.dispatch_decision must be DispatchDecision, "
                f"got {actual_type}."
            )
        if not isinstance(self.product_decision, OpenAIProductDecision):
            actual_type = type(self.product_decision).__name__
            raise TypeError(
                "OpenAIRuntimeStepResult.product_decision must be OpenAIProductDecision, "
                f"got {actual_type}."
            )
        if any(not (isinstance(warning, str) and warning.strip()) for warning in self.warnings):
            raise ValueError(
                "OpenAIRuntimeStepResult.warnings must contain only non-empty values after trimming."
            )
        if not isinstance(self.session, OpenAIRuntimeSession):
            actual_type = type(self.session).__name__
            raise TypeError(
                "OpenAIRuntimeStepResult.session must be OpenAIRuntimeSession, "
                f"got {actual_type}."
            )
        if self.event_index != self.session.event_index:
            raise ValueError(
                "OpenAIRuntimeStepResult.event_index must match session.event_index."
            )
        if self.product_decision.decision != self.session.next_recommended_move:
            raise ValueError(
                "OpenAIRuntimeStepResult.product_decision.decision must match "
                "session.next_recommended_move."
            )
        if (
            self.commitment_result_kind is not None
            and self.commitment_result_kind not in _ALLOWED_COMMITMENT_RESULT_KINDS
        ):
            raise ValueError(
                "OpenAIRuntimeStepResult.commitment_result_kind must be one of the canonical "
                "commitment status values or None."
            )

    @property
    def journal(self) -> dict[str, Any]:
        return self.session.as_summary()


def run_openai_runtime_step(
    raw_event_name: str,
    raw_payload: Mapping[str, Any] | None,
    session: OpenAIRuntimeSession | None = None,
) -> OpenAIRuntimeStepResult:
    if not is_raw_openai_host_event_name(raw_event_name):
        raise ValueError(
            "run_openai_runtime_step.event_name must be a raw OpenAI host event name, "
            "not a canonical Cortex event name."
        )
    prior_session = _coerce_session(session)
    bound_event = observe_openai_host_event(raw_event_name, raw_payload)
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
    session_id, session_id_warnings, failure_class = _resolve_session_id(
        prior_session,
        normalized_payload,
    )
    warnings = merge_warnings(warnings, session_id_warnings)

    candidate = None
    commitment_result_kind: str | None = None
    if dispatch_decision.lane is not DispatchLane.CHEAP:
        candidate, candidate_warnings = bind_openai_host_candidate(
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
        next_active_goal_ref,
        next_pending_goal_refs,
        continuity_warnings,
    ) = _apply_continuity_update(prior_session, normalized_payload)
    warnings = merge_warnings(warnings, continuity_warnings)
    confirmed_artifact_refs = _merge_confirmed_artifact_refs(
        prior_session.confirmed_artifact_refs,
        _first_concrete_artifact_ref(normalized_payload),
    )
    consequential_write_pending = bool(normalized_payload.get("externally_consequential"))
    approval_required = dispatch_decision.lane is not DispatchLane.CHEAP
    evidence_gap = consequential_write_pending and _first_concrete_artifact_ref(normalized_payload) is None
    continuation_debt = next_active_goal_ref is not None or bool(next_pending_goal_refs)
    decision = _decide_action(
        consequential_write_pending=consequential_write_pending,
        approval_required=approval_required,
        evidence_gap=evidence_gap,
        continuation_debt=continuation_debt,
        failure_class=failure_class,
    )
    product_decision = OpenAIProductDecision(
        decision=decision,
        consequential_write_pending=consequential_write_pending,
        approval_required=approval_required,
        evidence_gap=evidence_gap,
        continuation_debt=continuation_debt,
        failure_class=failure_class,
    )
    updated_session = OpenAIRuntimeSession(
        session_id=session_id,
        event_index=prior_session.event_index + 1,
        active_goal_ref=next_active_goal_ref,
        pending_goal_refs=next_pending_goal_refs,
        confirmed_artifact_refs=confirmed_artifact_refs,
        last_failure_class=failure_class,
        next_recommended_move=decision,
        preservation_state=(
            prior_session.preservation_state
            if prior_session.preservation_state is not None
            and next_active_goal_ref == prior_session.preservation_state.task_anchor
            else None
        ),
    )
    return OpenAIRuntimeStepResult(
        event_index=updated_session.event_index,
        bound_event=bound_event,
        dispatch_decision=dispatch_decision,
        product_decision=product_decision,
        warnings=warnings,
        session=updated_session,
        commitment_result_kind=commitment_result_kind,
    )


def run_openai_runtime_verification_step(
    outcome: VerificationOutcome,
    session: OpenAIRuntimeSession | None,
    *,
    work_contract: WorkContract,
    remaining_repairs: int,
) -> OpenAIRuntimeSession:
    if not isinstance(outcome, VerificationOutcome):
        actual_type = type(outcome).__name__
        raise TypeError(
            "run_openai_runtime_verification_step.outcome must be VerificationOutcome, "
            f"got {actual_type}."
        )
    if not isinstance(work_contract, WorkContract):
        actual_type = type(work_contract).__name__
        raise TypeError(
            "run_openai_runtime_verification_step.work_contract must be WorkContract, "
            f"got {actual_type}."
        )
    current_session = _coerce_session(session)
    preservation_state = derive_preservation_state(
        current_session.active_goal_ref,
        work_contract,
        outcome.parsed_paths,
        outcome,
        remaining_repairs=remaining_repairs,
    )
    decision = choose_preservation_move(preservation_state)
    return OpenAIRuntimeSession(
        session_id=current_session.session_id,
        event_index=current_session.event_index,
        active_goal_ref=preservation_state.task_anchor,
        pending_goal_refs=current_session.pending_goal_refs,
        confirmed_artifact_refs=current_session.confirmed_artifact_refs,
        last_failure_class=outcome.failure_class,
        next_recommended_move=decision,
        preservation_state=preservation_state,
    )


def _coerce_session(session: OpenAIRuntimeSession | None) -> OpenAIRuntimeSession:
    if session is None:
        return OpenAIRuntimeSession()
    if not isinstance(session, OpenAIRuntimeSession):
        actual_type = type(session).__name__
        raise TypeError(
            "run_openai_runtime_step.session must be OpenAIRuntimeSession | None, "
            f"got {actual_type}."
        )
    return session


def _resolve_session_id(
    prior_session: OpenAIRuntimeSession,
    normalized_payload: Mapping[str, Any],
) -> tuple[str | None, tuple[str, ...], str | None]:
    payload_session_id = _as_non_empty_string(normalized_payload.get("session_id"))
    if prior_session.session_id is None:
        return payload_session_id, (), None
    if payload_session_id is None or payload_session_id == prior_session.session_id:
        return prior_session.session_id, (), None
    return (
        prior_session.session_id,
        (f"session-rejected:mismatched-session-id:{payload_session_id}",),
        "session_mismatch",
    )


def _apply_continuity_update(
    prior_session: OpenAIRuntimeSession,
    normalized_payload: Mapping[str, Any],
) -> tuple[str | None, tuple[str, ...], tuple[str, ...]]:
    operation = _branch_operation(normalized_payload)
    active_goal_ref = prior_session.active_goal_ref
    pending_goal_refs = list(prior_session.pending_goal_refs)
    goal_ref = _continuity_track_ref(normalized_payload)
    payload_goal_refs = _pending_goal_refs_from_payload(normalized_payload)
    warnings: tuple[str, ...] = ()

    if operation is None:
        pending_goal_refs = _merge_unique_refs(tuple(pending_goal_refs), payload_goal_refs)
        return active_goal_ref, _normalized_pending_goal_refs(active_goal_ref, pending_goal_refs), warnings

    if operation is BranchOperation.OPEN:
        if goal_ref is None:
            warnings = ("continuity-rejected:missing-open-track-ref",)
            return active_goal_ref, tuple(prior_session.pending_goal_refs), warnings
        active_goal_ref = goal_ref
        pending_goal_refs = [ref for ref in pending_goal_refs if ref != goal_ref]
        pending_goal_refs = _merge_unique_refs(tuple(pending_goal_refs), payload_goal_refs)
        return active_goal_ref, _normalized_pending_goal_refs(active_goal_ref, pending_goal_refs), warnings

    if operation is BranchOperation.SUSPEND:
        if goal_ref is None or active_goal_ref != goal_ref:
            warnings = (_continuity_warning("missing-active-branch", goal_ref),)
            return active_goal_ref, tuple(prior_session.pending_goal_refs), warnings
        active_goal_ref = None
        pending_goal_refs = _merge_unique_refs(tuple(pending_goal_refs), (goal_ref, *payload_goal_refs))
        return active_goal_ref, _normalized_pending_goal_refs(active_goal_ref, pending_goal_refs), warnings

    if operation is BranchOperation.RESUME:
        if goal_ref is None:
            warnings = (_continuity_warning("missing-active-branch", goal_ref),)
            return active_goal_ref, tuple(prior_session.pending_goal_refs), warnings
        if goal_ref not in pending_goal_refs:
            warnings = (_continuity_warning("missing-resume-anchor", goal_ref),)
            return active_goal_ref, tuple(prior_session.pending_goal_refs), warnings
        active_goal_ref = goal_ref
        pending_goal_refs = [ref for ref in pending_goal_refs if ref != goal_ref]
        pending_goal_refs = _merge_unique_refs(tuple(pending_goal_refs), payload_goal_refs)
        return active_goal_ref, _normalized_pending_goal_refs(active_goal_ref, pending_goal_refs), warnings

    if operation is BranchOperation.MERGE:
        if goal_ref is None:
            warnings = (_continuity_warning("missing-active-branch", goal_ref),)
            return active_goal_ref, tuple(prior_session.pending_goal_refs), warnings
        merge_target_ref = _merge_target_ref(normalized_payload)
        if goal_ref in pending_goal_refs or active_goal_ref != goal_ref:
            warnings = (
                _continuity_warning("continuity-mismatch-after-suspension", goal_ref),
            )
            return active_goal_ref, tuple(prior_session.pending_goal_refs), warnings
        if (
            merge_target_ref is not None
            and merge_target_ref not in pending_goal_refs
            and merge_target_ref != goal_ref
        ):
            warnings = (_continuity_warning("illegal-merge-target", merge_target_ref),)
            return active_goal_ref, tuple(prior_session.pending_goal_refs), warnings
        active_goal_ref = merge_target_ref
        pending_goal_refs = [ref for ref in pending_goal_refs if ref != goal_ref]
        pending_goal_refs = _merge_unique_refs(tuple(pending_goal_refs), payload_goal_refs)
        return active_goal_ref, _normalized_pending_goal_refs(active_goal_ref, pending_goal_refs), warnings

    return active_goal_ref, tuple(prior_session.pending_goal_refs), warnings


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


def _merge_confirmed_artifact_refs(
    existing_refs: tuple[str, ...],
    artifact_ref: str | None,
) -> tuple[str, ...]:
    refs = _merge_unique_refs(existing_refs, (artifact_ref,) if artifact_ref is not None else ())
    return tuple(refs)


def _decide_action(
    *,
    consequential_write_pending: bool,
    approval_required: bool,
    evidence_gap: bool,
    continuation_debt: bool,
    failure_class: str | None,
) -> str:
    del continuation_debt
    if failure_class in _STOP_FAILURE_CLASSES:
        return "stop"
    if failure_class in _CHECK_FAILURE_CLASSES:
        return "check"
    if failure_class in _REPAIR_FAILURE_CLASSES:
        return "repair"
    if approval_required or consequential_write_pending or evidence_gap:
        return "check"
    return "continue"


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
    active_goal_ref = _as_non_empty_string(normalized_payload.get("active_goal_ref"))
    if active_goal_ref is not None:
        return active_goal_ref
    active_track_ref = _as_non_empty_string(normalized_payload.get("active_track_ref"))
    if active_track_ref == "main":
        return None
    return active_track_ref


def _merge_target_ref(normalized_payload: Mapping[str, Any]) -> str | None:
    target = _as_non_empty_string(normalized_payload.get("merge_target_ref"))
    if target == "main":
        return None
    return target


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
    incoming_refs: Sequence[str | None],
) -> list[str]:
    ordered_refs: list[str] = []
    for goal_ref in existing_refs:
        if goal_ref not in ordered_refs:
            ordered_refs.append(goal_ref)
    for goal_ref in incoming_refs:
        if goal_ref is None:
            continue
        if goal_ref not in ordered_refs:
            ordered_refs.append(goal_ref)
    return ordered_refs


def _normalized_pending_goal_refs(
    active_goal_ref: str | None,
    pending_goal_refs: Sequence[str],
) -> tuple[str, ...]:
    normalized: list[str] = []
    for goal_ref in pending_goal_refs:
        if goal_ref == active_goal_ref:
            continue
        if goal_ref not in normalized:
            normalized.append(goal_ref)
    return tuple(normalized)


def _continuity_warning(reason_code: str, subject: str | None) -> str:
    if subject is None:
        return f"continuity-rejected:{reason_code}"
    return f"continuity-rejected:{reason_code}:{subject}"


__all__ = [
    "OpenAIControlLedger",
    "OpenAIProductDecision",
    "OpenAIRuntimeSession",
    "OpenAIRuntimeStepResult",
    "run_openai_runtime_verification_step",
    "run_openai_runtime_step",
]
