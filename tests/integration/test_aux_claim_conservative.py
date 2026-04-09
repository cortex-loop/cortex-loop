"""Integration tests for AUX claim-conservative enforcement."""

from __future__ import annotations

import inspect

from cortex.aux.augmentation import AugmentedSupportSnapshot, AuxiliarySupportAppendix, augment_snapshot
from cortex.aux.cost import AuxBurdenReport
from cortex.core.commitments import (
    BoundaryAssessment,
    CommitmentStatus,
)
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
from experimental.drivers.reference_host_commitment import (
    ReferenceHostCommitmentResult,
    evaluate_reference_host_commitment,
)
from tests.integration._reference_lane import (
    assert_reference_verdict_status,
    assert_same_verdict,
    candidate_bearing_event,
    evaluate_reference_full_commitment_case,
    reference_environment_handle,
)


def test_certified_outcome_is_unchanged_by_aux_augmentation_and_burden_presence() -> None:
    baseline = evaluate_reference_full_commitment_case(
        commitment_id="commit-aux-certified",
        provenance_reference_id="artifact-certified",
    )
    augmented_snapshot, burden = _build_aux_scaffolds(baseline)
    with_aux_present = evaluate_reference_full_commitment_case(
        commitment_id="commit-aux-certified",
        provenance_reference_id="artifact-certified",
    )

    assert_reference_verdict_status(baseline, CommitmentStatus.CERTIFIED)
    assert_same_verdict(baseline, with_aux_present)
    assert isinstance(augmented_snapshot, AugmentedSupportSnapshot)
    assert burden.environment_query_cost == 1.0


def test_blocked_outcome_is_unchanged_by_aux_augmentation_and_burden_presence() -> None:
    blocked_boundary = BoundaryAssessment(
        blocked=True,
        reason_code="approval-required",
        boundary_tags=frozenset({"external-boundary"}),
    )
    baseline = evaluate_reference_full_commitment_case(
        commitment_id="commit-aux-blocked",
        provenance_reference_id="artifact-blocked",
        boundary_assessment=blocked_boundary,
    )
    augmented_snapshot, burden = _build_aux_scaffolds(baseline)
    with_aux_present = evaluate_reference_full_commitment_case(
        commitment_id="commit-aux-blocked",
        provenance_reference_id="artifact-blocked",
        boundary_assessment=blocked_boundary,
    )

    assert_reference_verdict_status(baseline, CommitmentStatus.BLOCKED)
    assert_same_verdict(baseline, with_aux_present)
    assert augmented_snapshot.auxiliary_support.notes == ("aux scaffold present",)
    assert burden.compute_overhead == 1.0


def test_uncertified_outcome_is_unchanged_by_aux_augmentation_and_burden_presence() -> None:
    baseline = evaluate_reference_full_commitment_case(
        commitment_id="commit-aux-uncertified",
    )
    augmented_snapshot, burden = _build_aux_scaffolds(baseline)
    with_aux_present = evaluate_reference_full_commitment_case(
        commitment_id="commit-aux-uncertified",
    )

    assert_reference_verdict_status(baseline, CommitmentStatus.UNCERTIFIED)
    assert_same_verdict(baseline, with_aux_present)
    assert augmented_snapshot.core_snapshot.trace.candidate_refs == ("commit-aux-uncertified",)
    assert burden.intervention_burden == 0.5


def test_aux_objects_remain_support_side_and_do_not_enter_commitment_apis() -> None:
    parameters = inspect.signature(evaluate_reference_host_commitment).parameters
    event_name, payload = candidate_bearing_event(
        candidate_id="candidate-aux-support",
    )
    result = evaluate_reference_host_commitment(
        event_name,
        payload,
        environment_handle=reference_environment_handle(),
    )
    augmented_snapshot, burden = _build_aux_scaffolds(result)

    assert "auxiliary_support" not in parameters
    assert "aux_burden" not in parameters
    assert result.verdict is None
    assert isinstance(augmented_snapshot, AugmentedSupportSnapshot)
    assert isinstance(burden, AuxBurdenReport)


def _build_aux_scaffolds(
    result: ReferenceHostCommitmentResult,
) -> tuple[AugmentedSupportSnapshot, AuxBurdenReport]:
    event = result.bound_event.observation.event
    candidate_refs = (result.candidate.candidate_id,) if result.candidate is not None else ()
    wake_receipts = tuple(
        WakeReceipt(reason_tag=tag, event_name=event.native_event_name)
        for tag in sorted(result.dispatch_decision.wake_decision.reason_tags)
    )
    artifact_refs = ()
    if result.verdict is not None and result.verdict.provenance_manifest is not None:
        artifact_refs = tuple(
            SupportReference("provenance", ref.reference_id)
            for ref in result.verdict.provenance_manifest.evidence_refs
        )

    snapshot = SupportSnapshot(
        trace=SupportTraceState(
            recent_events=(event,),
            candidate_refs=candidate_refs,
            wake_receipts=wake_receipts,
            degradation_records=result.verdict.degradation_refs if result.verdict is not None else (),
        ),
        session=SupportSessionState(
            pending_goal_refs=("goal-aux-check",),
            role_view_tags=frozenset({"aux/removable"}),
            wake_counters=(SupportCounter("wake-receipts", len(wake_receipts)),),
        ),
        host=SupportHostState(
            affordance_tags=result.bound_event.lifecycle_surface.tool_affordances,
            approval_boundary_tags=frozenset(
                tag for tag in event.facet_tags if tag.startswith("approval/")
            ),
        ),
        exec_memory_pub=SupportExecMemoryState(
            artifact_refs=artifact_refs,
        ),
    )
    appendix = AuxiliarySupportAppendix(
        derived_support_refs=(
            SupportReference(
                "adjunct",
                f"aux-{candidate_refs[0] if candidate_refs else event.native_event_name}",
            ),
        ),
        derived_tags=frozenset({"aux/claim-conservative"}),
        notes=("aux scaffold present",),
    )
    burden = AuxBurdenReport(
        compute_overhead=1.0,
        environment_query_cost=1.0,
        intervention_burden=0.5,
    )
    return augment_snapshot(snapshot, appendix), burden
