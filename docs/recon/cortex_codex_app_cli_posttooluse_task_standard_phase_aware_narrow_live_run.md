# Codex App/CLI PostToolUse Task-Standard Phase-Aware Narrow Live Run

Surface: product live proof

Date: 2026-05-07

## Verdict

Verdict: `failure_no_context`.

The approved phase-aware narrow live probe ran the Codex App/CLI PostToolUse
task-standard actuator on the earned `task_standard_exactness` /
evidence-recovery surface. It did not pass. The mismatch case captured the
model-derived task standard, observed PostToolUse lifecycle rows, and observed
candidate artifact prerequisite work, but emitted zero PostToolUse
`additionalContext` rows. Under the precommitted verdict rules, this is
`failure_no_context` with failure reason
`candidate_artifact_without_posttooluse_context`.

## Evidence Basis

Preflight:

```bash
python3 -m pytest tests/product/test_openai_codex_app_cli_hook_client.py tests/product/test_openai_codex_app_cli_hook_coordinator.py tests/product/test_sre_task_standard_spine.py -q
python3 -m pytest tests/lab/test_codex_app_cli_hook_native_behavior_comparison.py -q
python3 lab/codex_app_cli_hook_native_behavior_comparison.py --task-standard-posttooluse-phase-aware-gate0 --require-pass
python3 lab/codex_app_cli_hook_native_behavior_comparison.py --task-standard-posttooluse-live
```

The approval-refusal run returned `verdict: not_run`.

Approved live command:

```bash
CORTEX_CODEX_APP_CLI_TASK_STANDARD_POSTTOOLUSE_APPROVED=approved python3 lab/codex_app_cli_hook_native_behavior_comparison.py --task-standard-posttooluse-live
```

Result artifacts:

- `.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/task_standard_posttooluse_live_20260507T142129Z/summary.json`
- `.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/task_standard_posttooluse_live_20260507T142129Z/trajectory.jsonl`
- per-trial stdout, stderr, hook diagnostics, hook trajectory, subject config,
  and workspace artifacts under the same run root

Run summary:

- verdict: `failure_no_context`
- failure reason: `candidate_artifact_without_posttooluse_context`
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
- PostToolUse context count: 0
- no PostToolUse context hash, item id, reason, or repeated context loop
- first failed missing-artifact readback stayed silent with private
  `pre_artifact_candidate_missing`
- the artifact creation row then stayed silent with private
  `no_verification_marker`
- later readback rows stayed silent with private
  `no_candidate_artifact_or_readback`
- no model-visible PostToolUse text was emitted, so there was no
  PostToolUse next-action effect to evaluate

The mismatch command sequence created `exact_result.txt` and later performed
direct checks (`wc -l`, `wc -c`, `od`, and `cmp`). Those checks came without a
PostToolUse context. The existing Stop continuation loop still emitted the
locked overdue-verification block once and the continuation produced stronger
exactness evidence, so Stop remains the only live-proven corrective actuator
for this exactness shape.

Control cases:

- `clean_evidenced`: 0 PostToolUse contexts
- `honest_blocker`: 0 PostToolUse contexts
- `waiting_on_user`: 0 PostToolUse contexts
- `unrelated_tool`: 0 PostToolUse contexts

No clean/control overcontrol occurred.

## What This Earns

- Live evidence that the phase-aware subject config ran with the PostToolUse
  task-standard context flag enabled.
- Live evidence that task-standard capture, product-only config, hidden-scoring
  isolation, root-config stability, runtime-snapshot exclusion, and clean/control
  silence held in this probe.
- Live negative evidence that the current phase-aware firing boundary did not
  emit PostToolUse context after candidate artifact work in the mismatch case.

## What This Does Not Earn

- no broad Cortex behavior lift
- no output-quality lift
- no truth-gap lift
- no exactness-only value lift
- no PostToolUse next-action effect claim
- no Codex App parity or shipping promotion
- no permission to tune signed UserPromptSubmit text, PostToolUse text, Stop
  text, SRE law, scored matcher, thresholds, fixtures, scoring, root hooks,
  hidden-verifier boundaries, Sinkhorn/transport, PreToolUse denial, or
  PermissionRequest policy after seeing this result
- no permission to rerun live before no-live firing-boundary remediation passes

## Next Move

Queue `codex-app-cli-posttooluse-task-standard-firing-boundary-remediation`.

The next seam should reproduce and fix why the live candidate-artifact and
readback PostToolUse rows stayed silent after phase-aware Gate 0 passed. It
should be no-live first, keep the existing model-visible text and SRE/scoring
law fixed, and prove candidate-artifact mismatch emits one context while clean
and control rows stay silent before any further live run.
