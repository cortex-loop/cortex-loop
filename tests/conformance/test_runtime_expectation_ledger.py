"""Conformance tests for expectation-ledger threading across host runtimes."""

from __future__ import annotations

from cortex.hosts.claude.runtime import ClaudeRuntimeSession
from cortex.hosts.claude.session_io import (
    build_claude_runtime_session_artifact,
    parse_claude_runtime_session_artifact,
)
from cortex.hosts.claude_code_desktop.runtime import ClaudeCodeDesktopRuntimeSession
from cortex.hosts.gemini.runtime import GeminiRuntimeSession
from cortex.hosts.gemini.session_io import (
    build_gemini_runtime_session_artifact,
    parse_gemini_runtime_session_artifact,
)
from cortex.hosts.openai.runtime import OpenAIRuntimeSession
from cortex.hosts.openai.session_io import (
    build_openai_runtime_session_artifact,
    parse_openai_runtime_session_artifact,
)
from cortex.hosts.reference.runtime import ReferenceRuntimeSession, run_reference_runtime_step
from cortex.sre.expectations import (
    ExpectationLedger,
    ForwardCommitment,
    open_expectation_from_forward_commitment,
)


def test_all_runtime_sessions_default_to_empty_expectation_ledger() -> None:
    for session in (
        ReferenceRuntimeSession(),
        OpenAIRuntimeSession(),
        ClaudeRuntimeSession(),
        GeminiRuntimeSession(),
        ClaudeCodeDesktopRuntimeSession(),
    ):
        assert session.expectation_ledger == ExpectationLedger()


def test_openai_claude_and_gemini_artifacts_roundtrip_expectation_ledgers() -> None:
    ledger = _ledger()

    openai_payload = build_openai_runtime_session_artifact(
        OpenAIRuntimeSession(session_id="oa-ledger", expectation_ledger=ledger)
    ).as_payload()
    claude_payload = build_claude_runtime_session_artifact(
        ClaudeRuntimeSession(session_id="cl-ledger", expectation_ledger=ledger)
    ).as_payload()
    gemini_payload = build_gemini_runtime_session_artifact(
        GeminiRuntimeSession(session_id="gm-ledger", expectation_ledger=ledger)
    ).as_payload()

    assert openai_payload["journal"]["expectation_ledger"]["active"]
    assert claude_payload["control_residue"]["expectation_ledger"]["active"]
    assert gemini_payload["control_residue"]["expectation_ledger"]["active"]
    assert parse_openai_runtime_session_artifact(openai_payload).expectation_ledger == ledger
    assert parse_claude_runtime_session_artifact(claude_payload).expectation_ledger == ledger
    assert parse_gemini_runtime_session_artifact(gemini_payload).expectation_ledger == ledger


def test_old_host_artifacts_parse_missing_expectation_ledgers_as_empty() -> None:
    assert (
        parse_openai_runtime_session_artifact(_old_openai_payload()).expectation_ledger
        == ExpectationLedger()
    )
    assert (
        parse_claude_runtime_session_artifact(_old_claude_payload()).expectation_ledger
        == ExpectationLedger()
    )
    assert (
        parse_gemini_runtime_session_artifact(_old_gemini_payload()).expectation_ledger
        == ExpectationLedger()
    )


def test_runtime_step_exposes_zero_and_nonzero_resolution_deficit_without_feedback_drift() -> None:
    clean = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "reference-clean-ledger"},
    )
    indebted = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "reference-indebted-ledger"},
        ReferenceRuntimeSession(expectation_ledger=_ledger()),
    )

    assert clean.resolution_deficit_payload["negative_prediction_error"] == 0.0
    assert indebted.resolution_deficit_payload["negative_prediction_error"] > 0.0
    assert clean.feedback_window_summary_payload["window_size"] == 1
    assert indebted.feedback_window_summary_payload["window_size"] == 1
    assert (
        indebted.feedback_window_summary_payload["recent_evidence_progress_class"]
        == "none"
    )


def test_candidate_event_opens_next_step_expectation_without_self_payment() -> None:
    first = run_reference_runtime_step(
        "ApprovalRequest",
        {"session_id": "reference-candidate-ledger", "candidate_id": "candidate-1"},
    )
    second = run_reference_runtime_step(
        "ContextLoad",
        {"session_id": "reference-candidate-ledger"},
        first.session,
    )

    assert len(first.session.expectation_ledger.active) == 1
    assert first.session.expectation_ledger.active[0].horizon == "next_step"
    assert first.resolution_deficit_payload["negative_prediction_error"] == 0.0
    assert second.resolution_deficit_payload["negative_prediction_error"] > 0.0


def _ledger() -> ExpectationLedger:
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


def _old_openai_payload() -> dict[str, object]:
    return {
        "artifact_kind": "openai_product_journal",
        "artifact_version": 1,
        "journal": {
            "session_id": "oa-old",
            "event_index": 1,
            "branch_registry": ["main"],
            "active_track_ref": "main",
            "active_goal_ref": None,
            "pending_goal_refs": [],
            "confirmed_artifact_refs": [],
            "budget_history": [],
            "brake_history": [],
            "brake_tonic_history": [],
            "last_selected_family": None,
            "last_commitment_result_summary": None,
            "last_realization_feedback": None,
            "feedback_window": [],
            "executive_modulator_memory": None,
            "last_failure_class": None,
            "next_recommended_move": "continue",
        },
    }


def _old_claude_payload() -> dict[str, object]:
    return {
        "artifact_kind": "claude-runtime-session",
        "artifact_version": 1,
        "continuity_truth": {
            "session_id": "cl-old",
            "event_index": 1,
            "branch_registry": ["main"],
            "active_track_ref": "main",
            "pending_goal_refs": [],
            "continuity_reminders": [],
        },
        "control_residue": {
            "last_budget_band": None,
            "last_commitment_result_summary": None,
            "last_realization_feedback": None,
            "feedback_window": [],
            "executive_modulator_memory": None,
            "brake_tonic_history": [],
        },
    }


def _old_gemini_payload() -> dict[str, object]:
    payload = _old_claude_payload()
    payload["artifact_kind"] = "gemini-runtime-session"
    payload["continuity_truth"]["session_id"] = "gm-old"
    return payload
