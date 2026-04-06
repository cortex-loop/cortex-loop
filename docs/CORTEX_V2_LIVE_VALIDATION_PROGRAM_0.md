# CORTEX_V2_LIVE_VALIDATION_PROGRAM_0

Date: 2026-04-06
Status: active live-validation program under the R1 two-lane truth reset

## Purpose

This document records the live-validation contract after the R1 reset.

The live program now has two explicit evidence lanes:

- `service_api`
  - direct provider/API-backed runtime surface
  - canonical runtime truth
- `operator_cli`
  - signed-in headless provider CLI surface
  - watchlist and exploratory-comparison evidence

## Accepted parent

Accepted baseline for this train on the current line:

- branch: `main`
- line: clean synced `main` line recorded in `docs/CORTEX_V2_ACTIVE_WORKSTREAM.md`

## Environment rules

- live artifacts are local-only under `.cortex/live_validation/`
- repo-tracked docs carry only summaries and verdicts
- signed-in operator evidence remains useful, but it is no longer the primary runtime truth lane
- service/API truth is canonical once auth and spend policy are satisfied
- do not use CLI fallback to fake canonical service proof

## Shared coding harness

Project:

- `tests/fixtures/live_validation/project_template/`

Shared scenarios:

- `pass_minimal`
- `restart_continuity`
- `truth_gap`

Current reality:

- the operator/watchlist lane already uses the shared coding harness
- the current direct-service lane on this machine remains auth-blocked and still only exposes a smaller smoke/continuity proof surface
- the first canonical three-scenario API truth anchor is therefore a later bounded seam on a capable machine

## Closeout law

This program is only honestly closed when all are true:

- at least one host is re-earned on the canonical `service_api` lane through repeat-stable direct-API confirmation
- operator/CLI watchlist outputs are recorded truthfully but are not used as canonical runtime proof by themselves
- compare and verdict surfaces distinguish:
  - `execution_surface`
  - `evidence_role`
- gate and workstream summaries are updated truthfully to the reset contract
