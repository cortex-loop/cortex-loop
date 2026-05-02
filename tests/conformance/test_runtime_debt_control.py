"""Conformance locks for expectation debt feeding silent runtime control."""

from __future__ import annotations

from cortex.hosts.claude.runtime import ClaudeRuntimeSession, run_claude_runtime_step
from cortex.hosts.gemini.runtime import GeminiRuntimeSession, run_gemini_runtime_step
from cortex.hosts.openai.runtime import OpenAIRuntimeSession, run_openai_runtime_step
from cortex.hosts.reference.runtime import ReferenceRuntimeSession, run_reference_runtime_step
from cortex.sre.expectations import (
    ExpectationLedger,
    ForwardCommitment,
    open_expectation_from_forward_commitment,
)


def test_reference_runtime_uses_prior_debt_for_current_control_not_same_step_hindsight() -> None:
    first = run_reference_runtime_step(
        "ApprovalResult",
        {
            "session_id": "reference-debt-hindsight",
            "commitment_id": "commit-1",
            "externally_consequential": True,
        },
    )
    follow_up = run_reference_runtime_step(
        "ApprovalRequest",
        {
            "session_id": "reference-debt-hindsight",
            "candidate_id": "candidate-1",
        },
        first.session,
    )

    assert first.debt_control_payload["debt_pressure"] == 0.0
    assert first.resolution_deficit_payload["negative_prediction_error"] == 1.0
    assert follow_up.debt_control_payload["debt_pressure"] > 0.0
    assert follow_up.operator_route_payload["route_profile"] == "execute_guarded"
    assert follow_up.operator_route_payload["blocked_reason"] is None
    assert "debt-control:execute-guarded" in follow_up.operator_route_payload[
        "route_reason_tags"
    ]
    assert (
        follow_up.control_ledger.allocation_diagnostics["debt_control"]
        == follow_up.debt_control_payload
    )


def test_reference_runtime_candidate_debt_guards_next_forward_commitment() -> None:
    candidate = run_reference_runtime_step(
        "ApprovalRequest",
        {"session_id": "reference-debt-candidate", "candidate_id": "candidate-1"},
    )
    follow_up = run_reference_runtime_step(
        "ApprovalRequest",
        {"session_id": "reference-debt-candidate", "candidate_id": "candidate-2"},
        candidate.session,
    )

    assert candidate.debt_control_payload["debt_pressure"] == 0.0
    assert candidate.session.expectation_ledger.active[0].horizon == "next_step"
    assert follow_up.debt_control_payload["resolution_pressure"] > 0.0
    assert follow_up.operator_route_payload["route_profile"] == "execute_guarded"
    assert follow_up.operator_route_payload["blocked_reason"] is None
    assert follow_up.executive_policy_view_payload["debt_guard_bias"] > 0.0


def test_reference_runtime_debt_keeps_inspection_available_with_verification_relief() -> None:
    session = ReferenceRuntimeSession(
        session_id="reference-debt-inspect",
        expectation_ledger=_verification_ledger(),
    )
    inspected = run_reference_runtime_step(
        "ContextLoad",
        {
            "session_id": "reference-debt-inspect",
            "delta": "streamed context without verification",
        },
        session,
    )

    assert inspected.debt_control_payload["resolution_pressure"] > 0.0
    assert inspected.debt_control_payload["forward_commit_pressure"] == 0.0
    assert inspected.debt_control_payload["goal_drag"] == 0.0
    assert inspected.debt_control_payload["verification_relief_bias"] > 0.0
    assert inspected.operator_route_payload["route_profile"] == "inspect_light"
    assert inspected.operator_route_payload["route_budget"]["allow_extra_read_pass"] is True
    assert inspected.operator_route_payload["blocked_reason"] is None
    assert all(
        not tag.startswith("debt-control:default-penalty")
        for tag in inspected.operator_route_payload["route_reason_tags"]
    )


def test_reference_runtime_paid_down_debt_returns_next_control_to_neutral() -> None:
    paid = run_reference_runtime_step(
        "ContextLoad",
        {
            "session_id": "reference-debt-paid",
            "branch_operation": "resume",
            "branch_track_ref": "branch-alpha",
        },
        ReferenceRuntimeSession(
            session_id="reference-debt-paid",
            branch_registry=("main", "branch-alpha"),
            active_track_ref="main",
            pending_goal_refs=("branch-alpha",),
            expectation_ledger=_plan_ledger(),
        ),
    )
    follow_up = run_reference_runtime_step(
        "ApprovalRequest",
        {"session_id": "reference-debt-paid", "candidate_id": "candidate-2"},
        paid.session,
    )

    assert paid.session.expectation_ledger.active == ()
    assert paid.session.expectation_ledger.resolved[0].resolution_class == (
        "continuity_progress"
    )
    assert follow_up.debt_control_payload["debt_pressure"] == 0.0
    assert follow_up.operator_route_payload["route_profile"] == "continuity_standard"


def test_host_runtimes_expose_bounded_debt_diagnostics_without_model_visible_text() -> None:
    cases = (
        (
            run_openai_runtime_step,
            "response.output_text.delta",
            {"session_id": "openai-debt", "response_id": "resp-1", "delta": "hello"},
            OpenAIRuntimeSession(
                session_id="openai-debt",
                expectation_ledger=_verification_ledger(),
            ),
        ),
        (
            run_claude_runtime_step,
            "content_block_delta",
            {"session_id": "claude-debt", "message_id": "msg-1", "delta": "hello"},
            ClaudeRuntimeSession(
                session_id="claude-debt",
                expectation_ledger=_verification_ledger(),
            ),
        ),
        (
            run_gemini_runtime_step,
            "content.delta",
            {"session_id": "gemini-debt", "interaction_id": "int-1", "delta": "hello"},
            GeminiRuntimeSession(
                session_id="gemini-debt",
                expectation_ledger=_verification_ledger(),
            ),
        ),
    )

    for runner, event_name, payload, session in cases:
        result = runner(event_name, payload, session)

        assert result.debt_control_payload["debt_pressure"] > 0.0
        assert result.control_ledger.allocation_diagnostics["debt_control"] == (
            result.debt_control_payload
        )
        assert result.executive_policy_view_payload["debt_guard_bias"] > 0.0
        assert result.operator_route_payload["route_profile"] == "inspect_light"
        assert result.operator_route_payload["blocked_reason"] is None


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
