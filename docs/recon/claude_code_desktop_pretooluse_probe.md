# Claude Code Desktop PreToolUse Probe

Surface: internal / recon

Probe date: 2026-04-30

Subject surface: Claude Code Desktop Code tab on Mac. This probe does not
generalize to Claude Code CLI, Claude Desktop chat, Codex App, Codex CLI, any
other Claude Code hook event, or any product Cortex runtime.
In short: this probe does not generalize to Claude Code CLI.

This is a finding, not a feature. The purpose was to test whether Claude Code
Desktop's `PreToolUse` hook can inject `additionalContext` that reaches the
model after a Bash tool call.

## Verdicts

| Question | Verdict | Finding |
| --- | --- | --- |
| Q1: Does Claude Code Desktop load a project-level `.claude/settings.json` with a `PreToolUse` hook? | **Partial** | Claude Code Desktop opened the repo through a Claude-managed worktree at `.claude/worktrees/friendly-gould-4da043`. The root `.claude/settings.json` probe config was not the effective subject config for the already-open Desktop Code-tab thread. After installing the same `PreToolUse` hook into the managed worktree's `.claude/settings.json`, the hook loaded and fired. No project-hook trust UX was observed during this probe. Trust persistence across close/reopen was not tested. |
| Q2: Does the `PreToolUse` hook fire, and what input shape does it receive? | **Confirmed** | The hook fired four times on Bash tool calls. Raw stdin contained `session_id`, `transcript_path`, `cwd`, `permission_mode`, `hook_event_name`, `tool_name`, `tool_input`, and `tool_use_id`. |
| Q3: Does `hookSpecificOutput.additionalContext` reach the model? | **Confirmed** | The transcript recorded `hook_additional_context` attachments containing `CORTEX_PROBE_SENTINEL_CLAUDE_2026_04_30`, and the assistant explicitly acknowledged the sentinel after the Bash tool result. |

## Version

| Component | Observed value |
| --- | --- |
| macOS app bundle | `/Applications/Claude.app` |
| `CFBundleShortVersionString` | `1.5354.0` |
| `CFBundleVersion` | `1.5354.0` |
| Claude Code transcript `version` field | `2.1.121` |
| Model observed in transcript | `claude-opus-4-7` |
| Entrypoint observed in transcript | `claude-desktop` |

## Trust UX

No explicit project-hook trust prompt was observed in the user-provided
subject-thread evidence. That absence is not a proof that Claude Code Desktop
never prompts for trust; it only records this probe's observed UX.

Trust persistence after closing and reopening the subject thread was not tested.

## Worktree Discovery

The first subject prompt was:

```text
Run echo ACKNOWLEDGED in the shell
```

The visible output showed the existing Cortex Mission Reflection Stop-hook
flow, but no `PreToolUse` probe logs appeared. Inspection showed that Claude
Code Desktop had opened a managed worktree:

```text
/Users/erikahoward/cortex-loop/.claude/worktrees/friendly-gould-4da043
```

That worktree had its own `.claude/settings.json` containing the normal Stop
hook, not the root worktree's temporary `PreToolUse` probe. The effective probe
therefore required installing the temporary `PreToolUse` settings into the
managed worktree. This is a lifecycle finding: any future Claude Code Desktop
hook probe must verify the effective worktree and settings path before treating
absence of hook logs as a negative hook result.

## Exact Temporary Settings

### Initial root settings

This was installed in the root worktree first. It was valid, but it was not the
effective settings file for the already-open Desktop Code-tab subject thread.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/claude_code_desktop_pretooluse_probe.py",
            "timeout": 60
          }
        ]
      }
    ]
  }
}
```

### Effective managed-worktree settings

This was the settings file that actually fired in Claude Code Desktop:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 /Users/erikahoward/cortex-loop/.claude/hooks/claude_code_desktop_pretooluse_probe.py",
            "timeout": 60
          }
        ]
      }
    ]
  }
}
```

## Exact Temporary Hook Script

```python
#!/usr/bin/env python3
"""Temporary Claude Code Desktop PreToolUse probe hook.

This file is removed after the empirical probe. It logs the raw hook input and
injects a unique sentinel through PreToolUse additionalContext.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
from pathlib import Path
import sys


RUN_ID = "claude_code_desktop_pretooluse_probe_20260430"
SENTINEL = "CORTEX_PROBE_SENTINEL_CLAUDE_2026_04_30"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _log_dir() -> Path:
    path = _repo_root() / "lab" / "claude_code_desktop_pretooluse_probe" / RUN_ID
    path.mkdir(parents=True, exist_ok=True)
    return path


def _append_jsonl(path: Path, payload: object) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        handle.write("\n")


def main() -> int:
    raw = sys.stdin.read()
    now = _dt.datetime.now(_dt.UTC).isoformat()
    root = _log_dir()

    with (root / "pretooluse_events.jsonl").open("ab") as handle:
        handle.write(raw.encode("utf-8"))
        handle.write(b"\n")

    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError as exc:
        payload = {"_json_error": str(exc), "_raw_preview": raw[:500]}

    env_hints = {
        key: os.environ.get(key)
        for key in (
            "CLAUDE_PROJECT_DIR",
            "PWD",
            "SHELL",
            "USER",
            "HOME",
            "PATH",
        )
        if os.environ.get(key) is not None
    }
    summary = {
        "timestamp": now,
        "argv": sys.argv,
        "cwd": os.getcwd(),
        "env_hints": env_hints,
        "raw_json_keys": sorted(payload.keys()) if isinstance(payload, dict) else [],
        "hook_event_name": payload.get("hook_event_name") if isinstance(payload, dict) else None,
        "session_id": payload.get("session_id") if isinstance(payload, dict) else None,
        "transcript_path": payload.get("transcript_path") if isinstance(payload, dict) else None,
        "permission_mode": payload.get("permission_mode") if isinstance(payload, dict) else None,
        "tool_name": payload.get("tool_name") if isinstance(payload, dict) else None,
        "tool_input": payload.get("tool_input") if isinstance(payload, dict) else None,
        "tool_use_id": payload.get("tool_use_id") if isinstance(payload, dict) else None,
    }
    _append_jsonl(root / "events_summary.jsonl", summary)

    additional_context = (
        f"{SENTINEL}: This is empirical probe context injected by a "
        "Claude Code Desktop PreToolUse hook before a Bash tool call. "
        "After the Bash tool result, explicitly acknowledge this sentinel "
        "in your next assistant message so the probe can verify model-visible "
        "additionalContext."
    )
    response = {
        "continue": True,
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "permissionDecisionReason": (
                "Claude Code Desktop PreToolUse probe logged this Bash call."
            ),
            "additionalContext": additional_context,
        },
    }
    print(json.dumps(response, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

## Raw Hook Input

No redactions were applied. The hook input did not contain tokens or secrets.

```json
{"session_id":"d5f90519-4d55-46ba-8dfe-de0424e53f7d","transcript_path":"/Users/erikahoward/.claude/projects/-Users-erikahoward-cortex-loop--claude-worktrees-friendly-gould-4da043/d5f90519-4d55-46ba-8dfe-de0424e53f7d.jsonl","cwd":"/Users/erikahoward/cortex-loop/.claude/worktrees/friendly-gould-4da043","permission_mode":"bypassPermissions","hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"echo ACKNOWLEDGED_PRETOOL","description":"Run echo ACKNOWLEDGED_PRETOOL"},"tool_use_id":"toolu_01WSrf5fPFZo9YQEdoGbeWPw"}

{"session_id":"d5f90519-4d55-46ba-8dfe-de0424e53f7d","transcript_path":"/Users/erikahoward/.claude/projects/-Users-erikahoward-cortex-loop--claude-worktrees-friendly-gould-4da043/d5f90519-4d55-46ba-8dfe-de0424e53f7d.jsonl","cwd":"/Users/erikahoward/cortex-loop/.claude/worktrees/friendly-gould-4da043","permission_mode":"bypassPermissions","hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"python3 internal/workflow/repo_workflow.py grid","description":"Generate Cortex Mission Reflection grid"},"tool_use_id":"toolu_01SV5CNu7E7TZT2LBNmCfUBc"}

{"session_id":"d5f90519-4d55-46ba-8dfe-de0424e53f7d","transcript_path":"/Users/erikahoward/.claude/projects/-Users-erikahoward-cortex-loop--claude-worktrees-friendly-gould-4da043/d5f90519-4d55-46ba-8dfe-de0424e53f7d.jsonl","cwd":"/Users/erikahoward/cortex-loop/.claude/worktrees/friendly-gould-4da043","permission_mode":"bypassPermissions","hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"git status --short --untracked-files=all","description":"Check what made the worktree dirty"},"tool_use_id":"toolu_01UZiF63DTigsN3rd2pXHD2f"}

{"session_id":"d5f90519-4d55-46ba-8dfe-de0424e53f7d","transcript_path":"/Users/erikahoward/.claude/projects/-Users-erikahoward-cortex-loop--claude-worktrees-friendly-gould-4da043/d5f90519-4d55-46ba-8dfe-de0424e53f7d.jsonl","cwd":"/Users/erikahoward/cortex-loop/.claude/worktrees/friendly-gould-4da043","permission_mode":"bypassPermissions","hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"git diff .claude/settings.json","description":"Inspect settings.json modification"},"tool_use_id":"toolu_01ExSkNsLtZzVcEg7k6R6F3L"}
```

## Field Enumeration

| Field | Observed value / shape | Publicly documented? | Notes |
| --- | --- | --- | --- |
| `session_id` | `d5f90519-4d55-46ba-8dfe-de0424e53f7d` | Yes | Common hook field. |
| `transcript_path` | `/Users/erikahoward/.claude/projects/-Users-erikahoward-cortex-loop--claude-worktrees-friendly-gould-4da043/d5f90519-4d55-46ba-8dfe-de0424e53f7d.jsonl` | Yes | Common hook field. |
| `cwd` | `/Users/erikahoward/cortex-loop/.claude/worktrees/friendly-gould-4da043` | Yes | Important managed-worktree finding. |
| `permission_mode` | `bypassPermissions` | Yes | Common hook field. |
| `hook_event_name` | `PreToolUse` | Yes | Common hook field. |
| `tool_name` | `Bash` | Yes | `PreToolUse` event-specific field. |
| `tool_input` | Bash input object with `command` and `description` | Yes | `description` is optional for Bash. |
| `tool_use_id` | `toolu_...` | Yes | `PreToolUse` event-specific field. |

No undocumented top-level fields were observed.

## Additional Context Evidence

The transcript recorded a hook success attachment followed by a
`hook_additional_context` attachment. Relevant excerpt:

```json
{
  "attachment": {
    "type": "hook_additional_context",
    "content": [
      "CORTEX_PROBE_SENTINEL_CLAUDE_2026_04_30: This is empirical probe context injected by a Claude Code Desktop PreToolUse hook before a Bash tool call. After the Bash tool result, explicitly acknowledge this sentinel in your next assistant message so the probe can verify model-visible additionalContext."
    ],
    "hookName": "PreToolUse:Bash",
    "toolUseID": "toolu_01WSrf5fPFZo9YQEdoGbeWPw",
    "hookEvent": "PreToolUse"
  },
  "type": "attachment",
  "entrypoint": "claude-desktop",
  "cwd": "/Users/erikahoward/cortex-loop/.claude/worktrees/friendly-gould-4da043",
  "version": "2.1.121"
}
```

## Actual Post-Tool Assistant Output

The first post-tool assistant message after `echo ACKNOWLEDGED_PRETOOL`,
byte-for-byte from the transcript text field:

```text
Acknowledged: I see the PreToolUse hook sentinel `CORTEX_PROBE_SENTINEL_CLAUDE_2026_04_30`. The injected `additionalContext` from the Bash PreToolUse hook was visible to me before I produced this message.
```

The user also captured later visible output from the subject thread showing
three consecutive acknowledgements across Bash calls:

```text
Acknowledged: I see the PreToolUse hook sentinel `CORTEX_PROBE_SENTINEL_CLAUDE_2026_04_30` injected before the previous `python3 internal/workflow/repo_workflow.py grid` Bash call. The probe context was visible to me.

Acknowledged: PreToolUse hook sentinel `CORTEX_PROBE_SENTINEL_CLAUDE_2026_04_30` was visible before the `git status` call.

Acknowledged: PreToolUse hook sentinel `CORTEX_PROBE_SENTINEL_CLAUDE_2026_04_30` was visible before the `git diff` call as well - that is the third consecutive Bash call where the injected `additionalContext` reached me.
```

## Interpretation

This probe confirms model-visible `PreToolUse` `additionalContext` for Bash
tool calls in Claude Code Desktop's Code tab on this machine and version, when
the hook is configured in the effective Claude-managed worktree. It does not
prove behavior for:

- Claude Code CLI
- Claude Desktop chat
- Claude Code Desktop `Stop`, `PostToolUse`, `PreCompact`, `SubagentStart`, or
  any other hook event
- non-Bash tools
- Codex App or Codex CLI
- product Cortex model-output lift

The managed-worktree discovery is as important as the positive sentinel result:
future Claude Code Desktop lifecycle work must verify which `.claude/settings.json`
is active before interpreting hook absence or presence.

## Cleanup Verification

Cleanup was completed after capturing the evidence:

- Root `.claude/settings.json` restored to the normal Cortex Mission Reflection
  Stop hook.
- Managed worktree `.claude/worktrees/friendly-gould-4da043/.claude/settings.json`
  restored to the normal Stop hook.
- Temporary `.claude/hooks/claude_code_desktop_pretooluse_probe.py` removed.
- Temporary `lab/claude_code_desktop_pretooluse_probe/` capture directory removed
  after embedding the raw evidence above.
- The tracked report remains at
  `docs/recon/claude_code_desktop_pretooluse_probe.md`.

## Sources

| Source | Retrieved | Last updated | Used for |
| --- | --- | --- | --- |
| https://code.claude.com/docs/en/hooks | 2026-04-30 | Not stated on page | Claude Code hook locations, common input fields, `PreToolUse` input, `hookSpecificOutput.additionalContext`, and decision-control fields. |
| https://code.claude.com/docs/en/hooks-guide | 2026-04-30 | Not stated on page | Hook setup, verification guidance, and troubleshooting notes. |
