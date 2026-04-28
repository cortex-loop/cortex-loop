# Constraint-Fidelity Lab Findings

Surface: lab

This note records lab evidence only. It is not Cortex product truth, not an
operational status registry, and not a broad usefulness claim.

## Website Fixture Finding

The website fixture produced a falsifiable constraint-fidelity arc:

- smoke: raw Claude failed certification `3/3`; single-repair kernel certified
  `2/3`;
- prediction: the single-repair failures would mostly be `turn_budget_cutoff`,
  not unclear repair tickets or ignored repair tickets;
- confirmation: unchanged Claude `n=10` had raw failures `9/10`, single-repair
  kernel certifications `8/10`, and both kernel failures were classified as
  `turn_budget_cutoff`;
- ablation: bounded loop repair with the same per-turn budget certified `10/10`.

Narrow finding: single-shot factual repair is structurally insufficient for some
multi-violation states, while bounded check-repair-recheck loops can converge by
regenerating concrete tickets from fresh workspace evidence after each repair
turn.

Repo-hygiene therefore skips the single-repair comparator. The single-repair
policy was already tested on the website fixture at `n=10`, found ceiling-bound
by turn budget, and then beaten by the loop policy without changing the
per-repair budget.

## Runtime Baseline

Website loop runtime across the Claude `n=10` ablation:

- mean: `120.6s`
- median: `118.3s`
- nearest-rank p95 / max: `162.0s`

Repo-hygiene loop runtime should be compared against this baseline. If mean
repo-hygiene loop runtime exceeds four times this mean, about `482s`, runtime
scaling must be surfaced as a finding before any product discussion.

## Source Artifacts

- `.cortex/live_validation/website_constraint_fidelity/claude/n10_prediction.json`
- `.cortex/live_validation/website_constraint_fidelity/claude/n10_failure_classification.json`
- `.cortex/live_validation/website_constraint_fidelity/claude/summary.json`
- `.cortex/live_validation/website_constraint_fidelity/claude/kernel_loop_interpretation.json`
- `.cortex/live_validation/repo_hygiene_constraint_fidelity/claude/prediction.json`
- `.cortex/live_validation/repo_hygiene_constraint_fidelity/claude/summary.json`
- `.cortex/live_validation/website_constraint_fidelity/codex/prediction.json`
- `.cortex/live_validation/website_constraint_fidelity/codex/summary.json`

## Repo-Hygiene Fixture Result

The first repo-hygiene smoke exposed an under-specified fixture rule: the model
was told to create a commit with an allowed scope, but the repair fact did not
name the allowed scopes. The fixture rule and repair fact were made concrete
before the corrected smoke and promotion run.

Corrected Claude repo-hygiene `n=10` result:

- raw Claude failed certification `10/10`;
- loop kernel certified `10/10`;
- first-prompt hash matched across variants;
- no Cortex marker appeared in prompts or repair tickets;
- loop conversions spanned `checkpoint_commit`, `dirty_worktree`,
  `handoff`, and `rule_evidence`;
- loop runtime mean was about `46.6s`, below the four-times website-loop
  threshold;
- formal promotion was not earned under the predeclared composite gate because
  mean mechanical-score lift was `25` points, below the `30` point threshold.

Narrow interpretation: the loop converted every repo-hygiene certification
failure in this run, but the score-lift gate is under tension with procedural
fixtures where raw Claude can perform most mechanical work while still failing
hard closure constraints.

## Codex Website Parity Smoke

Codex parity started as a host-generality test of the same bounded loop policy:
`raw_host` versus `kernel_loop_cortex`, max three repair turns, byte-identical
first prompts, and no Cortex marker. The predeclared website prediction was raw
Codex uncertified `9/10`, loop certified `9/10`, and mechanical-score lift at or
above `30` points.

The first smoke exposed a harness-only observation bug: Codex command events
reported shell reads as `/bin/zsh -lc 'cat ...'`, while the deterministic adapter
recognized only bare shell names. That parser was fixed without changing
invariants, fixture files, repair tickets, loop policy, or scoring, and the smoke
was rerun from the amended implementation commit.

Corrected Codex website smoke result:

- raw Codex certified `3/3`;
- loop Codex certified `3/3`;
- first-prompt hash matched across variants;
- no Cortex marker appeared in prompts or repair tickets;
- raw mean mechanical score was `1.0`;
- loop mean mechanical score was `1.0`;
- mechanical-score lift was `0`;
- experiment status was `void_fixture_not_discriminative`.

Falsification check: the cross-host generalization claim was not falsified by a
valid raw fixture plus loop failure, because the raw fixture validity gate failed.
The website fixture is currently non-discriminative for Codex after correct
command-read observation, so the train stopped before website `n=10` and before
repo-hygiene live runs, as predeclared.

Narrow interpretation: prior Claude website failures were partly host-specific
or fixture-calibrated to Claude. On Codex, the existing website fixture does not
test the loop mechanism because raw Codex already satisfies the mechanical
constraints.

## Claims

Earned lab claim:

- The generic invariant loop improved the Claude website fixture over the
  single-repair kernel in the bounded `n=10` ablation.

Observed lab fact, not a promotion claim:

- The generic invariant loop converted Claude repo-hygiene fixture
  certification failures in the bounded `n=10` run, but the predeclared
  score-lift gate was not met.
- Codex website parity smoke is void/non-discriminative: raw Codex certified
  `3/3`, so no Codex loop lift or cross-host generalization claim is earned.

Still forbidden:

- Cortex broadly works.
- Cortex improves websites generally.
- Repo-hygiene lift is proven.
- Codex CLI parity is proven.
- The bounded check-repair loop generalizes from Claude to Codex.
- Repair is fully solved.
- The product layer is adoption-ready.
