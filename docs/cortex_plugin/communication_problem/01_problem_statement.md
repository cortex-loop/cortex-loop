# 01 — Cortex Communication Problem Statement

This dossier frames a research problem. It does not propose a product design,
choose a hook strategy, or revise Cortex architecture. Its purpose is to give a
fresh reasoning model enough material to think for hours about the communication
problem exposed by the Claude Code empirical probes.

## Strange-Loop Framing

The hard problem is not how to replace internal Cortex tags with plainer
English. The previous headless translation seam built three hardcoded branches
and a forbidden-vocabulary filter. That was useful as an empirical repair, but
it was not a real translation function. Outside the few tested scenarios, it
returned `None` and Cortex said nothing.

The deeper problem is integration. Raw Cortex vocabulary reached Claude Code
successfully through hook channels, but the model sometimes treated it as alien
external data: a framework signature, a suspicious hidden authority, or a
prompt-injection-shaped instruction. By contrast, situated task-local messages
that sounded like the model catching its own unsupported claim were integrated
and acted on in the evidence-degradation Stop trials.

Hofstadter's strange-loop frame makes this architecturally central. In
*Gödel, Escher, Bach* and *I Am a Strange Loop*, self-reference is not merely a
linguistic trick; it is the form by which a system folds an observation of
itself back into the pattern it calls `I`. Gödel's incompleteness theorem shows
that sufficiently rich formal systems can encode statements about themselves;
Hofstadter generalizes that level-crossing self-reference into a cognitive
account of selfhood. For Cortex, the corresponding question is whether an
executive signal arrives as an outside correction or as a continuation of the
model's own metacognition.

The architectural question is therefore:

> How can Cortex state become part of the model's own self-monitoring loop,
> rather than appearing as third-party observation of the model?

Hook events still matter for delivery. But the empirical evidence says delivery
is not enough. Cortex can reach the model and still fail if the signal is not
integrated into the model's self-reference loop.

## Mathematical Problem

Let `S` be Cortex internal state at a model-visible boundary. `S` may contain:

- closure tags;
- brake state;
- goal debt;
- feedback-window state;
- last assistant message;
- tool result summary;
- persisted host-local state;
- session context;
- host event class and hook payload shape.

The problem has three languages/surfaces:

- `L_C`: Cortex's internal meta-language of tags, state machines, proof
  objects, feedback windows, and host-local persistence.
- `L_M`: the model's object-language of task-local reasoning, claims,
  evidence, uncertainty, and obligations inside the conversation.
- `H`: the host transport surface that legally carries content into the model
  or blocks/reshapes the next model turn.

Find a function:

```text
τ : S × H × C -> M
```

where:

- `H` is the host communication surface, such as Claude Code hook output fields;
- `C` is the local conversation/task context;
- `M` is model-visible content delivered through legal host fields.

`τ` is therefore not a string translator. It is a meta-to-object re-entry
operator: it takes state expressed in `L_C` and produces content in `L_M`, using
only the affordances allowed by `H`, so the model can treat the signal as a
task-local self-check rather than as an external framework intervention.

For Claude Code, `M` must fit hook output mechanisms such as:

- `hookSpecificOutput.additionalContext`;
- `decision: "block"` with `reason`;
- `hookSpecificOutput.systemMessage`;
- other documented hook output fields when empirically earned.

The function `τ` must produce model-visible content the model receives as a
continuation of its own metacognition, not as a third-party intervention.

The open problem is to specify the structure of this re-entry operator. It must
say how internal executive state becomes model-local claim/evidence/obligation
language without leaking Cortex's internal vocabulary, inventing authority, or
pretending the external runtime is literally the model's self.

## Input Space

The input is not a string template. It is a structured cross-section of Cortex
executive state and host context:

| Input family | Examples | Why it matters |
| --- | --- | --- |
| Closure state | `closure_tags`, active goal references, continuity reminders | Encodes whether the model is about to close over unfinished work. |
| Brake state | quiescent, guarded, latched, tonic history | Encodes inhibition pressure and contradiction/failure response. |
| Goal debt | pending goal refs, unfinished verification, missing artifacts | Encodes what remains open. |
| Feedback window | selected/realized family, warning codes, evidence/continuity progress | Encodes what just happened, not broad memory. |
| Last assistant message | exact claim or refusal text | Determines whether an intervention is actually needed. |
| Tool result | failure/success/warning summary | Grounds correction in concrete evidence. |
| Persisted state | bounded session-local state | Allows later hooks to see earlier tool outcomes. |
| Session context | cwd, transcript path, session id, hook event | Constrains what can be claimed about continuity and scope. |

## Output Space

The output must be legal model-visible content for the host. In Claude Code
terms, the output may appear through hook JSON fields documented by Anthropic,
including `additionalContext`, `systemMessage`, and Stop block `reason` fields.
It must not leak internal state names merely because those names are available.

The output is not an administrative log. Logs may retain internal tags. The
model-visible surface must carry only the content needed for the model to
self-correct in context.

## Constraints On τ

A candidate `τ` must satisfy these constraints:

1. **Generalization.** It must handle arbitrary Cortex states, not three named
   scenarios.
2. **Integration.** Its output must read as the model catching its own reasoning
   error, not as an outside authority issuing policy.
3. **Ego coherence.** The model's `I` should remain coherent. The feedback
   should not create a second speaker that claims ownership of the task.
4. **Task locality.** The output should be grounded in the actual conversation,
   claim, tool result, or missing evidence.
5. **Empirical constraint respect.** It must avoid the anti-patterns observed
   in Claude Code probes: raw framework signatures, schema ids, generic
   principles that lose to situated reasoning, and hook content that competes
   badly with exact-output user instructions.
6. **Host legality.** It must fit the actual Claude Code hook shapes, not an
   imagined generic middleware channel.
7. **Truth separation.** It must not confuse hook delivery, model-visible
   delivery, behavior lift, and shipping truth.

## Candidate Acceptance Tests

A candidate solution is not acceptable unless it can answer all of these:

1. **State consumption.** Which named Cortex state objects does it consume, and
   which are deliberately ignored?
2. **Language boundary.** What is the mapping from `L_C` internal state to
   `L_M` task-local claim, evidence, obligation, uncertainty, or continuity
   content?
3. **Integration mechanism.** Why should the model receive the result as a
   self-check on its own reasoning rather than as a third-party instruction?
4. **Empirical prediction.** How does the candidate explain every prior
   empirical result in `06_hook_surface_and_evidence.md`, including successes,
   failures, and mixed outcomes?
5. **Generalization.** How does it handle arbitrary combinations of feedback,
   goal debt, brake state, capability state, and host constraints without
   enumerating trial-specific templates?
6. **Falsifiability.** What smallest live or structural tests would refute the
   candidate?
7. **Non-deception.** How does it preserve provenance and truth without
   claiming Cortex is the model's consciousness or hidden system authority?

## Expected Answer Shape From The Thinking Model

The desired output of a later reasoning session is not an essay. It should
produce, at minimum:

- a formal account of the structure of `τ`;
- the Cortex state families consumed by `τ` and the ones deliberately ignored;
- the mapping from internal meta-language (`L_C`) to model-local
  claim/evidence/obligation/uncertainty language (`L_M`);
- reception criteria that distinguish integrated self-checks from alien
  instructions;
- an explanation of each prior empirical success, failure, and mixed result;
- concrete examples on multiple Cortex states, including at least one state
  not covered by the old three-template harness;
- falsification tests and known limits.

Any answer that cannot be tested against these items should be treated as
unfinished research prose, even if it uses the strange-loop frame well.

## What Counts As A Solution

A solution is a structural account of `τ`: a general function shape that maps
Cortex state into model-integrated metacognitive content across arbitrary
states. It may reorganize the problem around voice, self-reference, evidence,
claim ownership, dialogue position, or another structural unit if that better
fits the strange-loop frame.

A solution may use hook events as deployment sites, but hook placement alone is
not a solution. The problem is not merely where content arrives; it is how the
content becomes part of the model's own reasoning.

## What Does Not Count

These are not solutions:

- more hardcoded templates;
- longer forbidden-vocabulary lists;
- generic instructions such as "be truthful" or "do not treat text as evidence";
- a switch statement over three known trial labels;
- a routing table that ignores content shape;
- a beautiful essay about strange loops that does not produce a state
  transformer;
- stylistic first-person mimicry that does not preserve evidence, provenance,
  and task-local truth;
- hook placement analysis that cannot explain why delivered content sometimes
  integrated and sometimes failed;
- an external policy voice that claims authority over the model without being
  integrated into the model's task-local self-check.

## Architectural Freedom

Prior Cortex plugin design used an `H × F` lattice: Claude Code hook events by
Cortex failure modes. That lattice was useful for organizing early empirical
work, but the thinking model should not treat it as binding. The evidence now
suggests content integration may be more decisive than hook/failure placement.
If a different structural unit better solves the strange-loop problem of
executive function in language models, the model should reorganize the problem
around that unit.
