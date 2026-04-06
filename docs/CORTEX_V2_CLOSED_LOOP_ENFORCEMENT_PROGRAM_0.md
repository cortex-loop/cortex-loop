# CORTEX_V2_CLOSED_LOOP_ENFORCEMENT_PROGRAM_0

Date: 2026-03-29
Status: accepted historical/reference runtime-program brief for the bounded closed-loop feedback and enforcement train on proven reference/OpenAI lanes

After accepted X1, this document remains historical/reference evidence only.
It is not the accepted OpenAI-only product runtime.

## Purpose

This document records the next bounded runtime/product train after accepted `K4`.

The chosen next move is:

- one bounded feedback-conditioned intervention-threshold law,
- one bounded enforcement-aware realized control loop,
- one closeout that keeps the proven reference/OpenAI line coherent as one accepted K train,
- and one explicit stop before support-memory runtime, mediation, service/auth work, or broader host rollout.

This document does not override:

- `docs/CORTEX_V2_CORE_2.md`
- `docs/CORTEX_V2_SRE_2.md`
- `docs/CORTEX_V2_AUX_2.md`
- `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
- `docs/CORTEX_V2_EXECUTIVE_LIVE_OUTCOME_PROGRAM_0.md`
- `docs/CORTEX_V2_COMPUTED_EXECUTIVE_LOOP_PROGRAM_0.md`

## Accepted parent and rationale

Accepted parent for this train on the current line:

- branch: `main`
- commit: `feacbf5`

Why this train opens now:

- accepted `K4` already makes `alpha_t` and `allocated_score` materially computed on the proven reference/OpenAI lanes,
- the strongest remaining honest gap in that same line is not memory or mediation but bounded feedback-conditioned intervention and realization,
- and the smallest truthful next move is to unfreeze threshold law and strengthen enforcement-aware realized control without widening the public shells.

## Locked scope

This train remains:

- reference/OpenAI only for acceptance truth,
- packet-subordinate,
- runtime-visible and feedback-conditioned only,
- and memory-off for current scope with `Q_t^{mem}=0.0`.

This train adds only:

- a computed `activation_threshold` over current visible pressure and bounded prior-feedback pressure,
- explicit `feedback_pressure_tags` in the internal control-allocation view,
- bounded guarded-feedback enforcement in runtime realization,
- and coherent reference/OpenAI projection of the stronger law through the existing nested `control_ledger.allocation_diagnostics` surface.

This train does **not** authorize:

- support-memory runtime,
- mediation or `Q_t^{final}` experimentation,
- service/auth work,
- new host-control lanes,
- Gemini/Claude closure claims,
- vigor scaling,
- offline consolidation,
- runtime AUX activation,
- or broader host rollout.

## Public runtime contract

No new public shells are introduced.

The public surfaces remain:

- `python3 -m cortex.runtime.reference_cli`
- `python3 -m cortex.runtime.openai_cli`
- `python3 -m cortex.runtime.openai_ingress_cli`
- `python3 -m cortex.runtime.openai_service`
- `POST /v1/actions/response-stream`

No new top-level runtime fields or top-level `control_ledger` keys are introduced.

The existing nested `control_ledger.allocation_diagnostics` payload remains the public surface for executive-loop diagnostics.

Within that payload on the accepted K-train line:

- `Q_t^{mem}=0.0`
- `alpha_t` remains computed
- `allocated_score` may differ from `online_score`
- `activation_threshold` may differ from budget-band baseline because it is now feedback-conditioned

Outside that payload:

- selected-family truth remains explicit,
- realized-family truth remains explicit,
- lawful commitment truth remains explicit,
- and enforcement warnings remain explicit when realization differs from selection.

## Runtime law for this train

Accepted K-train allocation law:

- `allocated_score = alpha_t * online_score`
- `memory_score = 0.0`
- `Q_t^{mem}` remains runtime-off

Accepted K-train threshold law:

- start from the current budget-band baseline:
  - `low = 0.35`
  - `medium = 0.25`
  - `high = 0.20`
- add `+0.10` if brake is `latched`
- else add `+0.05` if brake is `guarded`
- add `+0.05` if current visible pressure is present
- add `+0.05` if bounded prior-feedback pressure is present
- clamp to `0.20 .. 0.45`

Current visible pressure for this train means:

- non-empty `host_friction_tags`,
- current contradiction spikes that are not merely prior-feedback carryover,
- or non-goal classwise uncertainty `>= 0.55`

Prior-feedback pressure for this train is bounded and explicit:

- `feedback:rejection-pressure`
- `feedback:override-pressure`
- `feedback:latched-history`
- `feedback:degradation-pressure`

Accepted K-train enforcement law:

- latched-brake enforcement remains explicit and conservative,
- guarded-feedback enforcement may conservatively realize `check` or `neutral` when selected non-neutral control is still too risky after bounded feedback pressure,
- selected-family truth, realized-family truth, and lawful commitment truth must remain explicit,
- and runtime realization may not silently erase enforcement warnings or commitment status.

## Program order

This train remained split into three bounded program stages:

1. `K5` feedback-conditioned threshold law
2. `K6` bounded enforcement-aware realized control loop
3. `K7` train closeout and truth sync

## Acceptance gates

The K train is only honestly closed when all are true:

- `alpha_t` remains bounded and computed from runtime-visible pressure
- `Q_t^{mem}=0.0`
- `allocated_score` can differ from `online_score`
- `activation_threshold` is no longer fixed to budget-band baseline alone
- threshold pressure is sourced only from current visible pressure plus bounded prior-feedback pressure
- guarded/latched enforcement-aware realized control is explicit and bounded
- selected-family truth, realized-family truth, and lawful commitment truth remain explicit
- no new top-level runtime record fields or endpoints exist
- `allocation_diagnostics` remains non-persisted stronger-than-artifact truth
- `make revalidate-executive-loop`, `make test-smoke`, and `make verify` pass
- `R8`, `O7`, `R9`, and `O8` are updated truthfully
- `R4/R5/R7/O6` remain truthful ancestor slices

## Current accepted state after K-train closeout

On the accepted K-train closeout line opened from parent `feacbf5`:

- `alpha_t` remains computed from runtime-visible pressure rather than fixed
- `activation_threshold` is now feedback-conditioned over current visible pressure and bounded prior-feedback pressure
- `feedback_pressure_tags` are now explicit inside the internal control-allocation view
- reference/OpenAI runtime projections preserve the same public shape while surfacing the stronger threshold law through existing nested diagnostics
- guarded-feedback and latched-brake enforcement now preserve selected-family truth, realized-family truth, lawful commitment truth, and explicit warning truth simultaneously
- Gemini/Claude deterministic runtime projections remain compatible with the stronger scorer/realization semantics but are not promoted to new closure truth

## Current standing after X1

- `R8` / `O7` / `R9` / `O8` remain landed historical/reference evidence for the older allocation-heavy OpenAI line,
- the accepted OpenAI-only product runtime no longer carries those enforcement/threshold projections as product truth,
- and this document now serves as historical/reference context only.
