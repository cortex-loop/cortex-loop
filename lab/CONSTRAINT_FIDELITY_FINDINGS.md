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

## Claims

Earned lab claim:

- The generic invariant loop improved the Claude website fixture over the
  single-repair kernel in the bounded `n=10` ablation.

Observed lab fact, not a promotion claim:

- The generic invariant loop converted Claude repo-hygiene fixture
  certification failures in the bounded `n=10` run, but the predeclared
  score-lift gate was not met.

Still forbidden:

- Cortex broadly works.
- Cortex improves websites generally.
- Repo-hygiene lift is proven.
- Codex CLI parity is proven.
- Repair is fully solved.
- The product layer is adoption-ready.
