# CORTEX_V2_OPERATOR_DIRECTIONALITY_PROGRAM_0

Date: 2026-04-06
Status: accepted watchlist-evaluation brief for raw-vs-Cortex operator comparison

## Purpose

This document records the role of the paired raw-vs-Cortex operator harness after the R1 reset.

The operator directionality audit remains:

- evaluation-only
- host-watchlist evidence
- packaging/confound detection
- falsification infrastructure for wrapper burden and comparison contamination

It is no longer a canonical runtime-truth carrier.

## Locked watchlist contract

This audit is:

- operator-only on the current machine
- raw-host vs Cortex-operator
- same host surface for both variants
- same scenario
- same starting workspace
- contradiction-preserving

Variants:

- `raw_host`
- `cortex_operator`

Execution classification:

- `execution_surface = headless_cli`
- `evidence_role = watchlist`

## Truth law after the reset

- operator-lane positives do not by themselves promote accepted runtime truth
- operator-lane negatives do not by themselves overturn a later re-earned API truth lane unless they expose a direct contradiction in the canonical runtime path
- blocked or contaminated pairs remain useful watchlist evidence, not product truth

## Gemini falsification tooling

The Gemini operator harness may use:

- `--cortex-execution-flavor auto`
- `--cortex-execution-flavor minimal`
- `--cortex-execution-flavor wrapped`

These are harness-only falsification controls.
They do not authorize product default changes by themselves.

## Next lawful move

- keep operator directionality as watchlist evidence
- use it to detect packaging contamination, host-default-path drift, wrapper burden, and local-vs-accepted watchlist drift
- move canonical runtime claims to the service/API lane described in `docs/CORTEX_V2_LIVE_SERVICE_PROOF_0.md`
