"""Product locks for the Codex App/CLI product hook coordinator."""

from __future__ import annotations

import inspect

from cortex.hosts.openai import codex_app_cli_hook_coordinator
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
from cortex.sre.task_standard import TASK_STANDARD_FORMATION_TEXT
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
