# Codex App/CLI PostToolUse Task-Standard Calibration Decision

Surface: product architecture + lab proof review

Verdict: `decision_queue_narrow_live_posttooluse_probe`.

## Summary

This no-spend decision seam reviewed the already-passed PostToolUse Gate 0 and
queues a narrow live PostToolUse actuator probe. It does not queue a three-arm
behavior comparison.

The decision is stacked on
`codex/20260506-015000-codex-app-cli-task-standard-offline-replay-readiness-gate`
because the offline-readiness, raw-vs-silent, lifecycle-map, and PostToolUse
Gate 0 work are still in the current dirty stack.

## Evidence Basis

- Gate 0 report:
  `.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/task_standard_posttooluse_gate0/gate0_report.json`.
- Gate 0 verdict: `pass_posttooluse_gate0`.
- The mismatch case emitted one Codex-native PostToolUse
  `hookSpecificOutput.additionalContext` naming a specific unresolved standard
  item and concrete next evidence move.
- Clean-evidenced, blocker, waiting-on-user, unrelated-tool, and flag-disabled
  controls stayed silent.
- Root config stayed unchanged, no runtime snapshot loaded, hidden scoring
  stayed scoring-only, and no Stop block, PreToolUse denial,
  PermissionRequest policy, or Sinkhorn/transport path was used.

## Decision

Queue `codex-app-cli-posttooluse-task-standard-narrow-live-probe`.

The probe should be narrow: one `task_standard_exactness` /
evidence-recovery mismatch family plus clean controls. It should test whether
PostToolUse additionalContext changes the next model step after tool evidence,
not whether Cortex earns broad behavior lift.

Live execution remains approval-gated in the implementation turn. The live
command must not use `--require-pass`; negative verdicts are valid evidence.
The probe is not approved until the stack is published or merged and cleanup
no longer reports dirty worktree state.

## Forbidden Claims

Not earned: live behavior lift, broad Cortex lift, output-quality lift,
truth-gap lift, Codex App parity, shipping promotion, Sinkhorn/transport,
PreToolUse motor inhibition, three-arm comparison approval, or any change to
signed UserPromptSubmit text, Stop text, SRE law, scored matcher, fixtures,
scoring, hooks, root config, or hidden-verifier boundaries.
