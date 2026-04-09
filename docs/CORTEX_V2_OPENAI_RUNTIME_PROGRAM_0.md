# CORTEX_V2_OPENAI_RUNTIME_PROGRAM_0

Surface: product

Date: 2026-03-26
Status: accepted re-audited runtime-program brief for the compressed OpenAI-only documented host-event product shell

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
- `docs/internal/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
- `docs/experimental/CORTEX_V2_REFERENCE_RUNTIME_PROGRAM_0.md`
- `docs/experimental/CORTEX_V2_REFERENCE_FEEDBACK_PROGRAM_0.md`
- `docs/experimental/CORTEX_V2_REFERENCE_FEEDBACK_PROGRAM_1.md`
- `docs/experimental/CORTEX_V2_REFERENCE_CONTINUITY_PROGRAM_0.md`

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

This program now carries the X1 accepted compression on top of the earlier O1 shell and adds only:

- compact `OpenAIRuntimeSession` product-journal truth
- compact `OpenAIRuntimeSessionArtifact`
- `run_openai_runtime_step()` over the compact decision table
- `python3 -m cortex.runtime.openai_cli`
- raw OpenAI host-event output projection with `raw_host_event_name`, `decision`, and `journal`
- and OpenAI split-run equivalence proof on the compressed carrier

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

Top-level CLI projection fields, in exact order:

1. `event_index`
2. `raw_host_event_name`
3. `native_event_name`
4. `dispatch_lane`
5. `decision`
6. `warnings`
7. `journal`
8. `commitment_result_kind`

Input remains JSONL via stdin or `--event-file`.

Each input line must contain:

- `event_name`
- `payload`

`event_name` must be the raw OpenAI host event name, not a pre-normalized canonical Cortex event.

## Runtime law for this program

The accepted OpenAI runtime shell may:

- bind raw documented OpenAI Responses event names through the landed OpenAI driver,
- reject already-canonical Cortex event names before runtime processing,
- run the landed core dispatch and OpenAI commitment-path helpers,
- reuse OpenAI-owned continuation through one compact product journal,
- compute one explicit OpenAI-only decision table over consequential-write pressure, approval pressure, evidence gap, continuation debt, and accepted failure classes,
- and emit a host-specific runtime projection that preserves `raw_host_event_name`.

It may not:

- fabricate undocumented OpenAI lifecycle parity,
- widen into live network/service doctrine,
- realize outbound OpenAI host actions,
- introduce a generic runtime substrate,
- treat OpenAI-specific success as permission for Gemini runtime or broader orchestration,
- or route accepted product behavior through the reference-soft-control allocation stack.

Undocumented-event law:

- undocumented raw OpenAI event names must remain explicit conservative warnings,
- those events may still flow through the shell if the landed core/commitment law makes that lawful,
- but the shell must preserve `raw_host_event_name` and may not pretend the event was natively supported.

Persistence law:

- the OpenAI persisted artifact is host-specific and versioned,
- the only accepted export/import contract is `openai_product_journal` v1 with one top-level `journal` object,
- it always persists `session_id`, `event_index`, `active_goal_ref`, `pending_goal_refs`, `confirmed_artifact_refs`, `last_failure_class`, and `next_recommended_move`,
- it may additionally persist `preservation_state` on verified-work sessions only,
- it does **not** persist `continuity_truth`, `control_residue`, branch registry, feedback residue, `budget_history`, or `brake_history`,
- legacy pre-X1 artifacts are explicitly rejected rather than silently migrated,
- runtime and session I/O ownership remain self-contained inside the OpenAI runtime modules,
- and explicit load/save failure emits no stdout.

## Cross-process equivalence contract

`O1` equivalence means:

- same `journal`
- same per-event `decision`
- same per-event `warnings`
- same per-event `commitment_result_kind`
- same final persisted artifact

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
- OpenAI compact product-journal persistence is real,
- the outward record preserves the exact `decision + journal` contract,
- the accepted OpenAI product path no longer depends on reference-soft-control selection or allocation diagnostics,
- split-run OpenAI equivalence matches the contract recorded above,
- targeted tests pass twice,
- `make seam-preflight`, `make revalidate-openai-runtime`, `make test-smoke`, and `make verify` pass,
- and the `O1` phase-gate row is updated truthfully.

## Historical accepted state before X1 compression

On the accepted K1 runtime closeout line implemented at K1 proof head `d4c311f` and truthfully closed at deterministic closeout head `79b8f39` on branch `codex/k1f-openai-service-closeout`:

- `OpenAIRuntimeSession`, `OpenAIRuntimeSessionArtifact`, `run_openai_runtime_step()`, and `python3 -m cortex.runtime.openai_cli` are now landed `O1` surfaces,
- raw documented OpenAI host events drive a host-specific runtime shell,
- `raw_host_event_name` is preserved in the top-level CLI record,
- canonical Cortex event names are now explicitly rejected at both CLI and runtime entrypoint level,
- undocumented raw OpenAI host events remain explicit conservative warnings rather than fabricated parity,
- `O1` runtime/session I/O no longer import private reference-runtime helpers,
- OpenAI split-run continuity proof now exists against the `O1` contract with explicit diagnostic-history non-equivalence,
- `make revalidate-openai-runtime` now exists as the repo-local OpenAI runtime revalidation entry point,
- and targeted reruns, repeated `make revalidate-openai-runtime`, `make test-smoke`, and `make verify` all passed on the accepted K1 line.

## Current accepted state after X1 compression

On the accepted X1 line:

- `OpenAIRuntimeSession` is now the compact product journal for the accepted OpenAI-only product path,
- `OpenAIRuntimeSessionArtifact` now exports/imports `openai_product_journal` v1 only,
- `run_openai_runtime_step()` now uses an explicit OpenAI-only decision table instead of the reference-soft-control allocation path,
- `python3 -m cortex.runtime.openai_cli` now emits the compact `decision + journal` projection while preserving `raw_host_event_name`,
- split-run OpenAI equivalence is now re-earned on the compact journal carrier,
- and the old allocation/feedback surfaces survive only as historical/reference evidence rather than the accepted OpenAI-only product runtime.

On the current review line after the preservation-state candidate:

- `OpenAIRuntimeSession` may now carry optional `preservation_state` on verified-work sessions only,
- `run_openai_runtime_verification_step()` now derives and persists the preservation state from observable verification facts,
- verified-work activation now records a deterministic task anchor when the compact journal has no active anchor yet,
- and the thin path remains unchanged because sessions without `work_contract` still omit `preservation_state`.

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
