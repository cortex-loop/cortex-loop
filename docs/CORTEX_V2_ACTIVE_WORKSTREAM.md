# Cortex v2 Active Workstream

Status: live workflow-state ledger for compaction-safe continuation.

This document records accepted baseline truth, current seam state, blocked moves, and acknowledged workspace noise.
It is workflow state only. It does not override the packet documents, implementation authority, phase gates, status notes, or correspondence.

## 1. Accepted baseline

- Accepted baseline branch: `codex/a1-claude-runtime-product-parity`
- Accepted baseline commit: `9d6186c`
- Accepted baseline state:
  - burden-axis re-audit remains accepted through the three thrash-host burden slices
  - package-level burden remains `insufficient`
  - mediation remains blocked / not justified
  - the verification/evidence restack train remains landed on the same product truth
  - the OpenAI host-realization cell now has a committed three-pair evidence series and `candidate_positive` cell-level signal for better host-specialized realization
  - package-level mediation evidence remains `insufficient`
  - lower visible burden remains unclaimed for host-realization
  - accepted workflow baseline truth is now normalized around the accepted A1 Claude runtime/product parity line
  - the reference runtime shell, bounded reference continuity, OpenAI documented-host-event runtime shell, raw-transcript ingress shell, loopback service shell, bounded outbound OpenAI host-control lane, and explicit executive allocation diagnostics remain accepted on the current line
  - the Gemini documented-host-event runtime shell, raw-transcript ingress shell, loopback service shell, and bounded outbound Gemini host-control lane remain accepted on the same line
  - the Claude documented-host-event runtime shell, raw-transcript ingress shell, loopback service shell, and bounded outbound Claude host-control lane are now accepted on the same A1 line
  - `R6`, `O5`, `G1`, `G2`, `G3`, `G4`, `A1`, `A2`, `A3`, and `A4` are now landed on the current line
  - the next lawful big product-facing direction is multi-host live validation across reference, Claude, Gemini, and OpenAI
- Accepted baseline authority anchors:
  - `docs/CORTEX_V2_IMPLEMENTATION_STATUS_NOTE.md`
  - `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
  - `docs/CORTEX_V2_MEDIATION_JUSTIFICATION_NOTE.md`
  - `docs/CORTEX_V2_VERIFICATION_ERGONOMICS_MASTER_PLAN_0.md`

## 2. Current campaign and seam state

- Current campaign: `none`
- Current working branch at ledger update: `codex/a1-claude-runtime-product-parity`
- Current branch role: accepted-baseline receipt line over accepted A1 truth
- Current candidate seam: `none`
- Current seam status: `idle / accepted A1 closeout is recorded on the current line`
- Seam risk: `none / no open seam`

## 3. Next lawful move

- Current accepted state after A1 closeout:
  - the accepted A1 baseline now includes explicit K3 executive allocation diagnostics plus Claude runtime, ingress, service, and bounded host-control shells on the same line
  - the direct Claude unit/integration bundles are green, the Claude code is green under `make verify`, and the Claude slice now has repo-local verification entry points on the accepted line
  - package-level mediation evidence remains `insufficient`
- Next lawful move:
  - keep the branch clean and plan one bounded multi-host live validation train across reference, Claude, Gemini, and OpenAI

## 4. Explicitly blocked moves

- Do not treat mixed local edits on the current working branch as accepted truth.
- Do not branch new work from archival `main`.
- Do not reopen `E6` verification-ergonomics helper work without a new explicit re-audit.
- Do not promote package-level mediation justification from current burden evidence.
- Do not let support-surface documents silently redefine packet or status authority.
- Do not let stale campaign-specific cleanup notes survive into the live workstream ledger once the campaign has changed.
- Do not treat a three-pair OpenAI host-realization closeout as permission for mediation implementation.
- Do not reinterpret a host-level `candidate_positive` cell as package-level justification.
- Do not import donor runtime workflow truth wholesale from `codex/c1-reference-continuation`, `codex/o1-openai-runtime-shell`, `codex/o2-openai-ingress-shell`, or `codex/o3-openai-service-shell`.
- Do not reopen K3 into new executive-allocation widening beyond the accepted current-scope law.
- Do not open support-memory runtime, mediation / `Q_t^{final}` experimentation, extra Gemini or OpenAI work, tools or tool-result submission, thinking blocks, multimodal payloads, runtime AUX activation, offline consolidation, or generic reward-learning doctrine from `A1`.
- Do not skip Claude parity and jump straight to multi-host live validation while Claude remains outside the active host roadmap.

## 5. Acknowledged worktree noise at ledger creation

- The dirty donor branch `codex/e1-verification-substrate-entrypoints` remains mixed and is not the source of truth for future runtime restack work.
- The donor runtime branches remain source material only; their workflow truth is not authoritative on this line.
- The accepted `a1` line is now the source of accepted workflow baseline truth until a later accepted baseline update lands.
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
