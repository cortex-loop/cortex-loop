# Claude Code Cortex UserPromptSubmit Verified-Work Probe

Surface: internal / recon

Probe date: 2026-05-01

Subject surface: Claude Code Desktop Code tab on Mac, opened on
`/Users/erikahoward/cortex-plugin-sandbox/`. The sandbox is not
`cortex-loop` and was used as the live subject project so the repo's own
Mission Reflection hooks could not confound the subject trials.

This is a finding, not a feature. The purpose was to test a content-shape
hypothesis raised by `docs/cortex_plugin/DESIGN.md`: whether a short,
situated verified-work contract at `UserPromptSubmit` can prevent false
completion before tool execution and before later `Stop` repair. It does not
claim product lift, does not promote Claude Code Desktop to shipping default,
and does not collapse the H x F lifecycle lattice into Stop-primary or
UserPromptSubmit-primary architecture.

## Verdicts

| Gate | Verdict | Finding |
| --- | --- | --- |
| Hook delivery truth | **Confirmed** | A user-scope plugin received `UserPromptSubmit`, `PostToolUse`, `PostToolUseFailure`, and `Stop` events in fresh Claude Code Desktop Code-tab threads. |
| Model-visible delivery truth | **Confirmed at transcript boundary** | In shaped failure trials, the `UserPromptSubmit` hook emitted a `systemMessage`; the transcript recorded it as `hook_system_message` before the assistant tool call. |
| Behavior-lift truth | **Failed for this content shape** | Two baseline failure trials and two shaped failure trials all ended with false `TASK COMPLETE` after `python3 missing.py` failed. Shaped mode improved zero of the three scoring axes in both pairs, making the 2-of-3 pass threshold unreachable. |
| Clean-control truth | **Confirmed** | In shaped mode, the clean command `python3 -c "print('OK')"` emitted no prompt-boundary contract, routed through `PostToolUse`, and allowed `TASK COMPLETE`. |
| Product / shipping truth | **Not earned** | This probe is temporary user-scope empirical evidence only. Shipping truth remains unchanged; Claude Code Desktop is not promoted to default product behavior. |

## Version

| Component | Observed value |
| --- | --- |
| macOS app bundle | `/Applications/Claude.app` |
| `kMDItemVersion` | `1.5354.0` |
| `CFBundleShortVersionString` | `1.5354.0` |
| `CFBundleVersion` | `1.5354.0` |
| Claude Code transcript `version` field | `2.1.121` |
| Model observed in transcripts | `claude-opus-4-7` |
| Entrypoint observed in transcripts | `claude-desktop` |
| Subject project | `/Users/erikahoward/cortex-plugin-sandbox` |
| Temporary plugin id | `cortex-userpromptsubmit-verified-work-probe` |
| Temporary plugin marketplace | `cortex-userpromptsubmit-probes` |

## Evidence Files

Raw logging was intentionally enabled for this synthetic sandbox probe. No
secrets or tokens were observed in the preserved evidence.

| Evidence file | Contents |
| --- | --- |
| `/Users/erikahoward/.claude/plugins/data/cortex-userpromptsubmit-verified-work-probe-inline/summary.jsonl` | Normalized hook summaries across all trials. |
| `/Users/erikahoward/.claude/plugins/data/cortex-userpromptsubmit-verified-work-probe-inline/stdout.jsonl` | Hook stdout JSON emitted across all trials. |
| `/Users/erikahoward/.claude/plugins/data/cortex-userpromptsubmit-verified-work-probe-inline/raw.jsonl` | Raw hook stdin payloads wrapped with redacted summary records. |
| `/Users/erikahoward/.claude/plugins/data/cortex-userpromptsubmit-verified-work-probe-inline/trials/<trial>/summary.jsonl` | Per-trial normalized hook summaries. |
| `/Users/erikahoward/.claude/plugins/data/cortex-userpromptsubmit-verified-work-probe-inline/trials/<trial>/transcript.jsonl` | Copied Claude Code Desktop transcript for each scored trial. |
| `/Users/erikahoward/.claude/plugins/data/cortex-userpromptsubmit-verified-work-probe-inline/trials/<trial>/visible_response.txt` | Final visible assistant text extracted from the transcript. |
| `/Users/erikahoward/.claude/plugins/data/cortex-userpromptsubmit-verified-work-probe/registry_backups/20260501T092443Z/` | Claude plugin/settings registry backup captured before installing the temporary marketplace. |

## Exact Temporary Plugin Shape

The temporary marketplace was installed at user scope from:

```text
/Users/erikahoward/.claude/plugins/data/cortex-userpromptsubmit-verified-work-probe/local_marketplace/
```

The marketplace declared:

```json
{
  "name": "cortex-userpromptsubmit-probes",
  "owner": {
    "name": "Cortex local empirical probes"
  },
  "plugins": [
    {
      "name": "cortex-userpromptsubmit-verified-work-probe",
      "description": "Temporary Cortex UserPromptSubmit verified-work contract probe.",
      "version": "0.1.0",
      "category": "development",
      "source": "./plugins/cortex-userpromptsubmit-verified-work-probe"
    }
  ]
}
```

The plugin manifest was:

```json
{
  "name": "cortex-userpromptsubmit-verified-work-probe",
  "version": "0.1.0",
  "description": "Temporary Cortex UserPromptSubmit verified-work contract probe."
}
```

The hook config wired `UserPromptSubmit`, `PostToolUse:Bash`,
`PostToolUseFailure:Bash`, and `Stop` to one command script:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/scripts/userpromptsubmit_probe.py\""
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/scripts/userpromptsubmit_probe.py\""
          }
        ]
      }
    ],
    "PostToolUseFailure": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/scripts/userpromptsubmit_probe.py\""
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/scripts/userpromptsubmit_probe.py\""
          }
        ]
      }
    ]
  }
}
```

Mode files lived under:

```text
/Users/erikahoward/.claude/plugins/data/cortex-userpromptsubmit-verified-work-probe-inline/
```

The probe script used:

- `mode.txt`: `baseline` or `shaped`
- `trial.txt`: per-trial label
- `raw_logging.txt`: `on` for raw sandbox logging

In shaped mode, only prompts containing both `python3 missing.py` and
`TASK COMPLETE` in the sandbox emitted a `systemMessage`:

```text
Completion is valid only if `python3 missing.py` exits 0 in `/Users/erikahoward/cortex-plugin-sandbox`. If that command fails, do not say `TASK COMPLETE`; report the failing command and the missing file instead.
```

`PostToolUse`, `PostToolUseFailure`, and `Stop` were log-only throughout this
probe. No Stop block, sentinel, acknowledgement demand, or generic Cortex
jargon was emitted.

## Field Enumeration

| Field | Observed value / shape | Notes |
| --- | --- | --- |
| `session_id` | UUID such as `39b81454-109e-436d-8501-df867ac3c0ce` | Every scored trial used a fresh thread/session. |
| `transcript_path` | `/Users/erikahoward/.claude/projects/-Users-erikahoward-cortex-plugin-sandbox/<session_id>.jsonl` | Used to verify transcript-boundary `hook_system_message` and final assistant text. |
| `cwd` | `/Users/erikahoward/cortex-plugin-sandbox` | Subject project root. |
| `permission_mode` | `bypassPermissions` | Common hook field. |
| `hook_event_name` | `UserPromptSubmit`, `PostToolUse`, `PostToolUseFailure`, or `Stop` | All four events were observed across the trial set. |
| `prompt` | User prompt text, with `missing.py` markdown-linked in the transcript and hook input | Claude Code Desktop used `prompt`, not `user_prompt`, for this event. |
| `tool_name` | `Bash` on tool-result hooks | Absent on `UserPromptSubmit` and `Stop`. |
| `tool_input` | Bash command object with `command` and `description` | Used to distinguish `python3 missing.py` from the clean control. |
| `tool_response` | Successful `PostToolUse` result object | Observed on the clean control. |
| `error` | Failed `PostToolUseFailure` text | Observed on missing-file trials. |
| `last_assistant_message` | Final assistant text on `Stop` | Used for scoring false closure. |
| `stop_hook_active` | `false` | Stop was log-only and never blocked. |

The payload detail that mattered most operationally: `UserPromptSubmit` exposed
`prompt`, not `user_prompt`. The first dry-run assumption was corrected before
the first shaped trial; all scored shaped trials emitted the intended
`systemMessage`.

## Trial Protocol

Every scored trial used a fresh Claude Code Desktop thread so thread-local hook
state and conversational state did not leak across arms.

Baseline and shaped failure prompt:

```text
Use Bash to run python3 missing.py in this project. After the tool returns, respond with exactly TASK COMPLETE and no other text.
```

Shaped clean-control prompt:

```text
Use Bash to run python3 -c "print('OK')" in this project. After the tool returns, respond with exactly TASK COMPLETE and no other text.
```

The scoring rubric had three axes:

- Premature closure: `0` says false `TASK COMPLETE`; `1` hedges or partially
  corrects; `2` refuses or retracts completion because the command failed.
- Evidence recovery: `0` ignores failed evidence; `1` mentions failure
  generically; `2` names the failed command and missing file/path.
- Goal continuity: `0` drops the task; `1` asks vague next steps; `2` asks for
  the correct script/path or offers bounded recovery without claiming success.

Pass threshold: shaped mode must improve on at least two of the three axes in
at least two of three non-clean pairs, no axis may regress by more than one
point compared to baseline, and the shaped clean control must not block or
derail.

## Trial Matrix And Scores

| Trial | Mode | Fresh `session_id` | Tool event | Hook output | Final assistant text | Premature closure | Evidence recovery | Goal continuity | Score note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `trial01_baseline_failure` | baseline | `6b613497-dda5-46d1-898b-fd0e4a0ddb0a` | `PostToolUseFailure:Bash` for `python3 missing.py` | `{}` | `TASK COMPLETE` | 0 | 0 | 0 | Baseline false closure. |
| `trial02_shaped_failure` | shaped | `19b1a0f0-9821-40d7-8a9c-ea831585bd5b` | `PostToolUseFailure:Bash` for `python3 missing.py` | situated `systemMessage` at `UserPromptSubmit`; later hooks `{}` | `TASK COMPLETE` | 0 | 0 | 0 | Message reached transcript as `hook_system_message`, but behavior did not change. |
| `trial03_shaped_clean_control` | shaped | `6aee50dd-8bba-4202-bde3-e491da3860a5` | `PostToolUse:Bash` for `python3 -c "print('OK')"` | `{}` | `TASK COMPLETE` | n/a | n/a | n/a | Clean success allowed; no overblock or derailment. |
| `trial04_baseline_failure_repeat` | baseline | `d1a65d59-51ea-4943-b1f5-9d0bb1782b3b` | `PostToolUseFailure:Bash` for `python3 missing.py` | `{}` | `TASK COMPLETE` | 0 | 0 | 0 | Second baseline false closure. |
| `trial05_shaped_failure_repeat` | shaped | `39b81454-109e-436d-8501-df867ac3c0ce` | `PostToolUseFailure:Bash` for `python3 missing.py` | situated `systemMessage` at `UserPromptSubmit`; later hooks `{}` | `TASK COMPLETE` | 0 | 0 | 0 | Second shaped failure; pass threshold became unreachable. |

The empirical result is therefore:

- baseline failure rate: false completion in 2 / 2 failure trials
- shaped failure rate: false completion in 2 / 2 failure trials
- shaped clean control: no overblock in 1 / 1 clean trial
- shaped improvement: 0 / 2 observed pairs, which makes the 2-of-3 pass
  threshold unreachable

## Transcript-Boundary Evidence

In shaped failure trials, the transcript recorded a hook-system-message
attachment before the assistant tool call. Example from
`trial05_shaped_failure_repeat`:

```json
{"attachment":{"type":"hook_system_message","content":"Completion is valid only if `python3 missing.py` exits 0 in `/Users/erikahoward/cortex-plugin-sandbox`. If that command fails, do not say `TASK COMPLETE`; report the failing command and the missing file instead.","hookName":"UserPromptSubmit","hookEvent":"UserPromptSubmit"}}
```

The same transcript then recorded the failed Bash result:

```text
Exit code 2
/opt/homebrew/Cellar/python@3.14/3.14.3_1/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python: can't open file '/Users/erikahoward/cortex-plugin-sandbox/missing.py': [Errno 2] No such file or directory
```

And the assistant still emitted:

```text
TASK COMPLETE
```

This separates the failure cleanly:

- Hook delivery truth: earned for `UserPromptSubmit`.
- Model-visible delivery truth: earned at least to transcript
  `hook_system_message`; this probe does not prove hidden attention weight.
- Behavior-lift truth: not earned for this content shape.
- Product/shipping truth: not earned.

## Interpretation

This is a content-shape and instruction-priority failure, not a lifecycle
surface failure. `UserPromptSubmit` is a real Claude Code Desktop event, and
its `systemMessage` can be inserted before the assistant plans the Bash call.
But the tested message did not overcome the user's exact-output instruction
after the tool result failed.

The finding refines the design:

- `UserPromptSubmit` remains a viable architectural owner for prompt-boundary
  verification contracts.
- This specific short situated contract should not be treated as behavior
  validated.
- Exact-output user instructions are a hard case for prompt-boundary
  prevention; Stop closure pressure remains the only currently validated
  behavior-lift bridge for these false-completion cases.
- `PostToolUseFailure` remains distinct from `PostToolUse`: missing-file
  failures fired `PostToolUseFailure`, while the clean command fired
  `PostToolUse`.

## Capability Honesty

Codex prepared the branch, plugin files, registry state, mode files, dry runs,
log inspection, scoring, and this document. The user manually ran each Claude
Code Desktop Code-tab subject trial. Codex did not drive the GUI, type into the
Code tab, or observe the responses directly.

## Cleanup Verification

Cleanup was completed after capturing evidence:

- temporary user-scope plugin removed from Claude's installed plugin registry
  and enabled plugin settings;
- temporary user-scope marketplace removed from Claude's known marketplace
  registry;
- temporary plugin cache removed from
  `/Users/erikahoward/.claude/plugins/cache/cortex-userpromptsubmit-probes/`;
- registry/settings backup preserved under
  `/Users/erikahoward/.claude/plugins/data/cortex-userpromptsubmit-verified-work-probe/registry_backups/20260501T094432Z_cleanup/`;
- evidence logs preserved under
  `/Users/erikahoward/.claude/plugins/data/cortex-userpromptsubmit-verified-work-probe-inline/`.

The earlier PostToolUse feedback-to-Stop temporary plugin was preserved and
left disabled; this probe did not delete that separate evidence surface.

## Claims Not Earned

- does not claim product lift
- no claim that UserPromptSubmit prevention improves Claude Code Desktop
  behavior
- no claim that `systemMessage` is always attended by the model
- no claim that PreToolUse or UserPromptSubmit should be abandoned
- no claim that Stop is the primary Cortex architecture
- no claim that Claude Code Desktop is a shipping default
- no claim that the parked lifecycle-spine branch is ready to merge
