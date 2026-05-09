# Cortex Effectiveness V2 Live-Matrix Gate 1

## Verdict

`pass_cortex_effectiveness_v2_live_matrix_gate1`.

This no-live lab/proof seam wires the v2 evaluator case registry into a dry-run
future four-arm evaluator matrix. It does not run Codex, does not implement the
v2 live runner, and does not change product host behavior, model-visible Cortex
text, evaluator scoring, hidden verifier boundaries, root hooks, SRE law,
fixtures, or candidate policy.

## Evidence

The Gate 1 command is:

```bash
python3 lab/cortex_effectiveness_evaluator.py --v2-live-matrix-gate1 --require-pass
```

It writes `.cortex/live_validation/cortex_effectiveness_v2_live_matrix_gate1/`
with:

- `evaluator_design.json`
- `v2_case_registry.json`
- `live_plan.json`
- `episode_table.jsonl`
- `summary.json`
- `leaderboard.json`
- `failure_analysis.json`

The dry-run plan consumes the v2 registry from
`cortex-effectiveness-v2-case-registry-gate0`, validates it, and schedules
`60 dry-run rows`: four arms, five v2 families, and three repeats. The arms are
`no_cortex_baseline`, `simple_hook_baseline`, `cortex_silent_perception`, and
`cortex_active_policy`.

The v2 case ids are:

- `exactness_evidence_recovery_v2`
- `truthful_closure_v2`
- `blocker_surfacing_v2`
- `continuity_after_interruption_v2`
- `clean_verified_work_control_v2`

Rows use deterministic row ids containing v2 `case_id`, repeat, and arm.
Workspace seeds are matched across arms for the same case and repeat while
remaining row-isolatable for the later live seam. Every row carries registry
provenance/hash, dominance gates, approval metadata, mission contract fields,
and `live_trials_ran=false`.

## Preserved Negative Evidence

The v1 evaluator matrix artifact remains `run_20260508T221352Z` with preserved
verdict `failure_silent_perception_contamination`. This seam does not replace
`LIVE_MATRIX_CASES`, does not alter the v1 planner, and does not retroactively
rescore any v1 artifact.

Simple-hook parity and silent-perception success remain no-value boundaries.
Dominance gates still apply before scoring: overcontrol, repeated intervention
loop, trace ambiguity, hidden-verifier leakage, root config mutation, runtime
snapshot loading, simple baseline parity, and silent perception contamination.

## Future Live Shape

The future v2 live command is registered only as approval metadata:

```bash
CORTEX_CODEX_APP_CLI_EVALUATOR_LIVE_APPROVED=approved \
  python3 lab/cortex_effectiveness_evaluator.py --v2-live-matrix
```

Registered approval env: `CORTEX_CODEX_APP_CLI_EVALUATOR_LIVE_APPROVED=approved`.

Without approval, the future live surface must return
`not_run_approval_required`. The v2 live execution itself belongs to
`cortex-effectiveness-v2-live-matrix-run`, not this seam.

## Forbidden Claims

This earns v2 live-matrix interface readiness only. It does not earn Cortex
value, behavior lift, exactness value lift, broad Cortex lift, Codex App parity,
shipping promotion, product progress, or AlphaEvolve candidate-evolution
permission.

## Next Train

Queue `cortex-effectiveness-v2-live-matrix-run`.
