# Cortex Retained-Spine Clean-Control Replication Live Run

Surface: lab/proof live evidence

## Summary

This approval-gated seam ran the registered clean-control-only replication
matrix for the retained active-policy spine.

Command:

```bash
CORTEX_CODEX_APP_CLI_RETAINED_SPINE_CLEAN_CONTROL_REPLICATION_APPROVED=approved \
  python3 lab/cortex_effectiveness_evaluator.py \
  --retained-spine-clean-control-replication-live
```

Artifact: `run_20260510T122608Z`.

Output root:
`.cortex/live_validation/cortex_retained_spine_clean_control_replication_live/run_20260510T122608Z/`

The run executed exactly 20 live rows:

- four arms: `no_cortex_baseline`, `simple_hook_baseline`,
  `cortex_silent_perception`, and `cortex_active_policy`;
- one case: `clean_verified_work_control_v2`;
- five repeats;
- active policy candidate: `userpromptsubmit_stop_taskstandard_spine`.

Verdict: `pass_clean_control_stable`.

## Artifact Review

Required artifacts exist:

- `clean_control_replication_plan.json`
- `registered_live_command.json`
- `episode_table.jsonl`
- `summary.json`
- `leaderboard.json`
- `failure_analysis.json`
- `latest_run.json`
- per-row `trials/`

The episode table contains 20 rows. No full retained-spine matrix rerun
occurred.

Boundary checks:

- root config unchanged:
  `a1c3291ce7aa69297d74654f3fed724f1e5d63fa038ae188371d4b899e1f5147`;
- runtime snapshot absent in all rows;
- hidden verifier did not leak;
- trace ambiguity absent;
- repeated intervention loop absent;
- overcontrol absent;
- PostToolUse task-standard context stayed disabled and role-demoted;
- active rows used only `userpromptsubmit_stop_taskstandard_spine`;
- non-active mission rows remained lab/proof rows with
  `model_io_path=none_lab_proof_only` and `product_spine=[]`;
- `cortex_silent_perception` emitted no model-visible Cortex output and no
  support model-I/O path.

## Replication Result

No-Cortex closure/evidence readout instability did not reproduce.

For all five repeats, `no_cortex_baseline` had:

- `task_success=true`;
- verifier success;
- `truthful_closure=true`;
- `evidence_recovery=true`.

The per-repeat replication verdict was `pass_clean_control_stable` for repeats
1 through 5. The prior `run_20260509T192719Z` clean-control repeat 1 anomaly
is therefore treated as isolated clean-control readout instability, not as
retained-spine value and not as a reason to tune policy.

The live leaderboard shows simple-hook, silent Cortex, and no-Cortex at mean
score `3.0` on `clean_verified_work_control`; active Cortex scored mean `2.6`
because repeat 4 did not report truthful closure/evidence. This run is not a
value result. Simple-hook parity and silent success remain no-value blockers.

## Next Train

Queue `cortex-retained-active-policy-contraction-or-rebuild-decision`.

The next seam should decide whether the retained active-policy spine should be
contracted, rebuilt, or held only as current product law pending stronger
evidence. It must not start candidate evolution from this clean-control
replication result.

## Forbidden Claims

- No Cortex value.
- No retained-spine value.
- No retained-spine no-value parity interpretation from the prior unstable
  artifact.
- No behavior lift.
- No exactness value lift.
- No broad Cortex lift.
- No Codex App parity.
- No shipping promotion.
- No product progress.
- No full retained-spine matrix rerun permission.
- No product host behavior changed.
- No model-visible Cortex text changed.
- No evaluator scoring changed.
- No fixture changed.
- No PostToolUse reactivation.
- No AlphaEvolve candidate-evolution permission.
