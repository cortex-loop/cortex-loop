# Claude Code Desktop Cortex Host Adapter

Surface: product adapter / structural

Status: structural adapter skeleton. This document describes the host-adapter
pattern landed for Claude Code Desktop. It does not claim live model-output
lift or promote Claude Code Desktop to the shipping default.

## Pattern

Claude Code Desktop is represented as a Cortex host adapter, not as plugin-side
business logic. The plugin is transport wire; Cortex law lives under
`cortex/hosts/claude_code_desktop/` and reuses the existing Cortex math objects
already owned by `cortex/core/**`, `cortex/sre/**`, `cortex/runtime/**`, and
`cortex/aux/**`.

The v1 structural path is:

```text
Claude Code hook stdin
-> cortex/hosts/claude_code_desktop/ingress.py
-> cortex/hosts/claude_code_desktop/runtime.py
-> cortex/hosts/claude_code_desktop/hook_control.py
-> Claude hook JSON output
```

For the first build seam, only `PreToolUse:Bash` is wired end-to-end. Other
hook events parse to no-op transport stubs and do not mutate state. Those
stubs are explicit non-claims, not hidden product behavior.

## Code Homes

- `ingress.py` parses Claude Code Desktop hook payloads into a typed host event
  envelope. It rejects malformed `PreToolUse:Bash` payloads and marks
  unsupported hooks as unwired instead of pretending they are lifecycle proof.
- `runtime.py` defines `ClaudeCodeDesktopRuntimeSession`, a host-local carrier
  that mirrors the existing Claude runtime session shape. It delegates the
  wired Bash intent through the existing Claude runtime shell so shared Cortex
  dispatch, brake, feedback-window, modulator, and route law remain single
  owned.
- `hook_control.py` builds the Claude hook return JSON. For the wired path it
  converts prior non-clean `ReferenceRealizationFeedback` into bounded
  `hookSpecificOutput.additionalContext` through
  `cortex/hosts/runtime_context.py::runtime_context_from_last_feedback`.

The adapter does not introduce new math objects. It realizes host-specific
ingress and host-control boundaries for existing objects. Ownership stays with
the original modules recorded in the math-to-code map.

## Model-Visible Boundary

The model-visible boundary for this adapter is Claude Code Desktop hook output,
not an HTTP request body. The first structural bridge is:

```text
PreToolUse:Bash payload
-> parse_claude_code_desktop_hook_event(...)
-> run_claude_code_desktop_runtime_step(...)
-> build_claude_code_desktop_hook_output(...)
-> hookSpecificOutput.additionalContext
-> next assistant message after the Bash tool result
```

Clean prior feedback emits no context. Noisy prior feedback emits a bounded
`CORTEX_RUNTIME_CONTEXT_V1` block, capped at 720 characters and derived only
from the immediately prior feedback object. Observe mode updates runtime state
but emits no hook context.

## Plugin Skeleton

The lab skeleton lives at `lab/cortex_plugin_skeleton/`. It registers all eight
Claude Code Desktop hook events so packaging and lifecycle shape can be tested
without claiming all hooks are implemented:

- `PreToolUse:Bash` calls `scripts/cortex_pretool.py`, a thin transport wire.
- `SessionStart`, `UserPromptSubmit`, `PostToolUse`, `PreCompact`,
  `SubagentStop`, `Stop`, and `SessionEnd` call no-op stubs.

The skeleton remains a lab surface until a later empirical seam installs it in
Claude Code Desktop and proves live hook behavior. Shipping truth remains
`openai:operator_cli` until the status registry is explicitly changed by an
earned promotion seam.
