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

- Current campaign: `J1` OpenAI host-realization three-pair evidence closeout is now the next bounded candidate seam
- Current working branch at ledger update: `codex/e4b-reference-lane-helper-closeout`
- Current branch role: accepted reference-helper closeout line that truthfully re-landed `E4` for current scope without changing runtime behavior, packet meaning, or evidence verdict law
- Current candidate seam: `codex/j1-openai-host-realization-three-pair`
- Current seam status: `reference helper closeout landed / next lawful move is OpenAI three-pair evidence closeout on a clean descendant`
- Seam risk: the landed helper-closeout seam was a shared verification-plumbing seam and repeated direct plus smoke reruns passed before acceptance

## 3. Next lawful move

- Accepted answer after reference helper closeout:
  - the active verification-ergonomics plan now says `E4` is landed again for current scope
  - the current reference helper surface now has the accepted closeout truth that matches the already-landed shared outcome/assertion helpers
  - no broader gate-test dedup or `E6` seam is promoted from this re-audit
- Next lawful move:
  - open the OpenAI host-realization three-pair evidence seam on a clean descendant
  - keep accepted baseline truth anchored at `4bb7fbf`
  - keep mediation implementation blocked even if the OpenAI host-realization cell becomes `candidate_positive`

## 4. Explicitly blocked moves

- Do not treat mixed local edits on the current working branch as accepted truth.
- Do not branch new work from archival `main`.
- Do not reopen `E6` verification-ergonomics helper work without a new explicit re-audit.
- Do not promote package-level mediation justification from current burden evidence.
- Do not let support-surface documents silently redefine packet or status authority.
- Do not carry the one-line authority-surface edits currently sitting in `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md` or `docs/CORTEX_V2_SRE_2.md` into the verification/evidence restack train.
- Do not mix the OpenAI three-pair host-realization evidence seam into the reference-helper closeout seam.
- Do not treat a three-pair OpenAI host-realization closeout as permission for mediation implementation.

## 5. Acknowledged worktree noise at ledger creation

- Mixed tracked edits still exist across verification docs, mediation docs, and reference/OpenAI verification surfaces on `codex/e1-verification-substrate-entrypoints`.
- The support-surface theory and visualization files are now landed on this accepted truth-sync branch and are no longer just dirty-branch noise.
- The remaining mixed OpenAI mediation evidence edits still live on `codex/e1-verification-substrate-entrypoints` and should be quarried explicitly rather than accepted wholesale.
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
