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
- paired_episode_set_id: `pending_pair_openai_host_001`

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
- host_surface: OpenAI-host observe/bind plus candidate-bearing continuation and commitment-to-eval-packet publication path
- declared_scenario_goal: evaluate whether mediation improves OpenAI-native opportunity use or fallback selection without host flattening
- bounded_environment_or_approval_context: OpenAI-host candidate-bearing plus commitment/publication path with lawful provenance, contradiction-preserving degradation handling, and the committed OpenAI-lane packet/publication surface

## Run Outputs

- outcome_summary: The landed OpenAI-host path produces a certified current-pair evaluation packet with explicit contradiction, degradation, and truthful-withheld fields after an OpenAI-native candidate-bearing prelude.
- branch_trajectory_summary: One OpenAI-native candidate-bearing turn is followed by one full-commitment publication path only; no matched branch-lift comparison is recorded in this baseline packet.
- uncertainty_or_brake_summary: Contradiction and degradation remain explicit in the committed OpenAI packet example; no comparative uncertainty claim is made.
- burden_summary: none
- host_realization_summary: OpenAI-host observe/bind, candidate-bearing continuation, commitment, and publication surfaces are exercised end to end without any pooled host claim.

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

- observation: Baseline-only packet; no equal-value burden comparison is recorded.
- metric_notes: No committed AUX burden artifact exists for this packet.
- verdict: `insufficient`

### Better Host-Specialized Realization

- observation: This packet exercises the OpenAI-host candidate-bearing and publication path end to end, but no mediated comparison exists.
- metric_notes: OpenAI-host realization remains descriptive only until a matched mediated run exists.
- verdict: `insufficient`

## Exclusions Or Unusable-Pair Notes

- exclusion_status: `none`
- failure_tags: `none`
- notes: This packet is intentionally baseline-only and reserves `pending_pair_openai_host_001` for a future honest comparison if one is ever earned.

## Reviewer Note

- reviewer_note: This is baseline-only committed evidence, not comparative mediation evidence, and it does not justify mediation or authorize any implementation seam.
