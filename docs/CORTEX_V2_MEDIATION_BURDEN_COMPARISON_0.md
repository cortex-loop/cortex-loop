# CORTEX_V2_MEDIATION_BURDEN_COMPARISON_0

Date: 2026-03-30
Status: `j2_gap_closure_reference_openai_claude_recorded`

## Scope

This document records the equal-value burden comparison surface for mediation evidence review after J2.

## Use Rules

- Burden comparisons are only eligible when baseline and mediated runs land in the same task-value outcome class and preserve the same truth boundary class.
- `candidate_positive` is forbidden unless `equal_value_gate=passed` for every counted pair in that exact scenario-host cell.
- Keep excluded or drifted pairs in the paired-run ledger instead of laundering them into the burden table.

## Package Burden Verdict

| axis | current_package_verdict | current_candidate_positive_cells | why_still_insufficient |
| --- | --- | --- | --- |
| lower visible burden at equal task value | candidate_positive | scenario_thrash_reference_01/reference; scenario_thrash_gemini_01/gemini; scenario_thrash_openai_01/openai; scenario_burden_reference_01/reference; scenario_burden_openai_01/openai; scenario_burden_claude_01/claude | J2 broadens the burden axis beyond `thrash_control` on the three preferred hosts, so no current burden blocker remains for one bounded experimental seam. |

## Comparison Table

| scenario_id | host_family | usable_pair_count | equal_value_gate | baseline_burden_refs | mediated_burden_refs | current_verdict | supporting_paired_episode_sets | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| scenario_thrash_reference_01 | reference | 3 | passed | docs/mediation_evidence/reference/scenario_thrash_reference_01__baseline_non_mediated__run_001__aux_burden.md,docs/mediation_evidence/reference/scenario_thrash_reference_01__baseline_non_mediated__run_002__aux_burden.md,docs/mediation_evidence/reference/scenario_thrash_reference_01__baseline_non_mediated__run_003__aux_burden.md | docs/mediation_evidence/reference/scenario_thrash_reference_01__experimental_mediated__run_001__aux_burden.md,docs/mediation_evidence/reference/scenario_thrash_reference_01__experimental_mediated__run_002__aux_burden.md,docs/mediation_evidence/reference/scenario_thrash_reference_01__experimental_mediated__run_003__aux_burden.md | candidate_positive | pair_reference_thrash_001, pair_reference_thrash_002, pair_reference_thrash_003 | Three reference-only thrash pairs preserve equal completion while reducing visible intervention burden. |
| scenario_thrash_gemini_01 | gemini | 3 | passed | docs/mediation_evidence/gemini/scenario_thrash_gemini_01__baseline_non_mediated__run_001__aux_burden.md,docs/mediation_evidence/gemini/scenario_thrash_gemini_01__baseline_non_mediated__run_002__aux_burden.md,docs/mediation_evidence/gemini/scenario_thrash_gemini_01__baseline_non_mediated__run_003__aux_burden.md | docs/mediation_evidence/gemini/scenario_thrash_gemini_01__experimental_mediated__run_001__aux_burden.md,docs/mediation_evidence/gemini/scenario_thrash_gemini_01__experimental_mediated__run_002__aux_burden.md,docs/mediation_evidence/gemini/scenario_thrash_gemini_01__experimental_mediated__run_003__aux_burden.md | candidate_positive | pair_gemini_thrash_001, pair_gemini_thrash_002, pair_gemini_thrash_003 | Three Gemini-only thrash pairs preserve equal completion while reducing visible intervention burden. |
| scenario_thrash_openai_01 | openai | 3 | passed | docs/mediation_evidence/openai/scenario_thrash_openai_01__baseline_non_mediated__run_001__aux_burden.md,docs/mediation_evidence/openai/scenario_thrash_openai_01__baseline_non_mediated__run_002__aux_burden.md,docs/mediation_evidence/openai/scenario_thrash_openai_01__baseline_non_mediated__run_003__aux_burden.md | docs/mediation_evidence/openai/scenario_thrash_openai_01__experimental_mediated__run_001__aux_burden.md,docs/mediation_evidence/openai/scenario_thrash_openai_01__experimental_mediated__run_002__aux_burden.md,docs/mediation_evidence/openai/scenario_thrash_openai_01__experimental_mediated__run_003__aux_burden.md | candidate_positive | pair_openai_thrash_001, pair_openai_thrash_002, pair_openai_thrash_003 | Three OpenAI-only thrash pairs preserve equal completion while reducing visible intervention burden. |
| scenario_burden_reference_01 | reference | 3 | passed | docs/mediation_evidence/reference/scenario_burden_reference_01__baseline_non_mediated__run_001__aux_burden.md,docs/mediation_evidence/reference/scenario_burden_reference_01__baseline_non_mediated__run_002__aux_burden.md,docs/mediation_evidence/reference/scenario_burden_reference_01__baseline_non_mediated__run_003__aux_burden.md | docs/mediation_evidence/reference/scenario_burden_reference_01__experimental_mediated__run_001__aux_burden.md,docs/mediation_evidence/reference/scenario_burden_reference_01__experimental_mediated__run_002__aux_burden.md,docs/mediation_evidence/reference/scenario_burden_reference_01__experimental_mediated__run_003__aux_burden.md | candidate_positive | pair_reference_burden_001, pair_reference_burden_002, pair_reference_burden_003 | Three reference-only non-thrash burden pairs preserve equal completion while reducing visible intervention burden without thrash churn. |
| scenario_burden_openai_01 | openai | 3 | passed | docs/mediation_evidence/openai/scenario_burden_openai_01__baseline_non_mediated__run_001__aux_burden.md,docs/mediation_evidence/openai/scenario_burden_openai_01__baseline_non_mediated__run_002__aux_burden.md,docs/mediation_evidence/openai/scenario_burden_openai_01__baseline_non_mediated__run_003__aux_burden.md | docs/mediation_evidence/openai/scenario_burden_openai_01__experimental_mediated__run_001__aux_burden.md,docs/mediation_evidence/openai/scenario_burden_openai_01__experimental_mediated__run_002__aux_burden.md,docs/mediation_evidence/openai/scenario_burden_openai_01__experimental_mediated__run_003__aux_burden.md | candidate_positive | pair_openai_burden_001, pair_openai_burden_002, pair_openai_burden_003 | Three OpenAI-only non-thrash burden pairs preserve equal completion while reducing visible intervention burden without thrash churn. |
| scenario_burden_claude_01 | claude | 3 | passed | docs/mediation_evidence/claude/scenario_burden_claude_01__baseline_non_mediated__run_001__aux_burden.md,docs/mediation_evidence/claude/scenario_burden_claude_01__baseline_non_mediated__run_002__aux_burden.md,docs/mediation_evidence/claude/scenario_burden_claude_01__baseline_non_mediated__run_003__aux_burden.md | docs/mediation_evidence/claude/scenario_burden_claude_01__experimental_mediated__run_001__aux_burden.md,docs/mediation_evidence/claude/scenario_burden_claude_01__experimental_mediated__run_002__aux_burden.md,docs/mediation_evidence/claude/scenario_burden_claude_01__experimental_mediated__run_003__aux_burden.md | candidate_positive | pair_claude_burden_001, pair_claude_burden_002, pair_claude_burden_003 | Three Claude-only non-thrash burden pairs preserve equal completion while reducing visible intervention burden without thrash churn. |

## Exact Burden Gap

| gap_id | current_status | why_missing | minimum_next_evidence |
| --- | --- | --- | --- |
| non_thrash_equal_value_burden_family | resolved | J2 now records dedicated non-thrash burden evidence on the three preferred hosts. | no mandatory additional burden reruns are required before one bounded experimental seam |
