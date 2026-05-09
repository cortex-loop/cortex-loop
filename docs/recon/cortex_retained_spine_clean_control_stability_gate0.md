# Cortex Retained-Spine Clean-Control Stability Gate 0

Surface: lab/proof evaluator remediation

## Summary

This no-live seam diagnoses the isolated clean-control contamination in the
retained-spine corrected replay from `run_20260509T192719Z`.

The raw live artifact remains preserved:

- raw verdict: `fail`;
- raw failure reason: `mission_contract_error`;
- raw row count: 60;
- raw artifact is not rewritten or rescored in place.

The corrected replay remains preserved:

- corrected replay verdict: `failure_silent_perception_contamination`;
- corrected replay failure reason: `silent_perception_beat_no_cortex`;
- PostToolUse task-standard context disabled and role-demoted;
- active rows remain `userpromptsubmit_stop_taskstandard_spine`;
- root config unchanged;
- no runtime snapshot loaded;
- no hidden-verifier leakage recorded.

## Gate 0

Command:

```bash
python3 lab/cortex_effectiveness_evaluator.py \
  --retained-spine-clean-control-stability-gate0 --require-pass
```

Output root:
`.cortex/live_validation/cortex_retained_spine_clean_control_stability_gate0/`

Artifacts:

- `clean_control_stability_report.json`
- `no_cortex_readout_diagnosis.json`
- `arm_isolation_report.json`
- `gate0_report.json`
- `summary.json`

Gate 0 passed:
`pass_cortex_retained_spine_clean_control_stability_gate0`.

## Diagnosis

`clean_verified_work_control_v2` repeat 1 is classified as
`no_cortex_closure_readout_instability`.

Pinned row evidence:

- `no_cortex_baseline` had `task_success=true`;
- `no_cortex_baseline` had `v2_verifier_exit_code=0`;
- `no_cortex_baseline` had `truthful_closure=false`;
- `no_cortex_baseline` had `evidence_recovery=false`;
- `simple_hook_baseline`, `cortex_silent_perception`, and
  `cortex_active_policy` each reported task success, truthful closure, and
  evidence recovery.

The evidence depth is `stdout_stderr_and_verifier_artifacts`, not
`metrics_only`. The no-Cortex stdout shows the model reported
`command not found: python` and did not report the successful `python3` fallback
that the other arms reported.

Silent-arm isolation remains clean:

- no `cortex_silent_perception` row emitted model-visible Cortex output;
- no `cortex_silent_perception` row used a support model-I/O path;
- silent rows remain lab/proof mission rows with
  `model_io_path=none_lab_proof_only` and `product_spine=[]`.

Interpretation: the contaminating clean-control row is no-Cortex
closure/evidence readout instability. It is not retained-spine value, and it
is not clean retained-spine no-value parity.

## Next Train

Queue `cortex-retained-spine-clean-control-replication-gate1`.

The next seam should register a narrow clean-control replication check before
any retained-spine value interpretation, live matrix rerun, policy tuning, or
candidate evolution.

## Forbidden Claims

- No Cortex value.
- No retained-spine value.
- No retained-spine no-value parity interpretation.
- No behavior lift.
- No exactness value lift.
- No broad Cortex lift.
- No Codex App parity.
- No shipping promotion.
- No product progress.
- No live matrix rerun permission.
- No product host behavior changed.
- No model-visible Cortex text changed.
- No evaluator scoring changed to favor Cortex.
- No fixture changed to favor Cortex.
- No PostToolUse reactivation.
- No AlphaEvolve candidate-evolution permission.
