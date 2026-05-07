# Codex App/CLI Task-Standard Raw-vs-Silent Artifact Readout

Surface: lab proof + product architecture

Verdict: `signal_present_narrow`; broad behavior lift remains unearned.

## Summary

This no-spend seam mined the existing three-arm task-standard artifacts at:

`.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/task_standard_three_arm_live_20260506T001502Z/`

It compared `raw_codex` against `silent_task_standard` before any new
PostToolUse, PreToolUse, Sinkhorn, transport, or live behavior work.

Implementation note: this seam was recorded as an explicit stacked follow-on
on `codex/20260506-015000-codex-app-cli-task-standard-offline-replay-readiness-gate`
because the offline-readiness branch was not yet committed/published at the
time of implementation.

The readout found one narrow signal: on `task_standard_exactness`,
`silent_task_standard` beat `raw_codex` on `evidence_recovery` in 5/5 paired
trials, with no material regression in that family. The signal is not broad:
`output_quality_visible_success` was mixed and `truth_gap_false_completion`
showed a material `goal_continuity` regression.

## Evidence

Command:

```bash
python3 lab/codex_app_cli_hook_native_behavior_comparison.py --task-standard-raw-vs-silent-artifact-readout --require-pass
```

Report:

- `.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/task_standard_raw_vs_silent_artifact_readout/readout_report.json`

Boundary checks:

- existing `summary.json`, `trajectory.jsonl`, per-trial `codex_stdout.jsonl`,
  hook diagnostics, and hook trajectories were present where required;
- `raw_codex` had no hooks, context, standard state, evidence refs, or blocks;
- `silent_task_standard` delivered signed context and kept Stop blocks
  suppressed-only;
- clean controls had no silent overblock;
- hidden scoring stayed scoring-only;
- no live Codex run was executed.

Family readout:

- `task_standard_exactness`: `evidence_recovery` wins 5/5 for silent over raw;
  `premature_closure` and `goal_continuity` had smaller mixed/tied gains.
- `output_quality_visible_success`: silent beat raw on some rows but did not
  clear the narrow signal bar.
- `truth_gap_false_completion`: silent did not beat raw and had material
  `goal_continuity` regressions.

## Decision

Queue `codex-app-cli-lifecycle-actuator-map` next. The next seam should map
Codex App/CLI lifecycle events by actual product control and constrain
PostToolUse planning to the narrow exactness / evidence-recovery signal.

Do not run another live three-arm comparison yet. Do not implement Sinkhorn
next. Do not generalize this artifact readout into broad Cortex behavior lift.

## Forbidden Claims

This seam earns no runtime behavior change, no new live evidence, no active
Stop-gating lift, no output-quality lift, no truth-gap lift, no PostToolUse
actuator, no PreToolUse motor inhibition, no Sinkhorn implementation, no Codex
App parity, and no shipping promotion.
