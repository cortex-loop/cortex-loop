"""Focused tests for the first AUX scaffold slice."""

import pytest

from cortex.aux.augmentation import (
    AugmentedSupportSnapshot,
    AuxiliarySupportAppendix,
    augment_snapshot,
)
from cortex.aux.cost import AuxBurdenReport
from cortex.core.envelopes import MetadataField
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


def test_augment_snapshot_requires_explicit_support_snapshot_and_preserves_core_view() -> None:
    snapshot = _make_snapshot()
    appendix = AuxiliarySupportAppendix(
        derived_support_refs=(SupportReference("adjunct", "aux-1"),),
        derived_tags=frozenset({"support/cluster"}),
        notes=("derived auxiliary context",),
    )

    augmented = augment_snapshot(snapshot, appendix)

    assert isinstance(augmented, AugmentedSupportSnapshot)
    assert augmented.core_snapshot is snapshot
    assert augmented.auxiliary_support is appendix
    assert augmented.core_snapshot.trace.candidate_refs == ("candidate-1",)

    with pytest.raises(TypeError, match="SupportSnapshot"):
        augment_snapshot(SupportState(), appendix)

    with pytest.raises(
        TypeError,
        match="derived_support_refs must contain only SupportReference instances",
    ):
        augment_snapshot(snapshot, AuxiliarySupportAppendix(derived_support_refs=("aux-1",)))


def test_augment_snapshot_appends_auxiliary_support_without_mutating_core_snapshot_semantics() -> None:
    snapshot = _make_snapshot()
    appendix = AuxiliarySupportAppendix(
        derived_support_refs=(SupportReference("adjunct", "aux-2"),),
        derived_tags=frozenset({"resume/fidelity"}),
        metadata=(MetadataField("derivation_source", "auxiliary-review"),),
    )

    augmented = augment_snapshot(snapshot, appendix)

    assert augmented.core_snapshot.host.affordance_tags == frozenset({"tool/intercept"})
    assert augmented.core_snapshot.exec_memory_pub.artifact_refs[0].reference_id == "artifact-1"
    assert augmented.auxiliary_support.derived_support_refs[0].reference_id == "aux-2"
    assert augmented.auxiliary_support.metadata[0].key == "derivation_source"


def test_aux_burden_report_enforces_non_negative_values() -> None:
    burden = AuxBurdenReport(
        compute_overhead=1.0,
        memory_overhead=2,
        latency_overhead=0.1,
        environment_query_cost=3.0,
        retrieval_cost=0.5,
        intervention_burden=0.0,
    )

    assert burden.compute_overhead == 1.0
    assert burden.memory_overhead == 2
    assert burden.environment_query_cost == 3.0

    with pytest.raises(ValueError, match="non-negative"):
        AuxBurdenReport(latency_overhead=-0.1)


def test_aux_burden_report_rejects_boolean_values() -> None:
    with pytest.raises(TypeError, match="compute_overhead must be numeric, got bool"):
        AuxBurdenReport(compute_overhead=True)

    with pytest.raises(TypeError, match="memory_overhead must be numeric, got bool"):
        AuxBurdenReport(memory_overhead=False)


def test_aux_scaffold_types_remain_domain_general_and_removable() -> None:
    appendix = AuxiliarySupportAppendix(
        derived_support_refs=(SupportReference("adjunct", "aux-3"),),
        derived_tags=frozenset({"domain-general"}),
        notes=("general-purpose auxiliary support",),
    )
    burden = AuxBurdenReport(
        environment_query_cost=2.0,
        retrieval_cost=1.5,
        intervention_burden=1.0,
    )

    assert appendix.derived_support_refs[0].reference_kind == "adjunct"
    assert appendix.notes == ("general-purpose auxiliary support",)
    assert burden.retrieval_cost == 1.5
    assert burden.intervention_burden == 1.0

    with pytest.raises(
        TypeError,
        match="derived_support_refs must contain only SupportReference instances",
    ):
        AuxiliarySupportAppendix(derived_support_refs=("aux-1",))


def test_augment_snapshot_cannot_start_from_blank_core_support_reference_identity() -> None:
    snapshot = _make_snapshot()

    with pytest.raises(ValueError, match="reference_kind must be non-empty after trimming"):
        augment_snapshot(
            SupportSnapshot(
                trace=snapshot.trace,
                session=snapshot.session,
                host=snapshot.host,
                exec_memory_pub=SupportExecMemoryState(
                    published_memory_refs=(SupportReference("", "memo-blank"),),
                    artifact_refs=snapshot.exec_memory_pub.artifact_refs,
                ),
            ),
            AuxiliarySupportAppendix(),
        )

    with pytest.raises(ValueError, match="reference_id must be non-empty after trimming"):
        augment_snapshot(
            SupportSnapshot(
                trace=snapshot.trace,
                session=snapshot.session,
                host=snapshot.host,
                exec_memory_pub=SupportExecMemoryState(
                    published_memory_refs=(SupportReference("memory", "   "),),
                    artifact_refs=snapshot.exec_memory_pub.artifact_refs,
                ),
            ),
            AuxiliarySupportAppendix(),
        )

    with pytest.raises(
        ValueError,
        match="tags must contain only non-empty values after trimming",
    ):
        augment_snapshot(
            SupportSnapshot(
                trace=snapshot.trace,
                session=snapshot.session,
                host=snapshot.host,
                exec_memory_pub=SupportExecMemoryState(
                    published_memory_refs=(
                        SupportReference(
                            "memory",
                            "memo-1",
                            tags=frozenset({"   "}),
                        ),
                    ),
                    artifact_refs=snapshot.exec_memory_pub.artifact_refs,
                ),
            ),
            AuxiliarySupportAppendix(),
        )

    with pytest.raises(
        TypeError,
        match="metadata must contain only MetadataField instances",
    ):
        augment_snapshot(
            SupportSnapshot(
                trace=snapshot.trace,
                session=snapshot.session,
                host=snapshot.host,
                exec_memory_pub=SupportExecMemoryState(
                    published_memory_refs=(
                        SupportReference(
                            "memory",
                            "memo-1",
                            metadata=("not-field",),
                        ),
                    ),
                    artifact_refs=snapshot.exec_memory_pub.artifact_refs,
                ),
            ),
            AuxiliarySupportAppendix(),
        )


def test_augment_snapshot_cannot_start_from_untyped_core_exec_memory_refs() -> None:
    snapshot = _make_snapshot()

    with pytest.raises(
        TypeError,
        match="published_memory_refs must contain only SupportReference instances",
    ):
        augment_snapshot(
            SupportSnapshot(
                trace=snapshot.trace,
                session=snapshot.session,
                host=snapshot.host,
                exec_memory_pub=SupportExecMemoryState(
                    published_memory_refs=("memo-1",),
                    artifact_refs=snapshot.exec_memory_pub.artifact_refs,
                ),
            ),
            AuxiliarySupportAppendix(),
        )

    with pytest.raises(
        TypeError,
        match="artifact_refs must contain only SupportReference instances",
    ):
        augment_snapshot(
            SupportSnapshot(
                trace=snapshot.trace,
                session=snapshot.session,
                host=snapshot.host,
                exec_memory_pub=SupportExecMemoryState(
                    published_memory_refs=snapshot.exec_memory_pub.published_memory_refs,
                    artifact_refs=("artifact-1",),
                ),
            ),
            AuxiliarySupportAppendix(),
        )


def test_augment_snapshot_cannot_start_from_untyped_core_snapshot_component() -> None:
    with pytest.raises(TypeError, match="trace must be SupportTraceState, got str"):
        augment_snapshot(
            SupportSnapshot(
                trace="not-a-trace",
                session=SupportSessionState(),
                host=SupportHostState(),
                exec_memory_pub=SupportExecMemoryState(),
            ),
            AuxiliarySupportAppendix(),
        )


def test_augment_snapshot_cannot_start_from_blank_core_wake_receipt_identity() -> None:
    snapshot = _make_snapshot()

    with pytest.raises(ValueError, match="reason_tag must be non-empty after trimming"):
        augment_snapshot(
            SupportSnapshot(
                trace=SupportTraceState(
                    candidate_refs=snapshot.trace.candidate_refs,
                    wake_receipts=(WakeReceipt("   ", event_name="approval/request"),),
                ),
                session=snapshot.session,
                host=snapshot.host,
                exec_memory_pub=snapshot.exec_memory_pub,
            ),
            AuxiliarySupportAppendix(),
        )

    with pytest.raises(
        TypeError,
        match="recent_events must contain only LifecycleEventEnvelope instances",
    ):
        augment_snapshot(
            SupportSnapshot(
                trace=SupportTraceState(
                    recent_events=("event-1",),
                    candidate_refs=snapshot.trace.candidate_refs,
                    wake_receipts=snapshot.trace.wake_receipts,
                ),
                session=snapshot.session,
                host=snapshot.host,
                exec_memory_pub=snapshot.exec_memory_pub,
            ),
            AuxiliarySupportAppendix(),
        )

    with pytest.raises(
        TypeError,
        match="wake_receipts must contain only WakeReceipt instances",
    ):
        augment_snapshot(
            SupportSnapshot(
                trace=SupportTraceState(
                    candidate_refs=snapshot.trace.candidate_refs,
                    wake_receipts=("receipt-1",),
                ),
                session=snapshot.session,
                host=snapshot.host,
                exec_memory_pub=snapshot.exec_memory_pub,
            ),
            AuxiliarySupportAppendix(),
        )

    with pytest.raises(
        TypeError,
        match="degradation_records must contain only DegradationRecord instances",
    ):
        augment_snapshot(
            SupportSnapshot(
                trace=SupportTraceState(
                    candidate_refs=snapshot.trace.candidate_refs,
                    wake_receipts=snapshot.trace.wake_receipts,
                    degradation_records=("deg-1",),
                ),
                session=snapshot.session,
                host=snapshot.host,
                exec_memory_pub=snapshot.exec_memory_pub,
            ),
            AuxiliarySupportAppendix(),
        )

    with pytest.raises(
        TypeError,
        match="observables must contain only StructuredObservation instances",
    ):
        augment_snapshot(
            SupportSnapshot(
                trace=SupportTraceState(
                    candidate_refs=snapshot.trace.candidate_refs,
                    wake_receipts=snapshot.trace.wake_receipts,
                    observables=("obs-1",),
                ),
                session=snapshot.session,
                host=snapshot.host,
                exec_memory_pub=snapshot.exec_memory_pub,
            ),
            AuxiliarySupportAppendix(),
        )

    with pytest.raises(
        ValueError,
        match="event_name must be non-empty after trimming when provided",
    ):
        augment_snapshot(
            SupportSnapshot(
                trace=SupportTraceState(
                    candidate_refs=snapshot.trace.candidate_refs,
                    wake_receipts=(WakeReceipt("candidate-present", event_name="   "),),
                ),
                session=snapshot.session,
                host=snapshot.host,
                exec_memory_pub=snapshot.exec_memory_pub,
            ),
            AuxiliarySupportAppendix(),
        )


def test_augment_snapshot_cannot_start_from_blank_core_support_counter_tag() -> None:
    snapshot = _make_snapshot()

    with pytest.raises(ValueError, match="counter_tag must be non-empty after trimming"):
        augment_snapshot(
            SupportSnapshot(
                trace=snapshot.trace,
                session=SupportSessionState(
                    pending_goal_refs=snapshot.session.pending_goal_refs,
                    wake_counters=(SupportCounter("   ", 1),),
                ),
                host=snapshot.host,
                exec_memory_pub=snapshot.exec_memory_pub,
            ),
            AuxiliarySupportAppendix(),
        )

    with pytest.raises(
        TypeError,
        match="wake_counters must contain only SupportCounter instances",
    ):
        augment_snapshot(
            SupportSnapshot(
                trace=snapshot.trace,
                session=SupportSessionState(
                    pending_goal_refs=snapshot.session.pending_goal_refs,
                    wake_counters=("counter-1",),
                ),
                host=snapshot.host,
                exec_memory_pub=snapshot.exec_memory_pub,
            ),
            AuxiliarySupportAppendix(),
        )


def test_augment_snapshot_cannot_start_from_blank_core_support_trace_candidate_ref() -> None:
    snapshot = _make_snapshot()

    with pytest.raises(
        ValueError,
        match="candidate_refs must contain only non-empty values after trimming",
    ):
        augment_snapshot(
            SupportSnapshot(
                trace=SupportTraceState(
                    candidate_refs=("   ",),
                    wake_receipts=snapshot.trace.wake_receipts,
                ),
                session=snapshot.session,
                host=snapshot.host,
                exec_memory_pub=snapshot.exec_memory_pub,
            ),
            AuxiliarySupportAppendix(),
        )


def test_augment_snapshot_cannot_start_from_blank_core_pending_goal_ref() -> None:
    snapshot = _make_snapshot()

    with pytest.raises(
        ValueError,
        match="pending_goal_refs must contain only non-empty values after trimming",
    ):
        augment_snapshot(
            SupportSnapshot(
                trace=snapshot.trace,
                session=SupportSessionState(
                    pending_goal_refs=("   ",),
                    wake_counters=snapshot.session.wake_counters,
                ),
                host=snapshot.host,
                exec_memory_pub=snapshot.exec_memory_pub,
            ),
            AuxiliarySupportAppendix(),
        )


def test_augment_snapshot_cannot_start_from_blank_core_role_view_tag() -> None:
    snapshot = _make_snapshot()

    with pytest.raises(
        ValueError,
        match="role_view_tags must contain only non-empty values after trimming",
    ):
        augment_snapshot(
            SupportSnapshot(
                trace=snapshot.trace,
                session=SupportSessionState(
                    pending_goal_refs=snapshot.session.pending_goal_refs,
                    role_view_tags=frozenset({"   "}),
                    wake_counters=snapshot.session.wake_counters,
                ),
                host=snapshot.host,
                exec_memory_pub=snapshot.exec_memory_pub,
            ),
            AuxiliarySupportAppendix(),
        )


def test_augment_snapshot_cannot_start_from_blank_core_branch_registry_entry() -> None:
    snapshot = _make_snapshot()

    with pytest.raises(
        ValueError,
        match="branch_registry must contain only non-empty values after trimming",
    ):
        augment_snapshot(
            SupportSnapshot(
                trace=snapshot.trace,
                session=SupportSessionState(
                    branch_registry=("   ",),
                    pending_goal_refs=snapshot.session.pending_goal_refs,
                    role_view_tags=snapshot.session.role_view_tags,
                    wake_counters=snapshot.session.wake_counters,
                ),
                host=snapshot.host,
                exec_memory_pub=snapshot.exec_memory_pub,
            ),
            AuxiliarySupportAppendix(),
        )


def test_augment_snapshot_cannot_start_from_blank_core_budget_history_entry() -> None:
    snapshot = _make_snapshot()

    with pytest.raises(
        ValueError,
        match="budget_history must contain only non-empty values after trimming",
    ):
        augment_snapshot(
            SupportSnapshot(
                trace=snapshot.trace,
                session=SupportSessionState(
                    branch_registry=snapshot.session.branch_registry,
                    pending_goal_refs=snapshot.session.pending_goal_refs,
                    role_view_tags=snapshot.session.role_view_tags,
                    budget_history=("   ",),
                    wake_counters=snapshot.session.wake_counters,
                ),
                host=snapshot.host,
                exec_memory_pub=snapshot.exec_memory_pub,
            ),
            AuxiliarySupportAppendix(),
        )


def test_augment_snapshot_cannot_start_from_blank_core_brake_history_entry() -> None:
    snapshot = _make_snapshot()

    with pytest.raises(
        ValueError,
        match="brake_history must contain only non-empty values after trimming",
    ):
        augment_snapshot(
            SupportSnapshot(
                trace=snapshot.trace,
                session=SupportSessionState(
                    branch_registry=snapshot.session.branch_registry,
                    pending_goal_refs=snapshot.session.pending_goal_refs,
                    role_view_tags=snapshot.session.role_view_tags,
                    budget_history=snapshot.session.budget_history,
                    brake_history=("   ",),
                    wake_counters=snapshot.session.wake_counters,
                ),
                host=snapshot.host,
                exec_memory_pub=snapshot.exec_memory_pub,
            ),
            AuxiliarySupportAppendix(),
        )


def test_augment_snapshot_cannot_start_from_blank_core_reminder_entry() -> None:
    snapshot = _make_snapshot()

    with pytest.raises(
        ValueError,
        match="reminders must contain only non-empty values after trimming",
    ):
        augment_snapshot(
            SupportSnapshot(
                trace=snapshot.trace,
                session=SupportSessionState(
                    branch_registry=snapshot.session.branch_registry,
                    pending_goal_refs=snapshot.session.pending_goal_refs,
                    role_view_tags=snapshot.session.role_view_tags,
                    budget_history=snapshot.session.budget_history,
                    brake_history=snapshot.session.brake_history,
                    wake_counters=snapshot.session.wake_counters,
                    reminders=("   ",),
                ),
                host=snapshot.host,
                exec_memory_pub=snapshot.exec_memory_pub,
            ),
            AuxiliarySupportAppendix(),
        )


def test_augment_snapshot_cannot_start_from_blank_core_host_tag() -> None:
    snapshot = _make_snapshot()

    with pytest.raises(
        ValueError,
        match="affordance_tags must contain only non-empty values after trimming",
    ):
        augment_snapshot(
            SupportSnapshot(
                trace=snapshot.trace,
                session=snapshot.session,
                host=SupportHostState(affordance_tags=frozenset({"   "})),
                exec_memory_pub=snapshot.exec_memory_pub,
            ),
            AuxiliarySupportAppendix(),
        )

    with pytest.raises(
        ValueError,
        match="approval_boundary_tags must contain only non-empty values after trimming",
    ):
        augment_snapshot(
            SupportSnapshot(
                trace=snapshot.trace,
                session=snapshot.session,
                host=SupportHostState(approval_boundary_tags=frozenset({"   "})),
                exec_memory_pub=snapshot.exec_memory_pub,
            ),
            AuxiliarySupportAppendix(),
        )

    with pytest.raises(
        ValueError,
        match="constraint_tags must contain only non-empty values after trimming",
    ):
        augment_snapshot(
            SupportSnapshot(
                trace=snapshot.trace,
                session=snapshot.session,
                host=SupportHostState(constraint_tags=frozenset({"   "})),
                exec_memory_pub=snapshot.exec_memory_pub,
            ),
            AuxiliarySupportAppendix(),
        )

    with pytest.raises(
        TypeError,
        match="metadata must contain only MetadataField instances",
    ):
        augment_snapshot(
            SupportSnapshot(
                trace=snapshot.trace,
                session=snapshot.session,
                host=SupportHostState(metadata=("not-field",)),
                exec_memory_pub=snapshot.exec_memory_pub,
            ),
            AuxiliarySupportAppendix(),
        )


def _make_snapshot() -> SupportSnapshot:
    trace = SupportTraceState(
        candidate_refs=("candidate-1",),
        wake_receipts=(WakeReceipt("candidate-present", event_name="approval/request"),),
    )
    session = SupportSessionState(
        pending_goal_refs=("goal-1",),
        wake_counters=(SupportCounter("candidate-bearing", 1),),
    )
    host = SupportHostState(
        affordance_tags=frozenset({"tool/intercept"}),
        approval_boundary_tags=frozenset({"approval/request"}),
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
