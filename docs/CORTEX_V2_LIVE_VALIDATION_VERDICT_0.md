# CORTEX_V2_LIVE_VALIDATION_VERDICT_0

Date: 2026-03-28
Status: L2/L2b/L2c/L2d/L2e live-testing environment verdict note

## Verdict

**lifecycle-first is promising but under-instrumented**

This remains the broader live-validation verdict because Gemini is still an explicit partial host line and the March 29 automation/service reruns ended in an explicit deferred service continuation for this machine.

The new operator-only payoff note is narrower and may still conclude that operator lifecycle-first is already paying off clearly.
That operator-only audit is now landed for current scope.
The Gemini auto-mode product-path re-earn seam is now landed for current scope.

Reason:

- all three signed-in operator probes and smoke baselines are now green again, with Gemini now starting in CLI auto mode rather than a pinned model,
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
- Gemini now has real hook-backed lifecycle capture and local fallback truth:
  - operator probes and repeated smoke baselines are now clean in CLI auto mode with no pinned `-m` model argument
  - the deeper auto-mode product path now improves materially:
    - `pass_minimal` succeeds twice on `auto` with warning-preserving `capacity_exhausted`
    - `truth_gap` is truthful on the latest auto-mode reruns
    - `restart_continuity` is still not repeat-stable because the latest reruns include a `capacity_exhausted` blocker on `auto`
  - `gemini-2.5-pro` is valid locally but still capacity-blocked on the bounded exploratory smoke lane
- so Gemini remains the only operator-side host still blocking closure,
- and the March 29 automation/service reruns ended in a fully deferred machine-auth service lane on this machine.

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
- automation lane: repeated `N1` reruns remain auth-missing, so the service proof is deferred on this machine

### Gemini

- operator probe: clean in CLI auto mode with no pinned `-m` model argument
- operator baseline: clean twice in CLI auto mode
- operator product path:
  - hook-backed `pass_minimal`: success twice on `auto` with `capacity_exhausted` preserved as a warning
  - `truth_gap`: now truthful on the latest auto-mode reruns
  - `restart_continuity`: not repeat-stable yet because the latest reruns include a `capacity_exhausted` blocker on `auto`
  - this remains a watchlist rather than a closed host line
- exploratory sidecar:
  - `gemini-2.5-pro` smoke remains capacity-blocked
- hook surface:
  - `SessionStart`
  - `BeforeTool`
  - `AfterTool`
  - `SessionEnd`
- automation lane: repeated `N1` reruns remain auth-missing, so the service proof is deferred on this machine

### OpenAI

- operator probe: clean on signed-in Codex
- operator baseline: clean twice on `codex exec`
- operator product path:
  - `codex app-server pass_minimal`: success twice
  - `codex app-server truth_gap`: truthful incomplete
  - `codex app-server restart_continuity`: success twice
  - current caveat: App Server `thread/read` remains lossy for ephemeral threads, so the event timeline is the primary lifecycle truth surface
- automation lane: repeated `N1` reruns remain auth-missing, so the service proof is deferred on this machine

## What L2 already improves over L1

- OpenAI signed-in operator truth now uses the host-native Codex surface rather than the wrong `openai` utility surface
- Gemini now has an explicit fallback model policy instead of “preferred only or fail blindly”
- live machine artifacts are local-only and no longer belong in git
- the verdict now depends on a real coding harness rather than summary-only prompts
- `L2b` now re-earns OpenAI on the current host-native App Server lifecycle surface instead of treating `codex exec` alone as the strongest operator proof
- `L2b` explicitly keeps assisted mode deferred rather than smuggling bounded corrective intervention back in from v1
- `L2c` now re-earns Claude and Gemini on their documented hook surfaces rather than relying on transcript-only operator truth
- `G2` now re-optimizes Gemini operator testing around CLI auto mode, removes the pinned-model default from the smoke surfaces, and keeps explicit fallbacks only for failure recovery
- `G3` now re-earns the deeper Gemini operator lane on top of CLI auto mode: `pass_minimal` and `truth_gap` improved materially, but `restart_continuity` remains the explicit repeat-stability blocker
- `L2e` now proves that Gemini Pro is not the current closure model on this machine and that `flash-lite` rescues continuity but not truth-gap honesty

## Next corrective seam

The Gemini auto-mode product-path re-earn seam is now complete.
The next honest move is one bounded seam, chosen explicitly:

1. For current-machine continuation:
   - keep the machine-auth service lane deferred
   - open one bounded Gemini `restart_continuity` repeat-stability seam
   - do not smooth the current partial continuity story away
2. If you later intentionally reopen service proof:
   - satisfy the bounded service auth/spend contract recorded in `docs/CORTEX_V2_LIVE_SERVICE_PROOF_0.md`
   - then rerun the bounded service-proof lane

For the bounded service-proof path, rerun later:

- `make live-preflight`
- `python3 tools/live_cortex_host_control.py --lane automation --provider claude`
- `python3 tools/live_cortex_host_control.py --lane automation --provider gemini`
- `python3 tools/live_cortex_host_control.py --lane automation --provider openai`
- `make live-compare`
