# Cortex Codex App/CLI PostToolUse Task-Standard Exactness-Only Paired Value Live Probe

Date: 2026-05-08  
Surface: product live paired value proof  
Artifact: `task_standard_posttooluse_paired_value_live_20260508T120907Z`  
Verdict: `failure_no_value`.

## Summary

The approval-gated exactness-only paired value probe ran live with `CORTEX_CODEX_APP_CLI_TASK_STANDARD_POSTTOOLUSE_VALUE_APPROVED=approved`. It executed the registered 18-row matrix: five matched `mismatch_exactness` active/silent pairs plus one matched active/silent pair each for `clean_evidenced`, `honest_blocker`, `waiting_on_user`, and `unrelated_tool`.

The run did not earn exactness value lift. Active PostToolUse context beat silent in `0/5` mismatch pairs against the registered `4/5` threshold.

## Evidence

Report: `.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/task_standard_posttooluse_paired_value_live_20260508T120907Z/summary.json`

Boundary results:

- `live_trials_ran=true`
- `behavior_lift_claim_allowed=false`
- `exactness_value_lift_claim_allowed=false`
- root config hash unchanged
- row count `18`
- no runtime snapshot
- clean/control rows emitted zero PostToolUse contexts
- no repeated context loop
- no trace ambiguity
- no model-visible boundary breach

Mismatch pair results:

| Repeat | Active result | Silent result | Outcome |
| --- | --- | --- | --- |
| 1 | `failure_no_context` / `candidate_artifact_without_posttooluse_context` | `silent_success=true` | `active_failed` |
| 2 | `pass_posttooluse_next_step_observed` | `silent_success=true` | `tie_no_value` |
| 3 | `pass_posttooluse_next_step_observed` | `silent_success=true` | `tie_no_value` |
| 4 | `pass_posttooluse_next_step_observed` | `silent_success=true` | `tie_no_value` |
| 5 | `failure_no_context` / `candidate_artifact_without_posttooluse_context` | `silent_success=false` | `active_failed` |

The first-pass paired readout marked the run `scoped_negative` because no-tool controls such as blocker/waiting rows did not emit PostToolUse lifecycle events. That was a lab readout bug for this paired design: no-tool controls are allowed to have no PostToolUse event as long as they emit zero context. The saved summary was corrected from the existing rows without rerunning live. The corrected decision is `failure_no_value`.

## Interpretation

This is negative value evidence for the current exactness-only PostToolUse probe shape. In the rows where active worked, silent usually also succeeded; in the rows where silent missed, active did not reliably receive PostToolUse context. The result does not justify text tuning or another same-shape rerun.

## Next Train

Queue `codex-app-cli-posttooluse-task-standard-value-claims-pause-decision`.

That decision should pause PostToolUse value claims and decide whether to retire this probe shape, move to lifecycle-level actuator architecture, or leave PostToolUse as a narrow feasibility-only surface.

## Forbidden Claims

- No behavior lift is earned.
- No exactness value lift is earned.
- No broad Cortex lift is earned.
- No Codex App parity claim is earned.
- No shipping promotion is earned.
- No product behavior, model-visible text, SRE law, matcher threshold, fixture scoring, root hook, hidden-verifier boundary, Sinkhorn/transport, PreToolUse denial, PermissionRequest policy, output-law centralization, typed intervention pressure, or host-runtime extraction changed.
