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
  - `E24 OpenAI operator_cli proving-default realignment`
- Product target:
  - make OpenAI `operator_cli` the active proving/default lane for development, conformance, and train-loop iteration without changing the shipped OpenAI product/runtime claim
- Surface:
  - `internal` and `lab`
- Direct executive payoff:
  - keep development and iteration aimed at the affordable native OpenAI lane while preserving truthful product/runtime boundaries around the shipped executive layer
- Why this seam exists instead of a narrower product seam:
  - current policy defers new OpenAI `service_api` spend, but the lab still points default proving and train logic at that lane; the repo must stop drifting between product truth and proving truth before the next live executive iteration
- Current seam status:
  - E22 is landed locally on `main` through the canonical close-session flow and the repo is now on an explicit review branch because `start-session` is blocked until that ahead-of-origin `main` history is published or reconciled
  - E23 remains implemented on this branch as a verified product/runtime candidate:
    - new shipped SRE preservation-state carriers and move law
    - OpenAI verified-work anchor activation plus preservation-state persistence
    - preservation-centered repair ticketing
    - lawful repair-surface narrowing on the repair turn
    - repair verification overlay on top of preserved first-attempt file maps
  - current E24 candidate implementation now exists on top of that branch:
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
  - the branch is still candidate truth only, not accepted baseline truth
  - historical accepted OpenAI `service_api` evidence remains recorded as product/runtime claim history
  - the active proving/default lane for new iteration is now OpenAI `operator_cli` on this branch, while historical accepted `service_api` evidence remains recorded as product/runtime claim history and not as the day-to-day proving default

## 4. Next lawful move

- keep new OpenAI `service_api` spend deferred under the current policy
- if no adversarial review finding remains, accept E24 locally as the proving-default realignment seam
- after E24 lands locally, the next live proving move is repeated OpenAI `operator_cli` conformance/output-quality reruns on the bookmarks, normalize-port, and feature-flags packs rather than reopening `service_api` by habit
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

## 6. Acknowledged worktree noise

- Expected current-seam noise:
  - none expected beyond the owned E23 runtime/doc/test touch surface on `review/e23-preservation-state-machine`
