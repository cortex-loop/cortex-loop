"""Readiness scenarios for the seam-5 silent-control live probe.

These tests do not add runtime behavior. They pin the current composed
ledger -> deficit -> debt-control -> route/brake behavior so the phase-5
readiness document can distinguish proven safety from gaps that would make
live trials noisy.
"""

from __future__ import annotations

from cortex.core.dispatch import DispatchDecision, DispatchLane, EvidencePlan, WakeDecision
from cortex.hosts.reference.runtime import ReferenceRuntimeSession, run_reference_runtime_step
from cortex.sre.brake import BrakeState, evaluate_brake_state
from cortex.sre.debt_control import build_runtime_debt_control_pressure
from cortex.sre.expectations import (
    ExpectationLedger,
    ForwardCommitment,
    compute_resolution_deficit,
    expectation_record_for_forward_commitment,
    open_expectation_from_forward_commitment,
    update_expectation_ledger_for_structured_step,
)
from cortex.sre.uncertainty import UncertaintyEstimate


def test_horizon_boundary_table_documents_current_structural_coverage() -> None:
    """Structured cue coverage is accurate, but thin for deferred/waiting edges."""

    direct_cases = (
        ("completion", _commitment("completion", "high"), "immediate"),
        ("verification", _commitment("verification", "high"), "immediate"),
        ("artifact", _commitment("artifact_change", "high"), "next_step"),
        ("plan", _commitment("plan_commitment", "medium"), "next_step"),
        ("capability", _commitment("capability_claim", "medium"), "next_step"),
        ("deferred-followup", _commitment("deferred_followup", "high"), "deferred"),
        ("high-diagnosis", _commitment("diagnosis", "high"), "deferred"),
        ("low-diagnosis", _commitment("diagnosis", "low"), None),
    )
    observed = {}
    for name, commitment, expected_horizon in direct_cases:
        record = expectation_record_for_forward_commitment(commitment)
        observed[name] = record.horizon if record is not None else None
        assert observed[name] == expected_horizon

    waiting = update_expectation_ledger_for_structured_step(
        ledger=ExpectationLedger(),
        dispatch_decision=_dispatch(
            DispatchLane.CANDIDATE_BEARING,
            reason_tags=("proposal-surface", "candidate-present"),
        ),
        current_step=1,
        source_event_ref="event:waiting",
        evidence_progress_class="candidate",
        continuity_progress_class="none",
        commitment_result_kind=None,
        warning_codes=("approval-required",),
    )

    assert waiting.active[0].horizon == "next_step"
    assert waiting.active[0].suspension_state == "waiting_on_user"
    assert compute_resolution_deficit(waiting, current_step=10).negative_prediction_error == 0.0


def test_mixed_horizon_sequence_targets_current_certification_before_old_debt() -> None:
    """Mixed old debt plus new certified work resolves the current event first."""

    session = ReferenceRuntimeSession(
        session_id="phase5-readiness-mixed",
        pending_goal_refs=("goal-open",),
    )
    unpaid = run_reference_runtime_step(
        "ApprovalResult",
        {
            "session_id": "phase5-readiness-mixed",
            "commitment_id": "verify-1",
            "externally_consequential": True,
        },
        session,
    )
    candidate = run_reference_runtime_step(
        "ApprovalRequest",
        {
            "session_id": "phase5-readiness-mixed",
            "candidate_id": "candidate-1",
        },
        unpaid.session,
    )
    inspect = run_reference_runtime_step(
        "ContextLoad",
        {
            "session_id": "phase5-readiness-mixed",
            "delta": "inspection without verification",
        },
        candidate.session,
    )
    certified = run_reference_runtime_step(
        "ApprovalResult",
        {
            "session_id": "phase5-readiness-mixed",
            "commitment_id": "verify-2",
            "externally_consequential": True,
            "result_artifact_ref": "artifact-1",
        },
        inspect.session,
    )

    assert unpaid.resolution_deficit_payload["negative_prediction_error"] == 1.0
    assert candidate.debt_control_payload["goal_drag"] > 0.0
    assert candidate.operator_route_payload["route_profile"] == "continuity_guarded"
    assert candidate.operator_route_payload["blocked_reason"] is None
    assert inspect.operator_route_payload["blocked_reason"] is None

    # Explicit current-event certification resolves the expectation opened by
    # the same event before generic progress pays older compatible debt. Older
    # unresolved plan debt may remain active, but the certified event no longer
    # creates fresh verification noise for seam 5.
    assert {record.resolution_class for record in certified.session.expectation_ledger.resolved} == {
        "commitment_certified",
        "meaningful_evidence",
    }
    assert len(certified.session.expectation_ledger.active) == 1
    assert certified.session.expectation_ledger.active[0].opened_at_step < certified.event_index
    assert certified.session.expectation_ledger.active[0].deficit_kind == "preservation"
    assert all(
        record.opened_at_step != certified.event_index
        for record in certified.session.expectation_ledger.active
    )
    assert any(
        record.opened_at_step == certified.event_index
        and record.deficit_kind == "verification"
        and record.resolution_class == "commitment_certified"
        for record in certified.session.expectation_ledger.resolved
    )
    assert certified.resolution_deficit_payload["negative_prediction_error"] == 1.0


def test_waiting_boundary_relieves_blocker_without_residual_current_debt() -> None:
    """Pure waiting suspends debt and runtime blockers leave no residual current debt."""

    pure_waiting = update_expectation_ledger_for_structured_step(
        ledger=ExpectationLedger(),
        dispatch_decision=_dispatch(
            DispatchLane.CANDIDATE_BEARING,
            reason_tags=("proposal-surface", "candidate-present"),
        ),
        current_step=1,
        source_event_ref="event:pure-wait",
        evidence_progress_class="candidate",
        continuity_progress_class="none",
        commitment_result_kind=None,
        warning_codes=("approval-required",),
    )

    assert pure_waiting.active[0].suspension_state == "waiting_on_user"
    assert compute_resolution_deficit(pure_waiting, current_step=20).negative_prediction_error == 0.0

    approval = run_reference_runtime_step(
        "ApprovalRequest",
        {"session_id": "phase5-readiness-wait", "candidate_id": "candidate-1"},
        ReferenceRuntimeSession(session_id="phase5-readiness-wait"),
    )
    blocked = run_reference_runtime_step(
        "ApprovalResult",
        {
            "session_id": "phase5-readiness-wait",
            "commitment_id": "candidate-1",
            "externally_consequential": True,
            "boundary_blocked": True,
            "boundary_reason_code": "approval-required",
        },
        approval.session,
    )
    still_waiting = run_reference_runtime_step(
        "ContextLoad",
        {
            "session_id": "phase5-readiness-wait",
            "delta": "still waiting for the user",
        },
        blocked.session,
    )

    assert blocked.session.expectation_ledger.active == ()
    assert {
        record.resolution_class for record in blocked.session.expectation_ledger.resolved
    } == {"blocker_surfaced", "meaningful_evidence"}
    assert any(
        record.opened_at_step == blocked.event_index
        and record.deficit_kind == "verification"
        and record.resolution_class == "blocker_surfaced"
        and record.remaining_weight == 0.0
        for record in blocked.session.expectation_ledger.resolved
    )
    assert still_waiting.debt_control_payload["debt_pressure"] == 0.0
    assert still_waiting.operator_route_payload["route_profile"] == "inspect_light"
    assert still_waiting.operator_route_payload["blocked_reason"] is None


def test_debt_plus_phasic_spike_latches_only_on_phasic_cause() -> None:
    ledger = open_expectation_from_forward_commitment(
        ExpectationLedger(),
        _commitment("verification", "high", opened_at_step=0),
    )
    pressure = build_runtime_debt_control_pressure(
        resolution_deficit=compute_resolution_deficit(ledger, current_step=1),
        task_mode="execute",
        active_track_ref="main",
        pending_goal_refs=("goal-open",),
        continuity_warnings=(),
        continuity_reminders=(),
        degradation_pressure_bonus=0,
        sustained_spike_flags=(),
    )

    debt_only = evaluate_brake_state((), debt_control_pressure=pressure)
    phasic_plus_debt = evaluate_brake_state(
        (
            UncertaintyEstimate(
                class_tag="evidence",
                level=0.2,
                spike_tags=frozenset({"contradiction-expected-vs-observed"}),
            ),
        ),
        debt_control_pressure=pressure,
    )

    assert debt_only.state is BrakeState.GUARDED
    assert debt_only.dominant_cause == "resolution-deficit"
    assert phasic_plus_debt.state is BrakeState.LATCHED
    assert phasic_plus_debt.dominant_cause == "contradiction-expected-vs-observed"


def test_runtime_diagnostics_support_stepwise_trajectory_reconstruction() -> None:
    first = run_reference_runtime_step(
        "ApprovalResult",
        {
            "session_id": "phase5-readiness-diagnostics",
            "commitment_id": "verify-1",
            "externally_consequential": True,
        },
        ReferenceRuntimeSession(session_id="phase5-readiness-diagnostics"),
    )
    second = run_reference_runtime_step(
        "ApprovalRequest",
        {
            "session_id": "phase5-readiness-diagnostics",
            "candidate_id": "candidate-1",
        },
        first.session,
    )

    trajectory = [_trajectory_row(first), _trajectory_row(second)]

    assert trajectory[0]["post_step_deficit"]["negative_prediction_error"] == 1.0
    assert trajectory[0]["current_decision_debt"]["debt_pressure"] == 0.0
    assert trajectory[1]["current_decision_debt"]["debt_pressure"] > 0.0
    assert trajectory[1]["route"]["route_profile"] == "execute_guarded"
    assert trajectory[1]["allocation_debt"] == trajectory[1]["current_decision_debt"]
    assert "expectation_ledger" in trajectory[1]["session"]


def _trajectory_row(result) -> dict[str, object]:
    return {
        "event_index": result.event_index,
        "session": result.session_summary,
        "post_step_deficit": result.resolution_deficit_payload,
        "current_decision_debt": result.debt_control_payload,
        "route": result.operator_route_payload,
        "policy": result.executive_policy_view_payload,
        "allocation_debt": result.control_ledger_summary["allocation_diagnostics"][
            "debt_control"
        ],
    }


def _commitment(
    kind: str,
    assertiveness: str,
    *,
    opened_at_step: int = 1,
) -> ForwardCommitment:
    return ForwardCommitment(
        commitment_id=f"commit:{kind}:{assertiveness}:{opened_at_step}",
        source_event_ref=f"event:{opened_at_step}",
        claim_span_ref=f"event:{opened_at_step}:structured-cue",
        commitment_kind=kind,
        assertiveness=assertiveness,
        scope="task",
        opened_at_step=opened_at_step,
    )


def _dispatch(
    lane: DispatchLane,
    *,
    reason_tags: tuple[str, ...] = (),
) -> DispatchDecision:
    return DispatchDecision(
        lane=lane,
        wake_decision=WakeDecision(
            full_commitment_required=lane is DispatchLane.FULL_COMMITMENT,
            reason_tags=frozenset(reason_tags),
        ),
        evidence_plan=EvidencePlan(
            requires_candidate_extraction=lane is not DispatchLane.CHEAP,
            requires_provenance=lane is DispatchLane.FULL_COMMITMENT,
            requires_boundary_assessment=lane is DispatchLane.FULL_COMMITMENT,
        ),
        candidate_present=lane is not DispatchLane.CHEAP,
    )
