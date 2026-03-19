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


@dataclass(frozen=True, slots=True)
class SupportTraceState:
    recent_events: tuple[LifecycleEventEnvelope, ...] = field(default_factory=tuple)
    candidate_refs: tuple[str, ...] = field(default_factory=tuple)
    wake_receipts: tuple[WakeReceipt, ...] = field(default_factory=tuple)
    degradation_records: tuple[DegradationRecord, ...] = field(default_factory=tuple)
    observables: tuple[StructuredObservation, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if any(
            not (isinstance(candidate_ref, str) and candidate_ref.strip())
            for candidate_ref in self.candidate_refs
        ):
            raise ValueError(
                "SupportTraceState.candidate_refs must contain only non-empty values after trimming.",
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


@dataclass(frozen=True, slots=True)
class SupportHostState:
    affordance_tags: frozenset[str] = field(default_factory=frozenset)
    approval_boundary_tags: frozenset[str] = field(default_factory=frozenset)
    constraint_tags: frozenset[str] = field(default_factory=frozenset)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class SupportExecMemoryState:
    published_memory_refs: tuple[SupportReference, ...] = field(default_factory=tuple)
    artifact_refs: tuple[SupportReference, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class SupportState:
    trace: SupportTraceState = field(default_factory=SupportTraceState)
    session: SupportSessionState = field(default_factory=SupportSessionState)
    host: SupportHostState = field(default_factory=SupportHostState)
    exec_memory_pub: SupportExecMemoryState = field(default_factory=SupportExecMemoryState)


@dataclass(frozen=True, slots=True)
class SupportSnapshot:
    trace: SupportTraceState
    session: SupportSessionState
    host: SupportHostState
    exec_memory_pub: SupportExecMemoryState


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
