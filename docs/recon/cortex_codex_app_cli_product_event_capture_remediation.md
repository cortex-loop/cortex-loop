# Cortex Codex App/CLI Product Event-Capture Remediation

Surface: product / live hook perception proof

Probe date: 2026-05-04

Verdict: pass on live Codex CLI product event capture through project hooks.

## Summary

The previous no-snapshot probe installed only a `Stop` hook in the isolated
subject workspace, so its Stop-only result did not prove Codex lacked
non-Stop lifecycle payloads. This remediation registered the official
turn-scoped Codex lifecycle hooks used by the product loop:
`UserPromptSubmit`, `PreToolUse`, `PostToolUse`, and `Stop`.

The passing live run used a disposable subject workspace with its own git root,
product hook config only, no `--runtime-snapshot`, and unchanged root repo
guardrails. Real hook diagnostics recorded the full lifecycle:

```text
hook_event_counts: {"PostToolUse": 2, "PreToolUse": 2, "Stop": 2, "UserPromptSubmit": 1}
verdict: pass_full_lifecycle
runtime_snapshot_loaded: false on every row
```

The first Stop opened an overdue verification expectation from product-visible
state and emitted the locked identity-continuous block text. The continuation
then ran a file/content check. This earns live product event-capture and
Stop-actuator evidence only; it does not earn model-output lift.

## Run

Command:

```bash
CORTEX_CODEX_APP_CLI_PRODUCT_EVENT_CAPTURE_APPROVED=approved \
python3 lab/codex_app_cli_stop_activation_probe.py \
  --product-event-capture-live --require-pass
```

Subject command:

```bash
codex exec --json --full-auto --skip-git-repo-check -m gpt-5.3-codex \
  "Use shell commands to create a one-line file named cortex_product_event_capture_live.txt containing product event capture live done, read the file back, and then report done."
```

Artifact root:

```text
.cortex/live_validation/openai/codex_app_cli_product_event_capture_remediation/run_20260504T180756Z/
```

Key report fields:

```text
passed: true
verdict: pass_full_lifecycle
hook_rows: 7
prompt_rows: 1
tool_rows: 4
stop_rows: 2
block_rows: 1
exact_block_rows: 1
non_stop_stdout_rows: 0
subject_isolated_git_root: true
subject_config_product_event_capture_only: true
hook_rows_do_not_load_runtime_snapshot: true
actual_rendered_text_hashes: ["a384c80463a98828df0de20d5aa2baafda8bb4fa023bd062c2a17e03e7fc04fc"]
```

## What The Probe Proved

- A real isolated Codex CLI project run can deliver `UserPromptSubmit`,
  `PreToolUse`, `PostToolUse`, and `Stop` payloads to the product hook client
  when those hooks are configured.
- The product hook client can persist prompt/tool/Stop state before Stop
  without a prewritten runtime snapshot.
- Non-Stop hooks stayed silent and emitted no model-visible stdout.
- Stop can derive a product-runtime verification expectation from the stored
  task-set and assistant closure claim.
- The model-visible block text came from the product renderer, with rendered
  hash `a384c80463a98828df0de20d5aa2baafda8bb4fa023bd062c2a17e03e7fc04fc`.
- The root repo `.codex/config.toml` was unchanged, and the subject workspace
  was initialized as its own git root so parent repo workflow guardrails were
  not part of the evidence path.

## What The Probe Did Not Prove

- No behavior lift is claimed. The run was a live actuator/perception probe,
  not a paired comparison against silent-only control.
- No Codex App proof is claimed. This was a Codex CLI subject run; App and CLI
  actuator evidence remain partitioned.
- No root product hook activation is claimed. The hook config lived only in the
  disposable subject workspace.
- No hidden-verifier, fixture-prompt, task-identity, or lab-oracle perception
  was used.
- The continuation repair loop is not fully closed: after the block, Codex ran
  a visible file/content check, but the current continuation policy suppresses
  `stop_hook_active` Stop rows and did not resolve the open expectation in this
  report.

## Important Observation

The first remediation live run was intentionally discarded as the primary
verdict source because the subject workspace was still under the parent git
root. That shape risked parent repo Mission Reflection hooks influencing Stop
continuations. The harness now initializes live subject workspaces with their
own `.git` directory and records `subject_isolated_git_root: true` in boundary
checks before treating a run as product event-capture evidence.

The passing isolated run shows the earlier Stop-only finding was a harness
configuration gap, not a proven Codex host limitation. When configured with the
full lifecycle hooks documented by OpenAI, the Codex CLI lane supplies enough
product-visible event payloads to feed Cortex state before Stop.

## Next Move

Open a continuation-resolution seam before broad behavior trials. The next seam
should keep the same hook-native product path and make the post-block repair
loop accountable: a first Stop may block from product-visible overdue
verification, the continuation may run checks, and the final Stop should resolve
or stay open based on product-observable evidence rather than relying only on
`stop_hook_active` suppression. It must not use hidden verifiers, task identity,
runtime snapshots, fixture prompts, or new model-visible speech.
