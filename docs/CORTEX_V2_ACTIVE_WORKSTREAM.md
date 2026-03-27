# Cortex v2 Active Workstream

Status: live workflow-state ledger for compaction-safe continuation.

This document records accepted baseline truth, current seam state, blocked moves, and acknowledged workspace noise.
It is workflow state only. It does not override the packet documents, implementation authority, phase gates, status notes, or correspondence.

## 1. Accepted baseline

- Accepted baseline branch: `codex/l1-live-validation`
- Accepted baseline commit: `8eb7f08`
- Accepted baseline state:
  - burden-axis re-audit remains accepted through the three thrash-host burden slices
  - package-level burden remains `insufficient`
  - mediation remains blocked / not justified
  - the verification/evidence restack train remains landed on the same product truth
  - the OpenAI host-realization cell now has a committed three-pair evidence series and `candidate_positive` cell-level signal for better host-specialized realization
  - package-level mediation evidence remains `insufficient`
  - lower visible burden remains unclaimed for host-realization
  - accepted workflow baseline truth is now normalized around the refreshed post-A1 live-model line
  - the reference runtime shell, bounded reference continuity, OpenAI documented-host-event runtime shell, raw-transcript ingress shell, loopback service shell, bounded outbound OpenAI host-control lane, and explicit executive allocation diagnostics remain accepted on the current line
  - the Gemini documented-host-event runtime shell, raw-transcript ingress shell, loopback service shell, and bounded outbound Gemini host-control lane remain accepted on the current line
  - the Claude documented-host-event runtime shell, raw-transcript ingress shell, loopback service shell, and bounded outbound Claude host-control lane remain accepted on the current line
  - refreshed live models on the current line are `claude-sonnet-4-6`, `gemini-2.5-pro`, and `gpt-5.4`
  - `R6`, `O5`, `G1`, `G2`, `G3`, `G4`, `A1`, `A2`, `A3`, and `A4` are landed on the current line
  - the next lawful big product-facing direction is L1 multi-host live validation
- Accepted baseline authority anchors:
  - `docs/CORTEX_V2_IMPLEMENTATION_STATUS_NOTE.md`
  - `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
  - `docs/CORTEX_V2_MEDIATION_JUSTIFICATION_NOTE.md`
  - `docs/CORTEX_V2_VERIFICATION_ERGONOMICS_MASTER_PLAN_0.md`

## 2. Current campaign and seam state

- Current campaign: `L1 multi-host live validation train`
- Current working branch at ledger update: `codex/l1-live-validation`
- Current branch role: branch-local L1 candidate over the accepted refreshed A1 line; newer local edits are not baseline truth until committed
- Current candidate seam: `L0/L1` live-validation preflight, capture harness, and first verdict pass
- Current seam status: `initial live evidence captured / partial and blocked on live auth-model alignment`
- Seam risk: timing or environment-sensitive evidence seam; repeated direct reruns and repeated repo-local entry-point reruns are required before any future closure claim

## 3. Next lawful move

- Current candidate answer after the first L1 evidence pass:
  - the toolchain is updated locally: `claude` `2.1.85`, `gemini` `0.35.2`, and `openai` `2.30.0`
  - the machine-readable preflight report exists at `docs/live_validation/preflight_report.json`
  - direct provider baseline capture exists for Claude, Gemini, and OpenAI with explicit blocker classes rather than silent failure
  - Cortex loopback-service plus host-control capture exists for Claude, Gemini, and OpenAI and fails honestly at the live auth boundary for current scope
  - the first comparator and verdict exist at `docs/live_validation/comparators/live_validation_comparison.{json,md}`
- Next lawful move:
  - open one bounded live-auth alignment seam that makes the provider CLI sessions and the current A4 / G4 / O4 live transports prove fresh credentials without private-account drift
  - choose a subscription-runnable Gemini live model if `gemini-2.5-pro` remains capacity-blocked in the provider CLI baseline path
  - rerun `make live-preflight`, `make live-provider-baselines`, `make live-cortex-host-control`, and `make live-compare` after alignment
  - only then decide whether a richer live-host capture seam is justified

## 4. Explicitly blocked moves

- Do not treat mixed local edits on the current working branch as accepted truth.
- Do not branch new work from archival `main`.
- Do not reopen `E6` verification-ergonomics helper work without a new explicit re-audit.
- Do not promote package-level mediation justification from current burden evidence.
- Do not let support-surface documents silently redefine packet or status authority.
- Do not treat a three-pair OpenAI host-realization closeout as permission for mediation implementation.
- Do not reinterpret a host-level `candidate_positive` cell as package-level justification.
- Do not import donor runtime workflow truth wholesale from `codex/c1-reference-continuation`, `codex/o1-openai-runtime-shell`, `codex/o2-openai-ingress-shell`, or `codex/o3-openai-service-shell`.
- Do not reopen K3 into new executive-allocation widening beyond the accepted current-scope law.
- Do not treat signed-in provider CLI sessions as equivalent to the API-key auth the current A4 / G4 / O4 live transports require.
- Do not shell out from the current runtime transports to provider CLIs without a separately scoped auth-alignment seam.
- Do not open support-memory runtime, mediation / `Q_t^{final}` experimentation, tools or tool-result submission, thinking blocks, multimodal payloads, runtime AUX activation, offline consolidation, or generic reward-learning doctrine from `L1`.
- Do not reinterpret the current live blockers as proof that lifecycle-first is architecturally wrong; the current evidence is about auth-model alignment, not packet failure.

## 5. Acknowledged worktree noise at ledger creation

- The accepted refreshed A1 line at `8eb7f08` is now the source of accepted workflow baseline truth until a later accepted baseline update lands.
- `docs/live_validation/` now contains generated evidence artifacts and summary files from the initial L1 pass; reruns are expected to overwrite those support artifacts.
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
