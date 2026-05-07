# Codex App/CLI PostToolUse Task-Standard Narrow Live Probe

Surface: product host actuator + live-proof harness

## Verdict

Verdict: `live_probe_harness_ready_not_run`.

This no-spend implementation seam adds the approval-gated live probe surface for
the Gate-0-proven PostToolUse task-standard actuator. The live command was not
run in this seam because explicit current-turn approval was not provided.

## Evidence Basis

- New CLI mode:
  `python3 lab/codex_app_cli_hook_native_behavior_comparison.py --task-standard-posttooluse-live`.
- Approval env:
  `CORTEX_CODEX_APP_CLI_TASK_STANDARD_POSTTOOLUSE_APPROVED=approved`.
- The live mode refuses without approval.
- The generated subject config uses product hooks only, enables signed
  task-standard text and `--enable-posttooluse-task-standard-context`, and omits
  runtime snapshots.
- The verdict classifier distinguishes pass, no-context, ignored-context,
  overcontrol, scoped-negative, and boundary failure outcomes without changing
  runtime policy.

## Boundary

This seam changes lab proof machinery and status truth only. It does not run
Codex live, does not claim behavior lift, and does not change signed
UserPromptSubmit text, Stop text, SRE law, scored matcher, thresholds, fixtures,
scoring, root hooks, hidden-verifier boundaries, Sinkhorn/transport, PreToolUse
denial, or PermissionRequest policy.

## Next Move

Queue `codex-app-cli-posttooluse-task-standard-narrow-live-run`.

That future run still requires explicit current-turn approval and must not use
`--require-pass`; negative verdicts are valid evidence.
