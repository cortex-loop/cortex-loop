# scenario_host_openai_01__baseline_non_mediated__run_001

Date: 2026-03-20
Status: `reviewed_evidence`

## Scope

This committed run packet records one OpenAI-host baseline-only realization packet for mediation evidence review.
It does not provide comparative mediation evidence, justify mediation, or authorize implementation work.

## Header

- date: 2026-03-20
- status: `reviewed_evidence`
- scenario_id: `scenario_host_openai_01`
- run_id: `openai_host_realization_baseline_run_001`
- paired_episode_set_id: `pair_openai_host_001`

## Variant Metadata

- variant: `baseline_non_mediated`
- host_family: `openai`
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

- starting_request_or_event: `response.output_text.delta` candidate-bearing turn on `openai-host-packet-session-1` followed by `response.completed` with `commitment_id=openai-host-packet-commit-1`
- host_surface: OpenAI-host opportunity selection plus candidate-bearing continuation and commitment-to-eval-packet publication path
- declared_scenario_goal: evaluate whether mediation produces any OpenAI-host realization lift without adding burden or branch churn
- bounded_environment_or_approval_context: OpenAI-host candidate-bearing plus commitment/publication path with lawful provenance, contradiction-preserving degradation handling, the committed OpenAI-lane packet/publication surface, and a bounded host-opportunity set containing `mcp.query`

## Run Outputs

- outcome_summary: The baseline OpenAI-host path preserves the same certified current-pair evaluation packet with explicit contradiction, degradation, and truthful-withheld fields while retaining the generic `seek-context` family without direct host-native specialization.
- branch_trajectory_summary: One OpenAI-native candidate-bearing turn is followed by one full-commitment publication path only; the comparator delta for this pair is the host-opportunity realization choice, not a branch-sequence change.
- uncertainty_or_brake_summary: Contradiction and degradation remain explicit in the committed OpenAI packet example, and `direct_opportunity_specialization_used=0` remains explicit for the baseline side of the pair.
- burden_summary: none
- host_realization_summary: OpenAI-host realization retains the selected family `seek-context` with `direct_opportunity_specialization_used=0` while preserving the same host-opportunity set containing `mcp.query` and the same certified OpenAI `current-pair` publication surface.

## Artifact Refs

- event_trace_refs: `openai-lane:openai-host-packet-candidate-1`
- contradiction_refs: `openai-host-publication-check:OpenAI host publication evidence remains partially withheld`
- degradation_refs: `openai-host-publication-partial`
- aux_burden_refs_if_present: none
- evaluation_packet_refs_if_present: `docs/CORTEX_V2_OPENAI_LANE_PACKET_EXAMPLE_0.md`

## Lift-Axis Observations

### Reduced Thrashing

- observation: Baseline-only packet; no matched mediated run is recorded.
- metric_notes: No repeated reopen/resume metric is available from this packet alone.
- verdict: `insufficient`

### Better Branch Discipline

- observation: Baseline-only packet; no matched mediated run is recorded.
- metric_notes: No comparative branch-discipline evidence exists for this scenario-host cell yet.
- verdict: `insufficient`

### Better Uncertainty Handling

- observation: This packet preserves contradiction and degradation explicitly, but no mediated comparison exists.
- metric_notes: One baseline publication packet does not establish comparative uncertainty lift.
- verdict: `insufficient`

### Lower Visible Burden At Equal Task Value

- observation: The pair holds the same certified completion class and truth boundary, but this packet carries no AUX burden artifact.
- metric_notes: Package-level evidence notes govern whether repeated paired evidence is enough to claim any lower-burden verdict.
- verdict: `insufficient`

### Better Host-Specialized Realization

- observation: This baseline packet keeps the same host-opportunity set containing `mcp.query` but does not directly specialize it.
- metric_notes: The host-realization metric is `direct_opportunity_specialization_used=0` on the baseline side of the pair.
- verdict: `insufficient`

## Exclusions Or Unusable-Pair Notes

- exclusion_status: `none`
- failure_tags: `none`
- notes: This packet is the baseline side of `pair_openai_host_001`. A single packet does not justify mediation; package-level evidence notes govern verdicts.

## Reviewer Note

- reviewer_note: This is baseline-only committed evidence within the committed OpenAI host-realization paired-run series. It is not comparative mediation evidence by itself, does not justify mediation, and package-level evidence notes govern any verdict.
