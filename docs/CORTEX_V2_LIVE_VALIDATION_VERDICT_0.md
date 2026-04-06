# CORTEX_V2_LIVE_VALIDATION_VERDICT_0

Date: 2026-04-06
Status: live-validation verdict note for the R1 two-lane reset

## Verdict

**canonical runtime truth is re-earned for current scope; operator truth remains watchlist-only**

This is the broader live-validation verdict after the R1 reset.

Reason:

- the repo now distinguishes two live-evidence lanes:
  - `service_api`: `execution_surface = direct_api`, `evidence_role = canonical_truth`
  - `operator_cli`: `execution_surface = headless_cli`, `evidence_role = watchlist`
- current-machine service auth is ready for OpenAI and still missing for Claude and Gemini
- OpenAI now clears the canonical direct-API `canonical_anchor` suite twice on:
  - `pass_minimal`
  - `truth_gap`
  - `restart_continuity`
- so one host is now re-earned on the canonical runtime lane for current scope on this machine
- operator/headless-CLI evidence remains useful, but it is no longer allowed to stand in for canonical runtime truth by itself

## Current lane reading

### Service/API lane

- canonical truth lane
- current-machine status:
  - OpenAI: re-earned for current scope
  - Claude: blocked on missing auth
  - Gemini: blocked on missing auth
- one current-machine API truth anchor is now re-earned for current scope

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
- service/API truth remains blocked on missing `ANTHROPIC_API_KEY`

### Gemini

- operator watchlist signal remains the noisiest host-boundary line
- review-branch recoveries remain evidence only
- service/API truth remains blocked on missing direct auth

### OpenAI

- operator watchlist signal is currently the strongest
- service/API canonical truth is re-earned for current scope through two positive `canonical_anchor` cycles
- the direct-API anchor is currently limited to OpenAI current scope, not broader package closure

## Next lawful move

1. land the OpenAI current-scope canonical anchor on the accepted line
2. add `claude` if auth is ready on that machine
3. keep Gemini watchlist-only until direct API/service auth exists

Do not reopen mediation, AUX runtime, memory/runtime learning, or broad control-law expansion before that.
