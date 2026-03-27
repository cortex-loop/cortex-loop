# CORTEX_V2_CLAUDE_RUNTIME_RESTACK_PROGRAM_0

Date: 2026-03-27
Status: accepted re-audited support brief for the A1 Claude runtime/product parity train

## Purpose

This document records the accepted post-`G1` A1 Claude runtime/product parity train:

- land the Claude runtime, ingress, service, and bounded host-control shells in dependency order,
- reuse accepted K3 executive allocation diagnostics exactly as-is,
- and close the biggest remaining host/runtime asymmetry before the later all-three-host live validation train.

This brief does not override:

- `docs/CORTEX_V2_CORE_2.md`
- `docs/CORTEX_V2_SRE_2.md`
- `docs/CORTEX_V2_AUX_2.md`
- `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
- `docs/CORTEX_V2_PHASE_GATES_2.md`
- `docs/CORTEX_V2_MATH_TO_CODE_CORRESPONDENCE.md`

## Accepted parent and rationale

Accepted parent for this train:

- branch: `codex/g1-gemini-runtime-product-parity`
- commit: `9dfe38a`

Why this train opens now:

- release still requires all three host/model lines live,
- Claude is the largest remaining runtime/product asymmetry,
- and the smallest honest next big move is Claude parity on top of accepted G1 truth rather than more OpenAI widening.

## Locked scope

This train remains:

- runtime/product only
- Claude-only
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

## A1 seam order

1. Claude documented host-event runtime shell
2. Claude raw-transcript ingress shell
3. Claude loopback service shell
4. Claude bounded host-control lane

Each seam must end clean before the next opens.

## Current accepted state after A1 closeout

On the accepted A1 closeout line, implemented at A1 proof head `9d6186c` over accepted G1 baseline `9dfe38a`:

- Claude runtime, ingress, service, and bounded host-control shells are now landed as the accepted A1 runtime/product parity stack
- the Claude projections reuse accepted K3 executive allocation diagnostics exactly for current scope
- Claude repo-local revalidation targets now exist on the accepted line and repeat-stability reruns have passed for current scope
