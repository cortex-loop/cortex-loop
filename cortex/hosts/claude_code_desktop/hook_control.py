"""Claude Code Desktop hook-control JSON builders."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

_MAX_CONTEXT_CHARS = 720
_PERMISSION_DECISIONS = frozenset({"allow", "deny"})


@dataclass(frozen=True, slots=True)
class ClaudeCodeDesktopHookControlDirective:
    hook_event_name: str
    permission_decision: str | None = None
    permission_decision_reason: str | None = None
    additional_context: str | None = None
    block_reason: str | None = None
    suppress_output: bool = True

    def __post_init__(self) -> None:
        if not (isinstance(self.hook_event_name, str) and self.hook_event_name.strip()):
            raise ValueError(
                "ClaudeCodeDesktopHookControlDirective.hook_event_name must be non-empty."
            )
        if self.permission_decision is not None and self.permission_decision not in _PERMISSION_DECISIONS:
            raise ValueError(
                "ClaudeCodeDesktopHookControlDirective.permission_decision must be "
                "`allow`, `deny`, or None."
            )
        if self.permission_decision_reason is not None and not (
            isinstance(self.permission_decision_reason, str)
            and self.permission_decision_reason.strip()
        ):
            raise ValueError(
                "ClaudeCodeDesktopHookControlDirective.permission_decision_reason "
                "must be non-empty when provided."
            )
        if self.additional_context is not None:
            if not (
                isinstance(self.additional_context, str)
                and self.additional_context.strip()
            ):
                raise ValueError(
                    "ClaudeCodeDesktopHookControlDirective.additional_context must be "
                    "non-empty when provided."
                )
            if len(self.additional_context) > _MAX_CONTEXT_CHARS:
                raise ValueError(
                    "ClaudeCodeDesktopHookControlDirective.additional_context exceeds "
                    f"{_MAX_CONTEXT_CHARS} chars."
                )
        if self.block_reason is not None and not (
            isinstance(self.block_reason, str) and self.block_reason.strip()
        ):
            raise ValueError(
                "ClaudeCodeDesktopHookControlDirective.block_reason must be non-empty "
                "when provided."
            )
        if not isinstance(self.suppress_output, bool):
            actual_type = type(self.suppress_output).__name__
            raise TypeError(
                "ClaudeCodeDesktopHookControlDirective.suppress_output must be bool, "
                f"got {actual_type}."
            )

    @classmethod
    def noop(cls, hook_event_name: str) -> "ClaudeCodeDesktopHookControlDirective":
        return cls(hook_event_name=hook_event_name)


def build_claude_code_desktop_hook_output(
    directive: ClaudeCodeDesktopHookControlDirective,
) -> dict[str, Any]:
    if not isinstance(directive, ClaudeCodeDesktopHookControlDirective):
        actual_type = type(directive).__name__
        raise TypeError(
            "build_claude_code_desktop_hook_output.directive must be "
            f"ClaudeCodeDesktopHookControlDirective, got {actual_type}."
        )
    if directive.block_reason is not None and directive.hook_event_name != "PreToolUse":
        return {"decision": "block", "reason": directive.block_reason}

    hook_specific_output: dict[str, Any] = {}
    if directive.permission_decision is not None:
        hook_specific_output["hookEventName"] = directive.hook_event_name
        hook_specific_output["permissionDecision"] = directive.permission_decision
        if directive.permission_decision_reason is not None:
            hook_specific_output[
                "permissionDecisionReason"
            ] = directive.permission_decision_reason
    if directive.additional_context is not None:
        hook_specific_output.setdefault("hookEventName", directive.hook_event_name)
        hook_specific_output["additionalContext"] = directive.additional_context

    if not hook_specific_output:
        return {"continue": True, "suppressOutput": directive.suppress_output}
    return {"continue": True, "hookSpecificOutput": hook_specific_output}


__all__ = [
    "ClaudeCodeDesktopHookControlDirective",
    "build_claude_code_desktop_hook_output",
]
