# CORTEX_V2_MEDIATION_PAIRED_RUN_LEDGER_0

Date: 2026-03-20
Status: `no_live_pairs_recorded`

## Scope

This ledger records the planned mediation-comparison coverage surface and any later paired baseline versus mediated runs.
Version `0` is scaffold-only: it precommits coverage from the current scenario catalog and preserves explicit exclusions without recording any live pairs yet.

## Use Rules

- Keep every baseline versus mediated comparison matched on `scenario_id`, `host_family`, `task_value_rubric_id`, `approval_or_environment_context_id`, starting task framing, core commitment boundary, and evidence/publication surface.
- Record unusable or drifted pairs here instead of silently dropping them.
- Use `docs/CORTEX_V2_MEDIATION_RUN_PACKET_TEMPLATE_0.md` for the per-run packet refs recorded below.
- This ledger does not justify mediation or authorize implementation work.

## Coverage Commitments

| scenario_id | host_family | scenario_family | task_value_rubric_id | approval_or_environment_context_id | minimum_paired_run_count | coverage_status |
| --- | --- | --- | --- | --- | --- | --- |
| scenario_thrash_reference_01 | reference | thrash_control | task_value_equal_completion | env_local_default | 3 | planned |
| scenario_thrash_gemini_01 | gemini | thrash_control | task_value_equal_completion | env_local_default | 3 | planned |
| scenario_thrash_openai_01 | openai | thrash_control | task_value_equal_completion | env_local_default | 3 | planned |
| scenario_uncertainty_reference_01 | reference | uncertainty_boundary | task_value_equal_truth_preservation | env_uncertainty_sensitive | 3 | planned |
| scenario_uncertainty_gemini_01 | gemini | uncertainty_boundary | task_value_equal_truth_preservation | env_uncertainty_sensitive | 3 | planned |
| scenario_uncertainty_openai_01 | openai | uncertainty_boundary | task_value_equal_truth_preservation | env_uncertainty_sensitive | 3 | planned |
| scenario_host_reference_01 | reference | host_realization | task_value_equal_host_realization | env_boundary_sensitive | 3 | planned |
| scenario_host_gemini_01 | gemini | host_realization | task_value_equal_host_realization | env_boundary_sensitive | 3 | planned |
| scenario_host_openai_01 | openai | host_realization | task_value_equal_host_realization | env_boundary_sensitive | 3 | planned |

## Recorded Paired Runs

| paired_episode_set_id | scenario_id | host_family | baseline_run_id | mediated_run_id | baseline_packet_ref | mediated_packet_ref | pair_status | failure_tags | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| none_recorded_yet | — | — | — | — | — | — | not_recorded | none | No live paired runs are recorded yet. |
