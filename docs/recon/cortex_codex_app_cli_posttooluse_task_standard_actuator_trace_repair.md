# Cortex Codex App/CLI PostToolUse Actuator Boundary and Trace Repair

Surface: product host actuator + lab trace proof

Verdict: `pass_posttooluse_actuator_trace_gate0`.

Evidence basis:

- Product owner: `cortex/hosts/openai/posttooluse_task_standard_actuator.py`.
- Wiring owner: `cortex/hosts/openai/codex_app_cli_hook_coordinator.py`.
- Proof owner: `lab/codex_app_cli_hook_native_behavior_comparison.py`.
- Gate 0 report: `.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/task_standard_posttooluse_actuator_trace_gate0/gate0_report.json`.
- Replay artifact: `task_standard_posttooluse_live_20260507T153242Z`.

## Decision

The PostToolUse task-standard actuator decision is now owned by a small Codex
host module instead of the coordinator. The coordinator still owns lifecycle
state update and Codex-native response wiring, but the PostToolUse task-standard
phase classification, item selection, context rendering, session cap, and
private silence reasons now live behind `posttooluse_task_standard_context_decision(...)`.

The model-visible PostToolUse text did not change. The signed UserPromptSubmit
text, Stop text, SRE law, scored matcher, thresholds, fixtures, scoring, root
hooks, hidden-verifier boundary, Sinkhorn/transport, PreToolUse denial, and
PermissionRequest policy did not change.

## Trace Repair

The live harness now evaluates `next_tool_after_context` from hook chronology:
the context-emitting PostToolUse hook row is paired to the terminal command that
preceded it, and the next terminal command after that hook is treated as the
model action after context.

Replay of `task_standard_posttooluse_live_20260507T153242Z` proves the repaired
trace does not count the artifact-creation command as the next action after the
context that followed it:

- context row: PostToolUse row index `5`;
- preceding tool: `printf 'alpha beta omega' > exact_result.txt`;
- next tool after context: `od -An -t x1 -v exact_result.txt`.

This removes the overgenerous readout risk from the prior live rerun while
preserving the actual product actuator behavior.

## Gate 0 Result

`--task-standard-posttooluse-actuator-trace-gate0 --require-pass` passed.

Pinned outcomes:

- live-equivalent failed checks stay silent with private `phase_check_failed`;
- mismatch candidate artifact and readback rows still emit one existing
  Codex-native PostToolUse `additionalContext`;
- clean evidenced, blocker, waiting-on-user, unrelated, markerless, failed,
  and missing-artifact controls stay silent;
- the trace model identifies the next action strictly after the context row;
- root config was unchanged;
- no runtime snapshot, Stop block, PreToolUse denial, PermissionRequest policy,
  hidden scoring perception, or transport path appeared.

## Earned

This seam earns structural remediation only: one host-owned PostToolUse
task-standard actuator boundary and hook-chronological live readout causality.

## Not Earned

No live Codex run occurred in this seam. It earns no behavior lift, broad Cortex
lift, exactness value lift, clean-control safety claim in live use, Codex App
parity, shipping promotion, PreToolUse proof, or Sinkhorn/transport proof.

## Next Train

Keep the queued next train as
`codex-app-cli-posttooluse-task-standard-phase-aware-narrow-live-rerun`.

That future run still requires explicit current-turn live approval and must not
use `--require-pass`; negative verdicts remain valid evidence.
