# Cortex Executive Effectiveness Evaluator Live Gate 1

## Verdict

`pass_cortex_executive_effectiveness_evaluator_live_gate1`

Surface: no-live lab/proof evaluator live-interface gate.

This seam registers the future approval-gated live evaluator matrix without
running Codex and without changing product behavior, model-visible text,
fixtures, scoring, SRE law, packet law, root hooks, hidden-verifier boundaries,
or candidate policy.

## What Landed

`lab/cortex_effectiveness_evaluator.py --live-gate1 --require-pass` now writes
the `--live-gate1 --require-pass` no-live report:

- `evaluator_design.json`
- `live_plan.json`
- `episode_table.jsonl`
- `summary.json`
- `leaderboard.json`
- `failure_analysis.json`

The dry-run plan schedules a 60-row dry-run live matrix:

- 4 arms: `no_cortex_baseline`, `simple_hook_baseline`,
  `cortex_silent_perception`, `cortex_active_policy`
- 5 task families / five task families: exactness/evidence recovery, truthful closure, blocker
  surfacing, continuity after interruption, clean verified-work control
- 3 repeats / three repeats per family/arm

Every dry-run row preserves the mission objective contract:
`executive_function`, `loop_stage`, `control_mode`, `truth_scope`,
`model_io_path`, `product_spine`, and `contraction_implication`.

## Registered Future Live Command

Future live execution is registered but not run:

`CORTEX_CODEX_APP_CLI_EVALUATOR_LIVE_APPROVED=approved`
`python3 lab/cortex_effectiveness_evaluator.py --live-matrix`

```bash
CORTEX_CODEX_APP_CLI_EVALUATOR_LIVE_APPROVED=approved \
  python3 lab/cortex_effectiveness_evaluator.py --live-matrix
```

Running `--live-matrix` without the approval env returns
`not_run_approval_required`. Running it with approval still returns
`not_run_live_matrix_execution_deferred_until_simple_hook_challenger` until the
simple-hook baseline exists.

## Boundary Rules Preserved

- Simple-hook parity remains no-value and blocks Cortex value.
- Silent perception success remains no-value; it is contamination/no-value, not a Cortex win.
- dominance gates remain pre-scoring blockers. Dominance gates apply before scoring: overcontrol, repeated intervention
  loop, trace ambiguity, hidden-verifier leakage, root config mutation, runtime
  snapshot loaded, simple baseline parity, and silent perception contamination.
- Positive value results require user review.
- AlphaEvolve mutation loop remains disabled; AlphaEvolve-style mutation remains disabled.

## Next Train

Queue `cortex-simple-hook-baseline-challenger`.

That seam should implement the deliberately small independent baseline. The
future live matrix should not run until the simple-hook challenger is present
and runnable as an evaluator arm.

## Forbidden Claims

No live Codex run occurred. This seam does not earn behavior lift, does not earn exactness value lift, does not earn broad Cortex lift, does not earn Codex App parity, does not earn shipping promotion, and does not earn product progress. No product host behavior changed. No AlphaEvolve-style candidate mutation occurred.
