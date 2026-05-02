"""Falsification corpus for bounded runtime expectation debt."""

from __future__ import annotations

from dataclasses import dataclass

from cortex.core.commitments import CommitmentStatus
from cortex.core.dispatch import DispatchDecision, DispatchLane, EvidencePlan, WakeDecision
from cortex.sre.expectations import (
    EvidenceProgress,
    ExpectationLedger,
    ForwardCommitment,
    compute_resolution_deficit,
    expectation_record_for_forward_commitment,
    update_expectation_ledger_for_structured_step,
)


@dataclass(frozen=True, slots=True)
class StructuredStepCase:
    name: str
    dispatch: DispatchDecision
    evidence_progress_class: str | None = None
    continuity_progress_class: str | None = "none"
    commitment_result_kind: str | None = None
    warning_codes: tuple[str, ...] = ()
    task_mode: str = "execute"


def test_forward_motion_corpus_opens_expected_debt_without_prose_claims() -> None:
    cases = (
        (
            "false completion",
            StructuredStepCase(
                name="false completion",
                dispatch=_dispatch(
                    DispatchLane.FULL_COMMITMENT,
                    reason_tags=("explicit-completion-claim",),
                ),
            ),
            "completion",
            "immediate",
            1.0,
            1.0,
        ),
        (
            "unsupported verification",
            StructuredStepCase(
                name="unsupported verification",
                dispatch=_dispatch(
                    DispatchLane.FULL_COMMITMENT,
                    reason_tags=("commitment-subset",),
                ),
            ),
            "verification",
            "immediate",
            1.0,
            1.0,
        ),
        (
            "candidate plan",
            StructuredStepCase(
                name="candidate plan",
                dispatch=_dispatch(
                    DispatchLane.CANDIDATE_BEARING,
                    reason_tags=("proposal-surface", "candidate-present"),
                ),
                evidence_progress_class="candidate",
            ),
            "preservation",
            "next_step",
            0.0,
            1.0,
        ),
        (
            "durable write intent",
            StructuredStepCase(
                name="durable write intent",
                dispatch=_dispatch(
                    DispatchLane.FULL_COMMITMENT,
                    reason_tags=("durable-write",),
                ),
            ),
            "preservation",
            "next_step",
            0.0,
            1.0,
        ),
    )

    for name, case, expected_kind, expected_horizon, expected_open_deficit, expected_next_deficit in cases:
        ledger = _run_case(case)

        assert len(ledger.active) == 1, name
        assert ledger.active[0].deficit_kind == expected_kind
        assert ledger.active[0].horizon == expected_horizon
        assert (
            compute_resolution_deficit(ledger, current_step=1).negative_prediction_error
            == expected_open_deficit
        )
        assert (
            compute_resolution_deficit(ledger, current_step=2).negative_prediction_error
            == expected_next_deficit
        )


def test_commitment_status_corpus_distinguishes_certified_uncertified_and_blocked() -> None:
    uncertified = _run_case(
        StructuredStepCase(
            name="uncertified",
            dispatch=_dispatch(DispatchLane.FULL_COMMITMENT, reason_tags=("commitment-subset",)),
            evidence_progress_class="commitment",
            commitment_result_kind=CommitmentStatus.UNCERTIFIED.value,
        )
    )
    certified = _run_case(
        StructuredStepCase(
            name="certified",
            dispatch=_dispatch(DispatchLane.FULL_COMMITMENT, reason_tags=("commitment-subset",)),
            evidence_progress_class="commitment",
            commitment_result_kind=CommitmentStatus.CERTIFIED.value,
        )
    )
    blocked = _run_case(
        StructuredStepCase(
            name="blocked",
            dispatch=_dispatch(DispatchLane.FULL_COMMITMENT, reason_tags=("commitment-subset",)),
            evidence_progress_class="commitment",
            commitment_result_kind=CommitmentStatus.BLOCKED.value,
        )
    )

    assert uncertified.active[0].remaining_weight == 1.0
    assert compute_resolution_deficit(uncertified, current_step=1).negative_prediction_error == 1.0
    assert certified.active == ()
    assert certified.resolved[0].resolution_class == "commitment_certified"
    assert blocked.active == ()
    assert blocked.resolved[0].resolution_class == "blocker_surfaced"
    assert compute_resolution_deficit(blocked, current_step=1).relief_weight == 1.0


def test_paydown_corpus_accepts_only_compatible_generic_progress_classes() -> None:
    for progress_class in ("meaningful_evidence", "liability_retracted", "blocker_surfaced"):
        ledger = _verification_ledger().apply_progress(
            EvidenceProgress(progress_class, f"event:{progress_class}", weight=1.0),
            current_step=1,
        )

        assert ledger.active == (), progress_class
        assert ledger.resolved[0].resolution_class == progress_class

    continuity = _plan_ledger().apply_progress(
        EvidenceProgress("continuity_progress", "event:continuity", weight=1.0),
        current_step=2,
    )

    assert continuity.active == ()
    assert continuity.resolved[0].resolution_class == "continuity_progress"


def test_waiting_and_deferred_corpus_do_not_turn_incomplete_work_into_false_debt() -> None:
    waiting = _run_case(
        StructuredStepCase(
            name="waiting on user",
            dispatch=_dispatch(
                DispatchLane.CANDIDATE_BEARING,
                reason_tags=("proposal-surface", "candidate-present"),
            ),
            evidence_progress_class="candidate",
            warning_codes=("approval-required",),
        )
    )
    released_deferred = _deferred_followup_ledger().apply_progress(
        EvidenceProgress("waiting_released", "event:user-returned", weight=1.0),
        current_step=4,
    )

    assert waiting.active[0].suspension_state == "waiting_on_user"
    assert compute_resolution_deficit(waiting, current_step=10).due_weight == 0.0
    assert compute_resolution_deficit(waiting, current_step=10).suspended_weight == 0.6
    assert compute_resolution_deficit(waiting, current_step=10).negative_prediction_error == 0.0
    assert released_deferred.active == ()
    assert released_deferred.resolved[0].resolution_class == "waiting_released"


def test_stream_only_hook_success_and_low_confidence_diagnosis_do_not_pay_or_create_debt() -> None:
    stream_only = _verification_ledger().apply_progress(
        EvidenceProgress("stream_only", "event:stream", weight=1.0),
        current_step=1,
    )
    hook_success = update_expectation_ledger_for_structured_step(
        ledger=_verification_ledger(),
        dispatch_decision=_dispatch(DispatchLane.CHEAP),
        current_step=1,
        source_event_ref="event:hook-success",
        evidence_progress_class=None,
        continuity_progress_class="none",
        commitment_result_kind=None,
        warning_codes=("hook-success",),
    )
    low_diagnosis = ExpectationLedger()
    record = expectation_record_for_forward_commitment(
        ForwardCommitment(
            commitment_id="commit:diagnosis",
            source_event_ref="event:diagnosis",
            claim_span_ref="event:diagnosis:structured-cue",
            commitment_kind="diagnosis",
            assertiveness="low",
            scope="task",
            opened_at_step=1,
        )
    )

    assert stream_only == _verification_ledger()
    assert hook_success == _verification_ledger()
    assert record is None
    assert low_diagnosis == ExpectationLedger()


def test_capability_claim_carrier_is_bounded_but_runtime_producer_is_unearned() -> None:
    ledger = _capability_claim_ledger()

    assert ledger.active[0].deficit_kind == "capability"
    assert ledger.active[0].horizon == "next_step"
    assert ledger.active[0].weight == 0.6
    assert compute_resolution_deficit(ledger, current_step=1).negative_prediction_error == 0.0
    assert compute_resolution_deficit(ledger, current_step=2).negative_prediction_error == 1.0


def test_clean_structured_controls_leave_the_ledger_empty() -> None:
    clean = _run_case(
        StructuredStepCase(
            name="clean",
            dispatch=_dispatch(DispatchLane.CHEAP),
            task_mode="inspect",
        )
    )

    assert clean == ExpectationLedger()
    assert compute_resolution_deficit(clean, current_step=1).negative_prediction_error == 0.0


def _run_case(case: StructuredStepCase) -> ExpectationLedger:
    return update_expectation_ledger_for_structured_step(
        ledger=ExpectationLedger(),
        dispatch_decision=case.dispatch,
        current_step=1,
        source_event_ref=f"event:{case.name.replace(' ', '-')}",
        evidence_progress_class=case.evidence_progress_class,
        continuity_progress_class=case.continuity_progress_class,
        commitment_result_kind=case.commitment_result_kind,
        task_mode=case.task_mode,
        warning_codes=case.warning_codes,
    )


def _verification_ledger() -> ExpectationLedger:
    return update_expectation_ledger_for_structured_step(
        ledger=ExpectationLedger(),
        dispatch_decision=_dispatch(
            DispatchLane.FULL_COMMITMENT,
            reason_tags=("commitment-subset",),
        ),
        current_step=1,
        source_event_ref="event:verification",
        evidence_progress_class=None,
        continuity_progress_class="none",
        commitment_result_kind=None,
        task_mode="execute",
    )


def _plan_ledger() -> ExpectationLedger:
    return update_expectation_ledger_for_structured_step(
        ledger=ExpectationLedger(),
        dispatch_decision=_dispatch(
            DispatchLane.CANDIDATE_BEARING,
            reason_tags=("proposal-surface", "candidate-present"),
        ),
        current_step=1,
        source_event_ref="event:plan",
        evidence_progress_class=None,
        continuity_progress_class="none",
        commitment_result_kind=None,
        task_mode="execute",
    )


def _deferred_followup_ledger() -> ExpectationLedger:
    return ExpectationLedger().open_expectation(
        expectation_record_for_forward_commitment(
            ForwardCommitment(
                commitment_id="commit:deferred",
                source_event_ref="event:deferred",
                claim_span_ref="event:deferred:structured-cue",
                commitment_kind="deferred_followup",
                assertiveness="high",
                scope="task",
                opened_at_step=1,
            )
        )
    )


def _capability_claim_ledger() -> ExpectationLedger:
    return ExpectationLedger().open_expectation(
        expectation_record_for_forward_commitment(
            ForwardCommitment(
                commitment_id="commit:capability",
                source_event_ref="event:capability",
                claim_span_ref="event:capability:structured-cue",
                commitment_kind="capability_claim",
                assertiveness="medium",
                scope="task",
                opened_at_step=1,
            )
        )
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
