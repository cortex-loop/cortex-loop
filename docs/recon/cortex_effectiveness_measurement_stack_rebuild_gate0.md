# Cortex Effectiveness Measurement-Stack Rebuild Gate 0

Surface: no-live lab/proof measurement diagnosis

## Summary

Verdict: `pass_cortex_effectiveness_measurement_stack_rebuild_gate0`.

This seam diagnosed the first real four-arm evaluator matrix, artifact
`run_20260508T221352Z`, without running live Codex and without changing
product behavior, evaluator scoring, fixtures, hidden verifier boundaries, or
candidate policy.

The Gate 0 command was:

```bash
python3 lab/cortex_effectiveness_evaluator.py --measurement-stack-rebuild-gate0 --require-pass
```

It wrote:

- `.cortex/live_validation/cortex_effectiveness_measurement_stack_rebuild_gate0/measurement_diagnosis.json`
- `.cortex/live_validation/cortex_effectiveness_measurement_stack_rebuild_gate0/case_discriminability.json`
- `.cortex/live_validation/cortex_effectiveness_measurement_stack_rebuild_gate0/gate0_report.json`
- `.cortex/live_validation/cortex_effectiveness_measurement_stack_rebuild_gate0/summary.json`

Artifact names: `measurement_diagnosis.json`, `case_discriminability.json`,
`gate0_report.json`, and `summary.json`.

Model-I/O path for this seam: `none_lab_proof_only`.

## Evidence Loaded

The diagnosis loaded all registered historical matrix artifacts from
`.cortex/live_validation/cortex_effectiveness_evaluator_live_matrix/run_20260508T221352Z/`:

- `summary.json`
- `leaderboard.json`
- `failure_analysis.json`
- `episode_table.jsonl`

The historical verdict remains
`failure_silent_perception_contamination`. No current v1 live case was
retroactively rescored.

## Diagnosis

The v1 matrix did not isolate active Cortex value.

- `exactness_evidence_recovery`: baseline parity; classified as `too_easy`.
- `truthful_closure`: baseline parity; classified as `too_easy`.
- `blocker_surfacing`: baseline parity; classified as `too_easy`.
- `clean_verified_work_control`: baseline parity as a value case, but valid as
  a zero-intervention control; classified as `control_valid`.
- `continuity_after_interruption`: repeat 1 was the only discriminating row,
  but `cortex_silent_perception` and `cortex_active_policy` both scored `4`
  against `no_cortex_baseline` at `1`; classified as `silent_contaminated`.

In plain terms, silent Cortex and active Cortex both scored `4` against `no_cortex_baseline` at `1`, so the continuity signal is contaminated rather than active-policy value.

There were no active-candidate-signal episodes, no boundary-failure episodes,
and no missing-arm episodes in the diagnosis.

## V2 Measurement Proposal

This seam proposes requirements only. It does not implement new live fixtures.

- Exactness/evidence recovery should require lifecycle evidence that a simple
  static reminder cannot supply.
- Truthful closure should distinguish closure reporting from generic success.
- Blocker surfacing should test honest unresolved dependency reporting.
- Continuity should remove prompt/workspace artifacts that let silent Cortex
  improve over no-Cortex.
- Clean verified-work controls must remain zero-intervention controls.

The next train is `cortex-effectiveness-v2-case-registry-gate0`, not live
matrix rerun, product tuning, candidate generation, or contraction of product
machinery from this single matrix.

## Forbidden Claims

- No behavior lift.
- No exactness value lift.
- No broad Cortex lift.
- No Codex App parity.
- No shipping promotion.
- No product progress.
- No AlphaEvolve-style candidate evolution.
- No live Codex run occurred in this seam.
- No product host behavior changed.
- No model-visible Cortex text changed.
- No evaluator scoring was changed to favor Cortex.
- No current v1 live case was retroactively rescored.
