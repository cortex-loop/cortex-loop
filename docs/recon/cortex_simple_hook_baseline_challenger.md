# Cortex Simple-Hook Baseline Challenger

## Verdict

`pass_cortex_simple_hook_baseline_challenger`

Surface: no-live lab/proof evaluator baseline.

This seam adds the deliberately small independent simple-hook challenger so
rich Cortex cannot claim value by beating only a weak no-hook baseline. It
does not run Codex live and does not change product host behavior, Cortex
model-visible text, fixtures, scoring, SRE law, packet law, root hooks,
hidden-verifier boundaries, or candidate policy.

## What Landed

`lab/cortex_simple_hook_baseline.py` now implements a lab-owned
`simple_hook_baseline` under 500 nonblank noncomment LOC. The module imports no `cortex/**` modules
and is independent of `cortex/core`, `cortex/sre`, and `cortex/aux`.

The baseline is intentionally narrow:

- visible-task standard capture
- one reminder/context path
- one closure check

The baseline explicitly omits Cortex scoring lattice, Core commitment law,
AUX memory, multi-hook policy search, hidden verifier access, and
fixture-specific scoring. Its closure check accepts explicit evidence or
blocker reporting and rejects unsupported closure.

## Gate 0

CLI flag: `--simple-hook-baseline-gate0`.

`lab/cortex_effectiveness_evaluator.py --simple-hook-baseline-gate0 --require-pass`
writes the no-live proof report under
`.cortex/live_validation/cortex_simple_hook_baseline_challenger/`:

- `simple_hook_baseline.json`
- `gate0_report.json`
- `summary.json`

The report proves the LOC budget, import independence, runnable
capture/reminder/closure examples, no live trials, no value/product claims,
and valid `simple_hook_baseline` evaluator arm metadata.

## Evaluator Boundary

The `simple_hook_baseline` evaluator arm is now present and runnable. The
future `--live-matrix` path is no longer blocked on a missing simple hook, but
it still does not execute live in this seam. With approval it now defers to
`cortex-executive-effectiveness-evaluator-live-matrix-run`.

Simple-hook parity remains no-value. Silent perception success remains
no-value. Dominance gates remain pre-scoring blockers. Positive value results
still require user review.

## Next Train

Queue `cortex-executive-effectiveness-evaluator-live-matrix-run`.

That seam should run only through the registered approval-gated evaluator
command/env and should produce the first real four-arm matrix: no Cortex,
simple hook, silent Cortex, and active Cortex.

## Forbidden Claims

No live Codex run occurred. This seam does not earn behavior lift, does not
earn exactness value lift, does not earn broad Cortex lift, does not earn
Codex App parity, does not earn shipping promotion, and does not earn product
progress. No product host behavior changed. No model-visible Cortex text
changed. No AlphaEvolve-style candidate mutation occurred.

In explicit claim terms: this seam does not earn exactness value lift, does not earn broad Cortex lift, does not earn Codex App parity, does not earn shipping promotion, and does not earn product progress. No model-visible Cortex text changed.
