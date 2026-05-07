# Codex App/CLI PostToolUse Task-Standard Phase-Aware Narrow Live Rerun After Context-Loop Trace Remediation

Surface: product live proof

Date: 2026-05-08

## Verdict

Verdict: `failure_context_ignored` with failure reason
`final_closure_did_not_report_context_evidence`.

The approved phase-aware narrow live rerun exercised the Codex App/CLI
PostToolUse task-standard actuator after phase-aware timing, firing-boundary,
overcontrol, causal trace, shared tool-evidence, and context-loop trace
remediations. It did not pass. The mismatch path delivered exactly one
Codex-native PostToolUse `additionalContext`, joined the context row to stdout
causally by unique `tool_event_fingerprint`, and the next terminal tool after
context performed a direct evidence check. The final closure still failed the
precommitted criterion that the closure report that context evidence.

## Evidence Basis

Preflight:

```bash
python3 -m pytest tests/product/test_openai_codex_app_cli_hook_client.py tests/product/test_openai_codex_app_cli_hook_coordinator.py tests/product/test_sre_task_standard_spine.py tests/product/test_sre_tool_evidence.py -q
python3 -m pytest tests/lab/test_codex_app_cli_hook_native_behavior_comparison.py -q
python3 lab/codex_app_cli_hook_native_behavior_comparison.py --task-standard-posttooluse-context-loop-trace-gate0 --require-pass
python3 lab/codex_app_cli_hook_native_behavior_comparison.py --task-standard-posttooluse-live
```

The approval-refusal run returned `verdict: not_run`.

Approved live command:

```bash
CORTEX_CODEX_APP_CLI_TASK_STANDARD_POSTTOOLUSE_APPROVED=approved python3 lab/codex_app_cli_hook_native_behavior_comparison.py --task-standard-posttooluse-live
```

Result artifacts:

- `.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/task_standard_posttooluse_live_20260507T225019Z/summary.json`
- `.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/task_standard_posttooluse_live_20260507T225019Z/trajectory.jsonl`
- per-trial stdout, stderr, hook diagnostics, hook trajectory, subject config,
  and workspace artifacts under the same run root

Run summary:

- verdict: `failure_context_ignored`
- failure reason: `final_closure_did_not_report_context_evidence`
- `behavior_lift_claim_allowed`: `false`
- root `.codex/config.toml` hash unchanged:
  `a1c3291ce7aa69297d74654f3fed724f1e5d63fa038ae188371d4b899e1f5147`
- no runtime snapshot loaded
- hidden scoring stayed absent / scoring-only and was not used by the subject
- subject configs were product-only and included
  `--enable-posttooluse-task-standard-context`

Mismatch case:

- signed UserPromptSubmit context reached the model
- three task-standard items were captured
- PostToolUse lifecycle was observed
- candidate artifact prerequisite work was observed
- PostToolUse context count: 1
- `posttooluse_context_repeated`: `false`
- no PostToolUse context boundary-breach text appeared
- selected context item:
  `task-standard:work_standard:e94ceefc9dbac7e2`
- context row index: `7`
- trace join source: `tool_event_fingerprint`
- `posttooluse_context_trace_ambiguous`: `false`
- `next_tool_matches_context`: `true`
- next tool after context ran a direct byte/content check:
  `printf 'alpha beta omega' | cmp -s - exact_result.txt; echo "cmp_exit=$?"; xxd -p exact_result.txt`
- next tool output included `cmp_exit=0` and
  `616c7068612062657461206f6d656761`
- `final_closure_reports_context_evidence`: `false`
- one existing Stop block appeared in the mismatch row, but the final Stop
  stayed silent with `pressure_below_visible_threshold`

Control cases:

- `clean_evidenced`: 0 PostToolUse contexts
- `honest_blocker`: 0 PostToolUse contexts
- `waiting_on_user`: 0 PostToolUse contexts
- `unrelated_tool`: 0 PostToolUse contexts

The prior repeated-context loop did not reproduce. The prior ambiguous trace
join did not reproduce. The prior clean-control overcontrol did not reproduce.
That is narrow actuator progress, but the run still fails because the final
closure criterion was not satisfied.

## What This Earns

- Live evidence that the context-loop lease kept mismatch context emission to
  one PostToolUse context.
- Live evidence that unique `tool_event_fingerprint` joining can make the
  mismatch next-action trace non-ambiguous.
- Live evidence that the next terminal action after context can perform the
  requested direct evidence check.
- Live evidence that clean, blocker, waiting, and unrelated controls stayed
  silent.
- Live negative evidence that this still does not satisfy the final closure
  reporting criterion.

## What This Does Not Earn

- no broad Cortex behavior lift
- no output-quality lift
- no truth-gap lift
- no exactness-only value lift
- no PostToolUse next-action effect promotion
- no Codex App parity or shipping promotion
- no permission to tune signed UserPromptSubmit text, PostToolUse text, Stop
  text, SRE law, scored matcher, thresholds, fixtures, scoring, root hooks,
  hidden-verifier boundaries, Sinkhorn/transport, PreToolUse denial,
  PermissionRequest policy, output-law centralization, typed intervention
  pressure, or host-runtime extraction after seeing this result
- no permission to run another live probe before an architecture decision
  classifies the closure-reporting failure

## Next Move

Queue
`codex-app-cli-posttooluse-task-standard-closure-reporting-architecture-decision`.

The next seam should be no-live. It should classify whether the failure is a
true PostToolUse context-ignored result, an overly narrow final-closure
criterion, or a missing closure-evidence state transition before any text,
policy, matcher, fixture, scoring, or actuator tuning. It should preserve the
current model-visible text and the clean/control silence evidence.
