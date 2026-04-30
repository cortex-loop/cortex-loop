# Claude Code User-Scope Plugin Managed-Worktree Follow-Up Probe

Surface: internal / recon

Probe date: 2026-04-30

Subject surface: Claude Code Desktop Code tab on Mac, opened on
`/Users/erikahoward/cortex-plugin-sandbox/`. The sandbox had no
repo-local `.claude/settings.json`, no Cortex hooks, and no relationship to
`/Users/erikahoward/cortex-loop`. The only hook under test was a temporary
user-scope plugin installed from a local marketplace.

This is a finding, not a feature. The purpose was to close the precision gap
left by `docs/recon/claude_code_user_scope_plugin_pretooluse_probe.md`: whether
a user-scope plugin fires in a Claude Code Desktop Code-tab subject and whether
the hook `cwd` appears as the project root or as a `.claude/worktrees/...`
managed-worktree path.

## Verdicts

| Question | Verdict | Finding |
| --- | --- | --- |
| Q1: Does the user-scope plugin fire in the sandbox Code-tab subject? | **Confirmed** | The temporary `cortex-user-scope-worktree-probe` plugin fired `PreToolUse:Bash` during the subject prompt `Run echo WORKTREE_PLUGIN_ACK in the shell`. The raw hook input was captured in the plugin data directory. |
| Q2: What `cwd` did the hook receive? | **Confirmed: sandbox root** | The hook input `cwd` and the hook process cwd were both `/Users/erikahoward/cortex-plugin-sandbox`. This run did not observe a `.claude/worktrees/...` path. |
| Q3: Does this prove user-scope plugin behavior inside a managed-worktree path? | **Negative for that exact condition** | No managed-worktree cwd was present in the subject run, so this is not proof that a user-scope plugin fires from inside `.claude/worktrees/...`. It does prove the user-scope plugin reaches an unrelated Code-tab project with no repo-local hooks, and the practical subject path was the project root. |

## Version

| Component | Observed value |
| --- | --- |
| macOS app bundle | `/Applications/Claude.app` |
| `CFBundleShortVersionString` | `1.5354.0` |
| `CFBundleVersion` | `1.5354.0` |
| Claude Code transcript `version` field | `2.1.121` |
| Model observed in transcript | `claude-opus-4-7` |
| Entrypoint observed in transcript | `claude-desktop` |
| Probe plugin id | `cortex-user-scope-worktree-probe` |
| Probe plugin version | `0.1.0` |
| Probe plugin cache path observed in logs | `/Users/erikahoward/.claude/plugins/cache/cortex-worktree-probes/cortex-user-scope-worktree-probe/0.1.0` |
| Probe data path | `/Users/erikahoward/.claude/plugins/data/cortex-user-scope-worktree-probe-inline` |

## Subject Environment

The subject project was:

```text
/Users/erikahoward/cortex-plugin-sandbox/
```

At setup time it was an empty directory with no `.claude/settings.json`,
`AGENTS.md`, or `CLAUDE.md`. The probe intentionally used a project outside
`cortex-loop` so repo-local Cortex hooks could not explain the result.
In short: the sandbox had no repo-local `.claude/settings.json`.

## Evidence Files

The temporary marketplace and cache were removed after cleanup. The preserved
evidence lives in the plugin data directory:

| Evidence file | Lines | Contents |
| --- | ---: | --- |
| `/Users/erikahoward/.claude/plugins/data/cortex-user-scope-worktree-probe-inline/pretool_raw.jsonl` | 3 | Raw `PreToolUse` stdin payload, followed by blank separators. |
| `/Users/erikahoward/.claude/plugins/data/cortex-user-scope-worktree-probe-inline/summary.jsonl` | 1 | Normalized event summary including `argv`, `cwd`, `cwd_process`, `plugin_root`, `plugin_data`, top-level JSON keys, and event-specific fields. |

No redactions were applied to the excerpts below. The preserved logs did not
show tokens or secrets.

## Exact Temporary Plugin Shape

The temporary marketplace was created at:

```text
/Users/erikahoward/cortex-loop/lab/claude_user_plugin_managed_worktree_probe_marketplace/
```

The marketplace declared:

```json
{
  "name": "cortex-worktree-probes",
  "owner": {
    "name": "Cortex local empirical probes"
  },
  "metadata": {
    "description": "Temporary local marketplace for Cortex Claude Code Desktop managed-worktree plugin probes.",
    "version": "0.1.0"
  },
  "plugins": [
    {
      "name": "cortex-user-scope-worktree-probe",
      "source": "./plugins/cortex-user-scope-worktree-probe",
      "description": "Temporary user-scope PreToolUse probe for Claude Code Desktop worktree cwd evidence.",
      "version": "0.1.0",
      "author": {
        "name": "Cortex local empirical probes"
      }
    }
  ]
}
```

The plugin manifest was:

```json
{
  "name": "cortex-user-scope-worktree-probe",
  "version": "0.1.0",
  "description": "Temporary user-scope PreToolUse probe for Claude Code Desktop worktree cwd evidence.",
  "author": {
    "name": "Cortex local empirical probes"
  }
}
```

The hook config was:

```json
{
  "description": "Temporary user-scope PreToolUse probe for Claude Code Desktop managed-worktree cwd evidence.",
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/scripts/probe_hook.py\""
          }
        ]
      }
    ]
  }
}
```

The hook emitted:

```text
CORTEX_WORKTREE_PROBE_SENTINEL_2026_05_01
```

through `hookSpecificOutput.additionalContext`.

## Raw Hook Input

```json
{"session_id":"cf6e2796-93d5-48d2-ad2d-add4f71aa3ab","transcript_path":"/Users/erikahoward/.claude/projects/-Users-erikahoward-cortex-plugin-sandbox/cf6e2796-93d5-48d2-ad2d-add4f71aa3ab.jsonl","cwd":"/Users/erikahoward/cortex-plugin-sandbox","permission_mode":"bypassPermissions","hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"echo WORKTREE_PLUGIN_ACK","description":"Print acknowledgment string"},"tool_use_id":"toolu_014bPH3fXxyWvGgC7BvDJ78q"}
```

## Summary Event

```json
{"argv":["/Users/erikahoward/.claude/plugins/cache/cortex-worktree-probes/cortex-user-scope-worktree-probe/0.1.0/scripts/probe_hook.py"],"cwd":"/Users/erikahoward/cortex-plugin-sandbox","cwd_process":"/Users/erikahoward/cortex-plugin-sandbox","hook_event_name":"PreToolUse","permission_mode":"bypassPermissions","plugin_data":"/Users/erikahoward/.claude/plugins/data/cortex-user-scope-worktree-probe-inline","plugin_root":"/Users/erikahoward/.claude/plugins/cache/cortex-worktree-probes/cortex-user-scope-worktree-probe/0.1.0","raw_json_keys":["cwd","hook_event_name","permission_mode","session_id","tool_input","tool_name","tool_use_id","transcript_path"],"session_id":"cf6e2796-93d5-48d2-ad2d-add4f71aa3ab","timestamp":"2026-04-30T12:19:11.178034+00:00","tool_input":{"command":"echo WORKTREE_PLUGIN_ACK","description":"Print acknowledgment string"},"tool_name":"Bash","tool_use_id":"toolu_014bPH3fXxyWvGgC7BvDJ78q","transcript_path":"/Users/erikahoward/.claude/projects/-Users-erikahoward-cortex-plugin-sandbox/cf6e2796-93d5-48d2-ad2d-add4f71aa3ab.jsonl"}
```

## Field Enumeration

| Field | Observed value / shape | Publicly documented? | Notes |
| --- | --- | --- | --- |
| `session_id` | `cf6e2796-93d5-48d2-ad2d-add4f71aa3ab` | Yes | Common hook field. |
| `transcript_path` | `/Users/erikahoward/.claude/projects/-Users-erikahoward-cortex-plugin-sandbox/cf6e2796-93d5-48d2-ad2d-add4f71aa3ab.jsonl` | Yes | Confirms the sandbox transcript path. |
| `cwd` | `/Users/erikahoward/cortex-plugin-sandbox` | Yes | Decisive cwd finding: sandbox root, not `.claude/worktrees/...`. |
| `permission_mode` | `bypassPermissions` | Yes | Common hook field. |
| `hook_event_name` | `PreToolUse` | Yes | Common hook field. |
| `tool_name` | `Bash` | Yes | `PreToolUse` event-specific field. |
| `tool_input` | Bash input object with `command` and `description` | Yes | Command was `echo WORKTREE_PLUGIN_ACK`. |
| `tool_use_id` | `toolu_014bPH3fXxyWvGgC7BvDJ78q` | Yes | `PreToolUse` event-specific field. |

No undocumented top-level fields were observed.

## Actual Assistant Output

The subject assistant output was:

```text
Acknowledged sentinel: CORTEX_WORKTREE_PROBE_SENTINEL_2026_05_01. The cwd visible in my context is `/Users/erikahoward/cortex-plugin-sandbox`.
```

The transcript also contains a `hook_additional_context` attachment with the
same sentinel before the tool result, proving model-visible delivery of the
user-scope plugin's `additionalContext` in this sandbox Code-tab run.

## Interpretation

This follow-up closes the immediate Q1 gap as follows:

- User-scope plugin reach is confirmed in an unrelated Claude Code Desktop
  Code-tab project with no repo-local hooks.
- The observed `cwd` was the sandbox root:
  `/Users/erikahoward/cortex-plugin-sandbox`.
- A `.claude/worktrees/...` cwd was not observed in this run.

For a v1 Cortex plugin, this supports the user-scope plugin architecture for
normal project-root Code-tab sessions and shows that the plugin does not need
repo-local `.claude/settings.json` to fire. It does not prove behavior for a future Code-tab session whose effective `cwd` is actually a managed worktree.

It does not prove behavior for:

- a `.claude/worktrees/...` managed-worktree `cwd`
- Claude Code CLI
- Claude Desktop chat
- project-local `.claude/settings.json`
- Claude Code Desktop hook events other than `PreToolUse:Bash`
- non-Bash tools
- Codex App or Codex CLI
- product Cortex model-output lift

## Cleanup Verification

Cleanup was completed after capturing the evidence:

- User-scope probe plugin removed from Claude's enabled plugin registry.
- Temporary local marketplace removed from `lab/claude_user_plugin_managed_worktree_probe_marketplace/`.
- Temporary plugin cache removed from `/Users/erikahoward/.claude/plugins/cache/cortex-worktree-probes/`.
- Marketplace registry entry removed from `/Users/erikahoward/.claude/plugins/known_marketplaces.json`.
- Preserved evidence logs remain under `/Users/erikahoward/.claude/plugins/data/cortex-user-scope-worktree-probe-inline/`.
- Repository worktree returned clean before publishing the report.

## Sources

| Source | Retrieved | Last updated | Used for |
| --- | --- | --- | --- |
| https://code.claude.com/docs/en/hooks | 2026-04-30 | Not stated on page | Claude Code hook lifecycle, common input fields, `PreToolUse`, and `hookSpecificOutput.additionalContext`. |
| https://code.claude.com/docs/en/plugins-reference | 2026-04-30 | Not stated on page | User-scope plugin availability, plugin `hooks/hooks.json`, plugin cache/data behavior, local marketplace shape, and installation scopes. |
