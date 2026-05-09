# Cortex Retained-Spine Live-Matrix Materialization Remediation

Surface: lab/proof evaluator remediation

## Summary

This no-live seam repairs the retained-spine live-matrix materialization bug
from artifact `run_20260509T192719Z`.

Raw registered result preserved:

- verdict: `fail`;
- failure reason: `mission_contract_error`;
- affected rows: 15 `simple_hook_baseline` rows;
- raw error: `product-facing model_io_path requires product_spine`;
- raw support path: `lab_simple_hook_prompt_context`.

The bug was in evaluator mission metadata, not product behavior: the lab
simple-hook support context was stored as `mission_objective.model_io_path`,
which made the mission-contract validator treat a support baseline as
product-facing Cortex model I/O.

## Repair

The retained-spine executable matrix now records non-active arms as lab/proof
mission rows:

- `no_cortex_baseline`: `model_io_path=none_lab_proof_only`, `product_spine=[]`;
- `simple_hook_baseline`: `model_io_path=none_lab_proof_only`, `product_spine=[]`;
- `cortex_silent_perception`: `model_io_path=none_lab_proof_only`, `product_spine=[]`.

The simple-hook prompt context remains preserved as support metadata:
`support_model_io_path=lab_simple_hook_prompt_context`.

The active arm remains unchanged:
`model_io_path=codex_hooks_UserPromptSubmit_Stop_hookSpecificOutput_or_block_stdout`
with the retained `userpromptsubmit_stop_taskstandard_spine` product spine.
Active model-I/O path:
`codex_hooks_UserPromptSubmit_Stop_hookSpecificOutput_or_block_stdout`.

## Gate 0 Replay

Command:

```bash
python3 lab/cortex_effectiveness_evaluator.py \
  --retained-spine-materialization-remediation-gate0 --require-pass
```

Output root:
`.cortex/live_validation/cortex_retained_spine_live_matrix_materialization_remediation_gate0/`

Artifacts:

- `materialization_repair_report.json`
- `corrected_replay_report.json`
- `gate0_report.json`
- `summary.json`

Gate 0 passed:
`pass_cortex_retained_spine_live_matrix_materialization_remediation_gate0`.

Replay facts:

- raw `fail` / `mission_contract_error` is preserved;
- raw mission errors before repair: 15;
- corrected mission errors after repair: 0;
- row count: 60;
- all four arms, five v2 task families, and three repeats remain present;
- active rows remain `userpromptsubmit_stop_taskstandard_spine`;
- PostToolUse task-standard context remains disabled and role-demoted;
- root config remains unchanged;
- no runtime snapshot loaded;
- no hidden-verifier leakage was recorded.

Corrected replay verdict:
`failure_silent_perception_contamination`.

Corrected replay failure reason:
`silent_perception_beat_no_cortex`.

## Interpretation

This seam earns materialization repair, not Cortex value. The original live
artifact remains a registered `fail` under its raw recorded result. The
corrected no-live replay removes the mission-contract underfit and shows that
the retained-spine matrix is now blocked by measurement contamination, not by
simple-hook product-spine metadata.

The result does not authorize a live rerun or policy tuning. The next seam
should diagnose why silent Cortex beat no-Cortex in the corrected retained
spine replay before any retained-spine value interpretation, product policy
change, candidate database, bounded mutation generator, or AlphaEvolve-style
automation loop.

## Next Train

Queue `cortex-retained-spine-measurement-stack-remediation`.

## Forbidden Claims

- No Cortex value.
- No retained-spine value.
- No behavior lift.
- No exactness value lift.
- No broad Cortex lift.
- No Codex App parity.
- No shipping promotion.
- No product progress.
- No product host behavior changed.
- No model-visible Cortex text changed.
- No evaluator scoring changed to favor Cortex.
- No fixture changed to favor Cortex.
- No PostToolUse reactivation.
- No AlphaEvolve candidate-evolution permission.
