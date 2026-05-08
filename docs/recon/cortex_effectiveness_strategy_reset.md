# Cortex Effectiveness Strategy Reset

Date: 2026-05-08  
Surface: product strategy reset  
Verdict: `queue_cortex_executive_effectiveness_evaluator_gate0`.

## Summary

Cortex should regroup before any more PostToolUse task-standard value work. The
recent line did improve proof visibility, but it did not improve measured
effectiveness. The approval-gated paired live probe
`task_standard_posttooluse_paired_value_live_20260508T120907Z` produced
`failure_no_value`: active PostToolUse context beat silent in `0/5` mismatch
pairs against the registered `4/5` threshold.

That result is not a Cortex-wide failure. It is a stop sign for the current
PostToolUse-only exactness value path.

## Diagnosis

The last train was not an AlphaEvolve-style optimization loop.

An optimization loop would have had a hard objective first, an automatic
evaluator, multiple candidate policies, empirical selection, retained
population/history, and aggressive iteration against the same score.

The actual PostToolUse line was different:

- one plausible hook path was selected early;
- live failures exposed missing measurement boundaries one at a time;
- no-live gates repaired the most recent failure class;
- the hard paired evaluator arrived late;
- the final paired result showed no active-over-silent value.

Since the PostToolUse task-standard stack merge, the line added about 20K lines
and deleted about 1.5K lines across product, lab, docs, and tests. Some of that
was necessary measurement discipline. But the mass center shifted toward proof
repair rather than an empirical search over better executive policies.

## What Still Counts

The following evidence remains useful:

- Codex-native PostToolUse `hookSpecificOutput.additionalContext` can reach the
  model.
- Product controls can remain silent.
- Repeated context loops can be blocked.
- Trace joining and root/runtime isolation are now much better specified.
- The paired evaluator correctly treats silent success as `tie_no_value`, not
  Cortex value.

These are prerequisites, not product effectiveness.

## What Stops

The following work should stop unless a later evaluator proves a new reason:

- same-shape PostToolUse exactness live reruns;
- PostToolUse text tuning after `failure_no_value`;
- policy tuning that tries to force context emission on the same fixture;
- claiming exactness value lift from active-arm feasibility;
- treating more PostToolUse gates as progress toward Cortex effectiveness.

PostToolUse can stay as one candidate actuator in a broader lifecycle policy
set. It should not remain the research center.

## Cortex-Level Objective

The next evaluator should target Cortex's actual product loop:

model or host event -> task/executive state -> intervention decision -> host
action or silence -> better next model behavior.

The objective should compare policies on paired tasks using:

- task completion or exactness success delta;
- truthful closure delta;
- evidence-recovery delta;
- false-intervention and overcontrol rate;
- repeated-intervention loop rate;
- root/runtime/hidden-boundary integrity;
- user-visible friction or latency where measurable.

No policy gets credit when the silent or baseline arm succeeds equally well.

## Candidate Policies

The Gate 0 evaluator should register at least these policy families:

- baseline no Cortex product hooks;
- silent perception with Cortex state capture but no model-visible output;
- Stop-only truthful-closure continuation;
- UserPromptSubmit plus Stop;
- PostToolUse plus Stop;
- PreToolUse motor inhibition once the host contract is reverified;
- lifecycle-composed policy using more than one hook only when the state law
  justifies the composition.

The point is to search over lifecycle policies, not defend one hook.

## Next Train

Queue `cortex-executive-effectiveness-evaluator-gate0`.

That seam should be no-live and should define:

- a hard Cortex effectiveness score;
- candidate lifecycle policies and allowed deltas;
- paired baseline/silent/active design;
- replay use of existing evidence, including the PostToolUse negative result;
- kill rules for overcontrol, trace ambiguity, root mutation, runtime snapshots,
  and hidden verifier leakage;
- a contraction rule requiring stale PostToolUse proof paths to be retired,
  archived, or role-demoted as the new evaluator becomes the owner.

## Forbidden Claims

- No behavior lift is earned.
- No exactness value lift is earned.
- No broad Cortex lift is earned.
- No Codex App parity claim is earned.
- No shipping promotion is earned.
- No live Codex run is authorized by this reset.
- No product behavior, model-visible text, SRE law, matcher threshold, fixture
  scoring, root hook, hidden-verifier boundary, Sinkhorn/transport, PreToolUse
  denial, PermissionRequest policy, output-law centralization, typed
  intervention pressure, or host-runtime extraction changed.
