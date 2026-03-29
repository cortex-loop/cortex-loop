# CORTEX_V2_COMPUTED_EXECUTIVE_LOOP_PROGRAM_0

Date: 2026-03-29
Status: active runtime-program brief for the first bounded computed executive loop on proven reference/OpenAI lanes

## Purpose

This document opens the next explicit runtime/product program after the accepted diagnostics-first executive allocation slice.

The chosen next move is:

- one bounded computed executive loop over already-proven reference and OpenAI runtime lanes,
- one explicit unfreeze of `alpha_t` and `allocated_score` over current runtime-visible pressure,
- one current-scope law where `Q_t^{mem}=0.0`,
- one unchanged public projection shape through nested `control_ledger.allocation_diagnostics`,
- and one candidate closeout that keeps `R6/O5` truthful as the diagnostics-first ancestor slice.

This document does not authorize:

- support-memory runtime,
- mediation or `Q_t^{final}` experimentation,
- service/auth work,
- new host-control lanes,
- Claude/Gemini phase closure,
- offline consolidation,
- runtime AUX activation,
- or broader host rollout.

## Accepted parent and rationale

Accepted parent for this program on the current line:

- branch: `main`
- commit: `a369874`

Why this program opens now:

- the first explicit executive allocation slice is already real,
- the strongest proven runtime/product lanes are still reference and OpenAI,
- the next lawful gap is making the allocation loop materially computed rather than diagnostics-first,
- and the smallest truthful move is to unfreeze online allocation semantics before any support-memory or mediation work.

## Locked scope

This program remains:

- reference/OpenAI only for acceptance truth,
- online-signals-only,
- packet-subordinate,
- and memory-off for current scope with `Q_t^{mem}=0.0`.

This program adds only:

- computed `alpha_t` over runtime-visible pressure,
- computed `allocated_score` distinct from `online_score`,
- neutral-dominance selection over `allocated_score`,
- and coherent reference/OpenAI runtime projections of the existing nested `allocation_diagnostics` payload.

This program keeps fixed:

- `Q_t^{mem}=0.0`,
- the current budget-band activation-threshold law,
- the existing public CLI and HTTP shells,
- and the existing top-level runtime record shapes.

## Public runtime contract

No new public shells are introduced.

The public surfaces remain:

- `python3 -m cortex.runtime.reference_cli`
- `python3 -m cortex.runtime.openai_cli`
- `python3 -m cortex.runtime.openai_ingress_cli`
- `python3 -m cortex.runtime.openai_service`
- `POST /v1/actions/response-stream`

No new top-level runtime fields or top-level `control_ledger` keys are introduced.

The existing nested `control_ledger.allocation_diagnostics` payload remains the public surface.

Within that payload for current scope:

- `memory_score = 0.0`
- `alpha_t` is computed, not fixed
- `allocated_score` may differ from `online_score`

## Runtime law for this program

Current-scope allocation law:

- `allocated_score = alpha_t * online_score`
- `memory_score = 0.0`
- `Q_t^{mem}` remains runtime-off

Current-scope `alpha_t` law:

- `0.65` when brake is `latched`
- `0.75` when brake is `guarded` and visible pressure is present
- `0.85` when visible pressure is present without `latched/guarded`
- `1.0` otherwise

Visible pressure means any of:

- non-empty `host_friction_tags`
- non-empty `contradiction_spike_flags`
- max classwise uncertainty `>= 0.55`

This program may not:

- introduce memory contribution,
- add hidden weighting state,
- widen threshold law,
- or promote `allocation_diagnostics` into persisted continuity/artifact truth.

## Program order

This program remains split into five bounded seams:

1. `K4A` program lock and correspondence update
2. `K4B` computed allocation carrier/scoring update
3. `K4C` reference runtime projection update
4. `K4D` OpenAI proven-lane projection update
5. `K4E` re-audit and closeout

Every seam must end on a clean tree before the next opens.

## Acceptance gates

K4 is only honestly closed when all are true:

- `alpha_t` is not fixed to `1.0` on pressured reference/OpenAI traces
- `memory_score` stays `0.0`
- `allocated_score` can differ from `online_score`
- neutral-dominance selection runs on allocated score semantics
- no new top-level runtime record fields or endpoints exist
- `allocation_diagnostics` remains non-persisted stronger-than-artifact truth
- targeted tests pass twice
- `make revalidate-executive-loop`, `make test-smoke`, and `make verify` pass
- `R7` and `O6` are updated truthfully
- `R6/O5` remain the accepted diagnostics-first ancestor slice

## Current K4 candidate state before closeout

On the current K4 candidate line opened from accepted baseline `a369874`:

- `alpha_t` is computed from runtime-visible pressure rather than fixed
- `allocated_score` is the actual selection score while `online_score` remains diagnostic
- reference/OpenAI runtime projections preserve the same public shape while surfacing the stronger computed semantics
- Claude/Gemini deterministic runtime projections remain compatible with the new scorer semantics but are not promoted to new closure truth
