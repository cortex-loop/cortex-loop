# CORTEX_V2_LIVE_VALIDATION_SCENARIO_CATALOG_0

Date: 2026-04-06
Status: active live-validation scenario catalog for the R1 two-lane truth reset

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
  - later direct-API confirmation suite on a capable machine

### `restart_continuity`

- goal: prove whether the same lane can resume and finish cleanly after an explicit first-turn inspection

### `truth_gap`

- goal: preserve incompleteness honestly
- rule:
  - inspect only
  - no edits
  - no tests
- canonical-truth law:
  - when the API lane is expanded to this scenario, truth-gap discipline must be enforced by runtime constraints rather than prose-only “please inspect” wording

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
- service/API truth is blocked on missing auth on this machine

## Artifact policy

- machine output: local-only under `.cortex/live_validation/`
- committed docs:
  - this catalog
  - the program brief
  - the verdict note
  - workflow/gate/correspondence summaries
