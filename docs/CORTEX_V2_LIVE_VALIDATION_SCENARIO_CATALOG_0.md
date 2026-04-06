# CORTEX_V2_LIVE_VALIDATION_SCENARIO_CATALOG_0

Date: 2026-04-06
Status: active live-validation scenario catalog with the shared canonical direct-API suite recorded for current scope

## Shared coding harness

Project:

- `tests/fixtures/live_validation/project_template/`

Target task family:

- fix the `normalize_port()` upper-bound bug
- run `python -m pytest -q tests/test_normalize_port.py`

## Shared scenarios

### `pass_minimal`

- goal: one clean minimal bug-fix pass
- watchlist use:
  - operator/headless-CLI paired comparison
- canonical-truth target:
  - `canonical_anchor` direct-API suite
  - currently re-earned on OpenAI current scope and implemented for Claude once auth is ready
  - return a unified diff patch only
  - apply the patch externally in the harness
  - run the target test externally in the harness
  - score truth from actual patch/test outcome rather than model prose

### `restart_continuity`

- goal: prove whether the same lane can resume and finish cleanly after an explicit first-turn inspection
- canonical-truth target:
  - `canonical_anchor` direct-API suite
  - currently re-earned on OpenAI current scope and implemented for Claude once auth is ready
  - turn 1 uses the automation continuity inspection prompt
  - turn 2 resumes after session import and returns a unified diff patch only
  - apply the patch externally in the harness and run the target test externally

### `truth_gap`

- goal: preserve incompleteness honestly
- rule:
  - inspect only
  - no edits
  - no tests
- canonical-truth law:
  - `canonical_anchor` keeps the API lane text-only and toolless
  - OpenAI is the first re-earned current-scope host; Claude uses the same lane once auth is ready
  - no edits and no tests are available on the runtime lane itself
  - truth is scored from the returned text plus explicit no-edit/no-test harness evidence

## Lane classification

- `service_api`
  - `execution_surface = direct_api`
  - `evidence_role = canonical_truth`
- `operator_cli`
  - `execution_surface = headless_cli`
  - `evidence_role = watchlist`

## Current host caveat summary

### Claude

- operator watchlist lane exists now
- service/API truth is blocked on missing auth on this machine

### Gemini

- operator watchlist lane exists now
- current operator results remain the noisiest host-boundary watchlist line
- service/API truth is blocked on missing auth on this machine

### OpenAI

- operator watchlist lane exists now
- direct-API canonical truth is re-earned for current scope through the repeat-stable OpenAI `canonical_anchor` suite

## Artifact policy

- machine output: local-only under `.cortex/live_validation/`
- committed docs:
  - this catalog
  - the program brief
  - the verdict note
  - workflow/gate/correspondence summaries
