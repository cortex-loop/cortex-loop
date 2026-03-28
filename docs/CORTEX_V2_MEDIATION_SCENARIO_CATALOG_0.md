# CORTEX_V2_MEDIATION_SCENARIO_CATALOG_0

Date: 2026-03-20
Status: mediation comparative scenario inventory (`planning only`)

## Scope

This document defines the initial scenario inventory for mediation evidence collection.
It does not record results, justify mediation, or authorize implementation work.

## How To Use This Catalog

- Treat this as inventory-first evidence scaffolding.
- Use these scenario ids in mediation run packets and paired run ledgers.
- Keep baseline and mediated comparisons matched by scenario id, host family, task-value rubric, and approval/environment context.
- If a future scenario cannot be compared honestly under the same commitment boundary and evidence surface, exclude it instead of widening this catalog casually.

## Common Defaults

Unless a scenario says otherwise:

- baseline variant: `baseline_non_mediated`
- comparison variant: `experimental_mediated`
- paired evidence unit: one baseline run plus one mediated run with the same `paired_episode_set_id`
- minimum paired-run count expectation: `3`
- host coverage rule: record host splits explicitly; do not pool across hosts first

## Task-Value Rubrics

- `task_value_equal_completion`
  - used when the primary comparison is equal-value completion quality with no truth or scope loss
- `task_value_equal_truth_preservation`
  - used when the primary comparison is equal-value contradiction, blockedness, and certification integrity
- `task_value_equal_host_realization`
  - used when the primary comparison is host-specialized realization at equal task value

## Approval / Environment Context IDs

- `env_local_default`
  - ordinary local environment with no special approval constraint beyond current v2 defaults
- `env_boundary_sensitive`
  - environment where approval or external-boundary conditions are material to the task
- `env_uncertainty_sensitive`
  - environment where evidence uncertainty, contradiction risk, or brake behavior is expected to matter

## Scenario Families

### `thrash_control`

Designed to expose repeated reopen, resume, and control-family oscillation.

Primary lift axes:
- reduced thrashing
- better branch discipline

### `uncertainty_boundary`

Designed to expose uncertainty handling, brake timing, contradiction preservation, and blockedness behavior.

Primary lift axes:
- better uncertainty handling
- lower visible burden at equal task value

### `host_realization`

Designed to expose host-native opportunity use, fallback behavior, and host-specific realization quality.

Primary lift axes:
- better host-specialized realization
- lower visible burden at equal task value

## Scenario Inventory

### `scenario_thrash_reference_01`

- scenario_family: `thrash_control`
- host_family: `reference`
- task_value_rubric_id: `task_value_equal_completion`
- approval_or_environment_context_id: `env_local_default`
- minimum_paired_run_count: `3`
- scenario_goal: evaluate whether mediation reduces repeated branch reopen/resume cycles on a bounded multi-step reference-host episode without reducing lawful task completion
- starting_request_or_event: bounded reference-host task that requires at least one candidate-bearing turn and one follow-up turn
- primary_lift_axes:
  - reduced thrashing
  - better branch discipline
- secondary_lift_axes:
  - lower visible burden at equal task value

### `scenario_thrash_gemini_01`

- scenario_family: `thrash_control`
- host_family: `gemini`
- task_value_rubric_id: `task_value_equal_completion`
- approval_or_environment_context_id: `env_local_default`
- minimum_paired_run_count: `3`
- scenario_goal: evaluate whether mediation reduces repeated control-family oscillation on a bounded Gemini-host lifecycle episode without flattening Gemini-native behavior
- starting_request_or_event: bounded Gemini-host task with at least one branch-sensitive follow-up and observable host lifecycle events
- primary_lift_axes:
  - reduced thrashing
  - better branch discipline
- secondary_lift_axes:
  - better host-specialized realization

### `scenario_thrash_openai_01`

- scenario_family: `thrash_control`
- host_family: `openai`
- task_value_rubric_id: `task_value_equal_completion`
- approval_or_environment_context_id: `env_local_default`
- minimum_paired_run_count: `3`
- scenario_goal: evaluate whether mediation reduces repeated reopen/resume or unnecessary branch proliferation on a bounded OpenAI-host episode without lowering task completion quality
- starting_request_or_event: bounded OpenAI-host task with at least one candidate-bearing turn and one branch-sensitive continuation
- primary_lift_axes:
  - reduced thrashing
  - better branch discipline
- secondary_lift_axes:
  - better host-specialized realization

### `scenario_uncertainty_reference_01`

- scenario_family: `uncertainty_boundary`
- host_family: `reference`
- task_value_rubric_id: `task_value_equal_truth_preservation`
- approval_or_environment_context_id: `env_uncertainty_sensitive`
- minimum_paired_run_count: `3`
- scenario_goal: evaluate whether mediation improves uncertainty handling or brake timing on a bounded reference-host episode without smoothing contradictions or changing commitment truth
- starting_request_or_event: bounded reference-host task with incomplete or conflicting evidence and a realistic uncertified-or-blocked possibility
- primary_lift_axes:
  - better uncertainty handling
- secondary_lift_axes:
  - lower visible burden at equal task value

### `scenario_uncertainty_gemini_01`

- scenario_family: `uncertainty_boundary`
- host_family: `gemini`
- task_value_rubric_id: `task_value_equal_truth_preservation`
- approval_or_environment_context_id: `env_uncertainty_sensitive`
- minimum_paired_run_count: `3`
- scenario_goal: evaluate whether mediation improves Gemini-host uncertainty handling while preserving explicit degradation and contradiction-bearing outcomes
- starting_request_or_event: bounded Gemini-host task with uncertainty-heavy evidence and a plausible brake or blocked outcome
- primary_lift_axes:
  - better uncertainty handling
- secondary_lift_axes:
  - better host-specialized realization

### `scenario_uncertainty_openai_01`

- scenario_family: `uncertainty_boundary`
- host_family: `openai`
- task_value_rubric_id: `task_value_equal_truth_preservation`
- approval_or_environment_context_id: `env_uncertainty_sensitive`
- minimum_paired_run_count: `3`
- scenario_goal: evaluate whether mediation improves OpenAI-host uncertainty handling without altering lawful blockedness or contradiction preservation
- starting_request_or_event: bounded OpenAI-host task with uncertain evidence and realistic blocked or uncertified paths
- primary_lift_axes:
  - better uncertainty handling
- secondary_lift_axes:
  - better host-specialized realization

### `scenario_host_reference_01`

- scenario_family: `host_realization`
- host_family: `reference`
- task_value_rubric_id: `task_value_equal_host_realization`
- approval_or_environment_context_id: `env_boundary_sensitive`
- minimum_paired_run_count: `3`
- scenario_goal: evaluate whether mediation produces any reference-host realization lift without adding burden or branch churn
- starting_request_or_event: bounded reference-host task where host-native opportunity use is observable but not dominant over truth boundaries
- primary_lift_axes:
  - better host-specialized realization
- secondary_lift_axes:
  - lower visible burden at equal task value

### `scenario_host_gemini_01`

- scenario_family: `host_realization`
- host_family: `gemini`
- task_value_rubric_id: `task_value_equal_host_realization`
- approval_or_environment_context_id: `env_boundary_sensitive`
- minimum_paired_run_count: `3`
- scenario_goal: evaluate whether mediation improves Gemini-native opportunity use or fallback selection without host flattening
- starting_request_or_event: bounded Gemini-host task where Gemini-native continuation or candidate-bearing affordances are materially relevant
- primary_lift_axes:
  - better host-specialized realization
- secondary_lift_axes:
  - lower visible burden at equal task value

### `scenario_host_openai_01`

- scenario_family: `host_realization`
- host_family: `openai`
- task_value_rubric_id: `task_value_equal_host_realization`
- approval_or_environment_context_id: `env_boundary_sensitive`
- minimum_paired_run_count: `3`
- scenario_goal: evaluate whether mediation improves OpenAI-native realization quality without pooled averaging that hides OpenAI-specific regressions
- starting_request_or_event: bounded OpenAI-host task where OpenAI-native lifecycle or continuation affordances are materially relevant
- primary_lift_axes:
  - better host-specialized realization
- secondary_lift_axes:
  - lower visible burden at equal task value

## Exclusion Rules

Exclude a scenario from mediation comparison if any of the following are true:

- the same host family cannot be preserved across baseline and mediated runs
- the same task-value rubric cannot be preserved across variants
- the same core commitment boundary cannot be preserved across variants
- the scenario requires changing observe/bind meaning, certification truth, or packet publication meaning to make mediation look better
- the scenario only yields anecdotal single-run evidence

## Inventory Notes

- This catalog is intentionally small and host-split first.
- The initial inventory favors repeated paired evidence over breadth.
- Additional scenarios should be added only when they cover a missing lift axis or a missing host-specific comparison, not just to accumulate volume.
