"""Claude Code Desktop host adapter for Cortex lifecycle hooks."""

from .hook_control import (
    ClaudeCodeDesktopHookControlDirective,
    build_claude_code_desktop_hook_output,
)
from .ingress import (
    ClaudeCodeDesktopHookEventEnvelope,
    parse_claude_code_desktop_hook_event,
)
from .runtime import (
    ClaudeCodeDesktopRuntimeSession,
    ClaudeCodeDesktopRuntimeStepResult,
    run_claude_code_desktop_runtime_step,
)

__all__ = [
    "ClaudeCodeDesktopHookControlDirective",
    "ClaudeCodeDesktopHookEventEnvelope",
    "ClaudeCodeDesktopRuntimeSession",
    "ClaudeCodeDesktopRuntimeStepResult",
    "build_claude_code_desktop_hook_output",
    "parse_claude_code_desktop_hook_event",
    "run_claude_code_desktop_runtime_step",
]
