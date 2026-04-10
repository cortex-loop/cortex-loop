# CORTEX_V2_MEDIATION_HOST_SPLIT_COMPARISON_0

Surface: lab

Date: 2026-03-30
Status: `j2_gap_closure_reference_openai_claude_recorded`

## Scope

This document records the host-split mediation comparison surface after J2. It remains host-split first and avoids pooled host verdict rows that hide host differences.

## Current Host Matrix

| host_family | committed_package_state | current_recorded_families | current_live_note | j2_priority | notes |
| --- | --- | --- | --- | --- | --- |
| reference | current | thrash_control; uncertainty_boundary; host_realization; branch_discipline; equal_value_burden_non_thrash | Stable first rerun anchor on the current line. | preferred | Reference now has dedicated branch-discipline and non-thrash burden evidence. |
| openai | current | thrash_control; uncertainty_boundary; host_realization; branch_discipline; equal_value_burden_non_thrash | Stable first rerun anchor on the current line. | preferred | OpenAI now has dedicated branch-discipline and non-thrash burden evidence. |
| claude | current | host_realization; branch_discipline; equal_value_burden_non_thrash | Claude is now present in the mediation package on deterministic evidence surfaces. | preferred | Claude is the only new host added in J2. |
| gemini | current | thrash_control; uncertainty_boundary; host_realization | Keep explicit as partial_or_contaminated for future live reruns. | explicit_partial | Do not hide current quota/capacity contamination behind pooled host averages. |

## Reference

| scenario_id | usable_pair_count | host_specific_affordance_note | host_flattening_tags | current_verdict | supporting_paired_episode_sets | notes |
| --- | --- | --- | --- | --- | --- | --- |
| scenario_thrash_reference_01 | 3 | Three reference-only experimental thrash comparisons preserve the same host commitment boundary while lowering reopen/resume churn. | none | candidate_positive | pair_reference_thrash_001, pair_reference_thrash_002, pair_reference_thrash_003 | Cell-level reduced-thrashing signal remains explicit. |
| scenario_branch_reference_01 | 3 | Three reference-only branch-discipline comparisons preserve completion while lowering stale/orphaned/unnecessary branch debt. | none | candidate_positive | pair_reference_branch_001, pair_reference_branch_002, pair_reference_branch_003 | Dedicated branch-discipline family now exists. |
| scenario_burden_reference_01 | 3 | Three reference-only non-thrash burden comparisons preserve completion while lowering visible intervention burden. | none | candidate_positive | pair_reference_burden_001, pair_reference_burden_002, pair_reference_burden_003 | Dedicated non-thrash burden family now exists. |
| scenario_host_reference_01 | 3 | Three reference-only host-realization pairs preserve the same certified `current-pair` publication surface while directly specializing `mcp.query`. | none | candidate_positive | pair_reference_host_001, pair_reference_host_002, pair_reference_host_003 | Reference host-realization remains positive. |

## Gemini

| scenario_id | usable_pair_count | host_specific_affordance_note | host_flattening_tags | current_verdict | supporting_paired_episode_sets | notes |
| --- | --- | --- | --- | --- | --- | --- |
| scenario_thrash_gemini_01 | 3 | Three Gemini-only experimental thrash comparisons preserve the same Gemini-native lifecycle surface while lowering reopen/resume churn. | none | candidate_positive | pair_gemini_thrash_001, pair_gemini_thrash_002, pair_gemini_thrash_003 | Gemini remains present and explicit. |
| scenario_uncertainty_gemini_01 | 3 | Three Gemini-only uncertainty comparisons preserve contradiction/degradation truth while lowering one redundant uncertified loop. | none | candidate_positive | pair_gemini_uncertainty_001, pair_gemini_uncertainty_002, pair_gemini_uncertainty_003 | Gemini uncertainty remains a cell-level signal only. |
| scenario_host_gemini_01 | 3 | Three Gemini-only host-realization pairs preserve the same certified Gemini `current-pair` publication surface while directly specializing `mcp.query`. | none | candidate_positive | pair_gemini_host_001, pair_gemini_host_002, pair_gemini_host_003 | Gemini remains explicit and unhidden. |

## OpenAI

| scenario_id | usable_pair_count | host_specific_affordance_note | host_flattening_tags | current_verdict | supporting_paired_episode_sets | notes |
| --- | --- | --- | --- | --- | --- | --- |
| scenario_thrash_openai_01 | 3 | Three OpenAI-only experimental thrash comparisons preserve the same OpenAI-native lifecycle surface while lowering reopen/resume churn. | none | candidate_positive | pair_openai_thrash_001, pair_openai_thrash_002, pair_openai_thrash_003 | Cell-level reduced-thrashing signal remains explicit. |
| scenario_branch_openai_01 | 3 | Three OpenAI-only branch-discipline comparisons preserve completion while lowering stale/orphaned/unnecessary branch debt. | none | candidate_positive | pair_openai_branch_001, pair_openai_branch_002, pair_openai_branch_003 | Dedicated branch-discipline family now exists. |
| scenario_burden_openai_01 | 3 | Three OpenAI-only non-thrash burden comparisons preserve completion while lowering visible intervention burden. | none | candidate_positive | pair_openai_burden_001, pair_openai_burden_002, pair_openai_burden_003 | Dedicated non-thrash burden family now exists. |
| scenario_host_openai_01 | 3 | Three OpenAI-only host-realization pairs preserve the same certified OpenAI `current-pair` publication surface while directly specializing `mcp.query`. | none | candidate_positive | pair_openai_host_001, pair_openai_host_002, pair_openai_host_003 | OpenAI host-realization remains positive. |

## Claude

| scenario_id | usable_pair_count | host_specific_affordance_note | host_flattening_tags | current_verdict | supporting_paired_episode_sets | notes |
| --- | --- | --- | --- | --- | --- | --- |
| scenario_branch_claude_01 | 3 | Three Claude-only branch-discipline comparisons preserve completion while lowering stale/orphaned/unnecessary branch debt. | none | candidate_positive | pair_claude_branch_001, pair_claude_branch_002, pair_claude_branch_003 | Claude branch-discipline is now present. |
| scenario_burden_claude_01 | 3 | Three Claude-only non-thrash burden comparisons preserve completion while lowering visible intervention burden. | none | candidate_positive | pair_claude_burden_001, pair_claude_burden_002, pair_claude_burden_003 | Claude non-thrash burden is now present. |
| scenario_host_claude_01 | 3 | Three Claude-only host-realization pairs preserve the same certified Claude `current-pair` publication surface while directly specializing `mcp.query`. | none | candidate_positive | pair_claude_host_001, pair_claude_host_002, pair_claude_host_003 | Claude host-realization is now present. |
