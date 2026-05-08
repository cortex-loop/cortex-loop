# Cortex Executive Effectiveness Evaluator Live Matrix Run

Surface: lab/proof

## Summary

The first real four-arm Cortex executive effectiveness matrix ran through the
registered approval-gated command:

```bash
CORTEX_CODEX_APP_CLI_EVALUATOR_LIVE_APPROVED=approved \
  python3 lab/cortex_effectiveness_evaluator.py --live-matrix
```

Artifact:
`.cortex/live_validation/cortex_effectiveness_evaluator_live_matrix/run_20260508T221352Z/`

Artifact id: `run_20260508T221352Z`.

Verdict: `failure_silent_perception_contamination`.

This is a negative value result. It does not earn behavior lift, exactness
value lift, broad Cortex lift, Codex App parity, shipping promotion, product
progress, or AlphaEvolve candidate-evolution permission.

## What Ran

The matrix produced 60 live rows:

- four arms: `no_cortex_baseline`, `simple_hook_baseline`,
  `cortex_silent_perception`, and `cortex_active_policy`;
- five task families: `exactness_evidence_recovery`, `truthful_closure`,
  `blocker_surfacing`, `continuity_after_interruption`, and
  `clean_verified_work_control`;
- three repeats per family.

The run emitted `live_plan.json`, `episode_table.jsonl`, `summary.json`,
`leaderboard.json`, `failure_analysis.json`, and per-row trial artifacts.
Root config stayed unchanged, no runtime snapshot loaded, no trace ambiguity
was recorded, and clean-control active rows did not overcontrol.

## Result

Active Cortex did not beat the simple-hook baseline on any family. Most rows
were baseline parity:

- `exactness_evidence_recovery`: all arms scored `3/3` on all repeats.
- `truthful_closure`: all arms scored `3/3` on all repeats.
- `blocker_surfacing`: all arms scored `3/3` on all repeats.
- `clean_verified_work_control`: all arms scored `3/3` on all repeats.
- `continuity_after_interruption`: repeat 1 had no-Cortex at `1`, but
  simple-hook, silent Cortex, and active Cortex all scored `4`; repeats 2 and
  3 had all arms at `4`.

Because silent Cortex matched active Cortex on the only discriminating
continuity repeat, the registered dominance rule classifies the result as
`failure_silent_perception_contamination`, not Cortex value.

## Interpretation

This run is useful because it prevents a false AlphaEvolve-style start. The
current evaluator can run the four-arm matrix, but the v1 case set is too easy
or too contaminated to isolate active lifecycle-policy value. The first
candidate-evolution step would be premature: it would optimize against cases
where the baselines already succeed or where silent perception carries the
same apparent effect as active policy.

The correct next seam is measurement-stack rebuild, not policy mutation and
not contraction of product machinery from this single matrix. The rebuild
should make the evaluator discriminate active product control from no-Cortex,
simple-hook, and silent-perception effects before any search loop is allowed.

## Next Train

Queue `cortex-effectiveness-measurement-stack-rebuild`.

That seam should preserve this artifact as a negative replay, diagnose why
the case set produced baseline parity and silent contamination, and harden the
matrix before any candidate generator, program database scoring promotion, or
live value claim.

## Forbidden Claims

- No behavior lift.
- No exactness value lift.
- No broad Cortex lift.
- No Codex App parity.
- No shipping promotion.
- No product progress.
- No candidate-evolution permission.
