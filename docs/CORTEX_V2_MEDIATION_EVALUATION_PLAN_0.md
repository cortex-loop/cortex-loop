# CORTEX_V2_MEDIATION_EVALUATION_PLAN_0

Date: 2026-03-20
Status: active comparative evidence plan for future mediation audit (`planning only`)

## Scope

This document defines the comparative evidence plan required before any mediation implementation seam may begin.
Mediation remains unimplemented and unjustified; this document does not approve or start mediation code.

## Authority

- `docs/CORTEX_V2_MEDIATION_JUSTIFICATION_NOTE.md`
- `docs/CORTEX_V2_IMPLEMENTATION_STATUS_NOTE.md`
- `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
- `docs/CORTEX_V2_SRE_2.md`
- `docs/CORTEX_V2_PHASE_GATES_2.md`

## One-paragraph verdict

The current repo state permits mediation only as a later experimental possibility, not as active implementation work. This plan converts that blocker into a comparative evidence program: define how mediated and non-mediated behavior would be compared on the same scenarios, what artifacts would count as measurable lift, and what evidence gaps would still block implementation. It does not widen the truth court, change runtime behavior, or mutate phase/gate truth.

## Scope and Non-Scope

Planning-only scope:
- define the comparative question
- define experimental units and the baseline comparison
- define required lift axes, evidence shapes, and stop rules
- define the artifact set required before any future mediation implementation seam

Explicit non-scope:
- no runtime changes
- no mediation implementation
- no packet reinterpretation
- no truth-court widening
- no automatic approval of mediation
- no phase-gate or correspondence updates from this document alone

## Comparative Question

On the same bounded scenarios, with the same host slices, the same core certification boundary, and the same evaluation artifacts, does a future mediated SRE variant produce measurable lift over the current non-mediated baseline?

The comparison is always:
- mediated variant
- versus the currently landed non-mediated system
- on matched scenarios
- with the same success rubric and evidence surfaces

## Experimental Units

### Scenario

One scenario is one bounded task or lifecycle episode with:
- a fixed starting request or event context
- one identified host surface
- one declared task-value rubric
- one bounded environment/approval context
- one evaluation lens for branch, uncertainty, burden, and host realization outcomes

### Run

One run is one execution of one scenario under one variant:
- baseline non-mediated
- or a future mediated experimental variant

The run must preserve:
- the same host family
- the same initial task framing
- the same core commitment boundary
- the same evidence/publication surface

### Episode Set

One episode set is a paired collection of baseline and mediated runs over the same scenario set. One-off anecdotes are not enough; each claimed lift axis requires repeated paired evidence rather than a single curated transcript.

## Baseline and Future Comparison Target

Baseline system:
- the currently landed Cortex v2 system
- mediation absent / off-by-default
- current host-native slices and current SRE behavior unchanged

Future mediated comparison target:
- a later experimental branch that changes only the allowed SRE mediation surface
- no change to commitment truth
- no change to core certification law
- no change to host observe/bind meaning
- no change to packet publication meaning except where separately justified outside this plan

Existing landed proof-packet and latency evidence gates remain context only. They do not count as mediation lift evidence by themselves.

## Required Lift Axes

| Lift axis | Measurable artifact(s) | Metric(s) | Minimum evidence shape | Insufficient | Candidate positive signal |
| --- | --- | --- | --- | --- | --- |
| reduced thrashing | paired run ledger, branch/event trace excerpts, control-family sequence summaries | repeated branch reopen/resume loops, repeated control-family oscillation, redundant intervention count per completed scenario | matched baseline vs mediated runs on the same scenario set with explicit trace excerpts showing intervention sequence | one anecdote, one transcript, or only qualitative claims like "felt smoother" | repeated lower oscillation/retry counts without lower task completion or hidden escalation |
| better branch discipline | branch-state tables, pending-goal/branch registry summaries, merge/resume notes | stale branch count, orphaned branch count, unnecessary branch proliferation per completed scenario | paired scenario table showing branch trajectory and final branch state under both variants | only end-state screenshots, or no explicit branch trajectory | repeated fewer orphaned/stale branches with equal task value and no main-task loss |
| better uncertainty handling | uncertainty/brake traces, contradiction/degradation refs, evaluation packets or equivalent outcome tables | avoidable uncertainty churn, delayed brake, repeated uncertified/blocked surprises, contradiction-preserving handling quality | paired uncertainty-heavy scenarios with preserved contradiction/degradation evidence and explicit outcome comparison | subjective confidence claims, or evidence that smooths contradictions away | repeated earlier lawful brake/escalation or fewer avoidable uncertainty loops without truth smoothing |
| lower visible burden at equal task value | AUX burden reports, interruption counts, paired outcome summaries | visible burden count/cost per completed scenario, interruption count at equal outcome class | paired burden table holding scenario value constant and reporting both burden and outcome | lower burden on easier tasks, or lower burden with worse results | repeated lower visible burden while holding task-value outcome class constant |
| better host-specialized realization | host-split comparison tables, host-opportunity usage notes, per-host outcome summaries | stronger host-native opportunity use, fewer generic fallbacks, per-host completion/burden change | per-host paired evidence, not one pooled average across all hosts | evidence from only one host, or flattened averages that hide host differences | repeated lift on at least one host without requiring host flattening or causing regressions to be hidden |

## Guardrails

Any future mediated comparison remains subject to the current packet and justification limits:

- mediation remains experimental / off-by-default
- mediation may not affect commitment truth
- mediation may only modify `Q_t^{base}` into `Q_t^{final}` within the allowed SRE surface
- mediation must remain sparse, host-aware, and neutral-dominance-preserving
- mediation must satisfy the anti-hub law
- mediation may not become a second truth court
- baseline and mediated runs must keep core law, hard boundaries, and host observe/bind semantics fixed while measuring the executive difference

## Required Evaluation Artifacts Before Any Future Implementation Seam

Before a mediation implementation seam may open, the repo should have a concrete evidence package containing at least:

- one scenario catalog describing the compared scenario set and host coverage using `docs/CORTEX_V2_MEDIATION_SCENARIO_CATALOG_0.md`
- one paired run ledger for baseline vs mediated runs using `docs/CORTEX_V2_MEDIATION_RUN_PACKET_TEMPLATE_0.md`
- one per-axis comparison table covering all five required lift axes
- one burden comparison surface for equal-value tasks
- one host-split comparison surface rather than only pooled results
- one short narrative evidence note stating whether each axis is negative, neutral, mixed, or candidate-positive
- one mediation evidence taxonomy surface using `docs/CORTEX_V2_MEDIATION_FAILURE_TAXONOMY_0.md`
- one repo-local command/report path showing how the comparison artifacts were generated or checked

The evidence package may live in docs, reproducible reports, or committed evaluation artifacts, but it must be inspectable from the repo and must preserve contradiction-bearing failures instead of reporting only wins.

## Stop Rule

If no mediation-vs-non-mediation axis shows measurable lift under this plan, mediation remains blocked and no implementation seam may open.

## Next-Step Rule

This plan enables evidence-collection planning only. It does not authorize mediation code, packet edits, default-on behavior, or phase/gate status changes. If candidate-positive evidence is collected later, the next honest step is a justification update reviewing that evidence, not immediate implementation by inertia.
