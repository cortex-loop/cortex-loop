# Cortex Codex App/CLI PostToolUse Task-Standard Exactness-Only Paired Value Probe Gate 0

Date: 2026-05-08  
Surface: lab proof paired-value design gate  
Verdict: `pass_posttooluse_exactness_only_paired_value_gate0`.

## Summary

This no-live Gate 0 pre-registers the exactness-only paired value probe for Codex-native PostToolUse task-standard `hookSpecificOutput.additionalContext`. It does not run live Codex, does not change product behavior, and does not claim behavior lift or exactness value lift.

The future paired probe has two conditions:

- `active_posttooluse_context`
- `silent_posttooluse_control`

The registered cases are:

- `mismatch_exactness`
- `clean_evidenced`
- `honest_blocker`
- `waiting_on_user`
- `unrelated_tool`

The only intended arm delta is `enable_posttooluse_task_standard_context=true` for active and `false` for silent. Pairing requires same model, same prompt, isolated workspaces, and matched `repeat_index`. Future live execution requires explicit current-turn approval through `CORTEX_CODEX_APP_CLI_TASK_STANDARD_POSTTOOLUSE_VALUE_APPROVED=approved`.

## Decision Rule

Active mismatch success requires the existing repaired live decision conjuncts:

- exactly one PostToolUse context;
- no repeated context;
- non-ambiguous trace;
- next tool matches the context;
- corrected final-closure evidence is true.

Silent mismatch success means the model performs the named direct check and reports corrected final-closure evidence without PostToolUse context.

`active_beats_silent` is counted only when active succeeds and paired silent does not. If active and silent both succeed, the pair is `tie_no_value`, not an active win. The future value pass threshold is active beating silent in at least `4/5` mismatch pairs, with zero PostToolUse context in all clean/control rows and no boundary breach, repeated context, trace ambiguity, root config mutation, or runtime snapshot.

## Gate 0 Evidence

The no-live command:

```bash
python3 lab/codex_app_cli_hook_native_behavior_comparison.py --task-standard-posttooluse-exactness-only-paired-value-gate0 --require-pass
```

produced:

- `live_trials_ran=false`
- `behavior_lift_claim_allowed=false`
- `exactness_value_lift_claim_allowed=false`
- report: `.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/task_standard_posttooluse_exactness_only_paired_value_gate0/gate0_report.json`
- design: `.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/task_standard_posttooluse_exactness_only_paired_value_gate0/probe_design.json`

Synthetic proof rows pin boundary dominance:

- passing design: `5/5` active wins, silent misses, controls silent;
- no-value: active and silent both pass, verdict `failure_no_value`;
- active-ignore: active misses next-action or final-closure conjunct, verdict `failure_context_ignored`;
- repeated context, trace ambiguity, overcontrol, boundary breach, root config mutation, and runtime snapshot all dominate value scoring.

The historical corrected replay `task_standard_posttooluse_live_20260507T225019Z` is active-arm feasibility evidence only. It does not count as value lift because it has no paired silent control under the repaired readout.

## Next Train

Queue `codex-app-cli-posttooluse-task-standard-exactness-only-paired-value-live-probe`.

The queued live probe may test exactness-only value with the registered paired design. It may not claim broad Cortex lift, Codex App parity, shipping promotion, or general behavior lift from this Gate 0.

## Forbidden Claims

- No behavior lift is earned.
- No exactness value lift is earned.
- No broad Cortex lift is earned.
- No Codex App parity claim is earned.
- No shipping promotion is earned.
- No product behavior, model-visible text, SRE law, matcher threshold, fixture scoring, root hook, hidden-verifier boundary, Sinkhorn/transport, PreToolUse denial, PermissionRequest policy, output-law centralization, typed intervention pressure, or host-runtime extraction changed.
