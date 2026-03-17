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


@dataclass(frozen=True, slots=True)
class SupportCounter:
    counter_tag: str
    count: int


@dataclass(frozen=True, slots=True)
class SupportReference:
    reference_kind: str
    reference_id: str
    tags: frozenset[str] = field(default_factory=frozenset)
    metadata: tuple[MetadataField, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class SupportTraceState:
    recent_events: tuple[LifecycleEventEnvelope, ...] = field(default_factory=tuple)
    candidate_refs: tuple[str, ...] = field(default_factory=tuple)
    wake_receipts: tuple[WakeReceipt, ...] = field(default_factory=tuple)
    degradation_records: tuple[DegradationRecord, ...] = field(default_factory=tuple)
    observables: tuple[StructuredObservation, ...] = field(default_factory=tuple)


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
