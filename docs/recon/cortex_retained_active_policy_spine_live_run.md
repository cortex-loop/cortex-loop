# Cortex Retained Active-Policy Spine Live Run

Surface: lab/proof live evaluator evidence

## Summary

The retained active-policy spine matrix ran through the registered
approval-gated command:

```bash
CORTEX_CODEX_APP_CLI_RETAINED_SPINE_LIVE_APPROVED=approved \
  python3 lab/cortex_effectiveness_evaluator.py --retained-spine-live-matrix
```

Artifact:
`.cortex/live_validation/cortex_retained_active_policy_spine_live_matrix/run_20260509T192719Z/`

Artifact id: `run_20260509T192719Z`.

CLI flag: `--retained-spine-live-matrix`.

Registered verdict: `fail`.

Failure reason: `mission_contract_error`.

This is not retained-spine value evidence. It is a live matrix materialization
underfit: the harness treated the `simple_hook_baseline` arm's
`lab_simple_hook_prompt_context` model-I/O path as product-facing without a
product spine, so mission-contract validation failed before value scoring.

## What Ran

The matrix produced `60` live rows:

- four arms: `no_cortex_baseline`, `simple_hook_baseline`,
  `cortex_silent_perception`, and `cortex_active_policy`;
- five v2 cases: `exactness_evidence_recovery_v2`, `truthful_closure_v2`,
  `blocker_surfacing_v2`, `continuity_after_interruption_v2`, and
  `clean_verified_work_control_v2`;
- three repeats per v2 family.

The run emitted `retained_spine_contract.json`, `evaluator_design.json`,
`v2_case_registry.json`, `live_plan.json`, `episode_table.jsonl`,
`summary.json`, `leaderboard.json`, `failure_analysis.json`,
`latest_run.json`, and per-row `trials/` artifacts.

The active arm used only `userpromptsubmit_stop_taskstandard_spine`.
PostToolUse task-standard context stayed disabled and role-demoted; no row
contained the PostToolUse task-standard context flag.

## Boundary Review

- `row_count=60`, matching the expected 60 rows.
- All required arms, v2 cases, and repeats were present.
- Root config stayed unchanged.
- No runtime snapshot loaded.
- No hidden-verifier leakage was recorded.
- No clean-control overcontrol was recorded.
- No PostToolUse task-standard context was reactivated.
- `run_20260508T221352Z` remains preserved as
  `failure_silent_perception_contamination`.
- `run_20260509T112542Z` remains preserved as `failure_no_value`.

The mission-contract failure occurred on the 15 `simple_hook_baseline` rows:
`product-facing model_io_path requires product_spine`.

## Interpretation

This run cannot be interpreted as retained-spine success, retained-spine
failure, or no-value parity. The live rows exist, but the evaluator's mission
contract made the simple-hook support arm look product-facing. That is a lab
materialization bug and must be repaired before scoring or rerunning the
retained-spine matrix.

The correct next seam is no-live materialization remediation. It should repair
the simple-hook mission contract and replay this artifact without changing
product behavior, scoring, fixtures, hidden-verifier boundaries, root hooks,
SRE law, model-visible Cortex text, active policy, PostToolUse policy, or
candidate policy.

## Next Train

Queue `cortex-retained-spine-live-matrix-materialization-remediation`.

Do not rerun live, tune policy, or start candidate evolution until the
materialization bug is fixed and the existing artifact is replayed under the
corrected contract.

## Forbidden Claims

- No Cortex value.
- No behavior lift.
- No exactness value lift.
- No broad Cortex lift.
- No Codex App parity.
- No shipping promotion.
- No product progress.
- No AlphaEvolve candidate-evolution permission.
- No retained-spine value verdict.
- No product host behavior changed.
- No model-visible Cortex text changed.
- No evaluator scoring changed to favor Cortex.
