# Codex App/CLI PostToolUse Task-Standard Narrow Live Run

Surface: product live proof

## Verdict

Verdict: `failure_context_ignored`.

The approved narrow live probe ran the Codex App/CLI PostToolUse
task-standard actuator on the earned `task_standard_exactness` /
evidence-recovery surface. It did not pass. Cortex emitted exactly one
Codex-native PostToolUse `additionalContext` in the mismatch case, and clean
controls did not receive PostToolUse context, but the next model tool did not
perform the named direct check before closure. Under the precommitted verdict
rules, this queues an architecture decision before any text, policy, fixture,
scoring, matcher, or hook tuning.

## Evidence Basis

Preflight:

```bash
python3 -m pytest tests/product/test_openai_codex_app_cli_hook_client.py tests/product/test_openai_codex_app_cli_hook_coordinator.py tests/product/test_sre_task_standard_spine.py -q
python3 -m pytest tests/lab/test_codex_app_cli_hook_native_behavior_comparison.py -q
python3 lab/codex_app_cli_hook_native_behavior_comparison.py --task-standard-posttooluse-gate0 --require-pass
python3 lab/codex_app_cli_hook_native_behavior_comparison.py --task-standard-posttooluse-live
```

The approval-refusal run returned `verdict: not_run`.

Approved live command:

```bash
CORTEX_CODEX_APP_CLI_TASK_STANDARD_POSTTOOLUSE_APPROVED=approved python3 lab/codex_app_cli_hook_native_behavior_comparison.py --task-standard-posttooluse-live
```

Result artifacts:

- `.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/task_standard_posttooluse_live_20260507T100836Z/summary.json`
- `.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/task_standard_posttooluse_live_20260507T100836Z/trajectory.jsonl`
- per-trial stdout, stderr, hook diagnostics, hook trajectory, subject config, and workspace artifacts under the same run root

Run summary:

- verdict: `failure_context_ignored`
- failure reason: `next_model_tool_did_not_run_named_direct_check`
- `behavior_lift_claim_allowed`: `false`
- root `.codex/config.toml` hash unchanged:
  `a1c3291ce7aa69297d74654f3fed724f1e5d63fa038ae188371d4b899e1f5147`
- no runtime snapshot loaded
- hidden scoring stayed scoring-only and was not used by the subject
- subject configs were product-only and included
  `--enable-posttooluse-task-standard-context`

Mismatch case:

- signed UserPromptSubmit context reached the model
- three task-standard items were captured
- one PostToolUse context was emitted
- PostToolUse context item:
  `task-standard:closure_evidence:40d84127e1e9376d`
- PostToolUse context text asked for direct evidence through `wc -l` and exact
  byte checks such as `od -An -t x1 -c`
- the next model tool after the context did not perform the named direct check
  before closure
- Stop later emitted the existing locked overdue-verification block, and the
  continuation then produced stronger exactness checks

Control cases:

- `clean_evidenced`: 0 PostToolUse contexts
- `honest_blocker`: 0 PostToolUse contexts
- `waiting_on_user`: 0 PostToolUse contexts
- `unrelated_tool`: 0 PostToolUse contexts

The important nuance is timing: the PostToolUse context fired after an initial
failed `wc -l exact_result.txt` on a missing file. The model's next move was to
create the file, not to run the named direct check. Later exact checks came
after the Stop continuation loop, so this run does not prove that the
PostToolUse actuator changed the next action.

## What This Earns

- Live evidence that Codex CLI receives Cortex PostToolUse
  `hookSpecificOutput.additionalContext` in a real task-standard session.
- Live evidence that the actuator can emit a specific task-standard next-step
  context without over-controlling the clean/blocker/waiting/unrelated controls
  in this probe.
- Live negative evidence that the current PostToolUse timing/selection does not
  yet earn next-step actuator effect.

## What This Does Not Earn

- No broad Cortex behavior lift.
- No output-quality lift.
- No truth-gap lift.
- No exactness-only value lift.
- No claim that PostToolUse changed the next model action.
- No permission to tune signed UserPromptSubmit text, Stop text, SRE law,
  scored matcher, thresholds, fixtures, scoring, root hooks, hidden-verifier
  boundaries, Sinkhorn/transport, PreToolUse denial, or PermissionRequest
  policy after seeing this result.
- No Codex App parity or shipping promotion.

## Next Move

Queue `codex-app-cli-posttooluse-task-standard-actuator-architecture-decision`.
The next seam should decide whether the PostToolUse actuator should fire after
failed pre-artifact checks, whether its signal should target action timing
rather than evidence wording, and whether Stop remains the only observed
effective correction loop for this shape. It should be a decision seam, not a
text or policy remediation seam.
