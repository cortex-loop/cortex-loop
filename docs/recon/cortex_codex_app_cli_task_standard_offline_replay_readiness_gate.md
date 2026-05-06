# Codex App/CLI Task-Standard Offline Replay Readiness Gate

Surface: product + lab proof

## Summary

The no-spend readiness gate passed. The gate reads the prior three-arm live run
at `.cortex/live_validation/openai/codex_app_cli_hook_native_behavior_comparison/task_standard_three_arm_live_20260506T001502Z/`
and classifies the available artifacts honestly: exact raw hook-payload replay
is not available from the old run, but transcript-derived replay from
`codex_stdout.jsonl`, summarized hook trajectory, and diagnostics is available.

This seam also replaced binary task-standard token overlap with deterministic
scored lexical matching in SRE. The matcher is dependency-free, weights
product-specific tokens first, applies local frequency dampening, and keeps
transport/mass-conservation work deferred until pairwise scores prove
trustworthy.

## Evidence Earned

- `python3 lab/codex_app_cli_hook_native_behavior_comparison.py --task-standard-offline-readiness-gate --require-pass`
  passed.
- `clean_verified_work__active_task_standard__clean_control__001` replayed as
  `would_block=false`.
- `simple_success_file__active_task_standard__clean_control__004` replayed as
  `would_block=false`.
- Known task-standard exactness mismatch rows remain blockable under transcript-
  derived replay.
- Hidden scoring remains scoring-only.
- Active-vs-silent actuator opportunity is present on three paired exactness
  rows.
- Scored lexical precision passed: product-specific path/number/command matches
  align, compound cross-concept overlap stays below threshold, and generic
  unrelated checks do not over-credit unrelated standard items.
- Hygiene checks passed: no task-standard silent arm uses broad model-visible
  block suppression, no host-specific SRE policy was added, and no Sinkhorn or
  embedding/LLM judge was introduced.

## Boundary

This earns offline readiness only. It does not earn behavior lift, output-
quality lift, Codex App parity from Codex CLI evidence, shipping promotion,
truth-gap stability, exact raw hook-payload replay, or permission to tune
signed task-standard text, Stop text, selector thresholds, fixtures, scoring,
hook wiring, or hidden-verifier boundaries.

## Next Decision

The next train may be the pinned task-standard behavior comparison rerun, but
only with explicit current-turn live approval. The rerun remains under the
existing no-tuning rules: no text edits, no selector/threshold edits, no fixture
repair after seeing results, hidden scoring remains scoring-only, and behavior
lift may be claimed only if active Cortex beats both raw and silent controls
with captured-standard and block/continuation evidence and no clean-control
overblock.
