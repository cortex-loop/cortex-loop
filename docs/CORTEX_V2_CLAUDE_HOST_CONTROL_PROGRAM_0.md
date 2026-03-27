# CORTEX_V2_CLAUDE_HOST_CONTROL_PROGRAM_0

Date: 2026-03-27
Status: active runtime-program brief for the first bounded outbound Claude host-control lane

## Purpose

This document records the bounded outbound host-control slice inside the accepted G1 Claude runtime/product parity line.

The chosen next move is:

- one bounded outbound Claude control lane,
- one text-only `claude-message-stream` request surface,
- one stdlib transport over the official Claude `Messages streaming` surface,
- one loopback service action endpoint on top of the current-line `A3` shell,
- and one re-audit closeout that preserves G1 truth while opening the first bounded outbound host-control lane.

This document does not override:

- `docs/CORTEX_V2_CORE_2.md`
- `docs/CORTEX_V2_SRE_2.md`
- `docs/CORTEX_V2_AUX_2.md`
- `docs/CORTEX_V2_IMPLEMENTATION_MASTER_PLAN_2.md`
- `docs/CORTEX_V2_GEMINI_RUNTIME_PROGRAM_0.md`
- `docs/CORTEX_V2_GEMINI_INGRESS_PROGRAM_0.md`
- `docs/CORTEX_V2_GEMINI_SERVICE_PROGRAM_0.md`

## Accepted parent and rationale

Accepted parent for this program on the current line:

- branch: `codex/k3-executive-live-outcome`
- commit: `efe003e`

Why this program opens now:

- the current line now includes a real loopback service shell,
- the smallest remaining product gap is realized host action rather than more internal runtime math,
- the current Claude driver already names `claude-message-stream` as the relevant host lifecycle effect,
- and a bounded outbound lane is smaller and more truthful than tool-calling doctrine, cancel/update lanes, or executive-loop widening.

## Locked scope

This program remains:

- Claude only,
- one active session per process,
- loopback-only at the public service boundary,
- one outbound action family only: `claude-message-stream`,
- text-only and strict-whitelist on the request surface,
- packet-subordinate,
- and host-specific without generic action/runtime/service doctrine.

This program adds only:

- `ClaudeHostControlRequest`
- `ClaudeHostControlResult`
- `execute_claude_message_stream()`
- `run_claude_host_control()`
- `POST /v1/actions/message-stream`
- outbound-action fixture transport and continuity proof

This program does **not** authorize:

- tools or tool-result submission,
- cancel/update lanes,
- remote hosting,
- multi-session or multi-client doctrine,
- more Claude host-control widening,
- executive-loop rewrite,
- generic runtime/service abstraction,
- runtime AUX activation,
- offline consolidation,
- mediation implementation,
- or broader product claims beyond this bounded text-only outbound lane.

## Public service contract

The public G1 surface remains:

- `python3 -m cortex.runtime.claude_service`

New HTTP endpoint:

- `POST /v1/actions/message-stream`

Request body shape:

- top-level keys: `action_tag`, `request`
- `action_tag` must be `claude-message-stream`
- `request.model` required
- `request.input` required and must be one non-empty string
- optional request keys:
  - `system`
  - `metadata`
  - `max_output_tokens`
- `stream` is implicit `true`; if present and not `true`, reject the request
- all other request keys are rejected

Response body shape:

- `action_tag`
- `records`

`records` is the ordered list of exact current-line `A1` runtime record objects produced from the returned host events.

All responses remain JSON.

Error contract:

- `400` invalid outbound request
- `502` upstream transport failure, malformed upstream stream, or zero-event result
- existing `404` and `405` remain unchanged
- response body shape remains `{"error":"<message>"}`

## Runtime law for this program

The G1 outbound lane may:

- reuse the current-line loopback `A3` service shell,
- keep exactly one active `ClaudeRuntimeSession` per process,
- validate one strict text-only outbound request carrier,
- execute one stdlib outbound `Messages streaming` transport,
- parse returned upstream frames into the exact current-line `A2` raw transcript record shape,
- and feed every returned host event through the current-line `parse_claude_host_event_envelope()` and `run_claude_runtime_step()`.

It may not:

- accept tools or tool-result submission,
- accept content-part arrays or multimodal payloads,
- widen into cancel/update lanes,
- bypass the current-line `A2` parser,
- widen into remote hosting or multi-client doctrine,
- add an `claude` SDK dependency,
- require live network or a real API key in the canonical verification bundle,
- or introduce a generic control substrate.

Undocumented-event law:

- undocumented raw `content.*` or `interaction.*` events remain lawful downstream input,
- they must still degrade to explicit conservative warnings,
- and G1 may not fabricate documented parity where none exists.

## G4 equivalence contract

For the same ordered outbound action calls and the same returned host-event stream, `A4` equivalence means:

- same per-event `selected_family`
- same per-event `realized_family`
- same per-event `warnings`
- same per-event `commitment_result_kind`
- same per-event `feedback_window_summary`
- same final persisted artifact with exact `continuity_truth` and `control_residue`

Exact replay of one-process diagnostic `budget_history` and `brake_history` remains out of scope for cross-process equivalence.

## Program order

This program remains split into five bounded seams:

1. `G4A` program lock
2. `G4B` request/result carriers plus stdlib transport
3. `G4C` runtime composition over current-line `A2`/`A1`
4. `G4D` service endpoint and continuity proof
5. `G4E` re-audit and closeout

Every seam must end on a clean tree before the next opens.

## Acceptance gates

`A4` is only honestly closed when all are true:

- `POST /v1/actions/message-stream` is real on the loopback service shell
- the request boundary is strict-whitelist and text-only
- the outbound transport is stdlib-only and host-specific
- returned upstream host events re-enter through the current-line `A2` parsing and current-line `A1` runtime composition
- export/import continuity preserves exact `continuity_truth` plus bounded `control_residue`
- targeted tests pass twice
- `make seam-preflight`, `make revalidate-claude-host-control`, `make revalidate-claude-service`, `make test-smoke`, and `make verify` pass
- and the `A4` phase-gate row is updated truthfully

## Current accepted state after G1 closeout

On the accepted G1 closeout line over accepted K3 baseline `efe003e`:

- `ClaudeHostControlRequest`, `ClaudeHostControlResult`, `execute_claude_message_stream()`, `run_claude_host_control()`, and `POST /v1/actions/message-stream` are now landed `A4` surfaces, implemented at G1 proof head `fe33a7e`
- the request boundary is strict-whitelist and text-only for current scope
- the stdlib transport has an internal fixture mode so canonical tests require no live Claude network
- returned host events now re-enter the current-line `A2` parser and `A1` runtime shell directly
- repeated direct reruns plus repeated `make revalidate-claude-host-control` passed for current scope

## Explicitly blocked moves

This program does not authorize:

- tools or tool-result submission,
- cancel/update lanes,
- content-part or multimodal request inputs,
- remote bind,
- multi-session or multi-client hosting,
- more Claude host-control widening,
- executive-loop rewrite,
- generic runtime/service abstraction,
- runtime AUX activation,
- offline consolidation,
- mediation implementation,
- or broader product claims beyond this bounded outbound lane.
