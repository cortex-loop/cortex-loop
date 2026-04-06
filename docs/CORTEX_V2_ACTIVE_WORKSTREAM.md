# Cortex v2 Active Workstream

Status: live workflow-state ledger for compaction-safe continuation.

This document records accepted baseline truth, current seam state, blocked moves, and acknowledged workspace noise.
It is workflow state only. It does not override the packet documents, implementation authority, phase gates, status notes, or correspondence.

## 1. Accepted baseline

- Accepted baseline branch: `main`
- Accepted baseline commit lookup: `git rev-parse HEAD` on clean synced `main`
- Accepted baseline note:
  - exact accepted-head hashes are intentionally not mirrored in repo-tracked support docs because they self-stale on the next accepted closure commit
- Accepted baseline state:
  - packet authority remains unchanged:
    - `docs/CORTEX_V2_CORE_2.md`
    - `docs/CORTEX_V2_SRE_2.md`
    - `docs/CORTEX_V2_AUX_2.md`
  - the tiny integrity core, contradiction discipline, and existing math-to-code traceability remain accepted
  - review branches such as `review/gemini-cause-proof` remain evidence only and are not accepted runtime truth
  - the repo is now operating under an explicit two-lane live-evidence contract:
    - `service_api` is the canonical runtime truth lane
    - `operator_cli` is a watchlist and exploratory-comparison lane
  - accepted operator/CLI watchlist status on the current line:
    - Claude: positive watchlist signal
    - Gemini: unresolved watchlist signal
    - OpenAI: positive watchlist signal
  - signed-in CLI/operator results remain useful for host watchlisting, packaging/confound detection, and falsification work
  - CLI/operator results alone do not earn canonical runtime truth
  - current machine service auth remains blocked:
    - `OPENAI_API_KEY`: missing
    - `ANTHROPIC_API_KEY`: missing
    - `GEMINI_API_KEY`: missing
  - no current-machine API truth anchor is yet re-earned
  - the strongest current Gemini recovery evidence remains branch-local and non-authoritative until re-earned under the reset contract

## 2. Current campaign and seam state

- Current campaign: `R1C closure train: reset reconciliation, watchlist demotion, and phase-gate truth`
- Current working branch at ledger update: `review/r1c-closure-train`
- Current branch role: explicit manual/review branch because local `main` is ahead of `origin/main`; accepted baseline truth remains the clean local `main` line
- Current candidate seam: `R1C reset closure`
- Current seam status:
  - the R1 reset remains the accepted baseline on local `main`
  - this review branch now reconciles downstream support truth so the reset cannot silently drift back into operator-first claims
  - compare and verdict support surfaces now read canonical runtime truth from `direct_api` first
  - headless-CLI operator evidence remains watchlist-only, with local-vs-accepted watchlist drift surfaced explicitly instead of collapsed into package truth
  - the operator-payoff support note/tooling is now demoted to historical/watchlist diagnostic status only
  - Section 7 live-validation phase-gate rows are now rebased to the two-lane truth contract rather than the older operator-first framing
  - deterministic closure checks and repeated current-machine reruns now agree on the same canonical-blocked/watchlist-only interpretation
  - the OpenAI automation probe now keeps `gpt-5.4` as the stronger continuity model while using `gpt-5.4-mini` for the cheaper `service_smoke` probe

## 3. Next lawful move

- Finalize and manually reconcile this review branch so the R1 reset closeout becomes the new local accepted line.
- After that closure lands, the next bounded runtime move is:
  - re-earn one direct-API truth anchor on a capable machine
  - first host: `openai`
  - second host: `claude` if auth is ready
  - keep `gemini` as watchlist-only until direct API/service auth exists
- Do not treat branch-local Gemini CLI positives as accepted truth.

## 4. Explicitly blocked moves

- Do not treat signed-in provider CLI sessions as canonical runtime truth.
- Do not let CLI-only positives promote accepted product/runtime claims.
- Do not let CLI-only negatives overturn a later re-earned API truth lane unless they reveal a direct contradiction in the canonical runtime path.
- Do not merge `review/gemini-cause-proof` or similar review branches as product-truth branches.
- Do not reopen mediation, AUX runtime widening, support-memory runtime, or broader doctrine work during this reset.
- Do not substitute more CLI cleverness for missing direct API/service auth.
- Do not shell out from service transports to provider CLIs.
- Do not treat current-machine auth absence as permission to fake service proof.
- Do not silently promote `minimal` execution flavor from falsification tooling into a product default.
- Do not add new control/accounting surfaces unless they change route choice, tool exposure, blockedness, or observable runtime outcome.
- Do not let accepted watchlist fallback rows silently inflate canonical-looking package summaries.
- Do not use the operator-payoff support note/tool as an active runtime-payoff closure surface.

## 5. Acknowledged worktree noise at ledger creation

- `.cortex/live_validation/` contains local-only generated evidence and is expected to churn across reruns.
- local dossier files were moved out of the repo before this seam so they do not count as acknowledged worktree noise here.
- re-read `git status --short --untracked-files=all` before opening any new seam; this summary is only the continuity reminder, not the canonical file list.

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
