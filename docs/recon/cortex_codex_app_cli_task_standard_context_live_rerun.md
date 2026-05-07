# Cortex Codex App/CLI Task-Standard Context Live Rerun

Surface: product / live proof

Probe date: 2026-05-05

Verdict: partial_delivery_only. Codex-native `UserPromptSubmit`
`hookSpecificOutput.additionalContext` reached the live Codex CLI model turn,
and the model emitted the signed-off three-line task standard before its first
tool call. Cortex did not capture that standard into `TaskStandardSpine` before
tool use because the product hook rows did not expose the assistant preamble as
`last_assistant_message`; it appeared in the Codex JSON event stream and the
session transcript.

## What Ran

The approved live command was:

```bash
CORTEX_CODEX_APP_CLI_TASK_STANDARD_LIVE_APPROVED=approved python3 lab/codex_app_cli_stop_activation_probe.py --task-standard-live
```

The harness created an isolated subject workspace under
`.cortex/live_validation/openai/codex_app_cli_task_standard_live_probe/run_20260505T195300Z/`,
registered UserPromptSubmit, PreToolUse, PostToolUse, and Stop with the product
hook client, enabled `--enable-task-standard-text`, enabled
`--disable-stop-blocks`, and omitted `--runtime-snapshot`.

## Evidence

- `verdict`: `partial_delivery_only`.
- `hook_rows`: 4.
- `prompt_rows`: 1.
- `context_rows`: 1.
- `tool_rows`: 2.
- `stop_rows`: 1.
- `standard_capture_rows`: 0.
- `first_tool_index`: 2.
- `first_standard_capture_index`: null.
- `prework_standard_capture`: false.
- `runtime_snapshot_loaded`: false on every row.
- `root_config_hash_before` and `root_config_hash_after` matched.
- `context_hash`: `9021a0efef77eb6371eecf4996332d7fce31febae8462decf10b48056f6cf1a9`.

The Codex JSON output stream included this assistant message before the first
command execution:

```text
Work standard: Create `cortex_task_standard_live.txt` via shell with exactly one line `task standard live done`, then read it back with `cat` to verify content.
Likely misses: Wrong filename, extra/missing words, or skipping the read-back verification.
Closure evidence: Command output shows the exact line from the created file and I report completion.
```

The session transcript also recorded the signed task-standard text as a
developer message before the assistant preamble, then recorded the assistant
standard block before the function call. The PreToolUse hook payload did carry a
`transcript_path`, but the current product coordinator only parses assistant
standard blocks from `last_assistant_message`, which Codex supplies on Stop.

Stop-block suppression worked: the final Stop row selected existing
overdue-verification text privately and recorded suppressed rendered text hash
`a384c80463a98828df0de20d5aa2baafda8bb4fa023bd062c2a17e03e7fc04fc`, but emitted
no Stop stdout payload.

## Interpretation

This run proves the corrected context channel is no longer blind JSON emission:
Codex-native `additionalContext` reached the model strongly enough that the
model produced the requested task-standard block before tool use.

The remaining failure is capture boundary, not signed text, SRE law, or model
compliance. Cortex needs a product-visible way to ingest the pre-tool assistant
standard block before the first tool event. The observed lawful source is the
Codex session transcript referenced by `transcript_path` on PreToolUse and
PostToolUse hook rows.

## Not Earned

- No `TaskStandardSpine.standard_items` were captured in the live hook state.
- No downstream proof was earned that task-standard state shapes Stop or
  PreToolUse gating.
- No output-quality or behavior lift was earned.
- No Codex App parity, root-hook activation, hidden-verifier perception, SRE-law
  change, selector change, parser change, signed-text change, or Stop-text
  change was earned.

## Next Decision

Queue `codex-app-cli-task-standard-pretool-transcript-capture`. The next seam
should capture assistant standard blocks from product-visible Codex transcript
events during PreToolUse or PostToolUse before the first tool decision is
treated as standard-blind. If the transcript is not available early enough at
hook time, choose a Codex event-stream delivery/capture design rather than text
tuning.
