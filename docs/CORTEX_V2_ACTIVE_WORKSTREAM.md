# Cortex v2 Active Workstream

Status: live workflow-state ledger for compaction-safe continuation.

This document records accepted baseline truth, current seam state, blocked moves, and acknowledged workspace noise.
It is workflow state only. It does not override the packet documents, implementation authority, phase gates, status notes, or correspondence.

## 1. Accepted baseline

- Accepted baseline branch: `codex/l1-live-validation`
- Accepted baseline commit: `8eb7f08`
- Accepted baseline state:
  - burden-axis re-audit remains accepted through the three thrash-host burden slices
  - package-level burden remains `insufficient`
  - mediation remains blocked / not justified
  - the verification/evidence restack train remains landed on the same product truth
  - the OpenAI host-realization cell now has a committed three-pair evidence series and `candidate_positive` cell-level signal for better host-specialized realization
  - package-level mediation evidence remains `insufficient`
  - lower visible burden remains unclaimed for host-realization
  - accepted workflow baseline truth remains the refreshed post-A1 live-model line
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

- Current campaign: `L2c Claude and Gemini hook-backed operator lanes`
- Current working branch at ledger update: `codex/l1-live-validation`
- Current branch role: branch-local L2 candidate over accepted refreshed A1 truth
- Current candidate seam: hook-backed Claude/Gemini operator re-earn plus live-truth sync on top of the signed-in-first L2 environment
- Current seam status: `partially implemented and partially verified`
- Seam risk: timing or environment-sensitive evidence seam with local toolchain coupling; repeated reruns are required before any closure claim

## 3. Next lawful move

- Current L2/L2b answer so far:
  - the live-testing environment now has explicit operator and automation lane semantics
  - the local artifact root is `.cortex/live_validation/` rather than repo-tracked `docs/live_validation/`
  - preflight now detects install channels, auth modes, operator probe status, fallback models, and OpenAI surface split
  - all three signed-in operator probes and smoke baselines are now clean:
    - Claude on `claude-sonnet-4-6`
    - Gemini on fallback `gemini-2.5-flash`
    - OpenAI/Codex on `gpt-5.3-codex`
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
  - the Gemini operator lane is now hook-backed as well; hook capture is real and at least one full `pass_minimal` run succeeds on `gemini-2.5-flash`, but the host still emits quota/capacity retries and repeat-stable closure for Gemini is not yet earned
  - the current automation/service lane still fails honestly on missing automation credentials
- Next lawful move:
  - rerun Gemini after the current quota window and decide whether:
    - explicit `gemini-2.5-flash` with warning-preserving success is acceptable for closure
    - or an even narrower signed-in fallback must be documented
  - add or configure automation credentials:
    - `ANTHROPIC_API_KEY`
    - Vertex ADC or `GEMINI_API_KEY`
    - `OPENAI_API_KEY`
  - rerun `make live-preflight`, `make live-provider-baselines`, the focused provider-specific operator reruns, `make live-openai-app-server`, `make live-cortex-host-control`, and `make live-compare`
  - only after Gemini repeat stability and automation auth are re-earned should a broader cross-host closure claim be considered

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

## 5. Acknowledged worktree noise at ledger creation

- `.cortex/live_validation/` now contains local-only generated evidence for the current L2 pass and is expected to churn across reruns.
- Local workspace directories already exist under `.claude/worktrees/`.
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
