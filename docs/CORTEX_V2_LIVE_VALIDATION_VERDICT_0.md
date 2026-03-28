# CORTEX_V2_LIVE_VALIDATION_VERDICT_0

Date: 2026-03-28
Status: L2/L2b live-testing environment verdict note

## Verdict

**lifecycle-first is promising but under-instrumented**

Reason:

- all three signed-in operator smokes and provider baselines are now green,
- the OpenAI operator lane is now strong on the host-native surfaces that matter:
  - `codex exec` smoke is clean,
  - `codex app-server` passes `pass_minimal` twice,
  - `codex app-server` preserves `truth_gap`,
  - `codex app-server` passes `restart_continuity` twice,
- the cross-host `make live-host-native-product-paths` entrypoint still inherits the current Claude/Gemini watchlist drift and is not the clean closure signal yet,
- but Claude still has a partial heavier product lane because the current one-turn CLI harness stops at tool-use before `pass_minimal` and `truth_gap` can close,
- Gemini still hits `capacity_exhausted` on the heavier coding harness even on explicit `gemini-2.5-flash` fallback,
- and the automation/service lane is still all-blocked on missing automation credentials.

## Current host summary

### Claude

- operator probe: clean on `claude-sonnet-4-6`
- operator baseline: clean twice
- operator product path:
  - `pass_minimal`: not yet re-earned because the current one-turn CLI harness stops at the first tool-use
  - `truth_gap`: not yet re-earned for the same reason
  - `restart_continuity`: succeeds
- automation lane: blocked on missing `ANTHROPIC_API_KEY`

### Gemini

- operator probe: fallback to `gemini-2.5-flash` succeeds
- operator baseline: clean twice on fallback `gemini-2.5-flash`
- operator product path:
  - `pass_minimal`: still marked `capacity_exhausted` even though the workspace diff and target test succeed
  - `restart_continuity`: still marked `capacity_exhausted`
  - this remains a watchlist rather than a closed host line
- automation lane: blocked on missing ADC or `GEMINI_API_KEY`

### OpenAI

- operator probe: clean on signed-in Codex
- operator baseline: clean twice on `codex exec`
- operator product path:
  - `codex app-server pass_minimal`: success twice
  - `codex app-server truth_gap`: truthful incomplete
  - `codex app-server restart_continuity`: success twice
  - current caveat: App Server `thread/read` remains lossy for ephemeral threads, so the event timeline is the primary lifecycle truth surface
- automation lane: blocked on missing `OPENAI_API_KEY`

## What L2 already improves over L1

- OpenAI signed-in operator truth now uses the host-native Codex surface rather than the wrong `openai` utility surface
- Gemini now has an explicit fallback model policy instead of “preferred only or fail blindly”
- live machine artifacts are local-only and no longer belong in git
- the verdict now depends on a real coding harness rather than summary-only prompts
- `L2b` now re-earns OpenAI on the current host-native App Server lifecycle surface instead of treating `codex exec` alone as the strongest operator proof
- `L2b` explicitly keeps assisted mode deferred rather than smuggling bounded corrective intervention back in from v1

## Next corrective seam

Open one bounded **Claude/Gemini operator-harness re-audit plus automation-credential stabilization** seam that:

- re-audits the Claude CLI harness so `pass_minimal` and `truth_gap` can close honestly without flattening Claude-specific behavior
- stabilizes or narrows the Gemini operator-lane watchlist on `gemini-2.5-flash` or a later explicit fallback
- provides automation credentials for the current service lane:
  - `ANTHROPIC_API_KEY`
  - Vertex ADC or `GEMINI_API_KEY`
  - `OPENAI_API_KEY`

After that seam lands, rerun:

- `make live-preflight`
- `make live-provider-baselines`
- `make live-openai-app-server`
- `make live-host-native-product-paths`
- `make live-cortex-host-control`
- `make live-compare`
