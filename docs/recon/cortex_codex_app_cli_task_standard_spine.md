# Cortex Codex App/CLI Task Standard Spine

Surface: product / lab proof

Probe date: 2026-05-05

Verdict: task_standard_spine_structural; live model-standard formation and behavior lift remain unearned.

## Standard

Cortex should help the model form and preserve a task-specific standard for excellent work, not merely notice that generic verification happened. The executive object for this seam is the visible task, the model's own compact work standard, the likely misses it names, and the closure evidence it says would make handoff honest.

## What Changed

- Added `cortex/sre/task_standard.py` with `TaskStandardSpine`, `TaskStandardItem`, `TaskStandardEvidence`, and the gated standard-formation text. Product activation still requires explicit final text signoff.
- Extended `cortex/hosts/openai/codex_app_cli_hook_coordinator.py` so `UserPromptSubmit` initializes task-standard state, `PostToolUse` classifies evidence as `claim_aligned`, `standard_aligned`, `generic_check`, or `unrelated_activity`, and `Stop` can keep verification pressure open when closure claims outrun the stored standard/evidence relation.
- Added an opt-in Codex hook-client flag, `--enable-task-standard-text`, so the new model-visible text is structurally gated and the silent-only arm can suppress it with `--disable-model-visible-blocks`.
- Kept existing Stop identity-continuous texts unchanged.

## Gated Model-Visible Text

Only this structurally gated text was added, behind explicit activation flags:

```text
Before work starts, name the standard this work has to meet in three compact lines: Work standard, Likely misses, Closure evidence. What is it really trying to become, what would make it strong, what would be embarrassing to miss, and what evidence would make closure honest. Work against that standard.
```

No other new Cortex model-visible text was added, and no live activation is
earned without fresh explicit text signoff.

## Replay Evidence

`python3 lab/codex_app_cli_task_standard_spine.py --require-pass` replayed the existing Astro three-arm hook-native traces through the new spine.

- hidden-failing traces caught as open: 3
- hidden-passing traces with overblock risk: 2
- hidden verifier read by the spine: false
- verdict: `standard_spine_overblocks_without_real_model_standard`

The replay used existing traces that predate model-visible standard formation, so it is not evidence that the product text works or fails. It shows the new spine does not smuggle hidden verifier facts and that generic visible checks remain too weak without a real model-derived standard and aligned evidence.

## Evidence Earned

- Structural product evidence that task-standard state survives coordinator persistence and affects Stop closure pressure.
- Product tests proving generic build/readback activity alone does not pay down standard items once a standard exists.
- Product tests proving aligned evidence can pay down matching standard items.
- Hook-client tests proving the gated text is opt-in and silent arms suppress it.
- Lab replay evidence that hidden verifier files and output remain outside Cortex perception.

## Not Earned

- No live proof that Codex App/CLI accepts the `UserPromptSubmit` context payload as model-visible input.
- No live proof that the model produces the three-line standard block before work.
- No behavior-lift claim over raw Codex or silent-only Cortex.
- No Astro-specific rule, hidden verifier perception, task-identity trigger, or PreToolUse motor inhibition.

## Next Decision

Queue `codex-app-cli-task-standard-live-probe` only after explicit final text
signoff: prove the signed-off UserPromptSubmit context reaches a real Codex CLI
model turn, that the model forms the compact standard, and that Cortex stores it
from product-visible lifecycle evidence. If live context delivery or standard
capture fails, remediate the actuator before any behavior comparison.
