# Cortex v2 Active Workstream

Status: live workflow-state ledger for compaction-safe continuation.

This document records accepted baseline truth, current seam state, blocked moves, and acknowledged workspace noise.
It is workflow state only. It does not override the packet documents, implementation authority, phase gates, status notes, or correspondence.

## 1. Accepted baseline

- Accepted baseline branch: `codex/s3-r4-senior-closeout`
- Accepted baseline commit: `9d07c5b`
- Accepted baseline state:
  - burden-axis re-audit is accepted through the three thrash-host burden slices
  - package-level burden remains `insufficient`
  - mediation remains blocked / not justified
  - verification-ergonomics expansion beyond the accepted post-`E4` boundary is not currently promoted
  - continuation hardening, the Erika support surface, the runtime-program lock, the first accepted reference-host local CLI shell, the first bounded reference executive-state builder, the first bounded reference soft-control scoring/selection layer, the first integrated computed executive slice inside the runtime shell, and the first one-process live continuity slice plus explicit rejection enforcement are accepted on top of the same product truth
  - the corrective runtime hardening now preserves suspended pending-goal anchors across non-continuity events, explicitly rejects malformed `open`, surfaces session-id mismatch as an explicit contradiction, and keeps lawful commitment truth visible even when continuity rejection is also present
  - the first bounded `R4` reference closed-loop feedback slice is now landed on top of that shell: last-step realization feedback persists only the immediately previous realized outcome, the builder consumes that feedback only through bounded uncertainty/contradiction/brake-pressure updates, the CLI exposes a top-level control ledger, and latched-brake enforcement is now real and contradiction-preserving
  - committed end-to-end proof now exists for session-rejection feedback propagation, prior-enforcement-override pressure, clean-success no false pressure, deterministic control-ledger ordering, and CLI-visible selected-vs-realized divergence
  - a zero-finding adversarial runtime/API review found no defect for current scope
  - the accepted `R4` closeout head is now `9d07c5b`; the accepted proof head `7672304` and runtime landing `cecd82d` remain part of the same closeout history rather than the current baseline
- Accepted baseline authority anchors:
  - `docs/CORTEX_V2_IMPLEMENTATION_STATUS_NOTE.md`
  - `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
  - `docs/CORTEX_V2_MEDIATION_JUSTIFICATION_NOTE.md`
  - `docs/CORTEX_V2_VERIFICATION_ERGONOMICS_MASTER_PLAN_0.md`
  - `docs/CORTEX_V2_REFERENCE_RUNTIME_PROGRAM_0.md`
  - `docs/CORTEX_V2_REFERENCE_FEEDBACK_PROGRAM_0.md`
  - `docs/CORTEX_V2_REFERENCE_FEEDBACK_PROGRAM_1.md`

## 2. Current campaign and seam state

- Current campaign: `R5` short-window feedback and sustained-pressure program opened on the accepted `R4` closeout line
- Current working branch at ledger update: `codex/r5e-short-window-feedback-reaudit`
- Current branch role: deterministic support/program-lock seam opening the bounded `R5` runtime program
- Current candidate seam: `R5B`
- Current seam status: `P0A + R5A landed / `R5` open / stop after one bounded load-bearing seam at a time`
- Seam risk: this seam is deterministic docs/support/program-lock work only; the next seam becomes cross-layer runtime work and must remain one major seam per session

## 3. Next lawful move

- `R4` closeout answer:
  - the accepted baseline is now the clean senior-closeout head `9d07c5b`
  - the accepted proof head `7672304` still carries review-grade end-to-end proof inside the same closeout history
  - selected-family truth and realized-family truth remain distinct when enforcement overrides runtime behavior
  - the zero-finding adversarial runtime/API review found no defect for current scope
- Next lawful move from this clean accepted head:
  - open `R5B` as the first bounded short-window feedback seam
  - add a reference-only feedback window bounded to three runtime-realized outcomes
  - keep `R4` last-step behavior as a strict subset of the new window law
  - do not change scorer law in this train
  - do not auto-open cross-process continuity, cross-host runtime, runtime AUX activation, offline consolidation, or mediation from this work

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
- Do not widen `R5` beyond a bounded three-step reference-only feedback window, a prior-window summary, and the matching runtime/CLI trace surface.
- Do not rewrite scorer law, open a new policy court, or widen host/runtime scope inside `R5`.

## 5. Acknowledged worktree noise at ledger update

- The accepted closeout head `9d07c5b` is clean on the `R5` opening line.
- The accepted proof head `7672304` remains part of the same `R4` closeout history and is not a competing baseline.
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
