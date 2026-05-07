# Codex App/CLI PostToolUse Task-Standard Phase-Aware Narrow Live Rerun After Shared Tool Evidence

Surface: product live proof

Date: 2026-05-07

## Verdict

Verdict: `fail` with failure reason `repeated_posttooluse_context_loop`.

The approved phase-aware narrow live rerun exercised the Codex App/CLI
PostToolUse task-standard actuator after firing-boundary remediation, causal
trace IDs, overcontrol remediation, and shared SRE-owned tool-evidence
classification. It did not pass. The mismatch case emitted PostToolUse
`additionalContext`, but emitted it three times. Under the precommitted live
verdict rules, repeated PostToolUse context is a hard `fail` before any
next-action interpretation.

## Evidence Basis

Preflight:

```bash
python3 -m pytest tests/product/test_openai_codex_app_cli_hook_client.py tests/product/test_openai_codex_app_cli_hook_coordinator.py tests/product/test_sre_task_standard_spine.py tests/product/test_sre_tool_evidence.py -q
python3 -m pytest tests/lab/test_codex_app_cli_hook_native_behavior_comparison.py -q
python3 lab/codex_app_cli_hook_native_behavior_comparison.py --task-standard-posttooluse-shared-tool-evidence-gate0 --require-pass
python3 lab/codex_app_cli_hook_native_behavior_comparison.py --task-standard-posttooluse-live
```

The approval-refusal run returned `verdict: not_run`.

Approved live command:

```bash
CORTEX_CODEX_APP_CLI_TASK_STANDARD_POSTTOOLUSE_APPROVED=approved python3 lab/codex_app_cli_hook_native_behavior_comparison.py --task-standard-posttooluse-live
```

Result artifacts:

- `.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/task_standard_posttooluse_live_20260507T213732Z/summary.json`
- `.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/task_standard_posttooluse_live_20260507T213732Z/trajectory.jsonl`
- per-trial stdout, stderr, hook diagnostics, hook trajectory, subject config,
  and workspace artifacts under the same run root

Run summary:

- verdict: `fail`
- failure reason: `repeated_posttooluse_context_loop`
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
- PostToolUse context count: 3
- `posttooluse_context_repeated`: `true`
- no PostToolUse context boundary-breach text appeared
- first missing-artifact check stayed silent with private
  `pre_artifact_candidate_missing`
- candidate-artifact and markerless rows stayed silent before later readback
- context row `10` and row `11` repeated the same item
  `task-standard:work_standard:929237a14cf4d738`
- context row `13` emitted for
  `task-standard:closure_evidence:7608236188fd9be6`
- row `16` then stayed silent with private
  `posttooluse_context_session_cap_reached`

The mismatch trace was also not interpretable as a next-action effect:
`posttooluse_context_trace_ambiguous` was `true`, with ambiguity reason
`posttooluse_tool_event_ref_not_found_in_stdout`. Hook rows carried
`call_*` tool ids while stdout-derived command rows carried `item_*` refs, so
the harness correctly refused to infer the preceding or next tool by ordinal
position.

Control cases:

- `clean_evidenced`: 0 PostToolUse contexts
- `honest_blocker`: 0 PostToolUse contexts
- `waiting_on_user`: 0 PostToolUse contexts
- `unrelated_tool`: 0 PostToolUse contexts

The prior clean-control overcontrol did not reproduce. That does not rescue
the run, because the repeated-context loop and ambiguous live trace prevent a
valid next-action interpretation.

## What This Earns

- Live evidence that the shared tool-evidence classifier and overcontrol
  remediation kept clean, blocker, waiting, and unrelated controls silent.
- Live evidence that the mismatch path can emit Codex-native PostToolUse
  `additionalContext` after candidate/readback work.
- Live negative evidence that PostToolUse context-loop control is insufficient
  in real Codex CLI timing.
- Live negative evidence that the current hook/stdout event-ref join is not yet
  sufficient for this live run shape.

## What This Does Not Earn

- no broad Cortex behavior lift
- no output-quality lift
- no truth-gap lift
- no exactness-only value lift
- no PostToolUse next-action effect claim
- no clean-control safety promotion beyond this narrow failed run
- no Codex App parity or shipping promotion
- no permission to tune signed UserPromptSubmit text, PostToolUse text, Stop
  text, SRE law, scored matcher, thresholds, fixtures, scoring, root hooks,
  hidden-verifier boundaries, Sinkhorn/transport, PreToolUse denial, or
  PermissionRequest policy after seeing this result
- no permission to run another live probe before no-live context-loop and
  live-trace remediation passes

## Next Move

Queue `codex-app-cli-posttooluse-task-standard-context-loop-trace-remediation`.

The next seam should be no-live. It should prove the actuator cannot emit a
repeated PostToolUse context loop for the same unresolved task-standard item
under live-equivalent timing, and it should prove the live harness can join
hook rows to stdout-derived command rows without relying on ordinal position.
It must preserve the existing model-visible text, SRE law, matcher thresholds,
fixtures, scoring semantics, root hooks, hidden-verifier boundary,
Sinkhorn/transport deferral, PreToolUse denial deferral, and PermissionRequest
policy.
