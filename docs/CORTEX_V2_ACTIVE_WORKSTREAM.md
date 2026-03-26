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

- Current campaign: `E2` / `E5` verification truth-sync is now the next bounded candidate seam
- Current working branch at ledger update: `codex/e1a-resume-protocol-hardening`
- Current branch role: accepted workflow/docs guard line that landed the continuation resume protocol, seam-preflight documentation, and the live workstream ledger without widening runtime or packet scope
- Current candidate seam: `codex/e2e5-verification-truth-sync`
- Current seam status: `continuation hardening landed / next lawful move is verification truth-sync on a clean descendant`
- Seam risk: the landed continuation-hardening seam was a shared verification-plumbing seam and repeated clean-tree reruns passed before acceptance

## 3. Next lawful move

- Accepted answer after continuation hardening:
  - the repo now has an explicit resume protocol in `AGENTS.md`
  - the repo now has a live compaction-safe workstream ledger
  - local verification now documents `make seam-preflight`
  - future seam work now has a narrow drift guard against reopening dirty tracked work
- Next lawful move:
  - open the verification/evidence truth-sync seam on a clean descendant
  - keep the accepted baseline anchored at `4bb7fbf`
  - do not carry mixed local evidence/runtime/support edits from `codex/e1-verification-substrate-entrypoints` directly into accepted truth

## 4. Explicitly blocked moves

- Do not treat mixed local edits on the current working branch as accepted truth.
- Do not branch new work from archival `main`.
- Do not reopen `E6` verification-ergonomics helper work without a new explicit re-audit.
- Do not promote package-level mediation justification from current burden evidence.
- Do not let support-surface documents silently redefine packet or status authority.
- Do not carry the one-line authority-surface edits currently sitting in `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md` or `docs/CORTEX_V2_SRE_2.md` into the verification/evidence restack train.

## 5. Acknowledged worktree noise at ledger creation

- Mixed tracked edits still exist across verification docs, mediation docs, and reference/OpenAI verification surfaces on `codex/e1-verification-substrate-entrypoints`.
- Untracked support-surface files already exist under `docs/erika-visualizations/`.
- Untracked verification guard work already exists at `tests/unit/test_verification_docs_sync.py`.
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
