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
  - `codex/20260410-020933-e22-mission-lock-surface-separation`
- Current candidate seam:
  - `E22 mission lock and surface separation`
- Product target:
  - make the shipped Cortex identity unmistakable as the executive layer, not the proving apparatus
- Surface:
  - `internal` and `repo-boundary`
- Direct executive payoff:
  - reduce internal goal drift so future seams are forced to justify themselves against shipped executive improvement or a direct product blocker
- Why this seam exists instead of a narrower product seam:
  - the repo has repeatedly drifted into treating lab and governance surfaces as Cortex itself; that confusion is now a product blocker
- Current seam status:
  - repo surface split is closure-ready on this branch:
    - `cortex/` is the product package
    - `experimental/` is the public non-shipping host/runtime surface
    - `lab/` is the evaluation and proving surface
    - `internal/` is the workflow and governance surface
  - public/package boundary is now explicit and verified in:
    - `pyproject.toml`
    - root `README.md`
    - `docs/CORTEX_PRODUCT_CHARTER.md`
    - `docs/CORTEX_PRODUCT_BOUNDARY.md`
    - `docs/README.md`
  - canonical split surfaces now work from their new homes:
    - `internal/workflow/repo_workflow.py`
    - `lab/Makefile`
    - `lab/*`
  - one-cycle compatibility shims are still available and verified:
    - `scripts/repo_workflow.py`
    - `tools/*`
  - mission-lock enforcement is active in:
    - `AGENTS.md`
    - boundary tests
    - public/package/import-surface checks
    - internal packaging-boundary checks

## 4. Next lawful move

- Accept or reject E22 from the current branch with closure evidence:
  - product, experimental, internal, and lab verification bundles are green
  - canonical split surfaces work from their new homes
  - compatibility shims still work for one transition cycle
  - the wheel now exposes only the shipped `cortex` surface plus the two OpenAI console entrypoints
- After E22 is accepted:
  - product/runtime seams must justify themselves against shipped executive improvement directly
  - lab and governance seams must justify themselves as explicit product-unblocking work, not as Cortex identity

## 5. Explicitly blocked moves

- Do not merge the parked E20/E21 preserved branch through E22.
- Do not widen shipping truth in this seam.
- Do not change `WorkContract`, packet law, or runtime executive law in this seam.
- Do not describe lab, evidence, train, or governance work as shipped Cortex progress unless runtime behavior changes.
- Do not reopen E20 or E21 live work from this seam.
- Do not expose `experimental`, `lab`, or `internal` as the public install surface.
- Do not publish console scripts beyond:
  - `cortex-openai-cli`
  - `cortex-openai-service`

## 6. Acknowledged worktree noise

- Expected current-seam noise:
  - path moves from `tools/` to `lab/`
  - path moves from `scripts/` to `internal/workflow/`
  - path moves from mixed `docs/` root into `docs/experimental/`, `docs/lab/`, and `docs/internal/`
  - import and test fallout owned by the surface split
