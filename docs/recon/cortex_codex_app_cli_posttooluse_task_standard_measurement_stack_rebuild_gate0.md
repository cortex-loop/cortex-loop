# Codex App/CLI PostToolUse Task-Standard Measurement-Stack Rebuild Gate 0

Surface: lab proof architecture remediation

Date: 2026-05-08

## Verdict

Verdict: `pass_posttooluse_measurement_stack_gate0`.

The measurement stack now has one lab-owned evidence-recovery episode table for
the PostToolUse task-standard live line. The Gate 0 replayed all five historical
live artifacts and preserved their registered negative evidence while isolating
the latest run as final-closure metric underfit.

This is no-live proof only. It does not change product host behavior, signed
UserPromptSubmit text, PostToolUse text, Stop text, SRE law, matcher thresholds,
fixtures, scoring semantics, root hooks, hidden-verifier boundaries,
Sinkhorn/transport, PreToolUse denial, PermissionRequest policy, output-law
centralization, typed intervention pressure, or host-runtime extraction.

No behavior lift, exactness value lift, broad Cortex lift, Codex App parity, or
shipping promotion is earned.

## Evidence Table

| Artifact | Registered verdict | Episode classification | Preserved meaning |
| --- | --- | --- | --- |
| `task_standard_posttooluse_live_20260507T100836Z` | `failure_context_ignored` | `true_next_action_ignore` | Context emitted, but the next model tool did not run the named direct check. |
| `task_standard_posttooluse_live_20260507T142129Z` | `failure_no_context` | `failure_no_context` | Candidate/readback-shaped prerequisite work occurred without PostToolUse context. |
| `task_standard_posttooluse_live_20260507T153242Z` | `failure_overcontrol` | `failure_overcontrol` | The clean evidenced control received PostToolUse context. |
| `task_standard_posttooluse_live_20260507T213732Z` | `fail` | `repeated_context_trace_not_interpretable` | Repeated contexts and ambiguous trace block causal interpretation. |
| `task_standard_posttooluse_live_20260507T225019Z` | `failure_context_ignored` | `final_closure_metric_underfit` | Context emitted once, trace joined by `tool_event_fingerprint`, next action matched, and final output carried semantic closure evidence, but the old registered final-closure predicate returned false. |

Gate 0 report path:

`.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/task_standard_posttooluse_measurement_stack_gate0/gate0_report.json`

The report has `live_trials_ran=false`, `behavior_lift_claim_allowed=false`,
`passed=true`, and `verdict=pass_posttooluse_measurement_stack_gate0`.

## Semantic Final Closure

The table-scoped semantic closure helper recognizes the latest run's final
output evidence:

- `PASS`
- `bytes=16`
- expected hex `616c7068612062657461206f6d656761`
- exact content `alpha beta omega`

This recognition is deliberately table-scoped in this seam. It does not retroactively promote `task_standard_posttooluse_live_20260507T225019Z` to a
pass, and it does not change the registered live decision function. The old
verdict remains `failure_context_ignored` until a later no-live readout
remediation updates the final-closure predicate and replays the same historical
failure table.

## Boundary Dominance

Semantic final-output evidence cannot mask earlier blockers. The episode table
keeps these precedence rules:

- repeated context and ambiguous trace remain uninterpretable before any
  final-output readout;
- clean/control context remains `failure_overcontrol`;
- zero context after prerequisite work remains `failure_no_context`;
- a context that does not change the next model tool remains
  `true_next_action_ignore`;
- final-closure metric underfit is recognized only after context delivery,
  control silence, non-ambiguous trace, and next-action match have already
  passed.

## Next Train

Queue:

`codex-app-cli-posttooluse-task-standard-final-closure-readout-remediation-gate0`

That later seam may update the lab final-closure readout predicate, but it must
replay this same measurement table and preserve all earlier historical failure
classes. No live rerun or exactness value probe is authorized by this Gate 0.
