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
    - Claude: positive staged-workspace conformance signal, with provider-overload env blocks still possible on full tri-brain reruns
    - Gemini: positive staged-workspace conformance signal
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
    - OpenAI `service_api`: conformant on three repeated targeted current reruns; bounded read-only workspace context now exposes the writable-file and test contract, and the shipping-default lane passes the bookmarks pack on attempt `1`
    - Claude `operator_cli`: no longer divergent on truthful staged-workspace runs; two focused reruns passed on attempt `1`, while repeated full tri-brain reruns hit Anthropic `529 overloaded_error` before structured output and therefore count as `env_blocked`, not protocol drift
    - Gemini `operator_cli`: conformant on the corrected current line; staged workspace truth removes the earlier `read_file` miss, and repeated full reruns now pass the bookmarks pack

## 2. Current campaign and seam state

- Current campaign: `P1 product-first reduction program`
- Current working branch at ledger update: `review/e7-verified-work-breadth-train`
- Current branch role: explicit manual/review branch for the E7 verified-work breadth train while the accepted baseline remains local `main`
- Current candidate seam: `E7 verified-work breadth train`
- Current seam status:
  - accepted baseline truth on local `main` now includes the C3B brutal closed-loop train method on top of the E6 OpenAI verified-work context slice
  - A0, P1C, S1, S1C, X1, X2, the first verified-work restoration slice, the Cortex-law / fast-train method slice, the verified-work neutralization / conformance-correction slice, the Claude operator workspace-truth slice, the OpenAI verified-work context slice, and the C3B brutal closed-loop train method are now accepted on local `main`
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
  - the accepted next-seam correction recorded in `docs/CORTEX_V2_EXECUTIVE_RESTORATION_NOTE.md` has now landed on the accepted OpenAI realization:
    - keep the X1/X2 product simplification
    - cut prompt-shaping and benchmark-local executive control as product directions
    - restore one tiny runtime-native executive loop for larger tasks
  - the first verified-work restoration slice now lands:
    - shared `WorkContract`, `VerificationOutcome`, and `choose_verified_work_followup()` law
    - optional `work_contract` activation on the OpenAI host-control family
    - runtime-native external verification binding
    - one bounded repair turn on the OpenAI verified-work path
    - one bounded read-only workspace-context attachment on the OpenAI verified-work service lane
  - the accepted thin `O4` path remains unchanged when `work_contract` is absent
  - the `O4R` verified-work row now lands:
    - deterministic coverage and repo-local revalidation are landed
    - three repeated targeted OpenAI bookmarks reruns now pass on attempt `1`
    - the landed lane remains explicitly outside canonical-anchor proof
  - the active Cortex-law conformance method now lands:
    - one explicit `Train Charter` requirement for long trains
    - one explicit `build -> test -> iterate -> cut` default loop
    - one tri-brain conformance harness on the active bookmarks verified-work contract pack
    - one explicit divergence taxonomy: `cortex_law`, `brain_wiring`, `surface_wiring`, `env_blocked`
    - one corrected current-line reading where the OpenAI shipping-default lane now promotes on repeated targeted reruns, Gemini remains conformant, and Claude no longer counts as divergent when Anthropic overload returns a provider-side block instead of structured output
  - the active brutal closed-loop train method is now accepted on local `main` and remains the operating method for current review-branch work:
    - baseline result, primary metric, guardrail metric, iteration budget, rollback surface, and escalation-trigger fields to long-train charters
    - one explicit loop-class split: `deterministic`, `shared verification-plumbing`, `timing/env-sensitive`
    - one explicit per-iteration decision law: `promote`, `revise`, `cut`, `escalate`
    - one thin maintainer-only recorder at `tools/cortex_train_loop.py`
    - one conformance-summary truth pilot that records baseline, candidate proof, and final decision under `.cortex/train_loops/`
    - one conformance-harness correction where `summary.latest` only publishes from full tri-brain runs and can be reconciled to the latest surviving full run that matches accepted `CT2` decision
  - shipping truth remains OpenAI-first on the service lane
  - Claude remains outside the accepted shipping default, but Claude is no longer treated as generic backlog for Cortex-law conformance work
  - Gemini remains outside the accepted shipping default, but Gemini is no longer treated as generic backlog for Cortex-law conformance work
  - headless-CLI operator evidence remains watchlist-only even when conformance is positive; it does not widen shipping truth or canonical runtime proof
  - the older local `review/*` backlog is now archived to local `archive/review--*` tags and removed; full repo hygiene remains partial until `origin/main` reconciliation because local `main` is ahead
  - the accepted conformance-summary truth pilot on local `main` records:
    - baseline drift where `summary.latest` referenced missing artifacts and a stale `fix_wiring_only` decision
    - one clean full tri-brain rerun under `.cortex/live_validation/conformance/run_20260408T074128+0000`
    - one reconciled `summary.latest` state where OpenAI, Claude, and Gemini are all conformant and the shipping-default decision is `promote`
    - `CT2` therefore re-earned on the current line
  - the current E7 breadth slice on this review branch now adds:
    - one second explicit verified-work profile `python_workspace_pytest_port_fix_v1` over the existing `project_template` normalize-port task
    - one second contract pack `verified_work_normalize_port_v1` in the conformance harness
    - one bookmarks-preserving rule where `summary.latest` remains anchored to `verified_work_bookmarks_v1` and normalize-port breadth writes only explicit per-pack artifacts
    - one product-facing breadth train entry `verified-work-breadth-openai` in `tools/cortex_train_loop.py`
    - one localized verifier-install correction where the bounded workspace venv now installs `-e .[test] pytest`, keeping the existing bookmarks pack lawful while making the normalize-port verifier runnable
    - two repeated targeted OpenAI reruns where the bookmarks pack remains conformant and the normalize-port pack now passes on attempt `1`
    - one explicit normalize-port tri-brain guardrail rerun under `.cortex/live_validation/conformance/run_20260408T083436+0000` where OpenAI `service_api` is conformant, Claude `operator_cli` recovers after one lawful repair, Gemini `operator_cli` is conformant, and the guardrail decision remains `promote`
  - this E7 slice is landed on the current review branch and is not yet accepted on local `main`

## 3. Next lawful move

- No active verified-work shipping-gap seam remains on the accepted local `main` line.
- The accepted executive-restoration correction is now landed on the current OpenAI realization.
- While this explicit review branch remains open, the next lawful move is:
  - manually merge or deliberately reject the E7 review branch before opening another runtime/product seam
  - keep accepted-baseline truth separate from the review-branch candidate state
- After this E7 slice is accepted, later runtime/product seams should default to:
  - write the `Train Charter` first
  - record one baseline result before the first edit or candidate proof run
  - choose exactly one primary metric and one guardrail metric
  - lock one iteration budget, rollback surface, and escalation-trigger set
  - define the Cortex invariant before touching wiring
  - choose the fastest proving wiring and one tiny runnable contract pack
  - run tri-brain conformance on OpenAI, Claude, and Gemini
  - run the exact proof set
  - compare the candidate result against the baseline
  - end each iteration in exactly one of `promote`, `revise`, `cut`, or `escalate`
  - keep the landed `O4R` path stable before opening any new Cortex-law or host-scope seam
  - keep Claude in the `env_blocked` bucket when Anthropic overload prevents structured output; that is provider availability noise, not a new wiring or law failure
  - keep Gemini in the `conformant` bucket on the staged-workspace operator surface rather than reopening Gemini wiring prematurely
  - keep the default thin path unchanged and keep the landed verified-work lane outside canonical-anchor proof
  - keep repeated-failure inhibition and automatic carrier selection deferred until new evidence earns them
  - open any later shipping-truth widening beyond OpenAI only through an explicit separate host shipping train
- After this E7 slice is accepted, bookmarks should remain the accepted `CT2` anchor pack unless a later deliberate breadth-closure move says otherwise.
- After this E7 slice is accepted, the next product-facing move should be another bounded breadth or value slice rather than another governance-only train.
- Keep shipping-truth widening separate from conformance work:
  - `claude` may be conformance-required on `operator_cli` before any later Claude shipping train opens
  - `gemini` may be conformance-required on its strongest native surface before any later Gemini shipping train opens
- Keep `origin/main` reconciliation as separate workflow hygiene rather than active product/support closure.
- Open any later host expansion only through an explicit separate train.
- Do not treat operator/CLI positives from Claude or Gemini as service-lane shipping truth.

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
- Do not promote the landed `O4R` verified-work lane into canonical-anchor proof without a separate evidence-earning move.
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
