# CORTEX_V2_RUNTIME_RESTACK_PROGRAM_0

Date: 2026-03-26
Status: active support brief for the K1 runtime/product restack train

## Purpose

This document opens the next explicit post-`j2` train:

- re-earn the donor runtime/product line on current accepted workflow truth,
- land the reference runtime chain first,
- then land the OpenAI runtime, ingress, and loopback service shells in dependency order,
- without importing donor workflow truth wholesale.

This brief does not override:

- `docs/CORTEX_V2_CORE_2.md`
- `docs/CORTEX_V2_SRE_2.md`
- `docs/CORTEX_V2_AUX_2.md`
- `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
- `docs/CORTEX_V2_PHASE_GATES_2.md`
- `docs/CORTEX_V2_MATH_TO_CODE_CORRESPONDENCE.md`

## Accepted parent and rationale

Accepted parent for this train:

- branch: `codex/j2-restack-acceptance-truth-normalization`
- commit: `acfccf9`

Why this train opens now:

- the accepted north-star gap is still live runtime / product shell,
- the repo already has a donor runtime/product line with bounded reference continuity plus OpenAI runtime, ingress, and service shells,
- and the smallest honest next move is to re-earn that line on current accepted workflow truth instead of widening sideways into mediation or new theory.

## Locked scope

This train remains:

- runtime/product only
- OpenAI-only on the product shell side
- dependency-ordered
- packet-subordinate
- and donor-aware without donor workflow doctrine import

This train does **not** authorize:

- mediation implementation
- Gemini product/runtime shell
- outbound OpenAI host control
- generic runtime abstraction
- generic service abstraction
- runtime AUX activation
- offline consolidation
- multi-agent orchestration

## Donor-source rule

The donor runtime branches are source material only:

- `codex/c1-reference-continuation`
- `codex/o1-openai-runtime-shell`
- `codex/o2-openai-ingress-shell`
- `codex/o3-openai-service-shell`

They may contribute runtime code, tests, and runtime-program docs.
They may not contribute workflow truth wholesale:

- not `AGENTS.md`
- not active workstream truth
- not local verification baseline-parent wording
- not support-surface accepted-baseline wording

Those surfaces must stay reconciled to accepted `j2` workflow truth.

## K1 seam order

1. reference runtime foundation
2. reference continuity closeout
3. OpenAI documented host-event runtime shell
4. OpenAI raw-transcript ingress shell
5. OpenAI loopback service shell

Each seam must end clean before the next opens.

## Current branch-local state

On branch `codex/k1f-openai-service-closeout` opened from accepted `j2` closeout head `acfccf9`:

- the reference runtime shell, bounded reference continuity, OpenAI documented-host-event runtime shell, raw-transcript ingress shell, and loopback service shell are now present as branch-local K1 candidate surfaces
- runtime program docs, phase-gate rows, correspondence rows, runtime fixtures, runtime unit/integration tests, and repo-local runtime revalidation targets now exist on this branch
- donor runtime code has been re-homed without importing donor workflow truth wholesale
- this remains branch-local implementation truth until an explicit accepted-baseline update lands
