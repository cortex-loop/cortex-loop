# CORTEX_V2_LIVE_VALIDATION_VERDICT_0

Date: 2026-03-28
Status: L2/L2b/L2c live-testing environment verdict note

## Verdict

**lifecycle-first is promising but under-instrumented**

Reason:

- all three signed-in operator smokes and provider baselines are now green,
- Claude is now re-earned on a hook-backed operator lane:
  - `pass_minimal` twice
  - `truth_gap`
  - `restart_continuity`
- the OpenAI operator lane is now strong on the host-native surfaces that matter:
  - `codex exec` smoke is clean,
  - `codex app-server` passes `pass_minimal` twice,
  - `codex app-server` preserves `truth_gap`,
  - `codex app-server` passes `restart_continuity` twice,
- the cross-host `make live-host-native-product-paths` entrypoint still inherits the current Claude/Gemini watchlist drift and is not the clean closure signal yet,
- Gemini now has real hook-backed lifecycle capture and at least one full `pass_minimal` success on explicit fallback `gemini-2.5-flash`,
- but Gemini still hits quota/capacity retries before repeat-stable closure is earned,
- and the automation/service lane is still all-blocked on missing automation credentials.

## Current host summary

### Claude

- operator probe: clean on `claude-sonnet-4-6`
- operator baseline: clean twice
- operator product path:
  - hook-backed `pass_minimal`: success twice
  - hook-backed `truth_gap`: truthful incomplete
  - `restart_continuity`: succeeds
- hook surface:
  - `SessionStart`
  - `PreToolUse`
  - `PostToolUse`
  - `Stop`
  - `SessionEnd`
- automation lane: blocked on missing `ANTHROPIC_API_KEY`

### Gemini

- operator probe: fallback to `gemini-2.5-flash` succeeds
- operator baseline: clean twice on fallback `gemini-2.5-flash`
- operator product path:
  - hook-backed `pass_minimal`: at least one full success now exists, but quota/capacity warnings still appear
  - `truth_gap`: not yet re-earned on the refreshed hook-backed lane
  - `restart_continuity`: not yet re-earned on the refreshed hook-backed lane
  - this remains a watchlist rather than a closed host line
- hook surface:
  - `SessionStart`
  - `BeforeTool`
  - `AfterTool`
  - `SessionEnd`
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
- `L2c` now re-earns Claude and Gemini on their documented hook surfaces rather than relying on transcript-only operator truth

## Next corrective seam

Open one bounded **Claude/Gemini operator-harness re-audit plus automation-credential stabilization** seam that:

- reruns Gemini until either repeat-stable `gemini-2.5-flash` closure is earned or the warning-preserving fallback policy is narrowed further
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
