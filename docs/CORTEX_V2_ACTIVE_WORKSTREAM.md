# Cortex v2 Active Workstream

Status: live workflow-state ledger for compaction-safe continuation.

This document records accepted baseline truth, current seam state, blocked moves, and acknowledged workspace noise.
It is workflow state only. It does not override the packet documents, implementation authority, phase gates, status notes, or correspondence.

## 1. Accepted baseline

- Accepted baseline branch: `codex/j1-openai-host-realization-three-pair`
- Accepted baseline commit: `21354ab`
- Accepted baseline state:
  - burden-axis re-audit remains accepted through the three thrash-host burden slices
  - package-level burden remains `insufficient`
  - mediation remains blocked / not justified
  - the verification/evidence restack train is now landed for current scope on top of the same product truth
  - the OpenAI host-realization cell now has a committed three-pair evidence series and `candidate_positive` cell-level signal for better host-specialized realization
  - package-level mediation evidence remains `insufficient`
  - lower visible burden remains unclaimed for host-realization
  - verification-ergonomics expansion beyond the accepted restack boundary is not currently promoted without a new explicit non-feature seam
- Accepted baseline authority anchors:
  - `docs/CORTEX_V2_IMPLEMENTATION_STATUS_NOTE.md`
  - `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
  - `docs/CORTEX_V2_MEDIATION_JUSTIFICATION_NOTE.md`
  - `docs/CORTEX_V2_VERIFICATION_ERGONOMICS_MASTER_PLAN_0.md`

## 2. Current campaign and seam state

- Current campaign: restack acceptance truth normalization is now present on the working branch as a governance-only corrective seam
- Current working branch at ledger update: `codex/j2-restack-acceptance-truth-normalization`
- Current branch role: bounded workflow/support truth-normalization candidate over the accepted `j1` line; it does not widen runtime, packet, phase-gate, or correspondence scope
- Current candidate seam: `j2` restack acceptance truth normalization
- Current seam status: `in progress / accepted baseline remains clean accepted j1 line`
- Seam risk: shared verification-plumbing seam

## 3. Next lawful move

- Accepted answer on the current accepted `j1` line:
  - the verification/evidence restack train is accepted truth, not only a historically successful side branch
  - the OpenAI host-realization cell has the accepted three-pair evidence series and `candidate_positive` cell-level signal
  - package-level mediation evidence remains `insufficient`
  - mediation implementation remains blocked
- Next lawful move from this corrective seam:
  - normalize workflow and support surfaces so they all derive accepted baseline truth from this workstream ledger
  - rerun docs-sync, seam-preflight, smoke, and canonical verification
  - accept or reject the corrective seam explicitly before opening any new work

## 4. Explicitly blocked moves

- Do not treat mixed local edits on the current working branch as accepted truth.
- Do not branch new work from archival `main`.
- Do not reopen `E6` verification-ergonomics helper work without a new explicit re-audit.
- Do not promote package-level mediation justification from current burden evidence.
- Do not let support-surface documents silently redefine packet or status authority.
- Do not carry the one-line authority-surface edits currently sitting in `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md` or `docs/CORTEX_V2_SRE_2.md` into the verification/evidence restack train.
- Do not treat a three-pair OpenAI host-realization closeout as permission for mediation implementation.
- Do not reinterpret a host-level `candidate_positive` cell as package-level justification.

## 5. Acknowledged worktree noise at ledger creation

- The dirty donor branch `codex/e1-verification-substrate-entrypoints` remains mixed and is not the source of truth for this corrective seam.
- The accepted `j1` line remains clean and is the source of accepted workflow baseline truth until this corrective seam is accepted.
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
