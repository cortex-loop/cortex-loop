# Cortex Executive Effectiveness Evaluator Gate 0

Date: 2026-05-08  
Surface: no-live evaluator architecture gate  
Verdict: `pass_cortex_executive_effectiveness_evaluator_gate0`.

## Summary

This seam stops treating PostToolUse as the center of the strategy and defines
the evaluator Cortex should use before any more actuator work.

The Gate 0 artifact is produced by
`lab/cortex_effectiveness_evaluator.py --gate0`. It writes
`evaluator_design.json`, `gate0_report.json`, and `summary.json` under
`.cortex/live_validation/cortex_effectiveness_evaluator_gate0/`.

This is no-live lab/proof infrastructure. It changes no product host behavior,
model-visible text, SRE law, matcher threshold, fixture scoring, root hook,
hidden-verifier boundary, PreToolUse denial, PermissionRequest policy,
output-law code, typed-intervention code, or host-runtime extraction.

## Research Anchor

The design takes the AlphaEvolve lesson seriously without pretending Cortex is
already an AlphaEvolve loop.

- DeepMind describes AlphaEvolve as LLM-generated code changes grounded by
  automated evaluators and a retained program database:
  https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/
- The AlphaEvolve white paper is the external anchor for treating evaluation
  cascades, multiple metrics, and population history as part of the optimizer:
  https://arxiv.org/abs/2506.13131
- DeepMind's impact update reinforces the practical constraint: this style is
  useful only where measurable objectives and baseline comparisons exist:
  https://deepmind.google/blog/alphaevolve-impact/

For Cortex, that means the next phase must optimize against a hard evaluator,
not against a hand-defended hook path.

## Hard Objective

Cortex earns value only when an active lifecycle policy improves next model
behavior over both `no_cortex_baseline` and `simple_hook_baseline` without
overcontrol or boundary failure.

The required evaluator arms are:

- `no_cortex_baseline`
- `simple_hook_baseline`
- `cortex_silent_perception`
- `cortex_active_policy`

The simple-hook challenger is mandatory. It must be small, transparent,
independent of `cortex/core`, `cortex/sre`, and `cortex/aux`, and targeted under about 500 LOC in the later implementation seam. It may use task-standard
capture, one reminder/context path, and one closure check. It may not use the
Cortex scoring lattice.

Silent perception is a negative control. If silent succeeds equally or improves
over no Cortex, that is tie/no value or measurement contamination, not Cortex
value.

Simple-hook parity blocks Cortex value. Beating no hooks is insufficient if a
small direct hook can do the same job.

## Task Families

The initial evaluator families are:

- exactness/evidence recovery
- truthful closure
- blocker surfacing
- continuity after interruption
- clean verified-work controls

## Candidate Policies

The active policy candidates registered by Gate 0 are:

- Stop-only
- UserPromptSubmit plus Stop
- PostToolUse plus Stop
- lifecycle-composed policy
- PreToolUse later only after host contract verification

PostToolUse remains one candidate policy. It is no longer the research center.

## Dominance Gates

The evaluator must apply dominance gates before value scoring. Any of these
blocks value claims:

- overcontrol
- repeated intervention loop
- trace ambiguity
- hidden-verifier leakage
- root config mutation
- runtime snapshot loaded
- simple baseline parity
- silent perception contamination

Gate 0 includes synthetic decision rows proving that simple-hook parity, silent
success, overcontrol, trace ambiguity, root mutation, runtime snapshot, and
hidden-verifier leakage all block active value.

## Contraction Obligation

Once the general evaluator owns the evidence path, stale PostToolUse proof
surfaces become contraction candidates. The first role-demotion candidates are:

- PostToolUse-specific Gate 0 modes for phase-aware timing, firing boundary,
  overcontrol, context-loop trace, and exactness-only paired value;
- historical PostToolUse recons and artifacts, including
  `cortex_codex_app_cli_posttooluse_task_standard_exactness_only_paired_value_live_probe.md`
  and `task_standard_posttooluse_paired_value_live_20260508T120907Z`;
- old hook-local harness ownership in
  `lab/codex_app_cli_hook_native_behavior_comparison.py`.

Deletion is not authorized by this seam. The rule is role-demote or archive only
after the new evaluator can preserve the historical evidence and failure
classes.

## End-of-Part Decision

Gate 0 passed because it defines:

- a hard objective;
- four required arms;
- the mandatory simple-hook challenger;
- initial task families;
- lifecycle policy candidates;
- baseline/silent/active scoring rules;
- dominance gates;
- contraction obligations; and
- a staged AlphaEvolve-style future loop without starting it.

Queue `cortex-executive-effectiveness-evaluator-build`.

The next seam should build the automatic paired evaluator with a dedicated
episode table, `evaluator_design.json`, `episode_table.jsonl`, `summary.json`,
and `leaderboard.json`. It should not extend the old PostToolUse-specific
harness as the owner.

## Forbidden Claims

- No behavior lift is earned.
- No exactness value lift is earned.
- No broad Cortex lift is earned.
- No Codex App parity claim is earned.
- No shipping promotion is earned.
- No live Codex run is authorized.
- No AlphaEvolve-style mutation loop is authorized until the evaluator exists
  and passes no-live proof.
