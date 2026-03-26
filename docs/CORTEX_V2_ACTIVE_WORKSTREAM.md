# Cortex v2 Active Workstream

Status: live workflow-state ledger for compaction-safe continuation.

This document records accepted baseline truth, current seam state, blocked moves, and acknowledged workspace noise.
It is workflow state only. It does not override the packet documents, implementation authority, phase gates, status notes, or correspondence.

## 1. Accepted baseline

- Accepted baseline branch: `codex/k1f-openai-service-closeout`
- Accepted baseline commit: `79b8f39`
- Accepted baseline state:
  - burden-axis re-audit remains accepted through the three thrash-host burden slices
  - package-level burden remains `insufficient`
  - mediation remains blocked / not justified
  - the verification/evidence restack train remains landed on the same product truth
  - the OpenAI host-realization cell now has a committed three-pair evidence series and `candidate_positive` cell-level signal for better host-specialized realization
  - package-level mediation evidence remains `insufficient`
  - lower visible burden remains unclaimed for host-realization
  - accepted workflow baseline truth is now normalized around the accepted K1 runtime/product closeout line
  - the reference runtime shell, bounded reference continuity, OpenAI documented-host-event runtime shell, raw-transcript ingress shell, and loopback service shell are accepted on the same K1 closeout line
  - `O3` is now landed on the current line rather than remaining donor-branch candidate truth
  - the next lawful product-facing directions are bounded outbound OpenAI host-control realization or executive-loop computation over live runtime outcomes
- Accepted baseline authority anchors:
  - `docs/CORTEX_V2_IMPLEMENTATION_STATUS_NOTE.md`
  - `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
  - `docs/CORTEX_V2_MEDIATION_JUSTIFICATION_NOTE.md`
  - `docs/CORTEX_V2_VERIFICATION_ERGONOMICS_MASTER_PLAN_0.md`

## 2. Current campaign and seam state

- Current campaign: `none`
- Current working branch at ledger update: `codex/k1f-openai-service-closeout`
- Current branch role: clean accepted K1 runtime/product closeout line
- Current candidate seam: `none`
- Current seam status: `K1 landed / next lawful move is an explicitly opened follow-on train from accepted K1 truth`
- Seam risk: the landed K1 seam was a parser/doc-sync plus timing or environment-sensitive subprocess, file-I/O, and loopback-HTTP seam; repeated direct and repo-local reruns passed before acceptance

## 3. Next lawful move

- Accepted answer after K1 closeout:
  - the K1 runtime/product restack is accepted workflow truth, not a branch-local candidate
  - the reference runtime shell, bounded reference continuity, OpenAI documented-host-event runtime shell, raw-transcript ingress shell, and loopback service shell are landed on the current line
  - package-level mediation evidence remains `insufficient`
  - mediation implementation remains blocked
- Next lawful move:
  - choose one new explicitly bounded train from accepted K1 truth
  - the two lawful product-facing next directions are:
    - bounded outbound OpenAI host-control realization
    - executive-loop computation over live runtime outcomes

## 4. Explicitly blocked moves

- Do not treat mixed local edits on the current working branch as accepted truth.
- Do not branch new work from archival `main`.
- Do not reopen `E6` verification-ergonomics helper work without a new explicit re-audit.
- Do not promote package-level mediation justification from current burden evidence.
- Do not let support-surface documents silently redefine packet or status authority.
- Do not carry the one-line authority-surface edits currently sitting in `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md` or `docs/CORTEX_V2_SRE_2.md` into the verification/evidence restack train.
- Do not treat a three-pair OpenAI host-realization closeout as permission for mediation implementation.
- Do not reinterpret a host-level `candidate_positive` cell as package-level justification.
- Do not import donor runtime workflow truth wholesale from `codex/c1-reference-continuation`, `codex/o1-openai-runtime-shell`, `codex/o2-openai-ingress-shell`, or `codex/o3-openai-service-shell`.
- Do not open outbound OpenAI host control, Gemini product/runtime, runtime AUX activation, offline consolidation, or mediation implementation from `K1`.

## 5. Acknowledged worktree noise at ledger creation

- The dirty donor branch `codex/e1-verification-substrate-entrypoints` remains mixed and is not the source of truth for future runtime restack work.
- The donor runtime branches remain source material only; their workflow truth is not authoritative on this line.
- The accepted `k1f` line is now the source of accepted workflow baseline truth until a later accepted baseline update lands.
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
