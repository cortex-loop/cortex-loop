# Codex App/CLI PostToolUse Task-Standard Final-Closure Readout Remediation Gate 0

Surface: lab proof readout remediation

Date: 2026-05-08

## Verdict

Verdict: `pass_posttooluse_final_closure_readout_gate0`.

The lab final-closure readout now accepts the semantic exactness evidence shape
observed in `task_standard_posttooluse_live_20260507T225019Z`: `PASS`,
`bytes=16`, expected hex `616c7068612062657461206f6d656761`, exact
`alpha beta omega`, and byte-match language such as `cmp_exit=0` or exact byte
match. The decision ordering is unchanged: this final-output readout is consumed
only after context delivery, clean/control silence, non-ambiguous trace, and
next-action match have already passed.

The new semantic shape explicitly includes exact byte match evidence.

This is no-live lab proof only. It does not change product host behavior,
signed UserPromptSubmit text, PostToolUse text, Stop text, SRE law, matcher
thresholds, fixtures, scoring semantics, root hooks, hidden-verifier
boundaries, Sinkhorn/transport, PreToolUse denial, PermissionRequest policy,
output-law centralization, typed intervention pressure, or host-runtime
extraction.

No behavior lift, exactness value lift, broad Cortex lift, Codex App parity, or
shipping promotion is earned.

## Corrected Replay Table

| Artifact | Registered verdict | Old final readout | Corrected final readout | Corrected verdict |
| --- | --- | --- | --- | --- |
| `task_standard_posttooluse_live_20260507T100836Z` | `failure_context_ignored` | `false` | `true` | `failure_context_ignored` / `next_model_tool_did_not_run_named_direct_check` |
| `task_standard_posttooluse_live_20260507T142129Z` | `failure_no_context` | `false` | `true` | `failure_no_context` / `candidate_artifact_without_posttooluse_context` |
| `task_standard_posttooluse_live_20260507T153242Z` | `failure_overcontrol` | `false` | `true` | `failure_overcontrol` / `clean_or_control_case_received_context` |
| `task_standard_posttooluse_live_20260507T213732Z` | `fail` | `false` | `true` | `fail` / `repeated_posttooluse_context_loop` |
| `task_standard_posttooluse_live_20260507T225019Z` | `failure_context_ignored` | `false` | `true` | `pass_posttooluse_next_step_observed` |

Gate 0 report path:

`.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/task_standard_posttooluse_final_closure_readout_gate0/gate0_report.json`

The report has `live_trials_ran=false`, `behavior_lift_claim_allowed=false`,
`passed=true`, and `verdict=pass_posttooluse_final_closure_readout_gate0`.

## Boundary Dominance

The corrected final-closure readout does not mask earlier blockers:

- `20260507T100836Z` remains a true next-action ignore because the next model
  tool did not run the named direct check.
- `142129Z` remains no-context because candidate/readback-shaped prerequisite
  work occurred without PostToolUse context.
- `153242Z` remains overcontrol because the clean evidenced control received
  PostToolUse context.
- `213732Z` remains uninterpretable because repeated context and trace ambiguity
  dominate final-output evidence.
- `225019Z` becomes the only corrected replay pass because it delivered exactly
  one PostToolUse context, joined non-ambiguously by `tool_event_fingerprint`,
  ran the named direct check next, kept controls silent, and reported the
  semantic final evidence.

## Next Train

Queue:

`codex-app-cli-posttooluse-task-standard-exactness-only-paired-value-probe-gate0`

That next seam must be no-live unless it explicitly earns and records live-spend
approval later. It should design the exactness-only paired value probe from the
corrected readout evidence, not claim broad Cortex lift or queue a live rerun
directly from this Gate 0.
