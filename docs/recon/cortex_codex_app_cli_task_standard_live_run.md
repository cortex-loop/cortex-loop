# Cortex Codex App/CLI Task-Standard Live Run

Surface: product / live proof

Probe date: 2026-05-05

Verdict: fail; the signed UserPromptSubmit text was emitted by the product hook
client as a flat Cortex-internal `{"context": ...}` payload, not as Codex's
native `hookSpecificOutput.additionalContext` shape. The live model did not
produce a prework task-standard block, and existing Stop verification law
emitted model-visible overdue-verification text during the same run.

## What Ran

The approved live command was:

```bash
CORTEX_CODEX_APP_CLI_TASK_STANDARD_LIVE_APPROVED=approved python3 lab/codex_app_cli_stop_activation_probe.py --task-standard-live
```

The harness created an isolated subject workspace under
`.cortex/live_validation/openai/codex_app_cli_task_standard_live_probe/run_20260505T180138Z/`,
registered UserPromptSubmit, PreToolUse, PostToolUse, and Stop with the product
hook client, enabled `--enable-task-standard-text`, and omitted
`--runtime-snapshot`.

## Evidence

- `hook_rows`: 7.
- `prompt_rows`: 1.
- `context_rows`: 1.
- `tool_rows`: 4.
- `stop_rows`: 2.
- `standard_capture_rows`: 0.
- `first_tool_index`: 2.
- `first_standard_capture_index`: null.
- `prework_standard_capture`: false.
- `runtime_snapshot_loaded`: false on every row.
- `root_config_hash_before` and `root_config_hash_after` matched.
- `context_hash`: `9021a0efef77eb6371eecf4996332d7fce31febae8462decf10b48056f6cf1a9`.

The first hook row emitted the exact signed text, but the stdout contract was
the non-native flat `{"context": ...}` shape. That means this run did not prove
Codex CLI model-visible context assimilation. The first model message skipped
the requested `Work standard`, `Likely misses`, and `Closure evidence` block
and moved directly to creating and reading the file. No task-standard items
were captured before the first tool event or later in the turn.

At the first Stop row, the existing overdue-verification path emitted the
locked identity-continuous Stop text with rendered text hash
`a384c80463a98828df0de20d5aa2baafda8bb4fa023bd062c2a17e03e7fc04fc`. The
second Stop row had `stop_hook_active=true` and stayed silent with
`stop_hook_active_unresolved_verification_expectation`.

## Interpretation

This is not a task-standard behavior-lift result. It is a host-contract finding:
Codex CLI accepted and ran the project hooks, but the product hook client used a
Cortex-internal context shorthand instead of Codex's native
`hookSpecificOutput.additionalContext`. The existing Stop actuator also
confounded the task-standard-only measurement by firing overdue-verification
text after the model declared completion.

## Not Earned

- No prework task-standard capture was earned.
- No output-quality or behavior lift was earned.
- No downstream proof was earned that task-standard state shapes Stop or
  PreToolUse gating.
- No SRE law, Cortex speech, selector threshold, task-standard parser,
  runtime snapshot path, root hook config, or hidden-verifier perception
  changed.

## Next Decision

Queue `codex-app-cli-task-standard-capture-boundary-remediation`. The next seam
should isolate task-standard context assimilation and capture from existing Stop
blocking, serialize `UserPromptSubmit` through Codex-native
`hookSpecificOutput.additionalContext`, and record the result without changing
the signed text or weakening task-standard law.
