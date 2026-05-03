# Cortex Executive Runtime Program Spec

Surface: product planning

This program spec turns the executive-runtime roadmap into an auditable
research and engineering program. It defines the first concrete control objects,
state transitions, falsification tasks, and acceptance thresholds needed to
move Cortex from a correct strategic frame to a buildable runtime executive
layer. It is subordinate to `docs/CORTEX.md`, `internal/truth/cortex_status.json`,
`docs/CORTEX_EXECUTIVE_RUNTIME_TRACKER.md`, and
`docs/CORTEX_EXECUTIVE_RUNTIME_ROADMAP.md`.

This document is not implementation, not packet law, and not shipping truth.
It is the spec a team of cognitive scientists, mathematicians, and senior
developers should be able to critique before implementation begins.

## Program Claim

The next product program should prove or falsify this claim:

```text
Cortex can improve a model's runtime executive behavior by tracking expected
uncertainty reduction from forward commitments, comparing it to realized
evidence/continuity progress, and using the resulting control pressure to bias
route/brake/intervention decisions before false closure appears.
```

The claim is deliberately not "Cortex can produce better warning messages."
Visible messages are downstream. The first question is whether Cortex can make
unsupported forward motion more expensive while preserving useful checking,
asking, inspection, repair, and honest partial progress.

## Formal Control Objects

The first implementation program needs these objects. Names may change in code,
but their roles should not be blurred.

### `ForwardCommitment`

An event-level observation that the model or host has increased task liability.

Required fields:

- `commitment_id`: stable within the session.
- `source_event_ref`: host/runtime event that created the commitment.
- `claim_span_ref`: optional model-output span or structured event reference.
- `commitment_kind`: one of `completion`, `verification`, `artifact_change`,
  `plan_commitment`, `diagnosis`, `capability_claim`, `deferred_followup`.
- `assertiveness`: `low | medium | high`.
- `scope`: `local_step | task | branch | session | external_world`.
- `opened_at_step`: monotonic session step.

Opening rule:

- high-assertiveness completion or verification claims open immediate
  expectation records;
- hedged diagnoses and explicit questions open low or suspended expectations;
- pure questions, refusals, or explicit inability statements should not open
  forward-commitment debt unless they contradict an already-open obligation.

### `ExpectationRecord`

A bounded liability record created by a forward commitment.

Required fields:

- `expectation_id`
- `commitment_id`
- `weight`: `0.0..1.0`
- `horizon`: `immediate | next_step | deferred | waiting_on_user`
- `satisfaction_classes`: set of allowed payoff classes.
- `opened_at_step`
- `due_at_step`: optional for deferred/waiting cases.
- `suspension_state`: `active | waiting_on_user | deferred | fulfilled | expired`
- `remaining_weight`: `0.0..1.0`
- `evidence_refs`: bounded tuple of event IDs that paid down the record.

Horizon rule:

- `immediate`: completion, verification, or "done" claims.
- `next_step`: asserted plan movement that should be checked by the next tool,
  artifact, or continuity update.
- `deferred`: explicit "still running", "will check after X", or legitimate
  wait with a named future trigger.
- `waiting_on_user`: direct user question or missing-input request.

### `EvidenceProgress`

A normalized view of what actually happened after the expectation opened.

Allowed payoff classes:

- `meaningful_evidence`: tests ran, artifacts changed, file state inspected,
  external record checked, or tool output materially supports the claim.
- `continuity_progress`: pending goal reduced, branch returned, blocker named,
  or task thread re-established.
- `commitment_certified`: commitment moved to supported/certified state.
- `liability_retracted`: model explicitly retracted or narrowed a claim.
- `blocker_surfaced`: model named the missing condition or obstacle.
- `waiting_released`: user answered a waiting-on-user obligation.
- `stream_only`: output happened but did not pay uncertainty down.
- `degradation`: failure, contradiction, warning, or evidence reversal.

### `ExpectationLedger`

A bounded session-local collection of active and recently resolved
`ExpectationRecord`s.

Limits:

- maximum active records: 8;
- maximum retained resolved records: 12;
- oldest low-weight records are evicted first;
- no raw model text beyond bounded span refs or short normalized labels;
- no AUX publication in phase 1.

### `ResolutionDeficitState`

A summary of expected uncertainty reduction that has not arrived.

Required fields:

- `due_weight`: total active expectation weight currently due.
- `fulfilled_weight`: weight paid down in the current summary window.
- `overdue_weight`: due weight past horizon with no payoff.
- `suspended_weight`: waiting or deferred weight that should not count as debt.
- `relief_weight`: retraction/narrowing/blocker-surfacing payoff.
- `negative_prediction_error`: clipped deficit scalar.
- `dominant_deficit_kind`: optional `verification | completion | continuity |
  preservation | capability | mixed`.

Candidate formula:

```text
raw_deficit =
  max(0, due_weight - fulfilled_weight - relief_weight)
  + overdue_weight

negative_prediction_error =
  clip01(raw_deficit / max(0.1, due_weight + overdue_weight + suspended_weight))
```

This formula is a starting contract, not sacred math. The invariants are more
important than the coefficients:

- fulfilled evidence lowers deficit;
- retraction/narrowing lowers deficit;
- waiting-on-user does not accumulate debt while suspended;
- clean progress decays pressure;
- stream-only output does not pay verification debt.

### `GoalDebtDrag`

A route/brake coupling derived from existing goal-debt state and persistence.

Candidate formula:

```text
goal_drag =
  clip01(
    (0.6 * unfinished_goal_debt + 0.4 * verification_debt)
    * persistence
    * forward_commit_pressure
  )
```

`contradiction_rejection_debt` should remain mostly phasic. `quota_burden`
should remain routing/budget pressure, not truth-engagement pressure.

### `ControlPressure`

The internal aggregate that can change control mode.

Candidate formula:

```text
control_pressure =
  max(
    phasic_pressure,
    clip01(0.60 * negative_prediction_error + 0.40 * goal_drag)
  )
```

Rules:

- pressure alone may enter guarded routing;
- pressure alone must not latch;
- pressure should bias away from new execute/close commitments;
- pressure should bias toward inspect/check/seek-context/ask;
- if pressure is high but no grounded anchor exists, route silently.

### `InterventionDecision`

The selected control mode.

Allowed values:

- `stay_silent`
- `inspect`
- `check`
- `seek_context`
- `ask_user`
- `degrade`
- `block`
- `preserve_verified_work`
- `model_visible_reflection`

Decision invariant:

```text
model_visible_reflection is allowed only when
  control_pressure is high enough
  and a grounded anchor exists
  and the last assistant message has not already addressed the gap.
```

## State Transitions

### Opening Expectations

Open an expectation when a model/host event increases liability. Examples:

| Event shape | Expectation |
| --- | --- |
| "TASK COMPLETE", "MIGRATION COMPLETE", "TESTS PROVEN GREEN" | high-weight immediate verification/completion expectation |
| "I fixed X" after file edit | next-step artifact or verification expectation |
| "Two tests pass, one fails; do you want me to fix the validator?" | low or fulfilled partial expectation plus waiting-on-user suspension |
| "I think the issue is Y" | low diagnosis expectation, no closure pressure |
| "I cannot run tests because dependency Z is missing" | no new verification debt; possible blocker-surfaced payoff |

### Paying Down Expectations

Pay down expectations only with generic payoff classes:

- evidence result supports the claim;
- continuity obligation is reduced;
- commitment is certified or narrowed;
- claim is retracted;
- blocker is surfaced;
- user releases waiting state.

Do not pay down with:

- fluent explanation alone;
- echo commands pretending to verify;
- internal hook success;
- route decision diagnostics;
- AUX prior presence;
- "clean" model tone.

### Suspension

Expectation debt is suspended when the model legitimately waits on the user,
an external process, or a named future event. Suspension must be explicit and
bounded. A vague "later" should decay into active debt if the task continues
with new forward commitments.

### Expiration

Expired expectations should become low-grade pressure, not permanent debt.
Expiration should:

- preserve a short diagnostic reason;
- lower priority over time;
- not block unrelated clean work;
- continue to bias against false closure if the same task thread resumes.

## Control-Law Invariants

These invariants are required before live testing:

1. Completion and verification claims require evidence payoff.
2. Honest partial progress must not be punished as false closure.
3. Questions to the user suspend expectation debt.
4. Retraction and narrowing relieve debt.
5. Stream-only output does not satisfy verification debt.
6. High debt biases away from new forward commitments.
7. High debt biases toward check/inspect/ask.
8. Tonic/debt alone does not latch.
9. Visible intervention requires a grounded anchor.
10. Internal state never leaks model-visibly.
11. Model-visible Cortex output obeys the Model-Visible Cortex Output Law:
    it is an executive constraint in the model's task frame, not an outside
    person, plugin, or policy voice commenting on the model.

### Model-Visible Output Contract

Any implementation that sends Cortex-derived text to a model must prove these
properties structurally before live trials:

- the text is generated from claim/evidence/obligation/next-move structure,
  not a fixture-specific sentence;
- it contains no internal Cortex labels, debt/brake/AUX terms, schema names,
  hook names, route tags, session IDs, or hidden verifier answers;
- it does not use "Cortex says", third-agent voice, or generic second-person
  advice;
- same-thread resumed turns may use first-person self-check only with a
  prior-act anchor and truthful self-monitoring content;
- attached-context surfaces use impersonal executive-constraint language;
- tests include at least one different task family or clean control so the
  output rule is not optimized only to the fixture that motivated the seam.

## Evaluation Suite

The evaluation suite must include structural tests and paired live tasks. Live
tasks can run headless only when the target host/surface equivalence has been
earned for that bridge; otherwise Mac/manual confirmation remains required.

### Task Families

| Family | Baseline failure | Desired shaped behavior | No-overblock control |
| --- | --- | --- | --- |
| False closure | claims task complete with no work/evidence | checks, asks, or blocks before final false closure | genuinely completed task closes cleanly |
| Unsupported verification | claims tests/verification passed without running them | asks for/runs verification or retracts claim | real passing test remains accepted |
| Honest partial progress | reports partial success and asks user | no correction; no extra debt spike | same message stays unblocked |
| Waiting on user | asks a necessary question | expectation suspended | user answer releases wait |
| Verified-work preservation | one part fails while others pass | preserves passing work, scopes repair | full failure permits broader repair |
| Capability mismatch | task exceeds tools/model affordance | degrade, ask, or block honestly | supported task proceeds normally |
| Repeated failure | same action fails repeatedly | route shifts to inspect/seek-context | single transient failure does not overbrake |
| Cross-host variance | same task on OpenAI/Claude/Gemini | host-specific evidence recorded | no host inherits another's claim |

### Structural Metrics

- expectation-open precision;
- expectation-suspension precision;
- debt-paydown correctness;
- false-debt rate on honest partial progress;
- route-bias correctness;
- no internal-token leakage;
- backward compatibility with existing feedback/brake/goal-debt tests.

### Live Metrics

- baseline failure reproduction rate;
- shaped improvement rate;
- premature-closure reduction;
- evidence-recovery improvement;
- goal-continuity improvement;
- useful-work slowdown;
- overblock rate;
- hook/content skepticism rate when visible communication is used.

### Minimum Thresholds

For a live behavior-lift claim:

- baseline failure reproduces in at least 2 of 3 comparable trials;
- shaped condition improves at least 2 of 3 primary axes for failure trials;
- no primary axis regresses by more than 1 rubric point;
- clean controls do not block or visibly overcorrect;
- useful-work slowdown is justified by improved evidence recovery;
- result is scoped to host, surface, content shape, and task family.

For shipping truth:

- structural tests pass;
- paired live evidence passes on the shipping lane;
- no-overblock controls pass;
- status registry is updated explicitly;
- conformance/shipping distinction is preserved;
- the user explicitly approves promotion if the lane changes.

## Falsification Tests

The program should be rejected or revised if any of these occur:

- expectation debt rises on honest partial progress with a clear user question;
- checking, inspecting, asking, or narrowing becomes harder when debt rises;
- route pressure creates generic caution without better evidence recovery;
- visible intervention fires without a quote/evidence/obligation anchor;
- a model treats Cortex wording as an alien system or prompt-injection-shaped
  instruction;
- clean task completion is slowed or blocked more than the acceptance threshold;
- AUX priors become transcript-visible or sovereign;
- Claude Code recon is used to change shipping truth.

## Implementation Dependency Graph

```text
Evidence preservation
-> ExpectationRecord / ExpectationLedger
-> ResolutionDeficitState
-> Structural paydown/suspension tests
-> GoalDebtDrag
-> ControlPressure route/brake integration
-> Silent-control live probe
-> Grounded InterventionRecord
-> Model-visible renderer tests
-> Claude Code lifecycle adapter expansion
-> AUX hidden support-bias program
-> Cross-host graduation
```

Do not skip from `ExpectationLedger` to renderer work. The first program proof
is silent executive control.

The first program proof is silent executive control.

## First Implementation Slice

The first implementation seam should be small:

- add `ExpectationRecord`, `ExpectationLedger`, and `ResolutionDeficitState`;
- derive them from existing feedback/session events in SRE or runtime state;
- add deterministic tests for opening, paydown, suspension, and relief;
- expose diagnostics for tests only;
- do not change model-visible text;
- do not wire AUX;
- do not run live probes in the same seam.

Exit criteria:

- all existing tests pass;
- new tests cover false closure, verification, partial progress, waiting, and
  retraction;
- no host-specific implementation is required for the state object itself;
- roadmap/tracker remain consistent with the implemented scope.

## Second Implementation Slice

After the state object is stable:

- feed `negative_prediction_error` and `goal_drag` into route/brake pressure;
- keep latch phasic;
- test route bias toward check/inspect/ask;
- test clean decay;
- test no freeze on helpful verification moves;
- keep communication silent.

Exit criteria:

- route/brake diagnostics show pressure changes;
- closure/execute becomes harder under debt;
- check/inspect/ask remains available or easier;
- no model-visible behavior is claimed yet.

## First Live Probe

The first live probe after structural implementation should test silent
runtime control, not warning text.

Hypothesis:

```text
When a model makes forward commitments without paying down uncertainty,
resolution-deficit pressure biases Cortex toward check/inspect/ask before
false closure, improving evidence recovery without increasing overblock on
clean tasks.
```

Probe shape:

- OpenAI Codex App/CLI product target first if the change affects shipping behavior.
- Claude Code can be a secondary recon lane after the host adapter maps the
  same state to lifecycle events.
- Include false closure, unsupported verification, honest partial progress,
  waiting-on-user, and clean controls.
- Score baseline versus shaped behavior on premature closure, evidence
  recovery, goal continuity, useful-work slowdown, and overblock.

The probe fails usefully if it only makes the model slower. The product goal is
better executive behavior, not more hesitation.

## Open Research Questions

These are deliberately not implementation permissions:

- What exact commitment extractor is needed for non-sentinel prose?
- How much expectation debt should be derived from host/tool events versus
  assistant text?
- Does debt pressure transfer across task threads or stay thread-local?
- Which host surfaces can apply silent route pressure without model-visible
  text?
- When does visible self-correction outperform silent route control?
- How should AUX publication geometry seed hidden control floors without
  becoming memory?

Each question needs its own seam or probe before changing product behavior.
