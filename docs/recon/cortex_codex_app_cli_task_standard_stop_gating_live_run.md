# Codex App/CLI Task-Standard Stop-Gating Live Run

Surface: product + lab proof

Verdict: `pass_gating_observed`; behavior lift remains unearned.

## Summary

This seam ran the live Codex CLI Stop-gating probe after structural
calibration. It proved the signed task-standard context, product-visible
standard capture, Stop gate, continuation check, and final silent resolution
can all occur in one real Codex CLI turn.

The run did not change signed task-standard text, Stop text, SRE law, selector
thresholds, root hook configuration, hidden-verifier boundaries, or behavior
comparison criteria.

## Evidence

Command:

```bash
CORTEX_CODEX_APP_CLI_TASK_STANDARD_STOP_GATING_APPROVED=approved python3 lab/codex_app_cli_stop_activation_probe.py --task-standard-stop-gating-live
```

Result artifact:

`.cortex/live_validation/openai/codex_app_cli_task_standard_stop_gating_probe/run_20260505T222615Z/report.json`

Observed sequence:

- `UserPromptSubmit` emitted the signed Codex-native
  `hookSpecificOutput.additionalContext` payload.
- The model wrote a pre-tool `Work standard` / `Likely misses` /
  `Closure evidence` block.
- `PreToolUse` captured three assistant-authored standard items into
  `TaskStandardSpine` before tool evidence scoring.
- The initial tool command created the file and read it back, satisfying the
  closure-evidence item but leaving the model's own `Work standard` item
  unmatched because the standard named an exact one-line file.
- The first Stop emitted the existing locked overdue-verification block text
  with rendered hash
  `a384c80463a98828df0de20d5aa2baafda8bb4fa023bd062c2a17e03e7fc04fc`.
- The continuation ran stronger product-visible checks (`ls`, `wc -l`,
  `cat -A`, and `cmp`/content-match output).
- The final `stop_hook_active=true` Stop stayed silent with
  `pressure_below_visible_threshold` and no unmatched standard items.

Boundary checks:

- root `.codex/config.toml` hash unchanged:
  `a1c3291ce7aa69297d74654f3fed724f1e5d63fa038ae188371d4b899e1f5147`
- no runtime snapshot loaded
- subject config registered only the product hook client for
  `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, and `Stop`
- Stop blocks were not suppressed
- one real block row and two Stop rows were recorded

## What This Earns

- Live Codex CLI evidence that captured task standards can drive an existing
  Stop verification block.
- Live continuation evidence that the model can respond to the block by running
  stronger aligned checks, after which Cortex resolves the expectation and stays
  silent.
- Product-path evidence that the task-standard spine is no longer only a
  structural or replay object.

## What This Does Not Earn

- No paired behavior lift.
- No output-quality lift.
- No claim that Cortex beats raw Codex or silent Cortex.
- No Codex App parity claim beyond the Codex CLI host surface used here.
- No permission to tune signed task-standard text, Stop text, SRE law, selector
  thresholds, hidden-verifier boundaries, or task-identity triggers.

## Next Move

Queue `codex-app-cli-task-standard-behavior-comparison`. The next seam should
compare raw Codex, silent task-standard perception, and active task-standard
Stop gating on standard-sensitive tasks and clean controls. A product-value
claim requires active Cortex to beat raw and silent arms with actual captured
standard and block/continuation rows, without clean-control overblock.
