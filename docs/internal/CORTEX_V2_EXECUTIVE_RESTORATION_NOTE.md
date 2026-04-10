# CORTEX_V2_EXECUTIVE_RESTORATION_NOTE

Surface: internal

Date: 2026-04-10
Status: accepted executive-restoration note with the first verified-work restoration slice landed and the next preservation-state candidate now implemented on the current review line

## Scope

This note records the accepted keep/cut/restore decision for Cortex v2 after the X1/X2 reduction train and the later larger-task exploratory runs.
It does not start implementation by itself.
It exists to keep the next bounded runtime/product seam aligned with the packet, the implementation plan, and the current product truth.

## Authority audited

- `docs/CORTEX_V2_CORE_2.md`
- `docs/CORTEX_V2_SRE_2.md`
- `docs/internal/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
- `docs/internal/V1_CODE_PORT_DETERMINATION.md`
- `docs/internal/CORTEX_V2_ACTIVE_WORKSTREAM.md`

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

The accepted verified-work lane is therefore a **coding-domain realization** of bounded executive restoration.
It is useful evidence, but it is not yet general Cortex proof.

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

What the current review line now adds:

- one minimal preservation-state machine over:
  - task anchor
  - trusted structure
  - falsified structure
  - lawful repair surface
  - intervention budget
- deterministic verified-work anchor activation when no active goal is already present
- preservation-centered repair tickets with mechanical fields only
- repair verification that preserves already-trusted first-attempt structure outside the lawful repair surface

## Conformance reading under the current method

The active method now separates:

- `Cortex truth` — optional work contract, runtime-native verification as control truth, bounded repair
- `brain-wiring truth` — how OpenAI, Claude, and Gemini attach to that same law
- `conformance truth` — how faithfully each active surface realizes the law
- `shipping truth` — the current OpenAI-first product default

This section records the accepted historical proving line that re-earned `O4R` and `CT2`.
It does not, by itself, authorize future service-spend repetition by habit.
If maintainers intentionally defer new OpenAI `service_api` spend, the next lawful move is an explicit truth-realignment seam onto the intended proving surface, not a silent reinterpretation of the historical accepted line.

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

On the accepted feature-flags verified-work breadth pack, the current reading is:

- OpenAI `service_api`: conformant on repeated targeted reruns without regressing the accepted bookmarks or normalize-port packs
- Claude `operator_cli`: conformant on the explicit tri-brain guardrail rerun
- Gemini `operator_cli`: conformant on the explicit tri-brain guardrail rerun
- bookmarks remains the accepted `CT2` anchor pack and `summary.latest` remains bookmarks-only while the third pack stays explicit breadth evidence

The current accepted next decision for the shipping-default lane is therefore `promote`, not `improve_shipping_default`, because the OpenAI `O4R` gap is now closed on repeated targeted local reruns and no non-shipping divergent surface remains on the corrected current line.

On the current E9 repair-yield review line, the paired live proof reads:

- OpenAI `service_api` one-shot control: `11/12` conformant across two full paired rounds
- OpenAI `service_api` repair-enabled candidate: `12/12` conformant across the same two paired rounds
- repair opportunities: `0`
- train outcome: `escalate` because the current three-pack line does not produce enough natural first-attempt failures to measure repair yield honestly
- richer repair-ticket changes were therefore cut from the runtime path rather than kept as unearned mechanism

## Next lawful move

If a later runtime/product seam is opened after this note, the next lawful move is:

1. keep the current thin path as the default when no work contract is present
2. do not reopen OpenAI `service_api` spend by habit; if current policy defers it, open an explicit operator-cli truth-realignment seam instead of pretending the old proving-default lane still governs iteration
3. keep `O4R` stable on its already-earned historical line rather than reopening the law by habit
4. do not reopen breadth by habit; the three-pack historical line is already re-earned on the accepted note
5. if repair yield is the next target, open a smaller repair-pressure investigation that can create honest natural repair opportunities without replay or new Cortex law
6. run the same contract pack across OpenAI, Claude, and Gemini on their strongest available native surfaces whenever a later seam changes Cortex law or touches non-shipping wiring
7. revise Cortex law only if the same divergence repeats across brains; otherwise reopen wiring only on the specific drifting brain/surface
8. keep repeated-failure inhibition and carrier inference deferred until new evidence earns them
9. open any later shipping-truth widening beyond OpenAI only through an explicit separate host shipping train

This is the accepted north-light correction:

- keep Cortex small
- keep Cortex host-native
- keep Cortex neutral by default
- but restore one real bounded executive loop where larger-task work actually needs it

Future executive-improvement seams should therefore be framed as domain-general baskets with domain binding outside SRE, rather than as code-specific helpers or prompt-shaped benchmark doctrine.
