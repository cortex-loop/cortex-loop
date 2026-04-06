# CORTEX_V2_LIVE_VALIDATION_PROGRAM_0

Date: 2026-04-07
Status: active live-validation program under the R1 two-lane truth reset

## Purpose

This document records the live-validation contract after the R1 reset.
The reset itself is already landed on local `main`; this program keeps later live-evidence interpretation aligned to that contract.

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
- the accepted current product scope on the canonical direct-API lane is now OpenAI-only
- the OpenAI direct-service lane is repeat-stably re-earned through three positive current-machine `canonical_anchor` cycles on the shared suite for:
  - `pass_minimal`
  - `truth_gap`
  - `restart_continuity`
- the Claude direct-service lane retains that same canonical suite implementation as future host-expansion plumbing, but it is intentionally outside the current product scope
- Gemini remains watchlist-only until its direct API lane is explicitly opened

## Closeout law

This program is only honestly closed when all are true:

- at least one host is re-earned on the canonical `service_api` lane through repeat-stable direct-API confirmation
- operator/CLI watchlist outputs are recorded truthfully but are not used as canonical runtime proof by themselves
- compare and verdict surfaces distinguish:
  - `execution_surface`
  - `evidence_role`
- gate and workstream summaries are updated truthfully to the reset contract

## Next lawful move

1. open the bounded `X1` OpenAI-only runtime-compression train on clean `main`
2. keep operator/CLI reruns as watchlist evidence and drift detection only
3. keep `claude` and `gemini` outside the current product scope until a later host-expansion train is intentionally opened
