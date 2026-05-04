"""Pure Codex App/CLI lifecycle adaptor for product Cortex speech.

This module is product host-adaptor code. It consumes already-selected
grounded intervention decisions and lifecycle facts, then returns a typed
directive a future Codex App/CLI hook client can enact. It deliberately stays
separate from repo workflow guardrails.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from cortex.sre.interventions import (
    GroundedInterventionDecision,
    GroundedInterventionMode,
    InterventionRenderSurface,
    find_forbidden_model_visible_terms,
    render_grounded_intervention,
)


class OpenAICodexLifecycleEvent(str, Enum):
    USER_PROMPT_SUBMIT = "UserPromptSubmit"
    PRE_TOOL_USE = "PreToolUse"
    POST_TOOL_USE = "PostToolUse"
    STOP = "Stop"


class OpenAICodexLifecycleDirectiveAction(str, Enum):
    STAY_SILENT = "stay_silent"
    ALLOW = "allow"
    BLOCK_WITH_IDENTITY_CONTINUOUS_TEXT = "block_with_identity_continuous_text"


@dataclass(frozen=True, slots=True)
class OpenAICodexLifecycleFacts:
    hook_event_name: OpenAICodexLifecycleEvent
    transcript_path: str | None = None
    last_assistant_message: str | None = None
    stop_hook_active: bool = False
    prior_act_anchor: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.hook_event_name, OpenAICodexLifecycleEvent):
            actual_type = type(self.hook_event_name).__name__
            raise TypeError(
                "OpenAICodexLifecycleFacts.hook_event_name must be "
                f"OpenAICodexLifecycleEvent, got {actual_type}."
            )
        for field_name in ("transcript_path", "last_assistant_message"):
            value = getattr(self, field_name)
            if value is not None and not isinstance(value, str):
                actual_type = type(value).__name__
                raise TypeError(
                    f"OpenAICodexLifecycleFacts.{field_name} must be str | None, "
                    f"got {actual_type}."
                )
        if not isinstance(self.stop_hook_active, bool):
            actual_type = type(self.stop_hook_active).__name__
            raise TypeError(
                "OpenAICodexLifecycleFacts.stop_hook_active must be bool, "
                f"got {actual_type}."
            )
        if not isinstance(self.prior_act_anchor, bool):
            actual_type = type(self.prior_act_anchor).__name__
            raise TypeError(
                "OpenAICodexLifecycleFacts.prior_act_anchor must be bool, "
                f"got {actual_type}."
            )


@dataclass(frozen=True, slots=True)
class OpenAICodexLifecycleDirective:
    action: OpenAICodexLifecycleDirectiveAction
    hook_event_name: str
    model_visible_text: str | None = None
    silence_reason: str | None = None
    model_bound_difference_kind: str = "none"

    def __post_init__(self) -> None:
        if not isinstance(self.action, OpenAICodexLifecycleDirectiveAction):
            actual_type = type(self.action).__name__
            raise TypeError(
                "OpenAICodexLifecycleDirective.action must be "
                f"OpenAICodexLifecycleDirectiveAction, got {actual_type}."
            )
        if not isinstance(self.hook_event_name, str) or not self.hook_event_name.strip():
            raise ValueError(
                "OpenAICodexLifecycleDirective.hook_event_name must be non-empty."
            )
        if self.model_visible_text is not None and not (
            isinstance(self.model_visible_text, str) and self.model_visible_text.strip()
        ):
            raise ValueError(
                "OpenAICodexLifecycleDirective.model_visible_text must be non-empty "
                "when provided."
            )
        if self.silence_reason is not None and not (
            isinstance(self.silence_reason, str) and self.silence_reason.strip()
        ):
            raise ValueError(
                "OpenAICodexLifecycleDirective.silence_reason must be non-empty "
                "when provided."
            )
        if not (
            isinstance(self.model_bound_difference_kind, str)
            and self.model_bound_difference_kind.strip()
        ):
            raise ValueError(
                "OpenAICodexLifecycleDirective.model_bound_difference_kind must be "
                "non-empty."
            )

    def as_payload(self) -> dict[str, object]:
        return {
            "action": self.action.value,
            "hook_event_name": self.hook_event_name,
            "model_visible_text": self.model_visible_text,
            "silence_reason": self.silence_reason,
            "model_bound_difference_kind": self.model_bound_difference_kind,
        }


def build_openai_codex_app_cli_lifecycle_directive(
    *,
    grounded_intervention: GroundedInterventionDecision,
    lifecycle_facts: OpenAICodexLifecycleFacts,
) -> OpenAICodexLifecycleDirective:
    """Translate product runtime speech law into a Codex App/CLI lifecycle directive."""

    if not isinstance(grounded_intervention, GroundedInterventionDecision):
        actual_type = type(grounded_intervention).__name__
        raise TypeError(
            "grounded_intervention must be GroundedInterventionDecision, "
            f"got {actual_type}."
        )
    if not isinstance(lifecycle_facts, OpenAICodexLifecycleFacts):
        actual_type = type(lifecycle_facts).__name__
        raise TypeError(
            "lifecycle_facts must be OpenAICodexLifecycleFacts, "
            f"got {actual_type}."
        )

    if lifecycle_facts.hook_event_name is not OpenAICodexLifecycleEvent.STOP:
        return _allow(
            lifecycle_facts,
            "non_stop_lifecycle_state_update_only",
        )
    if lifecycle_facts.stop_hook_active:
        return _silent(lifecycle_facts, "stop_hook_active")
    if not _has_transcript_backed_assistant_turn(lifecycle_facts):
        return _silent(lifecycle_facts, "non_assistant_lifecycle_event")
    if grounded_intervention.mode is GroundedInterventionMode.STAY_SILENT:
        return _silent(
            lifecycle_facts,
            grounded_intervention.silence_reason or "grounded_intervention_silent",
        )
    if grounded_intervention.record is None:
        return _silent(lifecycle_facts, "missing_intervention_record")
    if not lifecycle_facts.prior_act_anchor:
        return _silent(lifecycle_facts, "missing_prior_act_anchor")

    rendered = render_grounded_intervention(
        grounded_intervention.record,
        surface=InterventionRenderSurface.IDENTITY_CONTINUOUS,
        prior_act_anchor=True,
    )
    forbidden = find_forbidden_model_visible_terms(rendered)
    if forbidden:
        return _silent(lifecycle_facts, "model_visible_forbidden_terms")
    return OpenAICodexLifecycleDirective(
        action=OpenAICodexLifecycleDirectiveAction.BLOCK_WITH_IDENTITY_CONTINUOUS_TEXT,
        hook_event_name=lifecycle_facts.hook_event_name.value,
        model_visible_text=rendered,
        silence_reason=None,
        model_bound_difference_kind="identity_continuous_threshold_text",
    )


def _has_transcript_backed_assistant_turn(facts: OpenAICodexLifecycleFacts) -> bool:
    return bool(
        isinstance(facts.transcript_path, str)
        and facts.transcript_path.strip()
        and isinstance(facts.last_assistant_message, str)
        and facts.last_assistant_message.strip()
    )


def _allow(
    facts: OpenAICodexLifecycleFacts,
    reason: str,
) -> OpenAICodexLifecycleDirective:
    return OpenAICodexLifecycleDirective(
        action=OpenAICodexLifecycleDirectiveAction.ALLOW,
        hook_event_name=facts.hook_event_name.value,
        model_visible_text=None,
        silence_reason=reason,
        model_bound_difference_kind="none",
    )


def _silent(
    facts: OpenAICodexLifecycleFacts,
    reason: str,
) -> OpenAICodexLifecycleDirective:
    return OpenAICodexLifecycleDirective(
        action=OpenAICodexLifecycleDirectiveAction.STAY_SILENT,
        hook_event_name=facts.hook_event_name.value,
        model_visible_text=None,
        silence_reason=reason,
        model_bound_difference_kind="none",
    )


__all__ = [
    "OpenAICodexLifecycleDirective",
    "OpenAICodexLifecycleDirectiveAction",
    "OpenAICodexLifecycleEvent",
    "OpenAICodexLifecycleFacts",
    "build_openai_codex_app_cli_lifecycle_directive",
]
