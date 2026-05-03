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
