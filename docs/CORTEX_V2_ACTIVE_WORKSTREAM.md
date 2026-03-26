# Cortex v2 Active Workstream

Status: live workflow-state ledger for compaction-safe continuation.

This document records accepted baseline truth, current seam state, blocked moves, and acknowledged workspace noise.
It is workflow state only. It does not override the packet documents, implementation authority, phase gates, status notes, or correspondence.

## 1. Accepted baseline

- Accepted baseline branch: `codex/j2-restack-acceptance-truth-normalization`
- Accepted baseline commit: `acfccf9`
- Accepted baseline state:
  - burden-axis re-audit remains accepted through the three thrash-host burden slices
  - package-level burden remains `insufficient`
  - mediation remains blocked / not justified
  - the verification/evidence restack train is now landed for current scope on top of the same product truth
  - the OpenAI host-realization cell now has a committed three-pair evidence series and `candidate_positive` cell-level signal for better host-specialized realization
  - package-level mediation evidence remains `insufficient`
  - lower visible burden remains unclaimed for host-realization
  - accepted workflow baseline truth is now normalized around that landed restack line instead of the stale `post-E4` parent story
  - verification-ergonomics expansion beyond the accepted restack boundary is not currently promoted without a new explicit non-feature seam
- Accepted baseline authority anchors:
  - `docs/CORTEX_V2_IMPLEMENTATION_STATUS_NOTE.md`
  - `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
  - `docs/CORTEX_V2_MEDIATION_JUSTIFICATION_NOTE.md`
  - `docs/CORTEX_V2_VERIFICATION_ERGONOMICS_MASTER_PLAN_0.md`

## 2. Current campaign and seam state

- Current campaign: `K1` runtime/product restack is now present on the working branch as a committed candidate train
- Current working branch at ledger update: `codex/k1f-openai-service-closeout`
- Current branch role: bounded runtime/product candidate that re-earns the donor runtime line on accepted `j2` workflow truth, from reference runtime through the OpenAI loopback service shell, without importing donor workflow truth wholesale
- Current candidate seam: `k1f` runtime/product restack closeout
- Current seam status: `K1 candidate implemented and verified / accepted baseline remains clean accepted j2 line`
- Seam risk: parser/doc-sync plus timing or environment-sensitive subprocess, file-I/O, and loopback-HTTP seam; repeated direct and repo-local reruns are required before any acceptance claim

## 3. Next lawful move

- Accepted answer on the current accepted `j2` line:
  - the verification/evidence restack train is accepted workflow truth
  - workflow and support surfaces now derive accepted baseline truth from this workstream ledger
  - package-level mediation evidence remains `insufficient`
  - mediation implementation remains blocked
- K1 branch-local answer:
  - the working branch now carries the reference runtime shell, bounded reference continuity, the OpenAI documented-host-event runtime shell, raw-transcript ingress shell, and loopback service shell
  - runtime program docs, phase gates, correspondence rows, runtime tests, fixtures, import smoke, and repo-local revalidation targets now exist on this branch
  - donor runtime code has been re-homed without importing donor workflow truth wholesale
- Next lawful move from this local candidate seam:
  - rerun the full K1 verification bundle plus repeated direct and repo-local runtime revalidation
  - accept/merge the K1 train or reject it explicitly
  - do not promote this branch-local implementation to accepted baseline truth without an explicit baseline update

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
- The accepted `j2` line is now the source of accepted workflow baseline truth until a later accepted baseline update lands.
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
