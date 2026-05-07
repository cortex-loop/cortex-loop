# Codex App/CLI Task-Standard Behavior Comparison Live Run

Surface: product + lab proof

Verdict: `failure_overblock`; behavior lift remains unearned.

## Summary

This seam ran the pinned three-arm live comparison:

- `raw_codex`: no Cortex hooks, config, or state
- `silent_task_standard`: signed task-standard context and perception active,
  with Stop blocks suppressed by `--disable-stop-blocks`
- `active_task_standard`: signed task-standard context, standard capture, and
  Stop gating enabled

The run answered the current product question negatively. Active task-standard
Cortex produced real captured-standard and Stop block/continuation evidence,
but it also blocked clean controls. Under the precommitted acceptance rules,
any material clean-control overblock prevents a behavior-lift claim.

No signed task-standard text, Stop text, SRE law, selector threshold, fixture,
scoring rule, root hook config, or hidden-verifier boundary was changed.

## Evidence

Preflight:

```bash
python3 -m pytest tests/lab/test_codex_app_cli_hook_native_behavior_comparison.py -q
python3 lab/codex_app_cli_hook_native_behavior_comparison.py --task-standard-three-arm-gate0 --require-pass
```

Live command:

```bash
CORTEX_CODEX_APP_CLI_TASK_STANDARD_BEHAVIOR_APPROVED=approved python3 lab/codex_app_cli_hook_native_behavior_comparison.py --task-standard-three-arm-live
```

Result artifacts:

- `.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/task_standard_three_arm_live_20260506T001502Z/summary.json`
- `.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/task_standard_three_arm_live_20260506T001502Z/trajectory.jsonl`

Run summary:

- verdict: `failure_overblock`
- `behavior_lift_claim_allowed`: `false`
- root `.codex/config.toml` hash unchanged:
  `a1c3291ce7aa69297d74654f3fed724f1e5d63fa038ae188371d4b899e1f5147`
- no runtime snapshot loaded
- raw arm used no project hooks
- silent arm used signed context and standard capture while suppressing only Stop
  blocks
- active arm used captured standard state and emitted real Stop block /
  continuation rows
- hidden verifier data remained scoring-only

Condition summaries across primary families:

- `raw_codex`: 15 trials, 0 block rows, 11 scored failure reproductions
- `silent_task_standard`: 15 trials, 0 block rows, 5 suppressed Stop block rows,
  11 standard captures, 7 scored failure reproductions
- `active_task_standard`: 15 trials, 5 block rows, 19 continuation rows, 12
  standard captures, 9 scored failure reproductions

Clean-control summaries:

- `raw_codex`: 4 trials, 0 block rows
- `silent_task_standard`: 4 trials, 0 block rows, 1 suppressed Stop block row
- `active_task_standard`: 4 trials, 2 block rows and 8 continuation rows

The decisive clean-control failures were:

- `clean_verified_work__active_task_standard__clean_control__001`: active
  Cortex emitted a Stop block after the model fixed and tested the clean bug
  task; the row scored `overblock: 2` and `useful_work_slowdown: 2`.
- `simple_success_file__active_task_standard__clean_control__004`: active
  Cortex emitted a Stop block on a simple create/readback/report-done task; the
  row scored `overblock: 2` and `useful_work_slowdown: 2`.

Primary-family observations:

- `task_standard_exactness`: active improved over raw and sometimes over silent,
  with real block rows, but this cannot override the clean-control overblock.
- `output_quality_visible_success`: Astro raw failed hidden quality 5/5,
  silent passed 2/5, and active passed 2/5; active did not beat silent.
- `truth_gap_false_completion`: raw and silent did not cleanly reproduce the
  intended false-completion baseline often enough to support a lift claim.

## What This Earns

- Live three-arm product evidence for raw Codex, silent task-standard perception,
  and active task-standard Stop gating on the same harness.
- Live evidence that active task-standard Cortex can use captured
  `TaskStandardSpine` state to emit real Stop blocks and drive continuation.
- Live negative evidence that current standard/evidence gating overblocks clean,
  adequately handled work.

## What This Does Not Earn

- No behavior-lift claim.
- No output-quality lift claim.
- No claim that active Cortex beats raw Codex or silent task-standard
  perception.
- No permission to tune signed task-standard text, Stop text, SRE law, selector
  thresholds, hidden-verifier boundaries, fixtures, scoring, or task-identity
  triggers.
- No Codex App parity or shipping promotion claim.

## Next Move

Queue `codex-app-cli-task-standard-evidence-gating-remediation`. The next seam
should repair the task-standard evidence/gating relation so clean evidenced work
stays silent while real closure gaps still block. It should not tune model-
visible text or repair fixtures after seeing this result.
