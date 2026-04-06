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

- Current campaign: `R1 strategic reset: two-lane truth, thin runtime, and surface compression`
- Current working branch at ledger update: `codex/20260406-182719-r1-two-lane-reset`
- Current branch role: managed session branch from clean synced `main`; accepted baseline truth remains the clean synced `main` line
- Current candidate seam: `R1 two-lane truth reset`
- Current seam status:
  - reset slice is now implemented and verified on this managed session branch
  - code now classifies live evidence explicitly by:
    - `execution_surface = headless_cli | direct_api`
    - `evidence_role = watchlist | canonical_truth`
  - the Gemini `auto|minimal|wrapped` execution-flavor tooling is being retained only as operator-harness falsification infrastructure
  - operator-facing docs are now watchlist-language surfaces
  - service/API-facing docs are now canonical-truth surfaces, while remaining blocked honestly on current-machine auth

## 3. Next lawful move

- Land the reset slice on clean synced `main` with:
  - explicit two-lane truth language in the active workflow and live-validation support docs
  - harness summaries that expose `execution_surface` and `evidence_role`
  - docs-sync/tests aligned to the new truth model
- After branch closeout, the next bounded runtime move is:
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
