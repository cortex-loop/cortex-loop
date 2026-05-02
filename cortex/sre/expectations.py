"""Bounded expectation-debt carriers for runtime feedback residue.

This module tracks structured expectation debt only. It does not inspect
arbitrary assistant prose, change brake or route policy, or emit
model-visible text.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from cortex.core.commitments import CommitmentStatus
from cortex.core.dispatch import DispatchDecision, DispatchLane

FORWARD_COMMITMENT_KINDS = frozenset(
    {
        "completion",
        "verification",
        "artifact_change",
        "plan_commitment",
        "diagnosis",
        "capability_claim",
        "deferred_followup",
    }
)
ASSERTIVENESS_LEVELS = frozenset({"low", "medium", "high"})
COMMITMENT_SCOPES = frozenset(
    {"local_step", "task", "branch", "session", "external_world"}
)
EXPECTATION_HORIZONS = frozenset(
    {"immediate", "next_step", "deferred", "waiting_on_user"}
)
SATISFACTION_CLASSES = frozenset(
    {
        "meaningful_evidence",
        "continuity_progress",
        "commitment_certified",
        "liability_retracted",
        "blocker_surfaced",
        "waiting_released",
        "stream_only",
        "degradation",
    }
)
PAYDOWN_CLASSES = frozenset(
    {
        "meaningful_evidence",
        "continuity_progress",
        "commitment_certified",
        "liability_retracted",
        "blocker_surfaced",
        "waiting_released",
    }
)
RELIEF_CLASSES = frozenset({"liability_retracted", "blocker_surfaced"})
SUSPENSION_STATES = frozenset(
    {"active", "waiting_on_user", "deferred", "fulfilled", "expired"}
)
DEFICIT_KINDS = frozenset(
    {"verification", "completion", "continuity", "preservation", "capability", "mixed"}
)

_MAX_ACTIVE_EXPECTATIONS = 8
_MAX_RESOLVED_EXPECTATIONS = 12
_COMMITMENT_RESULT_KINDS = frozenset(status.value for status in CommitmentStatus)

_COMPLETION_REASON_TAGS = frozenset({"explicit-completion-claim", "task-complete"})
_VERIFICATION_REASON_TAGS = frozenset(
    {"commitment-subset", "approval-gated", "boundary-required"}
)
_ARTIFACT_REASON_TAGS = frozenset(
    {"durable-write", "approved-external-mutation", "externally-consequential"}
)
_PLAN_REASON_TAGS = frozenset({"proposal-surface", "candidate-present"})
_USER_WAIT_WARNING_TAGS = frozenset(
    {"waiting-on-user", "user-input-required", "approval-required", "blocked-on-user"}
)


@dataclass(frozen=True, slots=True)
class ForwardCommitment:
    commitment_id: str
    source_event_ref: str
    commitment_kind: str
    assertiveness: str
    scope: str
    opened_at_step: int
    claim_span_ref: str | None = None

    def __post_init__(self) -> None:
        _require_non_empty_string(self.commitment_id, "ForwardCommitment.commitment_id")
        _require_non_empty_string(self.source_event_ref, "ForwardCommitment.source_event_ref")
        if self.commitment_kind not in FORWARD_COMMITMENT_KINDS:
            raise ValueError(
                "ForwardCommitment.commitment_kind must be a canonical forward commitment kind."
            )
        if self.assertiveness not in ASSERTIVENESS_LEVELS:
            raise ValueError(
                "ForwardCommitment.assertiveness must be one of low, medium, or high."
            )
        if self.scope not in COMMITMENT_SCOPES:
            raise ValueError("ForwardCommitment.scope must be a canonical commitment scope.")
        _require_non_negative_int(self.opened_at_step, "ForwardCommitment.opened_at_step")
        if self.claim_span_ref is not None:
            _require_non_empty_string(self.claim_span_ref, "ForwardCommitment.claim_span_ref")

    def as_payload(self) -> dict[str, object]:
        return {
            "commitment_id": self.commitment_id,
            "source_event_ref": self.source_event_ref,
            "claim_span_ref": self.claim_span_ref,
            "commitment_kind": self.commitment_kind,
            "assertiveness": self.assertiveness,
            "scope": self.scope,
            "opened_at_step": self.opened_at_step,
        }

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "ForwardCommitment":
        if not isinstance(payload, Mapping):
            actual_type = type(payload).__name__
            raise TypeError(
                "ForwardCommitment.from_payload payload must be a mapping, "
                f"got {actual_type}."
            )
        return cls(
            commitment_id=_required_string(payload.get("commitment_id"), "commitment_id"),
            source_event_ref=_required_string(payload.get("source_event_ref"), "source_event_ref"),
            claim_span_ref=_optional_string(payload.get("claim_span_ref"), "claim_span_ref"),
            commitment_kind=_required_string(payload.get("commitment_kind"), "commitment_kind"),
            assertiveness=_required_string(payload.get("assertiveness"), "assertiveness"),
            scope=_required_string(payload.get("scope"), "scope"),
            opened_at_step=_required_int(payload.get("opened_at_step"), "opened_at_step"),
        )


@dataclass(frozen=True, slots=True)
class EvidenceProgress:
    progress_class: str
    event_ref: str
    weight: float = 1.0
    commitment_id: str | None = None

    def __post_init__(self) -> None:
        if self.progress_class not in SATISFACTION_CLASSES:
            raise ValueError(
                "EvidenceProgress.progress_class must be a canonical satisfaction class."
            )
        _require_non_empty_string(self.event_ref, "EvidenceProgress.event_ref")
        _require_unitish_weight(self.weight, "EvidenceProgress.weight")
        if self.commitment_id is not None:
            _require_non_empty_string(self.commitment_id, "EvidenceProgress.commitment_id")

    def as_payload(self) -> dict[str, object]:
        return {
            "progress_class": self.progress_class,
            "event_ref": self.event_ref,
            "weight": float(self.weight),
            "commitment_id": self.commitment_id,
        }

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "EvidenceProgress":
        if not isinstance(payload, Mapping):
            actual_type = type(payload).__name__
            raise TypeError(
                "EvidenceProgress.from_payload payload must be a mapping, "
                f"got {actual_type}."
            )
        return cls(
            progress_class=_required_string(payload.get("progress_class"), "progress_class"),
            event_ref=_required_string(payload.get("event_ref"), "event_ref"),
            weight=_required_float(payload.get("weight"), "weight"),
            commitment_id=_optional_string(payload.get("commitment_id"), "commitment_id"),
        )


@dataclass(frozen=True, slots=True)
class ExpectationRecord:
    expectation_id: str
    commitment_id: str
    weight: float
    horizon: str
    satisfaction_classes: tuple[str, ...]
    opened_at_step: int
    due_at_step: int
    suspension_state: str = "active"
    remaining_weight: float | None = None
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)
    deficit_kind: str = "mixed"
    resolution_class: str | None = None

    def __post_init__(self) -> None:
        _require_non_empty_string(self.expectation_id, "ExpectationRecord.expectation_id")
        _require_non_empty_string(self.commitment_id, "ExpectationRecord.commitment_id")
        _require_unitish_weight(self.weight, "ExpectationRecord.weight")
        if self.horizon not in EXPECTATION_HORIZONS:
            raise ValueError("ExpectationRecord.horizon must be a canonical expectation horizon.")
        if not self.satisfaction_classes:
            raise ValueError(
                "ExpectationRecord.satisfaction_classes must contain at least one class."
            )
        if any(satisfaction not in SATISFACTION_CLASSES for satisfaction in self.satisfaction_classes):
            raise ValueError(
                "ExpectationRecord.satisfaction_classes must contain only canonical satisfaction classes."
            )
        _require_non_negative_int(self.opened_at_step, "ExpectationRecord.opened_at_step")
        _require_non_negative_int(self.due_at_step, "ExpectationRecord.due_at_step")
        if self.due_at_step < self.opened_at_step:
            raise ValueError("ExpectationRecord.due_at_step may not precede opened_at_step.")
        if self.suspension_state not in SUSPENSION_STATES:
            raise ValueError(
                "ExpectationRecord.suspension_state must be a canonical suspension state."
            )
        remaining_weight = self.weight if self.remaining_weight is None else self.remaining_weight
        _require_unitish_weight(remaining_weight, "ExpectationRecord.remaining_weight")
        if remaining_weight > self.weight:
            raise ValueError("ExpectationRecord.remaining_weight may not exceed weight.")
        if remaining_weight != self.remaining_weight:
            object.__setattr__(self, "remaining_weight", float(remaining_weight))
        if any(not (isinstance(ref, str) and ref.strip()) for ref in self.evidence_refs):
            raise ValueError(
                "ExpectationRecord.evidence_refs must contain only non-empty strings after trimming."
            )
        if self.deficit_kind not in DEFICIT_KINDS:
            raise ValueError("ExpectationRecord.deficit_kind must be a canonical deficit kind.")
        if self.resolution_class is not None and self.resolution_class not in SATISFACTION_CLASSES:
            raise ValueError(
                "ExpectationRecord.resolution_class must be a canonical satisfaction class or None."
            )
        if self.suspension_state in {"fulfilled", "expired"} and self.remaining_weight != 0.0:
            object.__setattr__(self, "remaining_weight", 0.0)

    @property
    def is_open(self) -> bool:
        return self.suspension_state in {"active", "waiting_on_user", "deferred"}

    @property
    def is_suspended(self) -> bool:
        return self.suspension_state in {"waiting_on_user", "deferred"}

    def is_due(self, current_step: int) -> bool:
        _require_non_negative_int(current_step, "ExpectationRecord.is_due.current_step")
        return self.suspension_state == "active" and self.due_at_step <= current_step

    def with_paydown(
        self,
        progress: EvidenceProgress,
        *,
        current_step: int,
    ) -> "ExpectationRecord":
        _require_non_negative_int(current_step, "ExpectationRecord.with_paydown.current_step")
        if not isinstance(progress, EvidenceProgress):
            actual_type = type(progress).__name__
            raise TypeError(
                "ExpectationRecord.with_paydown progress must be EvidenceProgress, "
                f"got {actual_type}."
            )
        if progress.progress_class not in self.satisfaction_classes:
            return self
        if self.suspension_state not in {"active", "waiting_on_user", "deferred"}:
            return self
        remaining = max(0.0, float(self.remaining_weight) - float(progress.weight))
        refs = _dedupe_string_tuple((*self.evidence_refs, progress.event_ref))
        if remaining == 0.0:
            return ExpectationRecord(
                expectation_id=self.expectation_id,
                commitment_id=self.commitment_id,
                weight=self.weight,
                horizon=self.horizon,
                satisfaction_classes=self.satisfaction_classes,
                opened_at_step=self.opened_at_step,
                due_at_step=current_step,
                suspension_state="fulfilled",
                remaining_weight=0.0,
                evidence_refs=refs,
                deficit_kind=self.deficit_kind,
                resolution_class=progress.progress_class,
            )
        return ExpectationRecord(
            expectation_id=self.expectation_id,
            commitment_id=self.commitment_id,
            weight=self.weight,
            horizon=self.horizon,
            satisfaction_classes=self.satisfaction_classes,
            opened_at_step=self.opened_at_step,
            due_at_step=self.due_at_step,
            suspension_state="active",
            remaining_weight=remaining,
            evidence_refs=refs,
            deficit_kind=self.deficit_kind,
        )

    def with_suspension(self, suspension_state: str) -> "ExpectationRecord":
        if suspension_state not in {"active", "waiting_on_user", "deferred"}:
            raise ValueError(
                "ExpectationRecord.with_suspension suspension_state must be active, waiting_on_user, or deferred."
            )
        return ExpectationRecord(
            expectation_id=self.expectation_id,
            commitment_id=self.commitment_id,
            weight=self.weight,
            horizon=self.horizon,
            satisfaction_classes=self.satisfaction_classes,
            opened_at_step=self.opened_at_step,
            due_at_step=self.due_at_step,
            suspension_state=suspension_state,
            remaining_weight=self.remaining_weight,
            evidence_refs=self.evidence_refs,
            deficit_kind=self.deficit_kind,
            resolution_class=self.resolution_class,
        )

    def as_payload(self) -> dict[str, object]:
        return {
            "expectation_id": self.expectation_id,
            "commitment_id": self.commitment_id,
            "weight": float(self.weight),
            "horizon": self.horizon,
            "satisfaction_classes": list(self.satisfaction_classes),
            "opened_at_step": self.opened_at_step,
            "due_at_step": self.due_at_step,
            "suspension_state": self.suspension_state,
            "remaining_weight": float(self.remaining_weight),
            "evidence_refs": list(self.evidence_refs),
            "deficit_kind": self.deficit_kind,
            "resolution_class": self.resolution_class,
        }

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "ExpectationRecord":
        if not isinstance(payload, Mapping):
            actual_type = type(payload).__name__
            raise TypeError(
                "ExpectationRecord.from_payload payload must be a mapping, "
                f"got {actual_type}."
            )
        return cls(
            expectation_id=_required_string(payload.get("expectation_id"), "expectation_id"),
            commitment_id=_required_string(payload.get("commitment_id"), "commitment_id"),
            weight=_required_float(payload.get("weight"), "weight"),
            horizon=_required_string(payload.get("horizon"), "horizon"),
            satisfaction_classes=_string_tuple(
                payload.get("satisfaction_classes"),
                "satisfaction_classes",
            ),
            opened_at_step=_required_int(payload.get("opened_at_step"), "opened_at_step"),
            due_at_step=_required_int(payload.get("due_at_step"), "due_at_step"),
            suspension_state=_required_string(
                payload.get("suspension_state"),
                "suspension_state",
            ),
            remaining_weight=_required_float(
                payload.get("remaining_weight"),
                "remaining_weight",
            ),
            evidence_refs=_string_tuple(payload.get("evidence_refs"), "evidence_refs"),
            deficit_kind=_required_string(payload.get("deficit_kind"), "deficit_kind"),
            resolution_class=_optional_string(
                payload.get("resolution_class"),
                "resolution_class",
            ),
        )


@dataclass(frozen=True, slots=True)
class ResolutionDeficitState:
    due_weight: float = 0.0
    fulfilled_weight: float = 0.0
    overdue_weight: float = 0.0
    suspended_weight: float = 0.0
    relief_weight: float = 0.0
    negative_prediction_error: float = 0.0
    dominant_deficit_kind: str | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "due_weight",
            "fulfilled_weight",
            "overdue_weight",
            "suspended_weight",
            "relief_weight",
            "negative_prediction_error",
        ):
            _require_non_negative_float(
                getattr(self, field_name),
                f"ResolutionDeficitState.{field_name}",
            )
        if not 0.0 <= self.negative_prediction_error <= 1.0:
            raise ValueError(
                "ResolutionDeficitState.negative_prediction_error must be in [0.0, 1.0]."
            )
        if self.dominant_deficit_kind is not None and self.dominant_deficit_kind not in DEFICIT_KINDS:
            raise ValueError(
                "ResolutionDeficitState.dominant_deficit_kind must be a canonical deficit kind or None."
            )

    def as_payload(self) -> dict[str, object]:
        return {
            "due_weight": float(self.due_weight),
            "fulfilled_weight": float(self.fulfilled_weight),
            "overdue_weight": float(self.overdue_weight),
            "suspended_weight": float(self.suspended_weight),
            "relief_weight": float(self.relief_weight),
            "negative_prediction_error": float(self.negative_prediction_error),
            "dominant_deficit_kind": self.dominant_deficit_kind,
        }


@dataclass(frozen=True, slots=True)
class ExpectationLedger:
    active: tuple[ExpectationRecord, ...] = ()
    resolved: tuple[ExpectationRecord, ...] = ()

    def __post_init__(self) -> None:
        if any(not isinstance(record, ExpectationRecord) for record in self.active):
            raise TypeError(
                "ExpectationLedger.active must contain only ExpectationRecord instances."
            )
        if any(not isinstance(record, ExpectationRecord) for record in self.resolved):
            raise TypeError(
                "ExpectationLedger.resolved must contain only ExpectationRecord instances."
            )
        if len(self.active) > _MAX_ACTIVE_EXPECTATIONS:
            raise ValueError(
                f"ExpectationLedger.active may contain at most {_MAX_ACTIVE_EXPECTATIONS} records."
            )
        if len(self.resolved) > _MAX_RESOLVED_EXPECTATIONS:
            raise ValueError(
                f"ExpectationLedger.resolved may contain at most {_MAX_RESOLVED_EXPECTATIONS} records."
            )
        ids = [record.expectation_id for record in (*self.active, *self.resolved)]
        if len(ids) != len(set(ids)):
            raise ValueError("ExpectationLedger records must have unique expectation_id values.")
        if any(not record.is_open for record in self.active):
            raise ValueError("ExpectationLedger.active may contain only open records.")
        if any(record.is_open for record in self.resolved):
            raise ValueError("ExpectationLedger.resolved may not contain open records.")

    def open_expectation(self, record: ExpectationRecord) -> "ExpectationLedger":
        if not isinstance(record, ExpectationRecord):
            actual_type = type(record).__name__
            raise TypeError(
                "ExpectationLedger.open_expectation record must be ExpectationRecord, "
                f"got {actual_type}."
            )
        if not record.is_open:
            raise ValueError("ExpectationLedger.open_expectation record must be open.")
        without_duplicate = tuple(
            existing
            for existing in self.active
            if existing.expectation_id != record.expectation_id
        )
        return _ledger_with_caps(
            active=(*without_duplicate, record),
            resolved=self.resolved,
        )

    def apply_progress(
        self,
        progress: EvidenceProgress,
        *,
        current_step: int,
    ) -> "ExpectationLedger":
        _require_non_negative_int(current_step, "ExpectationLedger.apply_progress.current_step")
        if not isinstance(progress, EvidenceProgress):
            actual_type = type(progress).__name__
            raise TypeError(
                "ExpectationLedger.apply_progress progress must be EvidenceProgress, "
                f"got {actual_type}."
            )
        if progress.progress_class == "stream_only":
            return self
        selected_index = _select_paydown_index(
            self.active,
            progress,
            current_step=current_step,
        )
        if selected_index is None:
            return self
        next_active: list[ExpectationRecord] = []
        next_resolved = list(self.resolved)
        for index, record in enumerate(self.active):
            if index != selected_index:
                next_active.append(record)
                continue
            updated_record = record.with_paydown(progress, current_step=current_step)
            if updated_record.is_open:
                next_active.append(updated_record)
            else:
                next_resolved.append(updated_record)
        return _ledger_with_caps(active=tuple(next_active), resolved=tuple(next_resolved))

    def suspend_matching(
        self,
        *,
        horizon: str,
        suspension_state: str,
    ) -> "ExpectationLedger":
        if horizon not in EXPECTATION_HORIZONS:
            raise ValueError("ExpectationLedger.suspend_matching horizon must be canonical.")
        if suspension_state not in {"waiting_on_user", "deferred"}:
            raise ValueError(
                "ExpectationLedger.suspend_matching suspension_state must be waiting_on_user or deferred."
            )
        return _ledger_with_caps(
            active=tuple(
                record.with_suspension(suspension_state)
                if record.horizon == horizon and record.suspension_state == "active"
                else record
                for record in self.active
            ),
            resolved=self.resolved,
        )

    def resolution_deficit(self, *, current_step: int) -> ResolutionDeficitState:
        return compute_resolution_deficit(self, current_step=current_step)

    def as_payload(self) -> dict[str, object]:
        return {
            "active": [record.as_payload() for record in self.active],
            "resolved": [record.as_payload() for record in self.resolved],
        }

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any] | None) -> "ExpectationLedger":
        if payload is None:
            return cls()
        if not isinstance(payload, Mapping):
            actual_type = type(payload).__name__
            raise TypeError(
                "ExpectationLedger.from_payload payload must be a mapping or None, "
                f"got {actual_type}."
            )
        return cls(
            active=tuple(
                ExpectationRecord.from_payload(record)
                for record in _mapping_sequence(payload.get("active"), "ExpectationLedger.active")
            ),
            resolved=tuple(
                ExpectationRecord.from_payload(record)
                for record in _mapping_sequence(payload.get("resolved"), "ExpectationLedger.resolved")
            ),
        )


def expectation_record_for_forward_commitment(
    commitment: ForwardCommitment,
) -> ExpectationRecord | None:
    if not isinstance(commitment, ForwardCommitment):
        actual_type = type(commitment).__name__
        raise TypeError(
            "expectation_record_for_forward_commitment commitment must be ForwardCommitment, "
            f"got {actual_type}."
        )
    weight = _weight_for_assertiveness(commitment.assertiveness)
    if commitment.commitment_kind == "completion":
        return _record_for_commitment(
            commitment,
            weight=weight,
            horizon="immediate",
            satisfaction_classes=(
                "meaningful_evidence",
                "commitment_certified",
                "liability_retracted",
                "blocker_surfaced",
            ),
            due_delta=0,
            deficit_kind="completion",
        )
    if commitment.commitment_kind == "verification":
        return _record_for_commitment(
            commitment,
            weight=weight,
            horizon="immediate",
            satisfaction_classes=(
                "meaningful_evidence",
                "commitment_certified",
                "liability_retracted",
                "blocker_surfaced",
            ),
            due_delta=0,
            deficit_kind="verification",
        )
    if commitment.commitment_kind in {"artifact_change", "plan_commitment"}:
        return _record_for_commitment(
            commitment,
            weight=min(0.7, weight),
            horizon="next_step",
            satisfaction_classes=(
                "meaningful_evidence",
                "continuity_progress",
                "commitment_certified",
                "liability_retracted",
                "blocker_surfaced",
            ),
            due_delta=1,
            deficit_kind="preservation",
        )
    if commitment.commitment_kind == "capability_claim":
        return _record_for_commitment(
            commitment,
            weight=min(0.6, weight),
            horizon="next_step",
            satisfaction_classes=(
                "meaningful_evidence",
                "liability_retracted",
                "blocker_surfaced",
            ),
            due_delta=1,
            deficit_kind="capability",
        )
    if commitment.commitment_kind in {"diagnosis", "deferred_followup"}:
        if commitment.assertiveness == "high":
            return _record_for_commitment(
                commitment,
                weight=0.3,
                horizon="deferred",
                satisfaction_classes=(
                    "meaningful_evidence",
                    "liability_retracted",
                    "blocker_surfaced",
                    "waiting_released",
                ),
                due_delta=3,
                suspension_state="deferred",
                deficit_kind="verification",
            )
        return None
    return None


def open_expectation_from_forward_commitment(
    ledger: ExpectationLedger,
    commitment: ForwardCommitment,
) -> ExpectationLedger:
    if not isinstance(ledger, ExpectationLedger):
        actual_type = type(ledger).__name__
        raise TypeError(
            "open_expectation_from_forward_commitment ledger must be ExpectationLedger, "
            f"got {actual_type}."
        )
    record = expectation_record_for_forward_commitment(commitment)
    if record is None:
        return ledger
    return ledger.open_expectation(record)


def forward_commitment_from_dispatch(
    *,
    dispatch_decision: DispatchDecision,
    source_event_ref: str,
    opened_at_step: int,
    commitment_result_kind: str | None = None,
    task_mode: str | None = None,
) -> ForwardCommitment | None:
    if not isinstance(dispatch_decision, DispatchDecision):
        actual_type = type(dispatch_decision).__name__
        raise TypeError(
            "forward_commitment_from_dispatch dispatch_decision must be DispatchDecision, "
            f"got {actual_type}."
        )
    _require_non_empty_string(source_event_ref, "forward_commitment_from_dispatch.source_event_ref")
    _require_non_negative_int(opened_at_step, "forward_commitment_from_dispatch.opened_at_step")
    if commitment_result_kind is not None and commitment_result_kind not in _COMMITMENT_RESULT_KINDS:
        raise ValueError(
            "forward_commitment_from_dispatch commitment_result_kind must be a canonical commitment status or None."
        )
    if task_mode is not None:
        _require_non_empty_string(task_mode, "forward_commitment_from_dispatch.task_mode")

    reason_tags = dispatch_decision.wake_decision.reason_tags
    commitment_kind = _commitment_kind_from_tags(
        reason_tags,
        dispatch_decision.lane,
        commitment_result_kind,
    )
    if commitment_kind is None:
        return None
    return ForwardCommitment(
        commitment_id=f"{source_event_ref}:{commitment_kind}",
        source_event_ref=source_event_ref,
        claim_span_ref=f"{source_event_ref}:structured-cue",
        commitment_kind=commitment_kind,
        assertiveness=_assertiveness_for_dispatch(dispatch_decision.lane),
        scope=_scope_for_task_mode(task_mode),
        opened_at_step=opened_at_step,
    )


def evidence_progress_from_feedback(
    *,
    event_ref: str,
    evidence_progress_class: str | None,
    continuity_progress_class: str | None,
    commitment_result_kind: str | None,
    current_commitment_id: str | None = None,
    warning_codes: tuple[str, ...] = (),
) -> tuple[EvidenceProgress, ...]:
    _require_non_empty_string(event_ref, "evidence_progress_from_feedback.event_ref")
    if current_commitment_id is not None:
        _require_non_empty_string(
            current_commitment_id,
            "evidence_progress_from_feedback.current_commitment_id",
        )
    progress: list[EvidenceProgress] = []
    if commitment_result_kind == CommitmentStatus.CERTIFIED.value:
        progress.append(
            EvidenceProgress(
                "commitment_certified",
                event_ref,
                weight=1.0,
                commitment_id=current_commitment_id,
            )
        )
    elif commitment_result_kind == CommitmentStatus.BLOCKED.value:
        progress.append(
            EvidenceProgress(
                "blocker_surfaced",
                event_ref,
                weight=1.0,
                commitment_id=current_commitment_id,
            )
        )

    if evidence_progress_class in {"candidate", "artifact", "external-record"}:
        progress.append(EvidenceProgress("meaningful_evidence", event_ref, weight=0.8))
    elif (
        evidence_progress_class == "commitment"
        and commitment_result_kind != CommitmentStatus.UNCERTIFIED.value
    ):
        progress.append(EvidenceProgress("meaningful_evidence", event_ref, weight=0.8))
    elif evidence_progress_class in {"token-stream", "structured-stream"}:
        progress.append(EvidenceProgress("stream_only", event_ref, weight=0.2))

    if continuity_progress_class is not None and continuity_progress_class != "none":
        progress.append(EvidenceProgress("continuity_progress", event_ref, weight=0.7))

    normalized_warnings = frozenset(warning.strip().lower() for warning in warning_codes)
    if normalized_warnings & _USER_WAIT_WARNING_TAGS:
        progress.append(EvidenceProgress("blocker_surfaced", event_ref, weight=0.7))

    return tuple(progress)


def update_expectation_ledger_for_structured_step(
    *,
    ledger: ExpectationLedger,
    dispatch_decision: DispatchDecision,
    current_step: int,
    source_event_ref: str,
    evidence_progress_class: str | None,
    continuity_progress_class: str | None,
    commitment_result_kind: str | None,
    task_mode: str | None = None,
    warning_codes: tuple[str, ...] = (),
) -> ExpectationLedger:
    if not isinstance(ledger, ExpectationLedger):
        actual_type = type(ledger).__name__
        raise TypeError(
            "update_expectation_ledger_for_structured_step ledger must be ExpectationLedger, "
            f"got {actual_type}."
        )
    next_ledger = ledger
    commitment = forward_commitment_from_dispatch(
        dispatch_decision=dispatch_decision,
        source_event_ref=source_event_ref,
        opened_at_step=current_step,
        commitment_result_kind=commitment_result_kind,
        task_mode=task_mode,
    )
    if commitment is not None:
        next_ledger = open_expectation_from_forward_commitment(next_ledger, commitment)
    for progress in evidence_progress_from_feedback(
        event_ref=source_event_ref,
        evidence_progress_class=evidence_progress_class,
        continuity_progress_class=continuity_progress_class,
        commitment_result_kind=commitment_result_kind,
        current_commitment_id=commitment.commitment_id if commitment is not None else None,
        warning_codes=warning_codes,
    ):
        next_ledger = next_ledger.apply_progress(progress, current_step=current_step)
    if frozenset(warning.strip().lower() for warning in warning_codes) & _USER_WAIT_WARNING_TAGS:
        next_ledger = next_ledger.suspend_matching(
            horizon="next_step",
            suspension_state="waiting_on_user",
        )
    return next_ledger


def compute_resolution_deficit(
    ledger: ExpectationLedger,
    *,
    current_step: int,
) -> ResolutionDeficitState:
    if not isinstance(ledger, ExpectationLedger):
        actual_type = type(ledger).__name__
        raise TypeError(
            "compute_resolution_deficit ledger must be ExpectationLedger, "
            f"got {actual_type}."
        )
    _require_non_negative_int(current_step, "compute_resolution_deficit.current_step")
    due_records = tuple(record for record in ledger.active if record.is_due(current_step))
    overdue_records = tuple(
        record
        for record in due_records
        if record.horizon in {"immediate", "next_step"} and record.due_at_step < current_step
    )
    suspended_records = tuple(record for record in ledger.active if record.is_suspended)
    due_weight = sum(float(record.remaining_weight) for record in due_records)
    overdue_weight = sum(float(record.remaining_weight) for record in overdue_records)
    suspended_weight = sum(float(record.remaining_weight) for record in suspended_records)
    fulfilled_weight = sum(
        record.weight
        for record in ledger.resolved
        if record.suspension_state == "fulfilled"
        and record.resolution_class not in RELIEF_CLASSES
    )
    relief_weight = sum(
        record.weight
        for record in ledger.resolved
        if record.suspension_state == "fulfilled"
        and record.resolution_class in RELIEF_CLASSES
    )
    # Resolved history is diagnostic, not credit that can pay unrelated new debt.
    # Once a record is fulfilled it leaves active debt; current deficit is only
    # the still-open due/overdue remainder.
    raw_deficit = due_weight + overdue_weight
    denominator = max(0.1, due_weight + overdue_weight + suspended_weight)
    dominant = _dominant_deficit_kind(due_records)
    return ResolutionDeficitState(
        due_weight=round(due_weight, 6),
        fulfilled_weight=round(fulfilled_weight, 6),
        overdue_weight=round(overdue_weight, 6),
        suspended_weight=round(suspended_weight, 6),
        relief_weight=round(relief_weight, 6),
        negative_prediction_error=round(_clip01(raw_deficit / denominator), 6),
        dominant_deficit_kind=dominant,
    )


def _record_for_commitment(
    commitment: ForwardCommitment,
    *,
    weight: float,
    horizon: str,
    satisfaction_classes: tuple[str, ...],
    due_delta: int,
    deficit_kind: str,
    suspension_state: str = "active",
) -> ExpectationRecord:
    return ExpectationRecord(
        expectation_id=f"{commitment.commitment_id}:expectation",
        commitment_id=commitment.commitment_id,
        weight=weight,
        horizon=horizon,
        satisfaction_classes=satisfaction_classes,
        opened_at_step=commitment.opened_at_step,
        due_at_step=commitment.opened_at_step + due_delta,
        suspension_state=suspension_state,
        deficit_kind=deficit_kind,
    )


def _commitment_kind_from_tags(
    reason_tags: frozenset[str],
    lane: DispatchLane,
    commitment_result_kind: str | None,
) -> str | None:
    if reason_tags & _COMPLETION_REASON_TAGS:
        return "completion"
    if reason_tags & _VERIFICATION_REASON_TAGS or commitment_result_kind is not None:
        return "verification"
    if reason_tags & _ARTIFACT_REASON_TAGS:
        return "artifact_change"
    if reason_tags & _PLAN_REASON_TAGS:
        return "plan_commitment"
    if lane is DispatchLane.CANDIDATE_BEARING:
        return "plan_commitment"
    if lane is DispatchLane.FULL_COMMITMENT:
        return "verification"
    return None


def _assertiveness_for_dispatch(lane: DispatchLane) -> str:
    if lane is DispatchLane.FULL_COMMITMENT:
        return "high"
    if lane is DispatchLane.CANDIDATE_BEARING:
        return "medium"
    return "low"


def _scope_for_task_mode(task_mode: str | None) -> str:
    if task_mode is None:
        return "local_step"
    normalized = task_mode.strip().lower().replace("-", "_")
    if normalized == "resume_execute":
        return "branch"
    if normalized == "execute":
        return "task"
    return "local_step"


def _select_paydown_index(
    records: tuple[ExpectationRecord, ...],
    progress: EvidenceProgress,
    *,
    current_step: int,
) -> int | None:
    compatible: list[tuple[int, ExpectationRecord]] = []
    for index, record in enumerate(records):
        if progress.progress_class not in record.satisfaction_classes:
            continue
        if record.opened_at_step == current_step and record.horizon != "immediate":
            continue
        if progress.commitment_id is not None and record.commitment_id != progress.commitment_id:
            continue
        compatible.append((index, record))
    if not compatible:
        return None
    compatible.sort(key=lambda item: (item[1].due_at_step, item[1].opened_at_step, item[0]))
    return compatible[0][0]


def _ledger_with_caps(
    *,
    active: tuple[ExpectationRecord, ...],
    resolved: tuple[ExpectationRecord, ...],
) -> ExpectationLedger:
    active_records = tuple(sorted(active, key=lambda record: (record.opened_at_step, record.expectation_id)))
    resolved_records = tuple(
        sorted(resolved, key=lambda record: (record.due_at_step, record.expectation_id))
    )
    if len(active_records) > _MAX_ACTIVE_EXPECTATIONS:
        overflow_count = len(active_records) - _MAX_ACTIVE_EXPECTATIONS
        overflow = active_records[:overflow_count]
        kept = active_records[overflow_count:]
        expired = tuple(_expire_record(record) for record in overflow)
        active_records = kept
        resolved_records = (*resolved_records, *expired)
    resolved_records = resolved_records[-_MAX_RESOLVED_EXPECTATIONS:]
    return ExpectationLedger(active=active_records, resolved=resolved_records)


def _expire_record(record: ExpectationRecord) -> ExpectationRecord:
    return ExpectationRecord(
        expectation_id=record.expectation_id,
        commitment_id=record.commitment_id,
        weight=record.weight,
        horizon=record.horizon,
        satisfaction_classes=record.satisfaction_classes,
        opened_at_step=record.opened_at_step,
        due_at_step=record.due_at_step,
        suspension_state="expired",
        remaining_weight=0.0,
        evidence_refs=record.evidence_refs,
        deficit_kind=record.deficit_kind,
        resolution_class="degradation",
    )


def _dominant_deficit_kind(records: tuple[ExpectationRecord, ...]) -> str | None:
    kinds = tuple(record.deficit_kind for record in records if record.remaining_weight > 0.0)
    if not kinds:
        return None
    unique = sorted(set(kinds))
    if len(unique) == 1:
        return unique[0]
    return "mixed"


def _weight_for_assertiveness(assertiveness: str) -> float:
    if assertiveness == "high":
        return 1.0
    if assertiveness == "medium":
        return 0.6
    return 0.3


def _clip01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


def _require_non_empty_string(value: str, label: str) -> None:
    if not (isinstance(value, str) and value.strip()):
        raise ValueError(f"{label} must be non-empty after trimming.")


def _required_string(value: object, label: str) -> str:
    if not (isinstance(value, str) and value.strip()):
        raise ValueError(f"{label} must be a non-empty string.")
    return value.strip()


def _optional_string(value: object, label: str) -> str | None:
    if value is None:
        return None
    if not (isinstance(value, str) and value.strip()):
        raise ValueError(f"{label} must be a non-empty string or None.")
    return value.strip()


def _required_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{label} must be an integer.")
    return value


def _required_float(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{label} must be numeric.")
    return float(value)


def _require_non_negative_int(value: int, label: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{label} must be an integer.")
    if value < 0:
        raise ValueError(f"{label} must be non-negative.")


def _require_non_negative_float(value: float, label: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{label} must be numeric.")
    if float(value) < 0.0:
        raise ValueError(f"{label} must be non-negative.")


def _require_unitish_weight(value: float, label: str) -> None:
    _require_non_negative_float(value, label)
    if float(value) > 1.0:
        raise ValueError(f"{label} must be between 0.0 and 1.0.")


def _string_tuple(value: object, label: str) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        raise TypeError(f"{label} must be a list or tuple.")
    result = tuple(_required_string(entry, f"{label}[]") for entry in value)
    return result


def _dedupe_string_tuple(values: tuple[str, ...]) -> tuple[str, ...]:
    seen: list[str] = []
    for value in values:
        stripped = value.strip()
        if stripped and stripped not in seen:
            seen.append(stripped)
    return tuple(seen)


def _mapping_sequence(value: object, label: str) -> tuple[Mapping[str, Any], ...]:
    if value is None:
        return ()
    if not isinstance(value, (list, tuple)):
        raise TypeError(f"{label} must be a list or tuple.")
    if any(not isinstance(entry, Mapping) for entry in value):
        raise TypeError(f"{label} must contain only mapping entries.")
    return tuple(value)


__all__ = [
    "ASSERTIVENESS_LEVELS",
    "COMMITMENT_SCOPES",
    "DEFICIT_KINDS",
    "EXPECTATION_HORIZONS",
    "FORWARD_COMMITMENT_KINDS",
    "PAYDOWN_CLASSES",
    "SATISFACTION_CLASSES",
    "SUSPENSION_STATES",
    "EvidenceProgress",
    "ExpectationLedger",
    "ExpectationRecord",
    "ForwardCommitment",
    "ResolutionDeficitState",
    "compute_resolution_deficit",
    "evidence_progress_from_feedback",
    "expectation_record_for_forward_commitment",
    "forward_commitment_from_dispatch",
    "open_expectation_from_forward_commitment",
    "update_expectation_ledger_for_structured_step",
]
