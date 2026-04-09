# CORTEX_V2_MEDIATION_GEMINI_HOST_REALIZATION_REPLICATION_NOTE_0

Surface: lab

Date: 2026-03-21
Status: `gemini host realization replication law recorded`

## Scope

This note records the fairness and admissibility law for the counted Gemini host-realization pair set.
It does not justify mediation, activate mediation, or widen the allowed comparison surface.

## Counted Pair Set

The counted Gemini host-realization pair set is currently:

- `pair_gemini_host_001`
- `pair_gemini_host_002`
- `pair_gemini_host_003`

## Cross-Pair Distinctness

| pair_id | baseline_run_id | mediated_run_id | session_id | commitment_candidate_id | provenance_artifact_id | contradiction_source_tag | contradiction_summary | degradation_reason_code |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pair_gemini_host_001 | gemini_host_realization_baseline_run_001 | gemini_host_realization_mediated_run_001 | gemini-host-packet-session-1 | gemini-host-packet-candidate-1 / gemini-host-packet-commit-1 | gemini-host-artifact-1 | gemini-host-publication-check | Gemini host publication evidence remains partially withheld | gemini-host-publication-partial |
| pair_gemini_host_002 | gemini_host_realization_baseline_run_002 | gemini_host_realization_mediated_run_002 | gemini-host-packet-session-2 | gemini-host-packet-candidate-2 / gemini-host-packet-commit-2 | gemini-host-artifact-2 | gemini-host-receipt-check | Gemini structured query result omitted one confirmation field | gemini-host-publication-partial-002 |
| pair_gemini_host_003 | gemini_host_realization_baseline_run_003 | gemini_host_realization_mediated_run_003 | gemini-host-packet-session-3 | gemini-host-packet-candidate-3 / gemini-host-packet-commit-3 | gemini-host-artifact-3 | gemini-host-artifact-check | Gemini supporting artifact trace remained partial | gemini-host-publication-partial-003 |

Trace ids must also remain distinct across the series.

## Within-Pair Fairness Law

Every counted pair must preserve:

- `scenario_id=scenario_host_gemini_01`
- `host_family=gemini`
- `task_value_rubric_id=task_value_equal_host_realization`
- `approval_or_environment_context_id=env_boundary_sensitive`
- the same Gemini observe/bind meaning across `content.delta` and `interaction.complete`
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
- Gemini observe/bind semantics
- packet/publication semantics
- contradiction/degradation payload meaning
- truthful-withheld fields
- burden claims
- package-level host-lift scope
- live opportunity specialization, by replacing it with prose-only interpretation

## Outcome

`pair_gemini_host_001`, `pair_gemini_host_002`, and `pair_gemini_host_003` are countable only because the baseline and mediated sides preserve the same certified Gemini `current-pair` publication surface while changing only direct host-native opportunity specialization at the selection layer.
Three Gemini-only pairs are real host-realization evidence, `scenario_host_gemini_01` / `gemini` now has `candidate_positive` cell-level signal for better host-specialized realization, and the accepted package-level justification decision is recorded in `docs/lab/CORTEX_V2_MEDIATION_JUSTIFICATION_NOTE.md`. This replication note does not by itself authorize implementation.
