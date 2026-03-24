# scenario_thrash_openai_01__experimental_mediated__run_003__aux_burden

Date: 2026-03-24
Status: `reviewed_evidence`

## Scope

This committed AUX burden artifact records one OpenAI-host experimental mediated thrash burden measurement within the committed OpenAI thrash paired-run series for mediation evidence review.
It does not justify mediation, authorize implementation work, or imply generic runtime burden beyond the visible intervention count recorded here.

## Header

- date: `2026-03-24`
- status: `reviewed_evidence`
- scenario_id: `scenario_thrash_openai_01`
- run_id: `openai_thrash_mediated_run_003`
- paired_episode_set_id: `pair_openai_thrash_003`

## Variant Metadata

- variant: `experimental_mediated`
- host_family: `openai`
- burden_metric: `visible_intervention_steps`
- pair_key: `003`

## Aux Burden Report

- compute_overhead: `0.0`
- memory_overhead: `0.0`
- latency_overhead: `0.0`
- environment_query_cost: `0.0`
- retrieval_cost: `0.0`
- intervention_burden: `3.0`

## Metadata

- scenario_id: `scenario_thrash_openai_01`
- run_id: `openai_thrash_mediated_run_003`
- paired_episode_set_id: `pair_openai_thrash_003`
- host_family: `openai`
- burden_metric: `visible_intervention_steps`

## Derivation

- branch_sequence: `open -> suspend -> merge`
- step_count: `3`
- note: Visible intervention burden is the exact committed branch-operation count for this run.
