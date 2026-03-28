# CORTEX_V2_MEDIATION_RUN_PACKET_TEMPLATE_0

Date: 2026-03-20
Status: mediation comparative evidence template (`unfilled`)

## Scope

This template defines the minimum evidence packet for one mediation-comparison run.
It does not record a result by itself, justify mediation, or authorize implementation work.

## How To Use This Packet

- Create one packet per run.
- Use the same `paired_episode_set_id` across the baseline and mediated runs that belong together.
- Keep baseline and mediated runs matched on host family, starting task framing, core commitment boundary, evidence surface, and success rubric.
- Preserve contradiction-bearing failures instead of reporting only wins.
- This packet alone cannot justify mediation. It is one component of the broader evidence package required by `docs/CORTEX_V2_MEDIATION_EVALUATION_PLAN_0.md`.

## Header

- date:
- status: `template` | `draft_evidence` | `reviewed_evidence`
- scenario_id:
- run_id:
- paired_episode_set_id:

## Variant Metadata

- variant: `baseline_non_mediated` | `experimental_mediated`
- host_family:
- scenario_family:
- task_value_rubric_id:
- approval_or_environment_context_id:

## Invariant Lock

- same_host_family_preserved: `yes` | `no`
- same_starting_task_framing_preserved: `yes` | `no`
- same_core_commitment_boundary_preserved: `yes` | `no`
- same_evidence_or_publication_surface_preserved: `yes` | `no`
- same_success_rubric_preserved: `yes` | `no`

## Scenario Inputs

- starting_request_or_event:
- host_surface:
- declared_scenario_goal:
- bounded_environment_or_approval_context:

## Run Outputs

- outcome_summary:
- branch_trajectory_summary:
- uncertainty_or_brake_summary:
- burden_summary:
- host_realization_summary:

## Artifact Refs

- event_trace_refs:
- contradiction_refs:
- degradation_refs:
- aux_burden_refs_if_present:
- evaluation_packet_refs_if_present:

## Lift-Axis Observations

### Reduced Thrashing

- observation:
- metric_notes:
- verdict: `negative` | `neutral` | `mixed` | `candidate_positive` | `insufficient`

### Better Branch Discipline

- observation:
- metric_notes:
- verdict: `negative` | `neutral` | `mixed` | `candidate_positive` | `insufficient`

### Better Uncertainty Handling

- observation:
- metric_notes:
- verdict: `negative` | `neutral` | `mixed` | `candidate_positive` | `insufficient`

### Lower Visible Burden At Equal Task Value

- observation:
- metric_notes:
- verdict: `negative` | `neutral` | `mixed` | `candidate_positive` | `insufficient`

### Better Host-Specialized Realization

- observation:
- metric_notes:
- verdict: `negative` | `neutral` | `mixed` | `candidate_positive` | `insufficient`

## Exclusions Or Unusable-Pair Notes

- exclusion_status: `none` | `excluded` | `confidence_downgraded`
- failure_tags:
- notes:

## Reviewer Note

Short narrative only.
Do not record a winner claim, pooled pass-rate claim, or implementation recommendation here.

- reviewer_note:

## Example Labels

Use anonymized labels when concrete public runtime names are not required.

- scenario example: `scenario_alpha`
- host example: `host_family_reference`
- environment example: `workspace_b`
