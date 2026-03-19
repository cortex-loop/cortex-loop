"""Unit tests for the minimal typed core substrate."""

import pytest

from cortex.core.commitments import (
    BoundaryAssessment,
    CertificationContext,
    CommitmentCandidate,
    CommitmentStatus,
    CommitmentVerdict,
    ProvenanceEvidenceRef,
    ProvenanceManifest,
)
from cortex.core.environment import (
    CANONICAL_QUERY_KINDS,
    CAPABILITY_VIEW,
    EXECUTION_TRACE,
    STATE_SNAPSHOT,
    CommitmentEnvironmentHandle,
    EnvironmentQuery,
    ExecutiveEnvironmentView,
)
from cortex.core.envelopes import EventPayloadHandle, LifecycleEventEnvelope, MetadataField
from cortex.core.errors import ContradictionRecord, CoreErrorRecord, DegradationRecord
from cortex.core.lifecycle import LifecycleEffectBinding, LifecycleSurface
from cortex.core.observation import ObservationBundle, PayloadView, RuntimeRecord, StructuredObservation
from cortex.core.support import (
    SupportCounter,
    SupportExecMemoryState,
    SupportHostState,
    SupportReference,
    SupportSessionState,
    SupportSnapshot,
    SupportState,
    SupportTraceState,
    WakeReceipt,
)


def test_lifecycle_event_and_observation_carriers_construct_cleanly() -> None:
    payload_handle = EventPayloadHandle(
        payload_kind="host-payload",
        payload_ref="evt-1",
        metadata=(MetadataField("payload_kind", "tool-result"),),
    )
    envelope = LifecycleEventEnvelope(
        native_event_name="host.tool/post",
        facet_tags=frozenset({"tool/post"}),
        channel_tags=frozenset({"tool"}),
        extension_tags=frozenset({"host/custom"}),
        payload_metadata=(MetadataField("attempt", 1),),
        payload_handle=payload_handle,
    )
    observation = ObservationBundle(
        event=envelope,
        payload_view=PayloadView(
            payload_handle=payload_handle,
            metadata=(MetadataField("view", "current"),),
            summary_tags=frozenset({"read-only"}),
        ),
        runtime_records=(
            RuntimeRecord(
                record_type="tool-result",
                record_id="record-1",
                tags=frozenset({"already-produced"}),
            ),
        ),
        structured_observations=(
            StructuredObservation(
                observation_type="result-artifact",
                tags=frozenset({"attached"}),
            ),
        ),
    )
    surface = LifecycleSurface(
        runtime_name="reference-host",
        event_substrate=frozenset({"tool/post", "turn/complete"}),
        context_affordances=frozenset({"session/context"}),
        tool_affordances=frozenset({"tool/intercept"}),
        turn_affordances=frozenset({"turn/complete"}),
        orchestration_affordances=frozenset({"branch/open"}),
        mcp_affordances=frozenset({"mcp/query"}),
        effect_map=(
            LifecycleEffectBinding(
                action_tag="bounded_prose",
                consequence_tags=frozenset({"visible-output"}),
            ),
        ),
    )

    assert observation.event is envelope
    assert "host/custom" in envelope.extension_tags
    assert observation.runtime_records[0].record_type == "tool-result"
    assert surface.effect_map[0].action_tag == "bounded_prose"

    with pytest.raises(
        TypeError,
        match="payload_handle must be EventPayloadHandle when provided, got str",
    ):
        PayloadView(payload_handle="not-a-handle")

    with pytest.raises(
        TypeError,
        match="event must be LifecycleEventEnvelope, got str",
    ):
        ObservationBundle(event="not-an-envelope", payload_view=PayloadView())

    with pytest.raises(
        TypeError,
        match="payload_view must be PayloadView, got str",
    ):
        ObservationBundle(
            event=LifecycleEventEnvelope(native_event_name="turn/complete"),
            payload_view="not-a-payload-view",
        )

    with pytest.raises(
        TypeError,
        match="runtime_records must contain only RuntimeRecord instances",
    ):
        ObservationBundle(
            event=LifecycleEventEnvelope(native_event_name="turn/complete"),
            payload_view=PayloadView(),
            runtime_records=("not-a-runtime-record",),
        )

    with pytest.raises(
        TypeError,
        match="structured_observations must contain only StructuredObservation instances",
    ):
        ObservationBundle(
            event=LifecycleEventEnvelope(native_event_name="turn/complete"),
            payload_view=PayloadView(),
            structured_observations=("not-a-structured-observation",),
        )

    with pytest.raises(
        TypeError,
        match="metadata must contain only MetadataField instances",
    ):
        PayloadView(metadata=("not-field",))

    with pytest.raises(
        ValueError,
        match="summary_tags must contain only non-empty values after trimming",
    ):
        PayloadView(summary_tags=frozenset({""}))

    with pytest.raises(
        ValueError,
        match="summary_tags must contain only non-empty values after trimming",
    ):
        PayloadView(summary_tags=frozenset({"   "}))

    with pytest.raises(ValueError, match="record_type must be non-empty after trimming"):
        RuntimeRecord(record_type="")

    with pytest.raises(ValueError, match="record_type must be non-empty after trimming"):
        RuntimeRecord(record_type="   ")

    with pytest.raises(
        ValueError,
        match="record_id must be non-empty after trimming when provided",
    ):
        RuntimeRecord(record_type="tool-result", record_id="")

    with pytest.raises(
        ValueError,
        match="record_id must be non-empty after trimming when provided",
    ):
        RuntimeRecord(record_type="tool-result", record_id="   ")

    with pytest.raises(
        ValueError,
        match="tags must contain only non-empty values after trimming",
    ):
        RuntimeRecord(record_type="tool-result", tags=frozenset({""}))

    with pytest.raises(
        ValueError,
        match="tags must contain only non-empty values after trimming",
    ):
        RuntimeRecord(record_type="tool-result", tags=frozenset({"   "}))

    with pytest.raises(
        TypeError,
        match="metadata must contain only MetadataField instances",
    ):
        RuntimeRecord(record_type="tool-result", metadata=("not-field",))

    with pytest.raises(ValueError, match="observation_type must be non-empty after trimming"):
        StructuredObservation(observation_type="")

    with pytest.raises(ValueError, match="observation_type must be non-empty after trimming"):
        StructuredObservation(observation_type="   ")

    with pytest.raises(
        ValueError,
        match="tags must contain only non-empty values after trimming",
    ):
        StructuredObservation(observation_type="runtime-note", tags=frozenset({""}))

    with pytest.raises(
        ValueError,
        match="tags must contain only non-empty values after trimming",
    ):
        StructuredObservation(observation_type="runtime-note", tags=frozenset({"   "}))

    with pytest.raises(
        TypeError,
        match="metadata must contain only MetadataField instances",
    ):
        StructuredObservation(observation_type="runtime-note", metadata=("not-field",))

    with pytest.raises(ValueError, match="runtime_name must be non-empty after trimming"):
        LifecycleSurface(runtime_name="")

    with pytest.raises(ValueError, match="runtime_name must be non-empty after trimming"):
        LifecycleSurface(runtime_name="   ")

    with pytest.raises(
        ValueError,
        match="event_substrate must contain only non-empty values after trimming",
    ):
        LifecycleSurface(
            runtime_name="reference-host",
            event_substrate=frozenset({""}),
        )

    with pytest.raises(
        ValueError,
        match="event_substrate must contain only non-empty values after trimming",
    ):
        LifecycleSurface(
            runtime_name="reference-host",
            event_substrate=frozenset({"   "}),
        )

    with pytest.raises(
        ValueError,
        match="context_affordances must contain only non-empty values after trimming",
    ):
        LifecycleSurface(
            runtime_name="reference-host",
            context_affordances=frozenset({""}),
        )

    with pytest.raises(
        ValueError,
        match="context_affordances must contain only non-empty values after trimming",
    ):
        LifecycleSurface(
            runtime_name="reference-host",
            context_affordances=frozenset({"   "}),
        )

    with pytest.raises(
        ValueError,
        match="tool_affordances must contain only non-empty values after trimming",
    ):
        LifecycleSurface(
            runtime_name="reference-host",
            tool_affordances=frozenset({""}),
        )

    with pytest.raises(
        ValueError,
        match="tool_affordances must contain only non-empty values after trimming",
    ):
        LifecycleSurface(
            runtime_name="reference-host",
            tool_affordances=frozenset({"   "}),
        )

    with pytest.raises(
        ValueError,
        match="turn_affordances must contain only non-empty values after trimming",
    ):
        LifecycleSurface(
            runtime_name="reference-host",
            turn_affordances=frozenset({""}),
        )

    with pytest.raises(
        ValueError,
        match="turn_affordances must contain only non-empty values after trimming",
    ):
        LifecycleSurface(
            runtime_name="reference-host",
            turn_affordances=frozenset({"   "}),
        )

    with pytest.raises(
        ValueError,
        match="orchestration_affordances must contain only non-empty values after trimming",
    ):
        LifecycleSurface(
            runtime_name="reference-host",
            orchestration_affordances=frozenset({""}),
        )

    with pytest.raises(
        ValueError,
        match="orchestration_affordances must contain only non-empty values after trimming",
    ):
        LifecycleSurface(
            runtime_name="reference-host",
            orchestration_affordances=frozenset({"   "}),
        )

    with pytest.raises(
        ValueError,
        match="mcp_affordances must contain only non-empty values after trimming",
    ):
        LifecycleSurface(
            runtime_name="reference-host",
            mcp_affordances=frozenset({""}),
        )

    with pytest.raises(
        ValueError,
        match="mcp_affordances must contain only non-empty values after trimming",
    ):
        LifecycleSurface(
            runtime_name="reference-host",
            mcp_affordances=frozenset({"   "}),
        )

    with pytest.raises(ValueError, match="action_tag must be non-empty after trimming"):
        LifecycleEffectBinding(action_tag="")

    with pytest.raises(ValueError, match="action_tag must be non-empty after trimming"):
        LifecycleEffectBinding(action_tag="   ")

    with pytest.raises(
        ValueError,
        match="consequence_tags must contain only non-empty values after trimming",
    ):
        LifecycleEffectBinding(
            action_tag="bounded_prose",
            consequence_tags=frozenset({""}),
        )

    with pytest.raises(
        ValueError,
        match="consequence_tags must contain only non-empty values after trimming",
    ):
        LifecycleEffectBinding(
            action_tag="bounded_prose",
            consequence_tags=frozenset({"   "}),
        )

    with pytest.raises(
        TypeError,
        match="metadata must contain only MetadataField instances",
    ):
        LifecycleEffectBinding(
            action_tag="bounded_prose",
            metadata=("not-field",),
        )

    with pytest.raises(
        TypeError,
        match="effect_map must contain only LifecycleEffectBinding instances",
    ):
        LifecycleSurface(
            runtime_name="reference-host",
            effect_map=("not-a-binding",),
        )


def test_metadata_field_rejects_blank_keys_and_preserves_lawful_scalar_values() -> None:
    field = MetadataField("payload_kind", "tool-result")

    assert field.key == "payload_kind"
    assert field.value == "tool-result"

    with pytest.raises(ValueError, match="key must be non-empty after trimming"):
        MetadataField("", "tool-result")

    with pytest.raises(ValueError, match="key must be non-empty after trimming"):
        MetadataField("   ", "tool-result")


def test_event_payload_handle_rejects_blank_payload_kinds_and_refs() -> None:
    handle = EventPayloadHandle(
        payload_kind="host-payload",
        payload_ref="evt-1",
        metadata=(MetadataField("payload_kind", "tool-result"),),
    )

    assert handle.payload_kind == "host-payload"
    assert handle.payload_ref == "evt-1"

    with pytest.raises(ValueError, match="payload_kind must be non-empty after trimming"):
        EventPayloadHandle(payload_kind="", payload_ref="evt-1")

    with pytest.raises(ValueError, match="payload_kind must be non-empty after trimming"):
        EventPayloadHandle(payload_kind="   ", payload_ref="evt-1")

    with pytest.raises(
        ValueError,
        match="payload_ref must be non-empty after trimming when provided",
    ):
        EventPayloadHandle(payload_kind="host-payload", payload_ref="")

    with pytest.raises(
        ValueError,
        match="payload_ref must be non-empty after trimming when provided",
    ):
        EventPayloadHandle(payload_kind="host-payload", payload_ref="   ")

    with pytest.raises(
        TypeError,
        match="metadata must contain only MetadataField instances",
    ):
        EventPayloadHandle(
            payload_kind="host-payload",
            payload_ref="evt-1",
            metadata=("not-field",),
        )


def test_lifecycle_event_envelope_rejects_empty_or_whitespace_only_native_event_name() -> None:
    valid = LifecycleEventEnvelope(
        native_event_name="turn/complete",
        facet_tags=frozenset({"turn/complete"}),
        channel_tags=frozenset({"turn"}),
        extension_tags=frozenset({"host/custom"}),
    )

    assert valid.native_event_name == "turn/complete"
    assert valid.facet_tags == frozenset({"turn/complete"})
    assert valid.channel_tags == frozenset({"turn"})
    assert valid.extension_tags == frozenset({"host/custom"})

    with pytest.raises(ValueError, match="native_event_name must be non-empty after trimming"):
        LifecycleEventEnvelope(native_event_name="")

    with pytest.raises(ValueError, match="native_event_name must be non-empty after trimming"):
        LifecycleEventEnvelope(native_event_name="   ")

    with pytest.raises(
        ValueError,
        match="facet_tags must contain only non-empty values after trimming",
    ):
        LifecycleEventEnvelope(
            native_event_name="turn/complete",
            facet_tags=frozenset({""}),
        )

    with pytest.raises(
        ValueError,
        match="facet_tags must contain only non-empty values after trimming",
    ):
        LifecycleEventEnvelope(
            native_event_name="turn/complete",
            facet_tags=frozenset({"   "}),
        )

    with pytest.raises(
        ValueError,
        match="channel_tags must contain only non-empty values after trimming",
    ):
        LifecycleEventEnvelope(
            native_event_name="turn/complete",
            channel_tags=frozenset({""}),
        )

    with pytest.raises(
        ValueError,
        match="channel_tags must contain only non-empty values after trimming",
    ):
        LifecycleEventEnvelope(
            native_event_name="turn/complete",
            channel_tags=frozenset({"   "}),
        )

    with pytest.raises(
        ValueError,
        match="extension_tags must contain only non-empty values after trimming",
    ):
        LifecycleEventEnvelope(
            native_event_name="turn/complete",
            extension_tags=frozenset({""}),
        )

    with pytest.raises(
        ValueError,
        match="extension_tags must contain only non-empty values after trimming",
    ):
        LifecycleEventEnvelope(
            native_event_name="turn/complete",
            extension_tags=frozenset({"   "}),
        )

    with pytest.raises(
        TypeError,
        match="payload_metadata must contain only MetadataField instances",
    ):
        LifecycleEventEnvelope(
            native_event_name="turn/complete",
            payload_metadata=("not-field",),
        )

    with pytest.raises(
        TypeError,
        match="payload_handle must be EventPayloadHandle when provided, got str",
    ):
        LifecycleEventEnvelope(
            native_event_name="turn/complete",
            payload_handle="not-a-payload-handle",
        )


def test_environment_query_vocabulary_accepts_canonical_query_kinds() -> None:
    constructed = tuple(EnvironmentQuery(kind=kind) for kind in CANONICAL_QUERY_KINDS)

    assert {query.kind for query in constructed} == CANONICAL_QUERY_KINDS

    with pytest.raises(
        ValueError,
        match="target must be non-empty after trimming when provided",
    ):
        EnvironmentQuery(kind=STATE_SNAPSHOT, target="")

    with pytest.raises(
        ValueError,
        match="target must be non-empty after trimming when provided",
    ):
        EnvironmentQuery(kind=STATE_SNAPSHOT, target="   ")


def test_environment_query_rejects_non_canonical_query_kind() -> None:
    with pytest.raises(ValueError, match="canonical core query vocabulary"):
        EnvironmentQuery("NOT_A_KIND")

    with pytest.raises(ValueError, match="canonical core query vocabulary"):
        EnvironmentQuery("state_snapshot")

    with pytest.raises(ValueError, match="canonical core query vocabulary"):
        EnvironmentQuery("  execution_trace  ")


def test_environment_carriers_reject_non_canonical_available_query_kinds() -> None:
    with pytest.raises(ValueError, match="canonical core query vocabulary"):
        ExecutiveEnvironmentView(
            available_query_kinds=frozenset({"NOT_A_KIND"}),
        )

    with pytest.raises(ValueError, match="canonical core query vocabulary"):
        ExecutiveEnvironmentView(
            available_query_kinds=frozenset({"state_snapshot"}),
        )

    with pytest.raises(ValueError, match="canonical core query vocabulary"):
        CommitmentEnvironmentHandle(
            available_query_kinds=frozenset({"NOT_A_KIND"}),
        )

    with pytest.raises(ValueError, match="canonical core query vocabulary"):
        CommitmentEnvironmentHandle(
            available_query_kinds=frozenset({"execution_trace"}),
        )


def test_support_state_and_snapshot_are_distinct_types() -> None:
    contradiction = ContradictionRecord(
        source_tag="host/tool",
        summary="tool output conflicts with prior observation",
        evidence_tags=frozenset({"tool", "observation"}),
    )
    degradation = DegradationRecord(
        reason_code="missing-capability",
        capability_tags=frozenset({"approval"}),
        contradiction_records=(contradiction,),
    )
    trace = SupportTraceState(
        recent_events=(LifecycleEventEnvelope(native_event_name="turn/complete"),),
        candidate_refs=("candidate-1",),
        wake_receipts=(WakeReceipt("candidate-present", "turn/complete"),),
        degradation_records=(degradation,),
        observables=(StructuredObservation(observation_type="runtime-note"),),
    )
    session = SupportSessionState(
        branch_registry=("main",),
        pending_goal_refs=("goal-1",),
        role_view_tags=frozenset({"goal_continuity", "mode_and_gating"}),
        budget_history=("budget/neutral",),
        brake_history=("quiescent",),
        wake_counters=(SupportCounter("candidate-bearing", 1),),
        reminders=("review later",),
    )
    host = SupportHostState(
        affordance_tags=frozenset({"tool/intercept"}),
        approval_boundary_tags=frozenset({"approval/request"}),
        constraint_tags=frozenset({"host/degraded"}),
    )
    exec_memory = SupportExecMemoryState(
        published_memory_refs=(SupportReference("memory", "memo-1"),),
        artifact_refs=(SupportReference("artifact", "artifact-1"),),
    )

    state = SupportState(
        trace=trace,
        session=session,
        host=host,
        exec_memory_pub=exec_memory,
    )
    snapshot = SupportSnapshot(
        trace=trace,
        session=session,
        host=host,
        exec_memory_pub=exec_memory,
    )

    assert type(state) is not type(snapshot)
    assert state.trace.candidate_refs == ("candidate-1",)
    assert snapshot.exec_memory_pub.published_memory_refs[0].reference_id == "memo-1"


def test_support_counter_rejects_impossible_counts_and_accepts_zero() -> None:
    counter = SupportCounter("wake-receipts", 0)

    assert counter.counter_tag == "wake-receipts"
    assert counter.count == 0

    with pytest.raises(ValueError, match="counter_tag must be non-empty after trimming"):
        SupportCounter("", 1)

    with pytest.raises(ValueError, match="counter_tag must be non-empty after trimming"):
        SupportCounter("   ", 1)

    with pytest.raises(TypeError, match="non-negative integer, got bool"):
        SupportCounter("wake-receipts", True)

    with pytest.raises(ValueError, match="non-negative"):
        SupportCounter("wake-receipts", -1)


def test_wake_receipt_requires_non_empty_reason_and_named_event_identity() -> None:
    named = WakeReceipt("candidate-present", "approval/request")
    unnamed = WakeReceipt("candidate-present", None)

    assert named.reason_tag == "candidate-present"
    assert named.event_name == "approval/request"
    assert unnamed.event_name is None

    with pytest.raises(ValueError, match="reason_tag must be non-empty after trimming"):
        WakeReceipt("   ", "approval/request")

    with pytest.raises(ValueError, match="reason_tag must be non-empty after trimming"):
        WakeReceipt("", "approval/request")

    with pytest.raises(
        ValueError,
        match="event_name must be non-empty after trimming when provided",
    ):
        WakeReceipt("candidate-present", "")

    with pytest.raises(
        ValueError,
        match="event_name must be non-empty after trimming when provided",
    ):
        WakeReceipt("candidate-present", "   ")


def test_support_reference_requires_non_empty_kind_and_id() -> None:
    reference = SupportReference(
        "memory",
        "memo-1",
        tags=frozenset({"published"}),
        metadata=(MetadataField("visibility", "published"),),
    )

    assert reference.reference_kind == "memory"
    assert reference.reference_id == "memo-1"
    assert reference.tags == frozenset({"published"})
    assert reference.metadata[0].key == "visibility"

    with pytest.raises(ValueError, match="reference_kind must be non-empty after trimming"):
        SupportReference("", "memo-1")

    with pytest.raises(ValueError, match="reference_kind must be non-empty after trimming"):
        SupportReference("   ", "memo-1")

    with pytest.raises(ValueError, match="reference_id must be non-empty after trimming"):
        SupportReference("memory", "")

    with pytest.raises(ValueError, match="reference_id must be non-empty after trimming"):
        SupportReference("memory", "   ")

    with pytest.raises(
        ValueError,
        match="tags must contain only non-empty values after trimming",
    ):
        SupportReference("memory", "memo-1", tags=frozenset({""}))

    with pytest.raises(
        ValueError,
        match="tags must contain only non-empty values after trimming",
    ):
        SupportReference("memory", "memo-1", tags=frozenset({"   "}))

    with pytest.raises(
        TypeError,
        match="metadata must contain only MetadataField instances",
    ):
        SupportReference("memory", "memo-1", metadata=("not-field",))


def test_support_exec_memory_requires_typed_references() -> None:
    exec_memory = SupportExecMemoryState(
        published_memory_refs=(SupportReference("memory", "memo-1"),),
        artifact_refs=(SupportReference("artifact", "artifact-1"),),
    )

    assert exec_memory.published_memory_refs[0].reference_id == "memo-1"
    assert exec_memory.artifact_refs[0].reference_kind == "artifact"

    with pytest.raises(
        TypeError,
        match="published_memory_refs must contain only SupportReference instances",
    ):
        SupportExecMemoryState(
            published_memory_refs=("memo-1",),
        )

    with pytest.raises(
        TypeError,
        match="artifact_refs must contain only SupportReference instances",
    ):
        SupportExecMemoryState(
            artifact_refs=("artifact-1",),
        )


def test_support_snapshot_requires_typed_components() -> None:
    snapshot = SupportSnapshot(
        trace=SupportTraceState(),
        session=SupportSessionState(),
        host=SupportHostState(),
        exec_memory_pub=SupportExecMemoryState(),
    )

    assert isinstance(snapshot.trace, SupportTraceState)
    assert isinstance(snapshot.session, SupportSessionState)
    assert isinstance(snapshot.host, SupportHostState)
    assert isinstance(snapshot.exec_memory_pub, SupportExecMemoryState)

    with pytest.raises(TypeError, match="trace must be SupportTraceState, got str"):
        SupportSnapshot(
            trace="not-a-trace",
            session=SupportSessionState(),
            host=SupportHostState(),
            exec_memory_pub=SupportExecMemoryState(),
        )

    with pytest.raises(TypeError, match="session must be SupportSessionState, got str"):
        SupportSnapshot(
            trace=SupportTraceState(),
            session="not-a-session",
            host=SupportHostState(),
            exec_memory_pub=SupportExecMemoryState(),
        )

    with pytest.raises(TypeError, match="host must be SupportHostState, got str"):
        SupportSnapshot(
            trace=SupportTraceState(),
            session=SupportSessionState(),
            host="not-a-host",
            exec_memory_pub=SupportExecMemoryState(),
        )

    with pytest.raises(
        TypeError,
        match="exec_memory_pub must be SupportExecMemoryState, got str",
    ):
        SupportSnapshot(
            trace=SupportTraceState(),
            session=SupportSessionState(),
            host=SupportHostState(),
            exec_memory_pub="not-exec-memory",
        )


def test_support_state_requires_typed_components() -> None:
    state = SupportState(
        trace=SupportTraceState(),
        session=SupportSessionState(),
        host=SupportHostState(),
        exec_memory_pub=SupportExecMemoryState(),
    )

    assert isinstance(state.trace, SupportTraceState)
    assert isinstance(state.session, SupportSessionState)
    assert isinstance(state.host, SupportHostState)
    assert isinstance(state.exec_memory_pub, SupportExecMemoryState)

    with pytest.raises(TypeError, match="trace must be SupportTraceState, got str"):
        SupportState(
            trace="not-a-trace",
            session=SupportSessionState(),
            host=SupportHostState(),
            exec_memory_pub=SupportExecMemoryState(),
        )

    with pytest.raises(TypeError, match="session must be SupportSessionState, got str"):
        SupportState(
            trace=SupportTraceState(),
            session="not-a-session",
            host=SupportHostState(),
            exec_memory_pub=SupportExecMemoryState(),
        )

    with pytest.raises(TypeError, match="host must be SupportHostState, got str"):
        SupportState(
            trace=SupportTraceState(),
            session=SupportSessionState(),
            host="not-a-host",
            exec_memory_pub=SupportExecMemoryState(),
        )

    with pytest.raises(
        TypeError,
        match="exec_memory_pub must be SupportExecMemoryState, got str",
    ):
        SupportState(
            trace=SupportTraceState(),
            session=SupportSessionState(),
            host=SupportHostState(),
            exec_memory_pub="not-exec-memory",
        )


def test_support_trace_requires_non_empty_candidate_refs() -> None:
    trace = SupportTraceState(
        recent_events=(LifecycleEventEnvelope(native_event_name="turn/complete"),),
        candidate_refs=("candidate-1",),
        wake_receipts=(WakeReceipt("candidate-present", "approval/request"),),
        degradation_records=(
            DegradationRecord(
                reason_code="missing-capability",
                capability_tags=frozenset({"approval"}),
            ),
        ),
        observables=(StructuredObservation(observation_type="runtime-note"),),
    )

    assert trace.recent_events[0].native_event_name == "turn/complete"
    assert trace.candidate_refs == ("candidate-1",)
    assert trace.wake_receipts[0].reason_tag == "candidate-present"
    assert trace.degradation_records[0].reason_code == "missing-capability"
    assert trace.observables[0].observation_type == "runtime-note"

    with pytest.raises(
        TypeError,
        match="recent_events must contain only LifecycleEventEnvelope instances",
    ):
        SupportTraceState(
            recent_events=("event-1",),
            candidate_refs=("candidate-1",),
            wake_receipts=(WakeReceipt("candidate-present", "approval/request"),),
        )

    with pytest.raises(
        ValueError,
        match="candidate_refs must contain only non-empty values after trimming",
    ):
        SupportTraceState(
            recent_events=(LifecycleEventEnvelope(native_event_name="turn/complete"),),
            candidate_refs=("",),
            wake_receipts=(WakeReceipt("candidate-present", "approval/request"),),
        )

    with pytest.raises(
        ValueError,
        match="candidate_refs must contain only non-empty values after trimming",
    ):
        SupportTraceState(
            recent_events=(LifecycleEventEnvelope(native_event_name="turn/complete"),),
            candidate_refs=("   ",),
            wake_receipts=(WakeReceipt("candidate-present", "approval/request"),),
        )

    with pytest.raises(
        TypeError,
        match="wake_receipts must contain only WakeReceipt instances",
    ):
        SupportTraceState(
            recent_events=(LifecycleEventEnvelope(native_event_name="turn/complete"),),
            candidate_refs=("candidate-1",),
            wake_receipts=("receipt-1",),
        )

    with pytest.raises(
        TypeError,
        match="degradation_records must contain only DegradationRecord instances",
    ):
        SupportTraceState(
            recent_events=(LifecycleEventEnvelope(native_event_name="turn/complete"),),
            candidate_refs=("candidate-1",),
            wake_receipts=(WakeReceipt("candidate-present", "approval/request"),),
            degradation_records=("deg-1",),
        )

    with pytest.raises(
        TypeError,
        match="observables must contain only StructuredObservation instances",
    ):
        SupportTraceState(
            recent_events=(LifecycleEventEnvelope(native_event_name="turn/complete"),),
            candidate_refs=("candidate-1",),
            wake_receipts=(WakeReceipt("candidate-present", "approval/request"),),
            observables=("obs-1",),
        )


def test_support_session_requires_non_empty_pending_goal_refs() -> None:
    session = SupportSessionState(
        branch_registry=("main",),
        pending_goal_refs=("goal-1",),
        role_view_tags=frozenset({"goal_continuity"}),
        budget_history=("budget/neutral",),
        brake_history=("quiescent",),
        wake_counters=(SupportCounter("candidate-bearing", 1),),
        reminders=("review later",),
    )

    assert session.branch_registry == ("main",)
    assert session.pending_goal_refs == ("goal-1",)
    assert session.role_view_tags == frozenset({"goal_continuity"})
    assert session.budget_history == ("budget/neutral",)
    assert session.brake_history == ("quiescent",)
    assert session.reminders == ("review later",)
    assert session.wake_counters[0].counter_tag == "candidate-bearing"

    with pytest.raises(
        ValueError,
        match="branch_registry must contain only non-empty values after trimming",
    ):
        SupportSessionState(
            branch_registry=("",),
            pending_goal_refs=("goal-1",),
            role_view_tags=frozenset({"goal_continuity"}),
            budget_history=("budget/neutral",),
            brake_history=("quiescent",),
            wake_counters=(SupportCounter("candidate-bearing", 1),),
            reminders=("review later",),
        )

    with pytest.raises(
        ValueError,
        match="branch_registry must contain only non-empty values after trimming",
    ):
        SupportSessionState(
            branch_registry=("   ",),
            pending_goal_refs=("goal-1",),
            role_view_tags=frozenset({"goal_continuity"}),
            budget_history=("budget/neutral",),
            brake_history=("quiescent",),
            wake_counters=(SupportCounter("candidate-bearing", 1),),
            reminders=("review later",),
        )

    with pytest.raises(
        ValueError,
        match="pending_goal_refs must contain only non-empty values after trimming",
    ):
        SupportSessionState(
            branch_registry=("main",),
            pending_goal_refs=("",),
            role_view_tags=frozenset({"goal_continuity"}),
            budget_history=("budget/neutral",),
            brake_history=("quiescent",),
            wake_counters=(SupportCounter("candidate-bearing", 1),),
            reminders=("review later",),
        )

    with pytest.raises(
        ValueError,
        match="pending_goal_refs must contain only non-empty values after trimming",
    ):
        SupportSessionState(
            branch_registry=("main",),
            pending_goal_refs=("   ",),
            role_view_tags=frozenset({"goal_continuity"}),
            budget_history=("budget/neutral",),
            brake_history=("quiescent",),
            wake_counters=(SupportCounter("candidate-bearing", 1),),
            reminders=("review later",),
        )

    with pytest.raises(
        ValueError,
        match="budget_history must contain only non-empty values after trimming",
    ):
        SupportSessionState(
            branch_registry=("main",),
            pending_goal_refs=("goal-1",),
            role_view_tags=frozenset({"goal_continuity"}),
            budget_history=("   ",),
            brake_history=("quiescent",),
            wake_counters=(SupportCounter("candidate-bearing", 1),),
            reminders=("review later",),
        )

    with pytest.raises(
        ValueError,
        match="brake_history must contain only non-empty values after trimming",
    ):
        SupportSessionState(
            branch_registry=("main",),
            pending_goal_refs=("goal-1",),
            role_view_tags=frozenset({"goal_continuity"}),
            budget_history=("budget/neutral",),
            brake_history=("   ",),
            wake_counters=(SupportCounter("candidate-bearing", 1),),
            reminders=("review later",),
        )

    with pytest.raises(
        ValueError,
        match="reminders must contain only non-empty values after trimming",
    ):
        SupportSessionState(
            branch_registry=("main",),
            pending_goal_refs=("goal-1",),
            role_view_tags=frozenset({"goal_continuity"}),
            budget_history=("budget/neutral",),
            brake_history=("quiescent",),
            wake_counters=(SupportCounter("candidate-bearing", 1),),
            reminders=("   ",),
        )

    with pytest.raises(
        TypeError,
        match="wake_counters must contain only SupportCounter instances",
    ):
        SupportSessionState(
            branch_registry=("main",),
            pending_goal_refs=("goal-1",),
            role_view_tags=frozenset({"goal_continuity"}),
            budget_history=("budget/neutral",),
            brake_history=("quiescent",),
            wake_counters=("counter-1",),
            reminders=("review later",),
        )

    with pytest.raises(
        ValueError,
        match="role_view_tags must contain only non-empty values after trimming",
    ):
        SupportSessionState(
            branch_registry=("main",),
            pending_goal_refs=("goal-1",),
            role_view_tags=frozenset({"   "}),
            budget_history=("budget/neutral",),
            brake_history=("quiescent",),
            wake_counters=(SupportCounter("candidate-bearing", 1),),
            reminders=("review later",),
        )


def test_support_host_requires_non_empty_identity_tags() -> None:
    host = SupportHostState(
        affordance_tags=frozenset({"tool/intercept"}),
        approval_boundary_tags=frozenset({"approval/request"}),
        constraint_tags=frozenset({"host/degraded"}),
        metadata=(MetadataField("host_state", "degraded"),),
    )

    assert host.affordance_tags == frozenset({"tool/intercept"})
    assert host.approval_boundary_tags == frozenset({"approval/request"})
    assert host.constraint_tags == frozenset({"host/degraded"})
    assert host.metadata[0].key == "host_state"

    with pytest.raises(
        ValueError,
        match="affordance_tags must contain only non-empty values after trimming",
    ):
        SupportHostState(affordance_tags=frozenset({"   "}))

    with pytest.raises(
        ValueError,
        match="approval_boundary_tags must contain only non-empty values after trimming",
    ):
        SupportHostState(approval_boundary_tags=frozenset({"   "}))

    with pytest.raises(
        ValueError,
        match="constraint_tags must contain only non-empty values after trimming",
    ):
        SupportHostState(constraint_tags=frozenset({"   "}))

    with pytest.raises(
        TypeError,
        match="metadata must contain only MetadataField instances",
    ):
        SupportHostState(metadata=("not-field",))


def test_commitment_status_is_the_exact_three_state_lattice() -> None:
    assert {status.value for status in CommitmentStatus} == {
        "certified",
        "uncertified",
        "blocked",
    }


def test_commitment_candidate_requires_non_empty_identity() -> None:
    candidate = CommitmentCandidate(candidate_id="candidate-1")

    assert candidate.candidate_id == "candidate-1"

    with pytest.raises(ValueError, match="candidate_id must be non-empty after trimming"):
        CommitmentCandidate(candidate_id="")

    with pytest.raises(ValueError, match="candidate_id must be non-empty after trimming"):
        CommitmentCandidate(candidate_id="   ")


def test_provenance_manifest_supports_multiple_domain_agnostic_source_families() -> None:
    manifest = ProvenanceManifest(
        evidence_refs=(
            ProvenanceEvidenceRef(
                source_family="lifecycle_trace",
                reference_id="trace-1",
                source_tags=frozenset({"host/runtime"}),
            ),
            ProvenanceEvidenceRef(
                source_family="external_artifact",
                reference_id="artifact-1",
                source_tags=frozenset({"approval"}),
            ),
            ProvenanceEvidenceRef(
                source_family="result_artifact",
                reference_id="result-1",
                source_tags=frozenset({"artifact"}),
            ),
        ),
        metadata=(MetadataField("ordering", "downward-first"),),
    )

    assert [ref.source_family for ref in manifest.evidence_refs] == [
        "lifecycle_trace",
        "external_artifact",
        "result_artifact",
    ]
    assert manifest.metadata[0].value == "downward-first"

    with pytest.raises(ValueError, match="source_family must be non-empty after trimming"):
        ProvenanceEvidenceRef(
            source_family="",
            reference_id="artifact-blank-family",
        )

    with pytest.raises(ValueError, match="source_family must be non-empty after trimming"):
        ProvenanceEvidenceRef(
            source_family="   ",
            reference_id="artifact-blank-family",
        )

    with pytest.raises(ValueError, match="reference_id must be non-empty after trimming"):
        ProvenanceEvidenceRef(
            source_family="result_artifact",
            reference_id="",
        )

    with pytest.raises(ValueError, match="reference_id must be non-empty after trimming"):
        ProvenanceEvidenceRef(
            source_family="result_artifact",
            reference_id="   ",
        )


def test_boundary_assessment_keeps_blockedness_separate_from_commitment_status() -> None:
    blocked = BoundaryAssessment(
        blocked=True,
        reason_code="boundary-check-failed",
        boundary_tags=frozenset({"external-boundary"}),
        capability_tags=frozenset({"approval"}),
    )
    allowed = BoundaryAssessment(
        blocked=False,
        reason_code=None,
        boundary_tags=frozenset({"tool/write"}),
    )

    assert blocked.blocked is True
    assert allowed.blocked is False
    assert CommitmentStatus.UNCERTIFIED.value == "uncertified"


def test_blocked_boundary_assessment_requires_non_empty_reason_code() -> None:
    blocked = BoundaryAssessment(
        blocked=True,
        reason_code="approval-required",
    )

    assert blocked.reason_code == "approval-required"

    with pytest.raises(ValueError, match="blocked=True requires a non-empty reason_code"):
        BoundaryAssessment(blocked=True, reason_code=None)

    with pytest.raises(ValueError, match="blocked=True requires a non-empty reason_code"):
        BoundaryAssessment(blocked=True, reason_code="   ")


def test_degradation_and_error_records_preserve_reason_and_capabilities() -> None:
    contradiction = ContradictionRecord(
        source_tag="external/record",
        summary="external record does not match visible claim",
        evidence_tags=frozenset({"external-record"}),
    )
    error = CoreErrorRecord(
        reason_code="boundary-required",
        capability_tags=frozenset({"approval", "tool"}),
        contradiction_records=(contradiction,),
        metadata=(MetadataField("mode", "verify"),),
    )

    assert error.reason_code == "boundary-required"
    assert error.capability_tags == frozenset({"approval", "tool"})
    assert error.contradiction_records[0].source_tag == "external/record"
    assert error.contradiction_records[0].summary == "external record does not match visible claim"

    with pytest.raises(ValueError, match="source_tag must be non-empty after trimming"):
        ContradictionRecord(
            source_tag="",
            summary="external record does not match visible claim",
        )

    with pytest.raises(ValueError, match="source_tag must be non-empty after trimming"):
        ContradictionRecord(
            source_tag="   ",
            summary="external record does not match visible claim",
        )

    with pytest.raises(ValueError, match="summary must be non-empty after trimming"):
        ContradictionRecord(
            source_tag="external/record",
            summary="",
        )

    with pytest.raises(ValueError, match="summary must be non-empty after trimming"):
        ContradictionRecord(
            source_tag="external/record",
            summary="   ",
        )

    with pytest.raises(
        ValueError,
        match="evidence_tags must contain only non-empty values after trimming",
    ):
        ContradictionRecord(
            source_tag="external/record",
            summary="external record does not match visible claim",
            evidence_tags=frozenset({""}),
        )

    with pytest.raises(
        ValueError,
        match="evidence_tags must contain only non-empty values after trimming",
    ):
        ContradictionRecord(
            source_tag="external/record",
            summary="external record does not match visible claim",
            evidence_tags=frozenset({"   "}),
        )

    with pytest.raises(ValueError, match="reason_code must be non-empty after trimming"):
        DegradationRecord(reason_code="")

    with pytest.raises(ValueError, match="reason_code must be non-empty after trimming"):
        DegradationRecord(reason_code="   ")

    with pytest.raises(
        ValueError,
        match="capability_tags must contain only non-empty values after trimming",
    ):
        DegradationRecord(
            reason_code="provenance-unavailable",
            capability_tags=frozenset({""}),
        )

    with pytest.raises(
        ValueError,
        match="capability_tags must contain only non-empty values after trimming",
    ):
        DegradationRecord(
            reason_code="provenance-unavailable",
            capability_tags=frozenset({"   "}),
        )

    with pytest.raises(
        TypeError,
        match="contradiction_records must contain only ContradictionRecord instances",
    ):
        DegradationRecord(
            reason_code="provenance-unavailable",
            contradiction_records=("not-a-contradiction",),
        )

    with pytest.raises(
        TypeError,
        match="metadata must contain only MetadataField instances",
    ):
        DegradationRecord(
            reason_code="provenance-unavailable",
            metadata=("not-a-field",),
        )

    with pytest.raises(ValueError, match="reason_code must be non-empty after trimming"):
        CoreErrorRecord(reason_code="")

    with pytest.raises(ValueError, match="reason_code must be non-empty after trimming"):
        CoreErrorRecord(reason_code="   ")

    with pytest.raises(
        ValueError,
        match="capability_tags must contain only non-empty values after trimming",
    ):
        CoreErrorRecord(
            reason_code="boundary-required",
            capability_tags=frozenset({""}),
        )

    with pytest.raises(
        ValueError,
        match="capability_tags must contain only non-empty values after trimming",
    ):
        CoreErrorRecord(
            reason_code="boundary-required",
            capability_tags=frozenset({"   "}),
        )

    with pytest.raises(
        TypeError,
        match="contradiction_records must contain only ContradictionRecord instances",
    ):
        CoreErrorRecord(
            reason_code="boundary-required",
            contradiction_records=("not-a-contradiction",),
        )

    with pytest.raises(
        TypeError,
        match="metadata must contain only MetadataField instances",
    ):
        CoreErrorRecord(
            reason_code="boundary-required",
            metadata=("not-a-field",),
        )


def test_commitment_verdict_holds_typed_certification_references() -> None:
    contradiction = ContradictionRecord(
        source_tag="runtime-record",
        summary="runtime record conflicts with approval state",
        evidence_tags=frozenset({"runtime-record", "approval"}),
    )
    degradation = DegradationRecord(
        reason_code="provenance-unavailable",
        capability_tags=frozenset({"external-record"}),
        contradiction_records=(contradiction,),
    )
    manifest = ProvenanceManifest(
        evidence_refs=(
            ProvenanceEvidenceRef(
                source_family="lifecycle_trace",
                reference_id="trace-1",
            ),
        ),
        contradiction_refs=(contradiction,),
    )
    boundary = BoundaryAssessment(
        blocked=False,
        reason_code=None,
        boundary_tags=frozenset({"external-boundary"}),
    )
    verdict = CommitmentVerdict(
        status=CommitmentStatus.UNCERTIFIED,
        candidate=CommitmentCandidate(candidate_id="candidate-1"),
        provenance_manifest=manifest,
        boundary_assessment=boundary,
        degradation_refs=(degradation,),
        contradiction_refs=(contradiction,),
        metadata=(MetadataField("wake", "candidate-present"),),
    )

    assert verdict.provenance_manifest is manifest
    assert verdict.boundary_assessment is boundary
    assert verdict.degradation_refs[0].reason_code == "provenance-unavailable"
    assert verdict.contradiction_refs[0].source_tag == "runtime-record"


def test_blocked_commitment_verdict_requires_blocked_boundary_assessment() -> None:
    candidate = CommitmentCandidate(candidate_id="candidate-blocked")
    manifest = ProvenanceManifest()
    blocked_boundary = BoundaryAssessment(
        blocked=True,
        reason_code="approval-required",
        boundary_tags=frozenset({"external-boundary"}),
    )
    verdict = CommitmentVerdict(
        status=CommitmentStatus.BLOCKED,
        candidate=candidate,
        provenance_manifest=manifest,
        boundary_assessment=blocked_boundary,
    )

    assert verdict.boundary_assessment is blocked_boundary
    assert verdict.boundary_assessment.reason_code == "approval-required"

    with pytest.raises(
        ValueError,
        match="status=BLOCKED requires boundary_assessment with blocked=True",
    ):
        CommitmentVerdict(
            status=CommitmentStatus.BLOCKED,
            candidate=candidate,
            provenance_manifest=manifest,
            boundary_assessment=None,
        )

    with pytest.raises(
        ValueError,
        match="status=BLOCKED requires boundary_assessment with blocked=True",
    ):
        CommitmentVerdict(
            status=CommitmentStatus.BLOCKED,
            candidate=candidate,
            provenance_manifest=manifest,
            boundary_assessment=BoundaryAssessment(blocked=False),
        )

    with pytest.raises(
        ValueError,
        match="boundary_assessment blocked=True requires status=BLOCKED",
    ):
        CommitmentVerdict(
            status=CommitmentStatus.CERTIFIED,
            candidate=candidate,
            provenance_manifest=manifest,
            boundary_assessment=blocked_boundary,
        )

    with pytest.raises(
        ValueError,
        match="boundary_assessment blocked=True requires status=BLOCKED",
    ):
        CommitmentVerdict(
            status=CommitmentStatus.UNCERTIFIED,
            candidate=candidate,
            provenance_manifest=manifest,
            boundary_assessment=blocked_boundary,
        )


def test_certified_commitment_verdict_requires_concrete_provenance() -> None:
    candidate = CommitmentCandidate(candidate_id="candidate-certified")
    boundary = BoundaryAssessment(blocked=False)
    concrete_manifest = ProvenanceManifest(
        evidence_refs=(
            ProvenanceEvidenceRef(
                source_family="result_artifact",
                reference_id="artifact-1",
            ),
        ),
    )
    verdict = CommitmentVerdict(
        status=CommitmentStatus.CERTIFIED,
        candidate=candidate,
        provenance_manifest=concrete_manifest,
        boundary_assessment=boundary,
    )

    assert verdict.provenance_manifest is concrete_manifest
    assert verdict.provenance_manifest.evidence_refs[0].reference_id == "artifact-1"

    with pytest.raises(
        ValueError,
        match="status=CERTIFIED requires provenance_manifest with at least one concrete evidence reference",
    ):
        CommitmentVerdict(
            status=CommitmentStatus.CERTIFIED,
            candidate=candidate,
            provenance_manifest=None,
            boundary_assessment=boundary,
        )

    with pytest.raises(
        ValueError,
        match="status=CERTIFIED requires provenance_manifest with at least one concrete evidence reference",
    ):
        CommitmentVerdict(
            status=CommitmentStatus.CERTIFIED,
            candidate=candidate,
            provenance_manifest=ProvenanceManifest(),
            boundary_assessment=boundary,
        )

    with pytest.raises(
        ValueError,
        match="reference_id must be non-empty after trimming",
    ):
        CommitmentVerdict(
            status=CommitmentStatus.CERTIFIED,
            candidate=candidate,
            provenance_manifest=ProvenanceManifest(
                evidence_refs=(
                    ProvenanceEvidenceRef(
                        source_family="artifact",
                        reference_id="   ",
                    ),
                ),
            ),
            boundary_assessment=boundary,
        )


def test_certification_context_rejects_executive_environment_view() -> None:
    observation = ObservationBundle(
        event=LifecycleEventEnvelope(native_event_name="turn/complete"),
        payload_view=PayloadView(),
    )
    candidate = CommitmentCandidate(candidate_id="candidate-1")
    executive_view = ExecutiveEnvironmentView(
        available_query_kinds=frozenset({STATE_SNAPSHOT, CAPABILITY_VIEW}),
        host_capability_tags=frozenset({"tool"}),
        bounded_requests=(
            EnvironmentQuery(
                kind=STATE_SNAPSHOT,
                target="session",
                capability_tags=frozenset({"runtime/read"}),
            ),
        ),
    )

    try:
        CertificationContext(
            candidate=candidate,
            observation=observation,
            environment_handle=executive_view,  # type: ignore[arg-type]
        )
    except TypeError as exc:
        assert "CommitmentEnvironmentHandle" in str(exc)
    else:
        raise AssertionError("ExecutiveEnvironmentView crossed the certification firewall.")


def test_certification_context_accepts_commitment_environment_handle() -> None:
    observation = ObservationBundle(
        event=LifecycleEventEnvelope(native_event_name="approval/result"),
        payload_view=PayloadView(),
    )
    candidate = CommitmentCandidate(candidate_id="candidate-1")
    commitment_handle = CommitmentEnvironmentHandle(
        available_query_kinds=frozenset({STATE_SNAPSHOT, EXECUTION_TRACE}),
        evidence_requests=(
            EnvironmentQuery(
                kind=EXECUTION_TRACE,
                target="event-trace",
                capability_tags=frozenset({"trace/read"}),
            ),
        ),
        capability_tags=frozenset({"trace/read", "boundary/check"}),
        boundary_scope_tags=frozenset({"external-boundary"}),
    )
    context = CertificationContext(
        candidate=candidate,
        observation=observation,
        environment_handle=commitment_handle,
        wake_reasons=frozenset({"approval-gated"}),
    )

    assert context.environment_handle is commitment_handle
    assert context.wake_reasons == frozenset({"approval-gated"})
