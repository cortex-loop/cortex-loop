# Cortex Executive Effectiveness Evaluator Build

Date: 2026-05-08  
Surface: no-live lab/proof evaluator build  
Verdict: `pass_cortex_executive_effectiveness_evaluator_build`.

## Summary

This seam builds the no-live evaluator owner for Cortex effectiveness. It does
not run live trials and does not mutate product host behavior. The evaluator is
now a dedicated artifact path rather than another PostToolUse-specific harness
extension.

Build command:

```bash
python3 lab/cortex_effectiveness_evaluator.py --build --require-pass
```

Build output:

```text
.cortex/live_validation/cortex_effectiveness_evaluator_build/
```

Required artifacts are now emitted:

- `evaluator_design.json`
- `episode_table.jsonl`
- `summary.json`
- `leaderboard.json`

## Evaluator Contract

The build preserves the four required arms:

- `no_cortex_baseline`
- `simple_hook_baseline`
- `cortex_silent_perception`
- `cortex_active_policy`

The build passes only because:

- every scoreable synthetic episode has all four arms;
- the simple-hook baseline is present;
- simple-hook parity blocks Cortex value;
- silent perception success blocks Cortex value;
- dominance gates block value before scoring;
- the historical PostToolUse paired-value artifact
  `task_standard_posttooluse_paired_value_live_20260508T120907Z` is preserved
  as `failure_no_value`;
- the historical replay is not counted as a new live run.

## Overnight Runner Contract

The local overnight runner is also hardened so the 9-hour automation cannot
drift into prompt-only execution:

- each cycle writes a cycle state file and `latest_cycle_state.json`;
- cycle state records cycle id, branch, allowed commands, start/end time,
  blocker, commit, and pull-request fields;
- code enforces the 22:00-07:00 overnight window;
- repeated clean-main ready cycles for the same untouched next train are blocked
  as no-op repetition;
- every ready evaluator-build cycle includes the allowed command
  `python3 lab/cortex_effectiveness_evaluator.py --build --require-pass`;
- non-test LOC growth is budgeted outside evaluator-build seams;
- policy/lab LOC growth outside evaluator-build requires a contraction
  candidate;
- registered live work must name exact live command/env pairs before the runner
  will allow it.

## AlphaEvolve Boundary

This is still not an AlphaEvolve-style mutation loop. It builds the measurement
surface needed before candidate evolution:

- no candidate mutation is authorized;
- no program database selection is active;
- no live matrix is run;
- no policy is promoted.

The next seam may build the no-live live-matrix interface, but it must still
keep live execution approval-gated and exact-command registered.

## Next Train

Queue `cortex-executive-effectiveness-evaluator-live-gate1`.

That seam should implement the approval-gated live evaluator interface and
exact registered command/env contract. It should not start candidate mutation
or claim Cortex value.

## Forbidden Claims

- No behavior lift is earned.
- No exactness value lift is earned.
- No broad Cortex lift is earned.
- No Codex App parity claim is earned.
- No shipping promotion is earned.
- No product host behavior changed.
- No model-visible text changed.
- No live Codex run occurred.
- No AlphaEvolve-style mutation loop is authorized yet.
