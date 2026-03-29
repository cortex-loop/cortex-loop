# Cortex v2 Active Workstream

Status: live workflow-state ledger for compaction-safe continuation.

This document records accepted baseline truth, current seam state, blocked moves, and acknowledged workspace noise.
It is workflow state only. It does not override the packet documents, implementation authority, phase gates, status notes, or correspondence.

## 1. Accepted baseline

- Accepted baseline branch: `main`
- Accepted baseline commit: `30871e6`
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
  - the reference runtime shell, bounded reference continuity, OpenAI documented-host-event runtime shell, raw-transcript ingress shell, loopback service shell, bounded outbound OpenAI host-control lane, and explicit executive allocation diagnostics remain accepted on the current line
  - the Gemini documented-host-event runtime shell, raw-transcript ingress shell, loopback service shell, and bounded outbound Gemini host-control lane remain accepted on the current line
  - the Claude documented-host-event runtime shell, raw-transcript ingress shell, loopback service shell, and bounded outbound Claude host-control lane remain accepted on the current line
  - refreshed live models on the current line are `claude-sonnet-4-6`, `gemini-2.5-pro`, and `gpt-5.4`
  - `R6`, `O5`, `G1`, `G2`, `G3`, `G4`, `A1`, `A2`, `A3`, and `A4` are landed on the current line
- Accepted baseline authority anchors:
  - `docs/CORTEX_V2_IMPLEMENTATION_STATUS_NOTE.md`
  - `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
  - `docs/CORTEX_V2_MEDIATION_JUSTIFICATION_NOTE.md`
  - `docs/CORTEX_V2_VERIFICATION_ERGONOMICS_MASTER_PLAN_0.md`

## 2. Current campaign and seam state

- Current campaign: `H3-H4 final repo closure landed`
- Current working branch at ledger update: `main`
- Current branch role: root checkout is the clean synced resting branch again
- Current candidate seam: none; `H3-H4` is landed for current scope
- Current seam status: `root main is now the only local checkout target, the frozen non-main branch/worktree set has been retired under pushed archive tags, and the strict cleanup-report gate is now the final hygiene contract`
- Seam risk: deterministic workflow/tooling closeout after archival retirement

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
    - `restart_continuity` is not yet repeat-stable because the latest reruns include a `capacity_exhausted` blocker on `auto`
  - repeat-stable Gemini closure is therefore still unearned
  - the current automation/service lane still fails honestly on missing machine auth
- Next lawful move:
  - use [`/Users/erikahoward/cortex-loop`](/Users/erikahoward/cortex-loop) as the only local checkout and clean synced `main`
  - run `python scripts/repo_workflow.py cleanup-report` or `make repo-hygiene` before calling the repo fully clean
  - if any future non-main branch/worktree is created, either land it promptly or archive/retire it back to this single-checkout state
  - ordinary managed-session work may now resume from clean synced `main`
  - service proof remains blocked until machine auth exists

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
