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
  - when a seam changes Cortex law, the repo now distinguishes four truths explicitly:
    - `Cortex truth` — the invariant Cortex law
    - `brain-wiring truth` — how OpenAI, Claude, and Gemini attach to that law
    - `conformance truth` — how faithfully each brain/surface realizes that law
    - `shipping truth` — which realization is the current product default
  - shipping truth may remain narrower than development conformance truth
  - for Cortex-law development, the strongest available native surface on each brain is conformance-required even when shipping truth remains narrower
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
  - the active verified-work conformance reading on the bookmarks contract pack is:
    - OpenAI `service_api`: partial on the corrected current run; the bounded repair path executed but still finished `test_failed`, so both conformance truth and shipping truth remain partial
    - Claude `operator_cli`: divergent on the corrected current run because the repair attempt did not complete cleanly and the final result still fell back to raw output and `output_invalid`
    - Gemini `operator_cli`: partial on the corrected current run; structured `json_object` extraction now works, import smoke passes, and the result still finishes `test_failed`, so the earlier false `output_invalid` divergence is removed
  - the strongest current Gemini recovery evidence remains branch-local and non-authoritative until re-earned under the reset contract

## 2. Current campaign and seam state

- Current campaign: `P1 product-first reduction program`
- Current working branch at ledger update: `main`
- Current branch role: accepted resting line after the E4 verified-work neutralization and conformance-correction slice
- Current candidate seam: `none active`
- Current seam status:
  - A0, P1C, S1, S1C, X1, X2, the first verified-work restoration slice, the Cortex-law / fast-train method slice, and the verified-work neutralization / conformance-correction slice are now accepted on local `main`
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
  - the active current-line proof bundle on the accepted line is now compressed to:
    - `python3 tools/live_preflight.py --skip-updates`
    - `python3 tools/live_cortex_host_control.py --lane automation --provider openai --suite current`
    - `python3 tools/live_cortex_host_control.py --lane automation --provider openai --suite canonical_anchor`
    - `python3 tools/live_compare.py`
    - deterministic support checks in `tests/unit/test_live_validation_tools.py`, `tests/unit/test_verification_docs_sync.py`, `tests/unit/test_correspondence_sre.py`, and `tests/unit/test_import_smoke.py`
  - retained operator/watchlist tools stay callable as diagnostics, but they no longer define the active current-line closure path
  - `O5`-`O8` remain landed as historical/reference evidence only; they are no longer the accepted OpenAI-only product runtime after X1
  - the accepted next-seam correction recorded in `docs/CORTEX_V2_EXECUTIVE_RESTORATION_NOTE.md` has now landed partially on the accepted line:
    - keep the X1/X2 product simplification
    - cut prompt-shaping and benchmark-local executive control as product directions
    - restore one tiny runtime-native executive loop for larger tasks
  - the first verified-work restoration slice now lands:
    - shared `WorkContract`, `VerificationOutcome`, and `choose_verified_work_followup()` law
    - optional `work_contract` activation on the OpenAI host-control family
    - runtime-native external verification binding
    - one bounded repair turn on the OpenAI verified-work path
  - the accepted thin `O4` path remains unchanged when `work_contract` is absent
  - the new `O4R` verified-work row remains partial:
    - deterministic coverage and repo-local revalidation are landed
    - local larger-task value lift is not yet re-earned repeat-stably
  - the active Cortex-law conformance method now lands:
    - one explicit `Train Charter` requirement for long trains
    - one explicit `build -> test -> iterate -> cut` default loop
    - one tri-brain conformance harness on the active bookmarks verified-work contract pack
    - one explicit divergence taxonomy: `cortex_law`, `brain_wiring`, `surface_wiring`, `env_blocked`
    - one corrected verified-work audit result of `next_decision = fix_wiring_only`; Gemini no longer carries a false raw-JSON-wrapper divergence after structured `json_object` extraction, while Claude remains the only divergent surface
  - shipping truth remains OpenAI-first on the service lane
  - Claude remains outside the accepted shipping default, but Claude is no longer treated as generic backlog for Cortex-law conformance work
  - Gemini remains outside the accepted shipping default, but Gemini is no longer treated as generic backlog for Cortex-law conformance work
  - headless-CLI operator evidence remains watchlist-only, with Gemini local-vs-accepted drift surfaced explicitly rather than promoted into runtime truth
  - the older local `review/*` backlog is now archived to local `archive/review--*` tags and removed; full repo hygiene remains partial until `origin/main` reconciliation because local `main` is ahead

## 3. Next lawful move

- No active verified-work restoration seam remains on the accepted local `main` line.
- The accepted executive-restoration correction is now partially landed on the current line.
- If a later runtime/product seam opens, the next lawful move is:
  - write the `Train Charter` first
  - define the Cortex invariant before touching wiring
  - choose the fastest proving wiring and one tiny runnable contract pack
  - run tri-brain conformance on OpenAI, Claude, and Gemini
  - classify divergence as `cortex_law`, `brain_wiring`, `surface_wiring`, or `env_blocked`
  - because the corrected current run leaves Claude as the only divergent surface, open the next seam as one narrower Claude wiring-correction train before touching Cortex law again
  - keep OpenAI and Gemini in the `partial` bucket as real brain-wiring evidence rather than treating either as a new law failure
  - keep the default thin path unchanged while `O4R` remains partial
  - keep repeated-failure inhibition and automatic carrier selection deferred until value is earned
  - cut back rather than widen if the verified-work path continues to fail without clear lift or better conformance
- Keep shipping-truth widening separate from conformance work:
  - `claude` may be conformance-required on `operator_cli` before any later Claude shipping train opens
  - `gemini` may be conformance-required on its strongest native surface before any later Gemini shipping train opens
- Keep `origin/main` reconciliation as separate workflow hygiene rather than active product/support closure.
- Open any later host expansion only through an explicit separate train.
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
- Do not treat Claude or Gemini as generic backlog-only when the active seam changes Cortex law; classify them as `conformant`, `partial`, `divergent`, `unwired`, or `env_blocked` instead.
- Do not spend on Claude or Gemini service proof while the accepted product scope is intentionally OpenAI-only unless an explicit shipping train opens.
- Do not silently promote `minimal` execution flavor from falsification tooling into a product default.
- Do not add new control/accounting surfaces unless they change route choice, tool exposure, blockedness, or observable runtime outcome.
- Do not let accepted watchlist fallback rows silently inflate canonical-looking package summaries.
- Do not use the operator-payoff support note/tool as an active runtime-payoff closure surface.
- Do not treat benchmark-local repair control as accepted product behavior.
- Do not reopen prompt shaping or hidden build-brief doctrine as a product direction.
- Do not solve larger-task repair by adding a second large task-specific subsystem when one optional work contract would suffice.
- Do not promote the partial `O4R` verified-work lane into canonical-anchor proof before repeat-stable live lift is earned.
- Do not let one host or one surface redefine Cortex law by itself.

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
