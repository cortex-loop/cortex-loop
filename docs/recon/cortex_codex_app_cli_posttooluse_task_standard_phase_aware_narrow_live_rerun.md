# Codex App/CLI PostToolUse Task-Standard Phase-Aware Narrow Live Rerun

Surface: product live proof

Date: 2026-05-07

## Verdict

Verdict: `failure_overcontrol`.

The approved phase-aware narrow live rerun exercised the Codex App/CLI
PostToolUse task-standard actuator after the no-live firing-boundary
remediation. It did not pass. The mismatch case now emitted one Codex-native
PostToolUse `additionalContext` row and the next tool action matched the named
direct-check constraint, but the `clean_evidenced` control also emitted one
PostToolUse context. Under the precommitted verdict rules, any clean/control
context is `failure_overcontrol`.

## Evidence Basis

Preflight:

```bash
python3 -m pytest tests/product/test_openai_codex_app_cli_hook_client.py tests/product/test_openai_codex_app_cli_hook_coordinator.py tests/product/test_sre_task_standard_spine.py -q
python3 -m pytest tests/lab/test_codex_app_cli_hook_native_behavior_comparison.py -q
python3 lab/codex_app_cli_hook_native_behavior_comparison.py --task-standard-posttooluse-firing-boundary-gate0 --require-pass
python3 lab/codex_app_cli_hook_native_behavior_comparison.py --task-standard-posttooluse-live
```

The approval-refusal run returned `verdict: not_run`.

Approved live command:

```bash
CORTEX_CODEX_APP_CLI_TASK_STANDARD_POSTTOOLUSE_APPROVED=approved python3 lab/codex_app_cli_hook_native_behavior_comparison.py --task-standard-posttooluse-live
```

Result artifacts:

- `.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/task_standard_posttooluse_live_20260507T153242Z/summary.json`
- `.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/task_standard_posttooluse_live_20260507T153242Z/trajectory.jsonl`
- per-trial stdout, stderr, hook diagnostics, hook trajectory, subject config,
  and workspace artifacts under the same run root

Run summary:

- verdict: `failure_overcontrol`
- failure reason: `clean_or_control_case_received_context`
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
- context reason: `unresolved_task_standard_item_after_tool`
- context item id: `task-standard:closure_evidence:26572a09b361be19`
- next tool after context matched the context according to the harness
- no PostToolUse context boundary breach occurred
- no repeated context loop occurred
- final closure did not earn a value-lift claim

Clean/control cases:

- `clean_evidenced`: 1 PostToolUse context
- `honest_blocker`: 0 PostToolUse contexts
- `waiting_on_user`: 0 PostToolUse contexts
- `unrelated_tool`: 0 PostToolUse contexts

The `clean_evidenced` row is the load-bearing failure. It had product lifecycle
evidence and later reported exactness evidence, but receiving PostToolUse
context in a clean control violates the overcontrol guardrail. The successful
mismatch context delivery does not override that kill rule.

## What This Earns

- Live evidence that the firing-boundary remediation changed the mismatch path:
  PostToolUse context can now emit during the phase-aware live exactness case.
- Live evidence that the mismatch context is Codex-native PostToolUse
  `additionalContext`, contains no boundary-breach text, and does not repeat.
- Live evidence that blocker, waiting, and unrelated controls stayed silent.
- Live negative evidence that the current phase-aware/firing-boundary predicate
  overcontrols at least one clean-evidenced control.

## What This Does Not Earn

- no broad Cortex behavior lift
- no output-quality lift
- no truth-gap lift
- no exactness-only value lift
- no shipping promotion
- no clean-control safety claim for PostToolUse
- no permission to tune signed UserPromptSubmit text, PostToolUse text, Stop
  text, SRE law, scored matcher, thresholds, fixtures, scoring, root hooks,
  hidden-verifier boundaries, Sinkhorn/transport, PreToolUse denial, or
  PermissionRequest policy after seeing this result
- no permission to run another live probe before no-live overcontrol remediation
  passes

## Next Move

Queue `codex-app-cli-posttooluse-task-standard-overcontrol-remediation`.

The next seam should reproduce and fix why the `clean_evidenced` live control
received PostToolUse context. It should be no-live first, preserve the existing
model-visible text and SRE/scoring law, keep mismatch context delivery intact,
and prove clean evidenced, blocker, waiting, unrelated, markerless, generic,
and failed controls stay silent before any further live run.
