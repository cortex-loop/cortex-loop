#!/usr/bin/env python3
"""Shared lab transport helpers for the Cortex plugin skeleton."""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys


def _repo_root() -> Path:
    override = os.environ.get("CORTEX_LOOP_REPO_ROOT")
    if override:
        return Path(override)
    return Path(__file__).resolve().parents[5]


def _ensure_repo_import() -> None:
    root = str(_repo_root())
    if root not in sys.path:
        sys.path.insert(0, root)


def run_pretool() -> int:
    _ensure_repo_import()
    from cortex.hosts.claude_code_desktop.hook_control import (
        build_claude_code_desktop_hook_output,
    )
    from cortex.hosts.claude_code_desktop.ingress import (
        parse_claude_code_desktop_hook_event,
    )
    from cortex.hosts.claude_code_desktop.runtime import (
        run_claude_code_desktop_runtime_step,
    )

    payload = json.loads(sys.stdin.read() or "{}")
    event = parse_claude_code_desktop_hook_event(payload)
    result = run_claude_code_desktop_runtime_step(
        event,
        mode=os.environ.get("CORTEX_PLUGIN_MODE", "observe"),
    )
    print(json.dumps(build_claude_code_desktop_hook_output(result.directive)))
    return 0


def run_noop() -> int:
    _ensure_repo_import()
    from cortex.hosts.claude_code_desktop.hook_control import (
        ClaudeCodeDesktopHookControlDirective,
        build_claude_code_desktop_hook_output,
    )

    payload = json.loads(sys.stdin.read() or "{}")
    hook_event_name = payload.get("hook_event_name")
    if not isinstance(hook_event_name, str) or not hook_event_name.strip():
        hook_event_name = "Unhandled"
    directive = ClaudeCodeDesktopHookControlDirective.noop(hook_event_name)
    print(json.dumps(build_claude_code_desktop_hook_output(directive)))
    return 0
