# CORTEX_V2_CLAUDE_RUNTIME_PROGRAM_0

Date: 2026-03-27
Status: active runtime-program brief for the first Claude documented host-event runtime shell

## Purpose

This document records the first Claude documented host-event runtime shell accepted on the A1 runtime/product parity line after accepted K3.

The chosen next move is:

- one Claude-specific documented host-event runtime shell,
- one Claude-specific bounded persisted continuation carrier,
- one Claude-specific CLI shell over raw documented Claude host events,
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

- branch: `codex/k3-executive-live-outcome`
- commit: `efe003e`

Why this program opens now:

- accepted `C1` now makes truthful continuation across fresh runs real,
- the next live product gap is not more reference-only refinement but one real host lifecycle surface,
- Claude already has landed observe/bind and commitment-path slices,
- and this bounded runtime shell is the first Claude parity step before ingress, service, and Claude host control.

## Locked scope

This program remains:

- Claude only,
- documented host-event shell only,
- local CLI only,
- explicit save/load only,
- packet-subordinate,
- and ingress-only.

This program adds only:

- `ClaudeRuntimeSession`
- `ClaudeRuntimeSessionArtifact`
- `run_claude_runtime_step()`
- `python3 -m cortex.runtime.claude_cli`
- raw Claude host-event output projection with `raw_host_event_name`
- and Claude split-run equivalence proof

This program does **not** authorize:

- extra OpenAI work,
- live network ingress,
- outbound Claude host control realization,
- generic runtime abstraction,
- Claude ingress/service doctrine,
- multi-agent orchestration,
- longer-than-three-step feedback history,
- scoring rewrite,
- runtime AUX activation,
- offline consolidation,
- or mediation implementation.

## Public runtime contract

The Claude runtime shell exposes:

- `python3 -m cortex.runtime.claude_cli`

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

`event_name` must be the raw Claude host event name, not a pre-normalized canonical Cortex event.

## Runtime law for this program

The Claude runtime shell may:

- bind raw documented Claude host event names through the landed Claude driver,
- reject already-canonical Cortex event names before runtime processing,
- run the landed core dispatch and Claude commitment-path helpers,
- reuse the accepted bounded `C1` continuation law with Claude-owned carriers,
- and emit a host-specific runtime projection that preserves `raw_host_event_name`.

It may not:

- fabricate undocumented Claude lifecycle parity,
- widen into live network/service doctrine,
- realize outbound Claude host actions,
- introduce a generic runtime substrate,
- or treat Claude-specific success as permission for Claude runtime or broader orchestration.

Undocumented-event law:

- undocumented raw Claude event names must remain explicit conservative warnings,
- those events may still flow through the shell if the landed core/commitment law makes that lawful,
- but the shell must preserve `raw_host_event_name` and may not pretend the event was natively supported.

Persistence law:

- the Claude persisted artifact is host-specific and versioned,
- it keeps the same top-level split as accepted `C1`: `continuity_truth` and `control_residue`,
- it persists bounded residue only,
- it does **not** persist full shell-long `budget_history` or `brake_history`,
- runtime and session I/O ownership remain self-contained inside the Claude runtime modules,
- and explicit load/save failure emits no stdout.

## Cross-process equivalence contract

`A1` equivalence means:

- same `continuity_truth`
- same per-event `selected_family`
- same per-event `realized_family`
- same per-event `warnings`
- same per-event `commitment_result_kind`
- same per-event `feedback_window_summary`
- same final persisted `control_residue`

`A1` equivalence does **not** require:

- exact byte-for-byte replay of `session_summary.budget_history`
- exact byte-for-byte replay of `session_summary.brake_history`

Those two histories remain public one-process diagnostics only.

## Program order

This program remains split into five bounded seams:

1. `G1A` program lock
2. `G1B` Claude runtime/session carriers plus persisted artifact
3. `G1C` Claude CLI projection
4. `G1D` Claude split-run equivalence proof
5. `G1E` re-audit and closeout

Every seam remains one-session max and must end on a clean tree before the next seam opens.

## Acceptance gates

`A1` is only honestly closed when all are true:

- documented raw Claude host events flow through the shell with preserved `raw_host_event_name`,
- undocumented raw host events remain explicit conservative warnings rather than fabricated parity,
- Claude bounded session persistence is real,
- split-run Claude equivalence matches the contract recorded above,
- targeted tests pass twice,
- `make seam-preflight`, `make revalidate-claude-runtime`, `make test-smoke`, and `make verify` pass,
- and the `A1` phase-gate row is updated truthfully.

## Current accepted state after G1 closeout

On the accepted G1 closeout line over accepted K3 baseline `efe003e`:

- `ClaudeRuntimeSession`, `ClaudeRuntimeSessionArtifact`, `run_claude_runtime_step()`, and `python3 -m cortex.runtime.claude_cli` are now landed `A1` surfaces, implemented at G1 proof head `fe33a7e`
- raw documented Claude host events drive a host-specific runtime shell
- `raw_host_event_name` is preserved in the top-level CLI record
- canonical Cortex event names are explicitly rejected at both CLI and runtime entrypoint level
- nested `control_ledger.allocation_diagnostics` reuses accepted K3 executive allocation truth exactly for current scope
- repeated direct reruns plus repeated `make revalidate-claude-runtime` passed for current scope

## Explicitly blocked moves

This program does not authorize:

- live network/service doctrine,
- outbound Claude host control,
- generic runtime abstraction,
- Claude ingress/service doctrine,
- multi-agent orchestration,
- runtime AUX activation,
- offline consolidation,
- mediation implementation,
- or broader runtime/product claims beyond this bounded Claude host-event shell.
