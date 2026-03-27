# CORTEX_V2_LIVE_VALIDATION_PROGRAM_0

Date: 2026-03-27
Status: active live-validation program brief for the first multi-host subscribed-host audit pass

## Purpose

This document records the first bounded live-validation train over the accepted reference, OpenAI, Gemini, and Claude runtime/product shells.

The train compares:

- direct terminal-backed provider baselines,
- the accepted loopback-service plus host-control product path,
- and the resulting evidence needed to judge whether the lifecycle-first approach is paying off on real hosts.

This program does not override:

- `docs/CORTEX_V2_CORE_2.md`
- `docs/CORTEX_V2_SRE_2.md`
- `docs/CORTEX_V2_AUX_2.md`
- `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
- `docs/CORTEX_V2_PHASE_GATES_2.md`
- `docs/CORTEX_V2_MATH_TO_CODE_CORRESPONDENCE.md`

## Accepted parent and baseline normalization

Accepted parent for this train:

- branch: `codex/l1-live-validation`
- commit: `8eb7f08`

This is the refreshed-model line that carries:

- Claude pinned to `claude-sonnet-4-6`,
- Gemini pinned to `gemini-2.5-pro`,
- and OpenAI pinned to `gpt-5.4`.

## Locked scope

This train remains:

- evidence-first
- host-specific
- runtime-product-path honest
- and bounded to direct provider baseline capture, loopback-service host-control capture, and comparison

This train does **not** authorize:

- CLI-backed transport substitution for the accepted A4 / G4 / O4 lanes
- tools or tool-result submission
- thinking blocks
- multimodal widening
- runtime AUX activation
- support-memory runtime
- mediation implementation
- generic runtime/service abstraction

## Current L1 surfaces

- machine-readable preflight report: `docs/live_validation/preflight_report.json`
- direct provider baseline summaries:
  - `docs/live_validation/claude/provider_baseline_runs.json`
  - `docs/live_validation/gemini/provider_baseline_runs.json`
  - `docs/live_validation/openai/provider_baseline_runs.json`
- Cortex live-path summaries:
  - `docs/live_validation/claude/cortex_live_runs.json`
  - `docs/live_validation/gemini/cortex_live_runs.json`
  - `docs/live_validation/openai/cortex_live_runs.json`
- comparison and verdict:
  - `docs/live_validation/comparators/live_validation_comparison.json`
  - `docs/live_validation/comparators/live_validation_comparison.md`
  - `docs/CORTEX_V2_LIVE_VALIDATION_VERDICT_0.md`

## Initial evidence after the first pass

The first L1 pass is real and machine-backed, but it is blocked:

- the provider toolchain is updated locally
- the direct provider baseline path is real for all three providers
- the Cortex loopback-service plus host-control path is real for all three providers
- no provider completed a successful live Cortex host-control run on this pass

Observed blocker classes:

- Claude direct terminal baseline: `auth_expired`
- Gemini direct terminal baseline: `capacity_exhausted`
- OpenAI direct baseline: `auth_missing`
- Claude / Gemini / OpenAI Cortex live product paths: `auth_missing`

## Closeout law

`L1` is only honestly closed when all are true:

- at least one successful direct provider baseline run exists for Claude, Gemini, and OpenAI
- at least one successful live Cortex host-control run exists for Claude, Gemini, and OpenAI
- at least one continuity/export-import live scenario completes successfully per provider
- the comparison and verdict are regenerated after those successful runs
- and the `L1`-`L4` phase-gate rows are updated truthfully

Until then, this train remains partial or blocked rather than silently “close enough.”
