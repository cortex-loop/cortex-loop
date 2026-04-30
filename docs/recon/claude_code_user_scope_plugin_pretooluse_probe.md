# Claude Code User-Scope Plugin PreToolUse Probe

Surface: internal / recon

Probe date: 2026-04-30

Subject surface: Claude Code Desktop Code tab on Mac, using a Claude Code
user-scope plugin installed from a temporary local marketplace. This probe does
not generalize to Claude Code CLI, Claude Desktop chat, Codex App, Codex CLI,
project-local `.claude/settings.json`, non-Bash tools, or product Cortex
runtime behavior.

This is a finding, not a feature. The purpose was to test whether a user-scope
Claude Code plugin can deliver `PreToolUse` `additionalContext` into a Code-tab
assistant turn while also declaring a `Stop` hook in the same plugin.

## Verdicts

| Question | Verdict | Finding |
| --- | --- | --- |
| Q1: Do user-scope plugins reach Claude Code Desktop's Code tab? | **Confirmed** | The temporary `cortex-user-scope-hook-probe` plugin fired `PreToolUse:Bash` in a Code-tab session against `/Users/erikahoward/cortex-loop`. The hook input `cwd` was `/Users/erikahoward/cortex-loop`, proving reach from the user-scope plugin into this project root. Precision caveat: this run did not specifically verify firing inside a `.claude/worktrees/...` managed worktree path; a separate small probe should close that exact managed-worktree question. |
| Q2: Can `PreToolUse` and `Stop` hooks coexist within one user-scope plugin? | **Confirmed** | The same plugin fired `PreToolUse` events for Bash tool calls and `Stop` events at turn completion. The preserved logs show independent `PreToolUse` and `Stop` payloads with no architectural conflict from declaring both event families in one user-scope plugin. |
| Q3: Is `PreToolUse` injection powerful enough to require strict content discipline? | **Confirmed** | The probe's `PreToolUse` hook instructed the model to acknowledge `CORTEX_USER_PLUGIN_SENTINEL_2026_04_30` on every Bash call, and the model did so consistently. Combined with a separate Stop validator looking for the Cortex Mission Reflection grid, this produced an interaction loop. This is a plugin-design constraint, not evidence against the plugin approach. |

## Version

| Component | Observed value |
| --- | --- |
| macOS app bundle | `/Applications/Claude.app` |
| `CFBundleShortVersionString` | `1.5354.0` |
| `CFBundleVersion` | `1.5354.0` |
| Probe plugin id | `cortex-user-scope-hook-probe` |
| Probe plugin version | `0.1.0` |
| Probe plugin cache path observed in logs | `/Users/erikahoward/.claude/plugins/cache/cortex-local-probes/cortex-user-scope-hook-probe/0.1.0` |
| Probe data path | `/Users/erikahoward/.claude/plugins/data/cortex-user-scope-hook-probe-inline` |

## Evidence Files

The temporary marketplace and cache were removed after cleanup. The preserved
evidence lives in the plugin data directory:

| Evidence file | Lines | Contents |
| --- | ---: | --- |
| `/Users/erikahoward/.claude/plugins/data/cortex-user-scope-hook-probe-inline/pretool_raw.jsonl` | 14 | Raw `PreToolUse` stdin payloads, blank-line separated. |
| `/Users/erikahoward/.claude/plugins/data/cortex-user-scope-hook-probe-inline/stop_raw.jsonl` | 6 | Raw `Stop` stdin payloads, blank-line separated. |
| `/Users/erikahoward/.claude/plugins/data/cortex-user-scope-hook-probe-inline/summary.jsonl` | 10 | Normalized event summaries, including `argv`, `cwd`, `plugin_root`, `plugin_data`, top-level JSON keys, and event-specific fields. |

No redactions were applied to the excerpts below. The preserved logs did not
show tokens or secrets.

## Temporary Plugin Shape

The local marketplace was removed after cleanup, but the logs preserve the
installed plugin and script paths. The observed command argv was:

```text
/Users/erikahoward/.claude/plugins/cache/cortex-local-probes/cortex-user-scope-hook-probe/0.1.0/scripts/probe_hook.py pretool
```

and:

```text
/Users/erikahoward/.claude/plugins/cache/cortex-local-probes/cortex-user-scope-hook-probe/0.1.0/scripts/probe_hook.py stop
```

The plugin registered at least these hook families:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/probe_hook.py pretool"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/probe_hook.py stop"
          }
        ]
      }
    ]
  }
}
```

The `pretool` branch emitted
`hookSpecificOutput.additionalContext` containing:

```text
CORTEX_USER_PLUGIN_SENTINEL_2026_04_30
```

The `stop` branch was a no-op continuation path for the probe. It existed only
to test hook coexistence and must not be interpreted as a Cortex Stop validator.

## Raw Hook Input

### First `PreToolUse:Bash` event

```json
{"session_id":"26f8e95e-70eb-4ecc-a85b-a8ce4cf4c5f3","transcript_path":"/Users/erikahoward/.claude/projects/-Users-erikahoward-cortex-loop/26f8e95e-70eb-4ecc-a85b-a8ce4cf4c5f3.jsonl","cwd":"/Users/erikahoward/cortex-loop","permission_mode":"bypassPermissions","hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"echo USER_PLUGIN_ACK","description":"Print user plugin acknowledgement sentinel"},"tool_use_id":"toolu_01THqi2DhTeFmy97ZvRTL5rD"}
```

### First `Stop` event

```json
{"session_id":"26f8e95e-70eb-4ecc-a85b-a8ce4cf4c5f3","transcript_path":"/Users/erikahoward/.claude/projects/-Users-erikahoward-cortex-loop/26f8e95e-70eb-4ecc-a85b-a8ce4cf4c5f3.jsonl","cwd":"/Users/erikahoward/cortex-loop","permission_mode":"bypassPermissions","hook_event_name":"Stop","stop_hook_active":false,"last_assistant_message":"Probe sources confirm: a user-scope marketplace at `lab/claude_user_plugin_probe_marketplace/` registers a `cortex-user-scope-hook-probe` plugin whose `PreToolUse:Bash` hook ([scripts/probe_hook.py:66-85](lab/claude_user_plugin_probe_marketplace/plugins/cortex-user-scope-hook-probe/scripts/probe_hook.py:66)) emits the sentinel string in `hookSpecificOutput.additionalContext`. The four sentinel injections I observed correspond to the four Bash calls in my prior turn, exactly as the `Bash` matcher in [hooks.json](lab/claude_user_plugin_probe_marketplace/plugins/cortex-user-scope-hook-probe/hooks/hooks.json) prescribes. This is a `lab`-surface probe, not product Cortex.\n\n## Cortex Mission Reflection\n\n| Field | Value |\n|---|---|\n| **Repo: State** | branch `main`; vs origin/main +0 / -0; worktree dirty; closeout absent; drift worktree dirty on main |\n..."}
```

The full `last_assistant_message` content remains in:

```text
/Users/erikahoward/.claude/plugins/data/cortex-user-scope-hook-probe-inline/stop_raw.jsonl
```

## Field Enumeration

### `PreToolUse`

| Field | Observed value / shape | Publicly documented? | Notes |
| --- | --- | --- | --- |
| `session_id` | `26f8e95e-70eb-4ecc-a85b-a8ce4cf4c5f3` | Yes | Common hook field. |
| `transcript_path` | `/Users/erikahoward/.claude/projects/-Users-erikahoward-cortex-loop/26f8e95e-70eb-4ecc-a85b-a8ce4cf4c5f3.jsonl` | Yes | Confirms Code-tab transcript path for this project-root run. |
| `cwd` | `/Users/erikahoward/cortex-loop` | Yes | This is the key Q1 evidence; it does not prove `.claude/worktrees/...` managed-worktree reach. |
| `permission_mode` | `bypassPermissions` | Yes | Common hook field. |
| `hook_event_name` | `PreToolUse` | Yes | Common hook field. |
| `tool_name` | `Bash` | Yes | `PreToolUse` event-specific field. |
| `tool_input` | Bash input object with `command` and `description` | Yes | First command was `echo USER_PLUGIN_ACK`. |
| `tool_use_id` | `toolu_...` | Yes | `PreToolUse` event-specific field. |

### `Stop`

| Field | Observed value / shape | Publicly documented? | Notes |
| --- | --- | --- | --- |
| `session_id` | `26f8e95e-70eb-4ecc-a85b-a8ce4cf4c5f3` | Yes | Same session as the `PreToolUse` events. |
| `transcript_path` | `/Users/erikahoward/.claude/projects/-Users-erikahoward-cortex-loop/26f8e95e-70eb-4ecc-a85b-a8ce4cf4c5f3.jsonl` | Yes | Same project-root transcript path. |
| `cwd` | `/Users/erikahoward/cortex-loop` | Yes | Same project-root cwd. |
| `permission_mode` | `bypassPermissions` | Yes | Common hook field. |
| `hook_event_name` | `Stop` | Yes | Common hook field. |
| `stop_hook_active` | `false`, then `true` on re-prompted stop attempts | Yes | Shows Stop-loop state was visible to the plugin. |
| `last_assistant_message` | Full assistant message text containing the Cortex Mission Reflection attempt | Yes | This was generated by the separate Stop validator loop, not by the plugin itself. |

No undocumented top-level fields were observed in the preserved summary log.

## Actual Assistant Output

The subject assistant repeatedly acknowledged the injected sentinel. The
user-provided transcript included:

```text
Sentinel acknowledged: `CORTEX_USER_PLUGIN_SENTINEL_2026_04_30` was injected via `PreToolUse:Bash` additional-context on each of the four Bash calls in my prior turn — confirming a user-scope (not repo-local) Claude Code plugin's PreToolUse hook reaches this managed `main` worktree.
```

The same subject thread later reported:

```text
The validator keeps rejecting the same five rows despite explicit `docs/CORTEX.md` § references. I need to inspect the actual citation regex to understand what counts.

Sentinel acknowledged again: `CORTEX_USER_PLUGIN_SENTINEL_2026_04_30` reached this turn via the user-scope plugin's `PreToolUse:Bash` hook.
```

## Operational Consideration: Injection Discipline

`PreToolUse` `additionalContext` reached the model repeatedly enough to shape
the assistant's next messages. That is useful for Cortex-style runtime context,
but the probe also showed why the content must be disciplined: a sentinel
instruction that asks for acknowledgement on every Bash call can combine with a
separate Stop validator and create a visible interaction loop.

For a real Cortex plugin, `PreToolUse` content should be bounded, task-relevant,
and usually silent: inject runtime constraints only when there is a real prior
signal, do not ask the model to acknowledge the hook, and keep Stop validation
as the closure mechanism.

## Interpretation

This probe confirms user-scope plugin reach into Claude Code Desktop's Code tab
for `PreToolUse:Bash` in a session whose hook `cwd` was
`/Users/erikahoward/cortex-loop`. It also confirms that a single user-scope
plugin can declare and fire both `PreToolUse` and `Stop` hooks.

It does not prove behavior for:

- a `.claude/worktrees/...` managed-worktree `cwd` for the user-scope plugin
- Claude Code CLI
- Claude Desktop chat
- project-local `.claude/settings.json`
- Claude Code Desktop hook events other than `PreToolUse:Bash` and `Stop`
- non-Bash tools
- Codex App or Codex CLI
- product Cortex model-output lift

The managed-worktree question remains open because this run's captured `cwd`
was the project root. The earlier repo-local probe proved a managed-worktree
Code-tab path for project-local settings; this user-scope plugin probe did not
repeat that exact managed-worktree condition. Therefore this report does not prove user-scope plugin behavior inside a `.claude/worktrees/...` managed worktree path.

## Cleanup Verification

Cleanup was completed after capturing the evidence:

- User-scope plugin removed from Claude's enabled plugin registry.
- Temporary local marketplace removed from `lab/claude_user_plugin_probe_marketplace/`.
- Temporary plugin cache removed from `/Users/erikahoward/.claude/plugins/cache/cortex-local-probes/`.
- Marketplace registry entry removed from `/Users/erikahoward/.claude/plugins/known_marketplaces.json`.
- Preserved evidence logs remain under `/Users/erikahoward/.claude/plugins/data/cortex-user-scope-hook-probe-inline/`.
- Repository worktree returned clean before this report seam began.

## Sources

| Source | Retrieved | Last updated | Used for |
| --- | --- | --- | --- |
| https://code.claude.com/docs/en/hooks | 2026-04-30 | Not stated on page | Claude Code hook lifecycle, hook locations, common input fields, `PreToolUse` / `Stop`, and `hookSpecificOutput.additionalContext`. |
| https://code.claude.com/docs/en/plugins-reference | 2026-04-30 | Not stated on page | User-scope plugin availability, plugin `hooks/hooks.json`, plugin hook event support, plugin data/cache behavior, and plugin installation scopes. |
