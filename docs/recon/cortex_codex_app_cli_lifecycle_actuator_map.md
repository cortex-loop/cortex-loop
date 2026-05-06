# Codex App/CLI Lifecycle Actuator Map

Surface: product architecture + doctrine/status

Verdict: `map_landed`; implementation remains queued.

## Summary

This seam maps Codex App/CLI lifecycle events by actual product control before
building another actuator. The prior raw-vs-silent readout found one narrow
signal: `silent_task_standard` beat `raw_codex` on `task_standard_exactness`
evidence recovery in 5/5 paired trials. That signal justifies a PostToolUse
implementation seam constrained to exactness/evidence recovery, not a broad
behavior-lift claim and not another live comparison.

No runtime behavior, model-visible text, hook output, SRE law, scored matcher,
fixture, scoring rule, root hook, hidden-verifier boundary, live run, or
Sinkhorn/transport implementation changed.

## Actuator Map

- `SessionStart`: session/workspace context through additionalContext. It is
  useful for startup/resume context, not task-local correction.
- `UserPromptSubmit`: prospective task-set formation through additionalContext.
  This is the current signed task-standard context surface.
- `PreToolUse`: hard motor deny/block only. Do not design it as coaching text;
  additionalContext is not a supported model-context surface for this event.
- `PermissionRequest`: approval-bound route control through allow, deny, or
  no-decision. It is not a general model coaching surface.
- `PostToolUse`: strongest next implementation target because it can attach
  context after product-visible tool evidence and before the next model step.
- `Stop`: late closure continuation through block/reason. It remains useful
  for truthful closure, but it is too late to be the only active lever.

## Next Implementation Constraint

Queue `codex-app-cli-posttooluse-task-standard-next-step-correction`.

The implementation must be specific to product-visible mismatch and must obey
Cortex output law: no third-agent voice, no internal labels, no hidden verifier
facts, and no generic "verify more" advice. The first PostToolUse target is the
earned `task_standard_exactness` / `evidence_recovery` signal only.

PreToolUse motor inhibition remains later and deny-only. Any future PreToolUse
seam must treat clean-control denial as a high-severity overblock.

Sinkhorn/transport remains deferred until an actuator loop exists and evidence
allocation precision remains load-bearing.

## Forbidden Claims

This seam earns no runtime behavior change, no new live evidence, no broad
Cortex lift, no output-quality lift, no truth-gap lift, no PostToolUse behavior
proof, no PreToolUse motor-inhibition proof, no Sinkhorn implementation, no
Codex App parity, and no shipping promotion.
