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
  - `E23 preservation-state machine`
- Product target:
  - give the shipped Cortex executive one minimal preservation/falsification state machine with lawful repair control on the OpenAI verified-work lane
- Surface:
  - `product` and `runtime-law`
- Direct executive payoff:
  - move the verified-work lane from failure-only repair into explicit preservation-aware executive control over trusted structure, falsified structure, lawful repair surface, and intervention budget
- Why this seam exists instead of a narrower product seam:
  - current Cortex law is still too post-hoc and too weak at representing preserved structure; that is the smallest direct product gap after E22
- Current seam status:
  - E22 is landed locally on `main` through the canonical close-session flow and the repo is now on an explicit E23 review branch because `start-session` is blocked until that ahead-of-origin `main` history is published or reconciled
  - current E23 candidate implementation now exists on this branch:
    - new shipped SRE preservation-state carriers and move law
    - OpenAI verified-work anchor activation plus preservation-state persistence
    - preservation-centered repair ticketing
    - lawful repair-surface narrowing on the repair turn
    - repair verification overlay on top of preserved first-attempt file maps
  - deterministic and repo-local proof is now green on this branch:
    - targeted runtime/correspondence/boundary bundle
    - `make -C lab revalidate-openai-host-control`
    - `tests/unit/test_cortex_conformance.py`
  - the branch is a verified review candidate, not accepted baseline truth
  - the earlier plan to close E23 with new OpenAI `service_api` acceptance reruns is no longer the active maintainer policy:
    - `service_api` spend is intentionally deferred for now
    - OpenAI `operator_cli` is the intended default proving lane for the next truth realignment
    - that operator-cli shift is not landed yet on this branch and must not be described as already accepted

## 4. Next lawful move

- keep the explicit E23 review branch finalized as a verified candidate with deterministic + repo-local proof already earned
- do not spend new OpenAI `service_api` acceptance cycles under the current policy
- open one explicit truth-realignment seam that:
  - changes the active OpenAI proving/default lane from historical `service_api` wording to `operator_cli`
  - updates the relevant docs, conformance/train-loop truth carriers, and acceptance procedure accordingly
  - keeps public product/runtime claims aligned with the actual shipped surface rather than pretending the operator-cli realization is already landed
- accept or reject E23 only after that policy-aligned proving lane is recorded truthfully and revalidated on its intended surface
- publication and reconciliation remain blocked on the local `main` ahead-of-origin state until the E22/E23 history is published or reconciled explicitly

## 5. Explicitly blocked moves

- Do not merge the parked E20/E21 preserved branch through E22.
- Do not widen E23 beyond the OpenAI verified-work realization.
- Do not reopen prompt shaping, basket overlays, or diagnostic modulators as runtime law.
- Do not change the thin OpenAI path when `work_contract` is absent.
- Do not widen retries beyond one bounded repair turn.
- Do not treat the current review branch as accepted baseline truth before publication/reconciliation.
- Do not claim E23 live acceptance on `service_api` while service spend is intentionally deferred by policy.
- Do not rewrite docs to call OpenAI `operator_cli` the accepted default lane until the conformance/runtime truth surfaces are explicitly realigned.

## 6. Acknowledged worktree noise

- Expected current-seam noise:
  - none expected beyond the owned E23 runtime/doc/test touch surface on `review/e23-preservation-state-machine`
