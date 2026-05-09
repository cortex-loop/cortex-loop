# Cortex Effectiveness V2 Case Registry Gate 0

Surface: no-live lab/proof evaluator v2 case-registry design

## Summary

Verdict: `pass_cortex_effectiveness_v2_case_registry_gate0`.

This seam turned the measurement-stack diagnosis from `run_20260508T221352Z`
into a concrete v2 evaluator case registry without running live Codex and
without changing product behavior, evaluator scoring, fixtures, hidden verifier
boundaries, root hooks, SRE law, model-visible Cortex text, or candidate policy.

The Gate 0 command was:

```bash
python3 lab/cortex_effectiveness_evaluator.py --v2-case-registry-gate0 --require-pass
```

It wrote:

- `.cortex/live_validation/cortex_effectiveness_v2_case_registry_gate0/v2_case_registry.json`
- `.cortex/live_validation/cortex_effectiveness_v2_case_registry_gate0/gate0_report.json`
- `.cortex/live_validation/cortex_effectiveness_v2_case_registry_gate0/summary.json`

Artifact names: `v2_case_registry.json`, `gate0_report.json`, and
`summary.json`.

Model-I/O path for this seam: `none_lab_proof_only`.

## Preserved Evidence

The v1 evaluator matrix artifact remains `run_20260508T221352Z` with preserved
verdict `failure_silent_perception_contamination`.

No v1 artifact was retroactively rescored. The v2 registry is a future-case
design surface only; it does not change the registered v1 matrix result.

## Registered V2 Cases

The registry defines one immutable `*_v2` case spec for each existing evaluator
family:

- `exactness_evidence_recovery_v2`: requires post-observation correction or
  lifecycle evidence that a simple static reminder cannot supply.
- `truthful_closure_v2`: distinguishes generic success from final reporting of
  actual verification evidence and unresolved obligations.
- `blocker_surfacing_v2`: tests honest unresolved dependency reporting where a
  fake workaround or fabricated progress is tempting but wrong.
- `continuity_after_interruption_v2`: removes prompt/workspace artifacts that
  let silent Cortex beat no-Cortex without active model-visible control.
- `clean_verified_work_control_v2`: remains a zero-intervention control; any
  active model-visible intervention is overcontrol.

Every case carries `case_id`, `task_family`, `measurement_rationale`,
`baseline_expectation`, `simple_hook_challenge`,
`silent_contamination_guard`, `active_policy_signal`, `dominance_gates`,
`acceptance_criteria`, `forbidden_shortcuts`, and `v1_failure_link`.

Every case also carries the mission contract fields:
`executive_function`, `loop_stage`, `control_mode`, `truth_scope`,
`model_io_path`, `product_spine`, and `contraction_implication`.

## Gate 0 Checks

The Gate 0 report passed these checks:

- all five task families are registered;
- all case IDs are unique and end in `_v2`;
- required case fields and mission-contract fields are present;
- `run_20260508T221352Z` remains `failure_silent_perception_contamination`;
- no v1 live case was retroactively rescored;
- the seam is lab-only with `model_io_path=none_lab_proof_only`;
- exactness, truthful closure, and blocker cases are not simple-baseline parity
  by design;
- continuity includes a silent-contamination guard;
- clean control requires zero active model-visible intervention.

The next train is `cortex-effectiveness-v2-live-matrix-gate1`, a no-live seam
to wire the v2 registry into a dry-run/future-live matrix interface. It is not
a live run and not candidate evolution.

## Forbidden Claims

- No behavior lift.
- No exactness value lift.
- No broad Cortex lift.
- No Codex App parity.
- No shipping promotion.
- No product progress.
- No AlphaEvolve-style candidate evolution.
- No live Codex run occurred in this seam.
- No product host behavior changed.
- No model-visible Cortex text changed.
- No evaluator scoring was changed to favor Cortex.
- No current v1 live case was retroactively rescored.
