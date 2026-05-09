# Cortex Retained-Spine Measurement-Stack Remediation

Surface: lab/proof evaluator remediation

## Summary

This no-live seam diagnoses the corrected retained-spine replay from
`run_20260509T192719Z`.

The raw live artifact remains preserved:

- raw verdict: `fail`;
- raw failure reason: `mission_contract_error`;
- raw mission-contract errors: 15;
- affected raw rows: `simple_hook_baseline`;
- raw artifact is not rewritten or rescored in place.

The corrected no-live replay from the materialization remediation remains:

- corrected mission-contract errors: 0;
- corrected replay verdict: `failure_silent_perception_contamination`;
- corrected replay failure reason: `silent_perception_beat_no_cortex`;
- row count: 60;
- all four arms, five v2 task families, and three repeats present;
- PostToolUse task-standard context disabled and role-demoted;
- active rows remain `userpromptsubmit_stop_taskstandard_spine`;
- root config unchanged;
- no runtime snapshot loaded;
- no hidden-verifier leakage recorded.

## Gate 0

Command:

```bash
python3 lab/cortex_effectiveness_evaluator.py \
  --retained-spine-measurement-stack-remediation-gate0 --require-pass
```

Output root:
`.cortex/live_validation/cortex_retained_spine_measurement_stack_remediation_gate0/`

Artifacts:

- `measurement_diagnosis.json`
- `silent_contamination_diagnosis.json`
- `episode_discriminability.json`
- `gate0_report.json`
- `summary.json`

Gate 0 passed:
`pass_cortex_retained_spine_measurement_stack_remediation_gate0`.

## Diagnosis

The corrected replay is blocked by measurement contamination, not retained-spine
value.

Pinned episode evidence:

- `clean_verified_work_control_v2` repeat 1 is `silent_contamination`;
- scores were `no_cortex_baseline=1`, `simple_hook_baseline=3`,
  `cortex_silent_perception=3`, and `cortex_active_policy=3`;
- `exactness_evidence_recovery_v2` repeat 2 is `active_underperformance`;
- no retained-spine family wins are present.

Family discriminability:

- `blocker_surfacing`: `baseline_parity_too_easy`;
- `clean_verified_work_control`: `control_instability`;
- `continuity_after_interruption`: `baseline_parity_too_easy`;
- `exactness_evidence_recovery`: `retained_spine_underperformance`;
- `truthful_closure`: `baseline_parity_too_easy`.

Silent-arm isolation checks passed:

- no `cortex_silent_perception` row emitted model-visible Cortex output;
- no `cortex_silent_perception` row used a support model-I/O path;
- silent rows remain lab/proof mission rows with
  `model_io_path=none_lab_proof_only` and `product_spine=[]`.

Interpretation: the contaminated clean-control row is a no-Cortex
closure/evidence reporting instability. It is not evidence that retained
Cortex improved output, and it is not a clean `failure_no_value` parity result
because the silent negative control beat no-Cortex.

## Next Train

Queue `cortex-retained-spine-clean-control-stability-gate0`.

This is a measurement-stability seam, not a policy-tuning seam. It should
determine whether the clean verified-work control can produce stable no-Cortex
readout without rerunning the retained-spine value matrix or changing product
policy.

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
- No live rerun permission.
- No product host behavior changed.
- No model-visible Cortex text changed.
- No evaluator scoring changed to favor Cortex.
- No fixture changed to favor Cortex.
- No PostToolUse reactivation.
- No AlphaEvolve candidate-evolution permission.
