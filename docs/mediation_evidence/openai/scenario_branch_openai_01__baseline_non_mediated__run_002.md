# scenario_branch_openai_01__baseline_non_mediated__run_002

Date: 2026-03-20
Status: `reviewed_evidence`

## Scope

This committed run packet records one branch-discipline mediation comparator within the committed paired-run series for mediation evidence review.
It does not justify mediation, activate mediation, or authorize implementation work.

## Header

- date: `2026-03-20`
- status: `reviewed_evidence`
- scenario_id: `scenario_branch_openai_01`
- run_id: `openai_branch_baseline_run_002`
- paired_episode_set_id: `pair_openai_branch_002`

## Variant Metadata

- variant: `baseline_non_mediated`
- host_family: `openai`
- scenario_family: `branch_discipline`
- task_value_rubric_id: `task_value_equal_completion`
- approval_or_environment_context_id: `env_local_default`

## Invariant Lock

- same_host_family_preserved: `yes`
- same_starting_task_framing_preserved: `yes`
- same_core_commitment_boundary_preserved: `yes`
- same_evidence_or_publication_surface_preserved: `yes`
- same_success_rubric_preserved: `yes`

## Scenario Inputs

- starting_request_or_event: bounded OpenAI-host branch-review task with one candidate-bearing branch detour before certified completion
- host_surface: OpenAI-host branch-review and commitment publication path with landed SRE branch carriers
- declared_scenario_goal: evaluate whether mediation reduces branch-discipline debt without reducing lawful task completion
- bounded_environment_or_approval_context: deterministic local default context with the same commitment boundary and the same host packet/publication surface on both sides of the pair

## Run Outputs

- outcome_summary: The comparator reaches the same certified completion class on both sides of the pair.
- branch_trajectory_summary: The baseline branch-discipline comparator records `open -> suspend -> resume -> merge` with `stale_branch_count=1`, `orphaned_branch_count=1`, and `unnecessary_branch_count=1`.
- uncertainty_or_brake_summary: Contradiction and degradation remain explicit and the completion boundary is unchanged.
- burden_summary: none
- host_realization_summary: This comparator is not a host-realization claim; it preserves the same host surface while changing only branch-discipline debt.

## Artifact Refs

- event_trace_refs: `openai-branch-002-step-1:response.output_text.delta/open, openai-branch-002-step-2:response.output_text.delta/suspend, openai-branch-002-step-3:response.output_text.delta/resume, openai-branch-002-step-4:response.completed/merge`
- contradiction_refs: `openai-branch-receipt-check:OpenAI branch receipt review remained partially unresolved`
- degradation_refs: `openai-branch-partial-002`
- aux_burden_refs_if_present: none
- evaluation_packet_refs_if_present: none

## Lift-Axis Observations

### Reduced Thrashing

- observation: This branch-discipline comparator records explicit reopen/resume pressure through `reopen_resume_count` within the same completion class.
- metric_notes: Package-level promotion is allowed only if the new branch-discipline cells show repeated lower reopen/resume counts.
- verdict: `insufficient`

### Better Branch Discipline

- observation: This comparator records explicit stale/orphaned/unnecessary branch counts on both sides of the pair.
- metric_notes: The branch-discipline metric is the strict comparison over `stale_branch_count + orphaned_branch_count + unnecessary_branch_count`.
- verdict: `insufficient`

### Better Uncertainty Handling

- observation: This packet preserves contradiction/degradation truth but does not target the uncertainty axis directly.
- metric_notes: Package-level uncertainty verdicts should continue to come from the uncertainty family unless explicitly widened later.
- verdict: `insufficient`

### Lower Visible Burden At Equal Task Value

- observation: This packet is not the non-thrash burden family and does not carry a burden artifact.
- metric_notes: Use the dedicated non-thrash burden family for burden promotion.
- verdict: `insufficient`

### Better Host-Specialized Realization

- observation: This comparator preserves the same host surface and does not claim host-native opportunity specialization lift.
- metric_notes: Host-realization verdicts should continue to come from the dedicated host_realization family.
- verdict: `insufficient`

## Exclusions Or Unusable-Pair Notes

- exclusion_status: `none`
- failure_tags: `none`
- notes: This packet is one side of `pair_openai_branch_002`. It is deterministic branch-discipline evidence only and does not by itself justify mediation.

## Reviewer Note

- reviewer_note: This is committed branch-discipline evidence only. It does not justify mediation implementation and package-level evidence notes govern verdicts.
