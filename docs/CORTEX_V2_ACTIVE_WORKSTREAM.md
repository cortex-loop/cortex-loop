# Cortex v2 Active Workstream

Status: live workflow-state ledger for compaction-safe continuation.

This document records accepted baseline truth, current seam state, blocked moves, and acknowledged workspace noise.
It is workflow state only. It does not override the packet documents, implementation authority, phase gates, status notes, or correspondence.

## 1. Accepted baseline

- Accepted baseline branch: `main`
- Accepted baseline commit lookup: `git rev-parse HEAD` on the accepted local `main` line
- Accepted baseline note:
  - exact accepted-head hashes are intentionally not mirrored in repo-tracked support docs because they self-stale on the next accepted closure commit
- Accepted baseline state:
  - packet authority remains unchanged:
    - `docs/CORTEX_V2_CORE_2.md`
    - `docs/CORTEX_V2_SRE_2.md`
    - `docs/CORTEX_V2_AUX_2.md`
  - the tiny integrity core, contradiction discipline, and existing math-to-code traceability remain accepted
  - archived evidence such as `archive/review--gemini-cause-proof` remains evidence only and is not accepted runtime truth
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
- Current working branch at ledger update: `review/x2-openai-support-eval-compression`
- Current branch role: candidate support/eval compression seam over the accepted X1 OpenAI-only product-runtime line
- Current candidate seam: `X2 OpenAI-only support/eval compression`
- Current seam status:
  - A0, P1C, S1, S1C, and X1 are now accepted on local `main`
  - X2 is implemented on this review branch only and is not accepted baseline truth yet
  - the explicit `current|canonical_anchor` direct-API service suites remain accepted on the current line
  - the OpenAI service spend split remains explicit:
    - `service_smoke` uses `gpt-5.4-mini`
    - `canonical_anchor` scenarios use `gpt-5.4`
  - the OpenAI direct-API `canonical_anchor` suite remains repeat-stably re-earned on the current machine; exact cycle count is local-artifact truth under `.cortex/live_validation/automation/openai/service/`
  - the stable current-scenario reading remains:
    - `pass_minimal`
    - `truth_gap` with `truthful_incomplete`
    - `restart_continuity`
  - the accepted canonical provider scope remains `openai` only
  - the accepted OpenAI-only product path now runs on:
    - direct API transport
    - one compact `openai_product_journal` continuation carrier
    - one explicit OpenAI-only decision table
    - one exact outward `decision + journal` projection
  - the accepted OpenAI product path no longer transits reference-soft-control selection, allocation diagnostics, or operator-routing/modulator surfaces as product-critical truth
  - `python3 tools/live_compare.py` continues to report:
    - `canonical runtime truth is re-earned for current scope`
    - `direct_api canonical truth is re-earned for current scope on openai`
  - the active current-line proof bundle on this branch is now compressed to:
    - `python3 tools/live_preflight.py --skip-updates`
    - `python3 tools/live_cortex_host_control.py --lane automation --provider openai --suite current`
    - `python3 tools/live_cortex_host_control.py --lane automation --provider openai --suite canonical_anchor`
    - `python3 tools/live_compare.py`
    - deterministic support checks in `tests/unit/test_live_validation_tools.py`, `tests/unit/test_verification_docs_sync.py`, `tests/unit/test_correspondence_sre.py`, and `tests/unit/test_import_smoke.py`
  - retained operator/watchlist tools stay callable as diagnostics, but they no longer define the active current-line closure path
  - `O5`-`O8` remain landed as historical/reference evidence only; they are no longer the accepted OpenAI-only product runtime after X1
  - Claude canonical-suite plumbing remains implemented, but Claude stays outside the accepted current product scope as future host-expansion backlog
  - Gemini remains canonical-lane out of scope and watchlist-only until its direct API lane is opened deliberately
  - headless-CLI operator evidence remains watchlist-only, with Gemini local-vs-accepted drift surfaced explicitly rather than promoted into runtime truth
  - the older local `review/*` backlog is now archived to local `archive/review--*` tags and removed; full repo hygiene remains partial until `origin/main` reconciliation because local `main` is ahead

## 3. Next lawful move

- Verify and close `X2` from this review branch onto the accepted local `main` line if reruns stay clean.
- Keep `claude` and `gemini` as future host-expansion backlog only:
  - `claude` retains dormant shared `canonical_anchor` plumbing for a later explicit host-expansion train
  - `gemini` remains watchlist-only until direct API/service auth exists and a separate host-expansion train is opened
- Keep `origin/main` reconciliation as separate workflow hygiene rather than active product/support closure.
- Do not treat branch-local Gemini CLI positives as accepted truth.

## 4. Explicitly blocked moves

- Do not treat signed-in provider CLI sessions as canonical runtime truth.
- Do not let CLI-only positives promote accepted product/runtime claims.
- Do not let CLI-only negatives overturn a later re-earned API truth lane unless they reveal a direct contradiction in the canonical runtime path.
- Do not promote archived Gemini recovery evidence such as `archive/review--gemini-cause-proof` into accepted product/runtime truth.
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
