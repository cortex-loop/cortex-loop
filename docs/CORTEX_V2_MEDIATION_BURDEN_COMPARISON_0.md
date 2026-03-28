# CORTEX_V2_MEDIATION_BURDEN_COMPARISON_0

Date: 2026-03-21
Status: `reference_three_series_with_gemini_three_series_and_openai_three_series_recorded`

## Scope

This document records the equal-value burden comparison surface for mediation evidence review.
Version `0` is preseeded from the current scenario catalog and now records three reference-only mediation-specific host-realization pairs, three Gemini-only mediation-specific host-realization pairs, three OpenAI-only mediation-specific host-realization pairs, three reference-only experimental thrash pairs, three Gemini-only experimental thrash pairs, three OpenAI-only experimental thrash pairs, three reference-only experimental uncertainty pairs, three Gemini-only experimental uncertainty pairs, and three OpenAI-only experimental uncertainty pairs while keeping every burden verdict conservative.

## Use Rules

- Burden comparisons are only eligible when baseline and mediated runs land in the same task-value outcome class and preserve the same truth boundary class.
- `candidate_positive` is forbidden unless `equal_value_gate=passed` for every counted pair in that exact scenario-host cell.
- Keep excluded or drifted pairs in the paired-run ledger instead of laundering them into the burden table.

## Comparison Table

| scenario_id | host_family | usable_pair_count | equal_value_gate | baseline_burden_refs | mediated_burden_refs | current_verdict | supporting_paired_episode_sets | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| scenario_thrash_reference_01 | reference | 3 | passed | none | none | insufficient | pair_reference_thrash_001, pair_reference_thrash_002, pair_reference_thrash_003 | Three reference-only experimental pairs preserve the same certified completion class and truth boundary, but no lower-burden evidence is committed yet. |
| scenario_thrash_gemini_01 | gemini | 3 | passed | none | none | insufficient | pair_gemini_thrash_001, pair_gemini_thrash_002, pair_gemini_thrash_003 | Three Gemini-only experimental pairs preserve the same certified completion class and truth boundary, but no lower-burden evidence is committed yet. |
| scenario_thrash_openai_01 | openai | 3 | passed | none | none | insufficient | pair_openai_thrash_001, pair_openai_thrash_002, pair_openai_thrash_003 | Three OpenAI-only experimental pairs preserve the same certified completion class and truth boundary, but no lower-burden evidence is committed yet. |
| scenario_uncertainty_reference_01 | reference | 3 | passed | none | none | insufficient | pair_reference_uncertainty_001, pair_reference_uncertainty_002, pair_reference_uncertainty_003 | Three reference-only experimental uncertainty pairs preserve the same certified completion class and truth boundary, but no lower-burden evidence is committed yet. |
| scenario_uncertainty_gemini_01 | gemini | 3 | passed | none | none | insufficient | pair_gemini_uncertainty_001, pair_gemini_uncertainty_002, pair_gemini_uncertainty_003 | Three Gemini-only experimental uncertainty pairs preserve the same certified completion class and truth boundary, but no lower-burden evidence is committed yet. |
| scenario_uncertainty_openai_01 | openai | 3 | passed | none | none | insufficient | pair_openai_uncertainty_001, pair_openai_uncertainty_002, pair_openai_uncertainty_003 | Three OpenAI-only experimental uncertainty pairs preserve the same certified completion class and truth boundary, but no lower-burden evidence is committed yet. |
| scenario_host_reference_01 | reference | 3 | passed | none | none | insufficient | pair_reference_host_001, pair_reference_host_002, pair_reference_host_003 | Three reference-only host-realization pairs preserve the same certified completion class and truth boundary, but no lower-burden evidence is committed yet. |
| scenario_host_gemini_01 | gemini | 3 | passed | none | none | insufficient | pair_gemini_host_001, pair_gemini_host_002, pair_gemini_host_003 | Three Gemini-only host-realization pairs preserve the same certified completion class and truth boundary, but no lower-burden evidence is committed yet. |
| scenario_host_openai_01 | openai | 3 | passed | none | none | insufficient | pair_openai_host_001, pair_openai_host_002, pair_openai_host_003 | Three OpenAI-only host-realization pairs preserve the same certified completion class and truth boundary, but no lower-burden evidence is committed yet. |
