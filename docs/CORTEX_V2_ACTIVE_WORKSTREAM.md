# Cortex v2 Active Workstream

Status: live workflow-state ledger for compaction-safe continuation.

This document records accepted baseline truth, current seam state, blocked moves, and acknowledged workspace noise.
It is workflow state only. It does not override the packet documents, implementation authority, phase gates, status notes, or correspondence.

## 1. Accepted baseline

- Accepted baseline branch: `codex/s0b-erika-support-closeout`
- Accepted baseline commit: `6218115`
- Accepted baseline state:
  - burden-axis re-audit is accepted through the three thrash-host burden slices
  - package-level burden remains `insufficient`
  - mediation remains blocked / not justified
  - verification-ergonomics expansion beyond the accepted post-`E4` boundary is not currently promoted
  - continuation hardening and the Erika support surface are accepted on top of the same product truth
- Accepted baseline authority anchors:
  - `docs/CORTEX_V2_IMPLEMENTATION_STATUS_NOTE.md`
  - `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
  - `docs/CORTEX_V2_MEDIATION_JUSTIFICATION_NOTE.md`
  - `docs/CORTEX_V2_VERIFICATION_ERGONOMICS_MASTER_PLAN_0.md`
  - `docs/CORTEX_V2_REFERENCE_RUNTIME_PROGRAM_0.md`

## 2. Current campaign and seam state

- Current campaign: reference runtime-shell opening
- Current working branch at ledger update: `codex/r1a-reference-runtime-program-lock`
- Current branch role: clean runtime-program branch opened from the accepted support parent
- Current candidate seam: runtime program lock for the reference-host local CLI shell
- Current seam status: `in progress / local-only`
- Seam risk: deterministic code/doc seam

## 3. Next lawful move

- Land the runtime-program lock seam:
  - add `docs/CORTEX_V2_REFERENCE_RUNTIME_PROGRAM_0.md`
  - add post-closeout runtime-program rows to `docs/CORTEX_V2_PHASE_GATES_2.md`
  - update the Erika tracker to mark the chosen next opening move as the reference runtime shell
  - extend the doc drift guard so these contracts stay explicit
- After `R1A` is accepted, open `R1B` as the first runtime-code seam from a clean tree.

## 4. Explicitly blocked moves

- Do not treat the mixed `codex/e1-verification-substrate-entrypoints` worktree as accepted truth.
- Do not branch new work from archival `main`.
- Do not reopen `E6` verification-ergonomics helper work without a new explicit re-audit.
- Do not promote package-level mediation justification from current burden evidence.
- Do not let support-surface documents silently redefine packet or status authority.
- Do not open Gemini/OpenAI runtime, runtime AUX activation, offline consolidation, or mediation implementation from this program-opening seam.

## 5. Acknowledged worktree noise at ledger update

- The accepted runtime-program line is clean at the start of `R1A`.
- The older `codex/e1-verification-substrate-entrypoints` workspace remains mixed and is not the source of truth for this train.
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
