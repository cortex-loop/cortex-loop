# Cortex Codex App/CLI Astro Three-Arm Fixture Refresh

Surface: product / lab proof

Probe date: 2026-05-05

Verdict: mixed_signal; no Cortex speech lift earned.

## Summary

This seam repaired the Astro output-quality comparison fixture so hidden
scoring is genuinely hidden from the subject model, then reran the product
comparison across three arms:

- `raw_codex`: no subject `.codex/config.toml`, no Cortex hooks, no Cortex
  state.
- `silent_only`: product lifecycle hooks capture state, but model-visible Stop
  blocks are disabled.
- `hook_native_cortex`: the same lifecycle hooks and state path, with Stop
  blocks enabled.

The important result is negative for Cortex speech: no trial in any arm emitted
model-visible Cortex text. The fully enabled arm therefore did not earn
intervention lift, even when it matched raw on hidden quality.

```text
gate0: passed
live_run: .cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/astro_three_arm_live_20260505T033207Z
model: gpt-5.3-codex
verdict: mixed_signal
raw_codex: 2/5 hidden pass, 4/5 objective pass, 0 blocks
silent_only: 1/5 hidden pass, 5/5 objective pass, 0 blocks
hook_native_cortex: 2/5 hidden pass, 5/5 objective pass, 0 blocks
hidden_verifier_probe_attempts: 0
subject_verifier_only_present_after_count: 0
timeouts: 0
root_config_unchanged: true
```

## Fixture Repair

The subject workspace now excludes verifier-only paths before the model sees
the project. For `astro_docs_site_v1`, this removes
`scripts/test-hidden.mjs` from the subject workspace.

The subject `package.json` also strips the hidden npm script, so the model no
longer sees or runs `npm run test:hidden` from visible project metadata. Hidden
scoring happens only after the model turn, in a separate evaluator workspace
that overlays verifier-only files back from the fixture template.

The raw arm now runs without a subject `.codex/config.toml`; the silent and
full arms use isolated product hook configs. All arms share the same visible
prompt hash, model, and sanitized subject manifest. Per-trial dependencies are
writable in the subject workspace, so read-only `node_modules` symlinks are not
a hidden confound.

## Run

Gate 0 command:

```bash
python3 lab/codex_app_cli_hook_native_behavior_comparison.py \
  --astro-three-arm-gate0 \
  --require-pass
```

Live command:

```bash
CORTEX_CODEX_APP_CLI_ASTRO_THREE_ARM_APPROVED=approved \
python3 lab/codex_app_cli_hook_native_behavior_comparison.py \
  --astro-three-arm-live \
  --astro-three-arm-trials 5
```

Gate 0 artifacts:

```text
.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/astro_three_arm_gate0/gate0_report.json
```

Live artifacts:

```text
.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/astro_three_arm_live_20260505T033207Z/summary.json
.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/astro_three_arm_live_20260505T033207Z/trajectory.jsonl
```

An earlier live attempt under
`.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/astro_three_arm_live_20260504T215848Z`
crashed on the fifteenth trial because raw `codex exec` timed out and the
harness did not persist timeout rows. The harness was repaired so future
timeouts become scoped-negative trial rows with stdout/stderr artifacts instead
of dropping the matrix.

## What This Proved

- The Astro subject workspace no longer exposes verifier-only files or the
  hidden npm script to the model.
- Hidden verifier output remains scoring-only: it is produced in the evaluator
  workspace after the model turn and is not fed into Cortex hooks, prompts,
  runtime state, or model-visible text.
- Raw, silent-only, and fully enabled arms now run against the same visible
  prompt, model, and sanitized subject seed.
- The raw arm has no Cortex hook config or Cortex state.
- Silent and full arms produce lifecycle hook rows without runtime snapshots.
- The live run completed all 15 planned trials without timeout, hidden-verifier
  probing, subject verifier leakage, or root `.codex/config.toml` drift.

## What This Did Not Prove

- No behavior lift is claimed. `hook_native_cortex` did not beat both raw and
  silent on hidden quality with actual Cortex intervention evidence.
- No Cortex speech lift is claimed. `hook_native_cortex` emitted 0 Stop blocks
  and 0 rendered texts across 5 Astro trials.
- No hidden-quality perception is claimed. The hidden evaluator found failures,
  but hidden verifier facts remained scoring-only and never became product
  perception.
- No architecture failure is claimed. The Astro task is noisy under the current
  model and hook lane: raw and full both passed hidden quality 2/5, while
  silent passed 1/5.

## Interpretation

The refreshed fixture answers the immediate concern: the earlier Astro result
was contaminated because subject workspaces exposed hidden verifier machinery.
That leak is fixed.

The rerun also shows that this Astro family does not currently provide clean
evidence that Cortex improves output quality. Fully enabled Cortex matched raw
on hidden quality and did not use the model-visible Stop path at all. Silent
perception lagged by one hidden pass, but that is not evidence for Cortex
speech because the full arm's advantage over silent arrived with zero block
rows and zero rendered text.

The honest next move is a perception/evaluation decision before another live
lift claim: either deepen product-visible perception for output-quality gaps,
choose a cleaner task family whose baseline failure reproduces without hidden
leakage, or decide that this hidden-quality class is outside the current
Stop-only closure-inhibition substrate.
