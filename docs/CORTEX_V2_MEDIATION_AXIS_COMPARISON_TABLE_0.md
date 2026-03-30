# CORTEX_V2_MEDIATION_AXIS_COMPARISON_TABLE_0

Date: 2026-03-24
Status: `reference_three_series_with_gemini_three_series_and_openai_three_series_recorded`

## Scope

This document preseeds the five lift-axis comparison surfaces from the current mediation scenario catalog.
Version `0` records three reference-only mediation-specific host-realization pairs, three Gemini-only mediation-specific host-realization pairs, three OpenAI-only mediation-specific host-realization pairs, three reference-only experimental thrash pairs, three Gemini-only experimental thrash pairs, three OpenAI-only experimental thrash pairs, three reference-only experimental uncertainty pairs, three Gemini-only experimental uncertainty pairs, and three OpenAI-only experimental uncertainty pairs, keeps the package-level summaries conservative, and does not pool across hosts.

## Count Rules

- `usable_pair_count` counts only pairs recorded as `usable`.
- `confidence_downgraded_pair_count` counts only pairs recorded as `confidence_downgraded`.
- `excluded_pair_count` counts pairs recorded as `excluded`.
- Any verdict other than `insufficient` requires at least `3` counted pairs for that exact scenario-host cell.

## Package Verdict Summary

| axis | current_package_verdict | current_candidate_positive_cells | why_still_insufficient | minimum_additional_paired_evidence |
| --- | --- | --- | --- | --- |
| reduced thrashing | insufficient | scenario_thrash_reference_01/reference; scenario_thrash_gemini_01/gemini; scenario_thrash_openai_01/openai | Current signal comes from one family only and has no non-thrash corroboration. | Record scenario_branch_reference_01, scenario_branch_openai_01, and scenario_branch_claude_01 with 3 usable pairs each. |
| better branch discipline | insufficient | scenario_thrash_reference_01/reference; scenario_thrash_gemini_01/gemini; scenario_thrash_openai_01/openai | Current branch-discipline signal derives only from thrash_control and has no dedicated family. | Record scenario_branch_reference_01, scenario_branch_openai_01, and scenario_branch_claude_01 with 3 usable pairs each. |
| better uncertainty handling | insufficient | scenario_uncertainty_reference_01/reference; scenario_uncertainty_gemini_01/gemini; scenario_uncertainty_openai_01/openai | Current uncertainty signal comes from one family only and still has no Claude expansion. | Record scenario_uncertainty_claude_01 with 3 usable pairs, or add one second uncertainty-sensitive family on stable hosts. |
| lower visible burden at equal task value | insufficient | scenario_thrash_reference_01/reference; scenario_thrash_gemini_01/gemini; scenario_thrash_openai_01/openai | Current burden signal is confined to thrash_control and no non-thrash equal-value burden family is recorded. | Record scenario_burden_reference_01, scenario_burden_openai_01, and scenario_burden_claude_01 with burden refs and 3 usable pairs each. |
| better host-specialized realization | insufficient | scenario_host_reference_01/reference; scenario_host_gemini_01/gemini; scenario_host_openai_01/openai | Current signal exists on one family only, Claude is missing, and future reruns should favor the most stable hosts first. | Record scenario_host_claude_01 with 3 usable pairs and refresh host_realization on reference and openai before promotion. |

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
| scenario_host_gemini_01 | gemini | 3 | 0 | 0 | insufficient | pair_gemini_host_001, pair_gemini_host_002, pair_gemini_host_003 | Three Gemini-only host-realization pairs are recorded, but this cell does not claim a thrash verdict. |
| scenario_host_openai_01 | openai | 3 | 0 | 0 | insufficient | pair_openai_host_001, pair_openai_host_002, pair_openai_host_003 | Three OpenAI-only host-realization pairs are recorded, but this cell does not claim a thrash verdict. |

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
| scenario_host_gemini_01 | gemini | 3 | 0 | 0 | insufficient | pair_gemini_host_001, pair_gemini_host_002, pair_gemini_host_003 | Three Gemini-only host-realization pairs are recorded, but this cell does not claim a branch-discipline verdict. |
| scenario_host_openai_01 | openai | 3 | 0 | 0 | insufficient | pair_openai_host_001, pair_openai_host_002, pair_openai_host_003 | Three OpenAI-only host-realization pairs are recorded, but this cell does not claim a branch-discipline verdict. |

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
| scenario_host_gemini_01 | gemini | 3 | 0 | 0 | insufficient | pair_gemini_host_001, pair_gemini_host_002, pair_gemini_host_003 | Three Gemini-only host-realization pairs are recorded, but this cell does not claim an uncertainty-handling verdict. |
| scenario_host_openai_01 | openai | 3 | 0 | 0 | insufficient | pair_openai_host_001, pair_openai_host_002, pair_openai_host_003 | Three OpenAI-only host-realization pairs are recorded, but this cell does not claim an uncertainty-handling verdict. |

## Lower Visible Burden At Equal Task Value

| scenario_id | host_family | usable_pair_count | confidence_downgraded_pair_count | excluded_pair_count | current_verdict | supporting_paired_episode_sets | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| scenario_thrash_reference_01 | reference | 3 | 0 | 0 | candidate_positive | pair_reference_thrash_001, pair_reference_thrash_002, pair_reference_thrash_003 | Three reference-only experimental pairs preserve equal completion while reducing visible intervention burden from `4.0` to `3.0` on every counted pair. |
| scenario_thrash_gemini_01 | gemini | 3 | 0 | 0 | candidate_positive | pair_gemini_thrash_001, pair_gemini_thrash_002, pair_gemini_thrash_003 | Three Gemini-only experimental pairs preserve equal completion while reducing visible intervention burden from `4.0` to `3.0` on every counted pair. |
| scenario_thrash_openai_01 | openai | 3 | 0 | 0 | candidate_positive | pair_openai_thrash_001, pair_openai_thrash_002, pair_openai_thrash_003 | Three OpenAI-only experimental pairs preserve equal completion while reducing visible intervention burden from `4.0` to `3.0` on every counted pair. |
| scenario_uncertainty_reference_01 | reference | 3 | 0 | 0 | insufficient | pair_reference_uncertainty_001, pair_reference_uncertainty_002, pair_reference_uncertainty_003 | Three reference-only experimental uncertainty pairs preserve equal truth/class resolution, but no lower-burden evidence is committed yet. |
| scenario_uncertainty_gemini_01 | gemini | 3 | 0 | 0 | insufficient | pair_gemini_uncertainty_001, pair_gemini_uncertainty_002, pair_gemini_uncertainty_003 | Three Gemini-only experimental uncertainty pairs preserve equal truth/class resolution, but no lower-burden evidence is committed yet. |
| scenario_uncertainty_openai_01 | openai | 3 | 0 | 0 | insufficient | pair_openai_uncertainty_001, pair_openai_uncertainty_002, pair_openai_uncertainty_003 | Three OpenAI-only experimental uncertainty pairs preserve equal truth/class resolution, but no lower-burden evidence is committed yet. |
| scenario_host_reference_01 | reference | 3 | 0 | 0 | insufficient | pair_reference_host_001, pair_reference_host_002, pair_reference_host_003 | Three reference-only host-realization pairs preserve equal certified completion class and truth boundary, but no lower-burden evidence is committed yet. |
| scenario_host_gemini_01 | gemini | 3 | 0 | 0 | insufficient | pair_gemini_host_001, pair_gemini_host_002, pair_gemini_host_003 | Three Gemini-only host-realization pairs preserve equal certified completion class and truth boundary, but no lower-burden evidence is committed yet. |
| scenario_host_openai_01 | openai | 3 | 0 | 0 | insufficient | pair_openai_host_001, pair_openai_host_002, pair_openai_host_003 | Three OpenAI-only host-realization pairs preserve equal certified completion class and truth boundary, but no lower-burden evidence is committed yet. |

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
| scenario_host_gemini_01 | gemini | 3 | 0 | 0 | candidate_positive | pair_gemini_host_001, pair_gemini_host_002, pair_gemini_host_003 | Three Gemini-only host-realization pairs preserve the same certified Gemini `current-pair` publication surface while changing `direct_opportunity_specialization_used` from `0` to `1`. |
| scenario_host_openai_01 | openai | 3 | 0 | 0 | candidate_positive | pair_openai_host_001, pair_openai_host_002, pair_openai_host_003 | Three OpenAI-only host-realization pairs preserve the same certified OpenAI `current-pair` publication surface while changing `direct_opportunity_specialization_used` from `0` to `1`. |

## Exact Missing-Evidence Delta

| axis | current_package_verdict | current_candidate_positive_cells | why_still_insufficient | minimum_additional_paired_evidence |
| --- | --- | --- | --- | --- |
| reduced thrashing | insufficient | scenario_thrash_reference_01/reference; scenario_thrash_gemini_01/gemini; scenario_thrash_openai_01/openai | Current signal comes from one family only and has no non-thrash corroboration. | Record scenario_branch_reference_01, scenario_branch_openai_01, and scenario_branch_claude_01 with 3 usable pairs each. |
| better branch discipline | insufficient | scenario_thrash_reference_01/reference; scenario_thrash_gemini_01/gemini; scenario_thrash_openai_01/openai | Current branch-discipline signal derives only from thrash_control and has no dedicated family. | Record scenario_branch_reference_01, scenario_branch_openai_01, and scenario_branch_claude_01 with 3 usable pairs each. |
| better uncertainty handling | insufficient | scenario_uncertainty_reference_01/reference; scenario_uncertainty_gemini_01/gemini; scenario_uncertainty_openai_01/openai | Current uncertainty signal comes from one family only and still has no Claude expansion. | Record scenario_uncertainty_claude_01 with 3 usable pairs, or add one second uncertainty-sensitive family on stable hosts. |
| lower visible burden at equal task value | insufficient | scenario_thrash_reference_01/reference; scenario_thrash_gemini_01/gemini; scenario_thrash_openai_01/openai | Current burden signal is confined to thrash_control and no non-thrash equal-value burden family is recorded. | Record scenario_burden_reference_01, scenario_burden_openai_01, and scenario_burden_claude_01 with burden refs and 3 usable pairs each. |
| better host-specialized realization | insufficient | scenario_host_reference_01/reference; scenario_host_gemini_01/gemini; scenario_host_openai_01/openai | Current signal exists on one family only, Claude is missing, and future reruns should favor the most stable hosts first. | Record scenario_host_claude_01 with 3 usable pairs and refresh host_realization on reference and openai before promotion. |
