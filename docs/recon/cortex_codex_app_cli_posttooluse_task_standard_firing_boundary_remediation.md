# Codex App/CLI PostToolUse Task-Standard Firing-Boundary Remediation

Surface: product host actuator + no-live remediation proof

Date: 2026-05-07

## Verdict

Verdict: `pass_posttooluse_firing_boundary_gate0`.

The no-live firing-boundary Gate 0 reproduced the live-equivalent payload
shape from `task_standard_posttooluse_live_20260507T142129Z` and fixed the
phase-aware PostToolUse eligibility gap. The coordinator now treats a
PostToolUse row as completed for the phase-aware task-standard candidate and
readback gate when `tool_response` is present, `payload.error` is absent, and
failure or missing-artifact markers are absent. This predicate is scoped to
phase-aware PostToolUse task-standard context eligibility and does not change
the generic tool-success classifier, SRE law, Stop behavior, or scoring.

## Evidence Basis

Structural proof command:

```bash
python3 lab/codex_app_cli_hook_native_behavior_comparison.py --task-standard-posttooluse-firing-boundary-gate0 --require-pass
```

Result artifact:

- `.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/task_standard_posttooluse_firing_boundary_gate0/gate0_report.json`

Run summary:

- verdict: `pass_posttooluse_firing_boundary_gate0`
- `live_trials_ran`: `false`
- `behavior_lift_claim_allowed`: `false`
- root `.codex/config.toml` hash unchanged:
  `a1c3291ce7aa69297d74654f3fed724f1e5d63fa038ae188371d4b899e1f5147`
- no runtime snapshot loaded
- hidden scoring stayed scoring-only
- no Stop block, PreToolUse deny, PermissionRequest, root hook mutation, or
  Sinkhorn/transport path appeared

Boundary results:

- live-equivalent missing artifact stayed silent with private
  `pre_artifact_candidate_missing`
- live-equivalent empty-output candidate artifact creation emitted one
  Codex-native PostToolUse `additionalContext`
- live-equivalent readback output without exit/status markers emitted one
  Codex-native PostToolUse `additionalContext`
- clean evidenced work stayed silent after no unresolved required item remained
- markerless aligned literal output stayed silent with private
  `no_verification_marker`
- failed candidate, blocker, waiting, unrelated, generic-output, and markerless
  controls stayed silent

The model-visible PostToolUse text itself did not change. The context remains
the existing direct-evidence template and the existing unresolved-item
selection, per-session cap, deduplication, and Codex-native JSON shape remain
unchanged.

## What This Earns

- No-live evidence that the live-equivalent candidate artifact row can now fire
  PostToolUse context without exit/status fields.
- No-live evidence that a live-equivalent readback row can now be treated as
  readback-shaped without exit/status fields.
- No-live evidence that the missing-artifact precondition still spends no
  context and clean/control rows stay silent.

## What This Does Not Earn

- no live behavior lift
- no exactness-only value lift
- no broad Cortex lift
- no output-quality lift
- no truth-gap lift
- no PostToolUse next-action effect claim
- no Codex App parity or shipping promotion
- no permission to tune signed UserPromptSubmit text, PostToolUse text, Stop
  text, SRE law, scored matcher, thresholds, fixtures, scoring, root hooks,
  hidden-verifier boundaries, Sinkhorn/transport, PreToolUse denial, or
  PermissionRequest policy

## Next Move

Queue `codex-app-cli-posttooluse-task-standard-phase-aware-narrow-live-rerun`.

The rerun still requires explicit current-turn approval, must not use
`--require-pass`, and may interpret only narrow PostToolUse actuator evidence
on `task_standard_exactness` / evidence recovery. It is not a three-arm
behavior comparison and cannot claim broad Cortex lift.
