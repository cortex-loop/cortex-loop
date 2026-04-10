# scenario_host_reference_01__experimental_mediated__run_002

Date: 2026-03-20
Status: `reviewed_evidence`

## Scope

This committed run packet records one reference-host experimental mediated host-realization comparator within the committed reference host-realization paired-run series for mediation evidence review.
It remains reference-only, does not justify mediation, and package-level evidence notes govern any verdict.

## Header

- date: 2026-03-20
- status: `reviewed_evidence`
- scenario_id: `scenario_host_reference_01`
- run_id: `reference_host_realization_mediated_run_002`
- paired_episode_set_id: `pair_reference_host_002`

## Variant Metadata

- variant: `experimental_mediated`
- host_family: `reference`
- scenario_family: `host_realization`
- task_value_rubric_id: `task_value_equal_host_realization`
- approval_or_environment_context_id: `env_boundary_sensitive`

## Invariant Lock

- same_host_family_preserved: `yes`
- same_starting_task_framing_preserved: `yes`
- same_core_commitment_boundary_preserved: `yes`
- same_evidence_or_publication_surface_preserved: `yes`
- same_success_rubric_preserved: `yes`

## Scenario Inputs

- starting_request_or_event: `ApprovalResult` with `commitment_id=commit-packet-2` and `session_id=packet-session-2`
- host_surface: reference-host opportunity selection plus commitment-to-eval-packet publication path
- declared_scenario_goal: evaluate whether mediation produces any reference-host realization lift without adding burden or branch churn
- bounded_environment_or_approval_context: reference-host commitment path with lawful provenance, contradiction-preserving degradation handling, the committed reference-lane packet/publication surface, and a bounded host-opportunity set containing `mcp.query`

## Run Outputs

- outcome_summary: The mediated reference-host path preserves the same certified current-pair evaluation packet with explicit contradiction, degradation, and truthful-withheld fields while directly specializing `mcp.query` for the selected `seek-context` family.
- branch_trajectory_summary: Single full-commitment publication path only; the only comparator delta is direct host-native opportunity specialization before packet publication.
- uncertainty_or_brake_summary: Contradiction and degradation remain explicit in the committed packet example, and `direct_opportunity_specialization_used=1` remains explicit for the mediated side of the pair.
- burden_summary: none
- host_realization_summary: Reference-host realization keeps the same selected family `seek-context`, the same bounded host-opportunity set containing `mcp.query`, and the same certified `current-pair` publication surface while changing `direct_opportunity_specialization_used` from `0` to `1`.

## Artifact Refs

- event_trace_refs: `reference-mediated-lane:commit-packet-2`
- contradiction_refs: `receipt-check:structured query result omitted one confirmation field`
- degradation_refs: `host-surface-degraded-002`
- aux_burden_refs_if_present: none
- evaluation_packet_refs_if_present: `docs/experimental/CORTEX_V2_REFERENCE_MEDIATED_LANE_PACKET_EXAMPLE_0.md`

## Lift-Axis Observations

### Reduced Thrashing

- observation: This mediated packet is part of the committed reference host-realization paired-run series, but it is not a branch-control comparison.
- metric_notes: Package-level evidence notes govern whether repeated paired evidence is enough to claim any thrash verdict.
- verdict: `insufficient`

### Better Branch Discipline

- observation: This mediated packet changes no branch trajectory and records no branch-discipline lift by itself.
- metric_notes: Package-level evidence notes govern whether repeated paired evidence is enough to claim any branch-discipline verdict.
- verdict: `insufficient`

### Better Uncertainty Handling

- observation: This packet preserves contradiction and degradation explicitly on the same certified publication surface used by the baseline.
- metric_notes: Package-level evidence notes govern whether repeated paired evidence is enough to claim any uncertainty-handling verdict.
- verdict: `insufficient`

### Lower Visible Burden At Equal Task Value

- observation: The pair holds the same certified completion class and truth boundary, but this packet carries no AUX burden artifact.
- metric_notes: Package-level evidence notes govern whether repeated paired evidence is enough to claim any lower-burden verdict.
- verdict: `insufficient`

### Better Host-Specialized Realization

- observation: This mediated packet directly specializes `mcp.query` for the selected `seek-context` family while preserving the same certified current-pair publication surface.
- metric_notes: The host-realization metric is `direct_opportunity_specialization_used=1` on the mediated side of the pair.
- verdict: `insufficient`

## Exclusions Or Unusable-Pair Notes

- exclusion_status: `none`
- failure_tags: `none`
- notes: This packet is the mediated side of `pair_reference_host_002`. A single packet does not justify mediation; package-level evidence notes govern verdicts.

## Reviewer Note

- reviewer_note: This is experimental mediated evidence only within the committed reference host-realization paired-run series. It remains reference-only, does not justify mediation, and package-level evidence notes govern any verdict.
