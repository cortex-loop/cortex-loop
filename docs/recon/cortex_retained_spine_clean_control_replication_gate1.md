# Cortex Retained-Spine Clean-Control Replication Gate 1

Surface: lab/proof evaluator readiness

## Summary

This no-live seam registers a narrow future clean-control replication check for
the retained-spine instability found in `run_20260509T192719Z`.

The prior diagnosis remains unchanged:

- raw retained-spine live verdict: `fail`;
- raw retained-spine live failure reason: `mission_contract_error`;
- corrected replay verdict: `failure_silent_perception_contamination`;
- corrected replay reason: `silent_perception_beat_no_cortex`;
- clean-control repeat 1 classification:
  `no_cortex_closure_readout_instability`.

The instability is not Cortex value and not retained-spine no-value parity. It
is a measurement/readout question: no-Cortex passed the verifier on
`clean_verified_work_control_v2` repeat 1 but under-reported closure/evidence,
while the simple-hook, silent Cortex, and active Cortex arms reported it.

## Gate 1

Command:

```bash
python3 lab/cortex_effectiveness_evaluator.py \
  --retained-spine-clean-control-replication-gate1 --require-pass
```

Output root:
`.cortex/live_validation/cortex_retained_spine_clean_control_replication_gate1/`

Artifacts:

- `clean_control_replication_plan.json`
- `episode_table.jsonl`
- `gate1_report.json`
- `summary.json`
- `registered_live_command.json`

Gate 1 passed:
`pass_cortex_retained_spine_clean_control_replication_gate1`.

## Registered Replication Plan

The dry-run plan contains exactly 20 rows:

- four arms: `no_cortex_baseline`, `simple_hook_baseline`,
  `cortex_silent_perception`, and `cortex_active_policy`;
- one case: `clean_verified_work_control_v2`;
- five repeats;
- matched workspace seeds across arms for each repeat;
- `live_trials_ran=false`.

Active rows use only `userpromptsubmit_stop_taskstandard_spine`. PostToolUse
task-standard context remains disabled and role-demoted in every planned row.

The seam reuses the existing v2 case materialization and retained-spine row
metadata. It does not create a new fixture, change evaluator scoring, tune
product policy, or reinterpret old artifacts.

## Future Live Command

The future live command is registered but not executable in this seam:

```bash
CORTEX_CODEX_APP_CLI_RETAINED_SPINE_CLEAN_CONTROL_REPLICATION_APPROVED=approved \
  python3 lab/cortex_effectiveness_evaluator.py \
  --retained-spine-clean-control-replication-live
```

Without the approval environment variable, the command returns
`not_run_approval_required`. With the approval variable in this seam, it returns
`not_run_registered_future_live_only`.

## Future Verdict Handling

- If no-Cortex is stable across replication and all boundaries stay clean,
  queue `cortex-retained-active-policy-contraction-or-rebuild-decision`.
- If no-Cortex closure/evidence readout instability reproduces, queue
  `cortex-retained-spine-clean-control-readout-remediation`.
- If the silent arm leaks model-visible or support effects, queue
  `cortex-retained-spine-silent-arm-isolation-remediation`.
- If the active arm overcontrols clean work, queue retained-spine boundary
  remediation.
- Boundary failures, missing artifacts, root mutation, runtime snapshot,
  hidden-verifier leakage, or PostToolUse reactivation dominate all
  interpretation.

## Next Train

Queue `cortex-retained-spine-clean-control-replication-live-run`.

That future seam may implement and run the registered replication command only
after explicit approval. It must remain clean-control-only and must not rerun
the full retained-spine matrix.

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
- No live result interpretation.
- No full retained-spine matrix rerun permission.
- No product host behavior changed.
- No model-visible Cortex text changed.
- No evaluator scoring changed.
- No fixture changed.
- No PostToolUse reactivation.
- No AlphaEvolve candidate-evolution permission.
