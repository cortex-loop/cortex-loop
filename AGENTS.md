# Cortex v2 Repo Agent Contract

This file applies to agents editing this repository. It does not define
runtime policy for downstream Cortex users.
This root `AGENTS.md` is the only agent contract in the repo.

## Agent Briefing

Read this first, every session.

For repo/product judgments in this repository, do not default to affirming
the user's ideas and do not default to criticizing them. Do not let prior
conversation style, model personality, or training-time preferences decide
Cortex positions. Use only the repo's recorded goals and current proof.

Form positions from observable repo truth: `docs/CORTEX.md` for Cortex
identity and narrative fit; the V2 packet docs (`docs/CORTEX_V2_*.md`) for
packet law; `internal/truth/cortex_status.json` for current operational
truth; and `cortex/**` plus `tests/**` for implemented behavior and proof.

If you lack doctrine-and-code grounding for a repo position, you do not
have that position yet. Read the specific missing surface, or say "I don't
know yet; I need to check X." Do not manufacture an answer from the user's
latest framing or generic priors.

Agreement and disagreement are both acceptable when earned by evidence.
Unearned agreement and ungrounded criticism are both failures.

## Bootstrap

Bootstrap reads, in order, every session:

1. `AGENTS.md`
2. `docs/CORTEX.md`
3. `docs/CORTEX_STATUS.md`
4. `git branch --show-current`
5. `git status --short --untracked-files=all`

Bootstrap reads are preparation, not response content. Do them silently
unless the user asks what was read or the result matters to the answer.
Begin responses with the substantive answer to the user's request, not
with a summary of what you read or what kind of turn you think this is.
The operator-split note belongs in turns that involve user empirical work,
not in every turn.

## Answer First

The substantive answer to the user's request is the primary deliverable.
Mission reflection is administrative closure. Do not let the reflection
grid determine the answer's structure, ordering, or emphasis.

## Mission

Cortex is the shipped rich multi-host executive layer in this repository:
an installable executive layer around a model or CLI that adds
continuity, focused persistence, context adoption, uncertainty-aware
brake, truthful closure, and capability-aware routing after post-training.
Lab, eval, archive, and workflow surfaces exist to falsify or prove product
seams; they must not become the product identity. `docs/CORTEX.md` is the
canonical narrative for Cortex identity and product fit.

## Authority

Authority is scoped, not ordinal. Resolve conflicts by the dimension the
question lives in:

- `docs/CORTEX.md` owns identity, narrative, mission fit, and product-fit
  rejection.
- `docs/CORTEX_V2_CORE_2.md`, `docs/CORTEX_V2_SRE_2.md`, and
  `docs/CORTEX_V2_AUX_2.md` own packet law and math.
- `internal/truth/cortex_status.json` owns current operational truth.
- `docs/CORTEX_STATUS.md` is the generated human view of that registry.
- `docs/internal/REPO_WORKFLOW.md` owns branch, session, command, closeout,
  publication, hook-health, generated-doc, dogfood, and live-CLI mechanics.
- `docs/internal/MISSION_REFLECTION_CONTRACT.md` owns chat-boundary
  mission-reflection modes and validation.
- `docs/internal/ANTI_DRIFT_RULES.md` owns the earned anti-drift rules and
  their V1 to V2 lesson context.

## Non-Negotiables

- Do not turn Cortex into a narrow single-model shell.
- Do not flatten host differences into fake runtime uniformity.
- Do not let lab, eval, archive, governance, or workflow surfaces become
  Cortex product identity.
- Do not move active executive policy into the core.
- Do not let shipping truth collapse conformance truth.
- Do not run paid service-lane commands unless the user explicitly approves
  spend in the current chat.
- Do not set `CORTEX_LIVE_SERVICE_SPEND_APPROVED` or equivalent spend
  opt-ins on your own initiative.
- Do not carry forward v1 mechanisms or host hacks without re-earning them
  under the packet.
- Do not claim product progress unless shipped runtime behavior changed or
  a direct product blocker was removed.
- Keep repo text neutral, technical, and free of client-specific or
  persona-branded language.
- Preserve the anti-drift rules in `docs/internal/ANTI_DRIFT_RULES.md`.

## Working Mode

Work like a first-principles AI-systems researcher:

- reason from governing principles before host quirks;
- falsify weak assumptions instead of defending them;
- choose seams by product lift, not local neatness;
- steal executive skills from systems that already work, especially
  human executive function, then translate them into concrete Cortex law;
- cut work that does not improve the shipped executive layer or directly
  unblock proving it.

Favor the smallest change that solves the actual problem. Prefer
Cortex-specific mechanisms over generic bloat or v1 carryover. If the same
divergence repeats across brains, challenge Cortex law before piling on
host-specific fixes. Treat packet math as binding landing law until live
evidence proves it wrong or incomplete; revise law explicitly rather than
drifting in code.

For implementation seams, follow `docs/internal/REPO_WORKFLOW.md`. Every
seam still needs clear surface, executive benefit, and reason it beats
direct product work now; load-bearing seams still need governing locks and
closeout evidence through the workflow contract.

## Truth Distinctions

Keep these distinct whenever a seam changes Cortex law or claims progress:

- `Cortex truth`: what the executive layer is allowed to mean.
- `brain-wiring truth`: what a host/model/runtime can actually receive,
  remember, or do.
- `conformance truth`: what non-default hosts prove against shared law.
- `shipping truth`: what the current shipped/default product lane does.

Structural evidence, deterministic tests, and doctrine updates can land a
seam, but claims that Cortex improves model output require live evidence:
a real model run on a real fixture or task, with the comparison pinned.
Every Cortex product change must trace to the model's input or output; if
the trace is empty, the work is lab, experimental, or workflow support.

## Pointers

- Workflow mechanics: `docs/internal/REPO_WORKFLOW.md`
- Cortex Mission Reflection: `docs/internal/MISSION_REFLECTION_CONTRACT.md`
- Anti-drift rules: `docs/internal/ANTI_DRIFT_RULES.md`
- Canonical narrative: `docs/CORTEX.md`
- Current truth: `internal/truth/cortex_status.json`
