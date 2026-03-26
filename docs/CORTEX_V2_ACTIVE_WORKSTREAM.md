# Cortex v2 Active Workstream

Status: live workflow-state ledger for compaction-safe continuation.

This document records accepted baseline truth, current seam state, blocked moves, and acknowledged workspace noise.
It is workflow state only. It does not override the packet documents, implementation authority, phase gates, status notes, or correspondence.

## 1. Accepted baseline

- Accepted baseline branch: `codex/j0-burden-axis-reaudit`
- Accepted baseline commit: `4bb7fbf`
- Accepted baseline state:
  - burden-axis re-audit is accepted through the three thrash-host burden slices
  - package-level burden remains `insufficient`
  - mediation remains blocked / not justified
  - verification-ergonomics expansion beyond the accepted post-`E4` boundary is not currently promoted
- Accepted baseline authority anchors:
  - `docs/CORTEX_V2_IMPLEMENTATION_STATUS_NOTE.md`
  - `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
  - `docs/CORTEX_V2_MEDIATION_JUSTIFICATION_NOTE.md`
  - `docs/CORTEX_V2_VERIFICATION_ERGONOMICS_MASTER_PLAN_0.md`

## 2. Current campaign and seam state

- Current campaign: verification/evidence restack train is landed for current scope
- Current working branch at ledger update: `codex/j1-openai-host-realization-three-pair`
- Current branch role: accepted OpenAI three-pair evidence closeout line that lands the verification/evidence restack train without widening into mediation implementation or new runtime/product behavior
- Current candidate seam: `none`
- Current seam status: `restack landed / next lawful move must be a new explicitly bounded non-feature seam or broader evidence collection seam`
- Seam risk: the landed OpenAI three-pair evidence closeout seam was an evidence-revalidation plus shared verification-plumbing seam and repeated direct plus repo-local reruns passed before acceptance

## 3. Next lawful move

- Accepted answer after OpenAI three-pair evidence closeout:
  - the OpenAI host-realization cell now has a committed three-pair evidence series and `candidate_positive` cell-level signal for better host-specialized realization
  - package-level mediation evidence remains `insufficient`
  - lower visible burden remains unclaimed for host-realization
  - mediation implementation remains blocked
- Next lawful move:
  - if work continues, choose one new explicitly bounded non-feature seam
  - or broaden evidence collection while keeping package-level mediation justification blocked
  - do not open mediation implementation from this line

## 4. Explicitly blocked moves

- Do not treat mixed local edits on the current working branch as accepted truth.
- Do not branch new work from archival `main`.
- Do not reopen `E6` verification-ergonomics helper work without a new explicit re-audit.
- Do not promote package-level mediation justification from current burden evidence.
- Do not let support-surface documents silently redefine packet or status authority.
- Do not carry the one-line authority-surface edits currently sitting in `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md` or `docs/CORTEX_V2_SRE_2.md` into the verification/evidence restack train.
- Do not mix the OpenAI three-pair host-realization evidence seam into the reference-helper closeout seam.
- Do not treat a three-pair OpenAI host-realization closeout as permission for mediation implementation.
- Do not reinterpret a host-level `candidate_positive` cell as package-level justification.

## 5. Acknowledged worktree noise at ledger creation

- Mixed tracked edits still exist across verification docs, mediation docs, and reference/OpenAI verification surfaces on `codex/e1-verification-substrate-entrypoints`.
- The support-surface theory and visualization files are now landed on this accepted truth-sync branch and are no longer just dirty-branch noise.
- The dirty donor branch `codex/e1-verification-substrate-entrypoints` remains mixed and is no longer the source of truth for this restack train.
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
