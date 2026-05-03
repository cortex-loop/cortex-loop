"""Conformance locks for grounded-intervention diagnostics across host runtimes."""

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


def test_clean_host_runtime_steps_expose_silent_intervention_payloads() -> None:
    cases = (
        (
            run_reference_runtime_step,
            "ContextLoad",
            {"session_id": "reference-grounded-clean", "delta": "context"},
            ReferenceRuntimeSession(session_id="reference-grounded-clean"),
        ),
        (
            run_openai_runtime_step,
            "response.output_text.delta",
            {"session_id": "openai-grounded-clean", "response_id": "resp-1", "delta": "hello"},
            OpenAIRuntimeSession(session_id="openai-grounded-clean"),
        ),
        (
            run_claude_runtime_step,
            "content_block_delta",
            {"session_id": "claude-grounded-clean", "message_id": "msg-1", "delta": "hello"},
            ClaudeRuntimeSession(session_id="claude-grounded-clean"),
        ),
        (
            run_gemini_runtime_step,
            "content.delta",
            {"session_id": "gemini-grounded-clean", "interaction_id": "int-1", "delta": "hello"},
            GeminiRuntimeSession(session_id="gemini-grounded-clean"),
        ),
    )

    for runner, event_name, payload, session in cases:
        result = runner(event_name, payload, session)

        assert result.grounded_intervention_payload["mode"] == "stay_silent"
        assert result.grounded_intervention_payload["record"] is None
        assert result.grounded_intervention_payload["silence_reason"] in {
            "pressure_below_visible_threshold",
            "state_relieved:paid_down",
        }
        assert result.operator_route_payload["blocked_reason"] is None


def test_unpaid_verification_debt_produces_grounded_diagnostics_without_route_change() -> None:
    cases = (
        (
            run_reference_runtime_step,
            "ContextLoad",
            {"session_id": "reference-grounded-debt", "delta": "streamed context"},
            ReferenceRuntimeSession(
                session_id="reference-grounded-debt",
                expectation_ledger=_verification_ledger(),
            ),
        ),
        (
            run_openai_runtime_step,
            "response.output_text.delta",
            {"session_id": "openai-grounded-debt", "response_id": "resp-1", "delta": "hello"},
            OpenAIRuntimeSession(
                session_id="openai-grounded-debt",
                expectation_ledger=_verification_ledger(),
            ),
        ),
        (
            run_claude_runtime_step,
            "content_block_delta",
            {"session_id": "claude-grounded-debt", "message_id": "msg-1", "delta": "hello"},
            ClaudeRuntimeSession(
                session_id="claude-grounded-debt",
                expectation_ledger=_verification_ledger(),
            ),
        ),
        (
            run_gemini_runtime_step,
            "content.delta",
            {"session_id": "gemini-grounded-debt", "interaction_id": "int-1", "delta": "hello"},
            GeminiRuntimeSession(
                session_id="gemini-grounded-debt",
                expectation_ledger=_verification_ledger(),
            ),
        ),
    )

    for runner, event_name, payload, session in cases:
        result = runner(event_name, payload, session)

        assert result.debt_control_payload["debt_pressure"] > 0.0
        assert result.operator_route_payload["route_profile"] == "inspect_light"
        assert result.grounded_intervention_payload["mode"] == "model_visible_reflection"
        record = result.grounded_intervention_payload["record"]
        assert record["kind"] == "overdue_verification"
        assert record["grounded_anchor_type"] == "evidence"
        assert record["task_local_anchor_text"] == "the verification opened by this task"
        assert record["next_move_class"] == "run_check"
        assert result.grounded_intervention_payload["selection_trace"][
            "perception_source"
        ] == "product_runtime_expectation"
        assert result.grounded_intervention_payload["selection_trace"][
            "selected_expectation_id"
        ]


def test_host_runtime_sequences_derive_visible_intervention_from_product_events() -> None:
    cases = (
        (
            run_reference_runtime_step,
            ReferenceRuntimeSession(session_id="reference-product-events"),
            "ApprovalResult",
            {
                "session_id": "reference-product-events",
                "commitment_id": "commit-product-events",
                "externally_consequential": True,
            },
            "ContextLoad",
            {
                "session_id": "reference-product-events",
                "delta": "continuing after an unresolved verification",
            },
        ),
        (
            run_openai_runtime_step,
            OpenAIRuntimeSession(session_id="openai-product-events"),
            "response.completed",
            {
                "session_id": "openai-product-events",
                "response_id": "resp-product-events-1",
                "commitment_id": "commit-product-events",
                "externally_consequential": True,
            },
            "response.output_text.delta",
            {
                "session_id": "openai-product-events",
                "response_id": "resp-product-events-2",
                "delta": "continuing after an unresolved verification",
            },
        ),
        (
            run_claude_runtime_step,
            ClaudeRuntimeSession(session_id="claude-product-events"),
            "message_stop",
            {
                "session_id": "claude-product-events",
                "message_id": "msg-product-events-1",
                "commitment_id": "commit-product-events",
                "externally_consequential": True,
            },
            "content_block_delta",
            {
                "session_id": "claude-product-events",
                "message_id": "msg-product-events-2",
                "delta": "continuing after an unresolved verification",
            },
        ),
        (
            run_gemini_runtime_step,
            GeminiRuntimeSession(session_id="gemini-product-events"),
            "interaction.complete",
            {
                "session_id": "gemini-product-events",
                "interaction_id": "int-product-events-1",
                "commitment_id": "commit-product-events",
                "externally_consequential": True,
            },
            "content.delta",
            {
                "session_id": "gemini-product-events",
                "interaction_id": "int-product-events-2",
                "delta": "continuing after an unresolved verification",
            },
        ),
    )

    for runner, session, opening_event, opening_payload, follow_event, follow_payload in cases:
        opened = runner(opening_event, opening_payload, session)
        followed = runner(follow_event, follow_payload, opened.session)

        assert opened.commitment_result_kind == "uncertified"
        assert opened.grounded_intervention_payload["mode"] == "stay_silent"
        assert opened.grounded_intervention_payload["silence_reason"] == (
            "silent_control_sufficient"
        )
        assert followed.grounded_intervention_payload["mode"] == "model_visible_reflection"
        trace = followed.grounded_intervention_payload["selection_trace"]
        assert trace["perception_source"] == "product_runtime_expectation"
        assert trace["selected_expectation_id"].endswith(":verification:expectation")
        assert trace["deficit_kind"] == "verification"
        assert trace["silence_reason"] is None
        assert trace["silent_control_sufficient"] is False


def test_certified_and_blocked_product_events_stay_silent_after_relief() -> None:
    certified = run_reference_runtime_step(
        "ApprovalResult",
        {
            "session_id": "reference-grounded-certified",
            "commitment_id": "commit-certified",
            "externally_consequential": True,
            "result_artifact_ref": "artifact-certified",
        },
        ReferenceRuntimeSession(session_id="reference-grounded-certified"),
    )
    blocked = run_reference_runtime_step(
        "ApprovalResult",
        {
            "session_id": "reference-grounded-blocked",
            "commitment_id": "commit-blocked",
            "externally_consequential": True,
            "boundary_blocked": True,
            "boundary_reason_code": "approval-required",
        },
        ReferenceRuntimeSession(session_id="reference-grounded-blocked"),
    )

    assert certified.commitment_result_kind == "certified"
    assert certified.grounded_intervention_payload["mode"] == "stay_silent"
    assert certified.grounded_intervention_payload["selection_trace"]["selected_expectation_id"] is None
    assert blocked.commitment_result_kind == "blocked"
    assert blocked.grounded_intervention_payload["mode"] == "stay_silent"
    assert blocked.grounded_intervention_payload["selection_trace"]["selected_expectation_id"] is None


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
