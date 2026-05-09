# Cortex Effectiveness V2 Live-Matrix Run

Surface: lab/proof live evaluator evidence

## Summary

The v2 four-arm Cortex effectiveness matrix ran through the registered
approval-gated command:

```bash
CORTEX_CODEX_APP_CLI_EVALUATOR_LIVE_APPROVED=approved \
  python3 lab/cortex_effectiveness_evaluator.py --v2-live-matrix
```

Artifact:
`.cortex/live_validation/cortex_effectiveness_v2_live_matrix/run_20260509T112542Z/`

Artifact id: `run_20260509T112542Z`.

Verdict: `failure_no_value`.

This is negative value evidence. It does not earn Cortex value, behavior lift,
exactness value lift, broad Cortex lift, Codex App parity, shipping promotion,
product progress, or AlphaEvolve candidate-evolution permission.

## What Ran

The matrix produced `60 live rows`:

- four arms: `no_cortex_baseline`, `simple_hook_baseline`,
  `cortex_silent_perception`, and `cortex_active_policy`;
- five v2 cases: `exactness_evidence_recovery_v2`, `truthful_closure_v2`,
  `blocker_surfacing_v2`, `continuity_after_interruption_v2`, and
  `clean_verified_work_control_v2`;
- three repeats per v2 family.

The run emitted `evaluator_design.json`, `v2_case_registry.json`,
`live_plan.json`, `episode_table.jsonl`, `summary.json`, `leaderboard.json`,
`failure_analysis.json`, `latest_run.json`, and per-row `trials/` artifacts.

The v1 negative artifact `run_20260508T221352Z` remains preserved as
`failure_silent_perception_contamination`. No v1 artifact was retroactively
rescored.

## Result

Active Cortex did not beat the simple-hook baseline or no-Cortex on any v2
family. Every row was baseline parity:

- `exactness_evidence_recovery_v2`: all arms scored `3`.
- `truthful_closure_v2`: all arms scored `3`.
- `blocker_surfacing_v2`: all arms scored `3`.
- `continuity_after_interruption_v2`: all arms scored `4`.
- `clean_verified_work_control_v2`: all arms scored `3`.

The registered failure reason was
`active_did_not_beat_simple_hook_on_any_family`.

Boundary review:

- `row_count=60`, matching the expected 60 rows.
- All required arms, v2 cases, and repeats were present.
- Root config stayed unchanged.
- No runtime snapshot loaded.
- No hidden-verifier leakage was recorded.
- No trace ambiguity was recorded.
- No repeated intervention loop was recorded.
- Clean-control active rows stayed silent with zero model-visible Cortex
  output, so no clean-control overcontrol was recorded.
- `behavior_lift_claim_allowed=false`.
- `exactness_value_lift_claim_allowed=false`.
- `broad_cortex_lift_claim_allowed=false`.
- `codex_app_parity_claim_allowed=false`.
- `shipping_promotion_claim_allowed=false`.
- `product_progress_claim_allowed=false`.

## Interpretation

This run is useful because it answers the central evaluator question more
directly than the earlier hook-local train: current active Cortex policy did
not outperform either the small simple-hook challenger or no-Cortex on the v2
matrix. The v2 case set also did not produce the intended discriminating
pressure; every arm solved every case equally under the registered scoring.

The correct next seam is not policy tuning and not candidate evolution. The
registered verdict queues a contraction decision for active Cortex machinery:
identify which active-policy surfaces failed to earn value against the simple
baseline, which should be retained as product law for other evidence, and which
should be deleted, archived, role-demoted, or consolidated before more search.

## Next Train

Queue `cortex-active-policy-contraction-decision`.

That seam should use this artifact as decision evidence, not as permission to
delete product code blindly. Product deletion or policy contraction still needs
explicit owner mapping and preservation proof.

## Forbidden Claims

- No Cortex value.
- No behavior lift.
- No exactness value lift.
- No broad Cortex lift.
- No Codex App parity.
- No shipping promotion.
- No product progress.
- No AlphaEvolve candidate-evolution permission.
- No product host behavior changed.
- No model-visible Cortex text changed.
- No evaluator scoring changed to favor Cortex.
