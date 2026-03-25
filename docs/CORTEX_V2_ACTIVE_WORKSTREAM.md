# Cortex v2 Active Workstream

Status: live workflow-state ledger for compaction-safe continuation.

This document records accepted baseline truth, current seam state, blocked moves, and acknowledged workspace noise.
It is workflow state only. It does not override the packet documents, implementation authority, phase gates, status notes, or correspondence.

## 1. Accepted baseline

- Accepted baseline branch: `codex/r4f-reference-feedback-reaudit`
- Accepted baseline commit: `cdcf6d6`
- Accepted baseline state:
  - burden-axis re-audit is accepted through the three thrash-host burden slices
  - package-level burden remains `insufficient`
  - mediation remains blocked / not justified
  - verification-ergonomics expansion beyond the accepted post-`E4` boundary is not currently promoted
  - continuation hardening, the Erika support surface, the runtime-program lock, the first accepted reference-host local CLI shell, the first bounded reference executive-state builder, the first bounded reference soft-control scoring/selection layer, the first integrated computed executive slice inside the runtime shell, and the first one-process live continuity slice plus explicit rejection enforcement are accepted on top of the same product truth
  - the corrective runtime hardening now preserves suspended pending-goal anchors across non-continuity events, explicitly rejects malformed `open`, surfaces session-id mismatch as an explicit contradiction, and keeps lawful commitment truth visible even when continuity rejection is also present
  - the first bounded `R4` reference closed-loop feedback slice is now landed on top of that shell: last-step realization feedback persists only the immediately previous realized outcome, the builder consumes that feedback only through bounded uncertainty/contradiction/brake-pressure updates, the CLI exposes a top-level control ledger, and latched-brake enforcement is now real and contradiction-preserving
- Accepted baseline authority anchors:
  - `docs/CORTEX_V2_IMPLEMENTATION_STATUS_NOTE.md`
  - `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
  - `docs/CORTEX_V2_MEDIATION_JUSTIFICATION_NOTE.md`
  - `docs/CORTEX_V2_VERIFICATION_ERGONOMICS_MASTER_PLAN_0.md`
  - `docs/CORTEX_V2_REFERENCE_RUNTIME_PROGRAM_0.md`
  - `docs/CORTEX_V2_REFERENCE_FEEDBACK_PROGRAM_0.md`

## 2. Current campaign and seam state

- Current campaign: bounded senior-critique closure train for the accepted `R4` feedback slice
- Current working branch at ledger update: `codex/s0-r4-accepted-head-truth`
- Current branch role: deterministic docs/test seam for accepted-head normalization after `R4` closeout
- Current candidate seam: `S1` committed end-to-end proof for `R4` feedback and enforcement behavior
- Current seam status: `accepted-head truth normalization in progress`
- Seam risk: this seam is deterministic docs/test truth alignment only; later `S1` and any `S2` fix seam remain cross-layer runtime review work

## 3. Next lawful move

- Corrective runtime re-hardening answer:
  - the pending-goal anchor-loss bug is resolved
  - the living-correspondence drift is resolved
  - session mismatch and commitment-vs-continuity coexistence are now explicit in code, docs, and tests
  - the zero-finding re-audit bundle passed from the corrected runtime baseline
- Next lawful move from this clean accepted head:
  - last-step realization feedback, the feedback-conditioned builder update, the top-level control ledger, and latched-brake enforcement are all landed
  - selected-family truth and realized-family truth remain distinct when enforcement overrides runtime behavior
  - the zero-finding re-audit bundle passed from the accepted `R4` closeout head `cdcf6d6`
  - normalize accepted-head truth so support/workstream surfaces point to the actual clean accepted head rather than the earlier runtime landing commit
  - then add review-grade end-to-end proof for feedback propagation and CLI-visible enforcement behavior before claiming `R4` is hard to critique
  - do not auto-open a new product program from this work; this is a closure-hardening train only

## 4. Explicitly blocked moves

- Do not treat the mixed `codex/e1-verification-substrate-entrypoints` worktree as accepted truth.
- Do not branch new work from archival `main`.
- Do not reopen `E6` verification-ergonomics helper work without a new explicit re-audit.
- Do not promote package-level mediation justification from current burden evidence.
- Do not let support-surface documents silently redefine packet or status authority.
- Do not automatically open feedback, multi-host runtime, runtime AUX activation, offline consolidation, or mediation implementation from the success of `R3`.
- Do not open Gemini/OpenAI runtime, cross-host runtime, runtime AUX activation, offline consolidation, or mediation implementation from this reference runtime-shell line.
- Do not reopen `R3` corrective work without a new explicit runtime problem or a new audit finding.
- Do not widen `R4` into cross-process continuity, cross-host runtime, runtime AUX activation, offline consolidation, or mediation.
- Do not let `R4` move enforcement or policy ownership into Core.
- Do not treat the first landed `R4` slice as permission for longer-window feedback history, a generic policy court, or broader runtime widening without a new program lock.

## 5. Acknowledged worktree noise at ledger update

- The accepted `R4` closeout head `cdcf6d6` is clean on the current closeout line.
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
