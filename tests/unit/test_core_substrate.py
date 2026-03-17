"""Unit tests for the minimal typed core substrate."""

from cortex.core.commitments import CertificationContext, CommitmentCandidate, CommitmentStatus
from cortex.core.environment import (
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


def test_commitment_status_is_the_exact_three_state_lattice() -> None:
    assert {status.value for status in CommitmentStatus} == {
        "certified",
        "uncertified",
        "blocked",
    }


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
