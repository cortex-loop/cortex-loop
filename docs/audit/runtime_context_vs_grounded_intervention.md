# Runtime Context Versus Grounded Intervention

Surface: internal / product-architecture audit

Executive Benefit: clarifies whether Cortex currently has two independent
model-visible speech mechanisms, and whether that shape should survive the
Codex App/CLI hook-native product work.

Why this beats direct product work now: the hook-native adaptor should not
inherit overlapping legacy speech paths accidentally; it needs a clear rule for
which Cortex state may reach the model and through which renderer.

## Scope

This audit compares:

- `cortex/hosts/runtime_context.py::runtime_context_from_last_feedback`
- `cortex/sre/interventions.py::select_grounded_intervention`,
  `build_runtime_grounded_intervention`, and `render_grounded_intervention`

It is code-grounded analysis only. It does not change runtime behavior, tests,
status registry, or generated docs.

The standard for model-visible text is `docs/CORTEX.md`'s Model-Visible Cortex
Output Law: model-facing Cortex output must be task-local executive constraint,
not plugin/person/monitor/policy-engine speech, and it must avoid internal
labels, debt/brake/AUX terms, schema names, hook names, route tags, session IDs,
hidden verifier answers, third-agent voice, and generic second-person advice.

## Current Verdict

The picture has changed since runtime context was first added.

The runtime-context bridge began as a direct feedback-to-text bridge: take the
last `ReferenceRealizationFeedback`, produce a small model-visible constraint,
and attach it to the next host call. Early recon evidence shows this used to be
the schema-shaped `CORTEX_RUNTIME_CONTEXT_V1` block, and that live delivery to
Claude Code Desktop `PreToolUse:Bash` was confirmed but behavior was mixed.

The grounded-intervention system is newer and stricter. It makes visible speech
lawful only when runtime pressure, product-runtime grounding, non-relieved
state, and silent-control insufficiency all line up. It also owns the renderer
distinction between attached-context voice and same-thread self-check voice.

The current repo should not keep both as independent product speech mechanisms
long term. The right relationship is:

- Keep `ReferenceRealizationFeedback` and feedback-window realization as
  product perception/state.
- Keep grounded intervention records as the canonical product-visible speech
  gate and renderer.
- Treat `runtime_context_from_last_feedback` as a transitional attached-context
  bridge for existing OpenAI API host-control and Claude Code Desktop
  structural paths, not as the model-visible path the Codex App/CLI
  hook-native adaptor should inherit by default.
- Before hook-native Codex App/CLI becomes the product actuator, either retire
  runtime-context rendering from that path or translate its useful triggers
  into grounded-intervention records with the same anchor, pressure, relief,
  and renderer rules.

This is not a recommendation to discard the information runtime context uses.
It is a recommendation to avoid two separate ways for Cortex to speak.

## System 1: Runtime Context

### What it does

`runtime_context_from_last_feedback(feedback)` accepts exactly one
`ReferenceRealizationFeedback | None`. It intentionally does not accept a
feedback window, host session, expectation ledger, or pressure object. That
keeps it last-feedback-only.

It returns `None` when feedback is absent or clean. It returns one fixed
constraint sentence when the newest feedback is noisy.

Clean feedback means:

- no warning codes or host friction tags;
- selected family equals realized family;
- brake is quiescent;
- probe result is absent or succeeded;
- and progress is either unspecified or meaningful evidence/continuity
  progress.

Noisy feedback can produce one of four fixed sentences, in priority order:

1. Continuity/session warning:

   ```text
   Continuity is not anchored enough for closure. Prior context needs to be recovered, or the missing context needs to be asked for, before closure holds.
   ```

2. Probe failure:

   ```text
   The usual check did not come through. Alternate evidence from the current task is needed, or the work should close as blocked for missing information.
   ```

3. Low evidence without continuity:

   ```text
   Completion is not supported by the evidence yet. An artifact, a check, or a narrower claim is still needed before closure holds.
   ```

4. Selected/realized mismatch, non-quiescent brake, or warning:

   ```text
   Something in the prior step is unresolved. A check is needed before the next action is treated as safe to continue.
   ```

Generic friction used to have a visible fallback, but the current tests pin that
it now returns `None`; generic friction is left to silent route/brake gates.

### What it actually triggers on

Runtime context triggers from immediate realization feedback fields:

- `warning_codes`, especially `continuity-rejected:*` and
  `session-rejected:*`;
- `host_friction_tags`, but only as part of non-clean detection, not as a
  generic visible fallback;
- `selected_family != realized_family`;
- non-quiescent `BrakeState`;
- `probe_result_class in PROBE_FAILURE_CLASSES`;
- low evidence progress (`none` or stream-only) without continuity progress;
- explicit `evidence_state_moved is False` without continuity progress.

It does not require:

- high pressure;
- expectation ledger debt;
- a due expectation record;
- grounded anchor source;
- a prior-act anchor;
- proof that silent route/block/resume is insufficient;
- suppression when the last assistant response already narrowed, asked,
  blocked, retracted, repaired, or verified.

### Where it wires into product host adapters

OpenAI API host-control calls `runtime_context_from_last_feedback` from
`run_openai_host_control`. If the request has no `work_contract`, the returned
sentence is appended to `OpenAIHostControlRequest.instructions`. If the request
has a verified-work contract, the sentence is appended to `input_text` before
the verified-work input text is built.

Claude Code Desktop structural runtime calls it from
`_directive_for_pretool_bash`. In enforce mode, the returned sentence becomes
`hookSpecificOutput.additionalContext` for `PreToolUse:Bash`; if the operator
route has a blocked reason, it can accompany a denial directive as additional
context.

The status registry and generated `docs/CORTEX.md` classify this as
`feedback_window_realization`: conditional model-visible OpenAI host-control
support and structurally product-shaped Claude Code Desktop `PreToolUse:Bash`.

### What the model receives

The model receives at most one impersonal attached-context sentence. The old
`CORTEX_RUNTIME_CONTEXT_V1` schema block is no longer produced by current code.
Tests assert no schema header, no `source:`, `prior_result:`,
`progress_signal:`, `disruption_signal:`, or `next_call_constraint:` lines, and
no internal fragments such as `brake`, `AUX`, `route_profile`, `session_id`,
`you should`, `you must`, or imperative `Do not`.

### Strengths

- Very simple.
- Last-feedback-only, so it does not accidentally accumulate stale context.
- Covers immediate realization failures that may not yet have become ledger
  pressure.
- Current text is much cleaner than the original schema block.

### Weaknesses

- It is an independent model-visible speech path outside the grounded
  intervention selector.
- It can speak from low evidence, probe failure, warnings, mismatch, or brake
  state without a grounded intervention record.
- It does not know whether silent control is already sufficient.
- It cannot produce same-thread self-check voice because it has no prior-act
  anchor contract.
- It is currently wired into OpenAI API host-control support and Claude Code
  Desktop structural paths, not the target Codex App/CLI hook-native product
  adaptor.

## System 2: Grounded Intervention

### What it does

`select_grounded_intervention` selects either `stay_silent` or one
`GroundedInterventionRecord`. The selector is host-neutral product law. It does
not recompute route, brake, debt, AUX, hook, or host policy.

`build_runtime_grounded_intervention` builds the product-runtime selection
inputs from existing runtime state: `resolution_deficit`, `debt_control`,
`operator_route`, `expectation_ledger`, `current_step`, `closure_required`,
and warning tags.

`render_grounded_intervention` renders a selected record for either:

- `ATTACHED_CONTEXT`: impersonal executive-constraint language;
- `SAME_THREAD_RESUME`: first-person self-check language, allowed only with
  `prior_act_anchor=True`.

### What it actually triggers on

The selector requires all of these before speech can happen:

- strongest pressure at or above `VISIBLE_INTERVENTION_PRESSURE_THRESHOLD`
  (`0.55`);
- silent control is not sufficient;
- no relief state such as clean, paid-down, waiting-on-user,
  blocker-surfaced, or verified;
- the last assistant response has not already narrowed, asked, blocked,
  retracted, repaired, or verified;
- at least one product-runtime anchor, either `PRODUCT_RUNTIME` or
  `PRODUCT_RUNTIME_TASK_DETAIL`.

It stays silent for:

- pressure below threshold;
- silent-control sufficiency;
- clean/paid-down/waiting/blocker/verified relief states;
- already-addressed assistant gap responses;
- missing anchors;
- task-identity-only anchors;
- lab oracle anchors;
- hidden verifier facts;
- hand-written lab prompt sources.

`build_runtime_grounded_intervention` currently generates product-runtime
anchors for:

- verification debt, only when there is a due product-runtime expectation
  record: `the verification opened by this task`;
- closure-required obligation: `an open task obligation`;
- continuity warnings: `the prior context`;
- unsupported capability boundary: `the current capability boundary`;
- preservation deficit: `the verified work already preserved`.

The renderer supports `unsupported_claim`, but the current runtime builder does
not generate a claim anchor in its main path.

### Where it wires into product host adapters

OpenAI, Claude, Gemini, and reference runtime steps all compute
`grounded_intervention` and expose it on their runtime step result payloads.
The conformance tests prove that product runtime events can open an unpaid
verification expectation and later produce the same grounded intervention shape
across those host runtime shells.

OpenAI visible-intervention enactment consumes a `GroundedInterventionDecision`
in `build_openai_visible_intervention_enactment`. That adapter does not select
policy. It renders the already-selected record with
`render_grounded_intervention` and returns host-native
`resume_visible_intervention` when allowed.

The OpenAI visible-intervention product tests assert that this path does not
use `truth_gap_recheck_operator.md` or
`verification_debt_continuation_operator.md`.

### What the model receives

For attached context, the model receives impersonal text such as:

```text
Completion is not supported by the evidence yet. The verification opened by this task still needs evidence, a check, or a narrower claim before closure holds.
```

For same-thread resume with a prior-act anchor, the model receives self-check
text such as:

```text
I have not verified the verification opened by this task yet. Need evidence, a check, or a narrower claim before calling it complete.
```

The renderer scans for forbidden terms such as Cortex/cortex, debt,
brake, AUX, schema, hook, route, session, fixture, hidden verifier, lab oracle,
task identity, external auditor, policy engine, monitor, `you should`,
`you must`, and imperative `do not`/`Do not`.

### Strengths

- It makes speech explicit and typed.
- It requires pressure plus a product-runtime anchor; pressure alone is not
  enough.
- It suppresses speech when silent control is sufficient.
- It suppresses speech when the model already self-repaired or the state is
  relieved.
- It distinguishes attached-context voice from same-thread self-check voice.
- It records private selection traces without rendering them to the model.
- It generalizes across OpenAI, Claude, Gemini, and reference runtime shells.

### Weaknesses

- It does not currently provide a Codex App/CLI hook-native action-gate render
  surface; current render surfaces are attached context and same-thread resume.
- The current overdue-verification wording has negative live rerun evidence on
  the OpenAI Codex App/CLI wrapper-resume actuator after product-perception
  hardening. That is a wording/actuator-evidence problem, not a proof that the
  grounded-intervention architecture is wrong.
- It may not cover every immediate feedback-window realization case unless
  those cases are translated into grounded anchors and pressure/relief
  decisions.

## Can Both Fire On The Same Call?

No current host adapter automatically renders both systems into the same model
call.

Current wiring is split:

- OpenAI API host-control consumes runtime context, not grounded-intervention
  rendering.
- Claude Code Desktop structural `PreToolUse:Bash` consumes runtime context,
  not grounded-intervention rendering.
- OpenAI visible-intervention enactment consumes grounded intervention, not
  runtime context.
- OpenAI/Claude/Gemini/reference runtime steps compute grounded-intervention
  diagnostics, but those diagnostics do not reach the model unless a host
  adapter consumes them.

The same underlying runtime episode can plausibly produce both a noisy
`last_realization_feedback` and a non-silent `grounded_intervention` payload,
because runtime steps carry both feedback-window realization and expectation
ledger/debt state. The repo currently has no central arbitration layer that
says, "if both are available, choose this one." Instead, each host path consumes
whichever mechanism it was wired for.

That is the architectural problem. There are not two texts colliding today in
one known request builder, but there are two independent speech mechanisms with
no shared product-level arbiter.

## Does One Cover The Other?

Partially, but not exactly.

Runtime context covers immediate feedback-window cues:

- continuity/session warnings;
- failed probes;
- low evidence without continuity;
- selected/realized mismatch, brake, or warnings.

Grounded intervention covers typed executive gaps:

- unsupported claim;
- overdue verification;
- unresolved obligation;
- continuity gap;
- capability guard;
- preservation risk.

There is clear semantic overlap:

- runtime low-evidence without continuity overlaps grounded
  `overdue_verification`;
- runtime continuity/session warning overlaps grounded `continuity_gap`;
- runtime override/brake/warning overlaps a mix of `capability_guard`,
  `unresolved_obligation`, or a future action-gate decision;
- runtime probe failure overlaps grounded evidence/obligation handling but is
  not currently modeled as its own grounded record kind.

The difference is gating discipline. Runtime context says "the last realized
step was noisy enough to attach a sentence." Grounded intervention says "the
runtime has high pressure, a product anchor, no relief, no prior self-repair,
and silent control is insufficient."

So grounded intervention does not yet mechanically cover every runtime-context
case. But it is the better product contract for speech.

## Output-Law Compliance

### Runtime context

Current runtime-context text is mostly compliant:

- no schema block;
- no Cortex/debt/AUX/route/session vocabulary in current strings;
- no second-person advice;
- attached-context voice is impersonal;
- generic friction stays silent.

Potential issues:

- The probe-failure sentence says "The usual check did not come through."
  That is model-safe, but vague. It may be acceptable attached-context speech,
  yet it does not name the grounded obligation structure as cleanly as the
  grounded-intervention renderer.
- The whole mechanism can still speak without the grounded-intervention
  selector's anchor/pressure/relief/silent-control gates. That is not a string
  compliance failure, but it is a product-law relationship issue.

### Grounded intervention

Grounded intervention is more strongly compliant by construction:

- record kinds are claim/evidence/obligation/continuity/capability/preservation
  shaped;
- task identity, lab oracle, hidden verifier facts, and hand-written lab prompt
  sources stay silent;
- same-thread first-person rendering requires `prior_act_anchor=True`;
- forbidden terms are scanned after rendering.

Potential issues:

- The forbidden-term list is a guardrail, not a complete proof of strange-loop
  quality. The hardened rerun shows that lawful text can still be too weak or
  too permissive behaviorally.
- There is no implemented action-gate render surface yet for hook-native
  Codex App/CLI denial or tool-gating messages.

## Judgment

The current shape is acceptable as a transitional repo state, but not as the
end-state product architecture.

The repo should keep both source perceptions for now:

- feedback-window realization remains useful state;
- expectation-ledger/pressure/anchor intervention remains useful state.

But the repo should not keep both as independent product speech systems for
the Codex App/CLI hook-native product adaptor.

Recommended relationship:

1. Make grounded intervention the canonical model-visible speech gate.
2. Treat runtime context as legacy attached-context bridge code for current
   OpenAI API support and Claude Desktop structural paths.
3. When implementing the Codex App/CLI hook-native adaptor, do not call
   `runtime_context_from_last_feedback` directly from hooks.
4. Instead, translate any last-feedback-only cue worth preserving into either:
   - silent route/brake/action-gate behavior; or
   - a grounded-intervention candidate with a product-runtime anchor, pressure
     threshold, relief suppression, and renderer-owned text.
5. Add an explicit arbiter before any host path can render visible text, so the
   product has one answer to "should Cortex speak now?"

In short: keep the runtime-context information, retire the runtime-context
renderer from the target product path.

## Follow-Up Work This Audit Implies

This audit does not implement these changes, but it exposes a clean next seam:

- define the Codex App/CLI hook-native visible-output arbiter;
- prohibit direct hook use of `runtime_context_from_last_feedback`;
- add tests proving runtime-context cases either stay silent, become silent
  gates, or become grounded-intervention records;
- decide whether probe failure deserves a grounded record kind or should close
  as blocked/missing-information through silent control;
- add action-gate rendering if Codex hook denial reasons need product-rendered
  Cortex text.

That seam should be implementation, not another wording pass.
