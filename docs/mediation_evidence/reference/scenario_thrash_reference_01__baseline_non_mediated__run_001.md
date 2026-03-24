# scenario_thrash_reference_01__baseline_non_mediated__run_001

Date: 2026-03-20
Status: `reviewed_evidence`

## Scope

This committed run packet records one reference-host baseline-only thrash control packet within the committed thrash paired-run series for mediation evidence review.
It does not provide comparative mediation evidence by itself, justify mediation, or authorize implementation work.

## Header

- date: 2026-03-20
- status: `reviewed_evidence`
- scenario_id: `scenario_thrash_reference_01`
- run_id: `reference_thrash_baseline_run_001`
- paired_episode_set_id: `pair_reference_thrash_001`

## Variant Metadata

- variant: `baseline_non_mediated`
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

- starting_request_or_event: bounded reference-host approval flow on `thrash-session-1` with repeated candidate-bearing follow-up before final certified completion
- host_surface: reference-host commitment path plus landed SRE goal, brake, allocation, and core support-session surfaces
- declared_scenario_goal: evaluate whether mediation reduces repeated branch reopen or resume cycles on a bounded multi-step reference-host episode without reducing lawful task completion
- bounded_environment_or_approval_context: `CommitmentEnvironmentHandle` with `available_query_kinds={EXECUTION_TRACE}` and `capability_tags={trace/read}` on `env_local_default`

## Run Outputs

- outcome_summary: The bounded reference-host episode reaches certified completion at `thrash-step-4` after one guarded uncertified follow-up at `thrash-step-2`.
- branch_trajectory_summary: The live reference-host episode derives an explicit `open -> suspend -> resume -> merge` sequence across `thrash-step-1` through `thrash-step-4`.
- uncertainty_or_brake_summary: Brake state is `guarded` only at `thrash-step-2` from elevated evidence uncertainty; no contradiction or degradation smoothing occurs.
- burden_summary: Visible intervention burden is recorded as `intervention_burden=4.0` from the committed branch-operation count on this baseline run.
- host_realization_summary: Reference-host commitment and landed SRE branch-control surfaces are exercised together without any pooled host claim.

## Artifact Refs

- event_trace_refs: `thrash-step-1:ApprovalRequest/open, thrash-step-2:ApprovalResult/suspend, thrash-step-3:ApprovalRequest/resume, thrash-step-4:ApprovalResult/merge`
- contradiction_refs: none
- degradation_refs: none
- aux_burden_refs_if_present: `docs/mediation_evidence/reference/scenario_thrash_reference_01__baseline_non_mediated__run_001__aux_burden.md`
- evaluation_packet_refs_if_present: none

## Lift-Axis Observations

### Reduced Thrashing

- observation: This packet records one lawful multi-step reference-host branch cycle within the committed thrash paired-run series.
- metric_notes: Package-level evidence notes govern whether repeated paired evidence is enough to claim thrash reduction.
- verdict: `insufficient`

### Better Branch Discipline

- observation: This packet preserves explicit branch trajectory evidence on the reference-host path within the committed thrash paired-run series.
- metric_notes: Package-level evidence notes govern whether repeated paired evidence is enough to claim branch-discipline lift.
- verdict: `insufficient`

### Better Uncertainty Handling

- observation: The guarded uncertified follow-up remains explicit within the committed thrash paired-run series.
- metric_notes: Package-level evidence notes govern whether repeated paired evidence is enough to claim uncertainty lift.
- verdict: `insufficient`

### Lower Visible Burden At Equal Task Value

- observation: Baseline-only packet within the committed thrash paired-run series with `intervention_burden=4.0` recorded from the visible branch-operation count.
- metric_notes: The burden metric is the exact committed branch-operation count for this run.
- verdict: `insufficient`

### Better Host-Specialized Realization

- observation: This packet exercises the reference-host commitment path together with landed SRE branch-control carriers within the committed thrash series.
- metric_notes: Package-level evidence notes govern whether repeated paired evidence is enough to claim host-specialized realization lift.
- verdict: `insufficient`

## Exclusions Or Unusable-Pair Notes

- exclusion_status: `none`
- failure_tags: `none`
- notes: This packet is part of the committed reference thrash paired-run series under `pair_reference_thrash_001`. A single packet does not justify mediation; package-level evidence notes govern verdicts.

## Reviewer Note

- reviewer_note: This is baseline-only committed evidence within the committed reference thrash paired-run series. It is not comparative mediation evidence by itself and does not justify mediation or authorize any implementation seam.
