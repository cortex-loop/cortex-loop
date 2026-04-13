"""Shared support-state builders for AUX experimental tests."""

from __future__ import annotations

from cortex.aux.evaluation import AuxTemporalScenario
from cortex.aux.reference_replay import AuxReferenceReplayScenario
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
from cortex.sre.brake import BrakeState
from cortex.sre.families import SoftControlFamily
from cortex.sre.state import (
    ReferenceBrakeView,
    ReferenceControlAllocationView,
    ReferenceExecutiveState,
    ReferenceGoalContinuityView,
    ReferenceModeAndGatingView,
    ReferenceUncertaintyMonitoringView,
)
from cortex.sre.uncertainty import UncertaintyEstimate


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


def make_temporal_support_snapshot(
    snapshot_id: str,
    *,
    candidate_refs: tuple[str, ...] = (),
    pending_goal_refs: tuple[str, ...] = (),
    branch_registry: tuple[str, ...] = ("main",),
    reminders: tuple[str, ...] = (),
    wake_reason_tags: tuple[str, ...] = (),
    degradation_reason: str | None = None,
    contradiction_evidence_tags: tuple[str, ...] = (),
    published_memory_refs: tuple[str, ...] = (),
    artifact_refs: tuple[str, ...] = (),
    brake_history: tuple[str, ...] = (),
) -> SupportSnapshot:
    contradiction_records = ()
    degradation_records = ()
    if degradation_reason is not None:
        contradiction_records = (
            ContradictionRecord(
                source_tag=f"{snapshot_id}/contradiction",
                summary=f"{snapshot_id} contradiction summary",
                evidence_tags=frozenset(contradiction_evidence_tags),
            ),
        )
        degradation_records = (
            DegradationRecord(
                reason_code=degradation_reason,
                capability_tags=frozenset(contradiction_evidence_tags),
                contradiction_records=contradiction_records,
            ),
        )

    trace = SupportTraceState(
        recent_events=(
            LifecycleEventEnvelope(
                native_event_name="turn/complete",
                payload_handle=EventPayloadHandle(
                    payload_kind="host-payload",
                    metadata=(MetadataField("source", snapshot_id),),
                ),
                facet_tags=frozenset({"approval/request"}),
            ),
        ),
        candidate_refs=candidate_refs,
        wake_receipts=tuple(
            WakeReceipt(reason_tag=reason_tag, event_name="turn/complete")
            for reason_tag in wake_reason_tags
        ),
        degradation_records=degradation_records,
    )
    session = SupportSessionState(
        branch_registry=branch_registry,
        pending_goal_refs=pending_goal_refs,
        role_view_tags=frozenset({"review", "aux/removable"}),
        budget_history=("medium",),
        brake_history=brake_history,
        wake_counters=(SupportCounter("wake-receipts", len(wake_reason_tags)),),
        reminders=reminders,
    )
    host = SupportHostState(
        affordance_tags=frozenset({"tool/intercept"}),
        approval_boundary_tags=frozenset({"approval/request"}),
        metadata=(MetadataField("surface", "operator_cli"),),
    )
    exec_memory = SupportExecMemoryState(
        published_memory_refs=tuple(
            SupportReference("memory", reference_id)
            for reference_id in published_memory_refs
        ),
        artifact_refs=tuple(
            SupportReference("artifact", reference_id)
            for reference_id in artifact_refs
        ),
    )
    return SupportSnapshot(
        trace=trace,
        session=session,
        host=host,
        exec_memory_pub=exec_memory,
    )


def make_aux_temporal_corpus() -> tuple[AuxTemporalScenario, ...]:
    return (
        AuxTemporalScenario(
            scenario_id="retrieval-reuse",
            source_snapshots=(
                make_temporal_support_snapshot(
                    "source-retrieval",
                    published_memory_refs=("normalize-port-memo",),
                    artifact_refs=("normalize-port-artifact",),
                ),
            ),
            target_snapshot=make_temporal_support_snapshot(
                "target-retrieval",
                candidate_refs=("normalize-port-candidate",),
                pending_goal_refs=("normalize-port-goal",),
                reminders=("normalize port before closing",),
            ),
        ),
        AuxTemporalScenario(
            scenario_id="branch-resume-recovery",
            source_snapshots=(
                make_temporal_support_snapshot(
                    "source-branch-a",
                    branch_registry=("main", "review-track"),
                    reminders=("resume review-track before closing",),
                    published_memory_refs=("review-track-memo",),
                ),
                make_temporal_support_snapshot(
                    "source-branch-b",
                    branch_registry=("main", "review-track"),
                    pending_goal_refs=("review-track-goal",),
                    published_memory_refs=("review-track-goal-memo",),
                ),
            ),
            target_snapshot=make_temporal_support_snapshot(
                "target-branch",
                candidate_refs=("review-track-candidate",),
                pending_goal_refs=("review-track-goal",),
                branch_registry=("main", "review-track"),
                reminders=("resume review-track after review",),
            ),
        ),
        AuxTemporalScenario(
            scenario_id="contradiction-review",
            source_snapshots=(
                make_temporal_support_snapshot(
                    "source-contradiction",
                    degradation_reason="host-degraded",
                    contradiction_evidence_tags=("capability-drift", "bookmark"),
                    published_memory_refs=("host-degraded-memo",),
                ),
            ),
            target_snapshot=make_temporal_support_snapshot(
                "target-contradiction",
                candidate_refs=("bookmark-review-candidate",),
                degradation_reason="host-degraded",
                contradiction_evidence_tags=("capability-drift", "review"),
            ),
        ),
        AuxTemporalScenario(
            scenario_id="uncertainty-brake-calibration",
            source_snapshots=(
                make_temporal_support_snapshot(
                    "source-uncertainty",
                    wake_reason_tags=("resume-needed",),
                    brake_history=("guarded",),
                    published_memory_refs=("guarded-review-memo",),
                ),
            ),
            target_snapshot=make_temporal_support_snapshot(
                "target-uncertainty",
                candidate_refs=("guarded-review-candidate",),
                wake_reason_tags=("resume-needed",),
                brake_history=("guarded",),
                degradation_reason="uncertain-host",
                contradiction_evidence_tags=("uncertain-host",),
            ),
        ),
        AuxTemporalScenario(
            scenario_id="no-lift-counterexample",
            source_snapshots=(
                make_temporal_support_snapshot(
                    "source-no-lift",
                    branch_registry=("main", "other-track"),
                    published_memory_refs=("totally-unrelated-memo",),
                    artifact_refs=("unrelated-artifact",),
                ),
            ),
            target_snapshot=make_temporal_support_snapshot(
                "target-no-lift",
                candidate_refs=("normalize-port-candidate",),
                pending_goal_refs=("normalize-port-goal",),
            ),
        ),
        AuxTemporalScenario(
            scenario_id="burden-heavy-counterexample",
            source_snapshots=(
                make_temporal_support_snapshot(
                    "source-burden-a",
                    branch_registry=("main", "burden-track", "burden-alt"),
                    published_memory_refs=(
                        "heavy-memory-a",
                        "heavy-memory-b",
                        "heavy-memory-c",
                    ),
                    artifact_refs=("heavy-artifact-a", "heavy-artifact-b"),
                    wake_reason_tags=("burden-reminder", "review-needed"),
                    brake_history=("guarded", "latched"),
                    degradation_reason="heavy-source-drift",
                    contradiction_evidence_tags=("burden", "drift"),
                ),
                make_temporal_support_snapshot(
                    "source-burden-b",
                    branch_registry=("main", "burden-track"),
                    published_memory_refs=("heavy-memory-d", "heavy-memory-e"),
                    artifact_refs=("heavy-artifact-c",),
                    wake_reason_tags=("burden-reminder",),
                    brake_history=("guarded",),
                ),
            ),
            target_snapshot=make_temporal_support_snapshot(
                "target-burden",
                candidate_refs=("small-fix-candidate",),
                pending_goal_refs=("small-fix-goal",),
            ),
        ),
    )


def make_aux_prune_candidate_corpus() -> tuple[AuxTemporalScenario, ...]:
    return (
        AuxTemporalScenario(
            scenario_id="prune-no-lift",
            source_snapshots=(
                make_temporal_support_snapshot(
                    "source-prune-no-lift",
                    published_memory_refs=("unrelated-memo-a", "unrelated-memo-b"),
                    artifact_refs=("unrelated-artifact-a",),
                ),
            ),
            target_snapshot=make_temporal_support_snapshot(
                "target-prune-no-lift",
                candidate_refs=("normalize-port-candidate",),
            ),
        ),
        AuxTemporalScenario(
            scenario_id="prune-burden-heavy",
            source_snapshots=(
                make_temporal_support_snapshot(
                    "source-prune-burden-a",
                    branch_registry=("main", "burden-track", "burden-alt"),
                    published_memory_refs=(
                        "unrelated-heavy-memory-a",
                        "unrelated-heavy-memory-b",
                        "unrelated-heavy-memory-c",
                    ),
                    artifact_refs=("unrelated-heavy-artifact-a", "unrelated-heavy-artifact-b"),
                    wake_reason_tags=("burden-reminder", "review-needed"),
                    brake_history=("guarded", "latched"),
                    degradation_reason="burden-source-drift",
                    contradiction_evidence_tags=("burden", "drift"),
                ),
            ),
            target_snapshot=make_temporal_support_snapshot(
                "target-prune-burden",
                candidate_refs=("small-fix-candidate",),
            ),
        ),
    )


def make_reference_executive_state(
    *,
    mode_tag: str,
    family_mask: frozenset[SoftControlFamily],
    budget_band: str,
    top_family_set: frozenset[SoftControlFamily],
    brake_state: BrakeState,
    pending_goal_refs: tuple[str, ...] = (),
    active_track_ref: str = "main",
    resume_anchor_available: bool = False,
    open_branch_count: int = 0,
    resume_anchor_quality: float = 0.0,
    merge_confidence: float = 0.0,
    host_friction_tags: frozenset[str] = frozenset(),
    feedback_pressure_tags: frozenset[str] = frozenset(),
    productive_exploration_bonus: float = 0.0,
    oscillation_penalty: float = 0.0,
    contradiction_spike_flags: frozenset[str] = frozenset(),
    uncertainty_levels: tuple[tuple[str, float], ...] = (),
) -> ReferenceExecutiveState:
    return ReferenceExecutiveState(
        goal_continuity=ReferenceGoalContinuityView(
            main_goal_ref=pending_goal_refs[0] if pending_goal_refs else None,
            active_track_ref=active_track_ref,
            pending_goal_refs=pending_goal_refs,
            resume_anchor_available=resume_anchor_available,
            open_branch_count=open_branch_count,
            resume_anchor_quality=resume_anchor_quality,
            merge_confidence=merge_confidence,
        ),
        uncertainty_monitoring=ReferenceUncertaintyMonitoringView(
            classwise_uncertainty=tuple(
                UncertaintyEstimate(class_tag=class_tag, level=level)
                for class_tag, level in uncertainty_levels
            ),
            contradiction_spike_flags=contradiction_spike_flags,
        ),
        mode_and_gating=ReferenceModeAndGatingView(
            mode_tag=mode_tag,
            family_mask=family_mask,
        ),
        control_allocation=ReferenceControlAllocationView(
            budget_band=budget_band,
            top_family_set=top_family_set,
            host_friction_tags=host_friction_tags,
            feedback_pressure_tags=feedback_pressure_tags,
            productive_exploration_bonus=productive_exploration_bonus,
            oscillation_penalty=oscillation_penalty,
        ),
        brake=ReferenceBrakeView(brake_state=brake_state),
    )


def make_aux_reference_replay_corpus() -> tuple[AuxReferenceReplayScenario, ...]:
    temporal_cases = {
        scenario.scenario_id: scenario
        for scenario in make_aux_temporal_corpus()
    }
    prune_cases = {
        scenario.scenario_id: scenario
        for scenario in make_aux_prune_candidate_corpus()
    }
    return (
        AuxReferenceReplayScenario(
            scenario_id="retrieval-reuse",
            source_snapshots=temporal_cases["retrieval-reuse"].source_snapshots,
            target_snapshot=temporal_cases["retrieval-reuse"].target_snapshot,
            executive_state=make_reference_executive_state(
                mode_tag="guarded_review",
                family_mask=frozenset(
                    {
                        SoftControlFamily.NEUTRAL,
                        SoftControlFamily.SEEK_CONTEXT,
                        SoftControlFamily.CHECK,
                        SoftControlFamily.BRAKE,
                    }
                ),
                budget_band="low",
                top_family_set=frozenset(
                    {
                        SoftControlFamily.NEUTRAL,
                        SoftControlFamily.SEEK_CONTEXT,
                    }
                ),
                brake_state=BrakeState.GUARDED,
                pending_goal_refs=("normalize-port-goal",),
                host_friction_tags=frozenset({"single-process-limit"}),
                uncertainty_levels=(
                    ("environment", 0.25),
                    ("goal-progress", 0.20),
                ),
            ),
            preferred_family=SoftControlFamily.SEEK_CONTEXT,
            expect_improvement=True,
            notes=("retrieval reuse should lift seek-context without changing commitment truth",),
        ),
        AuxReferenceReplayScenario(
            scenario_id="branch-resume-recovery",
            source_snapshots=temporal_cases["branch-resume-recovery"].source_snapshots,
            target_snapshot=temporal_cases["branch-resume-recovery"].target_snapshot,
            executive_state=make_reference_executive_state(
                mode_tag="review_pending",
                family_mask=frozenset(
                    {
                        SoftControlFamily.NEUTRAL,
                        SoftControlFamily.BRANCH,
                        SoftControlFamily.CHECK,
                        SoftControlFamily.REDIRECT,
                    }
                ),
                budget_band="low",
                top_family_set=frozenset(
                    {
                        SoftControlFamily.NEUTRAL,
                        SoftControlFamily.BRANCH,
                    }
                ),
                brake_state=BrakeState.GUARDED,
                pending_goal_refs=("review-track-goal",),
                active_track_ref="review-track",
                resume_anchor_available=True,
                open_branch_count=1,
                resume_anchor_quality=0.85,
                merge_confidence=0.70,
                host_friction_tags=frozenset({"single-process-limit"}),
                uncertainty_levels=(
                    ("goal-progress", 0.20),
                    ("environment", 0.30),
                ),
            ),
            preferred_family=SoftControlFamily.BRANCH,
            expect_improvement=True,
            notes=("branch continuity should gain from explicit replay priors",),
        ),
        AuxReferenceReplayScenario(
            scenario_id="contradiction-review",
            source_snapshots=(
                make_temporal_support_snapshot(
                    "source-contradiction-replay",
                    degradation_reason="host-degraded",
                    contradiction_evidence_tags=("capability-drift", "review"),
                    published_memory_refs=("host-degraded-memo",),
                    wake_reason_tags=("resume-needed",),
                    brake_history=("guarded",),
                ),
            ),
            target_snapshot=temporal_cases["contradiction-review"].target_snapshot,
            executive_state=make_reference_executive_state(
                mode_tag="review_pending",
                family_mask=frozenset(
                    {
                        SoftControlFamily.NEUTRAL,
                        SoftControlFamily.CHECK,
                        SoftControlFamily.BRAKE,
                    }
                ),
                budget_band="high",
                top_family_set=frozenset(
                    {
                        SoftControlFamily.NEUTRAL,
                        SoftControlFamily.CHECK,
                    }
                ),
                brake_state=BrakeState.GUARDED,
                contradiction_spike_flags=frozenset({"host-degraded"}),
                uncertainty_levels=(
                    ("evidence", 0.60),
                    ("environment", 0.35),
                ),
            ),
            preferred_family=SoftControlFamily.CHECK,
            expect_improvement=True,
            notes=("contradiction summaries should lift verification selection",),
        ),
        AuxReferenceReplayScenario(
            scenario_id="uncertainty-brake-calibration",
            source_snapshots=temporal_cases["uncertainty-brake-calibration"].source_snapshots,
            target_snapshot=temporal_cases["uncertainty-brake-calibration"].target_snapshot,
            executive_state=make_reference_executive_state(
                mode_tag="pass_through",
                family_mask=frozenset(
                    {
                        SoftControlFamily.NEUTRAL,
                        SoftControlFamily.BRAKE,
                        SoftControlFamily.CHECK,
                        SoftControlFamily.SEEK_CONTEXT,
                    }
                ),
                budget_band="high",
                top_family_set=frozenset(
                    {
                        SoftControlFamily.NEUTRAL,
                        SoftControlFamily.BRAKE,
                    }
                ),
                brake_state=BrakeState.GUARDED,
                contradiction_spike_flags=frozenset({"uncertain-host"}),
                uncertainty_levels=(
                    ("environment", 0.62),
                    ("host-capability", 0.30),
                ),
            ),
            preferred_family=SoftControlFamily.BRAKE,
            expect_improvement=True,
            notes=("uncertainty calibration should strengthen brake allocation",),
        ),
        AuxReferenceReplayScenario(
            scenario_id="no-lift-counterexample",
            source_snapshots=temporal_cases["no-lift-counterexample"].source_snapshots,
            target_snapshot=temporal_cases["no-lift-counterexample"].target_snapshot,
            executive_state=make_reference_executive_state(
                mode_tag="pass_through",
                family_mask=frozenset(
                    {
                        SoftControlFamily.NEUTRAL,
                        SoftControlFamily.BRANCH,
                        SoftControlFamily.CHECK,
                    }
                ),
                budget_band="medium",
                top_family_set=frozenset(
                    {
                        SoftControlFamily.NEUTRAL,
                        SoftControlFamily.BRANCH,
                    }
                ),
                brake_state=BrakeState.QUIESCENT,
                pending_goal_refs=("normalize-port-goal",),
                uncertainty_levels=(("goal-progress", 0.10),),
            ),
            preferred_family=SoftControlFamily.SEEK_CONTEXT,
            expect_improvement=False,
            notes=("calm reference state should ignore replay priors",),
        ),
        AuxReferenceReplayScenario(
            scenario_id="burden-heavy-counterexample",
            source_snapshots=temporal_cases["burden-heavy-counterexample"].source_snapshots,
            target_snapshot=temporal_cases["burden-heavy-counterexample"].target_snapshot,
            executive_state=make_reference_executive_state(
                mode_tag="pass_through",
                family_mask=frozenset(
                    {
                        SoftControlFamily.NEUTRAL,
                        SoftControlFamily.CHECK,
                        SoftControlFamily.BRANCH,
                    }
                ),
                budget_band="medium",
                top_family_set=frozenset(
                    {
                        SoftControlFamily.NEUTRAL,
                        SoftControlFamily.CHECK,
                    }
                ),
                brake_state=BrakeState.QUIESCENT,
                pending_goal_refs=("small-fix-goal",),
                uncertainty_levels=(("goal-progress", 0.15),),
            ),
            preferred_family=SoftControlFamily.CHECK,
            expect_improvement=False,
            notes=("burden-heavy replay should not count as lawful control lift",),
        ),
        AuxReferenceReplayScenario(
            scenario_id="prune-no-lift",
            source_snapshots=prune_cases["prune-no-lift"].source_snapshots,
            target_snapshot=prune_cases["prune-no-lift"].target_snapshot,
            executive_state=make_reference_executive_state(
                mode_tag="guarded_review",
                family_mask=frozenset(
                    {
                        SoftControlFamily.NEUTRAL,
                        SoftControlFamily.SEEK_CONTEXT,
                        SoftControlFamily.CHECK,
                    }
                ),
                budget_band="low",
                top_family_set=frozenset(
                    {
                        SoftControlFamily.NEUTRAL,
                        SoftControlFamily.SEEK_CONTEXT,
                    }
                ),
                brake_state=BrakeState.GUARDED,
                host_friction_tags=frozenset({"single-process-limit"}),
                uncertainty_levels=(("goal-progress", 0.18),),
            ),
            preferred_family=SoftControlFamily.SEEK_CONTEXT,
            expect_improvement=False,
            notes=("prune-no-lift should stay neutral even on the reference replay seam",),
        ),
        AuxReferenceReplayScenario(
            scenario_id="prune-burden-heavy",
            source_snapshots=prune_cases["prune-burden-heavy"].source_snapshots,
            target_snapshot=prune_cases["prune-burden-heavy"].target_snapshot,
            executive_state=make_reference_executive_state(
                mode_tag="pass_through",
                family_mask=frozenset(
                    {
                        SoftControlFamily.NEUTRAL,
                        SoftControlFamily.CHECK,
                        SoftControlFamily.BRANCH,
                    }
                ),
                budget_band="medium",
                top_family_set=frozenset(
                    {
                        SoftControlFamily.NEUTRAL,
                        SoftControlFamily.CHECK,
                    }
                ),
                brake_state=BrakeState.GUARDED,
                host_friction_tags=frozenset({"single-process-limit"}),
                uncertainty_levels=(("goal-progress", 0.20),),
            ),
            preferred_family=SoftControlFamily.CHECK,
            expect_improvement=False,
            notes=("prune-burden-heavy should not create verification lift under burden penalties",),
        ),
    )
