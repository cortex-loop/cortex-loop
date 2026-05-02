# 04 — Cortex Internal State

This file appends the Cortex package internals most relevant to the communication problem. It intentionally excludes OpenAI, Gemini, Codex App, Codex CLI, and repo workflow infrastructure. This is the state Cortex has to communicate about.

Read this file as the raw `L_C` side of the communication problem. The code
below is not model-facing language and should not be copied into hook output.
Use it to identify what Cortex actually knows: event envelopes, observations,
feedback, brake state, goal debt, routing, support priors, augmentation,
capability envelopes, and verified-work runtime state. The task for `τ` is to
turn those states into task-local claim/evidence/obligation content without
leaking the implementation vocabulary.

### `cortex/core/envelopes.py`

```python
"""Extensible lifecycle-event envelope carriers."""

from __future__ import annotations

from dataclasses import dataclass, field

MetadataScalar = str | int | float | bool | None


@dataclass(frozen=True, slots=True)
class MetadataField:
    key: str
    value: MetadataScalar

    def __post_init__(self) -> None:
        if not (isinstance(self.key, str) and self.key.strip()):
            raise ValueError(
                "MetadataField.key must be non-empty after trimming.",
            )


@dataclass(frozen=True, slots=True)
class EventPayloadHandle:
    payload_kind: str
    payload_ref: str | None = None
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not (isinstance(self.payload_kind, str) and self.payload_kind.strip()):
            raise ValueError(
                "EventPayloadHandle.payload_kind must be non-empty after trimming.",
            )
        if self.payload_ref is not None and not (
            isinstance(self.payload_ref, str) and self.payload_ref.strip()
        ):
            raise ValueError(
                "EventPayloadHandle.payload_ref must be non-empty after trimming when provided.",
            )
        if any(not isinstance(field, MetadataField) for field in self.metadata):
            raise TypeError(
                "EventPayloadHandle.metadata must contain only MetadataField instances.",
            )


@dataclass(frozen=True, slots=True)
class LifecycleEventEnvelope:
    native_event_name: str
    facet_tags: frozenset[str] = field(default_factory=frozenset)
    channel_tags: frozenset[str] = field(default_factory=frozenset)
    extension_tags: frozenset[str] = field(default_factory=frozenset)
    payload_metadata: tuple[MetadataField, ...] = field(default_factory=tuple)
    payload_handle: EventPayloadHandle | None = None

    def __post_init__(self) -> None:
        if not self.native_event_name.strip():
            raise ValueError(
                "LifecycleEventEnvelope.native_event_name must be non-empty after trimming.",
            )
        if any(not (isinstance(tag, str) and tag.strip()) for tag in self.facet_tags):
            raise ValueError(
                "LifecycleEventEnvelope.facet_tags must contain only non-empty values after trimming.",
            )
        if any(not (isinstance(tag, str) and tag.strip()) for tag in self.channel_tags):
            raise ValueError(
                "LifecycleEventEnvelope.channel_tags must contain only non-empty values after trimming.",
            )
        if any(not (isinstance(tag, str) and tag.strip()) for tag in self.extension_tags):
            raise ValueError(
                "LifecycleEventEnvelope.extension_tags must contain only non-empty values after trimming.",
            )
        if any(not isinstance(field, MetadataField) for field in self.payload_metadata):
            raise TypeError(
                "LifecycleEventEnvelope.payload_metadata must contain only MetadataField instances.",
            )
        if self.payload_handle is not None and not isinstance(
            self.payload_handle,
            EventPayloadHandle,
        ):
            actual_type = type(self.payload_handle).__name__
            raise TypeError(
                "LifecycleEventEnvelope.payload_handle must be EventPayloadHandle when provided, "
                f"got {actual_type}.",
            )


__all__ = [
    "EventPayloadHandle",
    "LifecycleEventEnvelope",
    "MetadataField",
    "MetadataScalar",
]
```

### `cortex/core/observation.py`

```python
"""Lightweight observation carriers for the canonical cheap path."""

from __future__ import annotations

from dataclasses import dataclass, field

from .envelopes import EventPayloadHandle, LifecycleEventEnvelope, MetadataField


@dataclass(frozen=True, slots=True)
class PayloadView:
    payload_handle: EventPayloadHandle | None = None
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)
    summary_tags: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if self.payload_handle is not None and not isinstance(
            self.payload_handle,
            EventPayloadHandle,
        ):
            actual_type = type(self.payload_handle).__name__
            raise TypeError(
                "PayloadView.payload_handle must be EventPayloadHandle when provided, "
                f"got {actual_type}.",
            )
        if any(not isinstance(field, MetadataField) for field in self.metadata):
            raise TypeError(
                "PayloadView.metadata must contain only MetadataField instances.",
            )
        if any(not (isinstance(tag, str) and tag.strip()) for tag in self.summary_tags):
            raise ValueError(
                "PayloadView.summary_tags must contain only non-empty values after trimming.",
            )


@dataclass(frozen=True, slots=True)
class RuntimeRecord:
    record_type: str
    record_id: str | None = None
    tags: frozenset[str] = field(default_factory=frozenset)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not (isinstance(self.record_type, str) and self.record_type.strip()):
            raise ValueError(
                "RuntimeRecord.record_type must be non-empty after trimming.",
            )
        if self.record_id is not None and not (
            isinstance(self.record_id, str) and self.record_id.strip()
        ):
            raise ValueError(
                "RuntimeRecord.record_id must be non-empty after trimming when provided.",
            )
        if any(not (isinstance(tag, str) and tag.strip()) for tag in self.tags):
            raise ValueError(
                "RuntimeRecord.tags must contain only non-empty values after trimming.",
            )
        if any(not isinstance(field, MetadataField) for field in self.metadata):
            raise TypeError(
                "RuntimeRecord.metadata must contain only MetadataField instances.",
            )


@dataclass(frozen=True, slots=True)
class StructuredObservation:
    observation_type: str
    tags: frozenset[str] = field(default_factory=frozenset)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not (isinstance(self.observation_type, str) and self.observation_type.strip()):
            raise ValueError(
                "StructuredObservation.observation_type must be non-empty after trimming.",
            )
        if any(not (isinstance(tag, str) and tag.strip()) for tag in self.tags):
            raise ValueError(
                "StructuredObservation.tags must contain only non-empty values after trimming.",
            )
        if any(not isinstance(field, MetadataField) for field in self.metadata):
            raise TypeError(
                "StructuredObservation.metadata must contain only MetadataField instances.",
            )


@dataclass(frozen=True, slots=True)
class ObservationBundle:
    event: LifecycleEventEnvelope
    payload_view: PayloadView
    runtime_records: tuple[RuntimeRecord, ...] = field(default_factory=tuple)
    structured_observations: tuple[StructuredObservation, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not isinstance(self.event, LifecycleEventEnvelope):
            actual_type = type(self.event).__name__
            raise TypeError(
                "ObservationBundle.event must be LifecycleEventEnvelope, "
                f"got {actual_type}.",
            )
        if not isinstance(self.payload_view, PayloadView):
            actual_type = type(self.payload_view).__name__
            raise TypeError(
                "ObservationBundle.payload_view must be PayloadView, "
                f"got {actual_type}.",
            )
        if any(not isinstance(record, RuntimeRecord) for record in self.runtime_records):
            raise TypeError(
                "ObservationBundle.runtime_records must contain only RuntimeRecord instances.",
            )
        if any(
            not isinstance(observation, StructuredObservation)
            for observation in self.structured_observations
        ):
            raise TypeError(
                "ObservationBundle.structured_observations must contain only StructuredObservation instances.",
            )


__all__ = [
    "ObservationBundle",
    "PayloadView",
    "RuntimeRecord",
    "StructuredObservation",
]
```

### `cortex/core/dispatch.py`

```python
"""Conservative event-local dispatch classification for commitment handling."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .commitment_extract import (
    FALLBACK_COMMITMENT_SOURCE,
    NATIVE_COMMITMENT_SOURCE,
    NO_COMMITMENT_SOURCE,
    PAYLOAD_COMMITMENT_SOURCE,
    resolve_commitment_extract,
)
from .envelopes import MetadataField
from .observation import ObservationBundle


class DispatchLane(Enum):
    CHEAP = "cheap"
    CANDIDATE_BEARING = "candidate-bearing"
    FULL_COMMITMENT = "full-commitment"


@dataclass(frozen=True, slots=True)
class WakeDecision:
    full_commitment_required: bool
    reason_tags: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if not isinstance(self.full_commitment_required, bool):
            actual_type = type(self.full_commitment_required).__name__
            raise TypeError(
                "WakeDecision.full_commitment_required must be bool, "
                f"got {actual_type}.",
            )
        if any(not reason_tag.strip() for reason_tag in self.reason_tags):
            raise ValueError(
                "WakeDecision.reason_tags must contain only non-empty values after trimming.",
            )


@dataclass(frozen=True, slots=True)
class EvidencePlan:
    requires_candidate_extraction: bool
    requires_provenance: bool
    requires_boundary_assessment: bool

    def __post_init__(self) -> None:
        if not isinstance(self.requires_candidate_extraction, bool):
            actual_type = type(self.requires_candidate_extraction).__name__
            raise TypeError(
                "EvidencePlan.requires_candidate_extraction must be bool, "
                f"got {actual_type}.",
            )
        if not isinstance(self.requires_provenance, bool):
            actual_type = type(self.requires_provenance).__name__
            raise TypeError(
                "EvidencePlan.requires_provenance must be bool, "
                f"got {actual_type}.",
            )
        if not isinstance(self.requires_boundary_assessment, bool):
            actual_type = type(self.requires_boundary_assessment).__name__
            raise TypeError(
                "EvidencePlan.requires_boundary_assessment must be bool, "
                f"got {actual_type}.",
            )


@dataclass(frozen=True, slots=True)
class DispatchDecision:
    lane: DispatchLane
    wake_decision: WakeDecision
    evidence_plan: EvidencePlan
    candidate_present: bool
    commitment_carrier_source: str = NO_COMMITMENT_SOURCE
    structured_payload_violation: bool = False
    warnings: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not isinstance(self.lane, DispatchLane):
            actual_type = type(self.lane).__name__
            raise TypeError(
                "DispatchDecision.lane must be DispatchLane, "
                f"got {actual_type}.",
            )
        if not isinstance(self.wake_decision, WakeDecision):
            actual_type = type(self.wake_decision).__name__
            raise TypeError(
                "DispatchDecision.wake_decision must be WakeDecision, "
                f"got {actual_type}.",
            )
        if not isinstance(self.evidence_plan, EvidencePlan):
            actual_type = type(self.evidence_plan).__name__
            raise TypeError(
                "DispatchDecision.evidence_plan must be EvidencePlan, "
                f"got {actual_type}.",
            )
        if not isinstance(self.candidate_present, bool):
            actual_type = type(self.candidate_present).__name__
            raise TypeError(
                "DispatchDecision.candidate_present must be bool, "
                f"got {actual_type}.",
            )
        if self.commitment_carrier_source not in {
            NATIVE_COMMITMENT_SOURCE,
            PAYLOAD_COMMITMENT_SOURCE,
            FALLBACK_COMMITMENT_SOURCE,
            NO_COMMITMENT_SOURCE,
        }:
            raise ValueError(
                "DispatchDecision.commitment_carrier_source must be one of the canonical source labels: "
                "native, payload.stop_fields, fallback, none.",
            )
        if not isinstance(self.structured_payload_violation, bool):
            actual_type = type(self.structured_payload_violation).__name__
            raise TypeError(
                "DispatchDecision.structured_payload_violation must be bool, "
                f"got {actual_type}.",
            )
        if any(not isinstance(warning, str) for warning in self.warnings):
            raise TypeError(
                "DispatchDecision.warnings must contain only string entries.",
            )
        if any(not warning.strip() for warning in self.warnings):
            raise ValueError(
                "DispatchDecision.warnings must contain only non-empty strings after trimming.",
            )


FULL_COMMITMENT_REASON_ALIASES = {
    "commitment-subset": "commitment-subset",
    "host/commitment-subset": "commitment-subset",
    "commitment/event": "commitment-subset",
    "externally-consequential": "externally-consequential",
    "approval-gated": "approval-gated",
    "approval-required": "approval-gated",
    "durable-write": "durable-write",
    "write-executed": "durable-write",
    "write-committed": "durable-write",
    "approved-external-mutation": "approved-external-mutation",
    "external-mutation": "approved-external-mutation",
    "explicit-completion-claim": "explicit-completion-claim",
    "completion-claim": "explicit-completion-claim",
    "task-complete": "explicit-completion-claim",
    "boundary-required": "boundary-required",
    "boundary-check-required": "boundary-required",
}

CANDIDATE_REASON_ALIASES = {
    "proposal": "proposal-surface",
    "write-proposal": "proposal-surface",
    "approval/request": "proposal-surface",
    "approval-request": "proposal-surface",
    "patch-proposal": "proposal-surface",
    "write-intent": "proposal-surface",
    "candidate-bearing": "proposal-surface",
}

_CHEAP_EVIDENCE_PLAN = EvidencePlan(
    requires_candidate_extraction=False,
    requires_provenance=False,
    requires_boundary_assessment=False,
)
_CANDIDATE_EVIDENCE_PLAN = EvidencePlan(
    requires_candidate_extraction=True,
    requires_provenance=False,
    requires_boundary_assessment=False,
)
_FULL_EVIDENCE_PLAN = EvidencePlan(
    requires_candidate_extraction=True,
    requires_provenance=True,
    requires_boundary_assessment=True,
)


def classify_dispatch(
    observation: ObservationBundle,
    *,
    payload: Mapping[str, Any] | None = None,
    native_commitment_fields: Mapping[str, Any] | None = None,
    require_structured_commitment_payload: bool = False,
) -> DispatchDecision:
    if payload is None:
        payload_mapping: Mapping[str, Any] = {}
    elif isinstance(payload, Mapping):
        payload_mapping = payload
    else:
        raise TypeError("payload must be a mapping when provided")

    marker_tags = _collect_marker_tags(observation, payload_mapping)
    full_commitment_reasons = _collect_reason_tags(
        marker_tags,
        FULL_COMMITMENT_REASON_ALIASES,
    )
    candidate_reasons = _collect_reason_tags(marker_tags, CANDIDATE_REASON_ALIASES)

    extraction = None
    if native_commitment_fields is not None or payload_mapping or full_commitment_reasons or candidate_reasons:
        extraction = resolve_commitment_extract(
            payload_mapping,
            native_commitment_fields=native_commitment_fields,
            require_structured_commitment_payload=require_structured_commitment_payload,
        )

    candidate_present = bool(
        extraction
        and extraction.commitment_fields is not None
        and not extraction.structured_payload_violation
    )
    if candidate_present:
        candidate_reasons.add("candidate-present")

    if full_commitment_reasons:
        lane = DispatchLane.FULL_COMMITMENT
    elif candidate_reasons:
        lane = DispatchLane.CANDIDATE_BEARING
    else:
        lane = DispatchLane.CHEAP

    return DispatchDecision(
        lane=lane,
        wake_decision=WakeDecision(
            full_commitment_required=bool(full_commitment_reasons),
            reason_tags=frozenset(full_commitment_reasons | candidate_reasons),
        ),
        evidence_plan=_evidence_plan_for_lane(lane),
        candidate_present=candidate_present,
        commitment_carrier_source=(
            extraction.carrier_source if extraction is not None else NO_COMMITMENT_SOURCE
        ),
        structured_payload_violation=(
            extraction.structured_payload_violation if extraction is not None else False
        ),
        warnings=extraction.warnings if extraction is not None else (),
    )


def _evidence_plan_for_lane(lane: DispatchLane) -> EvidencePlan:
    if lane is DispatchLane.CHEAP:
        return _CHEAP_EVIDENCE_PLAN
    if lane is DispatchLane.CANDIDATE_BEARING:
        return _CANDIDATE_EVIDENCE_PLAN
    return _FULL_EVIDENCE_PLAN


def _collect_marker_tags(
    observation: ObservationBundle,
    payload: Mapping[str, Any],
) -> frozenset[str]:
    tags = {
        _canonical_tag(observation.event.native_event_name),
        *(_canonical_tag(tag) for tag in observation.event.facet_tags),
        *(_canonical_tag(tag) for tag in observation.event.channel_tags),
        *(_canonical_tag(tag) for tag in observation.event.extension_tags),
        *(_canonical_tag(tag) for tag in observation.payload_view.summary_tags),
    }

    for field in _iter_metadata_fields(observation):
        key = _canonical_tag(field.key)
        if key in FULL_COMMITMENT_REASON_ALIASES and _is_truthy_marker_value(field.value):
            tags.add(key)
        if key in CANDIDATE_REASON_ALIASES and _is_truthy_marker_value(field.value):
            tags.add(key)

    for key, value in payload.items():
        canonical_key = _canonical_tag(str(key))
        if canonical_key in FULL_COMMITMENT_REASON_ALIASES and _is_truthy_marker_value(value):
            tags.add(canonical_key)
        if canonical_key in CANDIDATE_REASON_ALIASES and _is_truthy_marker_value(value):
            tags.add(canonical_key)

    tags.discard("")
    return frozenset(tags)


def _iter_metadata_fields(observation: ObservationBundle) -> tuple[MetadataField, ...]:
    payload_handle = observation.payload_view.payload_handle
    handle_metadata = payload_handle.metadata if payload_handle is not None else ()
    return (
        *observation.event.payload_metadata,
        *observation.payload_view.metadata,
        *handle_metadata,
    )


def _collect_reason_tags(
    marker_tags: frozenset[str],
    aliases: Mapping[str, str],
) -> set[str]:
    return {reason for tag, reason in aliases.items() if tag in marker_tags}


def _canonical_tag(value: str) -> str:
    return value.strip().lower().replace("_", "-").replace(" ", "-")


def _is_truthy_marker_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "required"}
    return False


__all__ = [
    "DispatchDecision",
    "DispatchLane",
    "EvidencePlan",
    "WakeDecision",
    "classify_dispatch",
]
```

### `cortex/sre/feedback.py`

```python
"""Bounded realization-feedback carriers for the reference runtime shell."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from cortex.core.commitments import CommitmentStatus

from .brake import BrakeState
from .families import SoftControlFamily
from .opportunities import PROBE_RESULT_CLASSES

if TYPE_CHECKING:
    from .operator_routing import OperatorTaskMode

_ALLOWED_COMMITMENT_RESULT_KINDS = frozenset(status.value for status in CommitmentStatus)
_MAX_REFERENCE_FEEDBACK_WINDOW_ENTRIES = 3
EVIDENCE_PROGRESS_CLASSES = frozenset(
    {
        "none",
        "token-stream",
        "structured-stream",
        "candidate",
        "artifact",
        "external-record",
        "commitment",
    }
)
MEANINGFUL_EVIDENCE_PROGRESS_CLASSES = frozenset(
    {"candidate", "artifact", "external-record", "commitment"}
)
STREAM_ONLY_EVIDENCE_PROGRESS_CLASSES = frozenset(
    {"token-stream", "structured-stream"}
)
CONTINUITY_PROGRESS_CLASSES = frozenset(
    {"none", "pending-goals-reduced", "branch-closed", "returned-to-main"}
)


@dataclass(frozen=True, slots=True)
class ReferenceRealizationFeedback:
    selected_family: SoftControlFamily
    realized_family: SoftControlFamily
    brake_state: BrakeState
    task_mode: "OperatorTaskMode | None" = None
    commitment_result_kind: str | None = None
    warning_codes: tuple[str, ...] = field(default_factory=tuple)
    host_friction_tags: tuple[str, ...] = field(default_factory=tuple)
    evidence_progress_class: str | None = None
    evidence_state_moved: bool | None = None
    continuity_progress_class: str | None = None
    continuity_improved: bool | None = None
    probe_result_class: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.selected_family, SoftControlFamily):
            actual_type = type(self.selected_family).__name__
            raise TypeError(
                "ReferenceRealizationFeedback.selected_family must be SoftControlFamily, "
                f"got {actual_type}."
            )
        if not isinstance(self.realized_family, SoftControlFamily):
            actual_type = type(self.realized_family).__name__
            raise TypeError(
                "ReferenceRealizationFeedback.realized_family must be SoftControlFamily, "
                f"got {actual_type}."
            )
        if not isinstance(self.brake_state, BrakeState):
            actual_type = type(self.brake_state).__name__
            raise TypeError(
                "ReferenceRealizationFeedback.brake_state must be BrakeState, "
                f"got {actual_type}."
            )
        if self.task_mode is not None:
            from .operator_routing import OperatorTaskMode

            if not isinstance(self.task_mode, OperatorTaskMode):
                actual_type = type(self.task_mode).__name__
                raise TypeError(
                    "ReferenceRealizationFeedback.task_mode must be "
                    f"OperatorTaskMode | None, got {actual_type}."
                )
        if (
            self.commitment_result_kind is not None
            and self.commitment_result_kind not in _ALLOWED_COMMITMENT_RESULT_KINDS
        ):
            raise ValueError(
                "ReferenceRealizationFeedback.commitment_result_kind must be one of the "
                "canonical commitment status values or None."
            )
        if any(not (isinstance(code, str) and code.strip()) for code in self.warning_codes):
            raise ValueError(
                "ReferenceRealizationFeedback.warning_codes must contain only non-empty values after trimming."
            )
        if any(not (isinstance(tag, str) and tag.strip()) for tag in self.host_friction_tags):
            raise ValueError(
                "ReferenceRealizationFeedback.host_friction_tags must contain only non-empty values after trimming."
            )
        if (
            self.evidence_progress_class is not None
            and self.evidence_progress_class not in EVIDENCE_PROGRESS_CLASSES
        ):
            raise ValueError(
                "ReferenceRealizationFeedback.evidence_progress_class must be a canonical evidence progress class or None."
            )
        for field_name in ("evidence_state_moved", "continuity_improved"):
            value = getattr(self, field_name)
            if value is not None and not isinstance(value, bool):
                actual_type = type(value).__name__
                raise TypeError(
                    f"ReferenceRealizationFeedback.{field_name} must be bool | None, got {actual_type}."
                )
        if (
            self.continuity_progress_class is not None
            and self.continuity_progress_class not in CONTINUITY_PROGRESS_CLASSES
        ):
            raise ValueError(
                "ReferenceRealizationFeedback.continuity_progress_class must be a canonical continuity progress class or None."
            )
        if (
            self.probe_result_class is not None
            and self.probe_result_class not in PROBE_RESULT_CLASSES
        ):
            raise ValueError(
                "ReferenceRealizationFeedback.probe_result_class must be a canonical probe result class or None."
            )
        if self.evidence_progress_class is not None:
            derived_evidence_state_moved = (
                self.evidence_progress_class in MEANINGFUL_EVIDENCE_PROGRESS_CLASSES
            )
            if (
                self.evidence_state_moved is not None
                and self.evidence_state_moved is not derived_evidence_state_moved
            ):
                raise ValueError(
                    "ReferenceRealizationFeedback.evidence_state_moved must match the derived value from evidence_progress_class when both are provided."
                )
            object.__setattr__(
                self,
                "evidence_state_moved",
                derived_evidence_state_moved,
            )
        if self.continuity_progress_class is not None:
            derived_continuity_improved = self.continuity_progress_class != "none"
            if (
                self.continuity_improved is not None
                and self.continuity_improved is not derived_continuity_improved
            ):
                raise ValueError(
                    "ReferenceRealizationFeedback.continuity_improved must match the derived value from continuity_progress_class when both are provided."
                )
            object.__setattr__(
                self,
                "continuity_improved",
                derived_continuity_improved,
            )

    def as_summary(self) -> dict[str, object]:
        summary = {
            "selected_family": self.selected_family.value,
            "realized_family": self.realized_family.value,
            "brake_state": self.brake_state.value,
            "commitment_result_kind": self.commitment_result_kind,
            "warning_codes": list(self.warning_codes),
            "host_friction_tags": list(self.host_friction_tags),
        }
        if self.task_mode is not None:
            summary["task_mode"] = self.task_mode.value
        if self.evidence_progress_class is not None:
            summary["evidence_progress_class"] = self.evidence_progress_class
        if self.evidence_state_moved is not None:
            summary["evidence_state_moved"] = self.evidence_state_moved
        if self.continuity_progress_class is not None:
            summary["continuity_progress_class"] = self.continuity_progress_class
        if self.continuity_improved is not None:
            summary["continuity_improved"] = self.continuity_improved
        if self.probe_result_class is not None:
            summary["probe_result_class"] = self.probe_result_class
        return summary


@dataclass(frozen=True, slots=True)
class ReferenceRealizationFeedbackWindow:
    entries: tuple[ReferenceRealizationFeedback, ...] = ()

    def __post_init__(self) -> None:
        if len(self.entries) > _MAX_REFERENCE_FEEDBACK_WINDOW_ENTRIES:
            raise ValueError(
                "ReferenceRealizationFeedbackWindow.entries must contain at most three items."
            )
        if any(not isinstance(entry, ReferenceRealizationFeedback) for entry in self.entries):
            raise TypeError(
                "ReferenceRealizationFeedbackWindow.entries must contain only "
                "ReferenceRealizationFeedback instances."
            )

    def append(
        self,
        feedback: ReferenceRealizationFeedback,
    ) -> "ReferenceRealizationFeedbackWindow":
        if not isinstance(feedback, ReferenceRealizationFeedback):
            actual_type = type(feedback).__name__
            raise TypeError(
                "ReferenceRealizationFeedbackWindow.append feedback must be "
                f"ReferenceRealizationFeedback, got {actual_type}."
            )
        return ReferenceRealizationFeedbackWindow(
            entries=(self.entries + (feedback,))[-_MAX_REFERENCE_FEEDBACK_WINDOW_ENTRIES :]
        )


@dataclass(frozen=True, slots=True)
class ReferenceFeedbackWindowSummary:
    window_size: int = 0
    rejection_count: int = 0
    override_count: int = 0
    latched_count: int = 0
    clean_success_streak: int = 0
    evidence_state_move_count: int = 0
    meaningful_evidence_progress_count: int = 0
    stream_only_progress_count: int = 0
    continuity_improvement_count: int = 0
    family_change_without_evidence_count: int = 0
    same_family_no_progress_count: int = 0
    same_context_retry_count: int = 0
    goal_progress_floor: float = 0.0
    degradation_pressure_bonus: int = 0
    recent_evidence_progress_class: str | None = None
    recent_continuity_progress_class: str | None = None
    sustained_spike_flags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not 0 <= self.window_size <= _MAX_REFERENCE_FEEDBACK_WINDOW_ENTRIES:
            raise ValueError(
                "ReferenceFeedbackWindowSummary.window_size must be between 0 and 3."
            )
        for field_name in (
            "rejection_count",
            "override_count",
            "latched_count",
            "clean_success_streak",
            "evidence_state_move_count",
            "meaningful_evidence_progress_count",
            "stream_only_progress_count",
            "continuity_improvement_count",
            "family_change_without_evidence_count",
            "same_family_no_progress_count",
            "same_context_retry_count",
            "degradation_pressure_bonus",
        ):
            value = getattr(self, field_name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise TypeError(
                    f"ReferenceFeedbackWindowSummary.{field_name} must be a non-negative integer."
                )
        if not 0.0 <= self.goal_progress_floor <= 1.0:
            raise ValueError(
                "ReferenceFeedbackWindowSummary.goal_progress_floor must be between 0.0 and 1.0."
            )
        if (
            self.recent_evidence_progress_class is not None
            and self.recent_evidence_progress_class not in EVIDENCE_PROGRESS_CLASSES
        ):
            raise ValueError(
                "ReferenceFeedbackWindowSummary.recent_evidence_progress_class must be a canonical evidence progress class or None."
            )
        if (
            self.recent_continuity_progress_class is not None
            and self.recent_continuity_progress_class not in CONTINUITY_PROGRESS_CLASSES
        ):
            raise ValueError(
                "ReferenceFeedbackWindowSummary.recent_continuity_progress_class must be a canonical continuity progress class or None."
            )
        if any(not (isinstance(flag, str) and flag.strip()) for flag in self.sustained_spike_flags):
            raise ValueError(
                "ReferenceFeedbackWindowSummary.sustained_spike_flags must contain only non-empty values after trimming."
            )

    def as_summary(self) -> dict[str, object]:
        return {
            "window_size": self.window_size,
            "rejection_count": self.rejection_count,
            "override_count": self.override_count,
            "latched_count": self.latched_count,
            "clean_success_streak": self.clean_success_streak,
            "evidence_state_move_count": self.evidence_state_move_count,
            "meaningful_evidence_progress_count": self.meaningful_evidence_progress_count,
            "stream_only_progress_count": self.stream_only_progress_count,
            "continuity_improvement_count": self.continuity_improvement_count,
            "family_change_without_evidence_count": self.family_change_without_evidence_count,
            "same_family_no_progress_count": self.same_family_no_progress_count,
            "same_context_retry_count": self.same_context_retry_count,
            "goal_progress_floor": self.goal_progress_floor,
            "degradation_pressure_bonus": self.degradation_pressure_bonus,
            "recent_evidence_progress_class": self.recent_evidence_progress_class,
            "recent_continuity_progress_class": self.recent_continuity_progress_class,
            "sustained_spike_flags": list(self.sustained_spike_flags),
        }


def summarize_reference_feedback_window(
    window: ReferenceRealizationFeedbackWindow,
) -> ReferenceFeedbackWindowSummary:
    if not isinstance(window, ReferenceRealizationFeedbackWindow):
        actual_type = type(window).__name__
        raise TypeError(
            "summarize_reference_feedback_window.window must be "
            f"ReferenceRealizationFeedbackWindow, got {actual_type}."
        )

    entries = window.entries
    rejection_count = sum(1 for entry in entries if _has_rejection_warning(entry))
    override_count = sum(
        1 for entry in entries if entry.realized_family is not entry.selected_family
    )
    latched_count = sum(1 for entry in entries if entry.brake_state is BrakeState.LATCHED)
    evidence_state_move_count = sum(1 for entry in entries if entry.evidence_state_moved is True)
    meaningful_evidence_progress_count = sum(
        1 for entry in entries if _has_meaningful_evidence_progress(entry)
    )
    stream_only_progress_count = sum(1 for entry in entries if _has_stream_only_progress(entry))
    continuity_improvement_count = sum(1 for entry in entries if entry.continuity_improved is True)
    family_change_without_evidence_count = sum(
        1
        for previous, current in zip(entries, entries[1:])
        if previous.selected_family is not current.selected_family
        and _lacks_progress(current)
    )
    same_family_no_progress_count = sum(
        1
        for previous, current in zip(entries, entries[1:])
        if previous.selected_family is current.selected_family
        and _lacks_progress(current)
    )
    same_context_retry_count = sum(
        1
        for previous, current in zip(entries, entries[1:])
        if _is_same_context_retry(previous, current)
    )

    clean_success_streak = 0
    for entry in reversed(entries):
        if (
            entry.warning_codes
            or entry.realized_family is not entry.selected_family
            or entry.brake_state is not BrakeState.QUIESCENT
        ):
            break
        clean_success_streak += 1

    rejection_floor = 0.0
    if rejection_count >= 2:
        rejection_floor = 0.70
    elif rejection_count == 1:
        rejection_floor = 0.55

    override_floor = 0.0
    if override_count >= 2:
        override_floor = 0.60
    elif override_count == 1:
        override_floor = 0.45

    typed_no_progress_floor = 0.0
    if entries and _is_low_progress_feedback(entries[-1]):
        typed_no_progress_floor = 0.30
    if len(entries) >= 2 and _is_same_context_low_progress_pair(entries[-2], entries[-1]):
        typed_no_progress_floor = 0.45

    degradation_pressure_bonus = 0
    if (
        rejection_count >= 2
        or latched_count >= 2
        or (rejection_count >= 1 and override_count >= 1)
    ):
        degradation_pressure_bonus = 2
    elif (
        rejection_count == 1
        or override_count >= 1
        or latched_count == 1
        or family_change_without_evidence_count >= 1
        or same_context_retry_count >= 1
    ):
        degradation_pressure_bonus = 1
    if family_change_without_evidence_count >= 2:
        degradation_pressure_bonus = max(degradation_pressure_bonus, 2)
    if same_context_retry_count >= 2:
        degradation_pressure_bonus = max(degradation_pressure_bonus, 2)

    sustained_spike_flags: list[str] = []
    if any(
        code.startswith("continuity-rejected:")
        for entry in entries
        for code in entry.warning_codes
    ):
        sustained_spike_flags.append("prior-continuity-rejection")
    if any(
        code.startswith("session-rejected:")
        for entry in entries
        for code in entry.warning_codes
    ):
        sustained_spike_flags.append("prior-session-mismatch")
    if override_count >= 1:
        sustained_spike_flags.append("prior-enforcement-override")
    if rejection_count >= 2 or (rejection_count >= 1 and override_count >= 1):
        sustained_spike_flags.append("sustained-feedback-disruption")
    if latched_count >= 2:
        sustained_spike_flags.append("sustained-latched-brake")
    if family_change_without_evidence_count >= 1:
        sustained_spike_flags.append("prior-non-productive-family-switch")
    if family_change_without_evidence_count >= 2:
        sustained_spike_flags.append("sustained-oscillation")

    return ReferenceFeedbackWindowSummary(
        window_size=len(entries),
        rejection_count=rejection_count,
        override_count=override_count,
        latched_count=latched_count,
        clean_success_streak=clean_success_streak,
        evidence_state_move_count=evidence_state_move_count,
        meaningful_evidence_progress_count=meaningful_evidence_progress_count,
        stream_only_progress_count=stream_only_progress_count,
        continuity_improvement_count=continuity_improvement_count,
        family_change_without_evidence_count=family_change_without_evidence_count,
        same_family_no_progress_count=same_family_no_progress_count,
        same_context_retry_count=same_context_retry_count,
        goal_progress_floor=max(rejection_floor, override_floor, typed_no_progress_floor),
        degradation_pressure_bonus=degradation_pressure_bonus,
        recent_evidence_progress_class=(
            entries[-1].evidence_progress_class if entries else None
        ),
        recent_continuity_progress_class=(
            entries[-1].continuity_progress_class if entries else None
        ),
        sustained_spike_flags=tuple(sustained_spike_flags),
    )


def _lacks_progress(entry: ReferenceRealizationFeedback) -> bool:
    has_signature = bool(
        entry.task_mode is not None
        or entry.evidence_progress_class is not None
        or entry.evidence_state_moved is not None
        or entry.continuity_progress_class is not None
        or entry.continuity_improved is not None
        or entry.probe_result_class is not None
    )
    return has_signature and not _has_meaningful_progress(entry)


def _has_meaningful_evidence_progress(entry: ReferenceRealizationFeedback) -> bool:
    return bool(
        entry.evidence_progress_class in MEANINGFUL_EVIDENCE_PROGRESS_CLASSES
        or entry.evidence_state_moved is True
    )


def _has_continuity_progress(entry: ReferenceRealizationFeedback) -> bool:
    return bool(
        entry.continuity_progress_class is not None
        and entry.continuity_progress_class != "none"
    ) or entry.continuity_improved is True


def _has_probe_success(entry: ReferenceRealizationFeedback) -> bool:
    return entry.probe_result_class == "succeeded"


def _has_meaningful_progress(entry: ReferenceRealizationFeedback) -> bool:
    return bool(
        _has_meaningful_evidence_progress(entry)
        or _has_continuity_progress(entry)
        or _has_probe_success(entry)
    )


def _has_stream_only_progress(entry: ReferenceRealizationFeedback) -> bool:
    return bool(
        entry.evidence_progress_class in STREAM_ONLY_EVIDENCE_PROGRESS_CLASSES
        and not _has_meaningful_progress(entry)
    )


def _is_low_progress_feedback(entry: ReferenceRealizationFeedback) -> bool:
    if _has_meaningful_progress(entry):
        return False
    if entry.evidence_progress_class in {"none", *STREAM_ONLY_EVIDENCE_PROGRESS_CLASSES}:
        return True
    return (
        entry.evidence_progress_class is None
        and (
            entry.evidence_state_moved is False
            or entry.continuity_improved is False
            or entry.task_mode is not None
            or entry.probe_result_class is not None
        )
    )


def _warning_bucket(entry: ReferenceRealizationFeedback) -> str:
    if not entry.warning_codes:
        return "clean"
    if any(code.startswith("continuity-rejected:") for code in entry.warning_codes):
        return "continuity-rejection"
    if any(code.startswith("session-rejected:") for code in entry.warning_codes):
        return "session-rejection"
    if any(code.startswith("guarded-feedback-enforced:") for code in entry.warning_codes):
        return "guarded-enforcement"
    if any(code.startswith("latched-brake-enforced:") for code in entry.warning_codes):
        return "latched-enforcement"
    return "other-warning"


def _probe_bucket(entry: ReferenceRealizationFeedback) -> str:
    return entry.probe_result_class if entry.probe_result_class is not None else "none"


def _is_same_context_retry(
    previous: ReferenceRealizationFeedback,
    current: ReferenceRealizationFeedback,
) -> bool:
    return bool(
        previous.selected_family is current.selected_family
        and previous.task_mode is not None
        and current.task_mode is not None
        and previous.task_mode is current.task_mode
        and tuple(sorted(previous.host_friction_tags))
        == tuple(sorted(current.host_friction_tags))
        and _warning_bucket(previous) == _warning_bucket(current)
        and _probe_bucket(previous) == _probe_bucket(current)
        and _lacks_progress(current)
    )


def _is_same_context_low_progress_pair(
    previous: ReferenceRealizationFeedback,
    current: ReferenceRealizationFeedback,
) -> bool:
    return bool(
        previous.selected_family is current.selected_family
        and previous.task_mode is not None
        and current.task_mode is not None
        and previous.task_mode is current.task_mode
        and tuple(sorted(previous.host_friction_tags))
        == tuple(sorted(current.host_friction_tags))
        and _warning_bucket(previous) == _warning_bucket(current)
        and _probe_bucket(previous) == _probe_bucket(current)
        and _is_low_progress_feedback(previous)
        and _is_low_progress_feedback(current)
    )


def latest_same_context_retry_feedback(
    window: ReferenceRealizationFeedbackWindow,
) -> ReferenceRealizationFeedback | None:
    if not isinstance(window, ReferenceRealizationFeedbackWindow):
        actual_type = type(window).__name__
        raise TypeError(
            "latest_same_context_retry_feedback.window must be "
            f"ReferenceRealizationFeedbackWindow, got {actual_type}."
        )
    entries = window.entries
    if len(entries) < 2:
        return None
    previous, current = entries[-2], entries[-1]
    if _is_same_context_retry(previous, current):
        return current
    return None


def _has_rejection_warning(entry: ReferenceRealizationFeedback) -> bool:
    return any(
        code.startswith(("continuity-rejected:", "session-rejected:"))
        for code in entry.warning_codes
    )


__all__ = [
    "CONTINUITY_PROGRESS_CLASSES",
    "EVIDENCE_PROGRESS_CLASSES",
    "MEANINGFUL_EVIDENCE_PROGRESS_CLASSES",
    "ReferenceFeedbackWindowSummary",
    "ReferenceRealizationFeedback",
    "ReferenceRealizationFeedbackWindow",
    "STREAM_ONLY_EVIDENCE_PROGRESS_CLASSES",
    "latest_same_context_retry_feedback",
    "summarize_reference_feedback_window",
]
```

### `cortex/sre/brake.py`

```python
"""Compact brake-state evaluation for SRE uncertainty handling."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .uncertainty import UncertaintyEstimate

_LATCHING_SPIKES = frozenset(
    {
        "contradiction-expected-vs-observed",
        "sudden-degradation",
        "environment-inconsistency",
    }
)


class BrakeState(str, Enum):
    QUIESCENT = "quiescent"
    GUARDED = "guarded"
    LATCHED = "latched"


_TONIC_DECAY_RHO = 0.60
_TONIC_ENTER_GUARDED = 0.35


def _clip_unit(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


@dataclass(frozen=True, slots=True)
class BrakeTonic:
    """Smoothed EMA baseline for brake pressure across steps.

    SRE_2 §7.5 narrows the brake exit to threshold-hysteresis-only; the
    rest-side EMA (`tonic_quiescence`) is retired because the landed exit
    gate did not consume it and carrying it as diagnostics-only telemetry
    drifted doctrine from code.
    """

    tonic_pressure: float = 0.0

    def __post_init__(self) -> None:
        if not 0.0 <= float(self.tonic_pressure) <= 1.0:
            raise ValueError("BrakeTonic.tonic_pressure must be between 0.0 and 1.0.")


@dataclass(frozen=True, slots=True)
class BrakeEvaluation:
    state: BrakeState
    dominant_cause: str | None = None
    max_uncertainty: float = 0.0
    spike_tags: frozenset[str] = field(default_factory=frozenset)
    tonic: BrakeTonic | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.state, BrakeState):
            actual_type = type(self.state).__name__
            raise TypeError(
                "BrakeEvaluation.state must be BrakeState, "
                f"got {actual_type}."
            )
        if any(not tag.strip() for tag in self.spike_tags):
            raise ValueError(
                "BrakeEvaluation.spike_tags must contain only non-empty values after trimming."
            )
        if self.dominant_cause is not None and not self.dominant_cause.strip():
            raise ValueError(
                "BrakeEvaluation.dominant_cause must be non-empty after trimming when provided."
            )
        if self.tonic is not None and not isinstance(self.tonic, BrakeTonic):
            actual_type = type(self.tonic).__name__
            raise TypeError(
                f"BrakeEvaluation.tonic must be BrakeTonic when provided, got {actual_type}."
            )


def evaluate_brake_state(
    uncertainty_estimates: tuple[UncertaintyEstimate, ...],
    *,
    repeated_failures: int = 0,
    repeated_degradations: int = 0,
    missing_resume_anchor: bool = False,
    host_friction_level: float = 0.0,
    prior_state: BrakeState | None = None,
    prior_tonic: BrakeTonic | None = None,
) -> BrakeEvaluation:
    for estimate in uncertainty_estimates:
        if not isinstance(estimate, UncertaintyEstimate):
            actual_type = type(estimate).__name__
            raise TypeError(
                "evaluate_brake_state.uncertainty_estimates must contain only "
                f"UncertaintyEstimate instances, got {actual_type}."
            )
    if repeated_failures < 0:
        raise ValueError("repeated_failures must be non-negative.")
    if repeated_degradations < 0:
        raise ValueError("repeated_degradations must be non-negative.")
    if not 0.0 <= host_friction_level <= 1.0:
        raise ValueError("host_friction_level must be between 0.0 and 1.0.")
    if prior_state is not None and not isinstance(prior_state, BrakeState):
        actual_type = type(prior_state).__name__
        raise TypeError(
            "evaluate_brake_state.prior_state must be BrakeState | None, "
            f"got {actual_type}."
        )
    if prior_tonic is not None and not isinstance(prior_tonic, BrakeTonic):
        actual_type = type(prior_tonic).__name__
        raise TypeError(
            f"evaluate_brake_state.prior_tonic must be BrakeTonic | None, got {actual_type}."
        )

    max_estimate = _max_estimate(uncertainty_estimates)
    spike_tags = _all_spike_tags(uncertainty_estimates)
    next_tonic = _update_brake_tonic(
        prior_tonic=prior_tonic,
        max_uncertainty=max_estimate.level,
        host_friction_level=host_friction_level,
        spike_tags=spike_tags,
        repeated_failures=repeated_failures,
        repeated_degradations=repeated_degradations,
    )

    if (
        spike_tags & _LATCHING_SPIKES
        or repeated_failures >= 2
        or repeated_degradations >= 2
        or max_estimate.level >= 0.85
    ):
        return BrakeEvaluation(
            state=BrakeState.LATCHED,
            dominant_cause=_dominant_cause(
                max_estimate=max_estimate,
                spike_tags=spike_tags,
                repeated_failures=repeated_failures,
                repeated_degradations=repeated_degradations,
                missing_resume_anchor=missing_resume_anchor,
                host_friction_level=host_friction_level,
            ),
            max_uncertainty=max_estimate.level,
            spike_tags=spike_tags,
            tonic=next_tonic,
        )

    if _should_stay_latched(
        prior_state=prior_state,
        spike_tags=spike_tags,
        repeated_failures=repeated_failures,
        repeated_degradations=repeated_degradations,
        host_friction_level=host_friction_level,
        max_uncertainty=max_estimate.level,
    ):
        return BrakeEvaluation(
            state=BrakeState.LATCHED,
            dominant_cause=_dominant_cause(
                max_estimate=max_estimate,
                spike_tags=spike_tags,
                repeated_failures=repeated_failures,
                repeated_degradations=repeated_degradations,
                missing_resume_anchor=missing_resume_anchor,
                host_friction_level=host_friction_level,
            ),
            max_uncertainty=max_estimate.level,
            spike_tags=spike_tags,
            tonic=next_tonic,
        )

    if _should_be_guarded(
        prior_state=prior_state,
        spike_tags=spike_tags,
        repeated_failures=repeated_failures,
        repeated_degradations=repeated_degradations,
        missing_resume_anchor=missing_resume_anchor,
        host_friction_level=host_friction_level,
        max_uncertainty=max_estimate.level,
        next_tonic=next_tonic,
    ):
        return BrakeEvaluation(
            state=BrakeState.GUARDED,
            dominant_cause=_dominant_cause(
                max_estimate=max_estimate,
                spike_tags=spike_tags,
                repeated_failures=repeated_failures,
                repeated_degradations=repeated_degradations,
                missing_resume_anchor=missing_resume_anchor,
                host_friction_level=host_friction_level,
            ),
            max_uncertainty=max_estimate.level,
            spike_tags=spike_tags,
            tonic=next_tonic,
        )

    return BrakeEvaluation(
        state=BrakeState.QUIESCENT,
        dominant_cause=None,
        max_uncertainty=max_estimate.level,
        spike_tags=spike_tags,
        tonic=next_tonic,
    )


def _should_stay_latched(
    *,
    prior_state: BrakeState | None,
    spike_tags: frozenset[str],
    repeated_failures: int,
    repeated_degradations: int,
    host_friction_level: float,
    max_uncertainty: float,
) -> bool:
    if prior_state is not BrakeState.LATCHED:
        return False
    return bool(
        spike_tags & _LATCHING_SPIKES
        or repeated_failures >= 2
        or repeated_degradations >= 2
        or host_friction_level >= 0.75
        or max_uncertainty >= 0.70
    )


def _should_be_guarded(
    *,
    prior_state: BrakeState | None,
    spike_tags: frozenset[str],
    repeated_failures: int,
    repeated_degradations: int,
    missing_resume_anchor: bool,
    host_friction_level: float,
    max_uncertainty: float,
    next_tonic: BrakeTonic,
) -> bool:
    # Immediate phasic entry: spike tags, contradiction, missing anchor.
    if spike_tags or missing_resume_anchor:
        return True
    # Repeated failure/degradation remain immediate (already counter-bounded).
    if repeated_failures >= 1 or repeated_degradations >= 1:
        return True
    # Soft-pressure paths: friction or uncertainty cross threshold.
    guarded_host_threshold = 0.55 if prior_state is BrakeState.GUARDED else 0.60
    guarded_uncertainty_threshold = 0.45 if prior_state is BrakeState.GUARDED else 0.55
    phasic_soft_pressure = (
        host_friction_level >= guarded_host_threshold
        or max_uncertainty >= guarded_uncertainty_threshold
    )
    if not phasic_soft_pressure:
        return False
    # Already guarded — stay on phasic evidence alone (exit-side hysteresis).
    if prior_state is BrakeState.GUARDED:
        return True
    # Entry from quiescent: require tonic confirmation so a single noisy tick
    # does not flip brake state (SRE_2 §7.5 tonic-pressure gate).
    return next_tonic.tonic_pressure >= _TONIC_ENTER_GUARDED


def _update_brake_tonic(
    *,
    prior_tonic: BrakeTonic | None,
    max_uncertainty: float,
    host_friction_level: float,
    spike_tags: frozenset[str],
    repeated_failures: int,
    repeated_degradations: int,
) -> BrakeTonic:
    current_pressure = _clip_unit(
        max(
            max_uncertainty,
            host_friction_level,
            0.6 if (spike_tags & _LATCHING_SPIKES) else 0.0,
            0.5 if repeated_failures >= 1 else 0.0,
            0.5 if repeated_degradations >= 1 else 0.0,
        )
    )

    if prior_tonic is None:
        next_pressure = current_pressure
    else:
        next_pressure = _clip_unit(
            (_TONIC_DECAY_RHO * prior_tonic.tonic_pressure)
            + ((1.0 - _TONIC_DECAY_RHO) * current_pressure)
        )

    return BrakeTonic(tonic_pressure=next_pressure)


def _max_estimate(
    uncertainty_estimates: tuple[UncertaintyEstimate, ...],
) -> UncertaintyEstimate:
    if not uncertainty_estimates:
        return UncertaintyEstimate(class_tag="evidence", level=0.0)
    return max(uncertainty_estimates, key=lambda estimate: estimate.level)


def _all_spike_tags(
    uncertainty_estimates: tuple[UncertaintyEstimate, ...],
) -> frozenset[str]:
    spike_tags: set[str] = set()
    for estimate in uncertainty_estimates:
        spike_tags.update(estimate.spike_tags)
    return frozenset(spike_tags)


def _dominant_cause(
    *,
    max_estimate: UncertaintyEstimate,
    spike_tags: frozenset[str],
    repeated_failures: int,
    repeated_degradations: int,
    missing_resume_anchor: bool,
    host_friction_level: float,
) -> str:
    if spike_tags & _LATCHING_SPIKES:
        return sorted(spike_tags & _LATCHING_SPIKES)[0]
    if repeated_failures >= 1:
        return "repeated-failure"
    if repeated_degradations >= 1:
        return "repeated-degradation"
    if missing_resume_anchor:
        return "missing-resume-anchor"
    if host_friction_level >= 0.6:
        return "host-friction"
    if spike_tags:
        return sorted(spike_tags)[0]
    return f"uncertainty:{max_estimate.class_tag}"


__all__ = ["BrakeEvaluation", "BrakeState", "BrakeTonic", "evaluate_brake_state"]
```

### `cortex/sre/goal_debt.py`

```python
"""Typed goal-debt and closure-pressure state over bounded runtime signals."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from numbers import Real

from .brake import BrakeState


def _clip_unit(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


@dataclass(frozen=True, slots=True)
class GoalDebtState:
    unfinished_goal_debt: float
    contradiction_rejection_debt: float
    verification_debt: float
    quota_burden_stop_pressure: float

    def __post_init__(self) -> None:
        for field_name in asdict(self):
            value = getattr(self, field_name)
            if not isinstance(value, Real):
                actual_type = type(value).__name__
                raise TypeError(f"GoalDebtState.{field_name} must be numeric, got {actual_type}.")
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(f"GoalDebtState.{field_name} must be between 0.0 and 1.0.")

    def as_payload(self) -> dict[str, float]:
        return {
            field_name: round(float(value), 4)
            for field_name, value in asdict(self).items()
        }


@dataclass(frozen=True, slots=True)
class ClosurePressureState:
    goal_debt: GoalDebtState
    closure_pressure: float
    closure_required: bool
    closure_reason_tags: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.goal_debt, GoalDebtState):
            actual_type = type(self.goal_debt).__name__
            raise TypeError(
                "ClosurePressureState.goal_debt must be GoalDebtState, "
                f"got {actual_type}."
            )
        if not isinstance(self.closure_required, bool):
            actual_type = type(self.closure_required).__name__
            raise TypeError(
                "ClosurePressureState.closure_required must be bool, "
                f"got {actual_type}."
            )
        if not isinstance(self.closure_pressure, Real):
            actual_type = type(self.closure_pressure).__name__
            raise TypeError(
                "ClosurePressureState.closure_pressure must be numeric, "
                f"got {actual_type}."
            )
        if not 0.0 <= float(self.closure_pressure) <= 1.0:
            raise ValueError(
                "ClosurePressureState.closure_pressure must be between 0.0 and 1.0."
            )
        if any(not (isinstance(tag, str) and tag.strip()) for tag in self.closure_reason_tags):
            raise ValueError(
                "ClosurePressureState.closure_reason_tags must contain only non-empty values."
            )


def build_goal_debt_state(
    *,
    active_track_ref: str,
    pending_goal_refs: tuple[str, ...],
    continuity_warnings: tuple[str, ...],
    continuity_reminders: tuple[str, ...],
    degradation_pressure_bonus: int,
    sustained_spike_flags: tuple[str, ...],
    repeated_failure_pressure: float,
    verification_conflict_pressure: float,
    quota_pressure: float,
    brake_state: BrakeState,
) -> GoalDebtState:
    if not isinstance(brake_state, BrakeState):
        actual_type = type(brake_state).__name__
        raise TypeError(
            "build_goal_debt_state.brake_state must be BrakeState, "
            f"got {actual_type}."
        )

    continuity_rejection_present = any(
        warning.startswith("continuity-rejected:")
        for warning in continuity_warnings
    )
    unfinished_goal_debt = 0.0
    if pending_goal_refs or continuity_reminders:
        unfinished_goal_debt = 1.0
    elif active_track_ref != "main":
        unfinished_goal_debt = 0.7

    contradiction_rejection_debt = _clip_unit(
        (1.0 if continuity_rejection_present else 0.0)
        + (0.20 * float(min(3, degradation_pressure_bonus)))
        + (0.15 if sustained_spike_flags else 0.0)
        + (0.20 * float(repeated_failure_pressure))
    )
    verification_debt = _clip_unit(
        float(verification_conflict_pressure)
        + (0.10 if continuity_rejection_present else 0.0)
    )
    quota_burden_stop_pressure = _clip_unit(
        float(quota_pressure)
        + (0.15 if brake_state is BrakeState.GUARDED else 0.0)
        + (0.25 if brake_state is BrakeState.LATCHED else 0.0)
    )
    return GoalDebtState(
        unfinished_goal_debt=unfinished_goal_debt,
        contradiction_rejection_debt=contradiction_rejection_debt,
        verification_debt=verification_debt,
        quota_burden_stop_pressure=quota_burden_stop_pressure,
    )


def build_closure_pressure_state(
    *,
    active_track_ref: str,
    pending_goal_refs: tuple[str, ...],
    continuity_warnings: tuple[str, ...],
    continuity_reminders: tuple[str, ...],
    degradation_pressure_bonus: int,
    sustained_spike_flags: tuple[str, ...],
    repeated_failure_pressure: float,
    verification_conflict_pressure: float,
    quota_pressure: float,
    brake_state: BrakeState,
) -> ClosurePressureState:
    goal_debt = build_goal_debt_state(
        active_track_ref=active_track_ref,
        pending_goal_refs=pending_goal_refs,
        continuity_warnings=continuity_warnings,
        continuity_reminders=continuity_reminders,
        degradation_pressure_bonus=degradation_pressure_bonus,
        sustained_spike_flags=sustained_spike_flags,
        repeated_failure_pressure=repeated_failure_pressure,
        verification_conflict_pressure=verification_conflict_pressure,
        quota_pressure=quota_pressure,
        brake_state=brake_state,
    )
    tags: set[str] = set()
    continuity_rejection_present = any(
        warning.startswith("continuity-rejected:")
        for warning in continuity_warnings
    )
    if pending_goal_refs:
        tags.add("pending_goal_debt")
    if continuity_rejection_present:
        tags.add("continuity_rejection")
    if continuity_reminders:
        tags.add("continuity_reminder")
    if brake_state is BrakeState.LATCHED:
        tags.add("latched_brake")
    if degradation_pressure_bonus > 0:
        tags.add("degradation_pressure")
    if sustained_spike_flags:
        tags.add("contradiction_spike")

    closure_pressure = max(
        goal_debt.unfinished_goal_debt,
        goal_debt.contradiction_rejection_debt,
        goal_debt.verification_debt,
        goal_debt.quota_burden_stop_pressure,
    )
    return ClosurePressureState(
        goal_debt=goal_debt,
        closure_pressure=closure_pressure,
        closure_required=bool(tags),
        closure_reason_tags=tuple(sorted(tags)),
    )


__all__ = [
    "ClosurePressureState",
    "GoalDebtState",
    "build_closure_pressure_state",
    "build_goal_debt_state",
]
```

### `cortex/sre/operator_routing.py`

```python
"""Bounded operator-routing realization over low-dimensional task-state geometry."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from enum import Enum
from numbers import Real

from .executive_summary import ExecutiveSignalSummary
from .modulators import (
    ExecutiveModulatorMemory,
    ExecutiveModulatorState,
    ExecutiveModulatorUpdate,
    ZERO_EXECUTIVE_MODULATOR_MEMORY,
)
from .policy_view import ExecutivePolicyView, build_executive_policy_view


class OperatorTaskMode(str, Enum):
    INSPECT = "inspect"
    EXECUTE = "execute"
    RESUME_EXECUTE = "resume_execute"


class OperatorRouteProfile(str, Enum):
    INSPECT_LIGHT = "inspect_light"
    EXECUTE_STANDARD = "execute_standard"
    EXECUTE_GUARDED = "execute_guarded"
    CONTINUITY_STANDARD = "continuity_standard"
    CONTINUITY_GUARDED = "continuity_guarded"
    BLOCKED = "blocked"


class OperatorContractBindingProfile(str, Enum):
    STANDARD = "standard"
    LEAN = "lean"


class OperatorBrainCapabilityMismatchLevel(str, Enum):
    NONE = "none"
    DEGRADE = "degrade"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True, slots=True)
class OperatorBrainCapabilityEnvelope:
    continuity_tolerance: float
    verification_tolerance: float
    output_contract_tolerance: float

    def __post_init__(self) -> None:
        for field_name in (
            "continuity_tolerance",
            "verification_tolerance",
            "output_contract_tolerance",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, Real):
                actual_type = type(value).__name__
                raise TypeError(
                    f"OperatorBrainCapabilityEnvelope.{field_name} must be numeric, "
                    f"got {actual_type}."
                )
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(
                    f"OperatorBrainCapabilityEnvelope.{field_name} must be between 0.0 and 1.0."
                )

    def as_payload(self) -> dict[str, float]:
        return {
            "continuity_tolerance": round(float(self.continuity_tolerance), 4),
            "verification_tolerance": round(float(self.verification_tolerance), 4),
            "output_contract_tolerance": round(
                float(self.output_contract_tolerance), 4
            ),
        }


@dataclass(frozen=True, slots=True)
class OperatorBrainCapabilityAssessment:
    continuity_mismatch: float
    verification_mismatch: float
    contract_mismatch: float
    level: OperatorBrainCapabilityMismatchLevel
    contract_binding_profile: OperatorContractBindingProfile
    fallback_family: str | None = None
    reason_tags: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        for field_name in (
            "continuity_mismatch",
            "verification_mismatch",
            "contract_mismatch",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, Real):
                actual_type = type(value).__name__
                raise TypeError(
                    f"OperatorBrainCapabilityAssessment.{field_name} must be numeric, "
                    f"got {actual_type}."
                )
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(
                    f"OperatorBrainCapabilityAssessment.{field_name} must be between 0.0 and 1.0."
                )
        if not isinstance(
            self.level, OperatorBrainCapabilityMismatchLevel
        ):
            actual_type = type(self.level).__name__
            raise TypeError(
                "OperatorBrainCapabilityAssessment.level must be "
                f"OperatorBrainCapabilityMismatchLevel, got {actual_type}."
            )
        if not isinstance(
            self.contract_binding_profile,
            OperatorContractBindingProfile,
        ):
            actual_type = type(self.contract_binding_profile).__name__
            raise TypeError(
                "OperatorBrainCapabilityAssessment.contract_binding_profile must be "
                f"OperatorContractBindingProfile, got {actual_type}."
            )
        if self.fallback_family is not None and not self.fallback_family.strip():
            raise ValueError(
                "OperatorBrainCapabilityAssessment.fallback_family must be non-empty after trimming when provided."
            )
        if any(not tag.strip() for tag in self.reason_tags):
            raise ValueError(
                "OperatorBrainCapabilityAssessment.reason_tags must contain only non-empty values after trimming."
            )

    def as_payload(self) -> dict[str, object]:
        return {
            "continuity": round(float(self.continuity_mismatch), 4),
            "verification": round(float(self.verification_mismatch), 4),
            "contract_binding": round(float(self.contract_mismatch), 4),
            "level": self.level.value,
            "fallback_family": self.fallback_family,
        }


@dataclass(frozen=True, slots=True)
class OperatorTaskState:
    task_mode: OperatorTaskMode
    complexity: float
    continuity_demand: float
    verification_demand: float
    uncertainty: float
    host_friction: float
    quota_pressure: float
    visible_burden_sensitivity: float
    contract_binding_demand: float = 0.0
    brain_capability: OperatorBrainCapabilityEnvelope = field(
        default_factory=lambda: OperatorBrainCapabilityEnvelope(
            continuity_tolerance=0.75,
            verification_tolerance=0.75,
            output_contract_tolerance=0.65,
        )
    )

    def __post_init__(self) -> None:
        if not isinstance(self.task_mode, OperatorTaskMode):
            actual_type = type(self.task_mode).__name__
            raise TypeError(
                "OperatorTaskState.task_mode must be OperatorTaskMode, "
                f"got {actual_type}."
            )
        for field_name in (
            "complexity",
            "continuity_demand",
            "verification_demand",
            "contract_binding_demand",
            "uncertainty",
            "host_friction",
            "quota_pressure",
            "visible_burden_sensitivity",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, Real):
                actual_type = type(value).__name__
                raise TypeError(
                    f"OperatorTaskState.{field_name} must be numeric, got {actual_type}."
                )
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(
                    f"OperatorTaskState.{field_name} must be between 0.0 and 1.0."
                )
        if not isinstance(self.brain_capability, OperatorBrainCapabilityEnvelope):
            actual_type = type(self.brain_capability).__name__
            raise TypeError(
                "OperatorTaskState.brain_capability must be "
                f"OperatorBrainCapabilityEnvelope, got {actual_type}."
            )

    def as_vector(self) -> tuple[float, ...]:
        return (
            float(self.complexity),
            float(self.continuity_demand),
            float(self.verification_demand),
            float(self.uncertainty),
            float(self.host_friction),
            float(self.quota_pressure),
        )


@dataclass(frozen=True, slots=True)
class OperatorBudgetProfile:
    max_turns: int
    max_retries: int
    allow_resume: bool
    allow_extra_read_pass: bool
    require_verification: bool
    stop_on_quota: bool
    stop_on_capacity: bool

    def __post_init__(self) -> None:
        for field_name in ("max_turns", "max_retries"):
            value = getattr(self, field_name)
            if not isinstance(value, int):
                actual_type = type(value).__name__
                raise TypeError(
                    f"OperatorBudgetProfile.{field_name} must be int, got {actual_type}."
                )
            if value < 0:
                raise ValueError(
                    f"OperatorBudgetProfile.{field_name} must be non-negative."
                )
        for field_name in (
            "allow_resume",
            "allow_extra_read_pass",
            "require_verification",
            "stop_on_quota",
            "stop_on_capacity",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, bool):
                actual_type = type(value).__name__
                raise TypeError(
                    f"OperatorBudgetProfile.{field_name} must be bool, got {actual_type}."
                )

    def as_payload(self) -> dict[str, int | bool]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class OperatorRouteDecision:
    profile: OperatorRouteProfile
    budget: OperatorBudgetProfile
    selected_margin: float
    neutral_margin: float
    reason_tags: frozenset[str]
    summary: ExecutiveSignalSummary
    modulator_memory: ExecutiveModulatorMemory
    modulator_state: ExecutiveModulatorState
    modulator_reason_tags: frozenset[str]
    policy_view: ExecutivePolicyView
    brain_capability_assessment: OperatorBrainCapabilityAssessment = field(
        default_factory=lambda: OperatorBrainCapabilityAssessment(
            continuity_mismatch=0.0,
            verification_mismatch=0.0,
            contract_mismatch=0.0,
            level=OperatorBrainCapabilityMismatchLevel.NONE,
            contract_binding_profile=OperatorContractBindingProfile.STANDARD,
        )
    )
    blocked_reason: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.profile, OperatorRouteProfile):
            actual_type = type(self.profile).__name__
            raise TypeError(
                "OperatorRouteDecision.profile must be OperatorRouteProfile, "
                f"got {actual_type}."
            )
        if not isinstance(self.budget, OperatorBudgetProfile):
            actual_type = type(self.budget).__name__
            raise TypeError(
                "OperatorRouteDecision.budget must be OperatorBudgetProfile, "
                f"got {actual_type}."
            )
        if not isinstance(self.modulator_state, ExecutiveModulatorState):
            actual_type = type(self.modulator_state).__name__
            raise TypeError(
                "OperatorRouteDecision.modulator_state must be ExecutiveModulatorState, "
                f"got {actual_type}."
            )
        if not isinstance(self.modulator_memory, ExecutiveModulatorMemory):
            actual_type = type(self.modulator_memory).__name__
            raise TypeError(
                "OperatorRouteDecision.modulator_memory must be ExecutiveModulatorMemory, "
                f"got {actual_type}."
            )
        if not isinstance(self.summary, ExecutiveSignalSummary):
            actual_type = type(self.summary).__name__
            raise TypeError(
                "OperatorRouteDecision.summary must be ExecutiveSignalSummary, "
                f"got {actual_type}."
            )
        if not isinstance(self.policy_view, ExecutivePolicyView):
            actual_type = type(self.policy_view).__name__
            raise TypeError(
                "OperatorRouteDecision.policy_view must be ExecutivePolicyView, "
                f"got {actual_type}."
            )
        if not isinstance(
            self.brain_capability_assessment, OperatorBrainCapabilityAssessment
        ):
            actual_type = type(self.brain_capability_assessment).__name__
            raise TypeError(
                "OperatorRouteDecision.brain_capability_assessment must be "
                f"OperatorBrainCapabilityAssessment, got {actual_type}."
            )
        for field_name in ("selected_margin", "neutral_margin"):
            value = getattr(self, field_name)
            if not isinstance(value, Real):
                actual_type = type(value).__name__
                raise TypeError(
                    f"OperatorRouteDecision.{field_name} must be numeric, got {actual_type}."
                )
        if any(not tag.strip() for tag in self.reason_tags):
            raise ValueError(
                "OperatorRouteDecision.reason_tags must contain only non-empty values after trimming."
            )
        if any(not tag.strip() for tag in self.modulator_reason_tags):
            raise ValueError(
                "OperatorRouteDecision.modulator_reason_tags must contain only non-empty values after trimming."
            )
        if self.blocked_reason is not None and not self.blocked_reason.strip():
            raise ValueError(
                "OperatorRouteDecision.blocked_reason must be non-empty after trimming when provided."
            )
        if self.profile is OperatorRouteProfile.BLOCKED and self.blocked_reason is None:
            raise ValueError(
                "OperatorRouteDecision.blocked_reason is required when the profile is blocked."
            )
        if self.profile is not OperatorRouteProfile.BLOCKED and self.blocked_reason is not None:
            raise ValueError(
                "OperatorRouteDecision.blocked_reason is only valid for the blocked profile."
            )


_ROUTE_PROTOTYPES = {
    OperatorRouteProfile.INSPECT_LIGHT: (0.10, 0.00, 0.05, 0.40, 0.10, 0.10),
    OperatorRouteProfile.EXECUTE_STANDARD: (0.45, 0.05, 0.70, 0.45, 0.20, 0.20),
    OperatorRouteProfile.EXECUTE_GUARDED: (0.40, 0.05, 0.55, 0.45, 0.55, 0.65),
    OperatorRouteProfile.CONTINUITY_STANDARD: (0.55, 0.90, 0.70, 0.45, 0.25, 0.25),
    OperatorRouteProfile.CONTINUITY_GUARDED: (0.50, 0.90, 0.55, 0.45, 0.60, 0.70),
}

_AXIS_WEIGHTS = (1.0, 1.2, 1.0, 0.8, 1.3, 1.5)
_ROUTE_GAIN_PRIORS = {
    OperatorRouteProfile.INSPECT_LIGHT: 0.35,
    OperatorRouteProfile.EXECUTE_STANDARD: 0.60,
    OperatorRouteProfile.EXECUTE_GUARDED: 0.50,
    OperatorRouteProfile.CONTINUITY_STANDARD: 0.70,
    OperatorRouteProfile.CONTINUITY_GUARDED: 0.58,
}
_HOST_COST_PRIORS = {
    OperatorRouteProfile.INSPECT_LIGHT: 0.10,
    OperatorRouteProfile.EXECUTE_STANDARD: 0.20,
    OperatorRouteProfile.EXECUTE_GUARDED: 0.55,
    OperatorRouteProfile.CONTINUITY_STANDARD: 0.25,
    OperatorRouteProfile.CONTINUITY_GUARDED: 0.60,
}
_QUOTA_COST_PRIORS = {
    OperatorRouteProfile.INSPECT_LIGHT: 0.10,
    OperatorRouteProfile.EXECUTE_STANDARD: 0.20,
    OperatorRouteProfile.EXECUTE_GUARDED: 0.65,
    OperatorRouteProfile.CONTINUITY_STANDARD: 0.25,
    OperatorRouteProfile.CONTINUITY_GUARDED: 0.70,
}
_VISIBLE_COST_PRIORS = {
    OperatorRouteProfile.INSPECT_LIGHT: 0.05,
    OperatorRouteProfile.EXECUTE_STANDARD: 0.35,
    OperatorRouteProfile.EXECUTE_GUARDED: 0.25,
    OperatorRouteProfile.CONTINUITY_STANDARD: 0.45,
    OperatorRouteProfile.CONTINUITY_GUARDED: 0.30,
}
_DEFAULT_PROFILE_BY_MODE = {
    OperatorTaskMode.INSPECT: OperatorRouteProfile.INSPECT_LIGHT,
    OperatorTaskMode.EXECUTE: OperatorRouteProfile.EXECUTE_STANDARD,
    OperatorTaskMode.RESUME_EXECUTE: OperatorRouteProfile.CONTINUITY_STANDARD,
}
_ADMISSIBLE_PROFILES_BY_MODE = {
    OperatorTaskMode.INSPECT: (OperatorRouteProfile.INSPECT_LIGHT,),
    OperatorTaskMode.EXECUTE: (
        OperatorRouteProfile.EXECUTE_STANDARD,
        OperatorRouteProfile.EXECUTE_GUARDED,
    ),
    OperatorTaskMode.RESUME_EXECUTE: (
        OperatorRouteProfile.CONTINUITY_STANDARD,
        OperatorRouteProfile.CONTINUITY_GUARDED,
    ),
}
_BUDGET_PROFILES = {
    OperatorRouteProfile.INSPECT_LIGHT: OperatorBudgetProfile(
        max_turns=1,
        max_retries=0,
        allow_resume=False,
        allow_extra_read_pass=False,
        require_verification=False,
        stop_on_quota=True,
        stop_on_capacity=True,
    ),
    OperatorRouteProfile.EXECUTE_STANDARD: OperatorBudgetProfile(
        max_turns=1,
        max_retries=0,
        allow_resume=False,
        allow_extra_read_pass=False,
        require_verification=True,
        stop_on_quota=False,
        stop_on_capacity=False,
    ),
    OperatorRouteProfile.EXECUTE_GUARDED: OperatorBudgetProfile(
        max_turns=1,
        max_retries=0,
        allow_resume=False,
        allow_extra_read_pass=False,
        require_verification=True,
        stop_on_quota=True,
        stop_on_capacity=True,
    ),
    OperatorRouteProfile.CONTINUITY_STANDARD: OperatorBudgetProfile(
        max_turns=2,
        max_retries=0,
        allow_resume=True,
        allow_extra_read_pass=False,
        require_verification=True,
        stop_on_quota=False,
        stop_on_capacity=False,
    ),
    OperatorRouteProfile.CONTINUITY_GUARDED: OperatorBudgetProfile(
        max_turns=2,
        max_retries=0,
        allow_resume=True,
        allow_extra_read_pass=False,
        require_verification=True,
        stop_on_quota=True,
        stop_on_capacity=True,
    ),
    OperatorRouteProfile.BLOCKED: OperatorBudgetProfile(
        max_turns=0,
        max_retries=0,
        allow_resume=False,
        allow_extra_read_pass=False,
        require_verification=False,
        stop_on_quota=True,
        stop_on_capacity=True,
    ),
}
_LAMBDA_D = 0.55
_LAMBDA_H = 0.20
_LAMBDA_Q = 0.30
_LAMBDA_V = 0.15
_MARGIN_THRESHOLD = 0.08

def select_operator_route(state: OperatorTaskState) -> OperatorRouteDecision:
    zero_summary = ExecutiveSignalSummary(
        uncertainty=0.0,
        repeated_failure_pressure=0.0,
        quota_pressure=0.0,
        continuity_demand=0.0,
        novelty_pressure=0.0,
        verification_conflict_pressure=0.0,
    )
    zero_update = ExecutiveModulatorUpdate(
        summary=zero_summary,
        previous_memory=ZERO_EXECUTIVE_MODULATOR_MEMORY,
        next_memory=ZERO_EXECUTIVE_MODULATOR_MEMORY,
        state=ExecutiveModulatorState(
            focus_gain=0.0,
            explore_gain=0.0,
            stop_pressure=0.0,
            update_pressure=0.0,
        ),
        reason_tags=frozenset(),
    )
    zero_policy = build_executive_policy_view(zero_summary, zero_update.state)
    return select_operator_route_with_policy(state, zero_update, zero_policy)


def select_operator_route_with_modulators(
    state: OperatorTaskState,
    modulator_update: ExecutiveModulatorUpdate | None = None,
) -> OperatorRouteDecision:
    if modulator_update is None:
        return select_operator_route(state)
    if not isinstance(modulator_update, ExecutiveModulatorUpdate):
        actual_type = type(modulator_update).__name__
        raise TypeError(
            "select_operator_route.modulator_update must be ExecutiveModulatorUpdate, "
            f"got {actual_type}."
        )
    return select_operator_route_with_policy(
        state,
        modulator_update,
        build_executive_policy_view(modulator_update.summary, modulator_update.state),
    )


def select_operator_route_with_policy(
    state: OperatorTaskState,
    modulator_update: ExecutiveModulatorUpdate,
    policy_view: ExecutivePolicyView,
) -> OperatorRouteDecision:
    if not isinstance(state, OperatorTaskState):
        actual_type = type(state).__name__
        raise TypeError(
            "select_operator_route.state must be OperatorTaskState, "
            f"got {actual_type}."
        )
    if not isinstance(modulator_update, ExecutiveModulatorUpdate):
        actual_type = type(modulator_update).__name__
        raise TypeError(
            "select_operator_route.modulator_update must be ExecutiveModulatorUpdate, "
            f"got {actual_type}."
        )
    if not isinstance(policy_view, ExecutivePolicyView):
        actual_type = type(policy_view).__name__
        raise TypeError(
            "select_operator_route.policy_view must be ExecutivePolicyView, "
            f"got {actual_type}."
        )

    admissible_profiles = _ADMISSIBLE_PROFILES_BY_MODE[state.task_mode]
    default_profile = _DEFAULT_PROFILE_BY_MODE[state.task_mode]
    brain_capability_assessment = assess_operator_brain_capability(state)
    utilities = {
        profile: _route_utility(profile, state)
        + _policy_profile_adjustment(
            profile,
            default_profile=default_profile,
            state=state,
            policy_view=policy_view,
        )
        for profile in admissible_profiles
    }
    reason_tags = {
        f"task_mode:{state.task_mode.value}",
        f"default_profile:{default_profile.value}",
        f"quota_pressure:{state.quota_pressure:.2f}",
        f"host_friction:{state.host_friction:.2f}",
    }

    if state.task_mode is OperatorTaskMode.RESUME_EXECUTE and state.host_friction >= 0.75:
        utilities[OperatorRouteProfile.CONTINUITY_GUARDED] += 0.10
        reason_tags.add("continuity:guarded-preferred")
    if state.task_mode is OperatorTaskMode.EXECUTE and (
        state.host_friction >= 0.55 or state.quota_pressure >= 0.60
    ):
        utilities[OperatorRouteProfile.EXECUTE_GUARDED] += 0.10
        reason_tags.add("execute:guarded-preferred")

    selected_profile = max(admissible_profiles, key=lambda profile: utilities[profile])
    default_utility = utilities[default_profile]
    selected_utility = utilities[selected_profile]
    neutral_margin = selected_utility - default_utility
    margin_threshold = _effective_margin_threshold(policy_view)

    if selected_profile is not default_profile and neutral_margin < margin_threshold:
        selected_profile = default_profile
        selected_utility = default_utility
        neutral_margin = 0.0
        reason_tags.add("gate:default-margin")
    elif selected_profile is default_profile:
        reason_tags.add("gate:default-profile")
    else:
        reason_tags.add("gate:non-default-profile")

    if (
        brain_capability_assessment.level
        is OperatorBrainCapabilityMismatchLevel.UNSUPPORTED
    ):
        reason_tags.update(brain_capability_assessment.reason_tags)
        reason_tags.add("blocked:brain-capability")
        return OperatorRouteDecision(
            profile=OperatorRouteProfile.BLOCKED,
            budget=_BUDGET_PROFILES[OperatorRouteProfile.BLOCKED],
            selected_margin=selected_utility,
            neutral_margin=neutral_margin,
            reason_tags=frozenset(reason_tags),
            summary=modulator_update.summary,
            modulator_memory=modulator_update.next_memory,
            modulator_state=modulator_update.state,
            modulator_reason_tags=modulator_update.reason_tags,
            policy_view=policy_view,
            brain_capability_assessment=brain_capability_assessment,
            blocked_reason="brain_capability_mismatch",
        )

    if modulator_update.state.stop_pressure >= policy_view.stop_threshold and selected_profile is not OperatorRouteProfile.INSPECT_LIGHT:
        reason_tags.add("blocked:modulator-stop-pressure")
        return OperatorRouteDecision(
            profile=OperatorRouteProfile.BLOCKED,
            budget=_BUDGET_PROFILES[OperatorRouteProfile.BLOCKED],
            selected_margin=selected_utility,
            neutral_margin=neutral_margin,
            reason_tags=frozenset(reason_tags),
            summary=modulator_update.summary,
            modulator_memory=modulator_update.next_memory,
            modulator_state=modulator_update.state,
            modulator_reason_tags=modulator_update.reason_tags,
            policy_view=policy_view,
            brain_capability_assessment=brain_capability_assessment,
            blocked_reason="blocked_by_modulator_stop_pressure",
        )

    if state.quota_pressure >= 0.80 and selected_profile is not OperatorRouteProfile.INSPECT_LIGHT:
        reason_tags.add("blocked:quota-pressure")
        return OperatorRouteDecision(
            profile=OperatorRouteProfile.BLOCKED,
            budget=_BUDGET_PROFILES[OperatorRouteProfile.BLOCKED],
            selected_margin=selected_utility,
            neutral_margin=neutral_margin,
            reason_tags=frozenset(reason_tags),
            summary=modulator_update.summary,
            modulator_memory=modulator_update.next_memory,
            modulator_state=modulator_update.state,
            modulator_reason_tags=modulator_update.reason_tags,
            policy_view=policy_view,
            brain_capability_assessment=brain_capability_assessment,
            blocked_reason="blocked_by_quota_pressure",
        )

    selected_profile = _apply_brain_capability_profile_downshift(
        selected_profile,
        state=state,
        assessment=brain_capability_assessment,
        reason_tags=reason_tags,
    )
    budget = _apply_policy_to_budget(
        _BUDGET_PROFILES[selected_profile],
        state=state,
        policy_view=policy_view,
        assessment=brain_capability_assessment,
        reason_tags=reason_tags,
    )

    return OperatorRouteDecision(
        profile=selected_profile,
        budget=budget,
        selected_margin=selected_utility,
        neutral_margin=neutral_margin,
        reason_tags=frozenset(reason_tags | {f"profile:{selected_profile.value}"}),
        summary=modulator_update.summary,
        modulator_memory=modulator_update.next_memory,
        modulator_state=modulator_update.state,
        modulator_reason_tags=modulator_update.reason_tags,
        policy_view=policy_view,
        brain_capability_assessment=brain_capability_assessment,
    )


def assess_operator_brain_capability(
    state: OperatorTaskState,
) -> OperatorBrainCapabilityAssessment:
    if not isinstance(state, OperatorTaskState):
        actual_type = type(state).__name__
        raise TypeError(
            "assess_operator_brain_capability.state must be OperatorTaskState, "
            f"got {actual_type}."
        )
    continuity_mismatch = max(
        0.0,
        float(state.continuity_demand)
        - float(state.brain_capability.continuity_tolerance),
    )
    verification_mismatch = max(
        0.0,
        float(state.verification_demand)
        - float(state.brain_capability.verification_tolerance),
    )
    contract_mismatch = max(
        0.0,
        float(state.contract_binding_demand)
        - float(state.brain_capability.output_contract_tolerance),
    )
    max_mismatch = max(
        continuity_mismatch,
        verification_mismatch,
        contract_mismatch,
    )
    if max_mismatch >= 0.50:
        level = OperatorBrainCapabilityMismatchLevel.UNSUPPORTED
    elif max_mismatch >= 0.20:
        level = OperatorBrainCapabilityMismatchLevel.DEGRADE
    else:
        level = OperatorBrainCapabilityMismatchLevel.NONE

    reason_tags: set[str] = set()
    if level is not OperatorBrainCapabilityMismatchLevel.NONE:
        if contract_mismatch > 0.0:
            reason_tags.add("brain-capability:contract-mismatch")
        if verification_mismatch > 0.0:
            reason_tags.add("brain-capability:verification-downshift")
    fallback_family = None
    if level is OperatorBrainCapabilityMismatchLevel.UNSUPPORTED:
        reason_tags.add("brain-capability:unsupported-floor")
        fallback_family = _brain_capability_fallback_family(
            state,
            continuity_mismatch=continuity_mismatch,
            verification_mismatch=verification_mismatch,
        )
    return OperatorBrainCapabilityAssessment(
        continuity_mismatch=continuity_mismatch,
        verification_mismatch=verification_mismatch,
        contract_mismatch=contract_mismatch,
        level=level,
        contract_binding_profile=(
            OperatorContractBindingProfile.LEAN
            if level is OperatorBrainCapabilityMismatchLevel.DEGRADE
            else OperatorContractBindingProfile.STANDARD
        ),
        fallback_family=fallback_family,
        reason_tags=frozenset(reason_tags),
    )


def build_operator_route_diagnostics(
    state: OperatorTaskState,
    decision: OperatorRouteDecision,
) -> dict[str, object]:
    if not isinstance(state, OperatorTaskState):
        actual_type = type(state).__name__
        raise TypeError(
            "build_operator_route_diagnostics.state must be OperatorTaskState, "
            f"got {actual_type}."
        )
    if not isinstance(decision, OperatorRouteDecision):
        actual_type = type(decision).__name__
        raise TypeError(
            "build_operator_route_diagnostics.decision must be OperatorRouteDecision, "
            f"got {actual_type}."
        )
    brain_capability_band = _brain_capability_band_for_state(state)
    return {
        "route_profile": decision.profile.value,
        "route_budget": decision.budget.as_payload(),
        "route_reason_tags": sorted(decision.reason_tags),
        "selected_margin": round(float(decision.selected_margin), 4),
        "neutral_margin": round(float(decision.neutral_margin), 4),
        "state_vector": [round(value, 4) for value in state.as_vector()],
        "quota_pressure": round(float(state.quota_pressure), 4),
        "host_friction": round(float(state.host_friction), 4),
        "visible_burden_sensitivity": round(
            float(state.visible_burden_sensitivity), 4
        ),
        "contract_binding_demand": round(float(state.contract_binding_demand), 4),
        "brain_capability": state.brain_capability.as_payload(),
        "brain_capability_band": brain_capability_band,
        "brain_capability_mismatch": (
            decision.brain_capability_assessment.as_payload()
        ),
        "brain_capability_reason_tags": sorted(
            decision.brain_capability_assessment.reason_tags
        ),
        "contract_binding_profile": (
            decision.brain_capability_assessment.contract_binding_profile.value
        ),
        "blocked_reason": decision.blocked_reason,
        "modulator_summary": decision.summary.as_payload(),
        "modulator_memory": decision.modulator_memory.as_payload(),
        "modulator_state": decision.modulator_state.as_payload(),
        "modulator_reason_tags": sorted(decision.modulator_reason_tags),
        "policy_view": decision.policy_view.as_payload(),
    }

def _route_utility(
    profile: OperatorRouteProfile,
    state: OperatorTaskState,
) -> float:
    prototype = _ROUTE_PROTOTYPES[profile]
    distance = sum(
        axis_weight * (state_value - prototype_value) ** 2
        for axis_weight, state_value, prototype_value in zip(
            _AXIS_WEIGHTS,
            state.as_vector(),
            prototype,
            strict=True,
        )
    )
    return (
        _ROUTE_GAIN_PRIORS[profile]
        - (_LAMBDA_D * distance)
        - (_LAMBDA_H * _HOST_COST_PRIORS[profile] * state.host_friction)
        - (_LAMBDA_Q * _QUOTA_COST_PRIORS[profile] * state.quota_pressure)
        - (_LAMBDA_V * _VISIBLE_COST_PRIORS[profile] * state.visible_burden_sensitivity)
    )


def _policy_profile_adjustment(
    profile: OperatorRouteProfile,
    *,
    default_profile: OperatorRouteProfile,
    state: OperatorTaskState,
    policy_view: ExecutivePolicyView,
) -> float:
    adjustment = 0.0
    if profile is default_profile:
        adjustment += policy_view.default_profile_bonus
    if state.task_mode is OperatorTaskMode.RESUME_EXECUTE and profile in {
        OperatorRouteProfile.CONTINUITY_STANDARD,
        OperatorRouteProfile.CONTINUITY_GUARDED,
    }:
        adjustment += 0.04 * policy_view.default_profile_bonus
    return adjustment


def _effective_margin_threshold(policy_view: ExecutivePolicyView) -> float:
    return float(policy_view.switch_margin)


def _apply_policy_to_budget(
    budget: OperatorBudgetProfile,
    *,
    state: OperatorTaskState,
    policy_view: ExecutivePolicyView,
    assessment: OperatorBrainCapabilityAssessment,
    reason_tags: set[str],
) -> OperatorBudgetProfile:
    if (
        assessment.level is OperatorBrainCapabilityMismatchLevel.DEGRADE
        and (budget.allow_extra_read_pass or budget.max_retries > 0)
    ):
        reason_tags.add("budget:brain-capability-suppressed")
        return replace(
            budget,
            max_retries=0,
            allow_extra_read_pass=False,
        )
    if state.task_mode is OperatorTaskMode.INSPECT and policy_view.allow_extra_read_pass:
        reason_tags.add("budget:extra-read-pass")
        return replace(
            budget,
            max_retries=budget.max_retries + 1,
            allow_extra_read_pass=True,
        )
    return budget


def _apply_brain_capability_profile_downshift(
    selected_profile: OperatorRouteProfile,
    *,
    state: OperatorTaskState,
    assessment: OperatorBrainCapabilityAssessment,
    reason_tags: set[str],
) -> OperatorRouteProfile:
    if assessment.level is not OperatorBrainCapabilityMismatchLevel.DEGRADE:
        reason_tags.update(assessment.reason_tags)
        return selected_profile
    reason_tags.update(assessment.reason_tags)
    if selected_profile in {
        OperatorRouteProfile.CONTINUITY_STANDARD,
        OperatorRouteProfile.CONTINUITY_GUARDED,
    }:
        reason_tags.add("brain-capability:continuity-downshift")
        if state.task_mode is OperatorTaskMode.RESUME_EXECUTE:
            return OperatorRouteProfile.EXECUTE_STANDARD
        return OperatorRouteProfile.INSPECT_LIGHT
    return selected_profile


def _brain_capability_fallback_family(
    state: OperatorTaskState,
    *,
    continuity_mismatch: float,
    verification_mismatch: float,
) -> str:
    if state.task_mode is OperatorTaskMode.INSPECT:
        return "inspect"
    if verification_mismatch >= continuity_mismatch or state.verification_demand >= 0.5:
        return "check"
    return "manual_escalation"


def _brain_capability_band_for_state(state: OperatorTaskState) -> str:
    from cortex.runtime.operator_brain_capability import (
        brain_capability_band_for_envelope,
    )

    return brain_capability_band_for_envelope(state.brain_capability)


__all__ = [
    "OperatorBrainCapabilityAssessment",
    "OperatorBrainCapabilityEnvelope",
    "OperatorBudgetProfile",
    "OperatorContractBindingProfile",
    "OperatorRouteDecision",
    "OperatorRouteProfile",
    "OperatorBrainCapabilityMismatchLevel",
    "OperatorTaskMode",
    "OperatorTaskState",
    "assess_operator_brain_capability",
    "build_operator_route_diagnostics",
    "select_operator_route_with_policy",
    "select_operator_route_with_modulators",
    "select_operator_route",
]
```

### `cortex/sre/families.py`

```python
"""Reference soft-control family set for the first active SRE hinge."""

from __future__ import annotations

from enum import Enum


class SoftControlFamily(str, Enum):
    NEUTRAL = "neutral"
    SEEK_CONTEXT = "seek-context"
    REDIRECT = "redirect"
    CHECK = "check"
    BRANCH = "branch"
    ESCALATE = "escalate"
    BRAKE = "brake"


REFERENCE_SOFT_CONTROL_FAMILIES = frozenset(SoftControlFamily)


__all__ = ["REFERENCE_SOFT_CONTROL_FAMILIES", "SoftControlFamily"]
```

### `cortex/aux/publication.py`

```python
"""Support-only offline publication contracts and augmentation-only re-entry."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from cortex.core.envelopes import MetadataField
from cortex.core.support import SupportReference, SupportSnapshot
from cortex.sre.memory_priors import HostReliabilityPrior

from .augmentation import AuxiliarySupportAppendix, AugmentedSupportSnapshot, augment_snapshot


def _validate_refs(
    refs: tuple[SupportReference, ...],
    *,
    field_name: str,
) -> None:
    if any(not isinstance(reference, SupportReference) for reference in refs):
        raise TypeError(f"{field_name} must contain only SupportReference instances.")


def _validate_text_values(
    values: frozenset[str] | tuple[str, ...],
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


def _dedupe_refs(references: tuple[SupportReference, ...]) -> tuple[SupportReference, ...]:
    ordered: list[SupportReference] = []
    seen: set[tuple[str, str]] = set()
    for reference in references:
        key = (reference.reference_kind, reference.reference_id)
        if key in seen:
            continue
        seen.add(key)
        ordered.append(reference)
    return tuple(ordered)


def _metadata_field_as_payload(field: MetadataField) -> dict[str, Any]:
    if not isinstance(field, MetadataField):
        actual_type = type(field).__name__
        raise TypeError(
            "offline_support_publication_as_payload() metadata must contain only MetadataField instances, "
            f"got {actual_type}."
        )
    return {
        "key": field.key,
        "value": field.value,
    }


def _parse_metadata_field_payload(
    payload: Mapping[str, Any],
    *,
    label: str,
) -> MetadataField:
    if not isinstance(payload, Mapping):
        actual_type = type(payload).__name__
        raise TypeError(f"{label} must be an object, got {actual_type}.")
    if tuple(payload) != ("key", "value"):
        raise ValueError(f"{label} must preserve the locked key order ('key', 'value').")
    return MetadataField(
        _required_payload_string(payload.get("key"), label=f"{label}.key"),
        payload.get("value"),
    )


def _support_reference_as_payload(reference: SupportReference) -> dict[str, Any]:
    if not isinstance(reference, SupportReference):
        actual_type = type(reference).__name__
        raise TypeError(
            "offline_support_publication_as_payload() support refs must contain only SupportReference instances, "
            f"got {actual_type}."
        )
    return {
        "reference_kind": reference.reference_kind,
        "reference_id": reference.reference_id,
        "tags": sorted(reference.tags),
        "metadata": [_metadata_field_as_payload(field) for field in reference.metadata],
    }


def _parse_support_reference_payload(
    payload: Mapping[str, Any],
    *,
    label: str,
) -> SupportReference:
    if not isinstance(payload, Mapping):
        actual_type = type(payload).__name__
        raise TypeError(f"{label} must be an object, got {actual_type}.")
    if tuple(payload) != ("reference_kind", "reference_id", "tags", "metadata"):
        raise ValueError(
            f"{label} must preserve the locked key order "
            "('reference_kind', 'reference_id', 'tags', 'metadata')."
        )
    tags = payload.get("tags")
    if not isinstance(tags, list):
        actual_type = type(tags).__name__
        raise TypeError(f"{label}.tags must be a list[str], got {actual_type}.")
    metadata = payload.get("metadata")
    if not isinstance(metadata, list):
        actual_type = type(metadata).__name__
        raise TypeError(f"{label}.metadata must be a list[dict[str, Any]], got {actual_type}.")
    return SupportReference(
        _required_payload_string(payload.get("reference_kind"), label=f"{label}.reference_kind"),
        _required_payload_string(payload.get("reference_id"), label=f"{label}.reference_id"),
        tags=frozenset(
            _required_payload_string(tag, label=f"{label}.tags[{index}]")
            for index, tag in enumerate(tags)
        ),
        metadata=tuple(
            _parse_metadata_field_payload(item, label=f"{label}.metadata[{index}]")
            for index, item in enumerate(metadata)
        ),
    )


def _required_payload_string(value: Any, *, label: str) -> str:
    if not isinstance(value, str):
        actual_type = type(value).__name__
        raise TypeError(f"{label} must be a string, got {actual_type}.")
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"{label} must be non-empty after trimming.")
    return stripped


def _string_list_payload(
    values: frozenset[str] | tuple[str, ...],
    *,
    field_name: str,
) -> list[str]:
    _validate_text_values(values, field_name=field_name)
    return sorted(values) if isinstance(values, frozenset) else list(values)


_HOST_RELIABILITY_PRIOR_PAYLOAD_KEYS: tuple[str, ...] = (
    "timeout_rate",
    "degradation_rate",
    "capability_availability",
    "contradiction_counter",
    "ttl_hours",
    "last_validated_at",
    "probe_failure_classes",
    "affordance_scope_tags",
)


def _host_reliability_prior_as_payload(
    prior: HostReliabilityPrior | None,
) -> dict[str, Any] | None:
    if prior is None:
        return None
    if not isinstance(prior, HostReliabilityPrior):
        actual_type = type(prior).__name__
        raise TypeError(
            "offline_support_publication_as_payload() host_reliability_prior must be "
            f"HostReliabilityPrior | None, got {actual_type}."
        )
    return {
        "timeout_rate": prior.timeout_rate,
        "degradation_rate": prior.degradation_rate,
        "capability_availability": prior.capability_availability,
        "contradiction_counter": prior.contradiction_counter,
        "ttl_hours": prior.ttl_hours,
        "last_validated_at": prior.last_validated_at,
        "probe_failure_classes": sorted(prior.probe_failure_classes),
        "affordance_scope_tags": sorted(prior.affordance_scope_tags),
    }


def _parse_host_reliability_prior_payload(
    value: Any,
    *,
    label: str,
) -> HostReliabilityPrior | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        actual_type = type(value).__name__
        raise TypeError(f"{label} must be an object or null, got {actual_type}.")
    if tuple(value) != _HOST_RELIABILITY_PRIOR_PAYLOAD_KEYS:
        raise ValueError(
            f"{label} must preserve the locked key order "
            f"{_HOST_RELIABILITY_PRIOR_PAYLOAD_KEYS!r}."
        )
    timeout_rate = value.get("timeout_rate")
    if isinstance(timeout_rate, bool) or not isinstance(timeout_rate, (int, float)):
        actual_type = type(timeout_rate).__name__
        raise TypeError(f"{label}.timeout_rate must be numeric, got {actual_type}.")
    degradation_rate = value.get("degradation_rate")
    if isinstance(degradation_rate, bool) or not isinstance(degradation_rate, (int, float)):
        actual_type = type(degradation_rate).__name__
        raise TypeError(f"{label}.degradation_rate must be numeric, got {actual_type}.")
    capability_availability = value.get("capability_availability")
    if isinstance(capability_availability, bool) or not isinstance(
        capability_availability, (int, float)
    ):
        actual_type = type(capability_availability).__name__
        raise TypeError(
            f"{label}.capability_availability must be numeric, got {actual_type}."
        )
    contradiction_counter = value.get("contradiction_counter")
    if isinstance(contradiction_counter, bool) or not isinstance(contradiction_counter, int):
        actual_type = type(contradiction_counter).__name__
        raise TypeError(
            f"{label}.contradiction_counter must be an integer, got {actual_type}."
        )
    ttl_hours = value.get("ttl_hours")
    if isinstance(ttl_hours, bool) or not isinstance(ttl_hours, int):
        actual_type = type(ttl_hours).__name__
        raise TypeError(f"{label}.ttl_hours must be an integer, got {actual_type}.")
    last_validated_at = value.get("last_validated_at")
    if last_validated_at is not None and not isinstance(last_validated_at, str):
        actual_type = type(last_validated_at).__name__
        raise TypeError(
            f"{label}.last_validated_at must be a string or null, got {actual_type}."
        )
    probe_failure_classes = value.get("probe_failure_classes")
    if not isinstance(probe_failure_classes, list):
        actual_type = type(probe_failure_classes).__name__
        raise TypeError(
            f"{label}.probe_failure_classes must be a list[str], got {actual_type}."
        )
    affordance_scope_tags = value.get("affordance_scope_tags")
    if not isinstance(affordance_scope_tags, list):
        actual_type = type(affordance_scope_tags).__name__
        raise TypeError(
            f"{label}.affordance_scope_tags must be a list[str], got {actual_type}."
        )
    return HostReliabilityPrior(
        timeout_rate=float(timeout_rate),
        degradation_rate=float(degradation_rate),
        capability_availability=float(capability_availability),
        contradiction_counter=contradiction_counter,
        ttl_hours=ttl_hours,
        last_validated_at=last_validated_at,
        probe_failure_classes=tuple(
            _required_payload_string(
                item,
                label=f"{label}.probe_failure_classes[{index}]",
            )
            for index, item in enumerate(probe_failure_classes)
        ),
        affordance_scope_tags=tuple(
            _required_payload_string(
                item,
                label=f"{label}.affordance_scope_tags[{index}]",
            )
            for index, item in enumerate(affordance_scope_tags)
        ),
    )


@dataclass(frozen=True, slots=True)
class OfflineSupportPublication:
    retrieval_prior_refs: tuple[SupportReference, ...] = field(default_factory=tuple)
    branch_prior_refs: tuple[SupportReference, ...] = field(default_factory=tuple)
    contradiction_summary_refs: tuple[SupportReference, ...] = field(default_factory=tuple)
    uncertainty_calibration_refs: tuple[SupportReference, ...] = field(default_factory=tuple)
    published_memory_summary_refs: tuple[SupportReference, ...] = field(default_factory=tuple)
    publication_tags: frozenset[str] = field(default_factory=frozenset)
    notes: tuple[str, ...] = field(default_factory=tuple)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)
    host_reliability_prior: HostReliabilityPrior | None = None

    def __post_init__(self) -> None:
        _validate_refs(
            self.retrieval_prior_refs,
            field_name="OfflineSupportPublication.retrieval_prior_refs",
        )
        _validate_refs(
            self.branch_prior_refs,
            field_name="OfflineSupportPublication.branch_prior_refs",
        )
        _validate_refs(
            self.contradiction_summary_refs,
            field_name="OfflineSupportPublication.contradiction_summary_refs",
        )
        _validate_refs(
            self.uncertainty_calibration_refs,
            field_name="OfflineSupportPublication.uncertainty_calibration_refs",
        )
        _validate_refs(
            self.published_memory_summary_refs,
            field_name="OfflineSupportPublication.published_memory_summary_refs",
        )
        _validate_text_values(
            self.publication_tags,
            field_name="OfflineSupportPublication.publication_tags",
        )
        _validate_text_values(
            self.notes,
            field_name="OfflineSupportPublication.notes",
        )
        _validate_metadata(
            self.metadata,
            field_name="OfflineSupportPublication.metadata",
        )
        if self.host_reliability_prior is not None and not isinstance(
            self.host_reliability_prior,
            HostReliabilityPrior,
        ):
            actual_type = type(self.host_reliability_prior).__name__
            raise TypeError(
                "OfflineSupportPublication.host_reliability_prior must be "
                f"HostReliabilityPrior | None, got {actual_type}.",
            )

    def support_refs(self) -> tuple[SupportReference, ...]:
        return _dedupe_refs(
            self.retrieval_prior_refs
            + self.branch_prior_refs
            + self.contradiction_summary_refs
            + self.uncertainty_calibration_refs
            + self.published_memory_summary_refs
        )


def offline_support_publication_as_payload(
    publication: OfflineSupportPublication,
) -> dict[str, Any]:
    if not isinstance(publication, OfflineSupportPublication):
        actual_type = type(publication).__name__
        raise TypeError(
            "offline_support_publication_as_payload() requires OfflineSupportPublication, "
            f"got {actual_type}."
        )
    return {
        "retrieval_prior_refs": [
            _support_reference_as_payload(reference)
            for reference in publication.retrieval_prior_refs
        ],
        "branch_prior_refs": [
            _support_reference_as_payload(reference)
            for reference in publication.branch_prior_refs
        ],
        "contradiction_summary_refs": [
            _support_reference_as_payload(reference)
            for reference in publication.contradiction_summary_refs
        ],
        "uncertainty_calibration_refs": [
            _support_reference_as_payload(reference)
            for reference in publication.uncertainty_calibration_refs
        ],
        "published_memory_summary_refs": [
            _support_reference_as_payload(reference)
            for reference in publication.published_memory_summary_refs
        ],
        "publication_tags": _string_list_payload(
            publication.publication_tags,
            field_name="OfflineSupportPublication.publication_tags",
        ),
        "notes": _string_list_payload(
            publication.notes,
            field_name="OfflineSupportPublication.notes",
        ),
        "metadata": [
            _metadata_field_as_payload(field)
            for field in publication.metadata
        ],
        "host_reliability_prior": _host_reliability_prior_as_payload(
            publication.host_reliability_prior,
        ),
    }


def parse_offline_support_publication_payload(
    payload: Mapping[str, Any],
) -> OfflineSupportPublication:
    if not isinstance(payload, Mapping):
        actual_type = type(payload).__name__
        raise TypeError(
            "parse_offline_support_publication_payload() requires a mapping, "
            f"got {actual_type}."
        )
    required_keys = (
        "retrieval_prior_refs",
        "branch_prior_refs",
        "contradiction_summary_refs",
        "uncertainty_calibration_refs",
        "published_memory_summary_refs",
        "publication_tags",
        "notes",
        "metadata",
        "host_reliability_prior",
    )
    if tuple(payload) != required_keys:
        raise ValueError(
            "parse_offline_support_publication_payload() requires the locked key order "
            f"{required_keys!r}."
        )

    def _ref_list(key: str) -> tuple[SupportReference, ...]:
        value = payload.get(key)
        if not isinstance(value, list):
            actual_type = type(value).__name__
            raise TypeError(
                f"parse_offline_support_publication_payload().{key} must be a list[dict[str, Any]], "
                f"got {actual_type}."
            )
        return tuple(
            _parse_support_reference_payload(item, label=f"offline_publication.{key}[{index}]")
            for index, item in enumerate(value)
        )

    def _string_tuple(key: str) -> tuple[str, ...]:
        value = payload.get(key)
        if not isinstance(value, list):
            actual_type = type(value).__name__
            raise TypeError(
                f"parse_offline_support_publication_payload().{key} must be a list[str], "
                f"got {actual_type}."
            )
        return tuple(
            _required_payload_string(item, label=f"offline_publication.{key}[{index}]")
            for index, item in enumerate(value)
        )

    metadata = payload.get("metadata")
    if not isinstance(metadata, list):
        actual_type = type(metadata).__name__
        raise TypeError(
            "parse_offline_support_publication_payload().metadata must be a list[dict[str, Any]], "
            f"got {actual_type}."
        )

    return OfflineSupportPublication(
        retrieval_prior_refs=_ref_list("retrieval_prior_refs"),
        branch_prior_refs=_ref_list("branch_prior_refs"),
        contradiction_summary_refs=_ref_list("contradiction_summary_refs"),
        uncertainty_calibration_refs=_ref_list("uncertainty_calibration_refs"),
        published_memory_summary_refs=_ref_list("published_memory_summary_refs"),
        publication_tags=frozenset(_string_tuple("publication_tags")),
        notes=_string_tuple("notes"),
        metadata=tuple(
            _parse_metadata_field_payload(item, label=f"offline_publication.metadata[{index}]")
            for index, item in enumerate(metadata)
        ),
        host_reliability_prior=_parse_host_reliability_prior_payload(
            payload.get("host_reliability_prior"),
            label="offline_publication.host_reliability_prior",
        ),
    )


def build_offline_support_publication(
    snapshot: SupportSnapshot,
    *,
    publication_tags: frozenset[str] = frozenset(),
    notes: tuple[str, ...] = (),
    metadata: tuple[MetadataField, ...] = (),
) -> OfflineSupportPublication:
    if not isinstance(snapshot, SupportSnapshot):
        actual_type = type(snapshot).__name__
        raise TypeError(
            "build_offline_support_publication() requires SupportSnapshot, "
            f"got {actual_type}.",
        )
    retrieval_prior_refs = _dedupe_refs(
        snapshot.exec_memory_pub.published_memory_refs + snapshot.exec_memory_pub.artifact_refs
    )
    branch_prior_refs = _dedupe_refs(
        tuple(
            SupportReference("branch", branch_ref, tags=frozenset({"branch-prior"}))
            for branch_ref in snapshot.session.branch_registry
            if branch_ref != "main"
        )
    )
    contradiction_summary_refs = _dedupe_refs(
        tuple(
            SupportReference(
                "contradiction",
                record.reason_code,
                tags=frozenset(record.capability_tags | {record.reason_code}),
            )
            for record in snapshot.trace.degradation_records
        )
    )
    uncertainty_calibration_refs = _dedupe_refs(
        tuple(
            SupportReference("uncertainty", brake_entry, tags=frozenset({"brake-history"}))
            for brake_entry in snapshot.session.brake_history
        )
        + tuple(
            SupportReference(
                "wake",
                receipt.reason_tag,
                tags=frozenset({"wake-receipt"}),
            )
            for receipt in snapshot.trace.wake_receipts
        )
    )
    merged_tags = frozenset({"aux/offline-publication", "claim-conservative"}) | publication_tags
    merged_notes = (
        "support-only publication derived from lawful public support snapshot",
    ) + notes
    merged_metadata = (MetadataField("source", "aux/offline-publication"),) + metadata
    return OfflineSupportPublication(
        retrieval_prior_refs=retrieval_prior_refs,
        branch_prior_refs=branch_prior_refs,
        contradiction_summary_refs=contradiction_summary_refs,
        uncertainty_calibration_refs=uncertainty_calibration_refs,
        published_memory_summary_refs=snapshot.exec_memory_pub.published_memory_refs,
        publication_tags=merged_tags,
        notes=merged_notes,
        metadata=merged_metadata,
    )


def augment_snapshot_with_offline_publication(
    snapshot: SupportSnapshot,
    publication: OfflineSupportPublication,
) -> AugmentedSupportSnapshot:
    if not isinstance(snapshot, SupportSnapshot):
        actual_type = type(snapshot).__name__
        raise TypeError(
            "augment_snapshot_with_offline_publication() requires SupportSnapshot, "
            f"got {actual_type}.",
        )
    if not isinstance(publication, OfflineSupportPublication):
        actual_type = type(publication).__name__
        raise TypeError(
            "augment_snapshot_with_offline_publication() requires OfflineSupportPublication, "
            f"got {actual_type}.",
        )

    return augment_snapshot(
        snapshot,
        AuxiliarySupportAppendix(
            derived_support_refs=publication.support_refs(),
            derived_tags=frozenset({"aux/offline-publication"}) | publication.publication_tags,
            notes=publication.notes,
            metadata=publication.metadata,
            published_host_reliability_prior=publication.host_reliability_prior,
        ),
    )


__all__ = [
    "OfflineSupportPublication",
    "build_offline_support_publication",
    "offline_support_publication_as_payload",
    "parse_offline_support_publication_payload",
    "augment_snapshot_with_offline_publication",
]
```

### `cortex/aux/persistence.py`

```python
"""Bounded AUX persistence for explicit support-memory episodes."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
from typing import Iterator

from cortex.core.envelopes import MetadataField
from cortex.core.support import SupportReference, SupportSnapshot
from cortex.sre.goals import normalize_continuity_reminder


DEFAULT_SUPPORT_MEMORY_STORE_PATH = Path(".cortex/aux/support_memory.sqlite3")
_PLAIN_TEXT_REMINDER = "plain-text-reminder"
_EPISODE_SCHEMA = """
CREATE TABLE IF NOT EXISTS episodes (
    episode_fingerprint TEXT PRIMARY KEY,
    recorded_at TEXT NOT NULL,
    recorded_at_epoch INTEGER,
    host_name TEXT NOT NULL,
    source_label TEXT NOT NULL,
    payload_json TEXT NOT NULL
);
"""


def _require_text(value: str, *, field_name: str) -> str:
    if not (isinstance(value, str) and value.strip()):
        raise ValueError(f"{field_name} must be non-empty after trimming.")
    return value.strip()


def _require_text_tuple(values: tuple[str, ...], *, field_name: str) -> tuple[str, ...]:
    if not isinstance(values, tuple):
        actual_type = type(values).__name__
        raise TypeError(f"{field_name} must be tuple[str, ...], got {actual_type}.")
    return tuple(_require_text(value, field_name=field_name) for value in values)


def _dedupe_ordered(values: tuple[str, ...]) -> tuple[str, ...]:
    ordered: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return tuple(ordered)


def _metadata_keys(metadata: tuple[MetadataField, ...]) -> tuple[str, ...]:
    return tuple(sorted({field.key for field in metadata}))


def _normalized_recorded_at_fields(
    value: str,
    *,
    field_name: str,
) -> tuple[str, int]:
    text = _require_text(value, field_name=field_name)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field_name} must be ISO-8601 timestamp text.") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware.")
    normalized = parsed.astimezone(timezone.utc).replace(microsecond=0)
    return normalized.isoformat(timespec="seconds"), int(normalized.timestamp())


def _require_aware_datetime(value: datetime, *, field_name: str) -> datetime:
    if not isinstance(value, datetime):
        actual_type = type(value).__name__
        raise TypeError(f"{field_name} must be datetime, got {actual_type}.")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware.")
    return value.astimezone(timezone.utc).replace(microsecond=0)


def _bounded_reminders(reminders: tuple[str, ...]) -> tuple[str, ...]:
    bounded: list[str] = []
    for reminder in reminders:
        normalized = normalize_continuity_reminder(reminder)
        if normalized is not None:
            bounded.append(normalized)
            continue
        bounded.append(_PLAIN_TEXT_REMINDER)
    return _dedupe_ordered(tuple(bounded))


@dataclass(frozen=True, slots=True)
class SupportEventSignature:
    native_event_name: str
    payload_kind: str
    payload_metadata_keys: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        _require_text(
            self.native_event_name,
            field_name="SupportEventSignature.native_event_name",
        )
        _require_text(
            self.payload_kind,
            field_name="SupportEventSignature.payload_kind",
        )
        _require_text_tuple(
            self.payload_metadata_keys,
            field_name="SupportEventSignature.payload_metadata_keys",
        )


@dataclass(frozen=True, slots=True)
class _SupportReferenceProjection:
    reference_kind: str
    reference_id: str
    tags: tuple[str, ...] = field(default_factory=tuple)
    metadata_keys: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        _require_text(
            self.reference_kind,
            field_name="_SupportReferenceProjection.reference_kind",
        )
        _require_text(
            self.reference_id,
            field_name="_SupportReferenceProjection.reference_id",
        )
        _require_text_tuple(
            self.tags,
            field_name="_SupportReferenceProjection.tags",
        )
        _require_text_tuple(
            self.metadata_keys,
            field_name="_SupportReferenceProjection.metadata_keys",
        )

    def as_support_reference(self) -> SupportReference:
        return SupportReference(
            self.reference_kind,
            self.reference_id,
            tags=frozenset(self.tags),
            metadata=tuple(MetadataField(key, key) for key in self.metadata_keys),
        )


@dataclass(frozen=True, slots=True)
class SupportMemoryEpisode:
    episode_fingerprint: str
    recorded_at: str
    host_name: str
    source_label: str
    event_signatures: tuple[SupportEventSignature, ...] = field(default_factory=tuple)
    candidate_refs: tuple[str, ...] = field(default_factory=tuple)
    wake_reason_tags: tuple[str, ...] = field(default_factory=tuple)
    degradation_reason_codes: tuple[str, ...] = field(default_factory=tuple)
    contradiction_source_tags: tuple[str, ...] = field(default_factory=tuple)
    contradiction_evidence_tags: tuple[str, ...] = field(default_factory=tuple)
    branch_registry: tuple[str, ...] = field(default_factory=tuple)
    pending_goal_refs: tuple[str, ...] = field(default_factory=tuple)
    role_view_tags: tuple[str, ...] = field(default_factory=tuple)
    budget_history: tuple[str, ...] = field(default_factory=tuple)
    brake_history: tuple[str, ...] = field(default_factory=tuple)
    reminders: tuple[str, ...] = field(default_factory=tuple)
    host_affordance_tags: tuple[str, ...] = field(default_factory=tuple)
    host_approval_boundary_tags: tuple[str, ...] = field(default_factory=tuple)
    host_constraint_tags: tuple[str, ...] = field(default_factory=tuple)
    host_metadata_keys: tuple[str, ...] = field(default_factory=tuple)
    published_memory_refs: tuple[_SupportReferenceProjection, ...] = field(default_factory=tuple)
    artifact_refs: tuple[_SupportReferenceProjection, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        _require_text(
            self.episode_fingerprint,
            field_name="SupportMemoryEpisode.episode_fingerprint",
        )
        normalized_recorded_at, _ = _normalized_recorded_at_fields(
            self.recorded_at,
            field_name="SupportMemoryEpisode.recorded_at",
        )
        object.__setattr__(self, "recorded_at", normalized_recorded_at)
        _require_text(
            self.host_name,
            field_name="SupportMemoryEpisode.host_name",
        )
        _require_text(
            self.source_label,
            field_name="SupportMemoryEpisode.source_label",
        )
        if any(not isinstance(event, SupportEventSignature) for event in self.event_signatures):
            raise TypeError(
                "SupportMemoryEpisode.event_signatures must contain only SupportEventSignature instances."
            )
        for field_name in (
            "candidate_refs",
            "wake_reason_tags",
            "degradation_reason_codes",
            "contradiction_source_tags",
            "contradiction_evidence_tags",
            "branch_registry",
            "pending_goal_refs",
            "role_view_tags",
            "budget_history",
            "brake_history",
            "reminders",
            "host_affordance_tags",
            "host_approval_boundary_tags",
            "host_constraint_tags",
            "host_metadata_keys",
        ):
            _require_text_tuple(
                getattr(self, field_name),
                field_name=f"SupportMemoryEpisode.{field_name}",
            )
        if any(
            not isinstance(reference, _SupportReferenceProjection)
            for reference in self.published_memory_refs
        ):
            raise TypeError(
                "SupportMemoryEpisode.published_memory_refs must contain only _SupportReferenceProjection instances."
            )
        if any(
            not isinstance(reference, _SupportReferenceProjection)
            for reference in self.artifact_refs
        ):
            raise TypeError(
                "SupportMemoryEpisode.artifact_refs must contain only _SupportReferenceProjection instances."
            )

    def payload_dict(self) -> dict[str, object]:
        return {
            "event_signatures": [
                {
                    "native_event_name": event.native_event_name,
                    "payload_kind": event.payload_kind,
                    "payload_metadata_keys": list(event.payload_metadata_keys),
                }
                for event in self.event_signatures
            ],
            "candidate_refs": list(self.candidate_refs),
            "wake_reason_tags": list(self.wake_reason_tags),
            "degradation_reason_codes": list(self.degradation_reason_codes),
            "contradiction_source_tags": list(self.contradiction_source_tags),
            "contradiction_evidence_tags": list(self.contradiction_evidence_tags),
            "branch_registry": list(self.branch_registry),
            "pending_goal_refs": list(self.pending_goal_refs),
            "role_view_tags": list(self.role_view_tags),
            "budget_history": list(self.budget_history),
            "brake_history": list(self.brake_history),
            "reminders": list(self.reminders),
            "host_affordance_tags": list(self.host_affordance_tags),
            "host_approval_boundary_tags": list(self.host_approval_boundary_tags),
            "host_constraint_tags": list(self.host_constraint_tags),
            "host_metadata_keys": list(self.host_metadata_keys),
            "published_memory_refs": [
                {
                    "reference_kind": reference.reference_kind,
                    "reference_id": reference.reference_id,
                    "tags": list(reference.tags),
                    "metadata_keys": list(reference.metadata_keys),
                }
                for reference in self.published_memory_refs
            ],
            "artifact_refs": [
                {
                    "reference_kind": reference.reference_kind,
                    "reference_id": reference.reference_id,
                    "tags": list(reference.tags),
                    "metadata_keys": list(reference.metadata_keys),
                }
                for reference in self.artifact_refs
            ],
        }

    @classmethod
    def from_payload(
        cls,
        *,
        episode_fingerprint: str,
        recorded_at: str,
        host_name: str,
        source_label: str,
        payload: dict[str, object],
    ) -> "SupportMemoryEpisode":
        def _projection_rows(name: str) -> tuple[_SupportReferenceProjection, ...]:
            rows = payload.get(name, [])
            if not isinstance(rows, list):
                raise TypeError(f"{name} must be a list in persisted payload.")
            return tuple(
                _SupportReferenceProjection(
                    reference_kind=str(row["reference_kind"]),
                    reference_id=str(row["reference_id"]),
                    tags=tuple(str(value) for value in row.get("tags", [])),
                    metadata_keys=tuple(str(value) for value in row.get("metadata_keys", [])),
                )
                for row in rows
                if isinstance(row, dict)
            )

        return cls(
            episode_fingerprint=episode_fingerprint,
            recorded_at=recorded_at,
            host_name=host_name,
            source_label=source_label,
            event_signatures=tuple(
                SupportEventSignature(
                    native_event_name=str(row["native_event_name"]),
                    payload_kind=str(row["payload_kind"]),
                    payload_metadata_keys=tuple(
                        str(value) for value in row.get("payload_metadata_keys", [])
                    ),
                )
                for row in payload.get("event_signatures", [])
                if isinstance(row, dict)
            ),
            candidate_refs=tuple(str(value) for value in payload.get("candidate_refs", [])),
            wake_reason_tags=tuple(str(value) for value in payload.get("wake_reason_tags", [])),
            degradation_reason_codes=tuple(
                str(value) for value in payload.get("degradation_reason_codes", [])
            ),
            contradiction_source_tags=tuple(
                str(value) for value in payload.get("contradiction_source_tags", [])
            ),
            contradiction_evidence_tags=tuple(
                str(value) for value in payload.get("contradiction_evidence_tags", [])
            ),
            branch_registry=tuple(str(value) for value in payload.get("branch_registry", [])),
            pending_goal_refs=tuple(str(value) for value in payload.get("pending_goal_refs", [])),
            role_view_tags=tuple(str(value) for value in payload.get("role_view_tags", [])),
            budget_history=tuple(str(value) for value in payload.get("budget_history", [])),
            brake_history=tuple(str(value) for value in payload.get("brake_history", [])),
            reminders=tuple(str(value) for value in payload.get("reminders", [])),
            host_affordance_tags=tuple(
                str(value) for value in payload.get("host_affordance_tags", [])
            ),
            host_approval_boundary_tags=tuple(
                str(value) for value in payload.get("host_approval_boundary_tags", [])
            ),
            host_constraint_tags=tuple(
                str(value) for value in payload.get("host_constraint_tags", [])
            ),
            host_metadata_keys=tuple(
                str(value) for value in payload.get("host_metadata_keys", [])
            ),
            published_memory_refs=_projection_rows("published_memory_refs"),
            artifact_refs=_projection_rows("artifact_refs"),
        )


def _reference_projection(reference: SupportReference) -> _SupportReferenceProjection:
    return _SupportReferenceProjection(
        reference_kind=reference.reference_kind,
        reference_id=reference.reference_id,
        tags=tuple(sorted(reference.tags)),
        metadata_keys=_metadata_keys(reference.metadata),
    )


def _event_signature_payload_keys(snapshot: SupportSnapshot, event_index: int) -> tuple[str, ...]:
    event = snapshot.trace.recent_events[event_index]
    event_metadata = _metadata_keys(event.payload_metadata)
    handle_metadata = ()
    if event.payload_handle is not None:
        handle_metadata = _metadata_keys(event.payload_handle.metadata)
    return tuple(sorted(set(event_metadata) | set(handle_metadata)))


def _episode_payload_dict(
    snapshot: SupportSnapshot,
) -> dict[str, object]:
    event_signatures = tuple(
        SupportEventSignature(
            native_event_name=event.native_event_name,
            payload_kind=(
                event.payload_handle.payload_kind
                if event.payload_handle is not None
                else "none"
            ),
            payload_metadata_keys=_event_signature_payload_keys(snapshot, index),
        )
        for index, event in enumerate(snapshot.trace.recent_events)
    )
    contradiction_source_tags = tuple(
        contradiction.source_tag
        for record in snapshot.trace.degradation_records
        for contradiction in record.contradiction_records
    )
    contradiction_evidence_tags = tuple(
        tag
        for record in snapshot.trace.degradation_records
        for contradiction in record.contradiction_records
        for tag in contradiction.evidence_tags
    )
    published_memory_refs = tuple(
        _reference_projection(reference)
        for reference in snapshot.exec_memory_pub.published_memory_refs
    )
    artifact_refs = tuple(
        _reference_projection(reference)
        for reference in snapshot.exec_memory_pub.artifact_refs
    )
    return {
        "event_signatures": [
            {
                "native_event_name": event.native_event_name,
                "payload_kind": event.payload_kind,
                "payload_metadata_keys": list(event.payload_metadata_keys),
            }
            for event in event_signatures
        ],
        "candidate_refs": list(_dedupe_ordered(snapshot.trace.candidate_refs)),
        "wake_reason_tags": list(
            _dedupe_ordered(tuple(receipt.reason_tag for receipt in snapshot.trace.wake_receipts))
        ),
        "degradation_reason_codes": list(
            _dedupe_ordered(tuple(record.reason_code for record in snapshot.trace.degradation_records))
        ),
        "contradiction_source_tags": list(_dedupe_ordered(contradiction_source_tags)),
        "contradiction_evidence_tags": list(_dedupe_ordered(contradiction_evidence_tags)),
        "branch_registry": list(_dedupe_ordered(snapshot.session.branch_registry)),
        "pending_goal_refs": list(_dedupe_ordered(snapshot.session.pending_goal_refs)),
        "role_view_tags": list(tuple(sorted(snapshot.session.role_view_tags))),
        "budget_history": list(_dedupe_ordered(snapshot.session.budget_history)),
        "brake_history": list(_dedupe_ordered(snapshot.session.brake_history)),
        "reminders": list(_bounded_reminders(snapshot.session.reminders)),
        "host_affordance_tags": list(tuple(sorted(snapshot.host.affordance_tags))),
        "host_approval_boundary_tags": list(tuple(sorted(snapshot.host.approval_boundary_tags))),
        "host_constraint_tags": list(tuple(sorted(snapshot.host.constraint_tags))),
        "host_metadata_keys": list(_metadata_keys(snapshot.host.metadata)),
        "published_memory_refs": [
            {
                "reference_kind": reference.reference_kind,
                "reference_id": reference.reference_id,
                "tags": list(reference.tags),
                "metadata_keys": list(reference.metadata_keys),
            }
            for reference in published_memory_refs
        ],
        "artifact_refs": [
            {
                "reference_kind": reference.reference_kind,
                "reference_id": reference.reference_id,
                "tags": list(reference.tags),
                "metadata_keys": list(reference.metadata_keys),
            }
            for reference in artifact_refs
        ],
    }


def episode_from_support_snapshot(
    snapshot: SupportSnapshot,
    *,
    host_name: str,
    source_label: str,
    recorded_at: str | None = None,
) -> SupportMemoryEpisode:
    if not isinstance(snapshot, SupportSnapshot):
        actual_type = type(snapshot).__name__
        raise TypeError(
            "episode_from_support_snapshot() requires SupportSnapshot, "
            f"got {actual_type}.",
        )
    host_name = _require_text(host_name, field_name="episode_from_support_snapshot.host_name")
    source_label = _require_text(
        source_label,
        field_name="episode_from_support_snapshot.source_label",
    )
    recorded_at = recorded_at or datetime.now(timezone.utc).isoformat(timespec="seconds")
    payload = _episode_payload_dict(snapshot)
    fingerprint_payload = {
        "host_name": host_name,
        "source_label": source_label,
        "payload": payload,
    }
    episode_fingerprint = hashlib.sha256(
        json.dumps(fingerprint_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return SupportMemoryEpisode.from_payload(
        episode_fingerprint=episode_fingerprint,
        recorded_at=recorded_at,
        host_name=host_name,
        source_label=source_label,
        payload=payload,
    )


class SqliteSupportMemoryStore:
    """Durable AUX-only store for bounded support-memory episodes."""

    def __init__(self, path: str | Path = DEFAULT_SUPPORT_MEMORY_STORE_PATH) -> None:
        self.path = path if isinstance(path, str) else Path(path)
        self._path_text = str(self.path)
        self._connection: sqlite3.Connection | None = None
        if self._path_text == ":memory:":
            self._connection = sqlite3.connect(":memory:")
            self._connection.row_factory = sqlite3.Row
            self._ensure_schema(self._connection)

    def _ensure_schema(self, connection: sqlite3.Connection) -> None:
        connection.executescript(_EPISODE_SCHEMA)
        columns = {
            str(row["name"])
            for row in connection.execute("PRAGMA table_info(episodes)")
        }
        if "recorded_at_epoch" not in columns:
            connection.execute("ALTER TABLE episodes ADD COLUMN recorded_at_epoch INTEGER")
        backfill_rows = tuple(
            connection.execute(
                """
                SELECT episode_fingerprint, recorded_at
                FROM episodes
                WHERE recorded_at_epoch IS NULL
                """
            )
        )
        for row in backfill_rows:
            normalized_recorded_at, recorded_at_epoch = _normalized_recorded_at_fields(
                str(row["recorded_at"]),
                field_name=(
                    "SqliteSupportMemoryStore.legacy_recorded_at"
                    f"[{row['episode_fingerprint']}]"
                ),
            )
            connection.execute(
                """
                UPDATE episodes
                SET recorded_at = ?, recorded_at_epoch = ?
                WHERE episode_fingerprint = ?
                """,
                (
                    normalized_recorded_at,
                    recorded_at_epoch,
                    str(row["episode_fingerprint"]),
                ),
            )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_episodes_host_recorded_at_epoch
            ON episodes(host_name, recorded_at_epoch)
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_episodes_source_recorded_at_epoch
            ON episodes(source_label, recorded_at_epoch)
            """
        )
        connection.commit()

    def _connect(self) -> sqlite3.Connection:
        if self._connection is not None:
            return self._connection
        if self._path_text != ":memory:":
            Path(self._path_text).parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self._path_text)
        connection.row_factory = sqlite3.Row
        self._ensure_schema(connection)
        return connection

    @contextmanager
    def _connection_context(self) -> Iterator[sqlite3.Connection]:
        connection = self._connect()
        try:
            yield connection
        finally:
            if self._connection is None:
                connection.close()

    def close(self) -> None:
        if self._connection is None:
            return
        self._connection.close()
        self._connection = None

    def __enter__(self) -> "SqliteSupportMemoryStore":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def insert_episode(self, episode: SupportMemoryEpisode) -> bool:
        if not isinstance(episode, SupportMemoryEpisode):
            actual_type = type(episode).__name__
            raise TypeError(
                "SqliteSupportMemoryStore.insert_episode() requires SupportMemoryEpisode, "
                f"got {actual_type}.",
            )
        _, recorded_at_epoch = _normalized_recorded_at_fields(
            episode.recorded_at,
            field_name="SqliteSupportMemoryStore.insert_episode.recorded_at",
        )
        with self._connection_context() as connection:
            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO episodes(
                    episode_fingerprint,
                    recorded_at,
                    recorded_at_epoch,
                    host_name,
                    source_label,
                    payload_json
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    episode.episode_fingerprint,
                    episode.recorded_at,
                    recorded_at_epoch,
                    episode.host_name,
                    episode.source_label,
                    json.dumps(
                        episode.payload_dict(),
                        sort_keys=True,
                        separators=(",", ":"),
                    ),
                ),
            )
            connection.commit()
            return cursor.rowcount > 0

    def load_episodes(
        self,
        *,
        host_name: str,
        source_label: str | None = None,
        horizon_hours: int = 72,
        limit: int = 32,
        now: datetime | None = None,
    ) -> tuple[SupportMemoryEpisode, ...]:
        host_name = _require_text(host_name, field_name="SqliteSupportMemoryStore.load_episodes.host_name")
        if source_label is not None:
            source_label = _require_text(
                source_label,
                field_name="SqliteSupportMemoryStore.load_episodes.source_label",
            )
        if isinstance(limit, bool) or not isinstance(limit, int) or limit <= 0:
            raise ValueError("SqliteSupportMemoryStore.load_episodes.limit must be positive int.")
        if isinstance(horizon_hours, bool) or not isinstance(horizon_hours, int) or horizon_hours <= 0:
            raise ValueError(
                "SqliteSupportMemoryStore.load_episodes.horizon_hours must be positive int."
            )
        current_time = (
            _require_aware_datetime(
                now,
                field_name="SqliteSupportMemoryStore.load_episodes.now",
            )
            if now is not None
            else datetime.now(timezone.utc).replace(microsecond=0)
        )
        since_epoch = int((current_time - timedelta(hours=horizon_hours)).timestamp())
        params: list[object] = [host_name, since_epoch]
        query = """
            SELECT episode_fingerprint, recorded_at, host_name, source_label, payload_json
            FROM episodes
            WHERE host_name = ? AND recorded_at_epoch >= ?
        """
        if source_label is not None:
            query += " AND source_label = ?"
            params.append(source_label)
        query += " ORDER BY recorded_at_epoch DESC, recorded_at DESC, episode_fingerprint DESC LIMIT ?"
        params.append(limit)
        with self._connection_context() as connection:
            rows = tuple(connection.execute(query, tuple(params)))
        episodes = [
            SupportMemoryEpisode.from_payload(
                episode_fingerprint=str(row["episode_fingerprint"]),
                recorded_at=str(row["recorded_at"]),
                host_name=str(row["host_name"]),
                source_label=str(row["source_label"]),
                payload=json.loads(str(row["payload_json"])),
            )
            for row in rows
        ]
        episodes.reverse()
        return tuple(episodes)


__all__ = [
    "DEFAULT_SUPPORT_MEMORY_STORE_PATH",
    "SqliteSupportMemoryStore",
    "SupportEventSignature",
    "SupportMemoryEpisode",
    "episode_from_support_snapshot",
]
```

### `cortex/aux/support_priors.py`

```python
"""AUX-side builders for lawful support-memory priors."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from cortex.core.envelopes import MetadataField
from cortex.core.support import SupportReference, SupportSnapshot
from cortex.sre.families import SoftControlFamily
from cortex.sre.memory_priors import (
    HostReliabilityPrior,
    SupportMemoryPriorAppendix,
    SupportMemoryPriorScore,
)
from cortex.sre.opportunities import PROBE_FAILURE_CLASSES

from ._support_match import (
    _dedupe_support_refs,
    _match_score,
    _reference_tokens,
    _source_refs_for_retrieval,
)
from .augmentation import AugmentedSupportSnapshot

_LIVE_MEMORY_ELIGIBLE_FAMILIES = frozenset(
    {
        SoftControlFamily.CHECK,
        SoftControlFamily.SEEK_CONTEXT,
        SoftControlFamily.BRANCH,
        SoftControlFamily.REDIRECT,
    }
)
_LIVE_MEMORY_METADATA_KEYS = frozenset(
    {
        "live_reentry_state",
        "live_source_host_name",
        "live_target_host_name",
    }
)


def _clip_unit(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _clip_prior_score(value: float) -> float:
    return max(0.0, min(0.75, float(value)))


@dataclass(frozen=True, slots=True)
class _HostReliabilityAdjustment:
    weight: float
    ttl_expired: bool = False

    @property
    def active(self) -> bool:
        return self.weight > 0.0 and not self.ttl_expired


def _refs_by_kind(
    references: tuple[SupportReference, ...],
    *kinds: str,
) -> tuple[SupportReference, ...]:
    allowed = set(kinds)
    return tuple(reference for reference in references if reference.reference_kind in allowed)


def _metadata_int(
    metadata: tuple[MetadataField, ...],
    key: str,
) -> int:
    for field in metadata:
        if field.key != key:
            continue
        try:
            return int(field.value)
        except (TypeError, ValueError):
            return 0
    return 0


def _metadata_str(
    metadata: tuple[MetadataField, ...],
    key: str,
) -> str:
    for field in metadata:
        if field.key != key:
            continue
        if isinstance(field.value, str):
            return field.value
        return str(field.value)
    return ""


def _normalized_candidate(reference: SupportReference) -> SupportReference:
    normalized_kind = {
        "retrieval-prior": "memory",
        "memory-summary": "memory",
        "branch-prior": "branch",
        "contradiction-summary": "contradiction",
        "uncertainty-calibration": "uncertainty",
    }.get(reference.reference_kind, reference.reference_kind)
    if normalized_kind == reference.reference_kind:
        return reference
    return SupportReference(
        normalized_kind,
        reference.reference_id,
        tags=reference.tags,
        metadata=reference.metadata,
    )


def _best_match_signal(
    source_refs: tuple[SupportReference, ...],
    candidate_refs: tuple[SupportReference, ...],
    *,
    base_score: float,
) -> float:
    best = 0.0
    for source_ref in source_refs:
        for candidate_ref in candidate_refs:
            normalized_candidate = _normalized_candidate(candidate_ref)
            token_overlap = _reference_tokens(source_ref) & _reference_tokens(normalized_candidate)
            if not token_overlap:
                continue
            best = max(
                best,
                _match_score(source_ref, normalized_candidate, base_score=base_score),
            )
    return _clip_unit(best)


def _target_branch_refs(snapshot: AugmentedSupportSnapshot) -> tuple[SupportReference, ...]:
    return _target_branch_refs_for_snapshot(snapshot.core_snapshot)


def _target_branch_refs_for_snapshot(
    snapshot: SupportSnapshot,
) -> tuple[SupportReference, ...]:
    branch_refs = tuple(
        SupportReference("branch", branch_ref, tags=frozenset({"resume-track"}))
        for branch_ref in snapshot.session.branch_registry
        if branch_ref != "main"
    )
    reminder_refs = tuple(
        SupportReference("reminder", reminder, tags=frozenset({"continuity-reminder"}))
        for reminder in snapshot.session.reminders
    )
    goal_refs = tuple(
        SupportReference("goal", goal_ref, tags=frozenset({"pending-goal"}))
        for goal_ref in snapshot.session.pending_goal_refs
    )
    return _dedupe_support_refs(branch_refs + reminder_refs + goal_refs)


def _target_contradiction_refs(snapshot: AugmentedSupportSnapshot) -> tuple[SupportReference, ...]:
    return _target_contradiction_refs_for_snapshot(snapshot.core_snapshot)


def _target_contradiction_refs_for_snapshot(
    snapshot: SupportSnapshot,
) -> tuple[SupportReference, ...]:
    refs: list[SupportReference] = []
    for record in snapshot.trace.degradation_records:
        tags = set(record.capability_tags | {record.reason_code})
        for contradiction in record.contradiction_records:
            tags.add(contradiction.source_tag)
            tags.update(contradiction.evidence_tags)
        refs.append(
            SupportReference(
                "contradiction",
                record.reason_code,
                tags=frozenset(tags),
            )
        )
    return _dedupe_support_refs(tuple(refs))


def _target_uncertainty_refs(snapshot: AugmentedSupportSnapshot) -> tuple[SupportReference, ...]:
    return _target_uncertainty_refs_for_snapshot(snapshot.core_snapshot)


def _target_uncertainty_refs_for_snapshot(
    snapshot: SupportSnapshot,
) -> tuple[SupportReference, ...]:
    refs = tuple(
        SupportReference("uncertainty", brake_entry, tags=frozenset({"brake-history"}))
        for brake_entry in snapshot.session.brake_history
    ) + tuple(
        SupportReference("wake", receipt.reason_tag, tags=frozenset({"wake-receipt"}))
        for receipt in snapshot.trace.wake_receipts
    )
    return _dedupe_support_refs(refs)


def _has_token(signal_tokens: frozenset[str], token: str) -> bool:
    return token in signal_tokens


def _host_reliability_prior(
    snapshot: AugmentedSupportSnapshot,
    signal_profile: SupportMemorySignalProfile,
) -> HostReliabilityPrior:
    degradation_records = snapshot.core_snapshot.trace.degradation_records
    contradiction_counter = sum(
        len(record.contradiction_records) for record in degradation_records
    )
    reason_code_tokens = {
        token
        for record in degradation_records
        for token in record.reason_code.replace("-", "_").split("_")
    }
    constraint_tags = snapshot.core_snapshot.host.constraint_tags
    timeout_rate = 1.0 if "timeout" in reason_code_tokens else 0.0
    degradation_rate = _clip_unit(
        (0.20 * len(degradation_records))
        + (0.15 if constraint_tags else 0.0)
        + (0.10 * signal_profile.burden_penalty)
    )
    capability_availability = 1.0
    if "missing-capability" in constraint_tags:
        capability_availability = 0.35
    elif constraint_tags:
        capability_availability = 0.65
    failure_classes: list[str] = []
    if timeout_rate > 0.0:
        failure_classes.append("timed-out")
    if degradation_records:
        failure_classes.append("degraded")
    if "missing-capability" in constraint_tags:
        failure_classes.append("unsupported")
    source_snapshot_count = _metadata_int(
        snapshot.auxiliary_support.metadata,
        "source_snapshot_count",
    )
    ttl_hours = 72 if source_snapshot_count > 1 else 24
    return HostReliabilityPrior(
        timeout_rate=timeout_rate,
        degradation_rate=degradation_rate,
        capability_availability=capability_availability,
        contradiction_counter=contradiction_counter,
        ttl_hours=ttl_hours,
        last_validated_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        probe_failure_classes=tuple(sorted(set(failure_classes))),
    )


def _parse_validated_at(timestamp: str | None) -> datetime | None:
    if timestamp is None:
        return None
    candidate = timestamp.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _host_reliability_adjustment(
    prior: HostReliabilityPrior,
    *,
    now: datetime | None = None,
) -> _HostReliabilityAdjustment:
    current_time = now or datetime.now(timezone.utc)
    last_validated = _parse_validated_at(prior.last_validated_at)
    if last_validated is not None:
        if current_time - last_validated > timedelta(hours=prior.ttl_hours):
            return _HostReliabilityAdjustment(weight=0.0, ttl_expired=True)

    weight = _clip_unit(
        (0.70 * prior.capability_availability)
        - (0.45 * prior.timeout_rate)
        - (0.25 * prior.degradation_rate)
    )
    return _HostReliabilityAdjustment(weight=weight)


def _reliability_signal_for_family(
    profile: SupportMemorySignalProfile,
    family: SoftControlFamily,
) -> float:
    if family is SoftControlFamily.BRANCH:
        return max(profile.branch_resume_signal, profile.retrieval_reuse_signal * 0.40)
    if family is SoftControlFamily.CHECK:
        return max(
            profile.contradiction_review_signal,
            profile.uncertainty_calibration_signal * 0.60,
        )
    if family is SoftControlFamily.SEEK_CONTEXT:
        return max(
            profile.retrieval_reuse_signal,
            profile.uncertainty_calibration_signal,
        )
    return 0.0


def _apply_host_reliability_weight(
    family: SoftControlFamily,
    *,
    base_score: float,
    reason_tags: frozenset[str],
    profile: SupportMemorySignalProfile,
    reliability_prior: HostReliabilityPrior,
    host_affordance_tags: frozenset[str],
    current_contradiction_active: bool,
    recent_probe_failure_class: str | None,
) -> tuple[float, frozenset[str], float]:
    if family not in {
        SoftControlFamily.BRANCH,
        SoftControlFamily.CHECK,
        SoftControlFamily.SEEK_CONTEXT,
    }:
        return base_score, reason_tags, 0.0

    adjustment = _host_reliability_adjustment(reliability_prior)
    if adjustment.ttl_expired:
        return (
            base_score,
            reason_tags | frozenset({"q_mem-host:ttl-expired"}),
            0.0,
        )

    if (
        family in {SoftControlFamily.CHECK, SoftControlFamily.SEEK_CONTEXT}
        and reliability_prior.affordance_scope_tags
        and not (
            set(host_affordance_tags) & set(reliability_prior.affordance_scope_tags)
        )
    ):
        return (
            base_score,
            reason_tags | frozenset({"q_mem-host:affordance-mismatch"}),
            0.0,
        )

    if current_contradiction_active:
        return (
            base_score,
            reason_tags | frozenset({"q_mem-host:current-contradiction-invalidated"}),
            0.0,
        )

    if (
        family in {SoftControlFamily.CHECK, SoftControlFamily.SEEK_CONTEXT}
        and recent_probe_failure_class in PROBE_FAILURE_CLASSES
    ):
        return (
            base_score,
            reason_tags | frozenset({"q_mem-host:recent-probe-failure-invalidated"}),
            0.0,
        )

    signal_strength = _reliability_signal_for_family(profile, family)
    if base_score <= 0.0 or signal_strength <= 0.0 or adjustment.weight <= 0.0:
        return base_score, reason_tags, 0.0

    reliability_bonus = 0.36 * adjustment.weight * max(signal_strength, 0.20)
    adjusted_score = _clip_prior_score(base_score + reliability_bonus)
    delta = adjusted_score - base_score
    updated_tags = reason_tags | frozenset({"q_mem-host:reliability-active"})
    if (
        reliability_prior.contradiction_counter > 0
        or reliability_prior.probe_failure_classes
    ):
        updated_tags = updated_tags | frozenset({"q_mem-host:success-reopened"})
    return adjusted_score, updated_tags, delta


@dataclass(frozen=True, slots=True)
class SupportMemorySignalProfile:
    retrieval_reuse_signal: float
    branch_resume_signal: float
    contradiction_review_signal: float
    uncertainty_calibration_signal: float
    burden_penalty: float

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "retrieval_reuse_signal",
            _clip_unit(self.retrieval_reuse_signal),
        )
        object.__setattr__(
            self,
            "branch_resume_signal",
            _clip_unit(self.branch_resume_signal),
        )
        object.__setattr__(
            self,
            "contradiction_review_signal",
            _clip_unit(self.contradiction_review_signal),
        )
        object.__setattr__(
            self,
            "uncertainty_calibration_signal",
            _clip_unit(self.uncertainty_calibration_signal),
        )
        object.__setattr__(
            self,
            "burden_penalty",
            _clip_unit(self.burden_penalty),
        )


def _build_signal_profile(snapshot: AugmentedSupportSnapshot) -> SupportMemorySignalProfile:
    appendix = snapshot.auxiliary_support
    derived_refs = appendix.derived_support_refs

    retrieval_refs = _refs_by_kind(derived_refs, "memory", "artifact", "result-artifact")
    branch_candidate_refs = _refs_by_kind(derived_refs, "branch", "memory", "artifact")
    contradiction_refs = _refs_by_kind(derived_refs, "contradiction")
    uncertainty_refs = _refs_by_kind(derived_refs, "uncertainty", "wake")

    retrieval_signal = _best_match_signal(
        _source_refs_for_retrieval(snapshot.core_snapshot),
        retrieval_refs,
        base_score=0.18,
    )

    branch_signal = _best_match_signal(
        _target_branch_refs(snapshot),
        branch_candidate_refs,
        base_score=0.16,
    )
    if branch_signal > 0.0 and snapshot.core_snapshot.session.reminders:
        branch_signal = _clip_unit(branch_signal + 0.05)

    contradiction_signal = _best_match_signal(
        _target_contradiction_refs(snapshot),
        contradiction_refs,
        base_score=0.20,
    )
    if contradiction_signal > 0.0 and snapshot.core_snapshot.trace.degradation_records:
        contradiction_signal = _clip_unit(contradiction_signal + 0.15)

    uncertainty_signal = _best_match_signal(
        _target_uncertainty_refs(snapshot),
        uncertainty_refs,
        base_score=0.18,
    )
    guarded_history = {
        entry
        for entry in snapshot.core_snapshot.session.brake_history
        if entry in {"guarded", "latched"}
    }
    if uncertainty_signal > 0.0 and guarded_history:
        uncertainty_signal = _clip_unit(uncertainty_signal + 0.12)
    if uncertainty_signal > 0.0 and snapshot.core_snapshot.trace.wake_receipts:
        uncertainty_signal = _clip_unit(uncertainty_signal + 0.08)

    token_pool = frozenset(
        token
        for reference in derived_refs
        for token in _reference_tokens(reference)
    )
    source_snapshot_count = _metadata_int(appendix.metadata, "source_snapshot_count")
    source_label = _metadata_str(appendix.metadata, "source")
    positive_prior_state = _metadata_str(appendix.metadata, "positive_prior_state")
    fanout_penalty = max(0.0, 0.05 * (len(derived_refs) - 4))
    source_penalty = 0.0
    if source_label != "aux/distillation":
        source_penalty = max(0.0, 0.10 * (source_snapshot_count - 1))
    burden_tag_penalty = 0.15 if _has_token(token_pool, "burden") else 0.0
    drift_tag_penalty = 0.10 if _has_token(token_pool, "drift") else 0.0
    suppressed_burden_penalty = (
        0.35 if "burden-heavy" in positive_prior_state else 0.0
    )
    burden_penalty = _clip_unit(
        fanout_penalty
        + source_penalty
        + burden_tag_penalty
        + drift_tag_penalty
        + suppressed_burden_penalty
    )

    return SupportMemorySignalProfile(
        retrieval_reuse_signal=retrieval_signal,
        branch_resume_signal=branch_signal,
        contradiction_review_signal=contradiction_signal,
        uncertainty_calibration_signal=uncertainty_signal,
        burden_penalty=burden_penalty,
    )


def _reason_tags(
    profile: SupportMemorySignalProfile,
    *,
    include_retrieval: bool = False,
    include_branch: bool = False,
    include_contradiction: bool = False,
    include_uncertainty: bool = False,
) -> frozenset[str]:
    tags = {"q_mem:active"}
    if include_retrieval and profile.retrieval_reuse_signal > 0.0:
        tags.add("q_mem-signal:retrieval")
    if include_branch and profile.branch_resume_signal > 0.0:
        tags.add("q_mem-signal:branch")
    if include_contradiction and profile.contradiction_review_signal > 0.0:
        tags.add("q_mem-signal:contradiction")
    if include_uncertainty and profile.uncertainty_calibration_signal > 0.0:
        tags.add("q_mem-signal:uncertainty")
    if profile.burden_penalty > 0.0:
        tags.add("q_mem-penalty:burden")
    return frozenset(tags)


def _replace_live_metadata(
    metadata: tuple[MetadataField, ...],
    *,
    state: str,
    source_host_name: str,
    target_host_name: str,
) -> tuple[MetadataField, ...]:
    retained = tuple(
        field for field in metadata if field.key not in _LIVE_MEMORY_METADATA_KEYS
    )
    return (
        MetadataField("live_reentry_state", state),
        MetadataField("live_source_host_name", source_host_name),
        MetadataField("live_target_host_name", target_host_name),
    ) + retained


def _support_ref_overlap(
    source_refs: tuple[SupportReference, ...],
    candidate_refs: tuple[SupportReference, ...],
    *,
    threshold: float = 0.25,
) -> bool:
    for source_ref in source_refs:
        for candidate_ref in candidate_refs:
            normalized_candidate = _normalized_candidate(candidate_ref)
            if _match_score(
                source_ref,
                normalized_candidate,
                base_score=0.0,
            ) >= threshold:
                return True
    return False


def _live_context_refs_for_family(
    snapshot: SupportSnapshot,
    family: SoftControlFamily,
) -> tuple[SupportReference, ...]:
    if family is SoftControlFamily.BRANCH:
        return _target_branch_refs_for_snapshot(snapshot)
    if family is SoftControlFamily.CHECK:
        return _dedupe_support_refs(
            _target_contradiction_refs_for_snapshot(snapshot)
            + _target_uncertainty_refs_for_snapshot(snapshot)
        )
    if family is SoftControlFamily.SEEK_CONTEXT:
        return _dedupe_support_refs(
            _source_refs_for_retrieval(snapshot)
            + _target_uncertainty_refs_for_snapshot(snapshot)
        )
    if family is SoftControlFamily.REDIRECT:
        return _dedupe_support_refs(
            _target_branch_refs_for_snapshot(snapshot)
            + _source_refs_for_retrieval(snapshot)
            + _target_contradiction_refs_for_snapshot(snapshot)
    )
    return ()


def _live_degradation_invalidation_tag(snapshot: SupportSnapshot) -> str | None:
    if any(record.contradiction_records for record in snapshot.trace.degradation_records):
        return "q_mem-live:invalidated:contradiction"
    if snapshot.trace.degradation_records:
        return "q_mem-live:invalidated:degradation"
    return None


def _live_resume_context_invalidation_tag(
    snapshot: SupportSnapshot,
    score: SupportMemoryPriorScore,
) -> str | None:
    if score.family not in {SoftControlFamily.BRANCH, SoftControlFamily.REDIRECT}:
        return None
    branch_context_refs = _target_branch_refs_for_snapshot(snapshot)
    if not branch_context_refs or not _support_ref_overlap(
        branch_context_refs,
        score.support_refs,
    ):
        return None
    return _live_degradation_invalidation_tag(snapshot)


def _live_reentry_reason_tags(
    *,
    snapshot: SupportSnapshot,
    score: SupportMemoryPriorScore,
    recent_probe_failure_class: str | None,
) -> frozenset[str]:
    tags: set[str] = set()
    if score.family not in _LIVE_MEMORY_ELIGIBLE_FAMILIES:
        tags.add("q_mem-live:family-ineligible")
        return frozenset(tags)

    context_refs = _live_context_refs_for_family(snapshot, score.family)
    if not context_refs or not _support_ref_overlap(context_refs, score.support_refs):
        tags.add("q_mem-live:context-miss")
        return frozenset(tags)

    if "q_mem-host:ttl-expired" in score.reason_tags:
        tags.add("q_mem-live:invalidated:ttl-expired")

    if (
        recent_probe_failure_class in PROBE_FAILURE_CLASSES
        and score.family in {SoftControlFamily.CHECK, SoftControlFamily.SEEK_CONTEXT}
        and _support_ref_overlap(
            _target_uncertainty_refs_for_snapshot(snapshot),
            score.support_refs,
        )
    ):
        tags.add("q_mem-live:invalidated:probe-failure")

    resume_context_invalidation_tag = _live_resume_context_invalidation_tag(
        snapshot,
        score,
    )
    if resume_context_invalidation_tag is not None:
        tags.add(resume_context_invalidation_tag)

    if not tags:
        tags.add("q_mem-live:eligible")
    return frozenset(tags)


def filter_live_support_memory_prior_appendix(
    snapshot: SupportSnapshot,
    appendix: SupportMemoryPriorAppendix,
    *,
    target_host_name: str,
    recent_probe_failure_class: str | None = None,
) -> SupportMemoryPriorAppendix:
    if not isinstance(snapshot, SupportSnapshot):
        actual_type = type(snapshot).__name__
        raise TypeError(
            "filter_live_support_memory_prior_appendix() requires SupportSnapshot, "
            f"got {actual_type}.",
        )
    if not isinstance(appendix, SupportMemoryPriorAppendix):
        actual_type = type(appendix).__name__
        raise TypeError(
            "filter_live_support_memory_prior_appendix() requires SupportMemoryPriorAppendix, "
            f"got {actual_type}.",
        )
    if not (isinstance(target_host_name, str) and target_host_name.strip()):
        raise ValueError(
            "filter_live_support_memory_prior_appendix().target_host_name must be non-empty after trimming."
        )
    if (
        recent_probe_failure_class is not None
        and recent_probe_failure_class not in PROBE_FAILURE_CLASSES
    ):
        raise ValueError(
            "filter_live_support_memory_prior_appendix().recent_probe_failure_class must be a canonical probe failure class or None."
        )

    source_host_name = _metadata_str(appendix.metadata, "host_name")
    host_match = source_host_name == target_host_name
    filtered_scores: list[SupportMemoryPriorScore] = []

    for score in appendix.scores:
        live_tags = set(score.reason_tags)
        if not host_match:
            if (
                score.family in _LIVE_MEMORY_ELIGIBLE_FAMILIES
                and score.score > 0.0
            ):
                live_tags.add("q_mem-live:invalidated:host-mismatch")
            elif score.family not in _LIVE_MEMORY_ELIGIBLE_FAMILIES:
                live_tags.add("q_mem-live:family-ineligible")
            filtered_scores.append(
                SupportMemoryPriorScore(
                    family=score.family,
                    score=0.0,
                    reason_tags=frozenset(live_tags),
                    support_refs=score.support_refs,
                    metadata=score.metadata,
                )
            )
            continue

        live_reentry_tags = _live_reentry_reason_tags(
            snapshot=snapshot,
            score=score,
            recent_probe_failure_class=recent_probe_failure_class,
        )
        live_tags.update(live_reentry_tags)
        zero_score = any(
            tag.startswith("q_mem-live:invalidated:")
            for tag in live_reentry_tags
        ) or "q_mem-live:family-ineligible" in live_reentry_tags or (
            "q_mem-live:context-miss" in live_reentry_tags
        )
        filtered_scores.append(
            SupportMemoryPriorScore(
                family=score.family,
                score=0.0 if zero_score else score.score,
                reason_tags=frozenset(live_tags),
                support_refs=score.support_refs,
                metadata=score.metadata,
            )
        )

    state = "host-mismatch"
    if host_match:
        state = (
            "active"
            if any(
                score.family in _LIVE_MEMORY_ELIGIBLE_FAMILIES and score.score > 0.0
                for score in filtered_scores
            )
            else "inactive"
        )

    return SupportMemoryPriorAppendix(
        scores=tuple(filtered_scores),
        appendix_tags=appendix.appendix_tags
        | frozenset({"q_mem-live:runtime-boundary", f"q_mem-live:{state}"}),
        notes=appendix.notes
        + (
            "live support-memory re-entry stays explicit, score-only, host-matched, and family-scoped",
        ),
        metadata=_replace_live_metadata(
            appendix.metadata,
            state=state,
            source_host_name=source_host_name,
            target_host_name=target_host_name,
        ),
        host_reliability_prior=appendix.host_reliability_prior,
    )


def build_support_memory_prior_appendix(
    snapshot: AugmentedSupportSnapshot,
    *,
    enable_host_reliability: bool = True,
    recent_probe_failure_class: str | None = None,
) -> SupportMemoryPriorAppendix:
    if not isinstance(snapshot, AugmentedSupportSnapshot):
        actual_type = type(snapshot).__name__
        raise TypeError(
            "build_support_memory_prior_appendix() requires AugmentedSupportSnapshot, "
            f"got {actual_type}.",
        )
    if not isinstance(enable_host_reliability, bool):
        actual_type = type(enable_host_reliability).__name__
        raise TypeError(
            "build_support_memory_prior_appendix().enable_host_reliability must be bool, "
            f"got {actual_type}.",
        )
    if (
        recent_probe_failure_class is not None
        and recent_probe_failure_class not in PROBE_FAILURE_CLASSES
    ):
        raise ValueError(
            "build_support_memory_prior_appendix().recent_probe_failure_class must be a canonical probe failure class or None."
        )

    appendix = snapshot.auxiliary_support
    if "aux/offline-publication" not in appendix.derived_tags:
        return SupportMemoryPriorAppendix(
            appendix_tags=appendix.derived_tags,
            notes=("offline publication tag missing; Q_mem remains inactive",),
            metadata=appendix.metadata,
        )

    derived_refs = appendix.derived_support_refs
    branch_refs = _refs_by_kind(derived_refs, "branch")
    retrieval_refs = _refs_by_kind(derived_refs, "memory", "artifact")
    contradiction_refs = _refs_by_kind(derived_refs, "contradiction")
    uncertainty_refs = _refs_by_kind(derived_refs, "uncertainty", "wake")
    signal_profile = _build_signal_profile(snapshot)
    reliability_prior = appendix.published_host_reliability_prior
    if reliability_prior is None:
        reliability_prior = _host_reliability_prior(snapshot, signal_profile)
    host_affordance_tags = snapshot.core_snapshot.host.affordance_tags
    current_contradiction_active = bool(
        snapshot.core_snapshot.trace.degradation_records
    )

    branch_base_score = _clip_prior_score(
        (0.55 * signal_profile.branch_resume_signal)
        + (0.15 * signal_profile.retrieval_reuse_signal)
        - (0.25 * signal_profile.burden_penalty)
    )
    branch_reason_tags = _reason_tags(
        signal_profile,
        include_retrieval=True,
        include_branch=True,
    )
    if enable_host_reliability:
        branch_score, branch_reason_tags, branch_delta = _apply_host_reliability_weight(
            SoftControlFamily.BRANCH,
            base_score=branch_base_score,
            reason_tags=branch_reason_tags,
            profile=signal_profile,
            reliability_prior=reliability_prior,
            host_affordance_tags=host_affordance_tags,
            current_contradiction_active=current_contradiction_active,
            recent_probe_failure_class=recent_probe_failure_class,
        )
    else:
        branch_score = branch_base_score
        branch_delta = 0.0

    check_base_score = _clip_prior_score(
        (0.50 * signal_profile.contradiction_review_signal)
        + (0.20 * signal_profile.uncertainty_calibration_signal)
        + (0.10 * signal_profile.retrieval_reuse_signal)
        - (0.15 * signal_profile.burden_penalty)
    )
    check_reason_tags = _reason_tags(
        signal_profile,
        include_retrieval=True,
        include_contradiction=True,
        include_uncertainty=True,
    )
    if enable_host_reliability:
        check_score, check_reason_tags, check_delta = _apply_host_reliability_weight(
            SoftControlFamily.CHECK,
            base_score=check_base_score,
            reason_tags=check_reason_tags,
            profile=signal_profile,
            reliability_prior=reliability_prior,
            host_affordance_tags=host_affordance_tags,
            current_contradiction_active=current_contradiction_active,
            recent_probe_failure_class=recent_probe_failure_class,
        )
    else:
        check_score = check_base_score
        check_delta = 0.0

    seek_context_base_score = _clip_prior_score(
        (0.35 * signal_profile.retrieval_reuse_signal)
        + (0.25 * signal_profile.uncertainty_calibration_signal)
        - (0.15 * signal_profile.burden_penalty)
    )
    seek_context_reason_tags = _reason_tags(
        signal_profile,
        include_retrieval=True,
        include_uncertainty=True,
    )
    if enable_host_reliability:
        (
            seek_context_score,
            seek_context_reason_tags,
            seek_context_delta,
        ) = _apply_host_reliability_weight(
            SoftControlFamily.SEEK_CONTEXT,
            base_score=seek_context_base_score,
            reason_tags=seek_context_reason_tags,
            profile=signal_profile,
            reliability_prior=reliability_prior,
            host_affordance_tags=host_affordance_tags,
            current_contradiction_active=current_contradiction_active,
            recent_probe_failure_class=recent_probe_failure_class,
        )
    else:
        seek_context_score = seek_context_base_score
        seek_context_delta = 0.0

    scores = (
        SupportMemoryPriorScore(
            family=SoftControlFamily.NEUTRAL,
            score=0.0,
        ),
        SupportMemoryPriorScore(
            family=SoftControlFamily.BRANCH,
            score=branch_score,
            reason_tags=branch_reason_tags,
            support_refs=branch_refs + retrieval_refs[:2],
            metadata=(
                MetadataField("q_mem-host:reliability_delta", branch_delta),
            ),
        ),
        SupportMemoryPriorScore(
            family=SoftControlFamily.CHECK,
            score=check_score,
            reason_tags=check_reason_tags,
            support_refs=contradiction_refs + uncertainty_refs[:2],
            metadata=(
                MetadataField("q_mem-host:reliability_delta", check_delta),
            ),
        ),
        SupportMemoryPriorScore(
            family=SoftControlFamily.REDIRECT,
            score=_clip_prior_score(
                (0.30 * signal_profile.retrieval_reuse_signal)
                + (0.20 * signal_profile.branch_resume_signal)
                + (0.10 * signal_profile.contradiction_review_signal)
                - (0.20 * signal_profile.burden_penalty)
            ),
            reason_tags=_reason_tags(
                signal_profile,
                include_retrieval=True,
                include_branch=True,
                include_contradiction=True,
            ),
            support_refs=branch_refs[:1] + retrieval_refs[:2],
        ),
        SupportMemoryPriorScore(
            family=SoftControlFamily.SEEK_CONTEXT,
            score=seek_context_score,
            reason_tags=seek_context_reason_tags,
            support_refs=uncertainty_refs[:2] + retrieval_refs[:1],
            metadata=(
                MetadataField("q_mem-host:reliability_delta", seek_context_delta),
            ),
        ),
        SupportMemoryPriorScore(
            family=SoftControlFamily.BRAKE,
            score=_clip_prior_score(
                (0.35 * signal_profile.contradiction_review_signal)
                + (0.35 * signal_profile.uncertainty_calibration_signal)
                - (0.20 * signal_profile.burden_penalty)
            ),
            reason_tags=_reason_tags(
                signal_profile,
                include_contradiction=True,
                include_uncertainty=True,
            ),
            support_refs=contradiction_refs[:2] + uncertainty_refs[:1],
        ),
        SupportMemoryPriorScore(
            family=SoftControlFamily.ESCALATE,
            score=_clip_prior_score(
                (0.20 * signal_profile.contradiction_review_signal)
                + (0.15 * signal_profile.uncertainty_calibration_signal)
                - (0.25 * signal_profile.burden_penalty)
            ),
            reason_tags=_reason_tags(
                signal_profile,
                include_contradiction=True,
                include_uncertainty=True,
            ),
            support_refs=contradiction_refs[:1],
        ),
    )
    return SupportMemoryPriorAppendix(
        scores=scores,
        appendix_tags=appendix.derived_tags | frozenset({"q_mem:explicit-aux"}),
        notes=appendix.notes
        + (
            "memory-conditioned priors derived from AUX offline publication",
            "host/tool reliability prior remains explicit, host-matched, capability-scoped, removable, and contradiction-first",
        ),
        metadata=(MetadataField("source", "aux/support-priors"),) + appendix.metadata,
        host_reliability_prior=reliability_prior,
    )


__all__ = [
    "build_support_memory_prior_appendix",
    "filter_live_support_memory_prior_appendix",
]
```

### `cortex/aux/augmentation.py`

```python
"""Explicit AUX-side support snapshot augmentation."""

from __future__ import annotations

from dataclasses import dataclass, field

from cortex.core.envelopes import MetadataField
from cortex.core.support import SupportReference, SupportSnapshot
from cortex.sre.memory_priors import HostReliabilityPrior


@dataclass(frozen=True, slots=True)
class AuxiliarySupportAppendix:
    derived_support_refs: tuple[SupportReference, ...] = field(default_factory=tuple)
    derived_tags: frozenset[str] = field(default_factory=frozenset)
    notes: tuple[str, ...] = field(default_factory=tuple)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)
    published_host_reliability_prior: HostReliabilityPrior | None = None

    def __post_init__(self) -> None:
        if any(
            not isinstance(reference, SupportReference)
            for reference in self.derived_support_refs
        ):
            raise TypeError(
                "AuxiliarySupportAppendix.derived_support_refs must contain only SupportReference instances.",
            )
        if any(not (isinstance(tag, str) and tag.strip()) for tag in self.derived_tags):
            raise ValueError(
                "AuxiliarySupportAppendix.derived_tags must contain only non-empty values after trimming.",
            )
        if any(not (isinstance(note, str) and note.strip()) for note in self.notes):
            raise ValueError(
                "AuxiliarySupportAppendix.notes must contain only non-empty values after trimming.",
            )
        if any(not isinstance(field, MetadataField) for field in self.metadata):
            raise TypeError(
                "AuxiliarySupportAppendix.metadata must contain only MetadataField instances.",
            )
        if self.published_host_reliability_prior is not None and not isinstance(
            self.published_host_reliability_prior,
            HostReliabilityPrior,
        ):
            actual_type = type(self.published_host_reliability_prior).__name__
            raise TypeError(
                "AuxiliarySupportAppendix.published_host_reliability_prior must be "
                f"HostReliabilityPrior | None, got {actual_type}.",
            )


@dataclass(frozen=True, slots=True)
class AugmentedSupportSnapshot:
    core_snapshot: SupportSnapshot
    auxiliary_support: AuxiliarySupportAppendix

    def __post_init__(self) -> None:
        if not isinstance(self.core_snapshot, SupportSnapshot):
            actual_type = type(self.core_snapshot).__name__
            raise TypeError(
                "AugmentedSupportSnapshot.core_snapshot must be SupportSnapshot, "
                f"got {actual_type}.",
            )
        if not isinstance(self.auxiliary_support, AuxiliarySupportAppendix):
            actual_type = type(self.auxiliary_support).__name__
            raise TypeError(
                "AugmentedSupportSnapshot.auxiliary_support must be AuxiliarySupportAppendix, "
                f"got {actual_type}.",
            )


def augment_snapshot(
    snapshot: SupportSnapshot,
    auxiliary_support: AuxiliarySupportAppendix,
) -> AugmentedSupportSnapshot:
    if not isinstance(snapshot, SupportSnapshot):
        actual_type = type(snapshot).__name__
        raise TypeError(
            "augment_snapshot() requires SupportSnapshot, "
            f"got {actual_type}.",
        )
    if not isinstance(auxiliary_support, AuxiliarySupportAppendix):
        actual_type = type(auxiliary_support).__name__
        raise TypeError(
            "augment_snapshot() requires AuxiliarySupportAppendix, "
            f"got {actual_type}.",
        )
    return AugmentedSupportSnapshot(
        core_snapshot=snapshot,
        auxiliary_support=auxiliary_support,
    )


__all__ = [
    "AugmentedSupportSnapshot",
    "AuxiliarySupportAppendix",
    "augment_snapshot",
]
```

### `cortex/runtime/operator_brain_capability.py`

```python
"""Shared operator-brain capability registry for bounded capability adaptation.

The SRE-side capability mechanism (`OperatorBrainCapabilityEnvelope`,
`assess_operator_brain_capability`, threshold ladder, routing consequences)
is host-agnostic: per-host band registries may differ but the assessment
math and the routing consequences must be identical across hosts (see
SRE_2 §6.9.4 — forbidden moves).

Currently only OpenAI has a populated band registry below; Claude, Gemini,
and reference hosts return the standard envelope by default until per-host
registries earn their own seam. This is intentional, not an oversight: the
brain-capability-aware-routing seam earned the SRE-side mechanism on the
OpenAI lane first, and the per-host registries are queued as a follow-up
under the same bio_to_code skill (Intervention pricing versus neutrality).

The dynamic-detection follow-up seam
(`brain-capability-observation-and-inference`, see
`internal/truth/cortex_status.json::next_product_train`) will replace the
static name-based lookup with an observed-performance accumulator whose
inference function produces the same `OperatorBrainCapabilityEnvelope`
shape; the SRE-side assessment math and routing consequences are reusable
unchanged when inference replaces lookup.
"""

from __future__ import annotations

from typing import Literal

from cortex.sre.operator_routing import OperatorBrainCapabilityEnvelope


OperatorBrainCapabilityBand = Literal["frontier", "standard", "bounded"]

_BRAIN_CAPABILITY_REGISTRY: dict[
    OperatorBrainCapabilityBand, OperatorBrainCapabilityEnvelope
] = {
    "frontier": OperatorBrainCapabilityEnvelope(
        continuity_tolerance=0.90,
        verification_tolerance=0.90,
        output_contract_tolerance=0.90,
    ),
    "standard": OperatorBrainCapabilityEnvelope(
        continuity_tolerance=0.75,
        verification_tolerance=0.75,
        output_contract_tolerance=0.65,
    ),
    "bounded": OperatorBrainCapabilityEnvelope(
        continuity_tolerance=0.45,
        verification_tolerance=0.50,
        output_contract_tolerance=0.20,
    ),
}

_OPENAI_OPERATOR_BAND_BY_MODEL = {
    "gpt-5.4": "frontier",
    "gpt-5.3-codex": "standard",
    "gpt-5.3-codex-spark": "bounded",
}


def operator_brain_capability_for_band(
    band: OperatorBrainCapabilityBand,
) -> OperatorBrainCapabilityEnvelope:
    if band not in _BRAIN_CAPABILITY_REGISTRY:
        raise ValueError(f"unsupported operator brain capability band: {band}")
    return _BRAIN_CAPABILITY_REGISTRY[band]


def operator_brain_capability_band_for_openai_model(
    model: str | None,
) -> OperatorBrainCapabilityBand:
    if not isinstance(model, str) or not model.strip():
        return "standard"
    return _OPENAI_OPERATOR_BAND_BY_MODEL.get(model.strip(), "standard")


def operator_brain_capability_for_openai_model(
    model: str | None,
) -> tuple[OperatorBrainCapabilityBand, OperatorBrainCapabilityEnvelope]:
    band = operator_brain_capability_band_for_openai_model(model)
    return band, operator_brain_capability_for_band(band)


def brain_capability_band_for_envelope(
    envelope: OperatorBrainCapabilityEnvelope,
) -> OperatorBrainCapabilityBand:
    if not isinstance(envelope, OperatorBrainCapabilityEnvelope):
        actual_type = type(envelope).__name__
        raise TypeError(
            "brain_capability_band_for_envelope.envelope must be "
            f"OperatorBrainCapabilityEnvelope, got {actual_type}."
        )
    for band, candidate in _BRAIN_CAPABILITY_REGISTRY.items():
        if envelope == candidate:
            return band
    return "standard"


__all__ = [
    "OperatorBrainCapabilityBand",
    "brain_capability_band_for_envelope",
    "operator_brain_capability_band_for_openai_model",
    "operator_brain_capability_for_band",
    "operator_brain_capability_for_openai_model",
]
```

### `cortex/runtime/verified_work_runtime.py`

```python
"""Shared verified-work runtime helpers over the landed verified-work law."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from cortex.sre.preservation import PreservationState
from cortex.sre.verified_work import VerificationOutcome, WorkContract


REPO_ROOT = Path(__file__).resolve().parents[2]
BLOCKED_REASON_MAP = {
    "needs_user_input": "blocked_missing_info",
    "unsafe_request": "blocked_unsafe",
}
_PYTHON_BIN = shutil.which("python3") or sys.executable
_VENV_DIR_NAME = ".verified-work-venv"
_FILE_HEADER_RE = re.compile(r"^=== FILE: (?P<path>.+?) ===$")
_BLOCKED_HEADER_RE = re.compile(
    r"^=== BLOCKED: (?P<reason>needs_user_input|unsafe_request) ===$"
)
_END_FILE_MARKER = "=== END FILE ==="
_END_BLOCKED_MARKER = "=== END BLOCKED ==="
_PASSED_RE = re.compile(r"(?P<count>\d+)\s+passed")
_FAILED_RE = re.compile(r"(?P<count>\d+)\s+failed")
_FAILING_TEST_RE = re.compile(r"^(?:FAILED|ERROR) (?P<name>tests/[^\s]+)", re.MULTILINE)

VerifiedWorkContextMode = Literal[
    "default",
    "off",
    "writable_files_only",
    "writable_files_plus_visible_tests",
]
VerifiedWorkRepairTicketStyle = Literal["factual", "minimal"]
VerifiedWorkContractBindingProfile = Literal["standard", "lean"]


@dataclass(frozen=True, slots=True)
class VerifiedWorkProfileSpec:
    template_root: Path
    read_only_context_paths: tuple[str, ...]
    import_target: str | None
    pytest_command: tuple[str, ...]


_VERIFIED_WORK_PROFILE_REGISTRY = {
    "python_workspace_pytest_v1": VerifiedWorkProfileSpec(
        template_root=(
            REPO_ROOT
            / "tests"
            / "lab"
            / "fixtures"
            / "live_validation"
            / "bookmarks_app_template"
        ),
        read_only_context_paths=("tests/test_bookmarks_api.py",),
        import_target="bookmarks_api.main",
        pytest_command=("-m", "pytest", "-q", "tests/test_bookmarks_api.py"),
    ),
    "python_workspace_pytest_port_fix_v1": VerifiedWorkProfileSpec(
        template_root=(
            REPO_ROOT
            / "tests"
            / "lab"
            / "fixtures"
            / "live_validation"
            / "project_template"
        ),
        read_only_context_paths=("tests/test_normalize_port.py",),
        import_target="normalize_port",
        pytest_command=("-m", "pytest", "-q", "tests/test_normalize_port.py"),
    ),
    "python_workspace_pytest_feature_flags_v1": VerifiedWorkProfileSpec(
        template_root=(
            REPO_ROOT
            / "tests"
            / "lab"
            / "fixtures"
            / "live_validation"
            / "feature_flags_template"
        ),
        read_only_context_paths=("tests/test_feature_flags.py",),
        import_target="feature_flags.evaluator",
        pytest_command=("-m", "pytest", "-q", "tests/test_feature_flags.py"),
    ),
}


def build_verified_work_instructions(
    work_contract: WorkContract,
    *,
    contract_binding_profile: VerifiedWorkContractBindingProfile = "standard",
) -> str:
    if contract_binding_profile not in {"standard", "lean"}:
        raise ValueError(
            "build_verified_work_instructions.contract_binding_profile must be accepted."
        )
    allowed_paths = "\n".join(f"- {path}" for path in work_contract.allowed_write_paths)
    if contract_binding_profile == "lean":
        return (
            "Return only protocol blocks for the allowed paths.\n"
            "Allowed paths:\n"
            f"{allowed_paths}\n\n"
            "Use exactly one of:\n"
            "=== FILE: relative/path ===\n"
            "<full file contents>\n"
            "=== END FILE ===\n\n"
            "=== BLOCKED: needs_user_input ===\n"
            "<message>\n"
            "=== END BLOCKED ===\n\n"
            "=== BLOCKED: unsafe_request ===\n"
            "<message>\n"
            "=== END BLOCKED ===\n\n"
            "No prose. No code fences. Do not run tests."
        )
    return (
        "Return only full-file blocks for the allowed paths.\n"
        "Allowed paths:\n"
        f"{allowed_paths}\n\n"
        "For each file, use:\n"
        "=== FILE: relative/path ===\n"
        "<full file contents>\n"
        "=== END FILE ===\n\n"
        "If blocked because you need missing user information, use:\n"
        "=== BLOCKED: needs_user_input ===\n"
        "<message>\n"
        "=== END BLOCKED ===\n\n"
        "If blocked because the request is unsafe, use:\n"
        "=== BLOCKED: unsafe_request ===\n"
        "<message>\n"
        "=== END BLOCKED ===\n\n"
        "Do not return prose, explanations, or code fences. Do not run tests."
    )


def build_verified_work_input_text(
    task_prompt: str,
    work_contract: WorkContract,
    *,
    context_mode: VerifiedWorkContextMode = "default",
    contract_binding_profile: VerifiedWorkContractBindingProfile = "standard",
) -> str:
    if not (isinstance(task_prompt, str) and task_prompt.strip()):
        raise ValueError(
            "build_verified_work_input_text.task_prompt must be non-empty after trimming."
        )
    if context_mode not in {
        "default",
        "off",
        "writable_files_only",
        "writable_files_plus_visible_tests",
    }:
        raise ValueError("build_verified_work_input_text.context_mode must be accepted.")
    if contract_binding_profile not in {"standard", "lean"}:
        raise ValueError(
            "build_verified_work_input_text.contract_binding_profile must be accepted."
        )
    if context_mode == "off":
        return task_prompt.strip()
    context_intro = (
        "Read-only workspace context follows. Use the existing writable-file contents and tests below as the task contract.\n"
        "Modify only the allowed paths named in the work contract.\n\n"
    )
    if contract_binding_profile == "lean":
        context_intro = (
            "Workspace context follows. Edit only allowed paths.\n\n"
        )
    return (
        f"{task_prompt.strip()}\n\n"
        f"{context_intro}"
        f"{_build_verified_work_context_bundle(work_contract, context_mode=context_mode)}"
    )


def build_verified_work_repair_ticket(
    preservation_state: PreservationState,
    *,
    style: VerifiedWorkRepairTicketStyle = "factual",
    contract_binding_profile: VerifiedWorkContractBindingProfile = "standard",
) -> str:
    if contract_binding_profile not in {"standard", "lean"}:
        raise ValueError(
            "build_verified_work_repair_ticket.contract_binding_profile must be accepted."
        )
    if contract_binding_profile == "lean":
        style = "minimal"
    if style not in {"factual", "minimal"}:
        raise ValueError("build_verified_work_repair_ticket.style must be accepted.")
    if not isinstance(preservation_state, PreservationState):
        actual_type = type(preservation_state).__name__
        raise TypeError(
            "build_verified_work_repair_ticket.preservation_state must be PreservationState, "
            f"got {actual_type}."
        )
    trusted_checks = ", ".join(sorted(preservation_state.trusted_structure.checks)) or "<none>"
    trusted_paths = ", ".join(sorted(preservation_state.trusted_structure.paths)) or "<none>"
    falsified_checks = ", ".join(
        sorted(preservation_state.falsified_structure.checks)
    ) or "<none>"
    failing_tests = ", ".join(
        sorted(preservation_state.falsified_structure.failing_tests)
    ) or "<none>"
    repair_surface = ", ".join(
        sorted(preservation_state.lawful_repair_surface)
    ) or "<none>"
    allowed_moves = ", ".join(sorted(preservation_state.intervention_budget.allowed_moves))
    if style == "minimal":
        return (
            f"task_anchor: {preservation_state.task_anchor}\n"
            f"failure_class: {preservation_state.falsified_structure.failure_class or '<none>'}\n"
            f"falsified_checks: {falsified_checks}\n"
            f"lawful_repair_surface: {repair_surface}\n"
            f"remaining_repairs: {preservation_state.intervention_budget.remaining_repairs}\n"
            f"allowed_moves: {allowed_moves}"
        )
    return (
        f"task_anchor: {preservation_state.task_anchor}\n"
        f"trusted_checks: {trusted_checks}\n"
        f"trusted_paths: {trusted_paths}\n"
        f"failure_class: {preservation_state.falsified_structure.failure_class or '<none>'}\n"
        f"falsified_checks: {falsified_checks}\n"
        f"failing_tests: {failing_tests}\n"
        f"lawful_repair_surface: {repair_surface}\n"
        f"remaining_repairs: {preservation_state.intervention_budget.remaining_repairs}\n"
        f"allowed_moves: {allowed_moves}"
    )


def verify_verified_work_result(
    result_text: str | None,
    work_contract: WorkContract,
    *,
    preserved_file_map: dict[str, str] | None = None,
    verifier_contract: WorkContract | None = None,
) -> tuple[dict[str, str] | None, VerificationOutcome]:
    file_map, blocked_outcome = _parse_verified_work_result(result_text, work_contract)
    if blocked_outcome is not None:
        return file_map, blocked_outcome
    assert file_map is not None
    effective_file_map = _overlay_verified_work_file_map(
        preserved_file_map,
        file_map,
    )
    return effective_file_map, _run_verified_work_verifier(
        effective_file_map,
        verifier_contract or work_contract,
    )


def _overlay_verified_work_file_map(
    preserved_file_map: dict[str, str] | None,
    repair_file_map: dict[str, str],
) -> dict[str, str]:
    if preserved_file_map is None:
        return dict(repair_file_map)
    combined = dict(preserved_file_map)
    combined.update(repair_file_map)
    return combined


def _build_verified_work_context_bundle(
    work_contract: WorkContract,
    *,
    context_mode: VerifiedWorkContextMode = "default",
) -> str:
    profile = _verified_work_profile_spec(work_contract)
    if context_mode == "writable_files_only":
        context_paths = tuple(work_contract.allowed_write_paths)
    else:
        context_paths = tuple(work_contract.allowed_write_paths) + profile.read_only_context_paths
    rendered_blocks: list[str] = []
    for relative_path in context_paths:
        source_path = profile.template_root / relative_path
        if not source_path.is_file():
            raise RuntimeError(
                "verified-work context file is missing from the selected template: "
                f"{relative_path}"
            )
        file_text = source_path.read_text(encoding="utf-8").rstrip()
        rendered_blocks.append(
            "\n".join(
                (
                    f"=== CONTEXT FILE: {relative_path} ===",
                    file_text,
                    "=== END CONTEXT FILE ===",
                )
            )
        )
    return "\n\n".join(rendered_blocks)


def _parse_verified_work_result(
    result_text: str | None,
    work_contract: WorkContract,
) -> tuple[dict[str, str] | None, VerificationOutcome | None]:
    if result_text is None or not result_text.strip():
        return None, VerificationOutcome(
            status="failed",
            failure_class="output_invalid",
            parse_error="result_text was empty.",
        )
    lines = result_text.strip().splitlines()
    file_map: dict[str, str] = {}
    blocked_reason: str | None = None
    blocked_message: str | None = None
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        file_match = _FILE_HEADER_RE.match(line)
        blocked_match = _BLOCKED_HEADER_RE.match(line)
        if file_match is not None:
            if blocked_reason is not None:
                return None, VerificationOutcome(
                    status="failed",
                    failure_class="output_invalid",
                    parse_error="blocked markers may not be mixed with file blocks.",
                )
            path = file_match.group("path").strip()
            if path not in work_contract.allowed_write_paths:
                return None, VerificationOutcome(
                    status="failed",
                    failure_class="output_invalid",
                    parse_error=f"unapproved write path: {path}",
                )
            if path in file_map:
                return None, VerificationOutcome(
                    status="failed",
                    failure_class="output_invalid",
                    parse_error=f"duplicate file block for {path}",
                )
            index += 1
            content_lines: list[str] = []
            while index < len(lines) and lines[index] != _END_FILE_MARKER:
                content_lines.append(lines[index])
                index += 1
            if index >= len(lines):
                return None, VerificationOutcome(
                    status="failed",
                    failure_class="output_invalid",
                    parse_error=f"missing end marker for {path}",
                )
            file_map[path] = "\n".join(content_lines)
            index += 1
            continue
        if blocked_match is not None:
            if file_map:
                return None, VerificationOutcome(
                    status="failed",
                    failure_class="output_invalid",
                    parse_error="file blocks may not be mixed with blocked markers.",
                )
            if blocked_reason is not None:
                return None, VerificationOutcome(
                    status="failed",
                    failure_class="output_invalid",
                    parse_error="only one blocked marker is allowed.",
                )
            blocked_reason = BLOCKED_REASON_MAP[blocked_match.group("reason")]
            index += 1
            message_lines: list[str] = []
            while index < len(lines) and lines[index] != _END_BLOCKED_MARKER:
                message_lines.append(lines[index])
                index += 1
            if index >= len(lines):
                return None, VerificationOutcome(
                    status="failed",
                    failure_class="output_invalid",
                    parse_error="missing blocked end marker.",
                )
            blocked_message = "\n".join(message_lines).strip()
            if not blocked_message:
                return None, VerificationOutcome(
                    status="failed",
                    failure_class="output_invalid",
                    parse_error="blocked marker requires a message.",
                )
            index += 1
            continue
        return None, VerificationOutcome(
            status="failed",
            failure_class="output_invalid",
            parse_error=f"unexpected text outside protocol blocks: {line}",
        )
    if blocked_reason is not None:
        return None, VerificationOutcome(
            status="blocked",
            failure_class=blocked_reason,
            blocked_message=blocked_message,
        )
    if not file_map:
        return None, VerificationOutcome(
            status="failed",
            failure_class="output_invalid",
            parse_error="no file blocks were produced.",
        )
    return file_map, None


def _run_verified_work_verifier(
    file_map: dict[str, str],
    work_contract: WorkContract,
) -> VerificationOutcome:
    profile = _verified_work_profile_spec(work_contract)
    with tempfile.TemporaryDirectory(prefix="cortex-openai-verified-work-") as tmpdir:
        project_root = Path(tmpdir) / "workspace"
        shutil.copytree(profile.template_root, project_root)
        for relative_path, content in file_map.items():
            destination = project_root / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content, encoding="utf-8")

        parsed_paths = tuple(file_map)
        python_bin = _prepare_verified_work_python(project_root)
        if profile.import_target is not None:
            import_command = [
                str(python_bin),
                "-c",
                (
                    "import importlib; "
                    f"importlib.import_module('{profile.import_target}')"
                ),
            ]
            import_result = _run_command(import_command, cwd=project_root)
            if import_result.returncode != 0:
                return VerificationOutcome(
                    status="failed",
                    failure_class="import_smoke_failed",
                    parsed_paths=parsed_paths,
                    import_smoke_ok=False,
                    import_smoke_excerpt=_first_relevant_excerpt(_command_output(import_result)),
                    first_failure_excerpt=_first_relevant_excerpt(_command_output(import_result)),
                )

        pytest_result = _run_command(
            [str(python_bin), *profile.pytest_command],
            cwd=project_root,
        )
        pytest_output = _command_output(pytest_result)
        passed_count = _extract_pytest_count(_PASSED_RE, pytest_output)
        failed_count = _extract_pytest_count(_FAILED_RE, pytest_output)
        failing_tests = tuple(dict.fromkeys(_FAILING_TEST_RE.findall(pytest_output)))
        if pytest_result.returncode != 0:
            return VerificationOutcome(
                status="failed",
                failure_class="test_failed",
                parsed_paths=parsed_paths,
                import_smoke_ok=True,
                pytest_ok=False,
                pytest_exit_code=pytest_result.returncode,
                pytest_passed=passed_count,
                pytest_failed=failed_count,
                failing_tests=failing_tests,
                first_failure_excerpt=_first_relevant_excerpt(pytest_output),
            )
        return VerificationOutcome(
            status="passed",
            failure_class=None,
            parsed_paths=parsed_paths,
            import_smoke_ok=True,
            pytest_ok=True,
            pytest_exit_code=pytest_result.returncode,
            pytest_passed=passed_count,
            pytest_failed=failed_count,
        )


def _run_command(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    pythonpath_parts = [str(cwd / "src")]
    existing_pythonpath = env.get("PYTHONPATH")
    if existing_pythonpath:
        pythonpath_parts.append(existing_pythonpath)
    env["PYTHONPATH"] = os.pathsep.join(pythonpath_parts)
    return subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=120,
        env=env,
    )


def _prepare_verified_work_python(project_root: Path) -> Path:
    venv_root = project_root / _VENV_DIR_NAME
    python_bin = _venv_python_path(venv_root)
    if python_bin.exists():
        return python_bin
    venv_result = subprocess.run(
        [_PYTHON_BIN, "-m", "venv", str(venv_root)],
        cwd=project_root,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if venv_result.returncode != 0:
        raise RuntimeError(
            "failed to create verified-work venv: "
            f"{_command_output(venv_result) or '<no output>'}"
        )
    install_result = subprocess.run(
        [
            str(python_bin),
            "-m",
            "pip",
            "install",
            "--quiet",
            "-e",
            ".[test]",
            "pytest",
        ],
        cwd=project_root,
        capture_output=True,
        text=True,
        timeout=300,
        env={
            **os.environ,
            "PIP_DISABLE_PIP_VERSION_CHECK": "1",
        },
    )
    if install_result.returncode != 0:
        raise RuntimeError(
            "failed to install verified-work dependencies: "
            f"{_command_output(install_result) or '<no output>'}"
        )
    return python_bin


def _venv_python_path(venv_root: Path) -> Path:
    if os.name == "nt":
        return venv_root / "Scripts" / "python.exe"
    return venv_root / "bin" / "python"


def _extract_pytest_count(pattern: re.Pattern[str], output: str) -> int | None:
    match = pattern.search(output)
    if match is None:
        return 0 if "no tests ran" in output else None
    return int(match.group("count"))


def _command_output(result: subprocess.CompletedProcess[str]) -> str:
    return "\n".join(part for part in (result.stdout, result.stderr) if part).strip()


def _first_relevant_excerpt(output: str) -> str | None:
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("E   ") or line.startswith("FAILED ") or line.startswith("ERROR "):
            return line
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if line:
            return line
    return None


def _verified_work_profile_spec(work_contract: WorkContract) -> VerifiedWorkProfileSpec:
    try:
        return _VERIFIED_WORK_PROFILE_REGISTRY[work_contract.verification_profile]
    except KeyError as exc:  # pragma: no cover - WorkContract validation owns legality.
        raise RuntimeError(
            "verified-work profile registry is missing the active profile: "
            f"{work_contract.verification_profile}"
        ) from exc


__all__ = [
    "BLOCKED_REASON_MAP",
    "build_verified_work_input_text",
    "build_verified_work_instructions",
    "build_verified_work_repair_ticket",
    "verify_verified_work_result",
]
```
