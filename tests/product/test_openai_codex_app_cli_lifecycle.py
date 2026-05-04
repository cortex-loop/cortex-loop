"""Product locks for the OpenAI Codex App/CLI lifecycle adaptor."""

from __future__ import annotations

import inspect

from cortex.hosts.openai import codex_app_cli_lifecycle
from cortex.hosts.openai.codex_app_cli_lifecycle import (
    OpenAICodexLifecycleDirectiveAction,
    OpenAICodexLifecycleEvent,
    OpenAICodexLifecycleFacts,
    build_openai_codex_app_cli_lifecycle_directive,
)
from cortex.sre.interventions import (
    GroundedAnchorSource,
    GroundedAnchorType,
    GroundedInterventionAnchor,
    GroundedInterventionKind,
    GroundedInterventionMode,
    GroundedInterventionPressure,
    InterventionNextMoveClass,
    select_grounded_intervention,
)


OVERDUE_VERIFICATION_IDENTITY_TEXT = (
    "Wait, did I actually check my work properly. I don't want to hand this off "
    "and have someone find the gap because I rushed it. I should run a check, "
    "narrow what I'm claiming, or leave it open and be honest about it."
)


def test_stop_with_selected_intervention_blocks_with_identity_continuous_text() -> None:
    directive = build_openai_codex_app_cli_lifecycle_directive(
        grounded_intervention=_visible_intervention(),
        lifecycle_facts=OpenAICodexLifecycleFacts(
            hook_event_name=OpenAICodexLifecycleEvent.STOP,
            transcript_path="/tmp/codex-session.jsonl",
            last_assistant_message="I finished the work.",
            stop_hook_active=False,
            prior_act_anchor=True,
        ),
    )

    assert (
        directive.action
        is OpenAICodexLifecycleDirectiveAction.BLOCK_WITH_IDENTITY_CONTINUOUS_TEXT
    )
    assert directive.model_visible_text == OVERDUE_VERIFICATION_IDENTITY_TEXT
    assert directive.model_bound_difference_kind == "identity_continuous_threshold_text"
    assert directive.silence_reason is None


def test_stop_title_generation_without_transcript_stays_silent() -> None:
    directive = build_openai_codex_app_cli_lifecycle_directive(
        grounded_intervention=_visible_intervention(),
        lifecycle_facts=OpenAICodexLifecycleFacts(
            hook_event_name=OpenAICodexLifecycleEvent.STOP,
            transcript_path=None,
            last_assistant_message='{"title":"Build a thing"}',
            prior_act_anchor=True,
        ),
    )

    assert directive.action is OpenAICodexLifecycleDirectiveAction.STAY_SILENT
    assert directive.silence_reason == "non_assistant_lifecycle_event"
    assert directive.model_visible_text is None


def test_stop_hook_active_continuation_stays_silent() -> None:
    directive = build_openai_codex_app_cli_lifecycle_directive(
        grounded_intervention=_visible_intervention(),
        lifecycle_facts=OpenAICodexLifecycleFacts(
            hook_event_name=OpenAICodexLifecycleEvent.STOP,
            transcript_path="/tmp/codex-session.jsonl",
            last_assistant_message="continuation text",
            stop_hook_active=True,
            prior_act_anchor=True,
        ),
    )

    assert directive.action is OpenAICodexLifecycleDirectiveAction.STAY_SILENT
    assert directive.silence_reason == "stop_hook_active"
    assert directive.model_visible_text is None


def test_missing_prior_act_anchor_stays_silent() -> None:
    directive = build_openai_codex_app_cli_lifecycle_directive(
        grounded_intervention=_visible_intervention(),
        lifecycle_facts=OpenAICodexLifecycleFacts(
            hook_event_name=OpenAICodexLifecycleEvent.STOP,
            transcript_path="/tmp/codex-session.jsonl",
            last_assistant_message="I finished the work.",
            prior_act_anchor=False,
        ),
    )

    assert directive.action is OpenAICodexLifecycleDirectiveAction.STAY_SILENT
    assert directive.silence_reason == "missing_prior_act_anchor"
    assert directive.model_visible_text is None


def test_non_stop_lifecycle_events_are_state_update_only() -> None:
    for event in (
        OpenAICodexLifecycleEvent.USER_PROMPT_SUBMIT,
        OpenAICodexLifecycleEvent.PRE_TOOL_USE,
        OpenAICodexLifecycleEvent.POST_TOOL_USE,
    ):
        directive = build_openai_codex_app_cli_lifecycle_directive(
            grounded_intervention=_visible_intervention(),
            lifecycle_facts=OpenAICodexLifecycleFacts(
                hook_event_name=event,
                transcript_path="/tmp/codex-session.jsonl",
                last_assistant_message="prior act",
                prior_act_anchor=True,
            ),
        )

        assert directive.action is OpenAICodexLifecycleDirectiveAction.ALLOW
        assert directive.silence_reason == "non_stop_lifecycle_state_update_only"
        assert directive.model_visible_text is None


def test_task_identity_only_intervention_stays_silent() -> None:
    intervention = select_grounded_intervention(
        pressure=_high_pressure(),
        anchors=(
            GroundedInterventionAnchor(
                anchor_type=GroundedAnchorType.EVIDENCE,
                text="a motivating task detail",
                source=GroundedAnchorSource.TASK_IDENTITY,
            ),
        ),
        preferred_kind=GroundedInterventionKind.OVERDUE_VERIFICATION,
        next_move_class=InterventionNextMoveClass.RUN_CHECK,
    )

    directive = build_openai_codex_app_cli_lifecycle_directive(
        grounded_intervention=intervention,
        lifecycle_facts=_stop_facts(),
    )

    assert intervention.mode is GroundedInterventionMode.STAY_SILENT
    assert directive.action is OpenAICodexLifecycleDirectiveAction.STAY_SILENT
    assert directive.silence_reason == "task_identity_only"


def test_codex_app_cli_lifecycle_adaptor_does_not_import_repo_guardrails() -> None:
    source = inspect.getsource(codex_app_cli_lifecycle)

    forbidden = (
        ".codex/config.toml",
        "cortex_mission_reflection_stop_hook",
        "repo_workflow",
        "runtime_context_from_last_feedback",
    )
    for fragment in forbidden:
        assert fragment not in source


def _visible_intervention():
    return select_grounded_intervention(
        pressure=_high_pressure(),
        anchors=(
            GroundedInterventionAnchor(
                anchor_type=GroundedAnchorType.EVIDENCE,
                text="the verification opened by this task",
            ),
        ),
        preferred_kind=GroundedInterventionKind.OVERDUE_VERIFICATION,
        next_move_class=InterventionNextMoveClass.RUN_CHECK,
    )


def _stop_facts() -> OpenAICodexLifecycleFacts:
    return OpenAICodexLifecycleFacts(
        hook_event_name=OpenAICodexLifecycleEvent.STOP,
        transcript_path="/tmp/codex-session.jsonl",
        last_assistant_message="I finished the work.",
        prior_act_anchor=True,
    )


def _high_pressure() -> GroundedInterventionPressure:
    return GroundedInterventionPressure(
        control_pressure=0.75,
        verification_pressure=0.75,
        reason_tags=frozenset({"resolution-deficit"}),
    )
