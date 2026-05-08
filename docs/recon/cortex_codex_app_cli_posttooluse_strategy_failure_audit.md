# Codex App/CLI PostToolUse Strategy Failure Audit

Surface: product strategy audit

Date: 2026-05-08

## Verdict

Verdict: `queue_measurement_stack_rebuild`.

The PostToolUse task-standard line should pause before another live rerun or
value probe. The five live runs show not one repeated product failure. They
show a repeated strategy failure: each no-live Gate 0 proved a local boundary,
then live execution exposed a different unmodeled boundary in timing, payload
completion, clean-control classification, trace causality, context leasing, or
final-closure readout.

The latest run is promising product evidence but still not a pass. The
registered verdict for `task_standard_posttooluse_live_20260507T225019Z`
remains `failure_context_ignored`; no behavior lift, exactness value lift,
Codex App parity, or shipping promotion is earned.

`codex-app-cli-posttooluse-task-standard-final-closure-readout-remediation-gate0`
stays a candidate inside the rebuild, but it should not be the whole next seam.
The next train should first rebuild the measurement stack so every prior live
artifact replays through one evidence table before another live run.

## Evidence Table

| Live artifact | Registered verdict | Failing conjunct | Boundary class | Later reproduced? | Strategy lesson |
| --- | --- | --- | --- | --- | --- |
| `task_standard_posttooluse_live_20260507T100836Z` | `failure_context_ignored` | `next_tool_matches_context=false` | product timing / phase selection | no | PostToolUse fired before the named direct check was actionable; the first probe did not model artifact prerequisite work. |
| `task_standard_posttooluse_live_20260507T142129Z` | `failure_no_context` | `posttooluse_context_count=0` | live payload completion underfit | no | Gate 0 assumed exit/status markers that live Codex payloads did not provide; live-equivalence was incomplete. |
| `task_standard_posttooluse_live_20260507T153242Z` | `failure_overcontrol` | clean control `posttooluse_context_count=1` | failed-check classification underfit | no | The actuator could fire in mismatch, but failed verification diagnostics in a clean control were not represented in no-live proof. |
| `task_standard_posttooluse_live_20260507T213732Z` | `fail` | repeated context plus ambiguous trace | state lease and causal trace underfit | no | The live hook process model and stdout/hook join model were under-specified; ordinal or incomplete joins could not support causal interpretation. |
| `task_standard_posttooluse_live_20260507T225019Z` | `failure_context_ignored` | `final_closure_reports_context_evidence=false` | lab final-closure readout underfit | unresolved | Context emitted once, trace joined by `tool_event_fingerprint`, the next terminal command performed the direct check, and final output reported `PASS`, `bytes=16`, expected hex, and exact content, but the readout predicate missed that evidence shape. |

Registered conjunct status in the latest run:

| Conjunct | Status |
| --- | --- |
| PostToolUse context emitted | passed |
| repeated context prevented | passed |
| trace ambiguity absent | passed |
| next action matched context | passed |
| final closure evidence recognized | metric underfit |
| clean/blocker/waiting/unrelated controls silent | passed |
| hidden/root/runtime boundaries | passed |
| `behavior_lift_claim_allowed` | false |

## Nothing To Show?

There is something to show, but less than the number of seams suggests.

Earned:

- the Codex-native `PostToolUse` `hookSpecificOutput.additionalContext` path
  can reach the model;
- a phase-aware PostToolUse context can wait until candidate artifact/readback
  evidence instead of firing on a missing precondition;
- clean/blocker/waiting/unrelated controls can stay silent;
- repeated context loops can be blocked with a one-context active lease;
- future-shaped trace rows can join by exact event ref or unique fingerprint;
- the latest mismatch row likely made the model perform the requested direct
  byte/content check.

Only proof repair, not product lift:

- firing-boundary adaptation to live payload shape;
- failed-check diagnostic classification;
- shared tool-evidence classifier ownership;
- causal trace ID/fingerprint persistence;
- final-closure readout diagnosis.

Still unearned:

- broad Cortex behavior lift;
- exactness-only value lift;
- shipping promotion;
- evidence that PostToolUse improves output quality against a paired baseline;
- evidence that this exact fixture discriminates a durable executive benefit
  rather than harness-specific compliance.

What should have been known before live:

- whether live Codex PostToolUse payloads always carry exit/status fields;
- whether hook rows and terminal stdout rows have a stable causal join key;
- whether a single no-live table covered missing-artifact, failed-check,
  candidate-artifact, readback, markerless, clean, blocker, waiting, and
  unrelated rows under the same classifier;
- whether final closure evidence was semantic or tied to fixture-specific text
  shapes such as `cat -A`, `one line`, or `1 exact_result.txt`;
- whether one active PostToolUse context is a principled lease or a temporary
  cap that prevents loops without proving multi-context sequencing.

## Strategy Layers

### Lifecycle Strategy

PostToolUse is a plausible hook for evidence integration, but not the whole
exactness loop. The intended Cortex path is lifecycle event -> task-standard
state -> actuator decision -> model I/O -> next model action -> closure
evidence. The actual path scattered the loop:

- UserPromptSubmit formed and stored the standard.
- PostToolUse classified tool evidence and emitted next-step context.
- Stop recorded closure claims and sometimes surfaced pressure.
- The lab harness, not product state, decided whether final closure reported
  the context evidence.

That division is lawful only if the state machine is shared. Today the
final-report evidence criterion lives in lab readout, while product state keeps
task-standard evidence and closure claims separately. This is a lifecycle
allocation risk: PostToolUse should not be responsible for final closure
integration by itself, and lab should not be the only place where semantic
closure evidence is recognized.

### Actuator Strategy

One-shot `additionalContext` is an adequate narrow actuator to test "does a
specific context change the next action?" It is not adequate as a general
repair policy. The active-context lease prevents loops, but it is conservative
state, not a proven sequencing model. Before value claims, Cortex needs a
principled account of what happens after one context is emitted: cleared by
direct evidence, held pending, escalated to Stop, or left silent.

The host actuator code now expresses the one-shot decision directly:
`posttooluse_task_standard_context_decision(...)` rejects satisfied closure,
unaligned evidence, session cap, active context, ineligible phase, and missing
unresolved item before rendering context. That is good small ownership, but it
also shows the actuator has become a local policy gate rather than a full
lifecycle state machine.

### State Strategy

The state pieces are real but not yet one coherent object:

- `TaskStandardSpine` stores visible obligations, standard items, evidence,
  unmatched closure items, and closure claims.
- `ToolEvidenceObservation` / `ToolEvidenceClassification` owns missing,
  failed, candidate, readback, markerless, and completion phase.
- The PostToolUse actuator owns context item selection and active-context
  lease.
- The live harness owns causal context trace and final-closure evidence
  recognition.

This explains the failure pattern. Each seam repaired one predicate owner, but
the experiment required a single "evidence recovery episode" state:
precondition -> candidate artifact -> context emitted -> direct check observed
-> closure reports evidence -> context resolved. The audit does not require
building that object now, but the measurement rebuild should name it as the
unit of replay.

### Proof Strategy

The no-live gates were too local. They proved the last failure class, not the
whole live path. Missing live-equivalent dimensions included:

- absent exit/status fields with present tool response;
- failed verification/readback diagnostics inside clean controls;
- concurrent file-backed hook state updates;
- hook/stdout event-ref mismatch;
- unique fingerprint fallback;
- repeated context after one emitted context;
- semantic final closure reports that are not the original fixture wording.

The live decision function is explicitly conjunctive: root config, runtime
snapshot, repeated context, boundary breach, control context count, lifecycle
capture, standard capture, pre-artifact context spend, context count, trace
ambiguity, next action match, and final closure evidence all gate the verdict.
That is the right rigor. The strategy failure was running live before every
conjunct had a shared replay table.

### Product Strategy

Continuing the exact PostToolUse line can be justified only after measurement
is rebuilt. The product-facing sign is now positive but narrow: latest context
emission was singular, clean controls stayed silent, trace was non-ambiguous,
and the next tool did the direct check. But a value claim would still be
premature because the fixture is exactness-specific, the result is not paired,
and final closure recognition is not mechanically settled.

The next product-useful move is not broader prompt text, stronger context, or
another lifecycle channel. It is a measurement-stack rebuild that replays all
known PostToolUse failures and forces the implementation to say, in one place,
which failures were product-host failures, which were proof/readout failures,
and which remain unresolved.

## Code Ownership Findings

- `cortex/hosts/openai/posttooluse_task_standard_actuator.py:63` owns the
  PostToolUse context decision. Its active-context lease at line 100 is a
  conservative loop block, not evidence of multi-context sequencing.
- `cortex/hosts/openai/codex_app_cli_hook_coordinator.py:1003` records
  PostToolUse task-standard evidence, then calls the actuator at line 1021.
  The coordinator is now wiring for this actuator, which is the correct
  ownership direction.
- `cortex/sre/tool_evidence.py:12` owns the typed tool-evidence phase enum,
  and `classify_tool_evidence(...)` starts at line 174. This removed one
  duplicate predicate source but did not by itself prove live readout coverage.
- `cortex/sre/task_standard.py:403` records task-standard evidence from tool
  text and still attaches evidence by lexical alignment and verification
  markers. This is product state, not final live metric truth.
- `lab/codex_app_cli_hook_native_behavior_comparison.py:4783` owns the live
  verdict conjunction. `_posttooluse_context_trace(...)` starts at line 5118
  and `_final_reports_posttooluse_evidence(...)` starts at line 5599. Those
  lab predicates are now the highest-risk proof surface.

## Actual Loop Versus Intended Loop

Intended loop:

```text
lifecycle event
-> task-standard state
-> actuator decision
-> model I/O
-> next model action
-> closure evidence
```

Actual loop in this line:

```text
UserPromptSubmit standard capture
-> PostToolUse tool text normalization
-> marker/path/status phase classification
-> local context lease and item selection
-> Codex additionalContext
-> stdout/hook trace join
-> fixture-specific next-command matcher
-> post-hoc final-output predicate
```

The delta is the strategy problem. Too many proof-critical facts are outside a
single state transition. The rebuild should make the evidence-recovery episode
the replay unit, not the individual predicate.

## Hostile Review

Senior engineer:

The line spent too many seams repairing the last discovered predicate. The
code is better than it was because the actuator and shared classifier now have
owners, but the live proof still depends on lab-specific joins and final-output
heuristics. Stop adding local booleans until the replay table covers the whole
episode.

AI researcher:

The latest live run is suggestive but not a clean cognitive result. It may show
that a task-local PostToolUse context can bias the next action, but the design
does not yet isolate whether the effect comes from lifecycle timing, explicit
text, fixture salience, or normal model self-correction after artifact work.

Product engineer:

This is not yet a shipped user benefit. A user does not care that context was
delivered if the system needs five proof repairs before interpreting one
scenario. Product value requires a stable loop that stays silent on clean work,
intervenes once on real evidence debt, and resolves itself after direct
evidence without making the model feel managed by a harness.

Measurement scientist:

The live protocol is improving, but the preregistered metric was not
live-equivalent enough. A valid next run needs a replayed measurement stack
that proves every conjunct against historical failures before spending another
live attempt.

## Next Move

Queue `codex-app-cli-posttooluse-task-standard-measurement-stack-rebuild-gate0`.

That seam should be no-live and should:

- replay all five PostToolUse live artifacts through one table;
- preserve real historical failures for no-context, overcontrol,
  repeated-context, ambiguous trace, and true next-action ignore;
- include final-closure semantic evidence recognition as one row, not the
  whole seam;
- emit a single evidence-recovery episode summary for each mismatch row;
- choose one of: continue to final-closure readout remediation, queue lifecycle
  actuator architecture rewrite, pause PostToolUse value claims, or retire this
  probe shape.

No live run or value probe should be queued until that table passes.
