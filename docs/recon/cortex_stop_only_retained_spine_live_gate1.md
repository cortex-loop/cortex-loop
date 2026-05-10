# Cortex Stop-Only Retained Spine Live Gate 1

Surface: no-live lab/proof evaluator interface

## Summary

Verdict: `pass_cortex_stop_only_retained_spine_live_gate1`.

This seam wires the Stop-only retained spine candidate `stop_only_closure_continuation_spine` into a future four-arm v2 evaluator matrix without running live Codex. The only active product model-I/O path under future test is Codex Stop `hookSpecificOutput` or block stdout continuation.

UserPromptSubmit and PostToolUse remain excluded from the active value spine.

## Artifacts

- `.cortex/live_validation/cortex_stop_only_retained_spine_live_gate1/stop_only_spine_contract.json`
- `.cortex/live_validation/cortex_stop_only_retained_spine_live_gate1/evaluator_design.json`
- `.cortex/live_validation/cortex_stop_only_retained_spine_live_gate1/v2_case_registry.json`
- `.cortex/live_validation/cortex_stop_only_retained_spine_live_gate1/live_plan.json`
- `.cortex/live_validation/cortex_stop_only_retained_spine_live_gate1/episode_table.jsonl`
- `.cortex/live_validation/cortex_stop_only_retained_spine_live_gate1/summary.json`
- `.cortex/live_validation/cortex_stop_only_retained_spine_live_gate1/leaderboard.json`
- `.cortex/live_validation/cortex_stop_only_retained_spine_live_gate1/failure_analysis.json`
- `.cortex/live_validation/cortex_stop_only_retained_spine_live_gate1/registered_live_command.json`

The dry-run plan contains 60 rows: four arms x five v2 task families x three repeats.

## Gate 1 Result

The Gate 1 command passed:

`python3 lab/cortex_effectiveness_evaluator.py --stop-only-retained-spine-live-gate1 --require-pass`

The refusal-only future live command also stayed no-live:

`python3 lab/cortex_effectiveness_evaluator.py --stop-only-retained-spine-live-matrix`

Registered future live command:

`CORTEX_CODEX_APP_CLI_STOP_ONLY_RETAINED_SPINE_LIVE_APPROVED=approved python3 lab/cortex_effectiveness_evaluator.py --stop-only-retained-spine-live-matrix`

Without approval, the future live command returns `not_run_approval_required`. With approval in this seam, it returns `not_run_registered_future_live_only`; executable live belongs to a later seam.

## Boundaries

- Active rows use `stop_only_closure_continuation_spine` only.
- Active rows use Codex Stop `hookSpecificOutput` or block stdout continuation only.
- UserPromptSubmit `hookSpecificOutput.additionalContext` is disabled as active model I/O.
- PostToolUse task-standard context is disabled and remains role-demoted.
- Non-active rows use `model_io_path=none_lab_proof_only`.
- Simple-hook prompt context remains support metadata only.
- Silent rows emit no model-visible Cortex output and do not claim product I/O.
- Simple-hook parity blocks value.
- Silent success blocks value.
- Dominance gates remain overcontrol, repeated intervention loop, trace ambiguity, hidden-verifier leakage, root config mutation, runtime snapshot loaded, simple baseline parity, and silent perception contamination.

## Next Train

Queue `cortex-stop-only-retained-spine-live-run`.

That seam may replace the refusal-only placeholder with an executable approval-gated live runner. This Gate 1 does not authorize live execution.

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
