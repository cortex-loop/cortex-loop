# CORTEX_V2_LIVE_VALIDATION_VERDICT_0

Date: 2026-04-07
Status: live-validation verdict note for the R1 two-lane reset

## Verdict

**canonical runtime truth is re-earned for current scope; operator truth remains watchlist-only**

This is the broader live-validation verdict after the R1 reset.

Reason:

- the repo now distinguishes two live-evidence lanes:
  - `service_api`: `execution_surface = direct_api`, `evidence_role = canonical_truth`
  - `operator_cli`: `execution_surface = headless_cli`, `evidence_role = watchlist`
- the accepted current product scope on the canonical lane is now OpenAI-only
- current-machine service auth is ready for OpenAI and still missing for Claude and Gemini
- OpenAI now clears the canonical direct-API `canonical_anchor` suite repeat-stably on:
  - `pass_minimal`
  - `truth_gap`
  - `restart_continuity`
- exact cycle count remains local-artifact truth under `.cortex/live_validation/automation/openai/service/`
- Claude retains the same canonical suite implementation as future host-expansion plumbing, but it is intentionally outside the current product scope
- so the current product/runtime claim is now re-earned on the canonical runtime lane for current scope on this machine
- operator/headless-CLI evidence remains useful, but it is no longer allowed to stand in for canonical runtime truth by itself

## Current lane reading

### Service/API lane

- canonical truth lane
- current accepted product scope:
  - OpenAI: re-earned for current scope
- future host-expansion backlog:
  - Claude: shared canonical suite plumbing exists, but auth is still missing on this machine
  - Gemini: intentionally out of canonical scope until its direct API lane is opened deliberately
- one current-machine API truth anchor is now re-earned for current OpenAI-only product scope

### Operator/CLI lane

- watchlist lane
- Claude: positive watchlist signal
- OpenAI: positive watchlist signal
- Gemini: unresolved watchlist signal on the accepted line

This makes the current machine useful for:

- canonical runtime confirmation on OpenAI
- host watchlisting
- packaging/confound detection
- wrapper-burden falsification

It does not yet make the broader package sufficient for cross-host canonical runtime closure.

## Host summary

### Claude

- operator watchlist signal is net positive
- the shared `canonical_anchor` direct-API path remains implemented as future host-expansion plumbing
- Claude is intentionally outside the current OpenAI-only product scope
- later Claude service/API truth remains blocked on missing `ANTHROPIC_API_KEY`

### Gemini

- operator watchlist signal remains the noisiest host-boundary line
- review-branch recoveries remain evidence only
- Gemini remains intentionally outside current product scope and watchlist-only
- later service/API truth remains blocked on missing direct auth

### OpenAI

- operator watchlist signal is currently the strongest
- service/API canonical truth is repeat-stably re-earned for current scope; exact cycle count is local-artifact truth
- the direct-API anchor now defines the accepted current product scope
- the accepted OpenAI-only product runtime now uses the compact `decision + journal` carrier rather than the older allocation-heavy shell

## Next lawful move

1. open the bounded `X2` OpenAI-only support/eval compression train from the accepted local `main` line
2. keep Claude and Gemini on watchlist or future host-expansion backlog only
3. do not widen current product scope without a separate host-expansion train

Do not reopen mediation, AUX runtime, memory/runtime learning, or broad control-law expansion before that.
