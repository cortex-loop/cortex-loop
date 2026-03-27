# CORTEX_V2_EXECUTIVE_LIVE_OUTCOME_PROGRAM_0

Date: 2026-03-27
Status: active runtime-program brief for the first explicit executive live-outcome allocation slice

## Purpose

This document opens the next explicit runtime/product program after accepted `O4`.

The chosen next move is:

- one explicit executive allocation slice over already-landed runtime shells,
- one explicit `Q_t^{online}` / `Q_t^{alloc}`-style diagnostic projection,
- one fixed current-scope law where `Q_t^{mem}=0.0`, `alpha_t=1.0`, and `Q_t^{alloc}=Q_t^{online}`,
- one nested `control_ledger.allocation_diagnostics` payload across reference and OpenAI runtime surfaces,
- and one candidate K3 closeout that keeps K2 truth stable while making executive allocation auditable.

This document does not override:

- `docs/CORTEX_V2_CORE_2.md`
- `docs/CORTEX_V2_SRE_2.md`
- `docs/CORTEX_V2_AUX_2.md`
- `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
- `docs/CORTEX_V2_REFERENCE_FEEDBACK_PROGRAM_1.md`
- `docs/CORTEX_V2_OPENAI_RUNTIME_PROGRAM_0.md`
- `docs/CORTEX_V2_OPENAI_INGRESS_PROGRAM_0.md`
- `docs/CORTEX_V2_OPENAI_SERVICE_PROGRAM_0.md`
- `docs/CORTEX_V2_OPENAI_HOST_CONTROL_PROGRAM_0.md`

## Accepted parent and rationale

Accepted parent for this program on the current line:

- branch: `codex/k2-openai-host-control`
- commit: `9ed7dae`

Why this program opens now:

- accepted K2 makes one bounded outbound host-control lane real,
- the next lawful product-facing gap is explicit executive-loop computation over live runtime outcomes,
- the current runtime shells already carry realized-feedback history and bounded feedback-window summary,
- and the smallest truthful next move is explicit executive allocation diagnostics rather than support-memory runtime, mediation, or more host-control widening.

## Locked scope

This program remains:

- reference/OpenAI runtime only,
- packet-subordinate,
- live-outcome-conditioned,
- diagnostics-first,
- and current-scope fixed with `Q_t^{mem}=0.0` and `alpha_t=1.0`.

This program adds only:

- explicit `online_score`, `memory_score`, and `allocated_score` diagnostics on the allocation carriers
- explicit `alpha_t` on the scorecard
- nested `control_ledger.allocation_diagnostics`
- one explicit runtime-facing allocation decomposition over current lawful runtime-visible signals
- one repo-local executive-loop revalidation target

This program does **not** authorize:

- support-memory runtime
- mediation or `Q_t^{final}` experimentation
- Gemini runtime shell
- more host-control lanes
- tools or tool-result submission
- generic reward-learning doctrine
- runtime AUX activation
- offline consolidation
- mediation implementation
- or broader product claims beyond this explicit executive allocation slice

## Public runtime contract

No new top-level runtime records or endpoints are introduced in K3.

The existing public shells remain:

- `python3 -m cortex.runtime.reference_cli`
- `python3 -m cortex.runtime.openai_cli`
- `python3 -m cortex.runtime.openai_ingress_cli`
- `python3 -m cortex.runtime.openai_service`
- `POST /v1/actions/response-stream`

K3 adds one nested field to the existing `control_ledger` payload:

- `allocation_diagnostics`

`allocation_diagnostics` key order is locked to:

1. `alpha_t`
2. `activation_threshold`
3. `selected_delta_over_neutral`
4. `scores`

Each `scores` entry key order is locked to:

1. `family`
2. `online_score`
3. `memory_score`
4. `allocated_score`
5. `admissible`
6. `reason_tags`

K3 does not reorder any existing top-level runtime record fields or existing top-level `control_ledger` keys.

## Runtime law for this program

The K3 executive allocation slice may:

- refine the existing SRE allocation carriers,
- expose explicit `Q_t^{online}` / `Q_t^{alloc}` diagnostics over current lawful runtime-visible signals,
- thread already-landed realized-feedback and feedback-window influence into those diagnostics,
- and preserve the existing neutral-dominance hinge while making it auditable.

It may not:

- turn on support-memory runtime,
- widen into learned reward or generic RL doctrine,
- enable mediation or `Q_t^{final}` experimentation,
- introduce new host-control lanes,
- persist `allocation_diagnostics` into runtime artifacts,
- or weaken existing continuity or artifact truth boundaries.

## K3 live-outcome contract

For current scope:

- `memory_score = 0.0` for every family
- `alpha_t = 1.0`
- `allocated_score = online_score`

Live-outcome conditioning means:

- a clean success sequence keeps pressure low,
- repeated mismatch / enforcement / degradation raises stability and uncertainty-conditioned score pressure,
- and the resulting `selected_delta_over_neutral` may lawfully change `selected_family` through the existing neutral-dominance law.

## Program order

This program remains split into five bounded seams:

1. `K3A` program lock
2. `K3B` allocation carrier and decomposition update
3. `K3C` runtime/control-ledger projection update
4. `K3D` live-outcome conditioning proof
5. `K3E` re-audit and closeout

Every seam must end on a clean tree before the next opens.

## Acceptance gates

K3 is only honestly closed when all are true:

- explicit `online_score`, `memory_score`, and `allocated_score` diagnostics are real
- `memory_score=0.0`, `alpha_t=1.0`, and `allocated_score=online_score` hold for current scope
- nested `control_ledger.allocation_diagnostics` is real across the reference/OpenAI runtime projections
- live-outcome conditioning is proven through the already-landed feedback window
- allocation diagnostics are not promoted into stronger persisted truth
- targeted tests pass twice
- `make seam-preflight`, `make revalidate-executive-loop`, `make revalidate-openai-host-control`, `make test-smoke`, and `make verify` pass
- and the `R6` and `O5` phase-gate rows are updated truthfully

## Current K3 candidate state before closeout

On branch `codex/k3-executive-live-outcome` rooted at accepted K2 baseline `9ed7dae`:

- the allocation carriers now expose explicit `online_score`, `memory_score`, and `allocated_score`
- the scorecard now exposes `alpha_t`
- the reference/OpenAI control ledgers and runtime projections now expose nested `allocation_diagnostics`
- `Q_t^{mem}=0.0`, `alpha_t=1.0`, and `allocated_score=online_score` hold for current scope
- and `make revalidate-executive-loop` now exists as the repo-local K3 revalidation entry point

This is branch-local K3 implementation truth.
It does **not** by itself promote accepted baseline truth.
