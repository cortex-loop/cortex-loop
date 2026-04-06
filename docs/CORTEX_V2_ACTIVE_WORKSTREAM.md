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
  - current machine service auth now reads:
    - `OPENAI_API_KEY`: ready
    - `ANTHROPIC_API_KEY`: missing
    - `GEMINI_API_KEY`: missing
  - the accepted product/runtime claim is now explicitly OpenAI-only on the canonical direct-API lane
  - one current-machine API truth anchor is now re-earned for current OpenAI-only product scope
  - the shared `canonical_anchor` direct-API suite remains implemented for `claude` and `openai`, but only `openai` is in the accepted current product scope
  - the strongest current Gemini recovery evidence remains branch-local and non-authoritative until re-earned under the reset contract

## 2. Current campaign and seam state

- Current campaign: `P1 product-first reduction program`
- Current working branch at ledger update: `main`
- Current branch role: accepted resting line after the S1 OpenAI-only scope narrowing seam
- Current candidate seam: `X1 OpenAI-only product-runtime compression`
- Current seam status:
  - A0 is now accepted on local `main`
  - the explicit `current|canonical_anchor` direct-API service suites are accepted on the current line
  - the OpenAI service spend split remains explicit:
    - `service_smoke` uses `gpt-5.4-mini`
    - `canonical_anchor` scenarios use `gpt-5.4`
  - the OpenAI direct-API `canonical_anchor` suite is now repeat-stably positive on the current machine through three positive current-machine `canonical_anchor` cycles:
    - `pass_minimal`
    - `truth_gap` with `truthful_incomplete`
    - `restart_continuity`
  - the accepted canonical provider scope is now `openai` only
  - compare/verdict logic now computes current-scope canonical truth from the declared `canonical_anchor` provider scope rather than every auth-ready provider
  - `python3 tools/live_compare.py` now reports:
    - `canonical runtime truth is re-earned for current scope`
    - `direct_api canonical truth is re-earned for current scope on openai`
  - Claude canonical-suite plumbing remains implemented, but Claude is now outside the accepted current product scope and stays frozen as future host-expansion backlog
  - Gemini remains canonical-lane out of scope and watchlist-only until its direct API lane is opened deliberately
  - headless-CLI operator evidence remains watchlist-only, with Gemini local-vs-accepted drift surfaced explicitly rather than promoted into runtime truth

## 3. Next lawful move

- Open `X1` as an OpenAI-only product-runtime compression seam on clean `main`.
- Keep `claude` and `gemini` as future host-expansion backlog only:
  - `claude` retains dormant shared `canonical_anchor` plumbing for a later explicit host-expansion train
  - `gemini` remains watchlist-only until direct API/service auth exists and a separate host-expansion train is opened
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
- Do not widen accepted current product scope beyond OpenAI without a separate host-expansion train.
- Do not spend on Claude or Gemini service proof while the accepted product scope is intentionally OpenAI-only.
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
