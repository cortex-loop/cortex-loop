"""Runtime replay corpus for expectation-debt safety before route/brake coupling."""

from __future__ import annotations

from cortex.hosts.reference.runtime import ReferenceRuntimeSession, run_reference_runtime_step
from cortex.sre.expectations import (
    ExpectationLedger,
    ForwardCommitment,
    open_expectation_from_forward_commitment,
)


def test_reference_runtime_corpus_replays_clean_candidate_and_unpaid_forward_motion() -> None:
    clean = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "reference-corpus-clean"},
    )
    candidate = run_reference_runtime_step(
        "ApprovalRequest",
        {"session_id": "reference-corpus-candidate", "candidate_id": "candidate-1"},
    )
    candidate_due = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "reference-corpus-candidate"},
        candidate.session,
    )
    uncertified = run_reference_runtime_step(
        "ApprovalResult",
        {
            "session_id": "reference-corpus-uncertified",
            "commitment_id": "commit-1",
            "externally_consequential": True,
        },
    )

    assert clean.session.expectation_ledger == ExpectationLedger()
    assert clean.resolution_deficit_payload["negative_prediction_error"] == 0.0
    assert len(candidate.session.expectation_ledger.active) == 1
    assert candidate.session.expectation_ledger.active[0].horizon == "next_step"
    assert candidate.resolution_deficit_payload["negative_prediction_error"] == 0.0
    assert candidate_due.resolution_deficit_payload["negative_prediction_error"] > 0.0
    assert uncertified.commitment_result_kind == "uncertified"
    assert uncertified.session.expectation_ledger.active[0].remaining_weight == 1.0
    assert uncertified.resolution_deficit_payload["negative_prediction_error"] == 1.0


def test_reference_runtime_corpus_replays_certified_and_blocked_paydown() -> None:
    certified = run_reference_runtime_step(
        "ApprovalResult",
        {
            "session_id": "reference-corpus-certified",
            "commitment_id": "commit-1",
            "externally_consequential": True,
            "result_artifact_ref": "artifact-1",
        },
    )
    blocked = run_reference_runtime_step(
        "ApprovalResult",
        {
            "session_id": "reference-corpus-blocked",
            "commitment_id": "commit-1",
            "externally_consequential": True,
            "boundary_blocked": True,
            "boundary_reason_code": "approval-required",
        },
    )

    assert certified.commitment_result_kind == "certified"
    assert certified.session.expectation_ledger.active == ()
    assert certified.session.expectation_ledger.resolved[0].resolution_class == "commitment_certified"
    assert certified.resolution_deficit_payload["negative_prediction_error"] == 0.0
    assert blocked.commitment_result_kind == "blocked"
    assert blocked.session.expectation_ledger.active == ()
    assert blocked.session.expectation_ledger.resolved[0].resolution_class == "blocker_surfaced"
    assert blocked.resolution_deficit_payload["relief_weight"] == 1.0


def test_reference_runtime_corpus_continuity_progress_pays_existing_plan_debt() -> None:
    session = ReferenceRuntimeSession(
        session_id="reference-corpus-continuity",
        branch_registry=("main", "branch-alpha"),
        active_track_ref="main",
        pending_goal_refs=("branch-alpha",),
        expectation_ledger=_plan_ledger(),
    )
    resumed = run_reference_runtime_step(
        "ContextLoad",
        {
            "session_id": "reference-corpus-continuity",
            "branch_operation": "resume",
            "branch_track_ref": "branch-alpha",
        },
        session,
    )

    assert resumed.session.last_realization_feedback is not None
    assert resumed.session.last_realization_feedback.continuity_progress_class == (
        "pending-goals-reduced"
    )
    assert resumed.session.expectation_ledger.active == ()
    assert resumed.session.expectation_ledger.resolved[0].resolution_class == (
        "continuity_progress"
    )
    assert resumed.resolution_deficit_payload["negative_prediction_error"] == 0.0


def test_reference_runtime_corpus_stream_only_does_not_pay_existing_verification_debt() -> None:
    session = ReferenceRuntimeSession(
        session_id="reference-corpus-stream",
        expectation_ledger=_verification_ledger(),
    )
    streamed = run_reference_runtime_step(
        "ContextLoad",
        {
            "session_id": "reference-corpus-stream",
            "delta": "streaming text without verification",
        },
        session,
    )

    assert streamed.session.last_realization_feedback is not None
    assert streamed.session.last_realization_feedback.evidence_progress_class == "token-stream"
    assert len(streamed.session.expectation_ledger.active) == 1
    assert streamed.session.expectation_ledger.active[0].deficit_kind == "verification"
    assert streamed.resolution_deficit_payload["negative_prediction_error"] == 1.0


def test_reference_runtime_corpus_preserves_feedback_window_shape() -> None:
    result = run_reference_runtime_step(
        "ApprovalRequest",
        {"session_id": "reference-corpus-feedback", "candidate_id": "candidate-1"},
    )

    assert result.feedback_window_summary_payload["window_size"] == 1
    assert result.feedback_window_summary_payload["recent_evidence_progress_class"] == (
        result.session.last_realization_feedback.evidence_progress_class
    )
    assert result.feedback_window_summary_payload["recent_continuity_progress_class"] == (
        result.session.last_realization_feedback.continuity_progress_class
    )


def _verification_ledger() -> ExpectationLedger:
    return open_expectation_from_forward_commitment(
        ExpectationLedger(),
        ForwardCommitment(
            commitment_id="commit:verification",
            source_event_ref="event:0",
            claim_span_ref="event:0:structured-cue",
            commitment_kind="verification",
            assertiveness="high",
            scope="task",
            opened_at_step=0,
        ),
    )


def _plan_ledger() -> ExpectationLedger:
    return open_expectation_from_forward_commitment(
        ExpectationLedger(),
        ForwardCommitment(
            commitment_id="commit:plan",
            source_event_ref="event:0",
            claim_span_ref="event:0:structured-cue",
            commitment_kind="plan_commitment",
            assertiveness="medium",
            scope="task",
            opened_at_step=0,
        ),
    )
