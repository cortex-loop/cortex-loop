# Cortex Overnight Evaluator Automation Hardening

Date: 2026-05-08  
Surface: internal automation guardrail  
Verdict: `overnight_evaluator_loop_guarded`.

## Summary

This seam turns the local overnight Codex automation into a repo-governed
evaluator loop contract instead of a free-form coding prompt.

The entrypoint is:

```bash
python3 internal/automation/cortex_overnight_loop.py --once
```

The command reads current truth from `internal/truth/cortex_status.json`,
classifies the next allowed evaluator task, records bloat/contraction metrics,
and writes one local digest under:

```text
.cortex/automation/overnight/YYYY-MM-DD/digest.md
```

Routine overnight digests are ignored local artifacts, not active docs. A recon
is still required only when durable evidence, strategy, or status truth changes.

## Automation Contract

Each cycle must:

- acquire a local lock;
- inspect branch cleanliness and sync state;
- allow clean `main` or a managed session branch only;
- read the current `next_product_train`;
- allow only evaluator-authorized work;
- preserve the no-Cortex / simple-hook / silent / active comparison;
- preserve simple-hook parity and silent success as no-value outcomes;
- apply dominance gates before value scoring;
- stop for user review on strategic judgment, product law revision,
  fixture/scoring changes, external paid credentials, or claims beyond the
  registered evaluator.

Codex CLI live runs are allowed only when current truth registers them inside
the evaluator plan. External paid APIs and service-lane credentials remain disallowed.

## Bloat Discipline

Every cycle records:

- LOC added and deleted;
- changed files;
- new policy paths;
- whether duplicate policy was removed;
- whether contraction debt increased.

The runner also fails closed when a candidate touches hidden scoring, fixtures,
Core law, workflow gates, or the old PostToolUse-specific harness instead of
the general evaluator episode table.

Any policy candidate that loses to the simple baseline twice creates a
contraction candidate for the machinery it depends on.

## AlphaEvolve Boundary

This seam does not start candidate mutation.

It only records the bounded candidate schema needed later:

- candidate id;
- parent id;
- policy candidate;
- changed files;
- mutation reason;
- metrics;
- score;
- failure class;
- contraction implication.

Candidate mutation remains deferred until
`cortex-executive-effectiveness-evaluator-build` lands and the evaluator can
score synthetic replay, historical replay, and live matrix evidence.

## Next Train

Keep `cortex-executive-effectiveness-evaluator-build` as the next product
train.

The overnight loop is now safe enough to run around that train because it can
block dirty main, forbidden surfaces, unsafe live runs, fixture/scoring edits,
and simple-baseline no-value cases before they become unattended repo drift.

## Forbidden Claims

- No behavior lift is earned.
- No exactness value lift is earned.
- No broad Cortex lift is earned.
- No Codex App parity claim is earned.
- No shipping promotion is earned.
- No product host behavior changed.
- No model-visible text changed.
- No evaluator live matrix was run.
- No AlphaEvolve-style mutation loop is authorized yet.
