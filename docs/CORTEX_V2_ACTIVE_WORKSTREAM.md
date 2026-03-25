# Cortex v2 Active Workstream

Status: live workflow-state ledger for compaction-safe continuation.

This document records accepted baseline truth, current seam state, blocked moves, and acknowledged workspace noise.
It is workflow state only. It does not override the packet documents, implementation authority, phase gates, status notes, or correspondence.

## 1. Accepted baseline

- Accepted baseline branch: `codex/r5e-short-window-feedback-reaudit`
- Accepted `R5` opening parent: `9d07c5b`
- Accepted `R5` proof head: `ee41eb4`
- Accepted `R5` deterministic closeout head: `fd6789f`
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
  - the accepted `R5` proof head `ee41eb4` now carries the bounded three-step realized-outcome window, bounded prior-window summary law, runtime-step summary projection, and top-level CLI `feedback_window_summary`
  - the accepted `R5` closeout line is truthfully landed at deterministic closeout head `fd6789f`, where the same bounded `R5` slice remains closed without reopening scope or changing phase-gate status
  - committed end-to-end proof now exists at `ee41eb4` for clean-window zero pressure, single-mismatch `0.55` floor, repeated-mismatch `0.70` floor, and oldest-entry truncation on the fourth append
  - the earlier `R4` proof head `7672304`, runtime landing `cecd82d`, and `R5` opening parent `9d07c5b` remain part of the same closeout history rather than competing baselines
- Accepted baseline authority anchors:
  - `docs/CORTEX_V2_IMPLEMENTATION_STATUS_NOTE.md`
  - `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
  - `docs/CORTEX_V2_MEDIATION_JUSTIFICATION_NOTE.md`
  - `docs/CORTEX_V2_VERIFICATION_ERGONOMICS_MASTER_PLAN_0.md`
  - `docs/CORTEX_V2_REFERENCE_RUNTIME_PROGRAM_0.md`
  - `docs/CORTEX_V2_REFERENCE_FEEDBACK_PROGRAM_0.md`
  - `docs/CORTEX_V2_REFERENCE_FEEDBACK_PROGRAM_1.md`

## 2. Current campaign and seam state

- Current campaign: `R5` short-window feedback and sustained-pressure closeout complete for current scope
- Current working branch at ledger update: `codex/r5f-accepted-baseline-truth-normalization`
- Current branch role: deterministic docs/test seam normalizing accepted-baseline truth on top of the already-landed `R5` closeout line
- Current candidate seam: `none`
- Current seam status: `R5 landed / stop after bounded short-window feedback slice`
- Seam risk: this closeout seam is deterministic docs/support/correspondence truth alignment only; all load-bearing `R5` runtime seams are already landed on the same line

## 3. Next lawful move

- `R5` closeout answer:
  - the accepted `R5` proof head `ee41eb4` carries the bounded three-step realized-outcome window, bounded prior-window summary law, runtime-step summary projection, and top-level CLI `feedback_window_summary`
  - the accepted `R5` landed closeout for that same line is anchored at deterministic closeout head `fd6789f`
  - `R4` last-step behavior remains a strict subset of the new window law
  - scorer law remains unchanged
  - the zero-finding re-audit bundle passed for current scope
- Next lawful move from this clean accepted head:
  - stop again and choose any broader runtime or product program explicitly
  - if future work opens, separate longer-window feedback from broader runtime widening
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
- Do not treat the first landed `R5` slice as permission for longer-than-three-step feedback history, a scoring rewrite, a new policy court, or broader runtime widening without a new program lock.
- Do not widen `R5` into cross-process continuity, cross-host runtime, runtime AUX activation, offline consolidation, or mediation.

## 5. Acknowledged worktree noise at ledger update

- The accepted `R5` proof head `ee41eb4` and deterministic closeout head `fd6789f` are both clean on the same `R5` closeout line.
- The accepted `R4` proof head `7672304`, runtime landing `cecd82d`, and `R5` opening parent `9d07c5b` remain part of the same closure-train history and are not competing baselines.
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
