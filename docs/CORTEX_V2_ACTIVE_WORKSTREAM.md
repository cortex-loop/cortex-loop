# Cortex v2 Active Workstream

Status: live workflow-state ledger for compaction-safe continuation.

This document records accepted baseline truth, current seam state, blocked moves, and acknowledged workspace noise.
It is workflow state only. It does not override the packet documents, implementation authority, phase gates, status notes, or correspondence.

## 1. Accepted baseline

- Accepted baseline branch: `codex/k2-openai-host-control`
- Accepted baseline commit: `9ed7dae`
- Accepted baseline state:
  - burden-axis re-audit remains accepted through the three thrash-host burden slices
  - package-level burden remains `insufficient`
  - mediation remains blocked / not justified
  - the verification/evidence restack train remains landed on the same product truth
  - the OpenAI host-realization cell now has a committed three-pair evidence series and `candidate_positive` cell-level signal for better host-specialized realization
  - package-level mediation evidence remains `insufficient`
  - lower visible burden remains unclaimed for host-realization
  - accepted workflow baseline truth is now normalized around the accepted K2 runtime/product closeout line
  - the reference runtime shell, bounded reference continuity, OpenAI documented-host-event runtime shell, raw-transcript ingress shell, loopback service shell, and bounded outbound OpenAI host-control lane are accepted on the same K2 closeout line
  - `O4` is now landed on the current line
  - the next lawful product-facing direction is executive-loop computation over live runtime outcomes
- Accepted baseline authority anchors:
  - `docs/CORTEX_V2_IMPLEMENTATION_STATUS_NOTE.md`
  - `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
  - `docs/CORTEX_V2_MEDIATION_JUSTIFICATION_NOTE.md`
  - `docs/CORTEX_V2_VERIFICATION_ERGONOMICS_MASTER_PLAN_0.md`

## 2. Current campaign and seam state

- Current campaign: `K3 executive live-outcome train`
- Current working branch at ledger update: `codex/k3-executive-live-outcome`
- Current branch role: branch-local K3 candidate over accepted K2 truth
- Current candidate seam: `K3` executive live-outcome closeout
- Current seam status: `K3 candidate implemented and verified / accepted baseline remains clean accepted K2 line`
- Seam risk: the K3 candidate is a parser/doc-sync plus timing or environment-sensitive runtime/service projection seam; repeated direct and repo-local reruns are required before acceptance

## 3. Next lawful move

- Current candidate answer after K3 implementation:
  - the accepted K2 baseline now includes the bounded outbound OpenAI host-control lane at `9ed7dae`
  - explicit executive allocation diagnostics are now real on the branch-local K3 line
  - `Q_t^{mem}=0.0`, `alpha_t=1.0`, and `allocated_score == online_score` for current scope
  - runtime and service projections now surface nested `control_ledger.allocation_diagnostics`
  - package-level mediation evidence remains `insufficient`
- Next lawful move:
  - rerun the targeted K3 bundle and repo-local revalidation targets on the clean branch
  - then either accept K3 onto baseline truth or reject it explicitly

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
- Do not reopen K2 into new outbound host-control lanes.
- Do not open support-memory runtime, mediation / `Q_t^{final}` experimentation, Gemini runtime shell, tools or tool-result submission, runtime AUX activation, offline consolidation, or generic reward-learning doctrine from `K3`.

## 5. Acknowledged worktree noise at ledger creation

- The dirty donor branch `codex/e1-verification-substrate-entrypoints` remains mixed and is not the source of truth for future runtime restack work.
- The donor runtime branches remain source material only; their workflow truth is not authoritative on this line.
- The accepted `k2` line is now the source of accepted workflow baseline truth until a later accepted baseline update lands.
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
