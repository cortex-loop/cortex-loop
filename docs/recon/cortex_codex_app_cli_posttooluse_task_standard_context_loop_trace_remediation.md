# Codex App/CLI PostToolUse Task-Standard Context-Loop Trace Remediation

Surface: product host actuator plus lab trace proof

Date: 2026-05-08

## Verdict

Verdict: `pass_posttooluse_context_loop_trace_gate0`.

The no-live remediation fixed the two blockers from
`task_standard_posttooluse_live_20260507T213732Z`: repeated PostToolUse
task-standard context emission and non-causal hook/stdout trace joining. The
proof did not run live Codex and does not earn behavior lift.

## Evidence Basis

Gate 0 command:

```bash
python3 lab/codex_app_cli_hook_native_behavior_comparison.py --task-standard-posttooluse-context-loop-trace-gate0 --require-pass
```

Result artifact:

- `.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/task_standard_posttooluse_context_loop_trace_gate0/gate0_report.json`

Gate 0 result:

- verdict: `pass_posttooluse_context_loop_trace_gate0`
- `behavior_lift_claim_allowed`: `false`
- live trials ran: `false`
- first live-equivalent eligible mismatch PostToolUse row emitted one existing-shape context
- second live-equivalent PostToolUse row stayed silent with
  `posttooluse_context_active_context_pending`
- only one PostToolUse task-standard context item was recorded
- exact `tool_event_ref` trace joining still works
- unique `tool_event_fingerprint` trace joining works when hook `call_*` ids and
  stdout `item_*` refs differ
- duplicate or missing fingerprints are marked ambiguous
- no ordinal fallback is used
- legacy trace artifacts without enough join material remain uninterpreted
- clean evidenced, missing-artifact, failed-check, markerless, failed-candidate,
  blocker, waiting, unrelated, and generic controls stayed silent
- no Stop, PreToolUse, PermissionRequest, transport, runtime snapshot, root
  config, hidden scoring, or boundary-text path appeared

## What Changed

The Codex App/CLI file-backed session store now protects per-session
load/update/save with a lock and writes JSON state through atomic replace. The
PostToolUse task-standard actuator now treats one emitted context as an active
repair lease; later PostToolUse rows stay silent until a later seam earns
multi-context sequencing.

The lab trace model keeps exact `tool_event_ref` joins and adds diagnostic-only
`tool_event_fingerprint` joins for future live-shaped rows. If neither exact id
nor unique fingerprint can join the hook row to stdout command records, the
trace remains ambiguous rather than inferred by list position.

## What This Earns

- no-live proof that the repeated-context loop is structurally blocked
- no-live proof that future hook/stdout trace joining can be non-ordinal
- no-live proof that clean/control silence survived the lease and trace changes
- permission to queue another approval-gated phase-aware narrow live rerun

## What This Does Not Earn

- no broad Cortex behavior lift
- no exactness value lift
- no PostToolUse next-action effect claim
- no output-quality lift
- no truth-gap lift
- no Codex App parity or shipping promotion
- no permission to change signed UserPromptSubmit text, PostToolUse text, Stop
  text, SRE law, matcher thresholds, fixtures, scoring semantics, root hooks,
  hidden-verifier boundary, Sinkhorn/transport, PreToolUse denial,
  PermissionRequest policy, output-law centralization, typed intervention
  pressure, or host-runtime extraction
- no permission to run live without explicit current-turn approval

## Next Move

Queue `codex-app-cli-posttooluse-task-standard-phase-aware-narrow-live-rerun`.

The rerun must remain approval-gated, must not use `--require-pass`, and can
earn only narrow PostToolUse actuator evidence on `task_standard_exactness` /
evidence recovery. Negative verdicts remain valid evidence.
