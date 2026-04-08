# CORTEX_V2_EXECUTIVE_RESTORATION_NOTE

Date: 2026-04-08
Status: accepted executive-restoration note with the first verified-work restoration slice landed and third-pack breadth now re-earned on the current review line

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

The first restoration slice is now landed on the accepted OpenAI realization:

- shared `WorkContract`, `VerificationOutcome`, and `choose_verified_work_followup()` now exist
- the shared verified-work runtime helpers now live in the neutral `cortex/runtime/verified_work_runtime.py` home instead of an OpenAI-shaped helper module
- the OpenAI host-control family now accepts an optional bounded `work_contract`
- the OpenAI verified-work path now attaches one bounded read-only workspace context bundle over the current writable-file contents plus the bookmarks contract tests
- external verification now updates runtime truth directly
- one bounded repair turn is now implemented on the verified-work path
- the default thin path remains unchanged when no `work_contract` is present
- repeated targeted local OpenAI reruns on the bookmarks pack now pass on the shipping-default lane

What is **not** yet earned:

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

- OpenAI `service_api`: conformant on three repeated targeted current reruns because bounded read-only workspace context now exposes the writable-file and test contract and the shipping-default lane passes on attempt `1`
- Claude `operator_cli`: no longer divergent on truthful staged-workspace runs; two focused reruns passed on attempt `1`, while repeated full tri-brain reruns currently hit Anthropic `529 overloaded_error` before structured output and therefore count as `env_blocked`
- Gemini `operator_cli`: conformant on the corrected current line because staged workspace truth removes the earlier `read_file` miss and the repeated full reruns now pass the bookmarks pack

On the accepted normalize-port verified-work breadth pack, the current reading is:

- OpenAI `service_api`: conformant on repeated targeted reruns after one localized verifier-install correction restored the bounded workspace test environment
- Claude `operator_cli`: conformant on the explicit tri-brain guardrail rerun after one lawful repair
- Gemini `operator_cli`: conformant on the explicit tri-brain guardrail rerun

On the current feature-flags verified-work breadth pack, the active review-branch reading is:

- OpenAI `service_api`: conformant on repeated targeted reruns without regressing the accepted bookmarks or normalize-port packs
- Claude `operator_cli`: conformant on the explicit tri-brain guardrail rerun
- Gemini `operator_cli`: conformant on the explicit tri-brain guardrail rerun
- bookmarks remains the accepted `CT2` anchor pack and `summary.latest` remains bookmarks-only while the third pack stays explicit breadth evidence

The current next decision for the shipping-default lane is therefore `promote`, not `improve_shipping_default`, because the OpenAI `O4R` gap is now closed on repeated targeted local reruns and no non-shipping divergent surface remains on the corrected current line.

## Next lawful move

If a later runtime/product seam is opened after this note, the next lawful move is:

1. keep the current thin path as the default when no work contract is present
2. keep `O4R` stable on repeated local reruns rather than reopening the law or the shipping-default wiring by habit
3. prove the middle-weight third verified-work breadth pack before treating two-pack success as a general Cortex win
4. run the same contract pack across OpenAI, Claude, and Gemini on their strongest available native surfaces whenever a later seam changes Cortex law or touches non-shipping wiring
5. revise Cortex law only if the same divergence repeats across brains; otherwise reopen wiring only on the specific drifting brain/surface
6. keep repeated-failure inhibition and carrier inference deferred until new evidence earns them
7. open any later shipping-truth widening beyond OpenAI only through an explicit separate host shipping train

This is the accepted north-light correction:

- keep Cortex small
- keep Cortex host-native
- keep Cortex neutral by default
- but restore one real bounded executive loop where larger-task work actually needs it
