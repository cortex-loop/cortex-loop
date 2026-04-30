"""Ingress parsing for Claude Code Desktop hook payloads."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

_HOOK_EVENTS = frozenset(
    {
        "SessionStart",
        "UserPromptSubmit",
        "PreToolUse",
        "PostToolUse",
        "PreCompact",
        "SubagentStop",
        "Stop",
        "SessionEnd",
    }
)
_WIRED_EVENT_KINDS = frozenset({"pretooluse:bash"})


@dataclass(frozen=True, slots=True)
class ClaudeCodeDesktopHookEventEnvelope:
    hook_event_name: str
    payload: dict[str, Any]
    event_kind: str
    wired: bool = False

    def __post_init__(self) -> None:
        if self.hook_event_name not in _HOOK_EVENTS:
            raise ValueError(
                "ClaudeCodeDesktopHookEventEnvelope.hook_event_name must be one "
                f"of {sorted(_HOOK_EVENTS)!r}."
            )
        if not isinstance(self.payload, dict):
            actual_type = type(self.payload).__name__
            raise TypeError(
                "ClaudeCodeDesktopHookEventEnvelope.payload must be dict[str, Any], "
                f"got {actual_type}."
            )
        if not (isinstance(self.event_kind, str) and self.event_kind.strip()):
            raise ValueError(
                "ClaudeCodeDesktopHookEventEnvelope.event_kind must be non-empty."
            )
        if not isinstance(self.wired, bool):
            actual_type = type(self.wired).__name__
            raise TypeError(
                "ClaudeCodeDesktopHookEventEnvelope.wired must be bool, "
                f"got {actual_type}."
            )
        if self.wired and self.event_kind not in _WIRED_EVENT_KINDS:
            raise ValueError(
                "Only explicitly wired Claude Code Desktop hook event kinds may "
                f"set wired=True; got {self.event_kind!r}."
            )


def parse_claude_code_desktop_hook_event(
    payload: Mapping[str, Any],
) -> ClaudeCodeDesktopHookEventEnvelope:
    if not isinstance(payload, Mapping):
        actual_type = type(payload).__name__
        raise TypeError(
            "parse_claude_code_desktop_hook_event.payload must be a mapping, "
            f"got {actual_type}."
        )
    hook_event_name = _required_hook_event_name(payload)
    normalized_payload = dict(payload)
    if hook_event_name == "PreToolUse" and payload.get("tool_name") == "Bash":
        tool_input = payload.get("tool_input")
        if not isinstance(tool_input, Mapping):
            actual_type = type(tool_input).__name__
            raise TypeError(
                "Claude Code Desktop PreToolUse:Bash payload must include "
                f"tool_input as a mapping, got {actual_type}."
            )
        return ClaudeCodeDesktopHookEventEnvelope(
            hook_event_name=hook_event_name,
            payload=normalized_payload,
            event_kind="pretooluse:bash",
            wired=True,
        )
    return ClaudeCodeDesktopHookEventEnvelope(
        hook_event_name=hook_event_name,
        payload=normalized_payload,
        event_kind=_unwired_event_kind(hook_event_name, payload),
        wired=False,
    )


def _required_hook_event_name(payload: Mapping[str, Any]) -> str:
    raw_name = payload.get("hook_event_name")
    if not isinstance(raw_name, str):
        actual_type = type(raw_name).__name__
        raise TypeError(
            "Claude Code Desktop hook payload must include string hook_event_name, "
            f"got {actual_type}."
        )
    stripped = raw_name.strip()
    if stripped not in _HOOK_EVENTS:
        raise ValueError(
            "Claude Code Desktop hook_event_name must be one of "
            f"{sorted(_HOOK_EVENTS)!r}, got {raw_name!r}."
        )
    return stripped


def _unwired_event_kind(hook_event_name: str, payload: Mapping[str, Any]) -> str:
    if hook_event_name in {"PreToolUse", "PostToolUse"}:
        tool_name = payload.get("tool_name")
        if isinstance(tool_name, str) and tool_name.strip():
            return f"{hook_event_name.lower()}:{tool_name.strip().lower()}:unwired"
    return f"{hook_event_name.lower()}:unwired"


__all__ = [
    "ClaudeCodeDesktopHookEventEnvelope",
    "parse_claude_code_desktop_hook_event",
]
