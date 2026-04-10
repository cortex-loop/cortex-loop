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
  - `E27 real-work replay proof`
- Product target:
  - turn the selected OpenAI `operator_cli` replay-bank cases into a tiny private proof surface that can test current Cortex behavior against real first-attempt failures without reopening the full broad watch
- Surface:
  - `internal`
- Direct executive payoff:
  - measure current Cortex lift on a frozen real-failure subset with a much smaller private proof loop before spending more live runtime on broad watches
- Why this seam exists instead of a narrower product seam:
  - the replay bank already exists; the missing move now is to prove or cut current Cortex behavior on that frozen subset without paying for the full broad output-quality surface
- Current seam status:
  - E22 is landed locally on `main` through the canonical close-session flow and the repo is now on an explicit review branch because `start-session` is blocked until that ahead-of-origin `main` history is published or reconciled
  - E23 remains implemented on this branch as verified product/runtime candidate state:
    - new shipped SRE preservation-state carriers and move law
    - OpenAI verified-work anchor activation plus preservation-state persistence
    - preservation-centered repair ticketing
    - lawful repair-surface narrowing on the repair turn
    - repair verification overlay on top of preserved first-attempt file maps
  - current E24 proving-default implementation still exists on top of that branch:
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
  - repeated direct OpenAI `operator_cli` conformance reruns remain clean on the three accepted verified-work packs:
    - bookmarks passed on attempt `1`
    - normalize-port passed on attempt `1`
    - feature-flags passed on attempt `1`
  - the repair-pressure proof surface exercised the preservation-aware repair branch on the accepted packs:
    - bookmarks direct repair-pressure reruns recovered cleanly twice after injected `output_invalid`
    - normalize-port recovered cleanly on the first direct repair-pressure rerun after injected `import_smoke_failed`
    - the second direct normalize-port repair-pressure rerun split with an unreproduced operator-resume payload-sanitization crash in `lab/live_openai_app_server_operator.py::_sanitize_payload()` during `wait_for_turn_completed()`
    - an immediate third normalize-port direct rerun recovered cleanly after the same injected `import_smoke_failed`
    - two fresh direct normalize-port repair-pressure reruns on 2026-04-10 both recovered cleanly after the same injected `import_smoke_failed`
    - feature-flags direct repair-pressure reruns recovered cleanly twice after injected `test_failed`
  - both canonical repo-local entrypoint reruns under `make -C lab live-openai-operator-repair-pressure` came back clean across all three accepted packs
  - the ordinary direct conformance guardrail reruns after repair-pressure remained clean on bookmarks, normalize-port, and feature-flags
  - the current E23 operator-cli keep/cut read now lands as `keep` on the current review line without widening shipping truth:
    - Cortex-base preservation-law proof is positive on the successful repair-pressure runs
    - authoritative artifact audits passed on every successful repair-pressure run
    - the earlier normalize-port operator-resume payload-sanitization crash did not recur on two fresh direct reruns and currently reads as unreproduced shared operator-proof-plumbing noise rather than preservation-law drift
  - the E25 internal runtime spend allocator now exists on this branch as a deterministic maintainer-only selector over:
    - `.cortex/live_validation/conformance/summary.latest.json`
    - `.cortex/live_validation/output_quality/summary.latest.json`
    - `.cortex/train_loops/*/summary.json`
    - this active workstream ledger
  - the allocator train output resolved the next runtime target:
    - train slug: `runtime-spend-allocator-openai`
    - artifact path: `.cortex/train_loops/runtime-spend-allocator-openai/summary.json`
    - human-readable note: `.cortex/train_loops/runtime-spend-allocator-openai/summary.md`
    - current recommended next train: `real-work-replay-pack-openai`
  - the E25 recommendation was grounded in current repo truth:
    - treat E23 as a local `keep` on the OpenAI `operator_cli` proving lane while leaving shipping truth unchanged
    - keep new OpenAI `service_api` spend deferred under the current policy
    - the accepted verified-work packs still pass on attempt `1`, so natural repair yield remains weak on the accepted line
    - the historical verified-work repair-yield train escalated because the accepted packs produced zero natural repair opportunities
    - the current broad OpenAI `operator_cli` output-quality watch is `env_blocked` / zero-lift and is not a good next runtime target
    - workflow-only publication/reconciliation closure remains useful but does not beat the next product-bearing replay-pack seam
  - the new E26 replay-pack miner now exists on this branch as a deterministic maintainer-only reducer over the current OpenAI output-quality artifact root:
    - train slug: `real-work-replay-pack-openai`
    - artifact path: `.cortex/train_loops/real-work-replay-pack-openai/summary.json`
    - human-readable note: `.cortex/train_loops/real-work-replay-pack-openai/summary.md`
    - recovered case file maps: `.cortex/train_loops/real-work-replay-pack-openai/cases/*/file_map.json`
  - the current replay-pack result on repo truth is:
    - extracted replayable cases: `5`
    - selected replay subset: `2`
    - framework coverage: `astro`, `react`
    - selected cases:
      - `astro_marketing_forms_v1`
      - `frontend_bugfix_cleanup_v1`
  - the miner is intentionally small and artifact-first:
    - it reads the current OpenAI output-quality summary plus the saved `seed/project_a` and `cortex/workspace/project_a` trees
    - it recovers changed-file maps from workspace diffs instead of trusting the failed summary payload's empty `changed_files`
    - it selects one highest-change replayable case per framework family to keep the next proof surface narrow
    - it does not add a new benchmark family, new product/runtime law, or new host scope
  - the new E27 replay-proof train now exists on this branch as a timing/env-sensitive maintainer-only proof seam over the selected replay subset:
    - train slug: `real-work-replay-proof-openai`
    - output target path: `.cortex/train_loops/real-work-replay-proof-openai/summary.json`
    - human-readable output target: `.cortex/train_loops/real-work-replay-proof-openai/summary.md`
    - private run root: `.cortex/train_loops/real-work-replay-proof-openai/runs`
  - the replay-proof seam was reduced after one oversized live attempt:
    - the first live replay-proof attempt reused the full output-quality arm set and spent time on `raw` and `tooling_only` even though the replay pack already preserved the baseline failure shapes
    - that oversized run produced two fast Astro failures (`raw`, `tooling_only`), both still `output_invalid`, while also surfacing the same `.vite` sandbox `EPERM` verification noise during model-chosen local checks
    - that spend shape was cut and the train was revised to run only `--arms cortex` against the frozen replay subset while keeping `--skip-latest-update`
  - the current E27 proof read is still unresolved:
    - deterministic proof is green for the reduced `cortex`-only train
    - a fresh reduced live replay-proof rerun on 2026-04-10 remained timing-heavy before the first completed Astro `cortex` attempt and was cut within the bounded turn budget
    - one direct private single-case rerun on `frontend_bugfix_cleanup_v1` completed end-to-end on 2026-04-10 without `env_blocked` and now serves as the first clean replay discriminator on the selected subset
    - that first React rerun still stayed `output_invalid` through the bounded repair turn:
      - attempt `1` returned summary prose outside the operator surface despite self-reporting passing local checks under `--configLoader runner`
      - attempt `2` returned `=== FILE:` blocks with `parse_error: operator completed without workspace edits`
    - one prompt-hardening revision on the maintainer-only operator replay prompt did not lift that result:
      - the second React rerun again completed without `env_blocked` and still stayed `output_invalid` through attempt `2`
      - the repair turn changed wording from file-block output to prose-only completion text, but still produced no persisted workspace edits
      - because the revision changed wording but not outcome, that prompt-hardening mechanism was cut and is not kept on this branch
    - the branch therefore carries the smaller replay-proof mechanism plus one clean React replay failure artifact, but no accepted keep/cut read yet on broader replay efficacy
  - the branch is still candidate truth only, not accepted baseline truth
  - historical accepted OpenAI `service_api` evidence remains recorded as product/runtime claim history
  - the active proving/default lane for new iteration is now OpenAI `operator_cli` on this branch, while historical accepted `service_api` evidence remains recorded as product/runtime claim history and not as the day-to-day proving default

## 4. Next lawful move

- use `.cortex/train_loops/real-work-replay-pack-openai/summary.json` as the next narrow proof target instead of the full broad output-quality watch
- keep the reduced `real-work-replay-proof-openai` train as the only maintained replay-proof seam
- use the completed React replay artifacts under `.cortex/train_loops/real-work-replay-proof-openai/runs/openai_operator_cli/run_20260410T093621+0000` and `run_20260410T094123+0000` as the current baseline evidence
- open one explicit localized corrective seam on shared OpenAI operator replay persistence / proof plumbing before spending more runtime on prompt micro-tweaks or reopening the full two-case replay proof
- keep replay proof private to `.cortex/train_loops/real-work-replay-proof-openai/runs` and keep the shared output-quality latest summary untouched
- keep E24 as the locally landed proving-default basis on this branch
- keep the successful repair-pressure artifacts as the current best evidence for E23 and stop spending runtime on broader watch surfaces by habit
- treat E23 as a local `keep` on the OpenAI `operator_cli` proving lane while leaving shipping truth unchanged
- if the normalize-port operator-resume payload-sanitization crash recurs later, open one explicit localized corrective seam on the shared OpenAI operator proof plumbing rather than reopening E23 law proof
- keep new OpenAI `service_api` spend deferred under the current policy
- publication and reconciliation remain blocked on the local accepted-history line until the landed history is published or reconciled explicitly, but that workflow-only closure now follows the recommended replay-pack seam

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
- Do not treat the clean repo-local entrypoint reruns as sufficient to erase the one split direct normalize-port repair-pressure failure.
- Do not reopen E23 broad watch surfaces by habit.
- Do not open a new `service_api` runtime-spend seam by habit while service spend remains deferred.
- Do not widen the next train into host expansion while the current product scope remains OpenAI-only.
- Do not open repeated-failure inhibition or carrier-inference trains before new evidence earns them.
- Do not let the allocator become product/runtime law, a second truth court, or a broader governance surface.
- Do not treat the full five-task OpenAI output-quality watch as the next proving surface now that the replay bank exists.
- Do not invent a new benchmark family or fixture tree when the replay miner can reuse the existing output-quality task packs and saved workspaces.
- Do not reopen `raw` or `tooling_only` replay arms in E27 now that the replay pack already preserves the baseline failure shapes.
- Do not treat the cut oversized replay-proof run or the cut timing-heavy `cortex`-only rerun as proof that replay efficacy is either earned or disproven.
- Do not add another replay-prompt micro-tweak on the React case; the first prompt-hardening revision changed wording but not outcome.

## 6. Acknowledged worktree noise

- Expected current-seam noise:
  - none expected beyond the owned E23/E27 runtime/doc/test touch surface on `review/e23-preservation-state-machine`
