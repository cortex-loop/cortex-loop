# CORTEX_V2_MEDIATION_AXIS_COMPARISON_TABLE_0

Date: 2026-03-21
Status: `reference_three_series_with_gemini_two_series_and_openai_two_series_recorded`

## Scope

This document preseeds the five lift-axis comparison surfaces from the current mediation scenario catalog.
Version `0` records three reference-only mediation-specific host-realization pairs, three reference-only experimental thrash pairs, three Gemini-only experimental thrash pairs, three OpenAI-only experimental thrash pairs, three reference-only experimental uncertainty pairs, three Gemini-only experimental uncertainty pairs, and three OpenAI-only experimental uncertainty pairs, keeps the package-level summaries conservative, and does not pool across hosts.

## Count Rules

- `usable_pair_count` counts only pairs recorded as `usable`.
- `confidence_downgraded_pair_count` counts only pairs recorded as `confidence_downgraded`.
- `excluded_pair_count` counts pairs recorded as `excluded`.
- Any verdict other than `insufficient` requires at least `3` counted pairs for that exact scenario-host cell.

## Reduced Thrashing

| scenario_id | host_family | usable_pair_count | confidence_downgraded_pair_count | excluded_pair_count | current_verdict | supporting_paired_episode_sets | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| scenario_thrash_reference_01 | reference | 3 | 0 | 0 | candidate_positive | pair_reference_thrash_001, pair_reference_thrash_002, pair_reference_thrash_003 | Three reference-only experimental pairs are recorded for this scenario-host cell and they show repeated shorter branch sequences at equal completion class. |
| scenario_thrash_gemini_01 | gemini | 3 | 0 | 0 | candidate_positive | pair_gemini_thrash_001, pair_gemini_thrash_002, pair_gemini_thrash_003 | Three Gemini-only experimental pairs are recorded for this scenario-host cell and they show repeated shorter branch sequences at equal completion class. |
| scenario_thrash_openai_01 | openai | 3 | 0 | 0 | candidate_positive | pair_openai_thrash_001, pair_openai_thrash_002, pair_openai_thrash_003 | Three OpenAI-only experimental pairs are recorded for this scenario-host cell and they show repeated shorter branch sequences at equal completion class. |
| scenario_uncertainty_reference_01 | reference | 3 | 0 | 0 | insufficient | pair_reference_uncertainty_001, pair_reference_uncertainty_002, pair_reference_uncertainty_003 | Three reference-only experimental uncertainty pairs are recorded, but this cell does not claim a thrash verdict. |
| scenario_uncertainty_gemini_01 | gemini | 3 | 0 | 0 | insufficient | pair_gemini_uncertainty_001, pair_gemini_uncertainty_002, pair_gemini_uncertainty_003 | Three Gemini-only experimental uncertainty pairs are recorded, but this cell does not claim a thrash verdict. |
| scenario_uncertainty_openai_01 | openai | 3 | 0 | 0 | insufficient | pair_openai_uncertainty_001, pair_openai_uncertainty_002, pair_openai_uncertainty_003 | Three OpenAI-only experimental uncertainty pairs are recorded, but this cell does not claim a thrash verdict. |
| scenario_host_reference_01 | reference | 3 | 0 | 0 | insufficient | pair_reference_host_001, pair_reference_host_002, pair_reference_host_003 | Three reference-only host-realization pairs are recorded, but this cell does not claim a thrash verdict. |
| scenario_host_gemini_01 | gemini | 0 | 0 | 0 | insufficient | none | No live paired runs recorded yet. |
| scenario_host_openai_01 | openai | 0 | 0 | 0 | insufficient | none | No live paired runs recorded yet. |

## Better Branch Discipline

| scenario_id | host_family | usable_pair_count | confidence_downgraded_pair_count | excluded_pair_count | current_verdict | supporting_paired_episode_sets | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| scenario_thrash_reference_01 | reference | 3 | 0 | 0 | candidate_positive | pair_reference_thrash_001, pair_reference_thrash_002, pair_reference_thrash_003 | Three reference-only experimental pairs are recorded for this scenario-host cell and they show repeated branch-discipline improvement at equal completion class. |
| scenario_thrash_gemini_01 | gemini | 3 | 0 | 0 | candidate_positive | pair_gemini_thrash_001, pair_gemini_thrash_002, pair_gemini_thrash_003 | Three Gemini-only experimental pairs are recorded for this scenario-host cell and they show repeated branch-discipline improvement at equal completion class. |
| scenario_thrash_openai_01 | openai | 3 | 0 | 0 | candidate_positive | pair_openai_thrash_001, pair_openai_thrash_002, pair_openai_thrash_003 | Three OpenAI-only experimental pairs are recorded for this scenario-host cell and they show repeated branch-discipline improvement at equal completion class. |
| scenario_uncertainty_reference_01 | reference | 3 | 0 | 0 | insufficient | pair_reference_uncertainty_001, pair_reference_uncertainty_002, pair_reference_uncertainty_003 | Three reference-only experimental uncertainty pairs are recorded, but this cell does not claim a branch-discipline verdict. |
| scenario_uncertainty_gemini_01 | gemini | 3 | 0 | 0 | insufficient | pair_gemini_uncertainty_001, pair_gemini_uncertainty_002, pair_gemini_uncertainty_003 | Three Gemini-only experimental uncertainty pairs are recorded, but this cell does not claim a branch-discipline verdict. |
| scenario_uncertainty_openai_01 | openai | 3 | 0 | 0 | insufficient | pair_openai_uncertainty_001, pair_openai_uncertainty_002, pair_openai_uncertainty_003 | Three OpenAI-only experimental uncertainty pairs are recorded, but this cell does not claim a branch-discipline verdict. |
| scenario_host_reference_01 | reference | 3 | 0 | 0 | insufficient | pair_reference_host_001, pair_reference_host_002, pair_reference_host_003 | Three reference-only host-realization pairs are recorded, but this cell does not claim a branch-discipline verdict. |
| scenario_host_gemini_01 | gemini | 0 | 0 | 0 | insufficient | none | No live paired runs recorded yet. |
| scenario_host_openai_01 | openai | 0 | 0 | 0 | insufficient | none | No live paired runs recorded yet. |

## Better Uncertainty Handling

| scenario_id | host_family | usable_pair_count | confidence_downgraded_pair_count | excluded_pair_count | current_verdict | supporting_paired_episode_sets | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| scenario_thrash_reference_01 | reference | 3 | 0 | 0 | insufficient | pair_reference_thrash_001, pair_reference_thrash_002, pair_reference_thrash_003 | Three reference-only experimental pairs are recorded, but the current committed evidence remains too narrow to justify an uncertainty-handling verdict. |
| scenario_thrash_gemini_01 | gemini | 3 | 0 | 0 | insufficient | pair_gemini_thrash_001, pair_gemini_thrash_002, pair_gemini_thrash_003 | Three Gemini-only experimental pairs are recorded, but the current committed evidence remains too narrow to justify an uncertainty-handling verdict. |
| scenario_thrash_openai_01 | openai | 3 | 0 | 0 | insufficient | pair_openai_thrash_001, pair_openai_thrash_002, pair_openai_thrash_003 | Three OpenAI-only experimental pairs are recorded, but this cell does not claim an uncertainty verdict. |
| scenario_uncertainty_reference_01 | reference | 3 | 0 | 0 | candidate_positive | pair_reference_uncertainty_001, pair_reference_uncertainty_002, pair_reference_uncertainty_003 | Three reference-only experimental uncertainty pairs preserve contradiction-bearing evidence and reduce one redundant uncertified loop before the same certified resolution class. |
| scenario_uncertainty_gemini_01 | gemini | 3 | 0 | 0 | candidate_positive | pair_gemini_uncertainty_001, pair_gemini_uncertainty_002, pair_gemini_uncertainty_003 | Three Gemini-only experimental uncertainty pairs preserve contradiction-bearing evidence and reduce one redundant uncertified loop before the same certified resolution class. |
| scenario_uncertainty_openai_01 | openai | 3 | 0 | 0 | candidate_positive | pair_openai_uncertainty_001, pair_openai_uncertainty_002, pair_openai_uncertainty_003 | Three OpenAI-only experimental uncertainty pairs preserve contradiction-bearing evidence and reduce one redundant uncertified loop before the same certified resolution class. |
| scenario_host_reference_01 | reference | 3 | 0 | 0 | insufficient | pair_reference_host_001, pair_reference_host_002, pair_reference_host_003 | Three reference-only host-realization pairs are recorded, but this cell does not claim an uncertainty-handling verdict. |
| scenario_host_gemini_01 | gemini | 0 | 0 | 0 | insufficient | none | No live paired runs recorded yet. |
| scenario_host_openai_01 | openai | 0 | 0 | 0 | insufficient | none | No live paired runs recorded yet. |

## Lower Visible Burden At Equal Task Value

| scenario_id | host_family | usable_pair_count | confidence_downgraded_pair_count | excluded_pair_count | current_verdict | supporting_paired_episode_sets | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| scenario_thrash_reference_01 | reference | 3 | 0 | 0 | insufficient | pair_reference_thrash_001, pair_reference_thrash_002, pair_reference_thrash_003 | Three reference-only experimental pairs preserve equal completion, but no lower-burden evidence is committed yet. |
| scenario_thrash_gemini_01 | gemini | 3 | 0 | 0 | insufficient | pair_gemini_thrash_001, pair_gemini_thrash_002, pair_gemini_thrash_003 | Three Gemini-only experimental pairs preserve equal completion, but no lower-burden evidence is committed yet. |
| scenario_thrash_openai_01 | openai | 3 | 0 | 0 | insufficient | pair_openai_thrash_001, pair_openai_thrash_002, pair_openai_thrash_003 | Three OpenAI-only experimental pairs preserve equal completion, but no lower-burden evidence is committed yet. |
| scenario_uncertainty_reference_01 | reference | 3 | 0 | 0 | insufficient | pair_reference_uncertainty_001, pair_reference_uncertainty_002, pair_reference_uncertainty_003 | Three reference-only experimental uncertainty pairs preserve equal truth/class resolution, but no lower-burden evidence is committed yet. |
| scenario_uncertainty_gemini_01 | gemini | 3 | 0 | 0 | insufficient | pair_gemini_uncertainty_001, pair_gemini_uncertainty_002, pair_gemini_uncertainty_003 | Three Gemini-only experimental uncertainty pairs preserve equal truth/class resolution, but no lower-burden evidence is committed yet. |
| scenario_uncertainty_openai_01 | openai | 3 | 0 | 0 | insufficient | pair_openai_uncertainty_001, pair_openai_uncertainty_002, pair_openai_uncertainty_003 | Three OpenAI-only experimental uncertainty pairs preserve equal truth/class resolution, but no lower-burden evidence is committed yet. |
| scenario_host_reference_01 | reference | 3 | 0 | 0 | insufficient | pair_reference_host_001, pair_reference_host_002, pair_reference_host_003 | Three reference-only host-realization pairs preserve equal certified completion class and truth boundary, but no lower-burden evidence is committed yet. |
| scenario_host_gemini_01 | gemini | 0 | 0 | 0 | insufficient | none | No live paired runs recorded yet. |
| scenario_host_openai_01 | openai | 0 | 0 | 0 | insufficient | none | No live paired runs recorded yet. |

## Better Host-Specialized Realization

| scenario_id | host_family | usable_pair_count | confidence_downgraded_pair_count | excluded_pair_count | current_verdict | supporting_paired_episode_sets | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| scenario_thrash_reference_01 | reference | 3 | 0 | 0 | insufficient | pair_reference_thrash_001, pair_reference_thrash_002, pair_reference_thrash_003 | Three reference-only experimental pairs are recorded, but this host-specialized realization cell remains descriptive only. |
| scenario_thrash_gemini_01 | gemini | 3 | 0 | 0 | insufficient | pair_gemini_thrash_001, pair_gemini_thrash_002, pair_gemini_thrash_003 | Three Gemini-only experimental pairs are recorded, but this host-specialized realization cell remains descriptive only. |
| scenario_thrash_openai_01 | openai | 3 | 0 | 0 | insufficient | pair_openai_thrash_001, pair_openai_thrash_002, pair_openai_thrash_003 | Three OpenAI-only experimental pairs are recorded, but this host-specialized realization cell remains descriptive only. |
| scenario_uncertainty_reference_01 | reference | 3 | 0 | 0 | insufficient | pair_reference_uncertainty_001, pair_reference_uncertainty_002, pair_reference_uncertainty_003 | Three reference-only experimental uncertainty pairs are recorded, but this host-specialized realization cell remains descriptive only. |
| scenario_uncertainty_gemini_01 | gemini | 3 | 0 | 0 | insufficient | pair_gemini_uncertainty_001, pair_gemini_uncertainty_002, pair_gemini_uncertainty_003 | Three Gemini-only experimental uncertainty pairs are recorded, but this host-specialized realization cell remains descriptive only. |
| scenario_uncertainty_openai_01 | openai | 3 | 0 | 0 | insufficient | pair_openai_uncertainty_001, pair_openai_uncertainty_002, pair_openai_uncertainty_003 | Three OpenAI-only experimental uncertainty pairs are recorded, but this host-specialized realization cell remains descriptive only. |
| scenario_host_reference_01 | reference | 3 | 0 | 0 | candidate_positive | pair_reference_host_001, pair_reference_host_002, pair_reference_host_003 | Three reference-only host-realization pairs preserve the same certified `current-pair` publication surface while changing `direct_opportunity_specialization_used` from `0` to `1`. |
| scenario_host_gemini_01 | gemini | 0 | 0 | 0 | insufficient | none | No live paired runs recorded yet. |
| scenario_host_openai_01 | openai | 0 | 0 | 0 | insufficient | none | No live paired runs recorded yet. |
