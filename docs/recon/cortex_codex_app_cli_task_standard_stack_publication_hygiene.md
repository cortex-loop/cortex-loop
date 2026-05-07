# Codex App/CLI Task-Standard Stack Publication Hygiene

Surface: workflow / product-proof hygiene

## Verdict

Verdict: `stack_publication_hygiene_required_before_live_probe`.

The task-standard stack contains real completed product and proof work, but the
work had accumulated on a stale `offline-replay-readiness-gate` branch while
current truth had advanced to PostToolUse calibration. This seam records the
publication correction: split the completed work onto
`codex/20260506-020000-task-standard-stack-publication-hygiene` as a reviewable
stack before any narrow live PostToolUse probe is approved.

## Evidence Basis

- The stack now separates scored lexical alignment, offline readiness/readouts,
  lifecycle actuator mapping, PostToolUse context wiring, and pre-live
  hardening into explicit commits.
- The old local
  `codex/20260506-015000-codex-app-cli-task-standard-offline-replay-readiness-gate`
  anchor is preserved until the stack is merged or intentionally retired.
- The queued next train remains
  `codex-app-cli-posttooluse-task-standard-narrow-live-probe`, but live approval
  is blocked until this stack is published or merged and cleanup no longer
  reports dirty worktree state.
- The narrow PostToolUse live probe remains queued but not approved by this
  seam.

## Forbidden Claims

- No live behavior lift is earned.
- No broad Cortex lift, output-quality lift, truth-gap lift, Codex App parity,
  or shipping promotion is earned.
- No signed task-standard text, Stop text, SRE law, selector threshold, fixture,
  scoring, root hook, hidden-verifier boundary, Sinkhorn/transport, PreToolUse
  denial, or PermissionRequest policy changed in this seam.
- The narrow live PostToolUse probe remains future work and still requires
  explicit current-turn approval; it must not use `--require-pass`.

## Next Move

Publish or merge the stack, then rerun cleanup hygiene. Only after the stack is
cleanly landed may the queued narrow live PostToolUse probe be considered.
