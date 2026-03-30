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

## Scenario Family Coverage Matrix

| scenario_family_id | current_host_coverage | axis_eligibility | burden_comparable_at_equal_task_value | evidence_state | notes |
| --- | --- | --- | --- | --- | --- |
| thrash_control | reference, gemini, openai current; claude missing | reduced thrashing; better branch discipline; lower visible burden at equal task value | yes | current | Current burden signal lives only here, so package-level burden remains too narrow. |
| uncertainty_boundary | reference, gemini, openai current; claude missing | better uncertainty handling | conditional | current | Current uncertainty signal exists, but it still comes from one family only. |
| host_realization | reference, gemini, openai current; claude missing | better host-specialized realization | conditional | current | Cell-level host-realization signal exists, but Claude breadth is still missing. |
| branch_discipline | none current; reference, openai, claude planned | better branch discipline; reduced thrashing secondary | yes | missing | Needed because current branch-discipline signal derives only from thrash_control. |
| equal_value_burden_non_thrash | none current; reference, openai, claude planned | lower visible burden at equal task value | yes | missing | Needed because current burden signal is confined to thrash_control. |
| uncertainty_expansion | none current; claude or second-family expansion planned | better uncertainty handling | conditional | missing | Needed if one-family uncertainty evidence remains too narrow after J2. |

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

## J2 Gap-Closure Target Inventory

| proposed_scenario_id | scenario_family_id | host_family | primary_axis | minimum_paired_run_count | planned_evidence_state | notes |
| --- | --- | --- | --- | --- | --- | --- |
| scenario_branch_reference_01 | branch_discipline | reference | better branch discipline | 3 | missing | First stable non-thrash branch-discipline target. |
| scenario_branch_openai_01 | branch_discipline | openai | better branch discipline | 3 | missing | Second stable non-thrash branch-discipline target. |
| scenario_branch_claude_01 | branch_discipline | claude | better branch discipline | 3 | missing | Adds the missing Claude branch-discipline line. |
| scenario_burden_reference_01 | equal_value_burden_non_thrash | reference | lower visible burden at equal task value | 3 | missing | First non-thrash equal-value burden family. |
| scenario_burden_openai_01 | equal_value_burden_non_thrash | openai | lower visible burden at equal task value | 3 | missing | Second non-thrash equal-value burden family. |
| scenario_burden_claude_01 | equal_value_burden_non_thrash | claude | lower visible burden at equal task value | 3 | missing | Adds the missing Claude burden line. |
| scenario_host_claude_01 | host_realization | claude | better host-specialized realization | 3 | missing | Expands host-realization breadth onto Claude. |
| scenario_uncertainty_claude_01 | uncertainty_expansion | claude | better uncertainty handling | 3 | missing | First uncertainty expansion target if one-family evidence remains too narrow. |
