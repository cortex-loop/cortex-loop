# Codex App/CLI PostToolUse Task-Standard Overcontrol Remediation

Surface: product host actuator + no-live remediation proof

Date: 2026-05-07

## Verdict

Verdict: `pass_posttooluse_overcontrol_gate0`.

The no-live overcontrol Gate 0 reproduced the live-equivalent clean-control
failure shape from `task_standard_posttooluse_live_20260507T153242Z` and fixed
the context-spend boundary. The coordinator now treats command usage/option
diagnostics such as `cat: illegal option -- A` and `usage:` as a failed
verification/readback phase for the phase-aware PostToolUse task-standard
context gate. That predicate is scoped to PostToolUse task-standard
candidate/readback eligibility and does not change the generic tool-success
classifier, SRE law, Stop behavior, or scoring.

The generic tool-success classifier itself did not change.

The mismatch candidate artifact and readback context paths still fire.

## Evidence Basis

Structural proof command:

```bash
python3 lab/codex_app_cli_hook_native_behavior_comparison.py --task-standard-posttooluse-overcontrol-gate0 --require-pass
```

Result artifact:

- `.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/task_standard_posttooluse_overcontrol_gate0/gate0_report.json`

Run summary:

- verdict: `pass_posttooluse_overcontrol_gate0`
- `live_trials_ran`: `false`
- `behavior_lift_claim_allowed`: `false`
- root `.codex/config.toml` hash unchanged:
  `a1c3291ce7aa69297d74654f3fed724f1e5d63fa038ae188371d4b899e1f5147`
- no runtime snapshot loaded
- hidden scoring stayed scoring-only
- no Stop block, PreToolUse deny, PermissionRequest, root hook mutation, or
  Sinkhorn/transport path appeared

Boundary results:

- live-equivalent failed clean check stayed silent with private
  `phase_check_failed`
- live-equivalent candidate artifact still emitted one Codex-native
  PostToolUse `additionalContext`
- live-equivalent readback still emitted one Codex-native PostToolUse
  `additionalContext`
- clean evidenced, blocker, waiting, unrelated, markerless, generic, failed,
  and missing-artifact controls stayed silent
- pre-artifact missing still stayed private as `pre_artifact_candidate_missing`
- markerless aligned literal output still stayed private as
  `no_verification_marker`

The model-visible PostToolUse text itself did not change. The existing
direct-evidence template, unresolved-item selection, per-session cap,
deduplication, and Codex-native JSON shape remain unchanged.

## What This Earns

- No-live evidence that a live-equivalent failed verification/readback phase no
  longer receives PostToolUse context.
- No-live evidence that the mismatch candidate artifact and readback context
  paths still fire after the overcontrol remediation.
- No-live evidence that clean/control cases stay silent under the synthetic
  live-equivalent harness.

## What This Does Not Earn

- no live behavior lift
- no exactness-only value lift
- no broad Cortex lift
- no output-quality lift
- no truth-gap lift
- no clean-control safety claim in live use
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
