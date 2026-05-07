# Codex App/CLI Task-Standard Behavior Comparison Harness

Surface: product + lab proof

Verdict: structural Gate 0 passed; live behavior lift remains unearned.

## Summary

This seam added the task-standard three-arm comparison surface for the next
Codex CLI product-value test. It compares:

- `raw_codex`: no subject `.codex/config.toml`, no Cortex hooks, no Cortex state
- `silent_task_standard`: signed task-standard context, lifecycle perception,
  transcript capture, and Stop blocks suppressed with `--disable-stop-blocks`
- `active_task_standard`: the same product hooks and signed context, with Stop
  blocks enabled

The seam did not run live paid trials, tune signed task-standard text, tune Stop
text, change SRE law, alter selector thresholds, repair fixtures after seeing
results, or change hidden-verifier boundaries.

## Evidence

Structural command:

```bash
python3 lab/codex_app_cli_hook_native_behavior_comparison.py --task-standard-three-arm-gate0 --require-pass
```

Targeted lab proof:

```bash
python3 -m pytest tests/lab/test_codex_app_cli_hook_native_behavior_comparison.py -q
```

Gate 0 result:

- raw arm recorded no hook rows and no subject hook config
- silent and active arms shared prompt hash, workspace seed hash, model, hook
  registration, signed task-standard context, and scoring surface
- silent arm used `--disable-stop-blocks` and did not use
  `--disable-model-visible-blocks`
- active arm captured three task-standard items and emitted an existing Stop
  block from captured standard state
- continuation rows were recorded after the first active/suppressed block
- no generated command contained a runtime snapshot flag
- root `.codex/config.toml` hash stayed unchanged
- hidden scoring remained marked scoring-only

## What This Earns

- Harness readiness for a pinned three-arm task-standard behavior comparison.
- Structural proof that the raw, silent, and active arms are isolated in the way
  the product question requires.
- Structural proof that active-arm success is tied to captured
  `TaskStandardSpine` state plus Stop block/continuation rows, not aggregate
  score drift.

## What This Does Not Earn

- No live behavior lift.
- No output-quality lift.
- No claim that Cortex beats raw Codex or silent task-standard perception.
- No permission to edit signed task-standard text, Stop text, SRE law, selector
  thresholds, hidden-verifier boundaries, fixtures, root hook config, or scoring
  after seeing live results.
- No shipping promotion or Codex App parity claim.

## Next Move

Queue `codex-app-cli-task-standard-behavior-comparison-live-run`. The live run
requires explicit current-turn approval and must use the pinned harness without
tuning. If active task-standard Cortex does not beat both controls, overblocks
clean controls, or baseline failures do not reproduce, the next turn is an
architecture decision pause rather than an implementation seam.
