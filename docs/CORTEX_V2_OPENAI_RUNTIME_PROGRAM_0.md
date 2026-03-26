# CORTEX_V2_OPENAI_RUNTIME_PROGRAM_0

Date: 2026-03-26
Status: accepted re-audited runtime-program brief for the first OpenAI documented host-event runtime shell

## Purpose

This document opens the next explicit runtime program after accepted `C1`.

The chosen next move is:

- one OpenAI-specific documented host-event runtime shell,
- one OpenAI-specific bounded persisted continuation carrier,
- one OpenAI-specific CLI shell over raw documented OpenAI host events,
- and one re-audit closeout that keeps real host lifecycle fit ahead of broader runtime widening.

This document does not override:

- `docs/CORTEX_V2_CORE_2.md`
- `docs/CORTEX_V2_SRE_2.md`
- `docs/CORTEX_V2_AUX_2.md`
- `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
- `docs/CORTEX_V2_REFERENCE_RUNTIME_PROGRAM_0.md`
- `docs/CORTEX_V2_REFERENCE_FEEDBACK_PROGRAM_0.md`
- `docs/CORTEX_V2_REFERENCE_FEEDBACK_PROGRAM_1.md`
- `docs/CORTEX_V2_REFERENCE_CONTINUITY_PROGRAM_0.md`

## Accepted parent and rationale

Accepted parent for this program:

- branch: `codex/j2-restack-acceptance-truth-normalization`
- commit: `acfccf9`

Why this program opens now:

- accepted `C1` now makes truthful continuation across fresh runs real,
- the next live product gap is not more reference-only refinement but one real host lifecycle surface,
- OpenAI already has landed observe/bind and commitment-path slices,
- and this bounded ingress-only shell is a smaller truthful step than bidirectional host control or generic runtime abstraction.

## Locked scope

This program remains:

- OpenAI only,
- documented host-event shell only,
- local CLI only,
- explicit save/load only,
- packet-subordinate,
- and ingress-only.

This program adds only:

- `OpenAIRuntimeSession`
- `OpenAIRuntimeSessionArtifact`
- `run_openai_runtime_step()`
- `python3 -m cortex.runtime.openai_cli`
- raw OpenAI host-event output projection with `raw_host_event_name`
- and OpenAI split-run equivalence proof

This program does **not** authorize:

- Gemini runtime,
- live network ingress,
- outbound OpenAI host control realization,
- generic runtime abstraction,
- service shell,
- multi-agent orchestration,
- longer-than-three-step feedback history,
- scoring rewrite,
- runtime AUX activation,
- offline consolidation,
- or mediation implementation.

## Public runtime contract

The OpenAI runtime shell exposes:

- `python3 -m cortex.runtime.openai_cli`

New public fields in the top-level CLI projection, in exact order:

1. `event_index`
2. `raw_host_event_name`
3. `native_event_name`
4. `dispatch_lane`
5. `selected_family`
6. `brake_state`
7. `executive_state_summary`
8. `control_ledger`
9. `warnings`
10. `session_summary`
11. `commitment_result_kind`
12. `feedback_window_summary`

Input remains JSONL via stdin or `--event-file`.

Each input line must contain:

- `event_name`
- `payload`

`event_name` must be the raw OpenAI host event name, not a pre-normalized canonical Cortex event.

## Runtime law for this program

The OpenAI runtime shell may:

- bind raw documented OpenAI Responses event names through the landed OpenAI driver,
- reject already-canonical Cortex event names before runtime processing,
- run the landed core dispatch and OpenAI commitment-path helpers,
- reuse the accepted bounded `C1` continuation law with OpenAI-owned carriers,
- and emit a host-specific runtime projection that preserves `raw_host_event_name`.

It may not:

- fabricate undocumented OpenAI lifecycle parity,
- widen into live network/service doctrine,
- realize outbound OpenAI host actions,
- introduce a generic runtime substrate,
- or treat OpenAI-specific success as permission for Gemini runtime or broader orchestration.

Undocumented-event law:

- undocumented raw OpenAI event names must remain explicit conservative warnings,
- those events may still flow through the shell if the landed core/commitment law makes that lawful,
- but the shell must preserve `raw_host_event_name` and may not pretend the event was natively supported.

Persistence law:

- the OpenAI persisted artifact is host-specific and versioned,
- it keeps the same top-level split as accepted `C1`: `continuity_truth` and `control_residue`,
- it persists bounded residue only,
- it does **not** persist full shell-long `budget_history` or `brake_history`,
- runtime and session I/O ownership remain self-contained inside the OpenAI runtime modules,
- and explicit load/save failure emits no stdout.

## Cross-process equivalence contract

`O1` equivalence means:

- same `continuity_truth`
- same per-event `selected_family`
- same per-event `realized_family`
- same per-event `warnings`
- same per-event `commitment_result_kind`
- same per-event `feedback_window_summary`
- same final persisted `control_residue`

`O1` equivalence does **not** require:

- exact byte-for-byte replay of `session_summary.budget_history`
- exact byte-for-byte replay of `session_summary.brake_history`

Those two histories remain public one-process diagnostics only.

## Program order

This program remains split into five bounded seams:

1. `O1A` program lock
2. `O1B` OpenAI runtime/session carriers plus persisted artifact
3. `O1C` OpenAI CLI projection
4. `O1D` OpenAI split-run equivalence proof
5. `O1E` re-audit and closeout

Every seam remains one-session max and must end on a clean tree before the next seam opens.

## Acceptance gates

`O1` is only honestly closed when all are true:

- documented raw OpenAI host events flow through the shell with preserved `raw_host_event_name`,
- undocumented raw host events remain explicit conservative warnings rather than fabricated parity,
- OpenAI bounded session persistence is real,
- split-run OpenAI equivalence matches the contract recorded above,
- targeted tests pass twice,
- `make seam-preflight`, `make revalidate-openai-runtime`, `make test-smoke`, and `make verify` pass,
- and the `O1` phase-gate row is updated truthfully.

## Current K1 candidate state before closeout

On branch `codex/k1f-openai-service-closeout` rooted at K1 proof head `d4c311f`:

- `OpenAIRuntimeSession`, `OpenAIRuntimeSessionArtifact`, `run_openai_runtime_step()`, and `python3 -m cortex.runtime.openai_cli` are now landed `O1` surfaces,
- raw documented OpenAI host events drive a host-specific runtime shell,
- `raw_host_event_name` is preserved in the top-level CLI record,
- canonical Cortex event names are now explicitly rejected at both CLI and runtime entrypoint level,
- undocumented raw OpenAI host events remain explicit conservative warnings rather than fabricated parity,
- `O1` runtime/session I/O no longer import private reference-runtime helpers,
- OpenAI split-run continuity proof now exists against the `O1` contract with explicit diagnostic-history non-equivalence,
- `make revalidate-openai-runtime` now exists as the repo-local OpenAI runtime revalidation entry point,
- and targeted reruns, repeated `make revalidate-openai-runtime`, `make test-smoke`, and `make verify` all passed on this candidate line.

This is branch-local K1 implementation truth.
It does **not** by itself promote accepted baseline truth.

## Explicitly blocked moves

This program does not authorize:

- live network/service doctrine,
- outbound OpenAI host control,
- generic runtime abstraction,
- Gemini runtime,
- multi-agent orchestration,
- runtime AUX activation,
- offline consolidation,
- mediation implementation,
- or broader runtime/product claims beyond this bounded OpenAI host-event shell.
