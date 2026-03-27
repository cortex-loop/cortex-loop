# CORTEX_V2_GEMINI_RUNTIME_RESTACK_PROGRAM_0

Date: 2026-03-27
Status: accepted re-audited support brief for the G1 runtime/product restack train

## Purpose

This document records the accepted post-`K3` G1 runtime/product restack train:

- land the Gemini runtime, ingress, service, and bounded host-control shells in dependency order,
- reuse accepted K3 executive allocation diagnostics exactly as-is,
- and close the biggest remaining host/runtime asymmetry before the later multi-host live validation train.

This brief does not override:

- `docs/CORTEX_V2_CORE_2.md`
- `docs/CORTEX_V2_SRE_2.md`
- `docs/CORTEX_V2_AUX_2.md`
- `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
- `docs/CORTEX_V2_PHASE_GATES_2.md`
- `docs/CORTEX_V2_MATH_TO_CODE_CORRESPONDENCE.md`

## Accepted parent and rationale

Accepted parent for this train:

- branch: `codex/k3-executive-live-outcome`
- commit: `efe003e`

Why this train opens now:

- release still requires all three host/model lines live,
- Gemini is the largest remaining runtime/product asymmetry,
- and the smallest honest next big move is Gemini parity on top of accepted K3 truth rather than more OpenAI widening.

## Locked scope

This train remains:

- runtime/product only
- Gemini-only
- dependency-ordered
- packet-subordinate
- and K3-reuse-first rather than new executive doctrine

This train does **not** authorize:

- support-memory runtime
- mediation implementation / `Q_t^{final}`
- generic runtime abstraction
- generic service abstraction
- runtime AUX activation
- offline consolidation
- multi-agent orchestration
- extra OpenAI work

## G1 seam order

1. Gemini documented host-event runtime shell
2. Gemini raw-transcript ingress shell
3. Gemini loopback service shell
4. Gemini bounded host-control lane

Each seam must end clean before the next opens.

## Current accepted state after G1 closeout

On the accepted G1 closeout line, implemented at G1 proof head `fe33a7e` and truthfully closed at deterministic closeout head `9dfe38a` over accepted K3 baseline `efe003e`:

- Gemini runtime, ingress, service, and bounded host-control shells are now landed as the accepted G1 runtime/product parity stack
- the Gemini projections reuse accepted K3 executive allocation diagnostics exactly for current scope
- Gemini repo-local revalidation targets now exist on the accepted line and repeat-stability reruns have passed for current scope
