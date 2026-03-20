# CORTEX_V2_MEDIATION_BURDEN_COMPARISON_0

Date: 2026-03-20
Status: `reference_thrash_pair_recorded`

## Scope

This document records the equal-value burden comparison surface for mediation evidence review.
Version `0` is preseeded from the current scenario catalog and now records one reference-only experimental thrash pair while keeping every burden verdict conservative.

## Use Rules

- Burden comparisons are only eligible when baseline and mediated runs land in the same task-value outcome class and preserve the same truth boundary class.
- `candidate_positive` is forbidden unless `equal_value_gate=passed` for every counted pair in that exact scenario-host cell.
- Keep excluded or drifted pairs in the paired-run ledger instead of laundering them into the burden table.

## Comparison Table

| scenario_id | host_family | usable_pair_count | equal_value_gate | baseline_burden_refs | mediated_burden_refs | current_verdict | supporting_paired_episode_sets | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| scenario_thrash_reference_01 | reference | 1 | passed | none | none | insufficient | pair_reference_thrash_001 | One reference-only experimental pair preserves the same certified completion class and truth boundary, but one pair is not enough to justify a burden verdict. |
| scenario_thrash_gemini_01 | gemini | 0 | not_recorded | none | none | insufficient | none | No live paired runs recorded yet. |
| scenario_thrash_openai_01 | openai | 0 | not_recorded | none | none | insufficient | none | No live paired runs recorded yet. |
| scenario_uncertainty_reference_01 | reference | 0 | not_recorded | none | none | insufficient | none | No live paired runs recorded yet. |
| scenario_uncertainty_gemini_01 | gemini | 0 | not_recorded | none | none | insufficient | none | No live paired runs recorded yet. |
| scenario_uncertainty_openai_01 | openai | 0 | not_recorded | none | none | insufficient | none | No live paired runs recorded yet. |
| scenario_host_reference_01 | reference | 0 | not_recorded | none | none | insufficient | none | No live paired runs recorded yet. |
| scenario_host_gemini_01 | gemini | 0 | not_recorded | none | none | insufficient | none | No live paired runs recorded yet. |
| scenario_host_openai_01 | openai | 0 | not_recorded | none | none | insufficient | none | No live paired runs recorded yet. |
