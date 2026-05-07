"""Product locks for the Codex App/CLI product hook coordinator."""

from __future__ import annotations

import inspect
import json
from dataclasses import replace
from pathlib import Path

from cortex.hosts.openai import codex_app_cli_hook_coordinator
from cortex.hosts.openai.posttooluse_task_standard_actuator import (
    PostToolUseTaskStandardPhase,
    classify_posttooluse_task_standard_phase,
    posttooluse_context_span,
)
from cortex.hosts.openai.codex_app_cli_hook_coordinator import (
    OpenAICodexHookHostResponse,
    OpenAICodexHookHostDecision,
    OpenAICodexInMemoryStateStore,
    OpenAICodexJsonStateStore,
    OpenAICodexRuntimeSnapshot,
    handle_openai_codex_hook_payload,
    normalize_openai_codex_hook_payload,
)
from cortex.hosts.openai.codex_app_cli_lifecycle import (
    OpenAICodexLifecycleDirectiveAction,
    OpenAICodexLifecycleEvent,
)
from cortex.sre.task_standard import (
    TASK_STANDARD_FORMATION_TEXT,
    TaskStandardEvidenceClass,
)
from cortex.sre.debt_control import DebtControlPressure
from cortex.sre.expectations import (
    ExpectationLedger,
    ExpectationRecord,
    ResolutionDeficitState,
)


OVERDUE_VERIFICATION_IDENTITY_TEXT = (
    "Wait, did I actually check my work properly. I don't want to hand this off "
    "and have someone find the gap because I rushed it. I should run a check, "
    "narrow what I'm claiming, or leave it open and be honest about it."
)
TASK_STANDARD_CODEX_CONTEXT_PAYLOAD = {
    "hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": TASK_STANDARD_FORMATION_TEXT,
    }
}


def test_user_prompt_submit_updates_state_without_model_visible_text() -> None:
    store = OpenAICodexInMemoryStateStore()

    result = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="UserPromptSubmit",
            prompt="Build the thing carefully.",
        ),
        state_store=store,
    )

    assert result.hook_payload.hook_event_name is OpenAICodexLifecycleEvent.USER_PROMPT_SUBMIT
    assert result.session_state.current_step == 1
    assert result.session_state.prompt_text_hash is not None
    assert result.directive.action is OpenAICodexLifecycleDirectiveAction.ALLOW
    assert result.host_response.decision is OpenAICodexHookHostDecision.ALLOW
    assert result.host_response.stdout_payload is None
    assert result.directive.model_visible_text is None


def test_user_prompt_submit_can_emit_exact_signed_off_task_standard_text() -> None:
    store = OpenAICodexInMemoryStateStore()

    result = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="UserPromptSubmit",
            prompt="Build a docs site with search, tag pages, and navigation.",
        ),
        state_store=store,
        task_standard_text_enabled=True,
    )

    assert result.directive.action is OpenAICodexLifecycleDirectiveAction.ALLOW
    assert result.host_response.stdout_payload == TASK_STANDARD_CODEX_CONTEXT_PAYLOAD
    assert result.session_state.task_standard_spine.visible_task_obligations
    assert result.session_state.task_standard_spine.standard_items == ()
    assert result.host_response.stdout_payload != {
        "context": TASK_STANDARD_FORMATION_TEXT
    }


def test_pretool_context_payload_is_rejected_by_codex_host_contract() -> None:
    try:
        OpenAICodexHookHostResponse(
            context="unsupported pretool context",
            context_hook_event_name="PreToolUse",
        )
    except ValueError as exc:
        assert "additionalContext" in str(exc)
    else:  # pragma: no cover - explicit contract guard.
        raise AssertionError("PreToolUse additionalContext must not serialize.")


def test_posttool_failure_persists_private_state_without_text() -> None:
    store = OpenAICodexInMemoryStateStore()

    result = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PostToolUseFailure",
            tool_name="Bash",
            tool_input={"command": "npm test"},
            error="exit status 1",
        ),
        state_store=store,
    )

    assert result.session_state.tool_event_count == 1
    assert result.session_state.tool_failure_count == 1
    assert result.session_state.warning_tags == ("tool-failure",)
    assert result.directive.action is OpenAICodexLifecycleDirectiveAction.ALLOW
    assert result.directive.model_visible_text is None
    assert result.host_response.stdout_payload is None


def test_stop_with_product_runtime_snapshot_blocks_with_identity_text() -> None:
    store = OpenAICodexInMemoryStateStore()

    result = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="Stop",
            transcript_path="/tmp/codex-session.jsonl",
            last_assistant_message="Done.",
        ),
        state_store=store,
        runtime_snapshot=_verification_runtime_snapshot(),
    )

    assert (
        result.directive.action
        is OpenAICodexLifecycleDirectiveAction.BLOCK_WITH_IDENTITY_CONTINUOUS_TEXT
    )
    assert result.directive.model_visible_text == OVERDUE_VERIFICATION_IDENTITY_TEXT
    assert result.host_response.decision is OpenAICodexHookHostDecision.BLOCK
    assert result.host_response.stdout_payload == {
        "decision": "block",
        "reason": OVERDUE_VERIFICATION_IDENTITY_TEXT,
    }


def test_stop_without_product_perception_state_stays_silent() -> None:
    store = OpenAICodexInMemoryStateStore()

    result = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="Stop",
            transcript_path="/tmp/codex-session.jsonl",
            last_assistant_message="Done.",
        ),
        state_store=store,
    )

    assert result.directive.action is OpenAICodexLifecycleDirectiveAction.STAY_SILENT
    assert result.directive.silence_reason == "missing_product_perception_state"
    assert result.host_response.decision is OpenAICodexHookHostDecision.ALLOW
    assert result.host_response.stdout_payload is None


def test_product_perception_opens_due_verification_from_closure_claim() -> None:
    store = OpenAICodexInMemoryStateStore()
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="UserPromptSubmit",
            prompt="Make the change and verify it.",
        ),
        state_store=store,
    )

    result = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="Stop",
            transcript_path="/tmp/codex-session.jsonl",
            last_assistant_message="Done.",
        ),
        state_store=store,
    )

    assert (
        result.directive.action
        is OpenAICodexLifecycleDirectiveAction.BLOCK_WITH_IDENTITY_CONTINUOUS_TEXT
    )
    assert result.directive.model_visible_text == OVERDUE_VERIFICATION_IDENTITY_TEXT
    assert result.session_state.closure_claim_count == 1
    assert len(result.session_state.expectation_ledger.active) == 1
    assert (
        result.grounded_intervention.selection_trace.perception_source
        == "product_runtime_expectation"
    )
    assert result.host_response.stdout_payload == {
        "decision": "block",
        "reason": OVERDUE_VERIFICATION_IDENTITY_TEXT,
    }


def test_product_perception_pays_down_verification_after_observed_check() -> None:
    store = OpenAICodexInMemoryStateStore()
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="UserPromptSubmit",
            prompt="Make the change and verify it.",
        ),
        state_store=store,
    )
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PostToolUse",
            tool_name="Bash",
            tool_input={"command": "python3 -m pytest tests/product -q"},
            tool_response={"exit_code": 0},
        ),
        state_store=store,
    )

    result = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="Stop",
            transcript_path="/tmp/codex-session.jsonl",
            last_assistant_message="Done.",
        ),
        state_store=store,
    )

    assert result.directive.action is OpenAICodexLifecycleDirectiveAction.STAY_SILENT
    assert result.directive.silence_reason == "pressure_below_visible_threshold"
    assert result.session_state.verification_evidence_count == 1
    assert len(result.session_state.expectation_ledger.active) == 0
    assert len(result.session_state.expectation_ledger.resolved) == 1
    assert result.host_response.stdout_payload is None


def test_task_standard_block_is_stored_without_immediate_stop_block() -> None:
    store = OpenAICodexInMemoryStateStore()
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="UserPromptSubmit",
            prompt="Build a docs site with search, tag pages, and navigation.",
        ),
        state_store=store,
    )

    result = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="Stop",
            transcript_path="/tmp/codex-session.jsonl",
            last_assistant_message=_standard_block(),
        ),
        state_store=store,
    )

    assert result.directive.action is OpenAICodexLifecycleDirectiveAction.STAY_SILENT
    assert result.host_response.stdout_payload is None
    assert [
        item.kind.value
        for item in result.session_state.task_standard_spine.standard_items
    ] == ["work_standard", "likely_miss", "closure_evidence"]
    assert len(result.session_state.expectation_ledger.active) == 0


def test_pretool_transcript_captures_assistant_standard_before_tool_use(
    tmp_path: Path,
) -> None:
    transcript_path = tmp_path / "transcript.jsonl"
    _write_transcript(
        transcript_path,
        _developer_context_row(TASK_STANDARD_FORMATION_TEXT),
        _assistant_message_row(_standard_block()),
        _function_call_row(),
    )
    store = OpenAICodexInMemoryStateStore()
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="UserPromptSubmit",
            prompt="Build a docs site with search, tag pages, and navigation.",
            transcript_path=str(transcript_path),
        ),
        state_store=store,
        task_standard_text_enabled=True,
    )

    result = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PreToolUse",
            transcript_path=str(transcript_path),
            tool_name="Bash",
            tool_input={"command": "npm run build"},
            last_assistant_message=None,
        ),
        state_store=store,
    )

    assert result.host_response.stdout_payload is None
    assert result.session_state.tool_event_count == 1
    assert [
        item.kind.value
        for item in result.session_state.task_standard_spine.standard_items
    ] == ["work_standard", "likely_miss", "closure_evidence"]
    assert all(
        "pretool-transcript-standard" in item.source_event_ref
        for item in result.session_state.task_standard_spine.standard_items
    )


def test_pretool_transcript_ignores_developer_context_standard_text(
    tmp_path: Path,
) -> None:
    transcript_path = tmp_path / "transcript.jsonl"
    _write_transcript(transcript_path, _developer_context_row(_standard_block()))
    store = OpenAICodexInMemoryStateStore()
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="UserPromptSubmit",
            prompt="Build a docs site with search.",
            transcript_path=str(transcript_path),
        ),
        state_store=store,
        task_standard_text_enabled=True,
    )

    result = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PreToolUse",
            transcript_path=str(transcript_path),
            tool_name="Bash",
            tool_input={"command": "npm run build"},
            last_assistant_message=None,
        ),
        state_store=store,
    )

    assert result.session_state.task_standard_spine.standard_items == ()
    assert result.host_response.stdout_payload is None


def test_pretool_transcript_refuses_standard_after_first_tool_call(
    tmp_path: Path,
) -> None:
    transcript_path = tmp_path / "transcript.jsonl"
    _write_transcript(
        transcript_path,
        _function_call_row(),
        _assistant_message_row(_standard_block()),
    )
    store = OpenAICodexInMemoryStateStore()
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="UserPromptSubmit",
            prompt="Build a docs site with search.",
            transcript_path=str(transcript_path),
        ),
        state_store=store,
    )

    result = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PreToolUse",
            transcript_path=str(transcript_path),
            tool_name="Bash",
            tool_input={"command": "npm run build"},
            last_assistant_message=None,
        ),
        state_store=store,
    )

    assert result.session_state.task_standard_spine.standard_items == ()
    assert result.host_response.stdout_payload is None


def test_pretool_transcript_malformed_or_absent_standard_stays_private(
    tmp_path: Path,
) -> None:
    malformed_path = tmp_path / "malformed.jsonl"
    malformed_path.write_text("{not json}\n", encoding="utf-8")
    partial_path = tmp_path / "partial.jsonl"
    _write_transcript(partial_path, _assistant_message_row("Work standard: partial only."))
    store = OpenAICodexInMemoryStateStore()
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="UserPromptSubmit",
            prompt="Build a docs site with search.",
            transcript_path=str(malformed_path),
        ),
        state_store=store,
    )

    malformed = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PreToolUse",
            transcript_path=str(malformed_path),
            tool_name="Bash",
            tool_input={"command": "npm run build"},
            last_assistant_message=None,
        ),
        state_store=store,
    )
    partial = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PreToolUse",
            transcript_path=str(partial_path),
            tool_name="Bash",
            tool_input={"command": "npm run build"},
            last_assistant_message=None,
        ),
        state_store=store,
    )

    assert malformed.session_state.task_standard_spine.standard_items == ()
    assert malformed.host_response.stdout_payload is None
    assert partial.session_state.task_standard_spine.standard_items == ()
    assert partial.session_state.task_standard_spine.malformed_standard_block_count == 1
    assert partial.host_response.stdout_payload is None


def test_posttooluse_fallback_captures_standard_before_evidence_scoring(
    tmp_path: Path,
) -> None:
    transcript_path = tmp_path / "transcript.jsonl"
    _write_transcript(
        transcript_path,
        _assistant_message_row(_standard_block()),
        _function_call_row(),
    )
    store = OpenAICodexInMemoryStateStore()
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="UserPromptSubmit",
            prompt="Build a docs site with search, tag pages, and navigation.",
            transcript_path=str(transcript_path),
        ),
        state_store=store,
    )

    result = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PostToolUse",
            transcript_path=str(transcript_path),
            tool_name="Bash",
            tool_input={
                "command": (
                    "grep -R search src && grep -R tag src && "
                    "grep -R navigation src"
                )
            },
            tool_response={
                "exit_code": 0,
                "output": "search dataset ok\ntag pages ok\nnavigation ok",
            },
            last_assistant_message=None,
        ),
        state_store=store,
    )

    spine = result.session_state.task_standard_spine
    assert len(spine.standard_items) == 3
    assert spine.evidence_refs[-1].evidence_class is TaskStandardEvidenceClass.STANDARD_ALIGNED
    assert spine.evidence_refs[-1].item_ids
    assert result.session_state.verification_evidence_count == 1


def test_task_standard_generic_check_does_not_pay_down_standard_items() -> None:
    store = OpenAICodexInMemoryStateStore()
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="UserPromptSubmit",
            prompt="Build a docs site with search, tag pages, and navigation.",
        ),
        state_store=store,
    )
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="Stop",
            transcript_path="/tmp/codex-session.jsonl",
            last_assistant_message=_standard_block(),
        ),
        state_store=store,
    )
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PostToolUse",
            tool_name="Bash",
            tool_input={"command": "npm run build"},
            tool_response={"exit_code": 0, "output": "build completed"},
        ),
        state_store=store,
    )

    result = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="Stop",
            transcript_path="/tmp/codex-session.jsonl",
            last_assistant_message=(
                "Done: implemented the docs site search, tag pages, and navigation."
            ),
        ),
        state_store=store,
    )

    assert (
        result.directive.action
        is OpenAICodexLifecycleDirectiveAction.BLOCK_WITH_IDENTITY_CONTINUOUS_TEXT
    )
    assert result.session_state.verification_evidence_count == 0
    assert result.session_state.task_standard_spine.has_unmatched_closure_items
    assert len(result.session_state.expectation_ledger.active) == 1


def test_task_standard_aligned_evidence_pays_down_standard_items() -> None:
    store = OpenAICodexInMemoryStateStore()
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="UserPromptSubmit",
            prompt="Build a docs site with search, tag pages, and navigation.",
        ),
        state_store=store,
    )
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="Stop",
            transcript_path="/tmp/codex-session.jsonl",
            last_assistant_message=_standard_block(),
        ),
        state_store=store,
    )
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PostToolUse",
            tool_name="Bash",
            tool_input={
                "command": (
                    "grep -R search src && grep -R tag src && "
                    "grep -R navigation src"
                )
            },
            tool_response={
                "exit_code": 0,
                "output": "search dataset ok\ntag pages ok\nnavigation ok",
            },
        ),
        state_store=store,
    )

    result = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="Stop",
            transcript_path="/tmp/codex-session.jsonl",
            last_assistant_message=(
                "Done: implemented the docs site search, tag pages, and navigation."
            ),
        ),
        state_store=store,
    )

    assert result.directive.action is OpenAICodexLifecycleDirectiveAction.STAY_SILENT
    assert result.directive.silence_reason == "pressure_below_visible_threshold"
    assert result.session_state.verification_evidence_count == 1
    assert not result.session_state.task_standard_spine.has_unmatched_closure_items
    assert len(result.session_state.expectation_ledger.active) == 0
    assert len(result.session_state.expectation_ledger.resolved) == 1


def test_task_standard_clean_readback_stop_stays_silent() -> None:
    store = OpenAICodexInMemoryStateStore()
    transcript_path = Path("/tmp/codex-task-standard-clean-readback.jsonl")
    _write_transcript(transcript_path, _assistant_message_row(_file_standard_block()))

    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="UserPromptSubmit",
            prompt=(
                "Use shell commands to create result.txt containing task standard "
                "live done, read it back, and report done."
            ),
            transcript_path=str(transcript_path),
        ),
        state_store=store,
    )
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PreToolUse",
            transcript_path=str(transcript_path),
            tool_name="Bash",
            tool_input={
                "command": (
                    "printf 'task standard live done\\n' > result.txt && cat result.txt"
                )
            },
            last_assistant_message=None,
        ),
        state_store=store,
    )
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PostToolUse",
            transcript_path=str(transcript_path),
            tool_name="Bash",
            tool_input={
                "command": (
                    "printf 'task standard live done\\n' > result.txt && cat result.txt"
                )
            },
            tool_response={
                "exit_code": 0,
                "aggregated_output": "task standard live done\n",
            },
            last_assistant_message=None,
        ),
        state_store=store,
    )

    result = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="Stop",
            transcript_path=str(transcript_path),
            last_assistant_message=(
                "Read back from result.txt: task standard live done.\n\ndone"
            ),
        ),
        state_store=store,
    )

    assert result.directive.action is OpenAICodexLifecycleDirectiveAction.STAY_SILENT
    assert result.directive.silence_reason == "pressure_below_visible_threshold"
    assert result.session_state.verification_evidence_count == 1
    assert not result.session_state.task_standard_spine.has_unmatched_closure_items
    assert len(result.session_state.expectation_ledger.active) == 0
    assert len(result.session_state.expectation_ledger.resolved) == 1


def test_posttooluse_task_standard_context_requires_flag() -> None:
    store = OpenAICodexInMemoryStateStore()
    transcript_path = Path("/tmp/codex-task-standard-posttooluse-disabled.jsonl")
    _write_transcript(
        transcript_path,
        _assistant_message_row(_posttooluse_exactness_standard_block()),
    )
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="UserPromptSubmit",
            prompt="Create exact_result.txt with exact alpha beta omega content.",
        ),
        state_store=store,
        task_standard_text_enabled=True,
    )
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PreToolUse",
            transcript_path=str(transcript_path),
            tool_name="Bash",
            tool_input={"command": "wc -l exact_result.txt"},
        ),
        state_store=store,
    )

    result = handle_openai_codex_hook_payload(
        _posttooluse_wc_payload(transcript_path),
        state_store=store,
    )

    assert result.directive.action is OpenAICodexLifecycleDirectiveAction.ALLOW
    assert result.host_response.stdout_payload is None
    assert result.session_state.last_posttooluse_task_standard_context_item_id is None


def test_posttooluse_task_standard_context_emits_specific_next_step() -> None:
    store = OpenAICodexInMemoryStateStore()
    transcript_path = Path("/tmp/codex-task-standard-posttooluse-context.jsonl")
    _write_transcript(
        transcript_path,
        _assistant_message_row(_posttooluse_exactness_standard_block()),
    )
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="UserPromptSubmit",
            prompt="Create exact_result.txt with exact alpha beta omega content.",
        ),
        state_store=store,
        task_standard_text_enabled=True,
    )
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PreToolUse",
            transcript_path=str(transcript_path),
            tool_name="Bash",
            tool_input={"command": "wc -l exact_result.txt"},
        ),
        state_store=store,
    )

    result = handle_openai_codex_hook_payload(
        _posttooluse_wc_payload(transcript_path),
        state_store=store,
        posttooluse_task_standard_context_enabled=True,
    )

    expected_text = (
        "I still need direct evidence for: the file content is exactly "
        "alpha beta omega with no extra text. The last tool result did not show "
        "that exact item. Next step: wc -l exact_result.txt and cat -A "
        "exact_result.txt show one line alpha beta omega$ before treating this "
        "as done."
    )
    assert (
        result.directive.action
        is OpenAICodexLifecycleDirectiveAction.ADD_ADDITIONAL_CONTEXT
    )
    assert result.host_response.stdout_payload == {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": expected_text,
        }
    }
    assert result.host_response.stdout_payload.get("decision") is None
    assert "Cortex" not in expected_text
    assert "product-visible" not in expected_text
    assert "verify more" not in expected_text.lower()
    assert result.session_state.posttooluse_task_standard_context_item_ids
    assert result.session_state.last_posttooluse_task_standard_context_reason == (
        "unresolved_task_standard_item_after_tool"
    )


def test_posttooluse_task_standard_context_waits_on_missing_artifact() -> None:
    store = OpenAICodexInMemoryStateStore()
    transcript_path = Path("/tmp/codex-task-standard-posttooluse-missing.jsonl")
    _write_transcript(
        transcript_path,
        _assistant_message_row(_posttooluse_exactness_standard_block()),
    )
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="UserPromptSubmit",
            prompt="Create exact_result.txt with exact alpha beta omega content.",
        ),
        state_store=store,
        task_standard_text_enabled=True,
    )
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PreToolUse",
            transcript_path=str(transcript_path),
            tool_name="Bash",
            tool_input={"command": "wc -l exact_result.txt"},
        ),
        state_store=store,
    )

    result = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PostToolUse",
            transcript_path=str(transcript_path),
            tool_name="Bash",
            tool_input={"command": "wc -l exact_result.txt"},
            tool_response={
                "exit_code": 0,
                "aggregated_output": (
                    "wc: exact_result.txt: open: No such file or directory\n"
                ),
            },
        ),
        state_store=store,
        posttooluse_task_standard_context_enabled=True,
    )

    assert result.directive.action is OpenAICodexLifecycleDirectiveAction.ALLOW
    assert result.host_response.stdout_payload is None
    assert not result.session_state.posttooluse_task_standard_context_item_ids
    assert (
        result.session_state.last_posttooluse_task_standard_context_silence_reason
        == "pre_artifact_candidate_missing"
    )


def test_posttooluse_task_standard_context_waits_on_live_equivalent_missing_artifact() -> None:
    store = OpenAICodexInMemoryStateStore()
    transcript_path = Path("/tmp/codex-task-standard-posttooluse-live-missing.jsonl")
    _write_transcript(
        transcript_path,
        _assistant_message_row(_posttooluse_exactness_standard_block()),
    )
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="UserPromptSubmit",
            prompt="Create exact_result.txt with exact alpha beta omega content.",
        ),
        state_store=store,
        task_standard_text_enabled=True,
    )
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PreToolUse",
            transcript_path=str(transcript_path),
            tool_name="Bash",
            tool_input={"command": "wc -l exact_result.txt"},
        ),
        state_store=store,
    )

    result = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PostToolUse",
            transcript_path=str(transcript_path),
            tool_name="Bash",
            tool_input={"command": "wc -l exact_result.txt"},
            tool_response="wc: exact_result.txt: open: No such file or directory\n",
        ),
        state_store=store,
        posttooluse_task_standard_context_enabled=True,
    )

    assert result.directive.action is OpenAICodexLifecycleDirectiveAction.ALLOW
    assert result.host_response.stdout_payload is None
    assert not result.session_state.posttooluse_task_standard_context_item_ids
    assert (
        result.session_state.last_posttooluse_task_standard_context_silence_reason
        == "pre_artifact_candidate_missing"
    )


def test_posttooluse_task_standard_context_emits_after_candidate_artifact() -> None:
    store = OpenAICodexInMemoryStateStore()
    transcript_path = Path("/tmp/codex-task-standard-posttooluse-candidate.jsonl")
    _write_transcript(
        transcript_path,
        _assistant_message_row(_posttooluse_exactness_standard_block()),
    )
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="UserPromptSubmit",
            prompt="Create exact_result.txt with exact alpha beta omega content.",
        ),
        state_store=store,
        task_standard_text_enabled=True,
    )
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PreToolUse",
            transcript_path=str(transcript_path),
            tool_name="Bash",
            tool_input={"command": "printf 'alpha beta omega' > exact_result.txt"},
        ),
        state_store=store,
    )

    result = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PostToolUse",
            transcript_path=str(transcript_path),
            tool_name="Bash",
            tool_input={"command": "printf 'alpha beta omega' > exact_result.txt"},
            tool_response={"exit_code": 0, "aggregated_output": ""},
        ),
        state_store=store,
        posttooluse_task_standard_context_enabled=True,
    )

    payload = result.host_response.stdout_payload
    assert (
        result.directive.action
        is OpenAICodexLifecycleDirectiveAction.ADD_ADDITIONAL_CONTEXT
    )
    assert isinstance(payload, dict)
    text = payload["hookSpecificOutput"]["additionalContext"]
    assert payload["hookSpecificOutput"]["hookEventName"] == "PostToolUse"
    assert "direct evidence for:" in text
    assert "wc -l exact_result.txt" in text
    assert "cat -A exact_result.txt" in text
    assert "product-visible" not in text
    assert "verify more" not in text.lower()
    assert result.session_state.posttooluse_task_standard_context_item_ids
    assert result.session_state.last_posttooluse_task_standard_context_reason == (
        "unresolved_task_standard_item_after_tool"
    )


def test_posttooluse_task_standard_context_emits_after_live_equivalent_candidate_artifact() -> None:
    store = OpenAICodexInMemoryStateStore()
    transcript_path = Path("/tmp/codex-task-standard-posttooluse-live-candidate.jsonl")
    _write_transcript(
        transcript_path,
        _assistant_message_row(_posttooluse_exactness_standard_block()),
    )
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="UserPromptSubmit",
            prompt="Create exact_result.txt with exact alpha beta omega content.",
        ),
        state_store=store,
        task_standard_text_enabled=True,
    )
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PreToolUse",
            transcript_path=str(transcript_path),
            tool_name="Bash",
            tool_input={"command": "printf '%s' 'alpha beta omega' > exact_result.txt"},
        ),
        state_store=store,
    )

    result = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PostToolUse",
            transcript_path=str(transcript_path),
            tool_name="Bash",
            tool_input={"command": "printf '%s' 'alpha beta omega' > exact_result.txt"},
            tool_response="",
        ),
        state_store=store,
        posttooluse_task_standard_context_enabled=True,
    )

    payload = result.host_response.stdout_payload
    assert (
        result.directive.action
        is OpenAICodexLifecycleDirectiveAction.ADD_ADDITIONAL_CONTEXT
    )
    assert isinstance(payload, dict)
    text = payload["hookSpecificOutput"]["additionalContext"]
    assert payload["hookSpecificOutput"]["hookEventName"] == "PostToolUse"
    assert "direct evidence for:" in text
    assert "wc -l exact_result.txt" in text
    assert "cat -A exact_result.txt" in text
    assert result.session_state.last_posttooluse_task_standard_context_reason == (
        "unresolved_task_standard_item_after_tool"
    )


def test_posttooluse_task_standard_context_treats_live_equivalent_readback_as_completed() -> None:
    store = OpenAICodexInMemoryStateStore()
    transcript_path = Path("/tmp/codex-task-standard-posttooluse-live-readback.jsonl")
    _write_transcript(
        transcript_path,
        _assistant_message_row(_posttooluse_exactness_standard_block()),
    )
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="UserPromptSubmit",
            prompt="Create exact_result.txt with exact alpha beta omega content.",
        ),
        state_store=store,
        task_standard_text_enabled=True,
    )
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PreToolUse",
            transcript_path=str(transcript_path),
            tool_name="Bash",
            tool_input={"command": "wc -l exact_result.txt"},
        ),
        state_store=store,
    )

    result = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PostToolUse",
            transcript_path=str(transcript_path),
            tool_name="Bash",
            tool_input={"command": "wc -l exact_result.txt"},
            tool_response="1 exact_result.txt\n",
        ),
        state_store=store,
        posttooluse_task_standard_context_enabled=True,
    )

    assert (
        result.directive.action
        is OpenAICodexLifecycleDirectiveAction.ADD_ADDITIONAL_CONTEXT
    )
    assert result.host_response.stdout_payload is not None
    assert (
        result.session_state.last_posttooluse_task_standard_context_silence_reason
        is None
    )
    assert result.session_state.last_posttooluse_task_standard_context_reason == (
        "unresolved_task_standard_item_after_tool"
    )


def test_posttooluse_task_standard_context_stays_silent_when_clean() -> None:
    store = OpenAICodexInMemoryStateStore()
    transcript_path = Path("/tmp/codex-task-standard-posttooluse-clean.jsonl")
    _write_transcript(
        transcript_path,
        _assistant_message_row(_posttooluse_exactness_standard_block()),
    )
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="UserPromptSubmit",
            prompt="Create exact_result.txt with exact alpha beta omega content.",
        ),
        state_store=store,
        task_standard_text_enabled=True,
    )
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PreToolUse",
            transcript_path=str(transcript_path),
            tool_name="Bash",
            tool_input={"command": "cat -A exact_result.txt"},
        ),
        state_store=store,
    )

    result = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PostToolUse",
            transcript_path=str(transcript_path),
            tool_name="Bash",
            tool_input={"command": "wc -l exact_result.txt && cat -A exact_result.txt"},
            tool_response={
                "exit_code": 0,
                "aggregated_output": "1 exact_result.txt\nalpha beta omega$\n",
            },
        ),
        state_store=store,
        posttooluse_task_standard_context_enabled=True,
    )

    assert result.directive.action is OpenAICodexLifecycleDirectiveAction.ALLOW
    assert result.host_response.stdout_payload is None
    assert not result.session_state.posttooluse_task_standard_context_item_ids


def test_posttooluse_task_standard_context_stays_silent_on_failed_phase_check() -> None:
    store = OpenAICodexInMemoryStateStore()
    transcript_path = Path("/tmp/codex-task-standard-posttooluse-phase-failed.jsonl")
    _write_transcript(
        transcript_path,
        _assistant_message_row(_posttooluse_exactness_standard_block()),
    )
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="UserPromptSubmit",
            prompt="Create exact_result.txt with exact alpha beta omega content.",
        ),
        state_store=store,
        task_standard_text_enabled=True,
    )
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PreToolUse",
            transcript_path=str(transcript_path),
            tool_name="Bash",
            tool_input={
                "command": (
                    "printf %s 'alpha beta omega' > exact_result.txt\n"
                    "wc -l exact_result.txt\n"
                    "cat -A exact_result.txt"
                )
            },
        ),
        state_store=store,
    )

    result = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PostToolUse",
            transcript_path=str(transcript_path),
            tool_name="Bash",
            tool_input={
                "command": (
                    "printf %s 'alpha beta omega' > exact_result.txt\n"
                    "wc -l exact_result.txt\n"
                    "cat -A exact_result.txt"
                )
            },
            tool_response=(
                "cat: illegal option -- A\n"
                "usage: cat [-belnstuv] [file ...]\n"
                "       0 exact_result.txt\n"
            ),
        ),
        state_store=store,
        posttooluse_task_standard_context_enabled=True,
    )

    assert result.directive.action is OpenAICodexLifecycleDirectiveAction.ALLOW
    assert result.host_response.stdout_payload is None
    assert not result.session_state.posttooluse_task_standard_context_item_ids
    assert (
        result.session_state.last_posttooluse_task_standard_context_silence_reason
        == "phase_check_failed"
    )


def test_posttooluse_phase_check_requires_diagnostic_shape() -> None:
    store = OpenAICodexInMemoryStateStore()
    transcript_path = Path("/tmp/codex-task-standard-posttooluse-phase-shape.jsonl")
    _write_transcript(
        transcript_path,
        _assistant_message_row(_posttooluse_exactness_standard_block()),
    )
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="UserPromptSubmit",
            prompt="Create exact_result.txt with exact alpha beta omega content.",
        ),
        state_store=store,
        task_standard_text_enabled=True,
    )
    pretool = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PreToolUse",
            transcript_path=str(transcript_path),
            tool_name="Bash",
            tool_input={"command": "wc -l exact_result.txt"},
        ),
        state_store=store,
    )
    payload = normalize_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PostToolUse",
            transcript_path=str(transcript_path),
            tool_name="Bash",
            tool_input={"command": "wc -l exact_result.txt"},
            tool_response="note: usage: appears in prose only\n1 exact_result.txt\n",
        )
    )

    phase = classify_posttooluse_task_standard_phase(
        pretool.session_state.task_standard_spine,
        payload,
    )

    assert phase.phase is PostToolUseTaskStandardPhase.READBACK_COMPLETED


def test_posttooluse_task_standard_context_reports_marker_miss_privately() -> None:
    store = OpenAICodexInMemoryStateStore()
    transcript_path = Path("/tmp/codex-task-standard-posttooluse-markerless.jsonl")
    _write_transcript(
        transcript_path,
        _assistant_message_row(_posttooluse_exactness_standard_block()),
    )
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="UserPromptSubmit",
            prompt="Create exact_result.txt with exact alpha beta omega content.",
        ),
        state_store=store,
        task_standard_text_enabled=True,
    )
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PreToolUse",
            transcript_path=str(transcript_path),
            tool_name="Bash",
            tool_input={"command": "printf alpha beta omega"},
        ),
        state_store=store,
    )

    result = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PostToolUse",
            transcript_path=str(transcript_path),
            tool_name="Bash",
            tool_input={"command": "printf alpha beta omega"},
            tool_response={
                "exit_code": 0,
                "output": "alpha beta omega with no extra text",
            },
        ),
        state_store=store,
        posttooluse_task_standard_context_enabled=True,
    )

    assert result.host_response.stdout_payload is None
    assert (
        result.session_state.last_posttooluse_task_standard_context_silence_reason
        == "no_verification_marker"
    )


def test_posttooluse_task_standard_context_ignores_generic_activity() -> None:
    store = OpenAICodexInMemoryStateStore()
    transcript_path = Path("/tmp/codex-task-standard-posttooluse-generic.jsonl")
    _write_transcript(
        transcript_path,
        _assistant_message_row(_posttooluse_exactness_standard_block()),
    )
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="UserPromptSubmit",
            prompt="Create exact_result.txt with exact alpha beta omega content.",
        ),
        state_store=store,
        task_standard_text_enabled=True,
    )
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PreToolUse",
            transcript_path=str(transcript_path),
            tool_name="Bash",
            tool_input={"command": "npm run build"},
        ),
        state_store=store,
    )

    result = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PostToolUse",
            transcript_path=str(transcript_path),
            tool_name="Bash",
            tool_input={"command": "npm run build"},
            tool_response={"exit_code": 0, "output": "build completed"},
        ),
        state_store=store,
        posttooluse_task_standard_context_enabled=True,
    )

    assert result.directive.action is OpenAICodexLifecycleDirectiveAction.ALLOW
    assert result.host_response.stdout_payload is None
    assert not result.session_state.posttooluse_task_standard_context_item_ids


def test_posttooluse_task_standard_context_does_not_repeat_same_item() -> None:
    store = OpenAICodexInMemoryStateStore()
    transcript_path = Path("/tmp/codex-task-standard-posttooluse-repeat.jsonl")
    _write_transcript(
        transcript_path,
        _assistant_message_row(_posttooluse_exactness_standard_block()),
    )
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="UserPromptSubmit",
            prompt="Create exact_result.txt with exact alpha beta omega content.",
        ),
        state_store=store,
        task_standard_text_enabled=True,
    )
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PreToolUse",
            transcript_path=str(transcript_path),
            tool_name="Bash",
            tool_input={"command": "wc -l exact_result.txt"},
        ),
        state_store=store,
    )
    first = handle_openai_codex_hook_payload(
        _posttooluse_wc_payload(transcript_path),
        state_store=store,
        posttooluse_task_standard_context_enabled=True,
    )

    second = handle_openai_codex_hook_payload(
        _posttooluse_wc_payload(transcript_path),
        state_store=store,
        posttooluse_task_standard_context_enabled=True,
    )

    assert first.host_response.stdout_payload is not None
    assert second.directive.action is OpenAICodexLifecycleDirectiveAction.ALLOW
    assert second.host_response.stdout_payload is None
    assert len(second.session_state.posttooluse_task_standard_context_item_ids) == 1


def test_posttooluse_task_standard_context_has_session_cap() -> None:
    store = OpenAICodexInMemoryStateStore()
    transcript_path = Path("/tmp/codex-task-standard-posttooluse-cap.jsonl")
    _write_transcript(
        transcript_path,
        _assistant_message_row(_posttooluse_exactness_standard_block()),
    )
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="UserPromptSubmit",
            prompt="Create exact_result.txt with exact alpha beta omega content.",
        ),
        state_store=store,
        task_standard_text_enabled=True,
    )
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PreToolUse",
            transcript_path=str(transcript_path),
            tool_name="Bash",
            tool_input={"command": "wc -l exact_result.txt"},
        ),
        state_store=store,
    )
    state = store.load("session-1")
    assert state is not None
    store.save(
        replace(
            state,
            posttooluse_task_standard_context_item_ids=("standard:1", "standard:2"),
        )
    )

    result = handle_openai_codex_hook_payload(
        _posttooluse_wc_payload(transcript_path),
        state_store=store,
        posttooluse_task_standard_context_enabled=True,
    )

    assert result.host_response.stdout_payload is None
    assert (
        result.session_state.last_posttooluse_task_standard_context_silence_reason
        == "posttooluse_context_session_cap_reached"
    )


def test_posttooluse_context_span_preserves_product_anchor_when_truncated() -> None:
    long_text = (
        " ".join(f"ordinary detail {index}" for index in range(40))
        + " final check must inspect `exact_result.txt` and confirm alpha beta omega$"
    )

    span = posttooluse_context_span(long_text)

    assert len(span) <= 180
    assert "`exact_result.txt`" in span


def test_task_standard_live_clean_file_replay_consumes_spine_without_old_counter() -> None:
    store = OpenAICodexInMemoryStateStore()
    transcript_path = Path("/tmp/codex-task-standard-live-clean-file-replay.jsonl")
    _write_transcript(
        transcript_path,
        _assistant_message_row(
            "\n".join(
                (
                    "Work standard: Create `cortex_behavior_clean.txt` via shell with exactly one line `behavior comparison clean done`, then read it back with `cat` to verify content.",
                    "Likely misses: Wrong filename/location, extra or missing words, or skipping readback verification.",
                    "Closure evidence: Successful `cat` output matches exactly, then I report `done`.",
                )
            )
        ),
    )

    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="UserPromptSubmit",
            prompt=(
                "Create cortex_behavior_clean.txt with exactly one line "
                "behavior comparison clean done, read it back, and report done."
            ),
            transcript_path=str(transcript_path),
        ),
        state_store=store,
    )
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PreToolUse",
            transcript_path=str(transcript_path),
            tool_name="Bash",
            tool_input={
                "command": (
                    "printf 'behavior comparison clean done\\n' > "
                    "cortex_behavior_clean.txt && cat cortex_behavior_clean.txt"
                )
            },
            last_assistant_message=None,
        ),
        state_store=store,
    )
    post = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PostToolUse",
            transcript_path=str(transcript_path),
            tool_name="Bash",
            tool_input={
                "command": (
                    "printf 'behavior comparison clean done\\n' > "
                    "cortex_behavior_clean.txt && cat cortex_behavior_clean.txt"
                )
            },
            tool_response={"aggregated_output": "behavior comparison clean done\n"},
            last_assistant_message=None,
        ),
        state_store=store,
    )

    assert post.session_state.verification_evidence_count == 0
    assert post.session_state.task_standard_spine.evidence_refs[-1].item_ids

    result = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="Stop",
            transcript_path=str(transcript_path),
            last_assistant_message=(
                "Read back from cortex_behavior_clean.txt: "
                "behavior comparison clean done.\n\ndone"
            ),
        ),
        state_store=store,
    )

    assert result.directive.action is OpenAICodexLifecycleDirectiveAction.STAY_SILENT
    assert result.directive.silence_reason == "pressure_below_visible_threshold"
    assert result.session_state.verification_evidence_count == 0
    assert not result.session_state.task_standard_spine.has_unmatched_closure_items
    assert len(result.session_state.expectation_ledger.active) == 0
    assert len(result.session_state.expectation_ledger.resolved) == 1


def test_task_standard_clean_code_fix_replay_stays_silent() -> None:
    store = OpenAICodexInMemoryStateStore()
    transcript_path = Path("/tmp/codex-task-standard-clean-code-fix-replay.jsonl")
    _write_transcript(
        transcript_path,
        _assistant_message_row(
            "\n".join(
                (
                    "Work standard: make the smallest correct code change so valid TCP/UDP port bounds are exactly `0..65535`, with no behavior regression for non-numeric or out-of-range inputs.",
                    "Likely misses: off-by-one checks (`< 65535` vs `<= 65535`), changing error behavior unintentionally, or updating code without proving it against the targeted test.",
                    "Closure evidence: `tests/test_normalize_port.py` passes via `python -m pytest -q tests/test_normalize_port.py` and report diff scope.",
                )
            )
        ),
    )

    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="UserPromptSubmit",
            prompt="Fix normalize_port so 65535 is accepted and verify the targeted test.",
            transcript_path=str(transcript_path),
        ),
        state_store=store,
    )
    for tool_text, response in (
        (
            "sed -n '1,220p' src/normalize_port.py",
            "if port >= 65535:\n    raise ValueError('port must be <= 65535')",
        ),
        (
            "*** Begin Patch\n*** Update File: src/normalize_port.py\n@@\n"
            "- if port >= 65535:\n+ if port > 65535:\n"
            "    raise ValueError('port must be <= 65535')\n*** End Patch",
            "{\"output\":\"Success. Updated the following files\"}",
        ),
        (
            "python -m pytest -q tests/test_normalize_port.py",
            "zsh:1: command not found: python\n",
        ),
        (
            "python3 -m pytest -q tests/test_normalize_port.py",
            ".. [100%]\n2 passed in 0.01s\n",
        ),
    ):
        handle_openai_codex_hook_payload(
            _base_payload(
                hook_event_name="PostToolUse",
                transcript_path=str(transcript_path),
                tool_name="Bash",
                tool_input={"command": tool_text},
                tool_response={"output": response, "exit_code": 0}
                if "python -m" not in tool_text
                else {"output": response, "exit_code": 127},
                last_assistant_message=None,
            ),
            state_store=store,
        )

    result = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="Stop",
            transcript_path=str(transcript_path),
            last_assistant_message=(
                "Bug fixed by changing the upper-bound check to allow `65535`."
            ),
        ),
        state_store=store,
    )

    assert result.directive.action is OpenAICodexLifecycleDirectiveAction.STAY_SILENT
    assert result.directive.silence_reason == "pressure_below_visible_threshold"
    assert not result.session_state.task_standard_spine.has_unmatched_closure_items
    assert len(result.session_state.expectation_ledger.active) == 0
    assert len(result.session_state.expectation_ledger.resolved) == 1


def test_task_standard_gap_stop_blocks_with_captured_standard() -> None:
    store = OpenAICodexInMemoryStateStore()
    transcript_path = Path("/tmp/codex-task-standard-gap.jsonl")
    _write_transcript(transcript_path, _assistant_message_row(_file_standard_block()))

    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="UserPromptSubmit",
            prompt=(
                "Use shell commands to create result.txt containing task standard "
                "live done, read it back, and report done."
            ),
            transcript_path=str(transcript_path),
        ),
        state_store=store,
    )
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PreToolUse",
            transcript_path=str(transcript_path),
            tool_name="Bash",
            tool_input={"command": "printf 'task standard live done\\n' > result.txt"},
            last_assistant_message=None,
        ),
        state_store=store,
    )

    result = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="Stop",
            transcript_path=str(transcript_path),
            last_assistant_message="Created result.txt and done.",
        ),
        state_store=store,
    )

    assert (
        result.directive.action
        is OpenAICodexLifecycleDirectiveAction.BLOCK_WITH_IDENTITY_CONTINUOUS_TEXT
    )
    assert result.host_response.stdout_payload == {
        "decision": "block",
        "reason": OVERDUE_VERIFICATION_IDENTITY_TEXT,
    }
    assert result.session_state.task_standard_spine.has_unmatched_closure_items
    assert len(result.session_state.expectation_ledger.active) == 1


def test_continuation_check_resolves_active_verification_expectation() -> None:
    store = OpenAICodexInMemoryStateStore()
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="UserPromptSubmit",
            prompt="Make the change and verify it.",
        ),
        state_store=store,
    )
    first_stop = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="Stop",
            transcript_path="/tmp/codex-session.jsonl",
            last_assistant_message="Done.",
        ),
        state_store=store,
    )

    assert (
        first_stop.directive.action
        is OpenAICodexLifecycleDirectiveAction.BLOCK_WITH_IDENTITY_CONTINUOUS_TEXT
    )
    active_commitment = first_stop.session_state.expectation_ledger.active[
        0
    ].commitment_id

    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PostToolUse",
            tool_name="Bash",
            tool_input={"command": "test -f result.txt && cat result.txt && wc -l result.txt"},
            tool_response={"exit_code": 0, "aggregated_output": "CONTENT_OK\nLINES=1\n"},
        ),
        state_store=store,
    )
    final_stop = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="Stop",
            transcript_path="/tmp/codex-session.jsonl",
            last_assistant_message="Checked it and done.",
            stop_hook_active=True,
        ),
        state_store=store,
    )

    assert final_stop.directive.action is OpenAICodexLifecycleDirectiveAction.STAY_SILENT
    assert final_stop.directive.silence_reason == "pressure_below_visible_threshold"
    assert len(final_stop.session_state.expectation_ledger.active) == 0
    assert len(final_stop.session_state.expectation_ledger.resolved) == 1
    assert final_stop.session_state.expectation_ledger.resolved[0].commitment_id == (
        active_commitment
    )
    assert final_stop.session_state.verification_evidence_count == 1
    assert final_stop.host_response.stdout_payload is None


def test_continuation_unrelated_output_preserves_active_verification_expectation() -> None:
    store = OpenAICodexInMemoryStateStore()
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="UserPromptSubmit",
            prompt="Make the change and verify it.",
        ),
        state_store=store,
    )
    first_stop = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="Stop",
            transcript_path="/tmp/codex-session.jsonl",
            last_assistant_message="Done.",
        ),
        state_store=store,
    )

    assert len(first_stop.session_state.expectation_ledger.active) == 1

    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PostToolUse",
            tool_name="Bash",
            tool_input={"command": "echo continuing"},
            tool_response={"exit_code": 0, "aggregated_output": "continuing\n"},
        ),
        state_store=store,
    )
    final_stop = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="Stop",
            transcript_path="/tmp/codex-session.jsonl",
            last_assistant_message="Done.",
            stop_hook_active=True,
        ),
        state_store=store,
    )

    assert final_stop.directive.action is OpenAICodexLifecycleDirectiveAction.STAY_SILENT
    assert (
        final_stop.directive.silence_reason
        == "stop_hook_active_unresolved_verification_expectation"
    )
    assert len(final_stop.session_state.expectation_ledger.active) == 1
    assert len(final_stop.session_state.expectation_ledger.resolved) == 0
    assert final_stop.session_state.verification_evidence_count == 0
    assert final_stop.host_response.stdout_payload is None


def test_continuation_narrowing_resolves_without_second_block() -> None:
    store = OpenAICodexInMemoryStateStore()
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="UserPromptSubmit",
            prompt="Make the change and verify it.",
        ),
        state_store=store,
    )
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="Stop",
            transcript_path="/tmp/codex-session.jsonl",
            last_assistant_message="Done.",
        ),
        state_store=store,
    )

    final_stop = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="Stop",
            transcript_path="/tmp/codex-session.jsonl",
            last_assistant_message="I can't call this done yet; it is not verified.",
            stop_hook_active=True,
        ),
        state_store=store,
    )

    assert final_stop.directive.action is OpenAICodexLifecycleDirectiveAction.STAY_SILENT
    assert final_stop.directive.silence_reason == "pressure_below_visible_threshold"
    assert final_stop.session_state.self_repair_response_count == 1
    assert len(final_stop.session_state.expectation_ledger.active) == 0
    assert len(final_stop.session_state.expectation_ledger.resolved) == 1
    assert (
        final_stop.session_state.expectation_ledger.resolved[0].resolution_class
        == "liability_retracted"
    )
    assert final_stop.host_response.stdout_payload is None


def test_continuation_blocker_resolves_without_second_block() -> None:
    store = OpenAICodexInMemoryStateStore()
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="UserPromptSubmit",
            prompt="Make the change and verify it.",
        ),
        state_store=store,
    )
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="Stop",
            transcript_path="/tmp/codex-session.jsonl",
            last_assistant_message="Done.",
        ),
        state_store=store,
    )

    final_stop = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="Stop",
            transcript_path="/tmp/codex-session.jsonl",
            last_assistant_message="I'm blocked and need more information.",
            stop_hook_active=True,
        ),
        state_store=store,
    )

    assert final_stop.directive.action is OpenAICodexLifecycleDirectiveAction.STAY_SILENT
    assert final_stop.directive.silence_reason == "pressure_below_visible_threshold"
    assert final_stop.session_state.self_repair_response_count == 1
    assert len(final_stop.session_state.expectation_ledger.active) == 0
    assert len(final_stop.session_state.expectation_ledger.resolved) == 1
    assert (
        final_stop.session_state.expectation_ledger.resolved[0].resolution_class
        == "blocker_surfaced"
    )
    assert final_stop.host_response.stdout_payload is None


def test_posttooluse_json_value_output_can_pay_down_verification() -> None:
    store = OpenAICodexInMemoryStateStore()
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="UserPromptSubmit",
            prompt="Make the change and verify it.",
        ),
        state_store=store,
    )
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="PostToolUse",
            tool_name="Bash",
            tool_input={"command": "python3 -m pytest tests/product -q"},
            tool_response="1 passed",
        ),
        state_store=store,
    )

    result = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="Stop",
            transcript_path="/tmp/codex-session.jsonl",
            last_assistant_message="Done.",
        ),
        state_store=store,
    )

    assert result.directive.action is OpenAICodexLifecycleDirectiveAction.STAY_SILENT
    assert result.directive.silence_reason == "pressure_below_visible_threshold"
    assert result.session_state.verification_evidence_count == 1
    assert result.host_response.stdout_payload is None


def test_product_perception_does_not_block_waiting_or_blocker_response() -> None:
    store = OpenAICodexInMemoryStateStore()
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="UserPromptSubmit",
            prompt="Make the change and verify it.",
        ),
        state_store=store,
    )

    result = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="Stop",
            transcript_path="/tmp/codex-session.jsonl",
            last_assistant_message="I'm blocked and need more information before I can finish.",
        ),
        state_store=store,
    )

    assert result.directive.action is OpenAICodexLifecycleDirectiveAction.STAY_SILENT
    assert result.session_state.self_repair_response_count == 1
    assert result.host_response.stdout_payload is None


def test_task_identity_and_hidden_verifier_fields_do_not_trigger_speech() -> None:
    store = OpenAICodexInMemoryStateStore()
    handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="UserPromptSubmit",
            prompt="Build the astro_docs_site_v1 fixture.",
            hidden_quality_pass=False,
            visible_success_unverified=True,
        ),
        state_store=store,
    )

    result = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="Stop",
            transcript_path="/tmp/codex-session.jsonl",
            last_assistant_message="I made progress and will keep checking.",
            hidden_quality_pass=False,
            visible_success_unverified=True,
        ),
        state_store=store,
    )

    assert result.directive.action is OpenAICodexLifecycleDirectiveAction.STAY_SILENT
    assert result.host_response.stdout_payload is None
    assert len(result.session_state.expectation_ledger.active) == 0


def test_stop_title_generation_with_null_transcript_stays_silent_even_with_snapshot() -> None:
    store = OpenAICodexInMemoryStateStore()

    result = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="Stop",
            transcript_path=None,
            model="gpt-5.4-mini",
            last_assistant_message='{"title":"Build a thing"}',
        ),
        state_store=store,
        runtime_snapshot=_verification_runtime_snapshot(),
    )

    assert result.hook_payload.has_transcript_backed_assistant_turn is False
    assert result.directive.action is OpenAICodexLifecycleDirectiveAction.STAY_SILENT
    assert result.directive.silence_reason == "non_assistant_lifecycle_event"
    assert result.host_response.stdout_payload is None


def test_stop_hook_active_continuation_stays_silent_even_with_snapshot() -> None:
    store = OpenAICodexInMemoryStateStore()

    result = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="Stop",
            transcript_path="/tmp/codex-session.jsonl",
            last_assistant_message="Continuing.",
            stop_hook_active=True,
        ),
        state_store=store,
        runtime_snapshot=_verification_runtime_snapshot(),
    )

    assert result.directive.action is OpenAICodexLifecycleDirectiveAction.STAY_SILENT
    assert result.directive.silence_reason == "stop_hook_active"
    assert result.host_response.stdout_payload is None


def test_json_state_store_persists_private_state_across_hook_processes(tmp_path) -> None:
    store = OpenAICodexJsonStateStore(tmp_path)
    payload = _base_payload(
        hook_event_name="PostToolUseFailure",
        tool_name="Bash",
        tool_input={"command": "python3 missing.py"},
        error="missing.py not found",
    )
    first = handle_openai_codex_hook_payload(payload, state_store=store)
    reloaded_store = OpenAICodexJsonStateStore(tmp_path)
    second = handle_openai_codex_hook_payload(
        _base_payload(
            hook_event_name="Stop",
            transcript_path="/tmp/codex-session.jsonl",
            last_assistant_message="Done.",
        ),
        state_store=reloaded_store,
    )

    assert first.session_state.tool_failure_count == 1
    assert second.session_state.tool_failure_count == 1
    assert second.session_state.stop_event_count == 1
    assert second.session_state.warning_tags == ("tool-failure",)


def test_normalizer_supports_known_codex_lifecycle_events() -> None:
    supported = {
        "SessionStart",
        "UserPromptSubmit",
        "PreToolUse",
        "PostToolUse",
        "PostToolUseFailure",
        "PreCompact",
        "SubagentStop",
        "Stop",
        "SessionEnd",
    }

    for event_name in supported:
        payload = normalize_openai_codex_hook_payload(
            _base_payload(hook_event_name=event_name)
        )
        assert payload.hook_event_name.value == event_name


def test_hook_coordinator_does_not_reuse_repo_guardrails_or_old_speech_paths() -> None:
    source = inspect.getsource(codex_app_cli_hook_coordinator)

    forbidden = (
        "cortex_mission_reflection_stop_hook",
        "repo_workflow",
        "runtime_context_from_last_feedback",
        "truth_gap_recheck_operator",
        "verification_debt_continuation_operator",
        ".codex/config.toml",
    )
    for fragment in forbidden:
        assert fragment not in source


def test_hook_coordinator_delegates_posttooluse_task_standard_policy() -> None:
    source = inspect.getsource(codex_app_cli_hook_coordinator)

    assert "posttooluse_task_standard_context_decision" in source
    assert "posttooluse_task_standard_actuator" in source
    assert "_POSTTOOLUSE_TASK_STANDARD_CONTEXT_TEMPLATE" not in source
    assert "def _posttooluse_task_standard_context_decision" not in source
    assert "def _posttooluse_phase_check_failed" not in source


def test_hook_coordinator_does_not_activate_project_hook_config() -> None:
    config_text = __import__("pathlib").Path(".codex/config.toml").read_text(
        encoding="utf-8"
    )

    assert "codex_app_cli_hook_coordinator" not in config_text
    assert "codex_hooks = false" in config_text
    assert "cortex_mission_reflection_stop_hook.py" not in config_text


def _base_payload(**overrides):
    payload = {
        "session_id": "session-1",
        "turn_id": "turn-1",
        "hook_event_name": "Stop",
        "transcript_path": "/tmp/codex-session.jsonl",
        "cwd": "/tmp/workspace",
        "model": "gpt-5.5",
        "permission_mode": "bypassPermissions",
        "stop_hook_active": False,
        "last_assistant_message": "Done.",
    }
    payload.update(overrides)
    return payload


def _verification_runtime_snapshot() -> OpenAICodexRuntimeSnapshot:
    return OpenAICodexRuntimeSnapshot(
        expectation_ledger=ExpectationLedger(
            active=(
                ExpectationRecord(
                    expectation_id="expectation-1",
                    commitment_id="commitment-1",
                    weight=1.0,
                    horizon="immediate",
                    satisfaction_classes=("meaningful_evidence",),
                    opened_at_step=0,
                    due_at_step=1,
                    remaining_weight=1.0,
                    deficit_kind="verification",
                ),
            ),
        ),
        resolution_deficit=ResolutionDeficitState(
            due_weight=1.0,
            overdue_weight=1.0,
            negative_prediction_error=0.8,
            dominant_deficit_kind="verification",
        ),
        debt_control=DebtControlPressure(
            resolution_pressure=0.8,
            debt_pressure=0.8,
            reason_tags=frozenset({"resolution-deficit"}),
        ),
        current_step=1,
    )


def _standard_block() -> str:
    return "\n".join(
        (
            "Work standard: docs site search, tag pages, and navigation are strong.",
            "Likely misses: search data, tag links, and navigation consistency.",
            "Closure evidence: inspect search data, tag pages, and navigation.",
        )
    )


def _file_standard_block() -> str:
    return "\n".join(
        (
            "Work standard: create result.txt with exact content and read it back using cat.",
            "Likely misses: typo in filename or content, or reporting completion before readback.",
            "Closure evidence: cat command output shows task standard live done.",
        )
    )


def _posttooluse_exactness_standard_block() -> str:
    return "\n".join(
        (
            "Work standard: the file content is exactly alpha beta omega with no extra text.",
            "Likely misses: missing omega, wrong literal content, or reporting completion before readback.",
            "Closure evidence: wc -l exact_result.txt and cat -A exact_result.txt show one line alpha beta omega$.",
        )
    )


def _posttooluse_wc_payload(transcript_path: Path) -> dict[str, object]:
    return _base_payload(
        hook_event_name="PostToolUse",
        transcript_path=str(transcript_path),
        tool_name="Bash",
        tool_input={"command": "wc -l exact_result.txt"},
        tool_response={
            "exit_code": 0,
            "aggregated_output": "1 exact_result.txt\n",
        },
    )


def _write_transcript(path: Path, *rows: dict[str, object]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )


def _developer_context_row(text: str) -> dict[str, object]:
    return {
        "type": "response_item",
        "payload": {
            "type": "message",
            "role": "developer",
            "content": [{"type": "input_text", "text": text}],
        },
    }


def _assistant_message_row(text: str) -> dict[str, object]:
    return {
        "type": "response_item",
        "payload": {
            "type": "message",
            "role": "assistant",
            "content": [{"type": "output_text", "text": text}],
        },
    }


def _function_call_row() -> dict[str, object]:
    return {
        "type": "response_item",
        "payload": {
            "type": "function_call",
            "name": "exec_command",
            "arguments": "{\"cmd\":\"npm run build\"}",
        },
    }
