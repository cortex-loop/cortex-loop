"""Claude Code Desktop runtime adapter over the existing Cortex host law."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from cortex.hosts.claude.runtime import ClaudeRuntimeSession, ClaudeRuntimeStepResult
from cortex.hosts.claude.runtime import run_claude_runtime_step
from cortex.hosts.runtime_context import runtime_context_from_last_feedback
from cortex.sre.families import SoftControlFamily
from cortex.sre.feedback import (
    ReferenceRealizationFeedback,
    ReferenceRealizationFeedbackWindow,
)
from cortex.sre.modulators import ExecutiveModulatorMemory

from .hook_control import ClaudeCodeDesktopHookControlDirective
from .ingress import ClaudeCodeDesktopHookEventEnvelope

_CONTEXT_REASON = "Cortex runtime context from prior realization feedback."
_DENY_REASON_PREFIX = "Cortex blocked this tool call before execution"
_VALID_MODES = frozenset({"observe", "enforce"})


@dataclass(frozen=True, slots=True)
class ClaudeCodeDesktopRuntimeSession:
    session_id: str | None = None
    event_index: int = 0
    branch_registry: tuple[str, ...] = ("main",)
    active_track_ref: str = "main"
    pending_goal_refs: tuple[str, ...] = ()
    continuity_reminders: tuple[str, ...] = ()
    budget_history: tuple[str, ...] = ()
    brake_history: tuple[str, ...] = ()
    brake_tonic_history: tuple[float, ...] = ()
    last_selected_family: SoftControlFamily | None = None
    last_commitment_result_summary: str | None = None
    last_realization_feedback: ReferenceRealizationFeedback | None = None
    feedback_window: ReferenceRealizationFeedbackWindow = field(
        default_factory=ReferenceRealizationFeedbackWindow
    )
    executive_modulator_memory: ExecutiveModulatorMemory | None = None

    def __post_init__(self) -> None:
        normalized = self.to_claude_session()
        object.__setattr__(self, "session_id", normalized.session_id)
        object.__setattr__(self, "event_index", normalized.event_index)
        object.__setattr__(self, "branch_registry", normalized.branch_registry)
        object.__setattr__(self, "active_track_ref", normalized.active_track_ref)
        object.__setattr__(self, "pending_goal_refs", normalized.pending_goal_refs)
        object.__setattr__(self, "continuity_reminders", normalized.continuity_reminders)
        object.__setattr__(self, "budget_history", normalized.budget_history)
        object.__setattr__(self, "brake_history", normalized.brake_history)
        object.__setattr__(
            self, "brake_tonic_history", normalized.brake_tonic_history
        )
        object.__setattr__(self, "last_selected_family", normalized.last_selected_family)
        object.__setattr__(
            self,
            "last_commitment_result_summary",
            normalized.last_commitment_result_summary,
        )
        object.__setattr__(
            self, "last_realization_feedback", normalized.last_realization_feedback
        )
        object.__setattr__(self, "feedback_window", normalized.feedback_window)
        object.__setattr__(
            self,
            "executive_modulator_memory",
            normalized.executive_modulator_memory,
        )

    def to_claude_session(self) -> ClaudeRuntimeSession:
        return ClaudeRuntimeSession(
            session_id=self.session_id,
            event_index=self.event_index,
            branch_registry=self.branch_registry,
            active_track_ref=self.active_track_ref,
            pending_goal_refs=self.pending_goal_refs,
            continuity_reminders=self.continuity_reminders,
            budget_history=self.budget_history,
            brake_history=self.brake_history,
            brake_tonic_history=self.brake_tonic_history,
            last_selected_family=self.last_selected_family,
            last_commitment_result_summary=self.last_commitment_result_summary,
            last_realization_feedback=self.last_realization_feedback,
            feedback_window=self.feedback_window,
            executive_modulator_memory=self.executive_modulator_memory,
        )

    @classmethod
    def from_claude_session(
        cls,
        session: ClaudeRuntimeSession,
    ) -> "ClaudeCodeDesktopRuntimeSession":
        if not isinstance(session, ClaudeRuntimeSession):
            actual_type = type(session).__name__
            raise TypeError(
                "ClaudeCodeDesktopRuntimeSession.from_claude_session.session must "
                f"be ClaudeRuntimeSession, got {actual_type}."
            )
        return cls(
            session_id=session.session_id,
            event_index=session.event_index,
            branch_registry=session.branch_registry,
            active_track_ref=session.active_track_ref,
            pending_goal_refs=session.pending_goal_refs,
            continuity_reminders=session.continuity_reminders,
            budget_history=session.budget_history,
            brake_history=session.brake_history,
            brake_tonic_history=session.brake_tonic_history,
            last_selected_family=session.last_selected_family,
            last_commitment_result_summary=session.last_commitment_result_summary,
            last_realization_feedback=session.last_realization_feedback,
            feedback_window=session.feedback_window,
            executive_modulator_memory=session.executive_modulator_memory,
        )

    def as_summary(self) -> dict[str, Any]:
        return self.to_claude_session().as_summary()


@dataclass(frozen=True, slots=True)
class ClaudeCodeDesktopRuntimeStepResult:
    event: ClaudeCodeDesktopHookEventEnvelope
    session: ClaudeCodeDesktopRuntimeSession
    directive: ClaudeCodeDesktopHookControlDirective
    claude_runtime_result: ClaudeRuntimeStepResult | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.event, ClaudeCodeDesktopHookEventEnvelope):
            actual_type = type(self.event).__name__
            raise TypeError(
                "ClaudeCodeDesktopRuntimeStepResult.event must be "
                f"ClaudeCodeDesktopHookEventEnvelope, got {actual_type}."
            )
        if not isinstance(self.session, ClaudeCodeDesktopRuntimeSession):
            actual_type = type(self.session).__name__
            raise TypeError(
                "ClaudeCodeDesktopRuntimeStepResult.session must be "
                f"ClaudeCodeDesktopRuntimeSession, got {actual_type}."
            )
        if not isinstance(self.directive, ClaudeCodeDesktopHookControlDirective):
            actual_type = type(self.directive).__name__
            raise TypeError(
                "ClaudeCodeDesktopRuntimeStepResult.directive must be "
                f"ClaudeCodeDesktopHookControlDirective, got {actual_type}."
            )
        if self.claude_runtime_result is not None and not isinstance(
            self.claude_runtime_result,
            ClaudeRuntimeStepResult,
        ):
            actual_type = type(self.claude_runtime_result).__name__
            raise TypeError(
                "ClaudeCodeDesktopRuntimeStepResult.claude_runtime_result must be "
                f"ClaudeRuntimeStepResult | None, got {actual_type}."
            )


def run_claude_code_desktop_runtime_step(
    event: ClaudeCodeDesktopHookEventEnvelope,
    session: ClaudeCodeDesktopRuntimeSession | None = None,
    *,
    mode: str = "enforce",
    max_context_chars: int = 720,
    audit_intensity: str = "minimal",
) -> ClaudeCodeDesktopRuntimeStepResult:
    if not isinstance(event, ClaudeCodeDesktopHookEventEnvelope):
        actual_type = type(event).__name__
        raise TypeError(
            "run_claude_code_desktop_runtime_step.event must be "
            f"ClaudeCodeDesktopHookEventEnvelope, got {actual_type}."
        )
    if mode not in _VALID_MODES:
        raise ValueError(
            "run_claude_code_desktop_runtime_step.mode must be `observe` or `enforce`."
        )
    if isinstance(max_context_chars, bool) or not isinstance(max_context_chars, int):
        actual_type = type(max_context_chars).__name__
        raise TypeError(
            "run_claude_code_desktop_runtime_step.max_context_chars must be int, "
            f"got {actual_type}."
        )
    if not 1 <= max_context_chars <= 720:
        raise ValueError(
            "run_claude_code_desktop_runtime_step.max_context_chars must be in [1, 720]."
        )
    prior_session = _coerce_session(session)
    if not event.wired:
        return ClaudeCodeDesktopRuntimeStepResult(
            event=event,
            session=prior_session,
            directive=ClaudeCodeDesktopHookControlDirective.noop(event.hook_event_name),
        )

    claude_result = run_claude_runtime_step(
        "content_block_delta",
        _pretool_bash_as_claude_payload(event.payload),
        prior_session.to_claude_session(),
        audit_intensity=audit_intensity,
    )
    updated_session = ClaudeCodeDesktopRuntimeSession.from_claude_session(
        claude_result.session
    )
    directive = _directive_for_pretool_bash(
        prior_session=prior_session,
        hook_event_name=event.hook_event_name,
        claude_result=claude_result,
        mode=mode,
        max_context_chars=max_context_chars,
    )
    return ClaudeCodeDesktopRuntimeStepResult(
        event=event,
        session=updated_session,
        directive=directive,
        claude_runtime_result=claude_result,
    )


def _coerce_session(
    session: ClaudeCodeDesktopRuntimeSession | None,
) -> ClaudeCodeDesktopRuntimeSession:
    if session is None:
        return ClaudeCodeDesktopRuntimeSession()
    if not isinstance(session, ClaudeCodeDesktopRuntimeSession):
        actual_type = type(session).__name__
        raise TypeError(
            "run_claude_code_desktop_runtime_step.session must be "
            f"ClaudeCodeDesktopRuntimeSession | None, got {actual_type}."
        )
    return session


def _directive_for_pretool_bash(
    *,
    prior_session: ClaudeCodeDesktopRuntimeSession,
    hook_event_name: str,
    claude_result: ClaudeRuntimeStepResult,
    mode: str,
    max_context_chars: int,
) -> ClaudeCodeDesktopHookControlDirective:
    blocked_reason = claude_result.operator_route.blocked_reason
    if mode == "enforce" and blocked_reason is not None:
        return ClaudeCodeDesktopHookControlDirective(
            hook_event_name=hook_event_name,
            permission_decision="deny",
            permission_decision_reason=_bounded_reason(
                f"{_DENY_REASON_PREFIX}: {blocked_reason}."
            ),
            additional_context=_bounded_optional_context(
                runtime_context_from_last_feedback(
                    prior_session.last_realization_feedback
                ),
                max_context_chars=max_context_chars,
            ),
            suppress_output=False,
        )

    context = runtime_context_from_last_feedback(prior_session.last_realization_feedback)
    if mode == "enforce" and context is not None:
        return ClaudeCodeDesktopHookControlDirective(
            hook_event_name=hook_event_name,
            permission_decision="allow",
            permission_decision_reason=_CONTEXT_REASON,
            additional_context=_bounded_optional_context(
                context,
                max_context_chars=max_context_chars,
            ),
            suppress_output=False,
        )
    return ClaudeCodeDesktopHookControlDirective.noop(hook_event_name)


def _pretool_bash_as_claude_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, Mapping):
        raise TypeError("PreToolUse:Bash payload must include mapping tool_input.")
    command = _optional_string(tool_input.get("command")) or "<missing command>"
    tool_use_id = _optional_string(payload.get("tool_use_id")) or "pretool-bash"
    session_id = _optional_string(payload.get("session_id"))
    synthetic: dict[str, Any] = {
        "message_id": f"claude-code-desktop:{tool_use_id}",
        "delta_type": "text_delta",
        "delta": f"PreToolUse Bash intent: {_truncate(command, 280)}",
        "tool_name": "Bash",
        "tool_input": dict(tool_input),
        "externally_consequential": _bash_command_may_mutate(command),
    }
    if session_id is not None:
        synthetic["session_id"] = session_id
    cwd = _optional_string(payload.get("cwd"))
    if cwd is not None:
        synthetic["current_workspace_ref"] = cwd
    transcript_path = _optional_string(payload.get("transcript_path"))
    if transcript_path is not None:
        synthetic["external_record_ref"] = transcript_path
    return synthetic


def _bash_command_may_mutate(command: str) -> bool:
    lowered = command.lower()
    mutation_tokens = (
        ">",
        "apply_patch",
        "cat >",
        "chmod ",
        "cp ",
        "git commit",
        "git mv",
        "mkdir ",
        "mv ",
        "python -c",
        "python3 -c",
        "rm ",
        "sed -i",
        "tee ",
        "touch ",
    )
    return any(token in lowered for token in mutation_tokens)


def _bounded_optional_context(context: str | None, *, max_context_chars: int) -> str | None:
    if context is None:
        return None
    if len(context) > max_context_chars:
        return context[: max_context_chars - 3] + "..."
    return context


def _bounded_reason(reason: str, *, max_chars: int = 360) -> str:
    if len(reason) <= max_chars:
        return reason
    return reason[: max_chars - 3] + "..."


def _optional_string(value: object) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _truncate(value: str, max_chars: int) -> str:
    if len(value) <= max_chars:
        return value
    return value[: max_chars - 3] + "..."


__all__ = [
    "ClaudeCodeDesktopRuntimeSession",
    "ClaudeCodeDesktopRuntimeStepResult",
    "run_claude_code_desktop_runtime_step",
]
