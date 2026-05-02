"""Product tests for bounded runtime expectation-debt state."""

from __future__ import annotations

from cortex.sre.expectations import (
    EvidenceProgress,
    ExpectationLedger,
    ForwardCommitment,
    compute_resolution_deficit,
    expectation_record_for_forward_commitment,
    open_expectation_from_forward_commitment,
)


def test_completion_and_verification_commitments_open_immediate_expectations() -> None:
    for kind, expected_deficit_kind in (
        ("completion", "completion"),
        ("verification", "verification"),
    ):
        commitment = _commitment(kind=kind, assertiveness="high")
        record = expectation_record_for_forward_commitment(commitment)

        assert record is not None
        assert record.horizon == "immediate"
        assert record.weight == 1.0
        assert record.due_at_step == commitment.opened_at_step
        assert record.deficit_kind == expected_deficit_kind


def test_candidate_movement_opens_next_step_expectation_and_later_deficit() -> None:
    ledger = open_expectation_from_forward_commitment(
        ExpectationLedger(),
        _commitment(kind="plan_commitment", assertiveness="medium"),
    )

    at_open = compute_resolution_deficit(ledger, current_step=1)
    later = compute_resolution_deficit(ledger, current_step=2)

    assert at_open.negative_prediction_error == 0.0
    assert later.due_weight == 0.6
    assert later.negative_prediction_error == 1.0
    assert later.dominant_deficit_kind == "preservation"


def test_meaningful_evidence_and_certification_pay_down_debt() -> None:
    ledger = open_expectation_from_forward_commitment(
        ExpectationLedger(),
        _commitment(kind="verification", assertiveness="high"),
    )
    paid = ledger.apply_progress(
        EvidenceProgress("commitment_certified", "event:certified", weight=1.0),
        current_step=1,
    )

    assert paid.active == ()
    assert paid.resolved[0].suspension_state == "fulfilled"
    assert paid.resolved[0].resolution_class == "commitment_certified"
    assert compute_resolution_deficit(paid, current_step=1).negative_prediction_error == 0.0


def test_retraction_blocker_and_user_wait_release_pay_down_without_false_debt() -> None:
    ledger = open_expectation_from_forward_commitment(
        ExpectationLedger(),
        _commitment(kind="completion", assertiveness="high"),
    )
    retracted = ledger.apply_progress(
        EvidenceProgress("liability_retracted", "event:retract", weight=1.0),
        current_step=1,
    )

    assert retracted.active == ()
    assert retracted.resolved[0].resolution_class == "liability_retracted"
    assert compute_resolution_deficit(retracted, current_step=1).relief_weight == 1.0
    assert compute_resolution_deficit(retracted, current_step=1).negative_prediction_error == 0.0


def test_stream_only_output_does_not_pay_verification_debt() -> None:
    ledger = open_expectation_from_forward_commitment(
        ExpectationLedger(),
        _commitment(kind="verification", assertiveness="high"),
    )
    unchanged = ledger.apply_progress(
        EvidenceProgress("stream_only", "event:stream", weight=1.0),
        current_step=1,
    )

    assert unchanged == ledger
    assert compute_resolution_deficit(unchanged, current_step=1).negative_prediction_error == 1.0


def test_waiting_on_user_suspends_due_weight() -> None:
    ledger = open_expectation_from_forward_commitment(
        ExpectationLedger(),
        _commitment(kind="plan_commitment", assertiveness="medium"),
    ).suspend_matching(horizon="next_step", suspension_state="waiting_on_user")

    deficit = compute_resolution_deficit(ledger, current_step=10)

    assert deficit.due_weight == 0.0
    assert deficit.suspended_weight == 0.6
    assert deficit.negative_prediction_error == 0.0


def test_honest_low_diagnosis_does_not_create_false_debt() -> None:
    ledger = open_expectation_from_forward_commitment(
        ExpectationLedger(),
        _commitment(kind="diagnosis", assertiveness="low"),
    )

    assert ledger == ExpectationLedger()


def test_ledger_caps_active_and_resolved_records_deterministically() -> None:
    ledger = ExpectationLedger()
    for step in range(12):
        ledger = open_expectation_from_forward_commitment(
            ledger,
            _commitment(
                commitment_id=f"commit:{step}",
                kind="verification",
                assertiveness="high",
                opened_at_step=step,
            ),
        )

    assert len(ledger.active) == 8
    assert len(ledger.resolved) == 4
    assert tuple(record.expectation_id for record in ledger.active)[0].startswith("commit:4")
    assert all(record.suspension_state == "expired" for record in ledger.resolved)


def test_resolved_history_does_not_pay_unrelated_new_due_debt() -> None:
    fulfilled = open_expectation_from_forward_commitment(
        ExpectationLedger(),
        _commitment(
            commitment_id="commit:old",
            kind="verification",
            assertiveness="high",
            opened_at_step=1,
        ),
    ).apply_progress(
        EvidenceProgress("commitment_certified", "event:old-certified", weight=1.0),
        current_step=1,
    )
    with_new_due = open_expectation_from_forward_commitment(
        fulfilled,
        _commitment(
            commitment_id="commit:new",
            kind="verification",
            assertiveness="high",
            opened_at_step=2,
        ),
    )

    deficit = compute_resolution_deficit(with_new_due, current_step=2)

    assert deficit.fulfilled_weight == 1.0
    assert deficit.due_weight == 1.0
    assert deficit.negative_prediction_error == 1.0


def test_targeted_progress_pays_current_commitment_before_older_compatible_debt() -> None:
    older = open_expectation_from_forward_commitment(
        ExpectationLedger(),
        _commitment(
            commitment_id="commit:old",
            kind="verification",
            assertiveness="high",
            opened_at_step=1,
        ),
    )
    mixed = open_expectation_from_forward_commitment(
        older,
        _commitment(
            commitment_id="commit:current",
            kind="verification",
            assertiveness="high",
            opened_at_step=2,
        ),
    )

    paid = mixed.apply_progress(
        EvidenceProgress(
            "commitment_certified",
            "event:current-certified",
            weight=1.0,
            commitment_id="commit:current",
        ),
        current_step=2,
    )

    assert tuple(record.commitment_id for record in paid.active) == ("commit:old",)
    assert paid.resolved[0].commitment_id == "commit:current"
    assert paid.resolved[0].resolution_class == "commitment_certified"


def _commitment(
    *,
    kind: str,
    assertiveness: str,
    opened_at_step: int = 1,
    commitment_id: str = "commit:1",
) -> ForwardCommitment:
    return ForwardCommitment(
        commitment_id=commitment_id,
        source_event_ref=f"event:{opened_at_step}",
        claim_span_ref=f"event:{opened_at_step}:structured-cue",
        commitment_kind=kind,
        assertiveness=assertiveness,
        scope="task",
        opened_at_step=opened_at_step,
    )
