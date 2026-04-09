# CORTEX_V2_MEDIATION_AXIS_COMPARISON_TABLE_0

Surface: lab

Date: 2026-03-30
Status: `j2_gap_closure_reference_openai_claude_recorded`

## Scope

This document records the current mediation lift-axis comparison surfaces after the mandatory J2 gap-closure reruns.

## Count Rules

- `usable_pair_count` counts only pairs recorded as `usable`.
- `confidence_downgraded_pair_count` counts only pairs recorded as `confidence_downgraded`.
- `excluded_pair_count` counts pairs recorded as `excluded`.
- Any verdict other than `insufficient` requires at least `3` counted pairs for that exact scenario-host cell.

## Package Verdict Summary

| axis | current_package_verdict | current_candidate_positive_cells | why_still_insufficient | minimum_additional_paired_evidence |
| --- | --- | --- | --- | --- |
| reduced thrashing | candidate_positive | scenario_thrash_reference_01/reference; scenario_thrash_gemini_01/gemini; scenario_thrash_openai_01/openai; scenario_branch_reference_01/reference; scenario_branch_openai_01/openai; scenario_branch_claude_01/claude | J2 now adds a dedicated branch-discipline family with repeated lower reopen/resume counts on reference, openai, and claude. | no mandatory additional paired evidence before one bounded experimental seam |
| better branch discipline | candidate_positive | scenario_thrash_reference_01/reference; scenario_thrash_gemini_01/gemini; scenario_thrash_openai_01/openai; scenario_branch_reference_01/reference; scenario_branch_openai_01/openai; scenario_branch_claude_01/claude | J2 now adds a dedicated branch-discipline family on the three preferred hosts. | no mandatory additional paired evidence before one bounded experimental seam |
| better uncertainty handling | insufficient | scenario_uncertainty_reference_01/reference; scenario_uncertainty_gemini_01/gemini; scenario_uncertainty_openai_01/openai | Current uncertainty signal still comes from one family only and still lacks Claude expansion. | optionally record scenario_uncertainty_claude_01 if the remaining uncertainty gap still matters after J2 |
| lower visible burden at equal task value | candidate_positive | scenario_thrash_reference_01/reference; scenario_thrash_gemini_01/gemini; scenario_thrash_openai_01/openai; scenario_burden_reference_01/reference; scenario_burden_openai_01/openai; scenario_burden_claude_01/claude | J2 now broadens the burden axis beyond thrash_control on the three preferred hosts. | no mandatory additional paired evidence before one bounded experimental seam |
| better host-specialized realization | candidate_positive | scenario_host_reference_01/reference; scenario_host_gemini_01/gemini; scenario_host_openai_01/openai; scenario_host_claude_01/claude | Claude host-realization is now present and the refreshed reference/openai cells remain positive. | no mandatory additional paired evidence before one bounded experimental seam |

## Reduced Thrashing

| scenario_id | host_family | usable_pair_count | confidence_downgraded_pair_count | excluded_pair_count | current_verdict | supporting_paired_episode_sets | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| scenario_thrash_reference_01 | reference | 3 | 0 | 0 | candidate_positive | pair_reference_thrash_001, pair_reference_thrash_002, pair_reference_thrash_003 | Repeated paired evidence now shows lower reopen/resume or oscillation counts for `scenario_thrash_reference_01` / `reference` at equal completion class. |
| scenario_thrash_gemini_01 | gemini | 3 | 0 | 0 | candidate_positive | pair_gemini_thrash_001, pair_gemini_thrash_002, pair_gemini_thrash_003 | Repeated paired evidence now shows lower reopen/resume or oscillation counts for `scenario_thrash_gemini_01` / `gemini` at equal completion class. |
| scenario_thrash_openai_01 | openai | 3 | 0 | 0 | candidate_positive | pair_openai_thrash_001, pair_openai_thrash_002, pair_openai_thrash_003 | Repeated paired evidence now shows lower reopen/resume or oscillation counts for `scenario_thrash_openai_01` / `openai` at equal completion class. |
| scenario_uncertainty_reference_01 | reference | 3 | 0 | 0 | insufficient | pair_reference_uncertainty_001, pair_reference_uncertainty_002, pair_reference_uncertainty_003 | This cell does not currently carry a reduced thrashing promotion claim. |
| scenario_uncertainty_gemini_01 | gemini | 3 | 0 | 0 | insufficient | pair_gemini_uncertainty_001, pair_gemini_uncertainty_002, pair_gemini_uncertainty_003 | This cell does not currently carry a reduced thrashing promotion claim. |
| scenario_uncertainty_openai_01 | openai | 3 | 0 | 0 | insufficient | pair_openai_uncertainty_001, pair_openai_uncertainty_002, pair_openai_uncertainty_003 | This cell does not currently carry a reduced thrashing promotion claim. |
| scenario_host_reference_01 | reference | 3 | 0 | 0 | insufficient | pair_reference_host_001, pair_reference_host_002, pair_reference_host_003 | This cell does not currently carry a reduced thrashing promotion claim. |
| scenario_host_gemini_01 | gemini | 3 | 0 | 0 | insufficient | pair_gemini_host_001, pair_gemini_host_002, pair_gemini_host_003 | This cell does not currently carry a reduced thrashing promotion claim. |
| scenario_host_openai_01 | openai | 3 | 0 | 0 | insufficient | pair_openai_host_001, pair_openai_host_002, pair_openai_host_003 | This cell does not currently carry a reduced thrashing promotion claim. |
| scenario_branch_reference_01 | reference | 3 | 0 | 0 | candidate_positive | pair_reference_branch_001, pair_reference_branch_002, pair_reference_branch_003 | Repeated paired evidence now shows lower reopen/resume or oscillation counts for `scenario_branch_reference_01` / `reference` at equal completion class. |
| scenario_branch_openai_01 | openai | 3 | 0 | 0 | candidate_positive | pair_openai_branch_001, pair_openai_branch_002, pair_openai_branch_003 | Repeated paired evidence now shows lower reopen/resume or oscillation counts for `scenario_branch_openai_01` / `openai` at equal completion class. |
| scenario_branch_claude_01 | claude | 3 | 0 | 0 | candidate_positive | pair_claude_branch_001, pair_claude_branch_002, pair_claude_branch_003 | Repeated paired evidence now shows lower reopen/resume or oscillation counts for `scenario_branch_claude_01` / `claude` at equal completion class. |
| scenario_burden_reference_01 | reference | 3 | 0 | 0 | insufficient | pair_reference_burden_001, pair_reference_burden_002, pair_reference_burden_003 | This cell does not currently carry a reduced thrashing promotion claim. |
| scenario_burden_openai_01 | openai | 3 | 0 | 0 | insufficient | pair_openai_burden_001, pair_openai_burden_002, pair_openai_burden_003 | This cell does not currently carry a reduced thrashing promotion claim. |
| scenario_burden_claude_01 | claude | 3 | 0 | 0 | insufficient | pair_claude_burden_001, pair_claude_burden_002, pair_claude_burden_003 | This cell does not currently carry a reduced thrashing promotion claim. |
| scenario_host_claude_01 | claude | 3 | 0 | 0 | insufficient | pair_claude_host_001, pair_claude_host_002, pair_claude_host_003 | This cell does not currently carry a reduced thrashing promotion claim. |

## Better Branch Discipline

| scenario_id | host_family | usable_pair_count | confidence_downgraded_pair_count | excluded_pair_count | current_verdict | supporting_paired_episode_sets | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| scenario_thrash_reference_01 | reference | 3 | 0 | 0 | candidate_positive | pair_reference_thrash_001, pair_reference_thrash_002, pair_reference_thrash_003 | Repeated paired evidence now shows lower stale/orphaned/unnecessary branch debt for `scenario_thrash_reference_01` / `reference` at equal completion class. |
| scenario_thrash_gemini_01 | gemini | 3 | 0 | 0 | candidate_positive | pair_gemini_thrash_001, pair_gemini_thrash_002, pair_gemini_thrash_003 | Repeated paired evidence now shows lower stale/orphaned/unnecessary branch debt for `scenario_thrash_gemini_01` / `gemini` at equal completion class. |
| scenario_thrash_openai_01 | openai | 3 | 0 | 0 | candidate_positive | pair_openai_thrash_001, pair_openai_thrash_002, pair_openai_thrash_003 | Repeated paired evidence now shows lower stale/orphaned/unnecessary branch debt for `scenario_thrash_openai_01` / `openai` at equal completion class. |
| scenario_uncertainty_reference_01 | reference | 3 | 0 | 0 | insufficient | pair_reference_uncertainty_001, pair_reference_uncertainty_002, pair_reference_uncertainty_003 | This cell does not currently carry a better branch discipline promotion claim. |
| scenario_uncertainty_gemini_01 | gemini | 3 | 0 | 0 | insufficient | pair_gemini_uncertainty_001, pair_gemini_uncertainty_002, pair_gemini_uncertainty_003 | This cell does not currently carry a better branch discipline promotion claim. |
| scenario_uncertainty_openai_01 | openai | 3 | 0 | 0 | insufficient | pair_openai_uncertainty_001, pair_openai_uncertainty_002, pair_openai_uncertainty_003 | This cell does not currently carry a better branch discipline promotion claim. |
| scenario_host_reference_01 | reference | 3 | 0 | 0 | insufficient | pair_reference_host_001, pair_reference_host_002, pair_reference_host_003 | This cell does not currently carry a better branch discipline promotion claim. |
| scenario_host_gemini_01 | gemini | 3 | 0 | 0 | insufficient | pair_gemini_host_001, pair_gemini_host_002, pair_gemini_host_003 | This cell does not currently carry a better branch discipline promotion claim. |
| scenario_host_openai_01 | openai | 3 | 0 | 0 | insufficient | pair_openai_host_001, pair_openai_host_002, pair_openai_host_003 | This cell does not currently carry a better branch discipline promotion claim. |
| scenario_branch_reference_01 | reference | 3 | 0 | 0 | candidate_positive | pair_reference_branch_001, pair_reference_branch_002, pair_reference_branch_003 | Repeated paired evidence now shows lower stale/orphaned/unnecessary branch debt for `scenario_branch_reference_01` / `reference` at equal completion class. |
| scenario_branch_openai_01 | openai | 3 | 0 | 0 | candidate_positive | pair_openai_branch_001, pair_openai_branch_002, pair_openai_branch_003 | Repeated paired evidence now shows lower stale/orphaned/unnecessary branch debt for `scenario_branch_openai_01` / `openai` at equal completion class. |
| scenario_branch_claude_01 | claude | 3 | 0 | 0 | candidate_positive | pair_claude_branch_001, pair_claude_branch_002, pair_claude_branch_003 | Repeated paired evidence now shows lower stale/orphaned/unnecessary branch debt for `scenario_branch_claude_01` / `claude` at equal completion class. |
| scenario_burden_reference_01 | reference | 3 | 0 | 0 | insufficient | pair_reference_burden_001, pair_reference_burden_002, pair_reference_burden_003 | This cell does not currently carry a better branch discipline promotion claim. |
| scenario_burden_openai_01 | openai | 3 | 0 | 0 | insufficient | pair_openai_burden_001, pair_openai_burden_002, pair_openai_burden_003 | This cell does not currently carry a better branch discipline promotion claim. |
| scenario_burden_claude_01 | claude | 3 | 0 | 0 | insufficient | pair_claude_burden_001, pair_claude_burden_002, pair_claude_burden_003 | This cell does not currently carry a better branch discipline promotion claim. |
| scenario_host_claude_01 | claude | 3 | 0 | 0 | insufficient | pair_claude_host_001, pair_claude_host_002, pair_claude_host_003 | This cell does not currently carry a better branch discipline promotion claim. |

## Better Uncertainty Handling

| scenario_id | host_family | usable_pair_count | confidence_downgraded_pair_count | excluded_pair_count | current_verdict | supporting_paired_episode_sets | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| scenario_thrash_reference_01 | reference | 3 | 0 | 0 | insufficient | pair_reference_thrash_001, pair_reference_thrash_002, pair_reference_thrash_003 | This cell does not currently carry a better uncertainty handling promotion claim. |
| scenario_thrash_gemini_01 | gemini | 3 | 0 | 0 | insufficient | pair_gemini_thrash_001, pair_gemini_thrash_002, pair_gemini_thrash_003 | This cell does not currently carry a better uncertainty handling promotion claim. |
| scenario_thrash_openai_01 | openai | 3 | 0 | 0 | insufficient | pair_openai_thrash_001, pair_openai_thrash_002, pair_openai_thrash_003 | This cell does not currently carry a better uncertainty handling promotion claim. |
| scenario_uncertainty_reference_01 | reference | 3 | 0 | 0 | candidate_positive | pair_reference_uncertainty_001, pair_reference_uncertainty_002, pair_reference_uncertainty_003 | Repeated paired evidence preserves contradiction-bearing truth while reducing avoidable uncertainty loops for `scenario_uncertainty_reference_01` / `reference`. |
| scenario_uncertainty_gemini_01 | gemini | 3 | 0 | 0 | candidate_positive | pair_gemini_uncertainty_001, pair_gemini_uncertainty_002, pair_gemini_uncertainty_003 | Repeated paired evidence preserves contradiction-bearing truth while reducing avoidable uncertainty loops for `scenario_uncertainty_gemini_01` / `gemini`. |
| scenario_uncertainty_openai_01 | openai | 3 | 0 | 0 | candidate_positive | pair_openai_uncertainty_001, pair_openai_uncertainty_002, pair_openai_uncertainty_003 | Repeated paired evidence preserves contradiction-bearing truth while reducing avoidable uncertainty loops for `scenario_uncertainty_openai_01` / `openai`. |
| scenario_host_reference_01 | reference | 3 | 0 | 0 | insufficient | pair_reference_host_001, pair_reference_host_002, pair_reference_host_003 | This cell does not currently carry a better uncertainty handling promotion claim. |
| scenario_host_gemini_01 | gemini | 3 | 0 | 0 | insufficient | pair_gemini_host_001, pair_gemini_host_002, pair_gemini_host_003 | This cell does not currently carry a better uncertainty handling promotion claim. |
| scenario_host_openai_01 | openai | 3 | 0 | 0 | insufficient | pair_openai_host_001, pair_openai_host_002, pair_openai_host_003 | This cell does not currently carry a better uncertainty handling promotion claim. |
| scenario_branch_reference_01 | reference | 3 | 0 | 0 | insufficient | pair_reference_branch_001, pair_reference_branch_002, pair_reference_branch_003 | This cell does not currently carry a better uncertainty handling promotion claim. |
| scenario_branch_openai_01 | openai | 3 | 0 | 0 | insufficient | pair_openai_branch_001, pair_openai_branch_002, pair_openai_branch_003 | This cell does not currently carry a better uncertainty handling promotion claim. |
| scenario_branch_claude_01 | claude | 3 | 0 | 0 | insufficient | pair_claude_branch_001, pair_claude_branch_002, pair_claude_branch_003 | This cell does not currently carry a better uncertainty handling promotion claim. |
| scenario_burden_reference_01 | reference | 3 | 0 | 0 | insufficient | pair_reference_burden_001, pair_reference_burden_002, pair_reference_burden_003 | This cell does not currently carry a better uncertainty handling promotion claim. |
| scenario_burden_openai_01 | openai | 3 | 0 | 0 | insufficient | pair_openai_burden_001, pair_openai_burden_002, pair_openai_burden_003 | This cell does not currently carry a better uncertainty handling promotion claim. |
| scenario_burden_claude_01 | claude | 3 | 0 | 0 | insufficient | pair_claude_burden_001, pair_claude_burden_002, pair_claude_burden_003 | This cell does not currently carry a better uncertainty handling promotion claim. |
| scenario_host_claude_01 | claude | 3 | 0 | 0 | insufficient | pair_claude_host_001, pair_claude_host_002, pair_claude_host_003 | This cell does not currently carry a better uncertainty handling promotion claim. |

## Lower Visible Burden At Equal Task Value

| scenario_id | host_family | usable_pair_count | confidence_downgraded_pair_count | excluded_pair_count | current_verdict | supporting_paired_episode_sets | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| scenario_thrash_reference_01 | reference | 3 | 0 | 0 | candidate_positive | pair_reference_thrash_001, pair_reference_thrash_002, pair_reference_thrash_003 | Repeated paired evidence now shows lower `visible_intervention_steps` for `scenario_thrash_reference_01` / `reference` at equal completion class. |
| scenario_thrash_gemini_01 | gemini | 3 | 0 | 0 | candidate_positive | pair_gemini_thrash_001, pair_gemini_thrash_002, pair_gemini_thrash_003 | Repeated paired evidence now shows lower `visible_intervention_steps` for `scenario_thrash_gemini_01` / `gemini` at equal completion class. |
| scenario_thrash_openai_01 | openai | 3 | 0 | 0 | candidate_positive | pair_openai_thrash_001, pair_openai_thrash_002, pair_openai_thrash_003 | Repeated paired evidence now shows lower `visible_intervention_steps` for `scenario_thrash_openai_01` / `openai` at equal completion class. |
| scenario_uncertainty_reference_01 | reference | 3 | 0 | 0 | insufficient | pair_reference_uncertainty_001, pair_reference_uncertainty_002, pair_reference_uncertainty_003 | This cell does not currently carry a lower visible burden at equal task value promotion claim. |
| scenario_uncertainty_gemini_01 | gemini | 3 | 0 | 0 | insufficient | pair_gemini_uncertainty_001, pair_gemini_uncertainty_002, pair_gemini_uncertainty_003 | This cell does not currently carry a lower visible burden at equal task value promotion claim. |
| scenario_uncertainty_openai_01 | openai | 3 | 0 | 0 | insufficient | pair_openai_uncertainty_001, pair_openai_uncertainty_002, pair_openai_uncertainty_003 | This cell does not currently carry a lower visible burden at equal task value promotion claim. |
| scenario_host_reference_01 | reference | 3 | 0 | 0 | insufficient | pair_reference_host_001, pair_reference_host_002, pair_reference_host_003 | This cell does not currently carry a lower visible burden at equal task value promotion claim. |
| scenario_host_gemini_01 | gemini | 3 | 0 | 0 | insufficient | pair_gemini_host_001, pair_gemini_host_002, pair_gemini_host_003 | This cell does not currently carry a lower visible burden at equal task value promotion claim. |
| scenario_host_openai_01 | openai | 3 | 0 | 0 | insufficient | pair_openai_host_001, pair_openai_host_002, pair_openai_host_003 | This cell does not currently carry a lower visible burden at equal task value promotion claim. |
| scenario_branch_reference_01 | reference | 3 | 0 | 0 | insufficient | pair_reference_branch_001, pair_reference_branch_002, pair_reference_branch_003 | This cell does not currently carry a lower visible burden at equal task value promotion claim. |
| scenario_branch_openai_01 | openai | 3 | 0 | 0 | insufficient | pair_openai_branch_001, pair_openai_branch_002, pair_openai_branch_003 | This cell does not currently carry a lower visible burden at equal task value promotion claim. |
| scenario_branch_claude_01 | claude | 3 | 0 | 0 | insufficient | pair_claude_branch_001, pair_claude_branch_002, pair_claude_branch_003 | This cell does not currently carry a lower visible burden at equal task value promotion claim. |
| scenario_burden_reference_01 | reference | 3 | 0 | 0 | candidate_positive | pair_reference_burden_001, pair_reference_burden_002, pair_reference_burden_003 | Repeated paired evidence now shows lower `visible_intervention_steps` for `scenario_burden_reference_01` / `reference` at equal completion class. |
| scenario_burden_openai_01 | openai | 3 | 0 | 0 | candidate_positive | pair_openai_burden_001, pair_openai_burden_002, pair_openai_burden_003 | Repeated paired evidence now shows lower `visible_intervention_steps` for `scenario_burden_openai_01` / `openai` at equal completion class. |
| scenario_burden_claude_01 | claude | 3 | 0 | 0 | candidate_positive | pair_claude_burden_001, pair_claude_burden_002, pair_claude_burden_003 | Repeated paired evidence now shows lower `visible_intervention_steps` for `scenario_burden_claude_01` / `claude` at equal completion class. |
| scenario_host_claude_01 | claude | 3 | 0 | 0 | insufficient | pair_claude_host_001, pair_claude_host_002, pair_claude_host_003 | This cell does not currently carry a lower visible burden at equal task value promotion claim. |

## Better Host-Specialized Realization

| scenario_id | host_family | usable_pair_count | confidence_downgraded_pair_count | excluded_pair_count | current_verdict | supporting_paired_episode_sets | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| scenario_thrash_reference_01 | reference | 3 | 0 | 0 | insufficient | pair_reference_thrash_001, pair_reference_thrash_002, pair_reference_thrash_003 | This cell does not currently carry a better host-specialized realization promotion claim. |
| scenario_thrash_gemini_01 | gemini | 3 | 0 | 0 | insufficient | pair_gemini_thrash_001, pair_gemini_thrash_002, pair_gemini_thrash_003 | This cell does not currently carry a better host-specialized realization promotion claim. |
| scenario_thrash_openai_01 | openai | 3 | 0 | 0 | insufficient | pair_openai_thrash_001, pair_openai_thrash_002, pair_openai_thrash_003 | This cell does not currently carry a better host-specialized realization promotion claim. |
| scenario_uncertainty_reference_01 | reference | 3 | 0 | 0 | insufficient | pair_reference_uncertainty_001, pair_reference_uncertainty_002, pair_reference_uncertainty_003 | This cell does not currently carry a better host-specialized realization promotion claim. |
| scenario_uncertainty_gemini_01 | gemini | 3 | 0 | 0 | insufficient | pair_gemini_uncertainty_001, pair_gemini_uncertainty_002, pair_gemini_uncertainty_003 | This cell does not currently carry a better host-specialized realization promotion claim. |
| scenario_uncertainty_openai_01 | openai | 3 | 0 | 0 | insufficient | pair_openai_uncertainty_001, pair_openai_uncertainty_002, pair_openai_uncertainty_003 | This cell does not currently carry a better host-specialized realization promotion claim. |
| scenario_host_reference_01 | reference | 3 | 0 | 0 | candidate_positive | pair_reference_host_001, pair_reference_host_002, pair_reference_host_003 | Repeated paired evidence preserves the same `current-pair` publication surface while direct `mcp.query` specialization changes from `0` to `1` for `scenario_host_reference_01` / `reference`. |
| scenario_host_gemini_01 | gemini | 3 | 0 | 0 | candidate_positive | pair_gemini_host_001, pair_gemini_host_002, pair_gemini_host_003 | Repeated paired evidence preserves the same `current-pair` publication surface while direct `mcp.query` specialization changes from `0` to `1` for `scenario_host_gemini_01` / `gemini`. |
| scenario_host_openai_01 | openai | 3 | 0 | 0 | candidate_positive | pair_openai_host_001, pair_openai_host_002, pair_openai_host_003 | Repeated paired evidence preserves the same `current-pair` publication surface while direct `mcp.query` specialization changes from `0` to `1` for `scenario_host_openai_01` / `openai`. |
| scenario_branch_reference_01 | reference | 3 | 0 | 0 | insufficient | pair_reference_branch_001, pair_reference_branch_002, pair_reference_branch_003 | This cell does not currently carry a better host-specialized realization promotion claim. |
| scenario_branch_openai_01 | openai | 3 | 0 | 0 | insufficient | pair_openai_branch_001, pair_openai_branch_002, pair_openai_branch_003 | This cell does not currently carry a better host-specialized realization promotion claim. |
| scenario_branch_claude_01 | claude | 3 | 0 | 0 | insufficient | pair_claude_branch_001, pair_claude_branch_002, pair_claude_branch_003 | This cell does not currently carry a better host-specialized realization promotion claim. |
| scenario_burden_reference_01 | reference | 3 | 0 | 0 | insufficient | pair_reference_burden_001, pair_reference_burden_002, pair_reference_burden_003 | This cell does not currently carry a better host-specialized realization promotion claim. |
| scenario_burden_openai_01 | openai | 3 | 0 | 0 | insufficient | pair_openai_burden_001, pair_openai_burden_002, pair_openai_burden_003 | This cell does not currently carry a better host-specialized realization promotion claim. |
| scenario_burden_claude_01 | claude | 3 | 0 | 0 | insufficient | pair_claude_burden_001, pair_claude_burden_002, pair_claude_burden_003 | This cell does not currently carry a better host-specialized realization promotion claim. |
| scenario_host_claude_01 | claude | 3 | 0 | 0 | candidate_positive | pair_claude_host_001, pair_claude_host_002, pair_claude_host_003 | Repeated paired evidence preserves the same `current-pair` publication surface while direct `mcp.query` specialization changes from `0` to `1` for `scenario_host_claude_01` / `claude`. |

## Exact Missing-Evidence Delta

| axis | current_package_verdict | current_candidate_positive_cells | why_still_insufficient | minimum_additional_paired_evidence |
| --- | --- | --- | --- | --- |
| reduced thrashing | candidate_positive | scenario_thrash_reference_01/reference; scenario_thrash_gemini_01/gemini; scenario_thrash_openai_01/openai; scenario_branch_reference_01/reference; scenario_branch_openai_01/openai; scenario_branch_claude_01/claude | J2 now adds a dedicated branch-discipline family with repeated lower reopen/resume counts on reference, openai, and claude. | no mandatory additional paired evidence before one bounded experimental seam |
| better branch discipline | candidate_positive | scenario_thrash_reference_01/reference; scenario_thrash_gemini_01/gemini; scenario_thrash_openai_01/openai; scenario_branch_reference_01/reference; scenario_branch_openai_01/openai; scenario_branch_claude_01/claude | J2 now adds a dedicated branch-discipline family on the three preferred hosts. | no mandatory additional paired evidence before one bounded experimental seam |
| better uncertainty handling | insufficient | scenario_uncertainty_reference_01/reference; scenario_uncertainty_gemini_01/gemini; scenario_uncertainty_openai_01/openai | Current uncertainty signal still comes from one family only and still lacks Claude expansion. | optionally record scenario_uncertainty_claude_01 if the remaining uncertainty gap still matters after J2 |
| lower visible burden at equal task value | candidate_positive | scenario_thrash_reference_01/reference; scenario_thrash_gemini_01/gemini; scenario_thrash_openai_01/openai; scenario_burden_reference_01/reference; scenario_burden_openai_01/openai; scenario_burden_claude_01/claude | J2 now broadens the burden axis beyond thrash_control on the three preferred hosts. | no mandatory additional paired evidence before one bounded experimental seam |
| better host-specialized realization | candidate_positive | scenario_host_reference_01/reference; scenario_host_gemini_01/gemini; scenario_host_openai_01/openai; scenario_host_claude_01/claude | Claude host-realization is now present and the refreshed reference/openai cells remain positive. | no mandatory additional paired evidence before one bounded experimental seam |
