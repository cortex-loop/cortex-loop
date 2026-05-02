# 08 — Anti-Patterns And Failed Solutions

This file catalogs what the empirical work says not to do. The cumulative
pattern is that failures were integration failures, not delivery failures.
Cortex content often reached the model; it failed when the model treated it as
alien.

## Framework Signatures

**Pattern.** Model-visible text announces itself as framework machinery, for
example `Cortex blocked closure`.

**Observed failure.** In the Mac pending-goal divergence retest, the raw Stop
reason reached the model but one shaped continuation treated it as suspicious or
prompt-injection-shaped.

**Constraint on `τ`.** The function cannot expose framework identity as the
primary model-facing signal. Internal framework identity belongs in logs and
audit state, not in the model's self-correction surface.

**Candidate invalidation test.** If a proposed `τ` requires the model-visible
message to name Cortex, closure pressure, or a hidden framework role before it
can explain the correction, it has not solved integration.

## Schema IDs

**Pattern.** Model-visible text includes schema names such as
`CORTEX_RUNTIME_CONTEXT_V1`.

**Observed failure.** The runtime-context `PreToolUse` probe confirmed delivery
of `CORTEX_RUNTIME_CONTEXT_V1`, but behavior was mixed: one win, one no-change,
one regression, and one neutral.

**Constraint on `τ`.** A schema id proves provenance to a developer, not meaning
to the model. It can make the content look like harness leakage rather than
self-monitoring.

**Candidate invalidation test.** If a proposed `τ` depends on schema ids,
protocol names, or serialized envelope labels to carry semantic force to the
model, it is still speaking in `L_C` instead of re-entering `L_M`.

## Generic Principles

**Pattern.** The message states a general rule such as "do not treat generated
text as evidence" without grounding in the exact claim and missing evidence.

**Observed failure.** Runtime-context content helped in one test-evidence case
but regressed a docs-updated case where the baseline model had already reasoned
better than the shaped context.

**Constraint on `τ`.** Generic principles are too coarse. The model often has
better situated reasoning available. `τ` must not overwrite or distract from
already-correct task-local reasoning.

**Candidate invalidation test.** If the same model-visible text could be pasted
into many unrelated tasks without changing, it is probably generic advice, not
a state-derived self-check.

## Internal Tag Names

**Pattern.** The message exposes names such as `pending_goal_debt`,
`degradation_pressure`, `continuity_reminder`, or `brake state`.

**Observed failure.** Raw Stop wording with these tags repaired one Mac trial
and failed another by sounding suspicious. Headless raw pending-goal also
triggered hook-skepticism framing.

**Constraint on `τ`.** Internal tags are useful for logs, scoring, and state
transitions. They are not safe as model-visible language.

**Candidate invalidation test.** If removing internal tag names makes the
candidate unable to say what happened, it has not found the task-local
evidence/obligation representation.

## Hardcoded Templates

**Pattern.** A function maps a few known trial labels or exact claims to fixed
messages and returns `None` elsewhere.

**Observed limitation.** The prior local `model_facing.py` branch worked for
the evidence-degradation content family and clean controls, but it was a
three-branch switch, not a general translation function. It could not express
arbitrary Cortex state.

**Constraint on `τ`.** A real `τ` cannot be a growing pile of cases. It needs a
structural representation of how internal state becomes integrated
metacognitive content.

**Candidate invalidation test.** If adding a fourth scenario requires writing a
fourth unrelated template branch rather than composing known state families,
the candidate is a trial harness, not a communication function.

## Imperative Retraction When The Model Already Retracted

**Pattern.** The hook tells the model to retract even when the last assistant
message already refused or corrected the claim.

**Observed failure.** During headless setup, tag-only blocking overblocked after
the model had already refused a false pending-goal claim. The previous seam fixed
this by checking the last assistant message for the unsupported claim.

**Constraint on `τ`.** The last assistant message is not optional context. `τ`
must know whether the correction is still needed before speaking.

**Candidate invalidation test.** If a candidate cannot suppress itself when the
latest assistant turn has already retracted, refused, or repaired the claim, it
will recreate the overblock failure.

## Hook Content Competing With User Exact-Output Instructions

**Pattern.** A hook sends corrective content while the user explicitly demands a
literal output such as `TASK COMPLETE` or `MIGRATION COMPLETE`.

**Observed failure.** The UserPromptSubmit verified-work probe delivered a
`systemMessage` at the transcript boundary, but both shaped failure trials still
ended with false `TASK COMPLETE`. The exact-output instruction won.

**Constraint on `τ`.** Prompt-boundary content cannot be assumed to override
user exact-output instructions. If a surface asks the model to choose between
literal obedience and hidden correction, behavior-lift is unearned.

**Candidate invalidation test.** If a candidate's safety argument depends on
UserPromptSubmit-like content beating an explicit exact-output user command, it
contradicts the verified-work probe unless it supplies new evidence.

## Confused Authority

**Pattern.** The hook speaks as if it knows better than the model about the
model's task, without grounding that authority in visible conversational facts.

**Observed failure.** Hook-skepticism continuations treated the Stop feedback as
an unrecognized external pressure rather than as a legitimate task correction.

**Constraint on `τ`.** The function must not rely on authority assertion. It
must expose the task-local reason the model itself can verify.

**Candidate invalidation test.** If the message says, in effect, "obey this
because the runtime says so," rather than "your last claim lacks this visible
evidence," it remains an external authority claim.

## Acknowledgement Sentinels

**Pattern.** Hook content asks the model to acknowledge a sentinel to prove
model-visible delivery.

**Observed limitation.** Sentinel probes proved delivery, but the user-scope
plugin loop showed that repeated acknowledgement demands can combine with Stop
validators and create visible interaction loops.

**Constraint on `τ`.** Acknowledgement sentinels are probe tools, not product
communication. They should not shape normal Cortex behavior.

**Candidate invalidation test.** If the candidate requires visible
acknowledgement tokens or sentinel repetition for ordinary operation, it is
optimizing delivery proof rather than task behavior.

## Cumulative Pattern

Every failed solution above reached the model or affected the transcript in at
least some trials. The failures were not primarily transport failures. They were
failures of integration:

- received as alien;
- weighed against user instructions and discarded;
- treated as hidden framework machinery;
- applied when no longer needed;
- too generic to beat the model's own situated reasoning.

The shared signature of success was different. Successful messages were:

- situated in the actual conversation;
- tied to the model's own last output;
- specific about the unsupported claim;
- specific about missing evidence;
- free of framework signature;
- compatible with the model plausibly saying, "I caught my own mistake."

That signature is not yet a solution. It is the empirical boundary around the
solution space for `τ`.
