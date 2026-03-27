# CORTEX_V2_LIVE_VALIDATION_VERDICT_0

Date: 2026-03-27
Status: first L2 live-testing environment verdict note

## Verdict

**lifecycle-first is promising but under-instrumented**

Reason:

- the signed-in operator lane is now real and has one clean OpenAI/Codex success on the shared coding harness,
- the same operator lane preserves a truthful incompleteness path on OpenAI/Codex,
- but Claude is still blocked on expired auth, Gemini is still an operator-lane watchlist, and the automation/service lane is still all-blocked on missing automation credentials.

## Current host summary

### Claude

- operator probe: `auth_expired`
- operator product path: blocked before task execution
- automation lane: blocked on missing `ANTHROPIC_API_KEY`

### Gemini

- operator probe: fallback to `gemini-2.5-flash` succeeds
- operator baseline: mixed and still operationally unstable
- operator product path: not yet counted as success
- automation lane: blocked on missing ADC or `GEMINI_API_KEY`

### OpenAI

- operator probe: clean on signed-in Codex
- operator baseline: clean on signed-in Codex
- operator product path:
  - `pass_minimal`: success
  - `truth_gap`: truthful incomplete
  - `restart_continuity`: success
- automation lane: blocked on missing `OPENAI_API_KEY`

## What L2 already improves over L1

- OpenAI signed-in operator truth now uses the host-native Codex surface rather than the wrong `openai` utility surface
- Gemini now has an explicit fallback model policy instead of “preferred only or fail blindly”
- live machine artifacts are local-only and no longer belong in git
- the verdict now depends on a real coding harness rather than summary-only prompts

## Next corrective seam

Open one bounded **operator-auth and automation-credential stabilization** seam that:

- refreshes Claude auth and re-proves the Claude signed-in operator lane
- stabilizes or narrows the Gemini operator-lane watchlist on `gemini-2.5-flash` or a later explicit fallback
- provides automation credentials for the current service lane:
  - `ANTHROPIC_API_KEY`
  - Vertex ADC or `GEMINI_API_KEY`
  - `OPENAI_API_KEY`

After that seam lands, rerun:

- `make live-preflight`
- `make live-provider-baselines`
- `make live-host-native-product-paths`
- `make live-cortex-host-control`
- `make live-compare`
