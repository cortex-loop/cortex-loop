# Cortex Stop-Only Retained Spine Gate 0

Surface: no-live lab/proof architecture contract

## Summary

Verdict: `pass_cortex_stop_only_retained_spine_gate0`.

This seam defines the smallest retained active product spine still worth testing after the composed `userpromptsubmit_stop_taskstandard_spine` failed to earn value. The Stop-only candidate is `stop_only_closure_continuation_spine`.

No live Codex command ran. This is contract readiness only, not Cortex value or product progress.

## Contract

Artifacts:

- `.cortex/live_validation/cortex_stop_only_retained_spine_gate0/stop_only_spine_contract.json` (`stop_only_spine_contract.json`)
- `.cortex/live_validation/cortex_stop_only_retained_spine_gate0/gate0_report.json` (`gate0_report.json`)
- `.cortex/live_validation/cortex_stop_only_retained_spine_gate0/summary.json` (`summary.json`)

The only active product model-I/O path in the future candidate is Codex Stop `hookSpecificOutput` or block stdout continuation. UserPromptSubmit task-standard context is not an active value path in this contract.

Allowed support law is non-model-visible only:

- `TaskStandardSpine` state law;
- `cortex/sre/tool_evidence.py` evidence classification;
- transcript/tool evidence and closure-claim state in the OpenAI Codex hook coordinator.

Excluded active model-I/O or policy paths:

- UserPromptSubmit `hookSpecificOutput.additionalContext`;
- PostToolUse task-standard context;
- PreToolUse denial;
- PermissionRequest policy;
- runtime snapshots;
- AlphaEvolve candidate mutation.

## Evidence Preserved

- `run_20260509T112542Z`: v2 evaluator `failure_no_value`, active Cortex `family_wins=0`, no boundary failures.
- `run_20260509T192719Z`: retained-spine raw `fail` / `mission_contract_error`, corrected replay `failure_silent_perception_contamination`.
- `run_20260510T122608Z`: clean-control replication `pass_clean_control_stable`; no-Cortex, simple-hook, and silent Cortex mean score `3.0`; active Cortex mean score `2.6`.
- `docs/recon/cortex_retained_active_policy_contraction_or_rebuild_decision.md`: `decision_contract_retained_spine_to_stop_only`.
- `docs/recon/cortex_codex_app_cli_task_standard_stop_gating_live_run.md`: prior Stop product model-I/O evidence, `pass_gating_observed`.
- `task_standard_posttooluse_paired_value_live_20260508T120907Z`: PostToolUse paired `failure_no_value`; PostToolUse remains role-demoted.

## Gate 0 Result

The Gate 0 command passed:

`python3 lab/cortex_effectiveness_evaluator.py --stop-only-retained-spine-gate0 --require-pass`

The report records:

- `live_trials_ran=false`;
- `model_io_path=none_lab_proof_only`;
- `active_policy_candidate=stop_only_closure_continuation_spine`;
- `active_product_model_io_path=Codex Stop hookSpecificOutput or block stdout continuation only`;
- simple-hook parity blocks value;
- silent success blocks value;
- UserPromptSubmit active context blocks Stop-only interpretation;
- PostToolUse reactivation blocks interpretation.

## Next Train

Queue `cortex-stop-only-retained-spine-live-gate1`.

Gate 1 must be no-live. It may schedule a future four-arm dry-run matrix for `stop_only_closure_continuation_spine`, but it must not run live. A later live run requires separate explicit approval.

## Forbidden Claims

- No Cortex value.
- No retained-spine value.
- No behavior lift.
- No exactness value lift.
- No broad Cortex lift.
- No Codex App parity.
- No shipping promotion.
- No product progress.
- No PostToolUse reactivation.
- No UserPromptSubmit active value reactivation.
- No AlphaEvolve candidate-evolution permission.
