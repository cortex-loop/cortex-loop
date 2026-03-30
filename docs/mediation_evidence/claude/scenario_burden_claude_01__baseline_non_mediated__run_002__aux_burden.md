# scenario_burden_claude_01__baseline_non_mediated__run_002__aux_burden

Date: 2026-03-30
Status: `reviewed_evidence`

## Scope

This committed AUX burden artifact records one Claude-host baseline-only non-thrash burden measurement within the committed Claude non-thrash paired-run series for mediation evidence review.
It does not justify mediation, authorize implementation work, or imply generic runtime burden beyond the visible intervention count recorded here.

## Header

- date: `2026-03-30`
- status: `reviewed_evidence`
- scenario_id: `scenario_burden_claude_01`
- run_id: `claude_burden_baseline_run_002`
- paired_episode_set_id: `pair_claude_burden_002`

## Variant Metadata

- variant: `baseline_non_mediated`
- host_family: `claude`
- burden_metric: `visible_intervention_steps`
- pair_key: `002`

## Aux Burden Report

- compute_overhead: `0.0`
- memory_overhead: `0.0`
- latency_overhead: `0.0`
- environment_query_cost: `0.0`
- retrieval_cost: `0.0`
- intervention_burden: `3.0`

## Metadata

- scenario_id: `scenario_burden_claude_01`
- run_id: `claude_burden_baseline_run_002`
- paired_episode_set_id: `pair_claude_burden_002`
- host_family: `claude`
- burden_metric: `visible_intervention_steps`

## Derivation

- interaction_sequence: `observe -> check -> resolve`
- step_count: `3`
- note: Visible intervention burden is the exact committed non-thrash interaction-step count for this run.
