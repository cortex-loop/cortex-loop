# Cortex Retained Active-Policy Spine Live Gate 1

Surface: no-live retained-spine evaluator dry-run gate

## Summary

Verdict: `pass_cortex_retained_active_policy_spine_live_gate1`.

This no-live seam wires the retained active-policy spine
`userpromptsubmit_stop_taskstandard_spine` into the evaluator dry-run matrix
without running live Codex. The artifact set is written under
`.cortex/live_validation/cortex_retained_active_policy_spine_live_gate1/`:
`retained_spine_contract.json`, `evaluator_design.json`, `live_plan.json`,
`episode_table.jsonl`, `summary.json`, `leaderboard.json`, and
`failure_analysis.json`.

The dry-run plan schedules `60` rows: `4` arms x `5` v2 task families x `3`
repeats. The arms are `no_cortex_baseline`, `simple_hook_baseline`,
`cortex_silent_perception`, and `cortex_active_policy`. The active arm is only
`userpromptsubmit_stop_taskstandard_spine`; no active row uses a PostToolUse
task-standard policy.

## Registered Future Live Interface

Future command:

```bash
CORTEX_CODEX_APP_CLI_RETAINED_SPINE_LIVE_APPROVED=approved python3 lab/cortex_effectiveness_evaluator.py --retained-spine-live-matrix
```

The command is registered but not implemented as a live runner in this seam.
Without approval it returns `not_run_approval_required`. With approval in this
seam it remains no-live / not-implemented and must not execute live trials.
The registered CLI flag is `--retained-spine-live-matrix`.

## Evidence Boundaries

- `live_trials_ran=false`.
- Seam model-I/O path: `none_lab_proof_only`.
- The future product model-I/O paths remain the retained Gate 0 paths: Codex
  `UserPromptSubmit` `hookSpecificOutput.additionalContext` and Codex `Stop`
  `hookSpecificOutput` or block stdout continuation.
- The v2 registry is consumed; v1/v2 prior live artifacts are not rescored.
- `run_20260508T221352Z` remains preserved as
  `failure_silent_perception_contamination`.
- `run_20260509T112542Z` remains preserved as `failure_no_value`.
- Simple-hook parity blocks Cortex value.
- Silent-perception success blocks Cortex value as contamination or no-value.
- Positive retained-spine value would require a later approved live run and user
  review.

## PostToolUse Role

PostToolUse task-standard context remains
`role_demoted_non_current_support_history`. This seam does not reactivate it as
current strategy, product progress, earned active policy, or a retained-spine
component.

## Decision

The retained spine is ready for one approval-gated live matrix attempt, but no
value has been earned. The next train is
`cortex-retained-active-policy-spine-live-run`.

If that live run ties or loses to the simple hook, active-policy growth remains
blocked and Cortex should contract or redesign before candidate evolution.

## Forbidden Moves

- No live Codex run.
- No product code deletion.
- No product host behavior change.
- No model-visible Cortex text change.
- No evaluator scoring or fixture change.
- No hidden-verifier boundary change.
- No root hook change.
- No SRE law change.
- No active policy or candidate-policy mutation.
- No PostToolUse task-standard context reactivation as earned active policy.
- No Cortex value, behavior lift, exactness value lift, broad Cortex lift,
  Codex App parity, shipping promotion, product progress, or AlphaEvolve
  candidate-evolution permission.
