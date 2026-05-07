# Codex App/CLI Raw vs Silent Artifact Readout Roadmap Update

Surface: lab proof + product architecture

## Summary

Before building PostToolUse or PreToolUse actuators, Cortex should mine the
existing three-arm task-standard live artifacts for the raw-vs-silent question.
This is a no-spend decision seam, not a new live probe: the prior run already
contains `raw_codex` and `silent_task_standard` rows on the same task families.

The question is narrow and load-bearing: does signed task-standard
context/perception produce any meaningful signal over raw Codex before active
Stop or future PostToolUse/PreToolUse intervention is considered.

## Required Readout

Read:

`.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/task_standard_three_arm_live_20260506T001502Z/`

Report raw-vs-silent wins, losses, and ties by family and primary axis:

- task-standard exactness,
- output-quality visible success / Astro hidden scoring,
- truth-gap false completion and baseline reproduction,
- clean controls,
- suppressed Stop rows,
- standard capture rows,
- and overblock risk.

The readout must separate hidden scoring from Cortex state and must not feed
hidden verifier output into product perception.

## Roadmap Decision

If silent shows no meaningful signal over raw, stop for architecture decision
before implementing PostToolUse. If silent has a narrow signal, feed only that
signal into the lifecycle actuator map and PostToolUse specificity rules. Do
not generalize a narrow raw-vs-silent result into broad Cortex behavior lift.

After this readout, the queued product architecture seam remains the Codex
App/CLI lifecycle actuator map:

- SessionStart: session/workspace context only.
- UserPromptSubmit: prospective task-set formation.
- PreToolUse: hard motor deny/block only, not coaching text.
- PermissionRequest: approval-bound route control.
- PostToolUse: strongest near-term next-step correction surface.
- Stop: late closure continuation.

## Forbidden Claims

This roadmap update earns no runtime behavior change, no new live evidence, no
PostToolUse actuator, no PreToolUse motor inhibition, no Sinkhorn
implementation, no model-visible text approval, and no broad behavior-lift
claim.
