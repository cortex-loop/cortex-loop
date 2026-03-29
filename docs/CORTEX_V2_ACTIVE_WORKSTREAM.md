# Cortex v2 Active Workstream

Status: live workflow-state ledger for compaction-safe continuation.

This document records accepted baseline truth, current seam state, blocked moves, and acknowledged workspace noise.
It is workflow state only. It does not override the packet documents, implementation authority, phase gates, status notes, or correspondence.

## 1. Accepted baseline

- Accepted baseline branch: `main`
- Accepted baseline commit lookup: `git rev-parse HEAD` on clean synced `main`
- Accepted baseline note:
  - exact accepted-head hashes are intentionally not mirrored in repo-tracked support docs because they self-stale on the next accepted closure commit
- Accepted baseline state:
  - burden-axis re-audit remains accepted through the three thrash-host burden slices
  - package-level burden remains `insufficient`
  - mediation remains blocked / not justified
  - the verification/evidence restack train remains landed on the same product truth
  - the OpenAI host-realization cell now has a committed three-pair evidence series and `candidate_positive` cell-level signal for better host-specialized realization
  - package-level mediation evidence remains `insufficient`
  - lower visible burden remains unclaimed for host-realization
  - accepted workflow baseline truth now rests on `main` rather than a long-lived working branch
  - final repo closure is now landed on the current line:
    - one clean synced local checkout only
    - one local branch only: `main`
    - no attached non-root worktrees
    - no residual local non-main branches
    - no remote `review/*` heads
    - retired non-main lines preserved under pushed `archive/final-repo-closeout/*` tags
  - `N1` service-lane proof is now landed for current machine truth:
    - automation preflight reruns remain all-`missing`
    - automation baseline reruns now block honestly on readiness rather than faking direct network probes
    - service-lane reruns remain all-blocked on `auth_missing`
    - operator proof remains the accepted current line and is preserved in compare/audit support surfaces when this seam reruns automation-only artifacts
  - `K4` bounded computed executive loop is now landed on the proven reference/OpenAI lanes:
    - `alpha_t` is computed from runtime-visible pressure rather than fixed
    - `Q_t^{mem}` remains `0.0`
    - `allocated_score` can differ from `online_score`
    - selection now runs on allocated-score semantics
    - the existing public runtime projection shapes remain unchanged
  - the bounded K train is now landed on the proven reference/OpenAI lanes:
    - `activation_threshold` is now feedback-conditioned rather than fixed to budget-band baseline alone
    - bounded prior-feedback pressure is now explicit through internal `feedback_pressure_tags`
    - guarded-feedback and latched-brake realization remain explicit rather than smoothing selected-family, realized-family, or lawful commitment truth
    - no support-memory runtime, mediation, service/auth widening, or broader host rollout was introduced
  - Gemini restart-continuity repeat-stability re-audit is now landed for current machine truth:
    - local Gemini settings already match current best practice:
      - no pinned default model
      - `modelRouting=true`
      - explicit project-scoped resume IDs remain valid on the current CLI
    - the Gemini continuity harness now preserves repeated continuity artifacts instead of overwriting them
    - the first inspect-only Gemini continuity turn now uses `plan` approval mode and the resumed edit/test turn keeps `yolo`
    - current local Gemini continuity truth remains mixed on `auto`:
      - successful resumed completions exist
      - first-turn `capacity_exhausted` failures still recur
    - an exploratory `gemini-2.5-flash` sidecar also failed on first-turn `capacity_exhausted`
    - the remaining Gemini continuity blocker now looks host-capacity-driven rather than a settings or resume-semantics mistake
  - the reference runtime shell, bounded reference continuity, OpenAI documented-host-event runtime shell, raw-transcript ingress shell, loopback service shell, bounded outbound OpenAI host-control lane, and explicit executive allocation diagnostics remain accepted on the current line
  - the Gemini documented-host-event runtime shell, raw-transcript ingress shell, loopback service shell, and bounded outbound Gemini host-control lane remain accepted on the current line
  - the Claude documented-host-event runtime shell, raw-transcript ingress shell, loopback service shell, and bounded outbound Claude host-control lane remain accepted on the current line
  - refreshed live models on the current line are `claude-sonnet-4-6`, `gemini-2.5-pro`, and `gpt-5.4`
  - `R6`, `R7`, `R8`, `R9`, `O5`, `O6`, `O7`, `O8`, `G1`, `G2`, `G3`, `G4`, `A1`, `A2`, `A3`, and `A4` are landed on the current line
- Accepted baseline authority anchors:
  - `docs/CORTEX_V2_IMPLEMENTATION_STATUS_NOTE.md`
  - `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
  - `docs/CORTEX_V2_MEDIATION_JUSTIFICATION_NOTE.md`
  - `docs/CORTEX_V2_VERIFICATION_ERGONOMICS_MASTER_PLAN_0.md`

## 2. Current campaign and seam state

- Current campaign: `N2 capable-machine service-proof blocked pending qualified machine`
- Current working branch at ledger update: `main`
- Current branch role: clean synced resting branch after K-train closeout
- Current candidate seam: none; the K train remains landed, the N2 contract/tooling slice is current, and actual capable-machine service proof is blocked here
- Current seam status: `zero-finding K-train closure audit is complete for current scope, live-preflight and automation-lane tooling now honor the accepted-baseline lookup contract again, repeated current-machine N2 reruns reconfirm all three automation auth states as missing, and this machine remains out of scope for actual service proof`
- the compare surface and live-validation truth from earlier seams remain accepted ancestor input and are not being reopened by the landed K train.
- Seam risk: load-bearing runtime seam plus deterministic docs/correspondence sync

## 3. Next lawful move

- Current L2/L2b answer so far:
  - the live-testing environment now has explicit operator and automation lane semantics
  - the local artifact root is `.cortex/live_validation/` rather than repo-tracked `docs/live_validation/`
  - preflight now detects install channels, auth modes, operator probe status, fallback models, and OpenAI surface split
  - the current signed-in smoke surfaces are now clean again:
    - Claude probe and smoke baselines are clean on `claude-sonnet-4-6`
    - Gemini probe and repeated smoke baselines are now clean in CLI auto mode with no pinned `-m` model argument
    - OpenAI/Codex probe and smoke baselines are clean on `gpt-5.3-codex`
  - the OpenAI operator hierarchy is now explicit:
    - `codex exec` for smoke
    - `codex app-server` for lifecycle proof
  - the OpenAI App Server operator lane now completes:
    - `pass_minimal` twice
    - `truth_gap` truthfully
    - `restart_continuity` twice
  - the OpenAI App Server event timeline is now the real lifecycle evidence surface for current scope; ephemeral `thread/read` remains lossy and is not treated as the primary truth surface
  - the generic cross-host `make live-host-native-product-paths` entrypoint still inherits Claude/Gemini watchlist drift and is not yet the clean acceptance signal for current scope
  - the Claude operator lane is now hook-backed and completes:
    - `pass_minimal` twice
    - `truth_gap` truthfully
    - `restart_continuity`
  - the Gemini operator lane is now hook-backed as well
  - Gemini operator testing now starts in CLI auto mode by default and only falls back to explicit models after failure
  - the installed CLI does accept `gemini-2.5-pro`, but the exploratory pro smoke still blocks on `capacity_exhausted`
  - the deeper Gemini auto-mode product-path rerun now shows:
    - `pass_minimal` succeeds twice on `auto` with explicit `capacity_exhausted` warnings
    - `truth_gap` is truthful on the latest reruns on `auto`
    - `restart_continuity` remains mixed after the best-practice re-audit:
      - successful resumed completions exist on `auto`
      - first-turn `capacity_exhausted` failures still recur
      - an exploratory `gemini-2.5-flash` sidecar did not eliminate the first-turn capacity blocker
  - repeat-stable Gemini closure is therefore still unearned
  - the current automation/service lane still fails honestly on missing machine auth
- Next lawful move:
  - keep the machine-auth service lane explicitly deferred on this machine for actual proof execution
  - keep Gemini as the remaining explicit partial host line on this machine
  - do not reopen the K train by inertia now that the bounded proven-lane executive/runtime line is landed
  - the next lawful move inside `N2` is:
    - move the repo to a capable machine
    - confirm clean synced `main`
    - confirm provider CLIs are installed
    - confirm machine auth readiness is `ready` for the intended providers
    - confirm spend approval is explicitly present where required
    - then rerun the bounded service-proof bundle there
  - if a capable machine is not available yet, stay blocked rather than collapsing `N2` into local prep-only work or fake service proof

## 4. Explicitly blocked moves

- Do not treat signed-in provider CLI sessions as equivalent to the automation credentials the current A4 / G4 / O4 service paths require.
- Do not flatten provider auth into a generic shared credential broker.
- Do not shell out from current A4 / G4 / O4 transports to provider CLIs without an explicit host-owned re-audit.
- Do not treat the new OpenAI App Server operator proof as license to reopen v1 assisted mode, bounded corrective retry, or App Server bridge doctrine inside `L2b`.
- Do not flatten Claude/Gemini hook events into a fake OpenAI-style lifecycle vocabulary or vice versa.
- Do not reopen K3 into new executive-allocation widening beyond the accepted current-scope law.
- Do not open support-memory runtime, mediation / `Q_t^{final}` experimentation, tool-result submission, multimodal widening, runtime AUX activation, offline consolidation, or generic reward-learning doctrine from `L2`.
- Do not keep repo-tracked live artifacts under `docs/live_validation/`; live machine output is local-only now.
- Do not interpret the current Gemini operator-lane instability as proof that the signed-in-first design is wrong; it is a host/watchlist issue until repeated reruns say otherwise.
- Do not overread ephemeral OpenAI `thread/read` emptiness as if the App Server lifecycle proof failed; for current scope the event timeline is the authoritative lifecycle surface and the persisted thread view remains a caveat.
- Do not silently discard Gemini capacity warnings when a run otherwise succeeds; preserve them as warnings rather than pretending the host was perfectly stable.
- Do not silently reintroduce a pinned Gemini operator model as the default testing start point; current local truth is that CLI auto mode is the intended default.
- Do not silently promote `gemini-2.5-pro` from exploratory sidecar to closure-path truth while it is still capacity-blocked on smoke.
- Do not reopen Gemini model chasing or assisted-mode speculation inside the active `L4` service-proof train.
- Do not shell out from service transports to provider CLIs.
- Do not overread the current auto-mode improvement as full Gemini closure while `restart_continuity` is still not repeat-stable.
- Do not widen `K4` into support-memory runtime, mediation, service/auth work, or broader host rollout.
- Do not unfreeze threshold law in `K4`; the current budget-band activation-threshold law stays fixed.
- Do not widen the landed K train into support-memory runtime, mediation, vigor scaling, service/auth work on this machine, or broader host rollout.
- Do not start a new managed session from local `main` while it is ahead or diverged from `origin/main`.
- Do not reintroduce extra long-lived local worktrees or non-main branch residue without an explicit new seam.
- Do not leave remote `review/*` heads behind after future publication cleanup.

## 5. Acknowledged worktree noise at ledger creation

- `.cortex/live_validation/` now contains local-only generated evidence for the current L2 pass and is expected to churn across reruns.
- Re-read `git status --short --untracked-files=all` before opening any new seam; this summary is only the continuity reminder, not the canonical file list.

## 6. Resume checklist

Before resuming or opening work:

1. Read `AGENTS.md`.
2. Read this workstream ledger.
3. Read the accepted-baseline authority anchors listed in Section 1.
4. Run `git branch --show-current`.
5. Run `git status --short --untracked-files=all`.
6. Compare the current repo state against the accepted baseline and current seam state recorded here.
7. Restate:
   - accepted baseline branch and commit
   - current seam status
   - next lawful move
   - blocked moves
   - acknowledged workspace noise
8. If the ledger and repo state disagree, record or resolve that drift before widening scope.

## 7. Update triggers

Update this ledger in the same slice whenever any of these change:

- accepted baseline branch or commit
- current campaign
- current seam or seam status
- next lawful move
- blocked moves
- acknowledged worktree noise

Never promote an uncommitted branch head or dirty worktree state to accepted baseline truth.
