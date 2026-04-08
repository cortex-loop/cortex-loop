# CORTEX_V2_EXECUTIVE_RESTORATION_NOTE

Date: 2026-04-08
Status: accepted executive-restoration note with the first verified-work restoration slice now landed partially

## Scope

This note records the accepted keep/cut/restore decision for Cortex v2 after the X1/X2 reduction train and the later larger-task exploratory runs.
It does not start implementation by itself.
It exists to keep the next bounded runtime/product seam aligned with the packet, the implementation plan, and the current product truth.

## Authority audited

- `docs/CORTEX_V2_CORE_2.md`
- `docs/CORTEX_V2_SRE_2.md`
- `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
- `docs/V1_CODE_PORT_DETERMINATION.md`
- `docs/CORTEX_V2_ACTIVE_WORKSTREAM.md`

## Current reading

The recent product simplification remains the right baseline:

- OpenAI-only accepted current product scope
- direct API as the canonical truth lane
- compact `openai_product_journal`
- one explicit current-line decision table
- compressed support/eval shell
- CLI and watchlist surfaces demoted to non-authoritative evidence

The local larger-task exploratory runs do not justify prompt shaping or a second large runtime subsystem.
They do justify one correction:

- Cortex currently behaves more like a verifier shell than a bounded larger-task executive because repairable external failures still live outside accepted runtime truth.

The accepted drift interpretation is therefore:

- too little runtime-native executive control
- not too much executive control
- and not a reason to restore the older heavy control residue

## Keep

- the OpenAI-only accepted current scope
- direct API as the canonical truth lane
- the compact `openai_product_journal`
- one explicit compact decision table on the current small-task path
- support/eval compression after X2
- CLI/watchlist as non-authoritative
- no prompt rewriting or hidden build briefs

## Cut

- benchmark-local executive control as a substitute for runtime control
- prompt shaping as a product direction
- one-shot larger-task assumptions as the only accepted runtime shape
- carrier blindness between diff and bounded full-file work
- any return to allocation diagnostics, feedback-window narration, or reference-soft-control residue on the accepted product path
- any new support doctrine pretending to be the product

## Restore

- runtime-native verification input
- one tiny active work contract for larger tasks:
  - writable surface
  - verifier
  - repair budget
- one bounded repair loop
- one failure taxonomy that actually steers repair, check, and stop
- inhibition of repeated failed moves
- tiny carrier selection by task shape
- one unified host-control family with neutral default behavior and bounded escalated repair behavior

## Decision basis

The next runtime/product seam should improve Cortex law first, then prove that law through host-specific wiring, not through an OpenAI-only patchwork.

That substrate should add only:

- optional work-contract activation
- runtime-native verification binding
- a bounded repair/inhibition gate
- tiny carrier selection

Then the OpenAI path should be the first host realization, followed immediately by cross-brain conformance checks on the strongest available Claude and Gemini surfaces.

This note does not authorize:

- prompt rewriting
- hidden implementation-preference prompts
- a second large task-specific subsystem
- broad support-ledger restoration
- or a rollback of the recent X1/X2 reduction train

## Progress on the accepted line

The first restoration slice is now partly landed on the accepted line:

- shared `WorkContract`, `VerificationOutcome`, and `choose_verified_work_followup()` now exist
- the shared verified-work runtime helpers now live in the neutral `cortex/runtime/verified_work_runtime.py` home instead of an OpenAI-shaped helper module
- the OpenAI host-control family now accepts an optional bounded `work_contract`
- external verification now updates runtime truth directly
- one bounded repair turn is now implemented on the verified-work path
- the default thin path remains unchanged when no `work_contract` is present

What is **not** yet earned:

- repeat-stable live lift for the verified-work path over one-shot behavior
- repeated-failure inhibition / NoGo promotion
- automatic carrier selection
- cross-host rollout beyond the first OpenAI realization

## Conformance reading under the current method

The active method now separates:

- `Cortex truth` — optional work contract, runtime-native verification as control truth, bounded repair
- `brain-wiring truth` — how OpenAI, Claude, and Gemini attach to that same law
- `conformance truth` — how faithfully each active surface realizes the law
- `shipping truth` — the current OpenAI-first product default

That means later work should not ask whether a second host is "deferred" in the abstract.
It should ask whether the same Cortex law is conformant, partial, divergent, unwired, or env-blocked on that host's strongest available native surface.

On the current bookmarks verified-work pack, the active reading is:

- OpenAI `service_api`: partial on the repeated corrected current runs because the bounded repair path still finishes `test_failed`
- Claude `operator_cli`: no longer divergent on truthful staged-workspace runs; two focused reruns passed on attempt `1`, while repeated full tri-brain reruns currently hit Anthropic `529 overloaded_error` before structured output and therefore count as `env_blocked`
- Gemini `operator_cli`: conformant on the corrected current line because staged workspace truth removes the earlier `read_file` miss and the repeated full reruns now pass the bookmarks pack

The current next decision is therefore `improve_shipping_default`, not `fix_wiring_only` and not `revise_cortex_law`, because no non-shipping divergent surface remains on the corrected current line and the main unresolved gap is still OpenAI `O4R` value lift.

## Next lawful move

If a later runtime/product seam is opened after this note, the next lawful move is:

1. keep the current thin path as the default when no work contract is present
2. recheck whether verified-work earns repeat-stable value on local larger-task reruns before widening shipping truth further
3. run the same contract pack across OpenAI, Claude, and Gemini on their strongest available native surfaces
4. revise Cortex law only if the same divergence repeats across brains; otherwise improve the remaining shipping-default gap first, reopening host wiring only if a non-shipping surface becomes truly divergent again
5. keep repeated-failure inhibition and carrier inference deferred until that value is earned
6. cut back rather than widen if the verified-work path keeps failing without value lift or improved conformance

This is the accepted north-light correction:

- keep Cortex small
- keep Cortex host-native
- keep Cortex neutral by default
- but restore one real bounded executive loop where larger-task work actually needs it
