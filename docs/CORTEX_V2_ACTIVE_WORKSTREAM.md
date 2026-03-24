# Cortex v2 Active Workstream

Status: live workflow-state ledger for compaction-safe continuation.

This document records accepted baseline truth, current seam state, blocked moves, and acknowledged workspace noise.
It is workflow state only. It does not override the packet documents, implementation authority, phase gates, status notes, or correspondence.

## 1. Accepted baseline

- Accepted baseline branch: `codex/r2b-reference-runtime-scoring`
- Accepted baseline commit: `fc6a9cb`
- Accepted baseline state:
  - burden-axis re-audit is accepted through the three thrash-host burden slices
  - package-level burden remains `insufficient`
  - mediation remains blocked / not justified
  - verification-ergonomics expansion beyond the accepted post-`E4` boundary is not currently promoted
  - continuation hardening, the Erika support surface, the runtime-program lock, the first accepted reference-host local CLI shell, the first bounded reference executive-state builder, and the first bounded reference soft-control scoring/selection layer are accepted on top of the same product truth
- Accepted baseline authority anchors:
  - `docs/CORTEX_V2_IMPLEMENTATION_STATUS_NOTE.md`
  - `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
  - `docs/CORTEX_V2_MEDIATION_JUSTIFICATION_NOTE.md`
  - `docs/CORTEX_V2_VERIFICATION_ERGONOMICS_MASTER_PLAN_0.md`
  - `docs/CORTEX_V2_REFERENCE_RUNTIME_PROGRAM_0.md`

## 2. Current campaign and seam state

- Current campaign: computed reference runtime-shell integration opening from an accepted scoring baseline
- Current working branch at ledger update: `codex/r2b-reference-runtime-scoring`
- Current branch role: clean accepted scoring branch after the first bounded `U_t^{sre}` realization
- Current candidate seam: none yet; `R2C` is the next lawful opening move
- Current seam status: `accepted baseline / ready for next seam selection`
- Seam risk: no active seam; the next seam is a cross-layer product/runtime seam

## 3. Next lawful move

- `R2B` stop-gate re-audit answer:
  - yes, the bounded reference-only scoring layer is stable enough to open runtime-shell integration
- Open `R2C` from this clean accepted head:
  - wire the accepted builder and scoring layer into the reference runtime shell
  - surface a compact `executive_state_summary` in the CLI record
  - keep the seam reference-host only and stop again before continuity work
- After `R2C` is accepted, stop and re-audit whether `R3A` can open on the resulting clean tree.

## 4. Explicitly blocked moves

- Do not treat the mixed `codex/e1-verification-substrate-entrypoints` worktree as accepted truth.
- Do not branch new work from archival `main`.
- Do not reopen `E6` verification-ergonomics helper work without a new explicit re-audit.
- Do not promote package-level mediation justification from current burden evidence.
- Do not let support-surface documents silently redefine packet or status authority.
- Do not open `R3A` until `R2C` lands on a clean tree and the computed reference executive slice is honestly marked landed.
- Do not open Gemini/OpenAI runtime, cross-host runtime, runtime AUX activation, offline consolidation, or mediation implementation from this reference runtime-shell line.

## 5. Acknowledged worktree noise at ledger update

- The accepted scoring line is clean at the end of `R2B`.
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
