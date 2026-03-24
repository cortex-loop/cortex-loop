# Cortex v2 Active Workstream

Status: live workflow-state ledger for compaction-safe continuation.

This document records accepted baseline truth, current seam state, blocked moves, and acknowledged workspace noise.
It is workflow state only. It does not override the packet documents, implementation authority, phase gates, status notes, or correspondence.

## 1. Accepted baseline

- Accepted baseline branch: `codex/r3c-continuity-reaudit`
- Accepted baseline commit: `012cc76`
- Accepted baseline state:
  - burden-axis re-audit is accepted through the three thrash-host burden slices
  - package-level burden remains `insufficient`
  - mediation remains blocked / not justified
  - verification-ergonomics expansion beyond the accepted post-`E4` boundary is not currently promoted
  - continuation hardening, the Erika support surface, the runtime-program lock, the first accepted reference-host local CLI shell, the first bounded reference executive-state builder, the first bounded reference soft-control scoring/selection layer, the first integrated computed executive slice inside the runtime shell, and the first one-process live continuity slice plus explicit rejection enforcement are accepted on top of the same product truth
- Accepted baseline authority anchors:
  - `docs/CORTEX_V2_IMPLEMENTATION_STATUS_NOTE.md`
  - `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
  - `docs/CORTEX_V2_MEDIATION_JUSTIFICATION_NOTE.md`
  - `docs/CORTEX_V2_VERIFICATION_ERGONOMICS_MASTER_PLAN_0.md`
  - `docs/CORTEX_V2_REFERENCE_RUNTIME_PROGRAM_0.md`

## 2. Current campaign and seam state

- Current campaign: corrective runtime re-hardening after the `012cc76` audit findings
- Current working branch at ledger update: `codex/c0-runtime-corrective-lock`
- Current branch role: corrective hardening branch reopening `R3` truth while runtime continuity and correspondence fixes are in flight
- Current candidate seam: `C0` corrective truth lock
- Current seam status: `corrective campaign opened / runtime closeout temporarily reopened`
- Seam risk: shared verification-plumbing plus cross-layer product/runtime corrective work

## 3. Next lawful move

- Corrective runtime re-hardening answer:
  - the audit found one real runtime continuity bug and one living-correspondence drift issue
  - the corrective train must resolve those issues plus the remaining session/ordering ambiguities before `R3` is re-closed as audit-clean
- Next lawful move from this corrective branch:
  - land the corrective truth lock
  - harden continuity state preservation and malformed-open rejection
  - make session mismatch and commitment-vs-continuity coexistence explicit in code, docs, and tests
  - repair the stale correspondence comparison rows
  - rerun the full zero-finding re-audit bundle before re-closing `R3`

## 4. Explicitly blocked moves

- Do not treat the mixed `codex/e1-verification-substrate-entrypoints` worktree as accepted truth.
- Do not branch new work from archival `main`.
- Do not reopen `E6` verification-ergonomics helper work without a new explicit re-audit.
- Do not promote package-level mediation justification from current burden evidence.
- Do not let support-surface documents silently redefine packet or status authority.
- Do not automatically open feedback, multi-host runtime, runtime AUX activation, offline consolidation, or mediation implementation from the success of `R3`.
- Do not open Gemini/OpenAI runtime, cross-host runtime, runtime AUX activation, offline consolidation, or mediation implementation from this reference runtime-shell line.
- Do not treat the current `R3` phase-gate closure as final truth until the corrective train re-closes it from a zero-finding audit.

## 5. Acknowledged worktree noise at ledger update

- The accepted `012cc76` closeout head is clean at corrective-train open.
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
