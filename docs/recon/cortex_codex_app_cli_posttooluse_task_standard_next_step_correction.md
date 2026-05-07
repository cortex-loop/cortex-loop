# Codex App/CLI PostToolUse Task-Standard Next-Step Correction

Surface: product host actuator + lab proof

Verdict: `pass_posttooluse_gate0`; implementation remains Gate-0 only.

## Summary

This seam adds the first upstream Codex App/CLI task-standard actuator:
flag-gated PostToolUse `additionalContext` after product-visible tool evidence
leaves a specific captured standard item unresolved. The actuator is host-side
Codex policy; task-standard state and matching remain host-agnostic SRE law.
Flag: `--enable-posttooluse-task-standard-context`. The context fires only
when a specific captured task-standard item is unresolved.

The Gate 0 harness emitted one Codex-native PostToolUse context for the
`task_standard_exactness` evidence-recovery mismatch and stayed silent for clean
evidenced work, unrelated/generic activity, honest blocker, and waiting-on-user
controls. Gate 0 controls: flag disabled stayed silent, clean-evidenced work
stayed silent, blocker/waiting/unrelated-tool controls stayed silent. No live
Codex run was executed.

## Evidence

- Command: `python3 lab/codex_app_cli_hook_native_behavior_comparison.py --task-standard-posttooluse-gate0 --require-pass`.
- Output root: `.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/task_standard_posttooluse_gate0/`.
- Context path: `hookSpecificOutput.additionalContext` with
  `hookEventName=PostToolUse`; no `decision:block`, `continue:false`,
  PreToolUse denial, PermissionRequest policy, or Stop text was used.
- Context content named one product-visible unresolved item and a concrete next
  evidence move; it did not use internal labels, hidden verifier facts, or
  generic "verify more" advice.
- Root config hash stayed unchanged, no runtime snapshot loaded, hidden scoring
  remained scoring-only, and Sinkhorn/transport was not implemented.

## Boundary

Earned: structural product proof that PostToolUse can carry a specific
task-standard next-step correction on simulated product-visible mismatch.

Not earned: live behavior lift, broad Cortex lift, output-quality lift,
truth-gap lift, live comparison approval, PreToolUse motor inhibition,
Sinkhorn/transport, Codex App parity, or shipping promotion.

## Next Move

Queue `codex-app-cli-posttooluse-task-standard-calibration-decision`. The next
decision should inspect the Gate 0 evidence and choose between a narrow live
PostToolUse actuator probe, more clean-control calibration, or architecture
revision. Do not jump directly to a three-arm behavior comparison.
