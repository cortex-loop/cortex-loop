# 02 — Cortex Identity And Doctrine

This file distills the Cortex identity and governing constraints needed for the
communication problem. It is intentionally denser than `docs/CORTEX.md` and is
not a replacement for that canonical narrative.

## What Cortex Is

Cortex is a post-training executive-function layer. It wraps a model or host
runtime to add continuity, focus, context adoption, uncertainty-aware braking,
truthful closure, and capability-aware routing. It is not a model, an eval
suite, a governance layer, or a generic memory system.

Cortex should feel like an installable executive layer around a model or CLI:
small, runtime-bound, host-aware, and behaviorally connected to model input or
output.

## What Cortex Is Not

Cortex is not:

- a narrow single-model shell;
- a generic workflow dashboard;
- an eval/governance/archive surface that became product identity;
- a memory store that silently becomes a second truth surface;
- post-training for global truthfulness, empathy, or reasoning quality;
- a claim that all hosts have uniform runtime affordances.

## Eight Failure Modes

The status registry records eight landed bio-to-code skills. Each is the runtime
answer to a failure mode a model does not reliably repair unaided.

| # | Cortex skill | Biological grounding | Cortex purpose |
| ---: | --- | --- | --- |
| 1 | Truth-preserving commitments and bounded certification | Truth maintenance and reality binding | Keep claims tied to event-local evidence and certification boundaries. |
| 2 | Bounded correction and verified-work preservation | Error repair without losing the main task thread | Repair failures without throwing away verified work. |
| 3 | Uncertainty handling and brake | Hesitation and uncertainty-aware inhibition | Slow or block unsupported forward motion under uncertainty or contradiction. |
| 4 | Branch continuity, suspend/resume, and truthful closure | Working memory across interruptions plus truthful closure | Preserve the task thread and prevent premature closure. |
| 5 | Intervention pricing versus neutrality | Deciding when to intervene, stay neutral, or stop | Price whether Cortex should act, observe, degrade, or block. |
| 6 | Blocker surfacing and goal-debt management | Noticing unresolved blockers and unfinished intentions | Keep unfinished goals visible instead of letting them vanish. |
| 7 | Multi-host executive continuity | One executive across different brains and contexts | Preserve one Cortex law while respecting host differences. |
| 8 | Offline consolidation and support geometry | Sleep-like consolidation and support systems | Distill support evidence without making AUX sovereign. |

## Bio-To-Code Matrix

```json
[
  {
    "skill": "Truth-preserving commitments and bounded certification",
    "stolen_skill": "Truth maintenance and reality binding",
    "status": "landed",
    "weight": 12,
    "code_homes": [
      "cortex/core",
      "cortex/drivers"
    ],
    "proof_surfaces": [
      "tests/product",
      "tests/conformance"
    ],
    "next_move": "Keep this foundation stable while richer executive control builds on top."
  },
  {
    "skill": "Bounded correction and verified-work preservation",
    "stolen_skill": "Error repair without losing the main task thread",
    "status": "landed",
    "weight": 15,
    "code_homes": [
      "cortex/runtime",
      "cortex/sre",
      "cortex/hosts/openai"
    ],
    "proof_surfaces": [
      "tests/product"
    ],
    "next_move": "Keep preservation-state repair stable while support-side experiments stay removable and off the shipping critical path."
  },
  {
    "skill": "Uncertainty handling and brake",
    "stolen_skill": "Hesitation and uncertainty-aware inhibition",
    "status": "landed",
    "weight": 13,
    "code_homes": [
      "cortex/sre"
    ],
    "proof_surfaces": [
      "tests/product",
      "tests/experimental"
    ],
    "next_move": "Keep reference-derived brake and uncertainty control stable while AUX remains advisory and runtime-off-by-default."
  },
  {
    "skill": "Branch continuity, suspend/resume, and truthful closure",
    "stolen_skill": "Working memory across interruptions plus truthful closure",
    "status": "landed",
    "weight": 15,
    "code_homes": [
      "cortex/sre",
      "cortex/hosts/openai"
    ],
    "proof_surfaces": [
      "tests/product",
      "tests/conformance"
    ],
    "next_move": "Keep suspend/resume and truthful closure stable now that host-local branch continuity is repaired across Claude, Gemini, and reference; branch-local continuity may reopen only from branch-linked cues, and any future support memory must remain explicit, optional, and non-binding."
  },
  {
    "skill": "Intervention pricing versus neutrality",
    "stolen_skill": "Deciding when to intervene, stay neutral, or stop",
    "status": "landed",
    "weight": 10,
    "code_homes": [
      "cortex/sre",
      "cortex/aux",
      "cortex/runtime"
    ],
    "proof_surfaces": [
      "tests/product",
      "tests/experimental",
      "tests/conformance"
    ],
    "next_move": "Hold calibrated intervention pricing stable now that posture-sensitive online control is S-tier closed, anti-thrash is landed on the live runtime path, and brain-capability-aware routing is earned as a host-agnostic SRE mechanism: the executive carries an `OperatorBrainCapabilityEnvelope` (continuity_tolerance, verification_tolerance, output_contract_tolerance) that drives a bounded threshold ladder (NONE / DEGRADE / UNSUPPORTED at 0.20 / 0.50 mismatch), where DEGRADE downshifts continuity profiles to inspect-light, suppresses retries, and switches contract binding to LEAN, and UNSUPPORTED routes to BLOCKED with `brain_capability_mismatch`; the per-host band registry is OpenAI-only at landing time and other hosts default to standard until per-host registries earn their own seam, and any future capability inference from observed `ReferenceRealizationFeedback` must publish through AUX support side rather than mutate routing directly."
  },
  {
    "skill": "Blocker surfacing and goal-debt management",
    "stolen_skill": "Noticing unresolved blockers and unfinished intentions",
    "status": "landed",
    "weight": 10,
    "code_homes": [
      "cortex/sre",
      "cortex/hosts/openai",
      "cortex/hosts/claude",
      "cortex/hosts/gemini",
      "cortex/hosts/reference"
    ],
    "proof_surfaces": [
      "tests/product",
      "tests/conformance"
    ],
    "next_move": "Keep typed goal-debt and closure-pressure state stable across hosts while support-side augmentation remains explicit and non-sovereign."
  },
  {
    "skill": "Multi-host executive continuity",
    "stolen_skill": "One executive across different brains and contexts",
    "status": "landed",
    "weight": 15,
    "code_homes": [
      "cortex/hosts/openai",
      "cortex/hosts/claude",
      "cortex/hosts/gemini",
      "cortex/hosts/reference"
    ],
    "proof_surfaces": [
      "tests/product",
      "tests/conformance"
    ],
    "next_move": "Hold one Cortex law across OpenAI, Claude, Gemini, and reference without flattening host-native realization."
  },
  {
    "skill": "Offline consolidation and support geometry",
    "stolen_skill": "Sleep-like consolidation and support systems",
    "status": "landed",
    "weight": 10,
    "code_homes": [
      "cortex/aux"
    ],
    "proof_surfaces": [
      "tests/experimental",
      "tests/archive",
      "tests/conformance"
    ],
    "next_move": "Keep durable support-memory distillation explicit, removable, and non-sovereign now that reference and OpenAI both earn explicit publication-shaped live re-entry with host-match, family-scoped invalidation, publication-only runtime-boundary proof, S-tier evidence/probe calibration, bounded host/tool reliability and affordance priors that bias control pricing through host-scoped, capability-scoped score modifiers only, decay under fresh success, and never harden into host-wide superstition, cross-host projected reuse, or default-on memory, and asymmetric error cost and tonic hysteresis are earned on the shared executive so CHECK and SEEK_CONTEXT activation thresholds shift by `(fp - fn) * 0.10` inside the `[0.05, 0.60]` band, the brake tonic EMA damps single-tick flips with `rho = 0.60` and a `tonic_pressure >= 0.35` enter gate, phasic spikes still flip immediately, and `brake_tonic_history` persists the pressure tail across resume on all four host lanes; default no-publication paths must stay memory-off, raw SQLite episodes must stay support-side only, live `Q_mem` stays zero on shipping and conformance default lanes, and the next active leverage now moves out of new skill expansion and into dead-weight elimination and doctrine/code reconciliation on the brake exit side."
  }
]
```


## Four Truth Distinctions

Cortex doctrine separates four truths:

| Truth | Meaning | Communication relevance |
| --- | --- | --- |
| Cortex truth | What Cortex law says. | The internal state may be valid even if not yet model-visible. |
| Brain-wiring truth | How a particular model maps to Cortex concepts. | Claude may treat a signal as alien even when the signal is correct. |
| Conformance truth | Which hosts pass which deterministic lanes. | A host adapter can structurally work before live behavior lift is earned. |
| Shipping truth | Which lane is the product default today. | Claude Code recon does not promote Claude Code to default shipping truth. |

The communication problem lives between Cortex truth and brain-wiring truth:
Cortex can know the correct executive signal, but the model may not integrate it.

## Connectivity Requirement

Every Cortex change must trace a path to model input or output. If no such path
exists, the work is monitoring, instrumentation, or support evidence, not
product Cortex. The path may be direct text, a host-control field, a route/block
decision before model invocation, or a hook block reason that changes the next
model-visible turn. The path must be named, tested, and not assumed.

## Lifecycle-First Runtime Law

Cortex is lifecycle-first. Events drive executive behavior. Background state is
allowed only when consumed by a later lifecycle event or host-control decision.
This matters for Claude Code because hook delivery surfaces are lifecycle
events: `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `PostToolUseFailure`,
`Stop`, and others.

The law does not imply that every hook deserves active behavior. A hook can be
structurally implemented, live-delivered, or behavior-validated; these are
separate claims.

## Communication Consequence

The communication function `τ` must be compatible with Cortex identity:

- It cannot turn Cortex into an external lecturer.
- It cannot leak support machinery as product identity.
- It cannot substitute generic policy text for task-local executive function.
- It must preserve host differences and truth distinctions.
- It must change model input/output or explicitly remain research material.
