# Cortex v2 Active Workstream

Surface: internal

Status: live workflow-state ledger for compaction-safe continuation.

This ledger records accepted baseline truth, current seam state, blocked moves, and acknowledged workspace noise.
It is workflow state only. It does not override the packet documents, implementation authority, phase gates, status notes, or correspondence.

## 1. Accepted baseline

- Accepted baseline branch: `main`
- Accepted baseline note:
  - the accepted product remains the `cortex` package
  - the shipped runtime claim remains OpenAI-first
  - the proven executive value still comes from the tiny integrity core plus the verified-work loop
  - diagnostics, train loops, graders, causal maps, dynamics atlases, and workflow ledgers are not the product
  - local `main` now includes the landed E22 mission-lock and surface-separation seam and is ahead of `origin/main` pending publication
  - historical accepted verified-work evidence on local `main` still records OpenAI `service_api` as the proving-default line, but current maintainer policy now defers further service spend and treats an OpenAI `operator_cli` proving-default realignment as the next truth-update seam rather than the current accepted state
- Authority anchors:
  - `docs/CORTEX_V2_CORE_2.md`
  - `docs/CORTEX_V2_SRE_2.md`
  - `docs/CORTEX_V2_AUX_2.md`
  - `docs/internal/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
  - `docs/internal/CORTEX_V2_PHASE_GATES_2.md`
  - `docs/internal/V1_CODE_PORT_DETERMINATION.md`
  - `docs/internal/CORTEX_V2_MATH_TO_CODE_CORRESPONDENCE.md`

## 2. Parked lab evidence

- Parked branch:
  - `maint/preserved-20260409-235722-e20-e21-preclose`
- Parked evidence status:
  - unresolved lab evidence only
  - not accepted baseline truth
  - not product truth
  - E20 remains unresolved timing/env-sensitive watchlist evidence
  - E21 remains implemented-but-blocked lab machinery

## 3. Current seam

- Current working branch:
  - `review/e23-preservation-state-machine`
- Current candidate seam:
  - `E23 OpenAI operator_cli keep/cut train`
- Product target:
  - determine whether the preservation-state executive slice survives honest repeated OpenAI `operator_cli` proof as a CLI-proved candidate without changing the shipped OpenAI product/runtime claim
- Surface:
  - `internal`, `lab`, and live proving
- Direct executive payoff:
  - determine whether Cortex's preservation-aware repair law adds real executive value on the affordable native OpenAI proving lane before any wider product/runtime move
- Why this seam exists instead of a narrower product seam:
  - E23 is already implemented and E24 already moved the proving defaults; the missing truth is whether the preserved-structure repair law earns a keep/cut reading on the active OpenAI operator lane
- Current seam status:
  - E22 is landed locally on `main` through the canonical close-session flow and the repo is now on an explicit review branch because `start-session` is blocked until that ahead-of-origin `main` history is published or reconciled
  - E23 remains implemented on this branch as a verified product/runtime candidate:
    - new shipped SRE preservation-state carriers and move law
    - OpenAI verified-work anchor activation plus preservation-state persistence
    - preservation-centered repair ticketing
    - lawful repair-surface narrowing on the repair turn
    - repair verification overlay on top of preserved first-attempt file maps
  - current E24 proving-default implementation now exists on top of that branch:
    - `ContractPack` and conformance summaries now split `product_runtime_claim` from `active_proving_default`
    - OpenAI conformance now has a real `operator_cli` runner with one resumable repair turn
    - `strongest_native_surface("openai", ...)` now defaults to `operator_cli`
    - OpenAI output-quality defaults now target `operator_cli`
    - OpenAI train-loop proof wiring now targets the operator-cli proving lane
    - `make -C lab revalidate-openai-operator-cli` is now the canonical repo-local proving loop for OpenAI iteration
  - deterministic and repo-local proof is green on this branch:
    - `tests/unit/test_cortex_conformance.py`
    - `tests/unit/test_cortex_train_loop.py`
    - `tests/unit/test_cortex_output_quality.py`
    - `tests/unit/test_live_openai_app_server_operator.py`
    - `tests/internal/test_docs_boundary.py`
    - `tests/internal/test_workflow_boundary.py`
    - `make -C lab revalidate-openai-operator-cli`
    - `make -C lab revalidate-openai-host-control`
  - the branch now also carries one maintainer-only OpenAI `operator_cli` repair-pressure proof surface:
    - the OpenAI operator-cli conformance repair path now reissues a narrowed repair contract and verifies attempt `2` over the preserved first-attempt file map
    - `python3 lab/cortex_conformance.py --mode repair-pressure --brain openai --contract-pack <accepted-pack>` now forces one verifier-visible repair case on the accepted packs without widening Cortex law
    - `make -C lab revalidate-openai-operator-repair-pressure` is the deterministic proof gate for that surface
    - `make -C lab live-openai-operator-repair-pressure` is the canonical live proof entry point
  - repeated direct OpenAI `operator_cli` conformance reruns are now clean on the three accepted verified-work packs:
    - bookmarks passed twice on attempt `1`
    - normalize-port passed twice on attempt `1`
    - feature-flags passed twice on attempt `1`
  - that direct conformance proof did **not** exercise the preservation-aware repair branch on the accepted packs because every repeated rerun passed on attempt `1`
  - one full OpenAI `operator_cli` output-quality watch run under `.cortex/live_validation/output_quality/openai_operator_cli/run_20260410T034643+0000/summary.json` did surface larger-task repair opportunities on the broader lab surface, but it finished `env_blocked` with all arms at `0` objective passes, all arms at `0` hidden-quality passes, and only pairwise ties
  - the current E23 operator-cli keep/cut read is therefore `partial` / `env-sensitive`:
    - no deterministic Cortex-base preservation-law bug was reproduced
    - no deterministic OpenAI realization-wiring bug was reproduced
    - but the authoritative accepted packs did not exercise repair and the broader watch surface did not close cleanly enough to promote E23 to CLI-proved candidate
  - the branch is still candidate truth only, not accepted baseline truth
  - historical accepted OpenAI `service_api` evidence remains recorded as product/runtime claim history
  - the active proving/default lane for new iteration is now OpenAI `operator_cli` on this branch, while historical accepted `service_api` evidence remains recorded as product/runtime claim history and not as the day-to-day proving default

## 4. Next lawful move

- keep new OpenAI `service_api` spend deferred under the current policy
- do not promote E23 to CLI-proved candidate yet
- keep E24 as the locally landed proving-default basis on this branch
- the next proof step for E23 is now explicit, not hypothetical:
  - run `make -C lab live-openai-operator-repair-pressure`
  - repeat the three repair-pressure cases until they classify cleanly as keep, cut, or env-sensitive
- publication and reconciliation remain blocked on the local `main` ahead-of-origin state until the landed history is published or reconciled explicitly

## 5. Explicitly blocked moves

- Do not merge the parked E20/E21 preserved branch through E22.
- Do not widen E23 beyond the OpenAI verified-work realization.
- Do not reopen prompt shaping, basket overlays, or diagnostic modulators as runtime law.
- Do not change the thin OpenAI path when `work_contract` is absent.
- Do not widen retries beyond one bounded repair turn.
- Do not treat the current review branch as accepted baseline truth before publication/reconciliation.
- Do not claim E23 live acceptance on `service_api` while service spend is intentionally deferred by policy.
- Do not rewrite public docs to call OpenAI `operator_cli` the shipped product/runtime lane.
- Do not describe the historical `service_api` evidence as if it still governs day-to-day iteration after E24 is accepted.
- Do not treat attempt-1-only conformant accepted packs as proof that the preservation-aware repair branch itself is earned.
- Do not use the `env_blocked` operator output-quality watch run as substitute law proof for E23.

## 6. Acknowledged worktree noise

- Expected current-seam noise:
  - none expected beyond the owned E23 runtime/doc/test touch surface on `review/e23-preservation-state-machine`
