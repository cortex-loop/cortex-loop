# CORTEX_V2_MEDIATION_REFERENCE_HOST_REALIZATION_REPLICATION_NOTE_0

Date: 2026-03-21
Status: `reference host realization replication law recorded`

## Scope

This note records the fairness and admissibility law for the counted reference host-realization pair set.
It does not justify mediation, activate mediation, or widen the allowed comparison surface.

## Counted Pair Set

The counted reference host-realization pair set is currently:

- `pair_reference_host_001`
- `pair_reference_host_002`
- `pair_reference_host_003`

## Cross-Pair Distinctness

| pair_id | baseline_run_id | mediated_run_id | session_id | commitment_candidate_id | provenance_artifact_id | contradiction_source_tag | contradiction_summary | degradation_reason_code |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pair_reference_host_001 | reference_host_realization_baseline_run_001 | reference_host_realization_mediated_run_001 | packet-session-1 | commit-packet-1 | artifact-packet-1 | host-check | write receipt was incomplete | host-surface-degraded |
| pair_reference_host_002 | reference_host_realization_baseline_run_002 | reference_host_realization_mediated_run_002 | packet-session-2 | commit-packet-2 | artifact-packet-2 | receipt-check | structured query result omitted one confirmation field | host-surface-degraded-002 |
| pair_reference_host_003 | reference_host_realization_baseline_run_003 | reference_host_realization_mediated_run_003 | packet-session-3 | commit-packet-3 | artifact-packet-3 | artifact-check | supporting artifact trace remained partial | host-surface-degraded-003 |

Trace ids must also remain distinct across the series.

## Within-Pair Fairness Law

Every counted pair must preserve:

- `scenario_id=scenario_host_reference_01`
- `host_family=reference`
- `task_value_rubric_id=task_value_equal_host_realization`
- `approval_or_environment_context_id=env_boundary_sensitive`
- the same reference observe/bind meaning
- the same commitment truth boundary
- the same evaluation-packet publication surface
- the same packet kind `current-pair`
- the same final certified completion class
- the same contradiction/degradation preservation law
- the same truthful-withheld meaning
- the same selected family `seek-context`
- the same host-opportunity set containing `mcp.query`

The only allowed within-pair comparator delta is that `HostNativeOpportunity.clearly_superior` changes from `False` to `True`, causing `direct_opportunity_specialization_used` to move from `0` to `1`.

## Forbidden Counted Drift

No pair may count if it changes any of the following:

- selected family
- `opportunity_ref`
- packet semantics
- contradiction/degradation payload meaning
- truthful-withheld fields
- burden claims
- package-level host-lift scope
- live opportunity specialization, by replacing it with prose-only interpretation

## Outcome

`pair_reference_host_001`, `pair_reference_host_002`, and `pair_reference_host_003` are countable only because the baseline and mediated sides preserve the same certified `current-pair` publication surface while changing only direct host-native opportunity specialization at the selection layer.
Three reference-only pairs are real host-realization evidence, and the accepted package-level justification decision is recorded in `docs/CORTEX_V2_MEDIATION_JUSTIFICATION_NOTE.md`. This replication note does not by itself authorize implementation.
