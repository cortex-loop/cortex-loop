"""Typed support-state carriers and read-only snapshots."""

from __future__ import annotations

from dataclasses import dataclass, field

from .envelopes import MetadataField, LifecycleEventEnvelope
from .errors import DegradationRecord
from .observation import StructuredObservation


@dataclass(frozen=True, slots=True)
class WakeReceipt:
    reason_tag: str
    event_name: str | None = None

    def __post_init__(self) -> None:
        if not (isinstance(self.reason_tag, str) and self.reason_tag.strip()):
            raise ValueError(
                "WakeReceipt.reason_tag must be non-empty after trimming.",
            )
        if self.event_name is not None and not (
            isinstance(self.event_name, str) and self.event_name.strip()
        ):
            raise ValueError(
                "WakeReceipt.event_name must be non-empty after trimming when provided.",
            )


@dataclass(frozen=True, slots=True)
class SupportCounter:
    counter_tag: str
    count: int

    def __post_init__(self) -> None:
        if not (isinstance(self.counter_tag, str) and self.counter_tag.strip()):
            raise ValueError(
                "SupportCounter.counter_tag must be non-empty after trimming.",
            )
        if isinstance(self.count, bool):
            raise TypeError("SupportCounter.count must be a non-negative integer, got bool.")
        if not isinstance(self.count, int):
            actual_type = type(self.count).__name__
            raise TypeError(
                f"SupportCounter.count must be a non-negative integer, got {actual_type}.",
            )
        if self.count < 0:
            raise ValueError("SupportCounter.count must be non-negative.")


@dataclass(frozen=True, slots=True)
class SupportReference:
    reference_kind: str
    reference_id: str
    tags: frozenset[str] = field(default_factory=frozenset)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not (isinstance(self.reference_kind, str) and self.reference_kind.strip()):
            raise ValueError(
                "SupportReference.reference_kind must be non-empty after trimming.",
            )
        if not (isinstance(self.reference_id, str) and self.reference_id.strip()):
            raise ValueError(
                "SupportReference.reference_id must be non-empty after trimming.",
            )
        if any(not (isinstance(tag, str) and tag.strip()) for tag in self.tags):
            raise ValueError(
                "SupportReference.tags must contain only non-empty values after trimming.",
            )


@dataclass(frozen=True, slots=True)
class SupportTraceState:
    recent_events: tuple[LifecycleEventEnvelope, ...] = field(default_factory=tuple)
    candidate_refs: tuple[str, ...] = field(default_factory=tuple)
    wake_receipts: tuple[WakeReceipt, ...] = field(default_factory=tuple)
    degradation_records: tuple[DegradationRecord, ...] = field(default_factory=tuple)
    observables: tuple[StructuredObservation, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if any(not isinstance(event, LifecycleEventEnvelope) for event in self.recent_events):
            raise TypeError(
                "SupportTraceState.recent_events must contain only LifecycleEventEnvelope instances.",
            )
        if any(
            not (isinstance(candidate_ref, str) and candidate_ref.strip())
            for candidate_ref in self.candidate_refs
        ):
            raise ValueError(
                "SupportTraceState.candidate_refs must contain only non-empty values after trimming.",
            )
        if any(not isinstance(receipt, WakeReceipt) for receipt in self.wake_receipts):
            raise TypeError(
                "SupportTraceState.wake_receipts must contain only WakeReceipt instances.",
            )
        if any(
            not isinstance(record, DegradationRecord)
            for record in self.degradation_records
        ):
            raise TypeError(
                "SupportTraceState.degradation_records must contain only DegradationRecord instances.",
            )
        if any(
            not isinstance(observable, StructuredObservation)
            for observable in self.observables
        ):
            raise TypeError(
                "SupportTraceState.observables must contain only StructuredObservation instances.",
            )


@dataclass(frozen=True, slots=True)
class SupportSessionState:
    branch_registry: tuple[str, ...] = field(default_factory=tuple)
    pending_goal_refs: tuple[str, ...] = field(default_factory=tuple)
    role_view_tags: frozenset[str] = field(default_factory=frozenset)
    budget_history: tuple[str, ...] = field(default_factory=tuple)
    brake_history: tuple[str, ...] = field(default_factory=tuple)
    wake_counters: tuple[SupportCounter, ...] = field(default_factory=tuple)
    reminders: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if any(
            not (isinstance(branch_ref, str) and branch_ref.strip())
            for branch_ref in self.branch_registry
        ):
            raise ValueError(
                "SupportSessionState.branch_registry must contain only non-empty values after trimming.",
            )
        if any(
            not (isinstance(goal_ref, str) and goal_ref.strip())
            for goal_ref in self.pending_goal_refs
        ):
            raise ValueError(
                "SupportSessionState.pending_goal_refs must contain only non-empty values after trimming.",
            )
        if any(
            not (isinstance(budget_entry, str) and budget_entry.strip())
            for budget_entry in self.budget_history
        ):
            raise ValueError(
                "SupportSessionState.budget_history must contain only non-empty values after trimming.",
            )
        if any(
            not (isinstance(brake_entry, str) and brake_entry.strip())
            for brake_entry in self.brake_history
        ):
            raise ValueError(
                "SupportSessionState.brake_history must contain only non-empty values after trimming.",
            )
        if any(
            not (isinstance(reminder, str) and reminder.strip())
            for reminder in self.reminders
        ):
            raise ValueError(
                "SupportSessionState.reminders must contain only non-empty values after trimming.",
            )
        if any(not isinstance(counter, SupportCounter) for counter in self.wake_counters):
            raise TypeError(
                "SupportSessionState.wake_counters must contain only SupportCounter instances.",
            )
        if any(
            not (isinstance(role_view_tag, str) and role_view_tag.strip())
            for role_view_tag in self.role_view_tags
        ):
            raise ValueError(
                "SupportSessionState.role_view_tags must contain only non-empty values after trimming.",
            )


@dataclass(frozen=True, slots=True)
class SupportHostState:
    affordance_tags: frozenset[str] = field(default_factory=frozenset)
    approval_boundary_tags: frozenset[str] = field(default_factory=frozenset)
    constraint_tags: frozenset[str] = field(default_factory=frozenset)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if any(not (isinstance(tag, str) and tag.strip()) for tag in self.affordance_tags):
            raise ValueError(
                "SupportHostState.affordance_tags must contain only non-empty values after trimming.",
            )
        if any(
            not (isinstance(tag, str) and tag.strip())
            for tag in self.approval_boundary_tags
        ):
            raise ValueError(
                "SupportHostState.approval_boundary_tags must contain only non-empty values after trimming.",
            )
        if any(not (isinstance(tag, str) and tag.strip()) for tag in self.constraint_tags):
            raise ValueError(
                "SupportHostState.constraint_tags must contain only non-empty values after trimming.",
            )


@dataclass(frozen=True, slots=True)
class SupportExecMemoryState:
    published_memory_refs: tuple[SupportReference, ...] = field(default_factory=tuple)
    artifact_refs: tuple[SupportReference, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if any(
            not isinstance(reference, SupportReference)
            for reference in self.published_memory_refs
        ):
            raise TypeError(
                "SupportExecMemoryState.published_memory_refs must contain only SupportReference instances.",
            )
        if any(not isinstance(reference, SupportReference) for reference in self.artifact_refs):
            raise TypeError(
                "SupportExecMemoryState.artifact_refs must contain only SupportReference instances.",
            )


@dataclass(frozen=True, slots=True)
class SupportState:
    trace: SupportTraceState = field(default_factory=SupportTraceState)
    session: SupportSessionState = field(default_factory=SupportSessionState)
    host: SupportHostState = field(default_factory=SupportHostState)
    exec_memory_pub: SupportExecMemoryState = field(default_factory=SupportExecMemoryState)

    def __post_init__(self) -> None:
        if not isinstance(self.trace, SupportTraceState):
            actual_type = type(self.trace).__name__
            raise TypeError(
                "SupportState.trace must be SupportTraceState, "
                f"got {actual_type}.",
            )
        if not isinstance(self.session, SupportSessionState):
            actual_type = type(self.session).__name__
            raise TypeError(
                "SupportState.session must be SupportSessionState, "
                f"got {actual_type}.",
            )
        if not isinstance(self.host, SupportHostState):
            actual_type = type(self.host).__name__
            raise TypeError(
                "SupportState.host must be SupportHostState, "
                f"got {actual_type}.",
            )
        if not isinstance(self.exec_memory_pub, SupportExecMemoryState):
            actual_type = type(self.exec_memory_pub).__name__
            raise TypeError(
                "SupportState.exec_memory_pub must be SupportExecMemoryState, "
                f"got {actual_type}.",
            )


@dataclass(frozen=True, slots=True)
class SupportSnapshot:
    trace: SupportTraceState
    session: SupportSessionState
    host: SupportHostState
    exec_memory_pub: SupportExecMemoryState

    def __post_init__(self) -> None:
        if not isinstance(self.trace, SupportTraceState):
            actual_type = type(self.trace).__name__
            raise TypeError(
                "SupportSnapshot.trace must be SupportTraceState, "
                f"got {actual_type}.",
            )
        if not isinstance(self.session, SupportSessionState):
            actual_type = type(self.session).__name__
            raise TypeError(
                "SupportSnapshot.session must be SupportSessionState, "
                f"got {actual_type}.",
            )
        if not isinstance(self.host, SupportHostState):
            actual_type = type(self.host).__name__
            raise TypeError(
                "SupportSnapshot.host must be SupportHostState, "
                f"got {actual_type}.",
            )
        if not isinstance(self.exec_memory_pub, SupportExecMemoryState):
            actual_type = type(self.exec_memory_pub).__name__
            raise TypeError(
                "SupportSnapshot.exec_memory_pub must be SupportExecMemoryState, "
                f"got {actual_type}.",
            )


__all__ = [
    "SupportCounter",
    "SupportExecMemoryState",
    "SupportHostState",
    "SupportReference",
    "SupportSessionState",
    "SupportSnapshot",
    "SupportState",
    "SupportTraceState",
    "WakeReceipt",
]
