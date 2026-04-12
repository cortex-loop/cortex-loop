"""Shared support-state builders for AUX experimental tests."""

from __future__ import annotations

from cortex.core.envelopes import EventPayloadHandle, LifecycleEventEnvelope, MetadataField
from cortex.core.errors import ContradictionRecord, DegradationRecord
from cortex.core.support import (
    SupportCounter,
    SupportExecMemoryState,
    SupportHostState,
    SupportReference,
    SupportSessionState,
    SupportSnapshot,
    SupportTraceState,
    WakeReceipt,
)


def make_support_snapshot() -> SupportSnapshot:
    trace = SupportTraceState(
        recent_events=(
            LifecycleEventEnvelope(
                native_event_name="turn/complete",
                payload_handle=EventPayloadHandle(
                    payload_kind="host-payload",
                    metadata=(MetadataField("source", "aux-test"),),
                ),
                facet_tags=frozenset({"approval/request"}),
            ),
        ),
        candidate_refs=("candidate-1",),
        wake_receipts=(WakeReceipt(reason_tag="resume-needed", event_name="turn/complete"),),
        degradation_records=(
            DegradationRecord(
                reason_code="host-degraded",
                contradiction_records=(
                    ContradictionRecord(
                        source_tag="host/runtime",
                        summary="host contradicted prior capability view",
                        evidence_tags=frozenset({"capability-drift"}),
                    ),
                ),
            ),
        ),
    )
    session = SupportSessionState(
        branch_registry=("main", "review-track"),
        pending_goal_refs=("goal-1",),
        role_view_tags=frozenset({"review", "aux/removable"}),
        budget_history=("medium",),
        brake_history=("guarded",),
        wake_counters=(SupportCounter("wake-receipts", 1),),
        reminders=("resume review-track before closing",),
    )
    host = SupportHostState(
        affordance_tags=frozenset({"tool/intercept"}),
        approval_boundary_tags=frozenset({"approval/request"}),
        metadata=(MetadataField("surface", "operator_cli"),),
    )
    exec_memory = SupportExecMemoryState(
        published_memory_refs=(SupportReference("memory", "memo-1"),),
        artifact_refs=(SupportReference("artifact", "artifact-1"),),
    )
    return SupportSnapshot(
        trace=trace,
        session=session,
        host=host,
        exec_memory_pub=exec_memory,
    )


def make_support_ref(reference_kind: str, reference_id: str) -> SupportReference:
    return SupportReference(reference_kind, reference_id)
