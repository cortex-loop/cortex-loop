# scenario_thrash_reference_01__experimental_mediated__run_003

Date: 2026-03-20
Status: `reviewed_evidence`

## Scope

This committed run packet records one reference-host experimental mediated thrash comparator within the committed thrash paired-run series for mediation evidence review.
It does not justify mediation, does not authorize implementation work, and package-level evidence notes govern any verdict.

## Header

- date: 2026-03-20
- status: `reviewed_evidence`
- scenario_id: `scenario_thrash_reference_01`
- run_id: `reference_thrash_mediated_run_003`
- paired_episode_set_id: `pair_reference_thrash_003`

## Variant Metadata

- variant: `experimental_mediated`
- host_family: `reference`
- scenario_family: `thrash_control`
- task_value_rubric_id: `task_value_equal_completion`
- approval_or_environment_context_id: `env_local_default`

## Invariant Lock

- same_host_family_preserved: `yes`
- same_starting_task_framing_preserved: `yes`
- same_core_commitment_boundary_preserved: `yes`
- same_evidence_or_publication_surface_preserved: `yes`
- same_success_rubric_preserved: `yes`

## Scenario Inputs

- starting_request_or_event: bounded reference-host approval flow on `thrash-session-3` with repeated candidate-bearing follow-up before final certified completion
- host_surface: reference-host commitment path plus landed SRE goal, brake, allocation, and core support-session surfaces
- declared_scenario_goal: evaluate whether mediation reduces repeated branch reopen or resume cycles on a bounded multi-step reference-host episode without reducing lawful task completion
- bounded_environment_or_approval_context: `CommitmentEnvironmentHandle` with `available_query_kinds={EXECUTION_TRACE}` and `capability_tags={trace/read}` on `env_local_default`

## Run Outputs

- outcome_summary: The experimental mediated comparator reaches the same certified reference-host completion class at `thrash-mediated-003-step-3` after one guarded uncertified follow-up.
- branch_trajectory_summary: The experimental comparator derives `open -> suspend -> merge`, removing the extra `resume` step present in the baseline while preserving certified completion.
- uncertainty_or_brake_summary: The guarded uncertified intermediate state remains explicit at `thrash-mediated-003-step-2`; certification still requires lawful provenance at `thrash-mediated-003-step-3`.
- burden_summary: Visible intervention burden is recorded as `intervention_burden=3.0` from the committed branch-operation count on this mediated run.
- host_realization_summary: The comparator remains reference-only and preserves the same reference-host commitment boundary and support-session evidence surface.

## Artifact Refs

- event_trace_refs: `thrash-mediated-003-step-1:ApprovalRequest/open, thrash-mediated-003-step-2:ApprovalResult/suspend, thrash-mediated-003-step-3:ApprovalResult/merge`
- contradiction_refs: none
- degradation_refs: none
- aux_burden_refs_if_present: `docs/mediation_evidence/reference/scenario_thrash_reference_01__experimental_mediated__run_003__aux_burden.md`
- evaluation_packet_refs_if_present: none

## Lift-Axis Observations

### Reduced Thrashing

- observation: This experimental reference-only packet preserves certified completion with a shorter branch sequence than its matched baseline packet.
- metric_notes: Package-level evidence notes govern whether repeated paired evidence is enough to claim thrash reduction.
- verdict: `insufficient`

### Better Branch Discipline

- observation: This experimental reference-only packet avoids the extra branch `resume` step while keeping the same completion class.
- metric_notes: Package-level evidence notes govern whether repeated paired evidence is enough to claim branch-discipline lift.
- verdict: `insufficient`

### Better Uncertainty Handling

- observation: The guarded uncertified intermediate state remains explicit within the committed thrash paired-run series.
- metric_notes: Package-level evidence notes govern whether repeated paired evidence is enough to claim uncertainty-handling lift.
- verdict: `insufficient`

### Lower Visible Burden At Equal Task Value

- observation: Equal certified completion is preserved with `intervention_burden=3.0` recorded from the visible branch-operation count.
- metric_notes: The burden metric is the exact committed branch-operation count for this run.
- verdict: `insufficient`

### Better Host-Specialized Realization

- observation: The comparator stays reference-only and host-split within the committed thrash paired-run series.
- metric_notes: Package-level evidence notes govern whether repeated paired evidence is enough to claim host-specialized realization lift.
- verdict: `insufficient`

## Exclusions Or Unusable-Pair Notes

- exclusion_status: `none`
- failure_tags: `none`
- notes: This experimental mediated packet is part of the committed reference thrash paired-run series under `pair_reference_thrash_003`. A single packet does not justify mediation; package-level evidence notes govern verdicts.

## Reviewer Note

- reviewer_note: This is experimental mediated evidence only within the committed reference thrash paired-run series. It remains reference-only, does not justify mediation, and package-level evidence notes govern any verdict.
