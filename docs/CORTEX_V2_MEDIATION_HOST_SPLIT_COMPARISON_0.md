# CORTEX_V2_MEDIATION_HOST_SPLIT_COMPARISON_0

Date: 2026-03-21
Status: `reference_three_series_with_gemini_three_series_and_openai_three_series_recorded`

## Scope

This document records the host-split mediation comparison surface.
Version `0` stays strictly host-split first: it now adds a host-coverage matrix for package truth, but it still avoids any pooled host verdict row that would hide per-host differences. It records three reference-only mediation-specific host-realization pairs, three Gemini-only mediation-specific host-realization pairs, three OpenAI-only mediation-specific host-realization pairs, three reference-only experimental thrash pairs, three Gemini-only experimental thrash pairs, three OpenAI-only experimental thrash pairs, three reference-only experimental uncertainty pairs, three Gemini-only experimental uncertainty pairs, and three OpenAI-only experimental uncertainty pairs.

## Current Host Matrix

| host_family | committed_package_state | current_recorded_families | current_live_note | j2_priority | notes |
| --- | --- | --- | --- | --- | --- |
| reference | current | thrash_control; uncertainty_boundary; host_realization | Stable first rerun anchor on the current line. | preferred | Use for branch-discipline, non-thrash burden, and host-realization refresh. |
| openai | current | thrash_control; uncertainty_boundary; host_realization | Stable first rerun anchor on the current line. | preferred | Use for branch-discipline, non-thrash burden, and host-realization refresh. |
| claude | missing | none | Current live operator line is positive, but mediation package coverage is still absent. | preferred | Highest-value missing host for host-realization and non-thrash burden breadth. |
| gemini | current | thrash_control; uncertainty_boundary; host_realization | Keep explicit as partial_or_contaminated for future live reruns. | explicit_partial | Do not hide current quota/capacity contamination behind pooled host averages. |

## Reference

| scenario_id | usable_pair_count | host_specific_affordance_note | host_flattening_tags | current_verdict | supporting_paired_episode_sets | notes |
| --- | --- | --- | --- | --- | --- | --- |
| scenario_thrash_reference_01 | 3 | Three reference-only experimental branch-control comparisons preserve the same host commitment boundary while shortening the branch sequence. | none | insufficient | pair_reference_thrash_001, pair_reference_thrash_002, pair_reference_thrash_003 | Three paired runs are recorded, but this host-specific surface remains descriptive until broader host or scenario coverage exists. |
| scenario_uncertainty_reference_01 | 3 | Three reference-only experimental uncertainty comparisons preserve contradiction-bearing evidence while removing one redundant uncertified loop before the same certified resolution class. | none | insufficient | pair_reference_uncertainty_001, pair_reference_uncertainty_002, pair_reference_uncertainty_003 | Three paired runs are recorded, but this host-specific surface remains descriptive until broader host or scenario coverage exists. |
| scenario_host_reference_01 | 3 | Three reference-only host-realization pairs preserve the same certified `current-pair` publication surface while directly specializing `mcp.query` instead of retaining generic family selection. | none | insufficient | pair_reference_host_001, pair_reference_host_002, pair_reference_host_003 | Three paired runs are recorded, but this host-specific surface remains descriptive until broader host or scenario coverage exists. |

## Gemini

| scenario_id | usable_pair_count | host_specific_affordance_note | host_flattening_tags | current_verdict | supporting_paired_episode_sets | notes |
| --- | --- | --- | --- | --- | --- | --- |
| scenario_thrash_gemini_01 | 3 | Three Gemini-only experimental branch-control comparisons preserve the same Gemini-native lifecycle surface while removing one redundant `resume` before certified completion. | none | insufficient | pair_gemini_thrash_001, pair_gemini_thrash_002, pair_gemini_thrash_003 | Three paired runs are recorded, but this host-specific surface remains descriptive until broader host or scenario coverage exists. |
| scenario_uncertainty_gemini_01 | 3 | Three Gemini-only experimental uncertainty comparisons preserve contradiction/degradation-bearing truth while removing one redundant uncertified loop before the same certified resolution class. | none | insufficient | pair_gemini_uncertainty_001, pair_gemini_uncertainty_002, pair_gemini_uncertainty_003 | Three paired runs are recorded, but this host-specific surface remains descriptive until broader host or scenario coverage exists. |
| scenario_host_gemini_01 | 3 | Three Gemini-only host-realization pairs preserve the same certified Gemini `current-pair` publication surface while directly specializing `mcp.query` instead of retaining generic family selection. | none | insufficient | pair_gemini_host_001, pair_gemini_host_002, pair_gemini_host_003 | Three paired runs are recorded, but this host-specific surface remains descriptive until broader host or scenario coverage exists. |

## OpenAI

| scenario_id | usable_pair_count | host_specific_affordance_note | host_flattening_tags | current_verdict | supporting_paired_episode_sets | notes |
| --- | --- | --- | --- | --- | --- | --- |
| scenario_thrash_openai_01 | 3 | Three OpenAI-only experimental branch-control comparisons preserve the same OpenAI-native lifecycle surface while removing one redundant `resume` before certified completion. | none | insufficient | pair_openai_thrash_001, pair_openai_thrash_002, pair_openai_thrash_003 | Three paired runs are recorded, but this host-specific surface remains descriptive until broader host or scenario coverage exists. |
| scenario_uncertainty_openai_01 | 3 | Three OpenAI-only experimental uncertainty comparisons preserve contradiction/degradation-bearing truth while removing one redundant uncertified loop before the same certified resolution class. | none | insufficient | pair_openai_uncertainty_001, pair_openai_uncertainty_002, pair_openai_uncertainty_003 | Three paired runs are recorded, but this host-specific surface remains descriptive until broader host or scenario coverage exists. |
| scenario_host_openai_01 | 3 | Three OpenAI-only host-realization pairs preserve the same certified OpenAI `current-pair` publication surface while directly specializing `mcp.query` instead of retaining generic family selection. | none | insufficient | pair_openai_host_001, pair_openai_host_002, pair_openai_host_003 | Three paired runs are recorded, but this host-specific surface remains descriptive until broader host or scenario coverage exists. |

## Claude

| scenario_id | usable_pair_count | host_specific_affordance_note | host_flattening_tags | current_verdict | supporting_paired_episode_sets | notes |
| --- | --- | --- | --- | --- | --- | --- |
| scenario_host_claude_01 | 0 | Claude is the highest-value missing mediation host-realization line on the current package. | none | insufficient | none | No Claude mediation host-realization pairs are committed yet. J2 should add this line before any package-level host-realization promotion. |
