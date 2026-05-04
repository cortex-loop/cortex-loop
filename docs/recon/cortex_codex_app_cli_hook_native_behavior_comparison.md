# Cortex Codex App/CLI Hook-Native Behavior Comparison

Surface: product / structural behavior-comparison readiness

Probe date: 2026-05-04

Verdict: gate0_ready; live behavior comparison not run.

## Summary

This seam adds the paired Codex CLI hook-native behavior comparison harness
without changing Cortex speech, selector law, or root repo hooks. The harness
compares two arms:

- `silent_only`: product lifecycle perception remains active, but the hook
  client suppresses model-visible Stop block JSON.
- `hook_native_cortex`: the same lifecycle perception and state path remains
  active, and selected Stop blocks reach the model with the locked
  identity-continuous renderer text.

Gate 0 passed. It proved the two comparison arms share the same prompt hash,
workspace seed hash, model, and task family while differing only in whether
the model-visible Stop block is emitted.

```text
probe: codex_app_cli_hook_native_behavior_comparison_gate0
passed: true
silent_only_stdout_payload: null
silent_only_suppressed_payload: exact overdue-verification block JSON
hook_native_stdout_payload: exact overdue-verification block JSON
runtime_snapshot_loaded: false
root_config_unchanged: true
```

No live behavior comparison was run in this seam because live Codex CLI trials
require explicit current-turn approval through
`CORTEX_CODEX_APP_CLI_BEHAVIOR_COMPARISON_APPROVED=approved`.

## Run

Gate 0 command:

```bash
python3 lab/codex_app_cli_hook_native_behavior_comparison.py --require-pass
```

Gate 0 artifacts:

```text
.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/gate0_report.json
.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/gate0_trajectory.jsonl
```

Live comparison command, not run in this seam:

```bash
CORTEX_CODEX_APP_CLI_BEHAVIOR_COMPARISON_APPROVED=approved \
python3 lab/codex_app_cli_hook_native_behavior_comparison.py \
  --live-trials --require-pass
```

## What This Proved

- The silent comparator can keep product perception active while suppressing
  model-visible Stop blocks.
- The hook-native arm emits the exact locked product-rendered Stop block.
- The two arms are structurally comparable before live trials: prompt hash,
  workspace seed hash, model, and task family match.
- No runtime snapshot, hidden verifier answer, task-identity trigger, fixture
  continuation prompt, or repo Mission Reflection hook supplies product
  perception.

## What This Did Not Prove

- No behavior lift is claimed. No paired live Codex CLI trials ran.
- No output-quality lift is claimed. `astro_docs_site_v1` remains a future
  live scoring family, not a product trigger.
- No root product hook activation is claimed. The comparison harness uses
  isolated subject configs only.
- No Codex App parity is claimed. The planned live comparison remains scoped to
  Codex CLI unless a separate Codex App run earns its own evidence.

## Precommitted Live Verdicts

The live comparison must use paired trial thresholds, not aggregate-only
movement:

- `success_truth_gap_only`: hook-native wins at least 4 of 5 paired trials on
  at least two primary axes for truth-gap, with no material regression and no
  clean-control overblock.
- `success_broad`: the same threshold passes for truth-gap and output-quality.
- `failure_no_lift`: baseline reproduces but hook-native misses the threshold.
  This requires an architecture decision pause before any implementation seam.
- `failure_overblock`: any material clean-control overblock or slowdown. This
  queues selector/gating remediation, not text tuning.
- `scoped_negative`: hooks or payloads fail to produce comparable live evidence.

## Next Move

Run the approved live behavior comparison as the next product train. If the
verdict is `failure_no_lift`, pause implementation and decide whether
Stop-only closure inhibition, perception depth, PreToolUse motor inhibition, or
Cortex scope needs revision.
